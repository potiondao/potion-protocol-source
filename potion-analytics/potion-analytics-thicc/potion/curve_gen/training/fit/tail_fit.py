"""
This module implements functions for fitting pareto tails to any two tailed distribution.
"""
import numpy as np
import pandas as pd
from scipy.stats import linregress, genpareto
from potion.curve_gen.training.distributions.skewed_students_t import skewed_t
from potion.curve_gen.training.train import swap_params


def _sort_tail_returns(return_df: pd.DataFrame, left_tail=True):
    """
    Takes the return samples of the distribution and creates a sorted copy of the values and
    returns them for fitting the tails of the distribution. The boolean flag controls whether
    the samples being sorted are for the left tail (negative returns) or the right tail
    (positive returns). By default, this flag is True corresponding to the left tail. The
    sorted array is returned.

    Parameters
    ----------
    return_df : pandas.DataFrame
        The return samples of the financial asset. DataFrame contains one column Return containing
        the samples
    left_tail : bool
        (Optional. Default: True) Specifies whether the samples being sorted correspond to the
        left or right tail

    Returns
    -------
    sorted_tail_returns : pandas.DataFrame
        The sorted return samples
    """
    sorted_tail_returns = return_df.copy().sort_values(by=['Return'], ascending=left_tail)

    if left_tail:
        sorted_tail_returns = sorted_tail_returns[sorted_tail_returns.Return < 0.0]
    else:
        sorted_tail_returns = sorted_tail_returns[sorted_tail_returns.Return > 0.0]
    sorted_tail_returns.reset_index(inplace=True, drop=True)

    return sorted_tail_returns


def _convert_samples_to_log_deltas(sorted_return: pd.DataFrame, location: float,
                                   threshold: float, left_tail=True):
    """
    Converts returns to deltas from the center of the distribution. If the distribution is already
    centered at 0.0 return, the delta and return will be the same. Afterwards, these delta values
    are converted to log delta values so that the tail estimation algorithm can perform the
    tail fitting algorithm in the log domain.

    Parameters
    ----------
    sorted_return : pandas.DataFrame
        The sorted return samples
    location : float
        The location parameter of the center of a two tailed distribution
    threshold : float
        The threshold value to use as the start of 'tail' samples. Ex. 0.1 is samples larger than
        ten percent return are on the tail

    Returns
    -------
    log_delta : numpy.ndarray
        The log delta values for each of the return samples on the tail
    """
    if left_tail:
        delta = location - sorted_return.Return.to_numpy()
    else:
        delta = sorted_return.Return.to_numpy() - location
    delta = delta[delta > threshold]
    delta = delta[delta != 0.0]

    return np.log(np.abs(delta))


def _adjust_deltas_to_same_size(left_deltas: np.ndarray, right_deltas: np.ndarray):
    """
    Adjusts the size of the two delta arrays so that they are the same.

    Parameters
    ----------
    left_deltas : numpy.ndarray
        The log delta values of the left tail
    right_deltas : numpy.ndarray
        The log delta values of the right tail

    Returns
    -------
    left_deltas : numpy.ndarray
        The log delta values of the left tail
    right_deltas : numpy.ndarray
        The log delta values of the right tail
    """
    left_size = len(left_deltas)
    right_size = len(right_deltas)

    if right_size < left_size:
        left_deltas = left_deltas[0:right_size]
    elif left_size < right_size:
        right_deltas = right_deltas[0:left_size]

    assert len(left_deltas) == len(right_deltas)

    return left_deltas, right_deltas


def fit_samples(return_df, *args, dist=skewed_t,
                left_threshold=0.1, right_threshold=0.1):
    """
    Performs a fit of any two tailed probability distribution and fits pareto tails to the left
    and right tail.

    Parameters
    ----------
    return_df : pandas.DataFrame
        The training data financial return history as a DataFrame. Contains one column called
        Return with the index corresponding to each time step's sample
    args : List[float]
        The parameter list to pass to the optimizer as an initial guess. See scipy.rv_continuous
        fit function for more details.
    dist : rv_continuous
        (Optional. Default: skewed_t) The probability distribution to use to generate the
        Kelly curve
    left_threshold : float
        (Optional. Default: 0.1) The probability threshold where the sample is considered on the
        left tail. For example, 0.1 is 10% return.
    right_threshold : float
        (Optional. Default: 0.1) The probability threshold where the sample is considered on the
        right tail. For example, 0.1 is 10% return.

    Returns
    -------
    dist_params : List[float]
        The fit parameters contain in a List the parameters of the two tailed fit, followed by
        the intercept and slope of the left pareto, and the intercept and slope of the right
        pareto. For example, with Skewed Normal this List would be [loc, scale, skew, left_int,
        left_slope, right_int, right_slope]
    fit_dict : dict
        A dict containing stats information from the quality of the fit and extra info which may
        be useful for certain plotting log-log plots
    """
    return_df = pd.DataFrame(return_df, columns=['Return'])
    dist_params = list(dist.fit(return_df, *args))
    dist_params = swap_params(dist_params)

    sorted_left_samples = _sort_tail_returns(return_df, left_tail=True)
    sorted_right_samples = _sort_tail_returns(return_df, left_tail=False)

    left_log_delta = _convert_samples_to_log_deltas(
        sorted_left_samples, dist_params[0], left_threshold, left_tail=True)
    right_log_delta = _convert_samples_to_log_deltas(
        sorted_right_samples, dist_params[0], right_threshold, left_tail=False)

    left_log_delta, right_log_delta = _adjust_deltas_to_same_size(left_log_delta, right_log_delta)

    # Calculate the ranks of the sample - 1st, 2nd, 3rd, etc. Convert to log domain.
    # Off by 1 so no divide by 0 converting to log
    log_rank = np.log(np.linspace(1, len(left_log_delta) + 1, len(left_log_delta)))

    # Perform the linear regression to find the parameters for the tail distributions
    (left_m, left_b, left_r_value, left_p_value, left_std_err) = linregress(
        left_log_delta, log_rank)
    (right_m, right_b, right_r_value, right_p_value, right_std_err) = linregress(
        right_log_delta, log_rank)

    # Add the tail distribution parameters to the list of distribution parameters
    dist_params.append(-left_m)
    dist_params.append(-right_m)

    left_fit_stats = {
        'r': left_r_value,
        'p': left_p_value,
        'std_err': left_std_err
    }
    right_fit_stats = {
        'r': right_r_value,
        'p': right_p_value,
        'std_err': right_std_err
    }

    # Save the most extreme worst and best values
    extreme_values = (sorted_left_samples.Return[0], sorted_right_samples.Return[0])

    return dist_params, {
        'log_rank': log_rank,
        'evs': extreme_values,
        'left_log_delta': left_log_delta,
        'right_log_delta': right_log_delta,
        'left_stats': left_fit_stats,
        'right_stats': right_fit_stats,
        'left_b': left_b,
        'right_b': right_b
    }


def fit_samples_mle(return_df, *args, dist=skewed_t,
                    left_threshold=0.1, right_threshold=0.1):
    """
    Performs a fit of any two tailed probability distribution and fits pareto tails to the left
    and right tail using maximum likelihood estimation.

    Parameters
    ----------
    return_df : pandas.DataFrame
        The training data financial return history as a DataFrame. Contains one column called
        Return with the index corresponding to each time step's sample
    args : List[float]
        The parameter list to pass to the optimizer as an initial guess. See scipy.rv_continuous
        fit function for more details.
    dist : rv_continuous
        (Optional. Default: skewed_t) The probability distribution to use to generate the
        Kelly curve
    left_threshold : float
        (Optional. Default: 0.1) The probability threshold where the sample is considered on the
        left tail. For example, 0.1 is 10% return.
    right_threshold : float
        (Optional. Default: 0.1) The probability threshold where the sample is considered on the
        right tail. For example, 0.1 is 10% return.

    Returns
    -------
    dist_params : List[float]
        The fit parameters contain in a List the parameters of the two tailed fit, followed by
        the intercept and slope of the left pareto, and the intercept and slope of the right
        pareto. For example, with Skewed Normal this List would be [loc, scale, skew, left_int,
        left_slope, right_int, right_slope]
    fit_dict : dict
        A dict containing stats information from the quality of the fit and extra info which may
        be useful for certain plotting log-log plots
    """
    return_df = pd.DataFrame(return_df, columns=['Return'])
    dist_params = list(dist.fit(return_df, *args))
    dist_params = swap_params(dist_params)

    sorted_sample_data = np.sort(return_df.Return.to_numpy())

    left_tail_x_points = sorted_sample_data[sorted_sample_data <= -left_threshold]
    right_tail_x_points = sorted_sample_data[sorted_sample_data >= right_threshold]

    left_tail_start_sample = left_tail_x_points[-1]
    right_tail_start_sample = right_tail_x_points[0]

    scale = dist_params[1]
    left_tail_xi = genpareto.fit(-sorted_sample_data,
                                 floc=-left_tail_start_sample, fscale=scale)[0]
    right_tail_xi = genpareto.fit(sorted_sample_data,
                                  floc=right_tail_start_sample, fscale=scale)[0]

    left_alpha = 1.0 / left_tail_xi
    right_alpha = 1.0 / right_tail_xi

    dist_params.append(left_alpha)
    dist_params.append(right_alpha)

    return dist_params, {}


def perform_linear_replication(log_rank: np.ndarray, b: float, m: float):
    """
    Uses the slope and intercept values found in regression to replicate the extreme
    samples that would be consistent with an exact power law relationship

    Parameters
    ----------
    log_rank : numpy.ndarray
        The rankings of the samples (1st, 2nd, 3rd, etc.) converted to log for plotting or
        analyzing tails
    b : float
        The Y-intercept value for the line in log-log space which corresponds to the power law
    m : float
        The slope of the line in log-log space which corresponds to the power law

    Returns
    -------
    replicated_values : numpy.ndarray
        The distribution values which would correspond to an exact power law (straight line)
    """
    if m == 0.0:
        return np.full_like(log_rank, np.inf)
    return (log_rank - b) / m


def calculate_expected_next_extreme(current_extreme: float, m: float):
    """
    Uses the linear regression parameters to project to more extreme values and calculates
    the expected next extreme values

    Parameters
    ----------
    current_extreme : float
        The best (right tail) or worst (left tail) extreme return value
    m : float
        The slope of the power law tail

    Returns
    -------
    next_extreme : float
        The next extreme value
    """
    return (current_extreme * m) / (1.0 + m)

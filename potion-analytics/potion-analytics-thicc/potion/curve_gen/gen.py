"""
This module provides the main functionality for generating the Kelly curves for a
given specified payout. This payout could represent a single option or a spread. These
curves depend on a probability distribution representing returns created from a set of
training data.
"""
import numpy as np
import pandas as pd

from scipy.optimize import brentq

from potion.curve_gen.builder import GeneratorConfigBuilder, GeneratorConfig
from potion.curve_gen.kelly import (probability_from_density, kelly_formula_derivative)
from potion.curve_gen.utils import (training_output_to_csv, training_output_to_convolution_config,
                                    training_output_to_payoff_config, add_pdf_csv_columns,
                                    add_curve_csv_rows)

from potion.curve_gen.training.distributions.skewed_students_t import skewed_t
from potion.curve_gen.training.train import (configure_training, train)
from potion.curve_gen.convolution.convolution import (configure_convolution, run_convolution,
                                                      get_pdf_arrays)
from potion.curve_gen.constraints.bounds import (configure_bounds, get_lower_bound, get_upper_bound)
from potion.curve_gen.kelly_fit.kelly_fit import (configure_fit, fit_kelly_curve)
from potion.curve_gen.payoff.payoff import (configure_payoff, get_payoff_odds)

"""
To customize the curve generator behavior, update the function entries in the table below from 
the caller's code
"""
_train_config = configure_training
_train_train = train
_conv_config = configure_convolution
_conv_run = run_convolution
_conv_get = get_pdf_arrays
_bounds_config = configure_bounds
_bounds_get_low = get_lower_bound
_bounds_get_up = get_upper_bound
_fit_config = configure_fit
_fit_curve = fit_kelly_curve
_payoff_config = configure_payoff
_payoff_get_odds = get_payoff_odds


def _perform_training(*args, dist=skewed_t, payoff_dict=None):
    """
    Performs the training process during the curve generation

    Parameters
    ----------
    args : arglist
        The initial guess for the optimizer when performing the training
    dist : scipy.stats.rv_continuous
        The probability distribution to use during the training process
    payoff_dict : dict
        (Optional) The payoff dict specifying the info used to calculate the curves. By default,
        this specifies a short put. This can be used to specify other individual options or an
        option spread. See potion.curve_gen.utils.make_payoff_dict for more info

    Returns
    -------
    conv_dfs : List[pandas.DataFrame]
        The DataFrames containing the output info from training
    conv_configs : List[ConvolutionConfig]
        The ConvolutionConfig objects to use during the convolution process
    payoff_configs : List[PayoffConfig]
        The PayoffConfig objects to use during curve generation
    """
    conv_dfs = _train_train(*args, dist=dist)
    conv_configs = training_output_to_convolution_config(conv_dfs, dist=dist)
    payoff_configs = training_output_to_payoff_config(conv_dfs, conv_configs,
                                                      payoff_dict=payoff_dict)
    return conv_dfs, conv_configs, payoff_configs


def _perform_convolution(conv_cfg, exps):
    """
    Performs the convolution process during the curve generation

    Parameters
    ----------
    conv_cfg : ConvolutionConfig
        The ConvolutionConfig object for the batch of curves
    exps : List[int]
        The expirations for the batch of curves

    Returns
    -------
    exp_days : List[int]
        The sorted expirations for the batch of curves
    """
    _conv_config(conv_cfg)
    exp_days = np.sort(exps)
    _conv_run(expiration_days=exp_days)

    return exp_days


def _kelly_derivative(premium: float, bet_frac: np.ndarray, prob_bins: np.ndarray):
    """
    Calculates the derivative of the function k so that we can run the optimizer and find
    where the derivative is equal to zero.

    Parameters
    ----------
    premium : float
        The premium to try as input
    bet_frac : numpy.ndarray
        The ndarray corresponding to the possible bet fractions of the bankroll from 0 to 1
    prob_bins : numpy.ndarray
        The bins of probability to use in the calculation

    Returns
    -------
    derivative: numpy.ndarray
        The value of the derivative being scored by the optimizer
    """
    return kelly_formula_derivative(prob_bins, _payoff_get_odds(premium), bet_frac)


def _generate_premiums(bet_fractions: np.ndarray, prob_bins: np.ndarray, bounds_dict=None):
    """
    Helper function to run the optimizer and generate the premium for each curve

    Parameters
    ----------
    bet_fractions : numpy.ndarray
        The array containing the X points of the generated curves
    prob_bins : numpy.ndarray
        The probability values at each point

    Returns
    -------
    opt_premiums : List[float]
        The Y values of the points on the Kelly curve
    """
    opt_premiums = []
    for bf_i, bf in enumerate(bet_fractions):

        if bounds_dict is None:
            bounds_dict = {}

        lower_bound = _bounds_get_low(bounds_dict, bf_i)
        upper_bound = _bounds_get_up(bounds_dict, bf_i)

        try:
            premium = brentq(_kelly_derivative, lower_bound, upper_bound,
                             args=(bf, prob_bins))

            opt_premiums.append(premium)
        except ValueError:
            if lower_bound < 0.0:
                opt_premiums.append(upper_bound)
            else:
                opt_premiums.append(lower_bound)

    return opt_premiums


def _generate_curves(payoff_cfg, expiration_days,
                     bet_fractions=np.linspace(0.0, 0.9999, 50)):
    """
    Helper function to generate curves for each convolution batch

    Parameters
    ----------
    payoff_cfg : List[PayoffConfig]
        The list of PayoffConfig objects for each strike
    expiration_days : numpy.ndarray
        The array containing all of the expiration days
    bet_fractions : numpy.ndarray
        (Optional. Default: numpy.linspace(0, 1, 50)) The array containing the X points
        of the generated curves

    Returns
    -------
    outputs : List[dict]
        The List of output dicts for each curve
    """
    # Gets the output PDFs from the convolution process
    pdf_x, pdfs_y = _conv_get()

    # Loop over the expirations. Looping is in reverse in case the caller has configured
    # constraints related to calendar arbitrage
    payoffs = list(dict.fromkeys(payoff_cfg))
    uexps = np.unique(expiration_days).tolist()
    tuple_list = [(exp, strike) for exp in reversed(uexps) for strike in payoffs]

    strikes = [cfg.option_legs[0]['strike'] for cfg in payoffs]

    shifted_strikes = pd.Series(strikes).shift(1).tolist()
    shifted_strikes_two = pd.Series(strikes).shift(2).tolist()
    last_strike_map = {current_strike: last_strike for current_strike, last_strike in zip(
        strikes, shifted_strikes)}
    next_last_strike_map = {current_strike: next_last_strike for current_strike, next_last_strike
                            in zip(strikes, shifted_strikes_two)}

    shfted_exps = pd.Series(uexps).shift(-1).tolist()
    next_exp_map = {current_exp: next_exp for current_exp, next_exp in zip(uexps, shfted_exps)}

    outputs = {exp: {strike: {} for strike in strikes} for exp in uexps}
    for day_index, (day_count, strike_payoff_cfg) in enumerate(tuple_list):

        strike = strike_payoff_cfg.option_legs[0]['strike']
        last_strike = last_strike_map[strike]
        next_last_strike = next_last_strike_map[strike]

        # Configure the payoff and calculate the probability
        _payoff_config(strike_payoff_cfg)
        pdf_index = uexps.index(day_count)
        pdf_y = pdfs_y[pdf_index]
        prob_bins = probability_from_density(pdf_x, pdf_y)

        if len(strike_payoff_cfg.option_legs) > 0:
            r = strike_payoff_cfg.option_legs[0]['r']
            q = strike_payoff_cfg.option_legs[0]['q']
        else:
            r = 0.0
            q = 0.0

        tau = day_count / 365.0

        if not np.isnan(last_strike):
            last_price_dict = outputs[day_count][last_strike]

            if 'prem' not in last_price_dict:
                last_price_curve = np.full_like(bet_fractions, np.nan)
            else:
                last_price_curve = last_price_dict['prem']
        else:
            last_price_curve = np.full_like(bet_fractions, np.nan)

        if not np.isnan(next_last_strike):
            next_last_price_dict = outputs[day_count][next_last_strike]

            if 'prem' not in next_last_price_dict:
                next_last_price_curve = np.full_like(bet_fractions, np.nan)
            else:
                next_last_price_curve = next_last_price_dict['prem']
        else:
            next_last_price_curve = np.full_like(bet_fractions, np.nan)

        bounds_dict = {
            'p_ii': last_price_curve,
            'p_iii': next_last_price_curve,
            'k_i': strike,
            'k_ii': last_strike,
            'k_iii': next_last_strike,
            's': 1.0,  # price is the current price when calculating curves
            'r': r,
            'q': q,
            'tau': tau
        }

        if not np.isnan(next_exp_map[day_count]):
            bounds_dict['exp_tau'] = (next_exp_map[day_count] - day_count) / 365.0

            next_exp_dict = outputs[next_exp_map[day_count]][strike]

            if 'prem' not in next_exp_dict:
                next_exp_price_curve = np.full_like(bet_fractions, np.nan)
            else:
                next_exp_price_curve = next_exp_dict['prem']

            bounds_dict['p_mm'] = next_exp_price_curve
        else:
            bounds_dict['p_mm'] = np.full_like(bet_fractions, np.nan)

        # Generate the premiums for the current probability and payoff
        opt_premiums = _generate_premiums(bet_fractions, prob_bins, bounds_dict=bounds_dict)

        # Fit A, B, C, D parameters to the curve
        fit_params = _fit_curve(bet_fractions, opt_premiums,
                                lower_bounds=(0.0, 0.0, 0.0, -100.0),
                                upper_bounds=(100.0, 100.0, 100.0, 100.0))

        # Save the outputs
        outputs[day_count][strike] = {
            'payoff': strike_payoff_cfg,
            'exp': day_count,
            'params': fit_params,
            'prem': opt_premiums
        }

    outs = [outputs[exp][strike.option_legs[0]['strike']] for exp in uexps for strike in payoffs]

    return outs


class Generator:
    """
    This class implements the major curve generation functions
    """

    def __init__(self):
        """
        Initializes the curve generator with the default configuration
        """
        self.config = GeneratorConfigBuilder().build_config()
        self.configure_curve_gen(self.config)

    def configure_curve_gen(self, config: GeneratorConfig):
        """
        Configures the curve generator with the specified config object

        Parameters
        ----------
        config : GeneratorConfig
            The curve generator configuration object

        Returns
        -------
        None
        """
        self.config = config
        _train_config(self.config.train_config)
        _bounds_config(self.config.bounds_config)
        _fit_config(self.config.fit_config)

    @staticmethod
    def generate_curves(initial_guess=(1.0, 3.5), bet_fractions=np.linspace(0.0, 0.9999, 50),
                        dist=skewed_t, payoff_dict=None):
        """
        Generates the Kelly curves based on the current configuration

        Parameters
        ----------
        initial_guess : List[float]
            (Optional. Default: [1.0, 3.5]) The initial guess for the distribution parameters in
            the optimizer during the training process
        bet_fractions : numpy.ndarray
            (Optional. Default: 50 points) The X-values to use as the points for the Kelly curves
        dist : scipy.stats.rv_continuous
            (Optional. Default: skewed_t) The probability distribution to use during the training
            process
        payoff_dict : dict
            (Optional. Default: None) The payoff dict specifying the info used to calculate the
            curves. By default, this specifies a short put. This can be used to specify other
            individual options or an option spread. See potion.curve_gen.utils.make_payoff_dict
            for more info

        Returns
        -------
        curves_df : pandas.DataFrame
            The DataFrame containing the information about each generated curve, used by the
            other tools
        pdf_df : pandas.DataFrame
            The DataFrame containing the information about the convolution PDFs, used by the
            other tools
        training_df : pandas.DataFrame
            The DataFrame containing the information about the training windows, used by the
            other tools
        """
        # Perform the training
        conv_dfs, conv_configs, payoff_configs = _perform_training(*initial_guess, dist=dist,
                                                                   payoff_dict=payoff_dict)

        # Run each convolution batch and save the output
        curves_df_rows = []
        column_data = []
        column_names = []
        for index, (df, conv_cfg, payoff_cfg) in enumerate(zip(conv_dfs, conv_configs,
                                                               payoff_configs)):
            # Perform the convolution process
            exp_days = _perform_convolution(conv_cfg, df['Expiration'].values)

            # Generate the Kelly curves
            outputs = _generate_curves(
                payoff_cfg, exp_days, bet_fractions=bet_fractions)

            # Record the values so the output DataFrames can be built later
            curves_df_rows.extend(add_curve_csv_rows(
                df, outputs, conv_cfg.dist_params, bet_fractions=bet_fractions))
            column_names, column_data = add_pdf_csv_columns(
                exp_days, column_names, column_data, df['Asset'].values[0],
                df['TrainingLabel'].values[0], get_pdfs_fcn=_conv_get)

        # Build the output DataFrames
        curves_df = pd.DataFrame(curves_df_rows)
        pdf_df = pd.concat(column_data, axis=1, keys=column_names)
        training_df = training_output_to_csv(conv_dfs)

        return curves_df, pdf_df, training_df


# Define a Global object with default values to be configured by the module user
_gen = Generator()

# Prebind the object's methods so the module can be used by object oriented and functional
# programmers alike
configure_curve_gen = _gen.configure_curve_gen
generate_curves = _gen.generate_curves

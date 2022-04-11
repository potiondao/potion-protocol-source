"""
This module contains all of the functions related to the Kelly Criterion which are helpful in
calculating common outputs
"""
import numpy as np

from typing import Union, List


def expected_value(probability: np.ndarray, payout: np.ndarray):
    """
    Calculates the expected value based on the specified probability values and their
    corresponding payouts. Each element in the array is a different outcome

    Parameters
    ----------
    probability : numpy.ndarray
        The probability values
    payout : numpy.ndarray
        The payout at the same points as the corresponding probability values

    Returns
    -------
    expected_value : float
        The expected (average) value
    """
    mult = np.multiply(probability, payout)
    return np.sum(mult)


def trapezoidal_rule(x1: float, y1: float, x2: float, y2: float):
    """
    Calculates a rough integral of a given function bin

    Parameters
    ----------
    x1 : float
        The x coordinate of the first point
    y1 : float
        f(x) of the first point
    x2 : float
        The x coordinate of the second point
    y2 : float
        f(x) of the second point

    Returns
    -------
    area : float
        Integral of f(x) between x1 and x2
    """
    return (x2 - x1) * (y1 + y2) / 2.0


def probability_from_density(sample_points: np.ndarray, probability: np.ndarray):
    """
    Calculates the probability in each bin for the given PDF function

    Parameters
    ----------
    sample_points : numpy.ndarray
        The X points of the PDF function
    probability : numpy.ndarray
        The Y points of the PDF function representing the density values

    Returns
    -------
    prob_bins : numpy.ndarray
        The probability in each bin
    """
    # Iterate over the PDF and calculate the probability in each bin
    prob_bins = np.full_like(probability, 0.0)
    for i in range(sample_points.size - 1):
        point = sample_points[i]
        next_point = sample_points[i + 1]
        prob = probability[i]
        next_prob = probability[i + 1]
        prob_bins[i + 1] = trapezoidal_rule(point, prob, next_point, next_prob)

    return prob_bins


def kelly_formula(prob_bins: np.ndarray, odds: np.ndarray, bet_amount):
    """
    Calculates the Kelly Formula for a given probability PDF and payout function. The formula
    takes an amount to bet as input.
    
    If a person betting has M starting capital and bets xM amount on the bet, the expected
    value of the log of the capital on the next step in time is:
    E = ln(M) + sum[p_i * ln(1 + b_i * x)]
    
    where p_i is the probability for outcome i and b_i is the betting odds paid out. We want to
    maximize the sum term, which is the growth rate of the capital. With the optimal fraction
    x, the expected growth rate of the bet on the next time step is given by e^x

    Parameters
    ----------
    prob_bins : numpy.ndarray
        The probability bins in the histogram
    odds : numpy.ndarray
        The betting odds payout function values at each sample point
    bet_amount : Union[float, numpy.ndarray]
        The amount of the starting capital to bet

    Returns
    -------
    kelly_out : numpy.ndarray
        The Kelly Formula value for the specified bet_amount
    """
    if type(bet_amount) == np.ndarray:
        if bet_amount.ndim == 1:
            bet_amount = bet_amount.reshape(bet_amount.shape[0], -1)
        return np.sum(prob_bins * np.log(1.0 + odds * bet_amount), axis=1)
    else:
        return np.sum(prob_bins * np.log(1.0 + odds * bet_amount))


def kelly_formula_derivative(prob_bins: np.ndarray, odds: np.ndarray, bet_amount):
    """
    Calculates the derivative of the Kelly formula. Sometimes, it is more convenient to look
    at the derivative because it is used neatly with optimization logic

    Parameters
    ----------
    prob_bins : numpy.ndarray
        The probability bins in the histogram
    odds : numpy.ndarray
        The betting odds payout function values at each sample point
    bet_amount : numpy.ndarray
        The amount of the starting capital to bet

    Returns
    -------
    d_kelly_out : numpy.ndarray
        The derivative of the Kelly Formula value for the specified bet_amount
    """
    # Iterate over the PDF and calculate the probability in each bin
    # prob_bins = np.full_like(probability, 0.0)
    if type(bet_amount) == np.ndarray:
        bet_amount = bet_amount.reshape(bet_amount.shape[0], -1)
        return np.sum((prob_bins * odds) / (1.0 + odds * bet_amount), axis=1)
    else:
        arr_sum = np.sum((prob_bins * odds) / (1.0 + odds * bet_amount))
        return arr_sum


def cagr_to_growth_per_bet(cagr: float, bets_in_year: float):
    """
    This function is given a target compound annual growth rate and the number of bets
    performed in one year. It calculates the expected growth rate per bet according to
    the two values.

    Parameters
    ----------
    cagr : float
        The compound annual growth rate
    bets_in_year : float
        The number of bets performed in one year

    Returns
    -------
    growth_per_bet : float
        The expected growth rate of performing the bet once

    """
    nth_root = 1.0 / bets_in_year
    return np.power((cagr / 100.0) + 1, nth_root)


def growth_per_bet_to_cagr(gpb: float, bets_in_year: float):
    """
    Converts the growth per bet and the number of bets in a year into the compound annual
    growth rate (CAGR)

    Parameters
    ----------
    gpb : float
        The growth per bet
    bets_in_year : float
        The number of times the bet happens in a year

    Returns
    -------
    cagr : float
        The compound annual growth rate
    """
    return (np.power(gpb, bets_in_year) - 1.0) * 100.0


def kelly_value_to_growth_per_bet(kelly_value):
    """
    Converts the value output from the Kelly formula into the expected growth per bet

    Parameters
    ----------
    kelly_value : Union[float, numpy.ndarray]
        The value output from the kelly formula

    Returns
    -------
    gpb : Union[float, numpy.ndarray]
        The expected (average) growth per bet
    """
    return np.exp(kelly_value)


def expected_growth_to_log_growth(growth: float):
    """
    This function takes the expected growth rate each time the bet is performed and
    calculates the natural log

    Parameters
    ----------
    growth : float
        The expected growth rate

    Returns
    -------
    log_g : float
        The natural log of the growth rate
    """
    return np.log(growth)


def evaluate_premium_curve(fit_params: List[float], util: Union[float, np.ndarray]):
    """
    Function to calculate the premium of a fit curve

    Parameters
    -----------
    fit_params : List[float]
        The A, B, C, D values of the curve
    util : Union[float, numpy.ndarray]
        The util percentage that is the function input

    Raises
    -----------
    ValueError
        If the util is not between 0.0 and 1.0, or if the fit_params are not positive numbers

    Returns
    -----------
    Union[float, numpy.ndarray]
        The premium to charge. Float or ndarray depending on the type of util parameter
    """
    a = fit_params[0]
    b = fit_params[1]
    c = fit_params[2]
    d = fit_params[3]

    if np.isscalar(util):
        if util > 1.0 or util < 0.0:
            raise ValueError('Util must be between 0 and 1.0: {}'.format(util))
    if a < 0.0 or b < 0.0 or c < 0.0:
        raise ValueError('Fit Parameters must be positive: {}'.format(fit_params))

    return a * util * np.cosh(b * util ** c) + d

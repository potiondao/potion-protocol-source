"""
This module supplies the helper functions used to calculate the payoff of an option or
spread of options. Two implementations of payoff functions are supplied here. These are
expiration_only, which calculates the option payoff at expiration and
black_scholes_payoff which uses the Generalized Black-Scholes equation.
"""
import numpy as np
from potion.curve_gen.payoff.black_scholes import call, put


def _bs_long_call(x_points: np.ndarray, option_leg: dict, premium=0.0):
    """
    Calculates the payoff for a long call using the Black Scholes equation

    Parameters
    ----------
    x_points : numpy.ndarray
        The possible prices of the underlying asset
    option_leg : dict
        Dict containing the parameters of the option leg
    premium : float
        The premium collected for the option leg

    Returns
    -------
    payoff : numpy.ndarray
        The payoff for a long call
    """
    price, greeks = call(x_points, option_leg['strike'], option_leg['t'], option_leg['sigma'],
                         option_leg['r'], option_leg['q'])
    return (price - premium) * option_leg['amt']


def _bs_short_call(x_points: np.ndarray, option_leg: dict, premium=0.0):
    """
    Calculates the payoff for a short call using the Black Scholes equation

    Parameters
    ----------
    x_points : numpy.ndarray
        The possible prices of the underlying asset
    option_leg : dict
        Dict containing the parameters of the option leg
    premium : float
        The premium collected for the option leg

    Returns
    -------
    payoff : numpy.ndarray
        The payoff for a short call
    """
    price, greeks = call(x_points, option_leg['strike'], option_leg['t'], option_leg['sigma'],
                         option_leg['r'], option_leg['q'])
    return (premium - price) * option_leg['amt']


def _bs_long_put(x_points: np.ndarray, option_leg: dict, premium=0.0):
    """
    Calculates the payoff for a long put using the Black Scholes equation

    Parameters
    ----------
    x_points : numpy.ndarray
        The possible prices of the underlying asset
    option_leg : dict
        Dict containing the parameters of the option leg
    premium : float
        The premium collected for the option leg

    Returns
    -------
    payoff : numpy.ndarray
        The payoff for a long put
    """
    price, greeks = put(x_points, option_leg['strike'], option_leg['t'], option_leg['sigma'],
                        option_leg['r'], option_leg['q'])
    return (price - premium) * option_leg['amt']


def _bs_short_put(x_points: np.ndarray, option_leg: dict, premium=0.0):
    """
    Calculates the payoff for a short put using the Black Scholes equation

    Parameters
    ----------
    x_points : numpy.ndarray
        The possible prices of the underlying asset
    option_leg : dict
        Dict containing the parameters of the option leg
    premium : float
        The premium collected for the option leg

    Returns
    -------
    payoff : numpy.ndarray
        The payoff for a short put
    """
    price, greeks = put(x_points, option_leg['strike'], option_leg['t'], option_leg['sigma'],
                        option_leg['r'], option_leg['q'])
    return (premium - price) * option_leg['amt']


def black_scholes_payoff(x_points: np.ndarray, option_leg: dict, premium=0.0):
    """
    Calculates the payoff for an option leg using the Black Scholes equation

    Parameters
    ----------
    x_points : numpy.ndarray
        The possible prices of the underlying asset
    option_leg : dict
        Dict containing the parameters of the option leg
    premium : float
        The premium collected for the option leg

    Returns
    -------
    payoff : numpy.ndarray
        The payoff for the option leg
    """
    look_up_table = {
        'call': {
            'long': _bs_long_call,
            'short': _bs_short_call
        },
        'put': {
            'long': _bs_long_put,
            'short': _bs_short_put
        }
    }

    return look_up_table[option_leg['type']][option_leg['dir']](x_points, option_leg, premium)


def expiration_only(x_points: np.ndarray, option_leg: dict, premium=0.0):
    """
    Calculates the payoff for an option at expiration

    Parameters
    ----------
    x_points : numpy.ndarray
        The possible prices of the underlying asset
    option_leg : dict
        Dict containing the parameters of the option leg
    premium : float
        The premium collected for the option leg

    Returns
    -------
    payoff : numpy.ndarray
        The payoff for the option leg
    """
    strike = option_leg['strike']
    amount = option_leg['amt']

    look_up_table = {
        'call': {
            'long': np.where(x_points >= strike, (amount * x_points - strike * amount), 0.0) - (
                    amount * premium),
            'short': np.where(x_points >= strike, (-amount * x_points + strike * amount), 0.0) + (
                    amount * premium)
        },
        'put': {
            'long': np.where(x_points <= strike, (-amount * x_points + strike * amount), 0.0) - (
                    amount * premium),
            'short': np.where(x_points <= strike, (amount * x_points - strike * amount), 0.0) + (
                    amount * premium)
        }
    }

    return look_up_table[option_leg['type']][option_leg['dir']]

"""
This module is responsible for implementing the Black Scholes equation to model the payoff of an
option. The version of the equation that's used is called the Generalized Black Scholes. This
version includes dividends for the underlying so that if the user wants to calculate the
payoff for a crypto which has a cash flow attached (like staking or something similar) they can
set the equivalent annual interest rate in the formula
"""
import numpy as np
from typing import Union
from scipy.stats import norm


def check_div_zero(value, close_value=1e-10):
    """
    Checks if the value passed is zero. If the value is zero, it is replaced with a float that
    is extremely close to zero. When doing lots of calculations, this is faster than using the
    exception stack to check for ZeroDivisionError

    Parameters
    ----------
    value : float or numpy.ndarray
        The value to check if it is zero
    close_value : float
        The value to replace with. Cannot be 0.0. (Default: 1e-30)

    Returns
    -------
    value : float or numpy.ndarray
        The value with zero replaced
    """

    if isinstance(value, np.ndarray):
        value[value == 0.0] = close_value
    elif value == 0.0:
        value = close_value

    return value


def _d1(s, r: float, q: float, k: float, tau: float, sigma: float):
    """
    Calculates the d1 parameter of the Black-Scholes equation (sometimes called d+)

    Parameters
    ----------
    s : float
        The current price of the underlying asset
    r : float
        The interest rate (annualized) in the currency which the option was struck
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    k : float
        The strike price of the option
    tau : float
        The time in years from now until the option expiration
    sigma : float
        The volatility of the underlying asset

    Returns
    -------
    d1 : float
        The output of the d1 calculation
    """
    return (np.log(s / k) + ((r - q) + (sigma * sigma / 2.0)) * tau) / (sigma * np.sqrt(tau))


def _d2(d_1, sigma: float, tau: float):
    """
    Calculates the d2 parameter of the Black-Scholes equation (sometimes called d-)

    Parameters
    ----------
    d_1 : float
        The output of the d1 calculation so that it is not calculated twice
    sigma : float
        The volatility of the underlying asset
    tau : float
        The time in years from now until the option expiration

    Returns
    -------
    d2 : float
        The output of the d2 calculation
    """
    return d_1 - sigma * np.sqrt(tau)


def _gamma(s: float, tau: float, sigma: float, q: float, d_1: float):
    """
    Calculates the Greek corresponding to realized volatility. Same calculation for both
    Calls and Puts

    Parameters
    ----------
    s : float
        The current price of the underlying asset
    tau : float
        The time in years from now until the option expiration
    sigma : float
        The volatility of the underlying asset
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    d_1 : float
        The d1 parameter of the BS equation

    Returns
    -------
    gamma : float
        The second derivative of the option with respect to the underlying price
    """
    return (1.0 / (s * sigma * np.sqrt(tau))) * np.exp(-q * tau) * norm.pdf(d_1)


def _vega(s: float, tau: float, q: float, d_1: float):
    """
    Calculate the Greek corresponding to a change in volatility. Same calculation for both
    Calls and Puts.

    Parameters
    ----------
    s : float
        The current price of the underlying asset
    tau : float
        The time in years from now until the option expiration
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    d_1 : float
        The d1 parameter of the BS equation

    Returns
    -------
    vega : float
        The derivative of the option with respect to changes in implied volatility
    """
    return np.sqrt(tau) * s * np.exp(-q * tau) * norm.pdf(d_1)


# Gamma and Vega are the same for both Calls and Puts
call_gamma = _gamma
call_vega = _vega
put_gamma = _gamma
put_vega = _vega


def call_delta(tau: float, q: float, d_1: float):
    """
    Calculates the Greek corresponding to change in price for a Call

    Parameters
    ----------
    tau : float
        The time in years from now until the option expiration
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    d_1 : float
        The d1 parameter of the BS equation

    Returns
    -------
    delta : float
        The derivative of the option with respect to changes in the underlying price
    """
    return np.exp(-q * tau) * norm.cdf(d_1)


def call_theta(s: float, k: float, tau: float, sigma: float, r: float, q: float,
               d_1: float, d_2: float):
    """
    Calculates the Greek corresponding to the passage of time for a Call

    Parameters
    ----------
    s : float
        The current price of the underlying asset
    k : float
        The strike price of the option
    tau : float
        The time in years from now until the option expiration
    sigma : float
        The volatility of the underlying asset
    r : float
        The interest rate (annualized) in the currency which the option was struck
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    d_1 : float
        The d1 parameter of the BS equation
    d_2 : float
        The d2 parameter of the BS equation

    Returns
    -------
    theta : float
        The derivative of the option with respect to changes in time
    """
    strike_term = -k * r * np.exp(-r * tau) * norm.cdf(d_2)
    price_term = s * q * np.exp(-q * tau) * norm.cdf(d_1)
    sigma_term = sigma * -s * np.exp(-q * tau) * norm.pdf(d_1) / (2.0 * np.sqrt(tau))
    return price_term + strike_term + sigma_term


def call_rho_r(k: float, tau: float, r: float, d_2: float):
    """
    Sets the Greek corresponding to a change in the interest rate for a Call

    Parameters
    ----------
    k : float
        The strike price of the option
    tau : float
        The time in years from now until the option expiration
    r : float
        The interest rate (annualized) in the currency which the option was struck
    d_2 : float
        The d2 parameter of the BS equation

    Returns
    -------
    rho_r : float
        The derivative of the option with respect to changes in the interest rate
    """
    return tau * k * np.exp(-r * tau) * norm.cdf(d_2)


def call_rho_q(s: float, tau: float, q: float, d_1: float):
    """
    Sets the Greek corresponding to a change in the interest rate from
    cash flows (like dividends) for a Call

    Parameters
    ----------
    s : float
        The current price of the underlying asset
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    tau : float
        The time in years from now until the option expiration
    d_1 : float
        The d1 parameter of the BS equation

    Returns
    -------
    rho_q : float
        The derivative of the option with respect to changes in the interest rate from
        cash flows
    """
    return -tau * s * np.exp(-q * tau) * norm.cdf(d_1)


def put_delta(tau: float, q: float, d_1: float):
    """
    Calculates the Greek corresponding to change in price for a Put

    Parameters
    ----------
    tau : float
        The time in years from now until the option expiration
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    d_1 : float
        The d1 parameter of the BS equation

    Returns
    -------
    delta : float
        The derivative of the option with respect to changes in the underlying price
    """
    return -np.exp(-q * tau) * norm.cdf(-d_1)


def put_theta(s: float, k: float, tau: float, sigma: float, r: float, q: float,
              d_1: float, d_2: float):
    """
    Calculates the Greek corresponding to the passage of time for a Put

    Parameters
    ----------
    s : float
        The current price of the underlying asset
    k : float
        The strike price of the option
    tau : float
        The time in years from now until the option expiration
    sigma : float
        The volatility of the underlying asset
    r : float
        The interest rate (annualized) in the currency which the option was struck
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    d_1 : float
        The d1 parameter of the BS equation
    d_2 : float
        The d2 parameter of the BS equation

    Returns
    -------
    theta : float
        The derivative of the option with respect to changes in time
    """
    strike_term = k * r * np.exp(-r * tau) * norm.cdf(-d_2)
    price_term = s * q * np.exp(-q * tau) * norm.cdf(-d_1)
    sigma_term = (sigma / (2.0 * np.sqrt(tau))) * s * np.exp(-q * tau) * norm.pdf(d_1)
    return strike_term - price_term - sigma_term


def put_rho_r(k: float, tau: float, r: float, d_2: float):
    """
    Calculates the Greek corresponding to a change in the interest rate for a Put

    Parameters
    ----------
    k : float
        The strike price of the option
    tau : float
        The time in years from now until the option expiration
    r : float
        The interest rate (annualized) in the currency which the option was struck
    d_2 : float
        The d2 parameter of the BS equation

    Returns
    -------
    rho_r : float
        The derivative of the option with respect to changes in the interest rate
    """
    return -tau * k * np.exp(-r * tau) * norm.cdf(-d_2)


def put_rho_q(s: float, tau: float, q: float, d_1: float):
    """
    Calculates the Greek corresponding to a change in the interest rate from
    cash flows (like dividends) for a Put

    Parameters
    ----------
    s : float
        The current price of the underlying asset
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    tau : float
        The time in years from now until the option expiration
    d_1 : float
        The d1 parameter of the BS equation

    Returns
    -------
    rho_q : float
        The derivative of the option with respect to changes in the interest rate from
        cash flows
    """
    return tau * s * np.exp(-q * tau) * norm.cdf(-d_1)


def call(s: Union[float, np.ndarray], k: Union[float, np.ndarray], tau: float,
         sigma: Union[float, np.ndarray], r: float, q: float, calculate_greeks=False):
    """
    Calculates the price of the Call and optionally all of the Greeks associated with the option
    and returns the price and a dict containing the greeks.

    Parameters
    ----------
    s : Union[float, np.ndarray]
        The current price of the underlying asset
    k : Union[float, np.ndarray]
        The strike price of the option
    tau : float
        The time in years from now until the option expiration
    sigma : Union[float, np.ndarray]
        The volatility of the underlying asset
    r : float
        The interest rate (annualized) in the currency which the option was struck
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    calculate_greeks : bool
        Flag indicating whether the greek values should be calculated or not (Default: False)

    Returns
    -------
    call_price : float
        The option price
    greeks : dict
        A dict containing the Greek values
    """
    # If parameter is 0 make it just above 0 so we don't get NaNs
    s = check_div_zero(s)
    k = check_div_zero(k)
    sigma = check_div_zero(sigma)
    tau = check_div_zero(tau)

    # Calculate the d values for the equation
    d1 = _d1(s, r, q, k, tau, sigma)
    d2 = _d2(d1, sigma, tau)

    # Calculate the price
    strike_term = k * np.exp(-r * tau) * norm.cdf(d2)
    price_term = s * np.exp(-q * tau) * norm.cdf(d1)

    call_price = price_term - strike_term

    # Calculate the greeks
    if calculate_greeks:
        greeks = {
            'delta': call_delta(tau, q, d1),
            'gamma': call_gamma(s, tau, sigma, q, d1),
            'theta': call_theta(s, k, tau, sigma, r, q, d1, d2),
            'vega': call_vega(s, tau, q, d1),
            'rho_r': call_rho_r(k, tau, r, d2),
            'rho_q': call_rho_q(s, tau, q, d1)
        }
    else:
        greeks = {}

    return call_price, greeks


def put(s: Union[float, np.ndarray], k: Union[float, np.ndarray], tau: float,
        sigma: Union[float, np.ndarray], r: float, q: float, calculate_greeks=False):
    """
    Calculates the price of the Put and optionally all of the Greeks associated with the
    option and returns the price and a dict containing the greeks.

    Parameters
    ----------
    s : Union[float, np.ndarray]
        The current price of the underlying asset
    k : Union[float, np.ndarray]
        The strike price of the option
    tau : float
        The time in years from now until the option expiration
    sigma : Union[float, np.ndarray]
        The volatility of the underlying asset
    r : float
        The interest rate (annualized) in the currency which the option was struck
    q : float
        The rate of return (annualized) of cash flow from the underlying (like a dividend)
    calculate_greeks : bool
        Flag indicating whether the greek values should be calculated or not (Default: False)

    Returns
    -------
    put_price : float
        The option price
    greeks : dict
        A dict containing the Greek values
    """
    # If parameter is 0 make it just above 0 so we don't get NaNs
    s = check_div_zero(s)
    k = check_div_zero(k)
    sigma = check_div_zero(sigma)
    tau = check_div_zero(tau)

    # Calculate the d values for the equation
    d1 = _d1(s, r, q, k, tau, sigma)
    d2 = _d2(d1, sigma, tau)

    # Calculate the price
    strike_term = k * np.exp(-r * tau) * norm.cdf(-d2)
    price_term = s * np.exp(-q * tau) * norm.cdf(-d1)

    put_price = strike_term - price_term

    # Calculate the greeks
    if calculate_greeks:
        greeks = {
            'delta': put_delta(tau, q, d1),
            'gamma': put_gamma(s, tau, sigma, q, d1),
            'theta': put_theta(s, k, tau, sigma, r, q, d1, d2),
            'vega': put_vega(s, tau, q, d1),
            'rho_r': put_rho_r(k, tau, r, d2),
            'rho_q': put_rho_q(s, tau, q, d1)
        }
    else:
        greeks = {}

    return put_price, greeks

#!/usr/bin/env python3
"""Module with functions to utilize/calculate Kelly Criteria
https://en.wikipedia.org/wiki/Kelly_criterion"""
import warnings
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, fminbound

convert_zero_to_very_small_value = lambda x: 0.1 ** 100 if x == 0 else x
convert_zero_to_very_small_value = np.vectorize(convert_zero_to_very_small_value)

def put_option_payout(expiration_price, strike, premium):
    """Function to calculate payout for the put option
    Args:
        expiration_price (float):
            Price at the put expiration date. Expressed as pct from current price.
            e.g. 0.1 stands for 10% above current
        strike (float):
            Strike price. Expressed as pct from current price.
            e.g. 1.1 stands for 10% above current
        premium (float):
            Option Premium. Expressed as pct from current price.
            e.g. 0.1 stands for 10% above current
    Returns:
        payout (float):
            1 is 100%
    """
    if expiration_price < (strike - 1):
        res = -abs(expiration_price - (strike - 1)) / strike + premium
    else:
        res = premium

    # it's not possible to loose more than 100%
    if res < -1:
        res = -1

    return res


def call_option_payout(expiration_price, strike, premium):
    """Function to calculate payout for the call option
    Args:
        expiration_price (float):
            Price at the put expiration date. Expressed as pct from current price.
            e.g. 0.1 stands for 10% above current
        strike (float):
            Strike price. Expressed as pct from current price.
            e.g. 1.1 stands for 10% above current
        premium (float):
            Option Premium. Expressed as pct from current price.
            e.g. 0.1 stands for 10% above current
    Returns:
        payout (float):
            1 is 100%
    """
    if expiration_price > (strike - 1):
        res = -abs(expiration_price - (strike - 1)) / strike + premium
    else:
        res = premium

    # it's not possible to loose more than 100%
    if res < -1:
        res = -1

    return res


def get_curve_df(coef_a, coef_b, coef_c, coef_d, n_samples):
    """Function to calculate y(x) = a*x*cosh(b*x**c) + d
    y - premium, x - utilization (util)
    Args:
        a (float):
            coefficient
        b (float):
            coefficient
        c (float):
            coefficient
        d (float):
            coefficient
        resolution (float):
            Number of the points.
            The Higher the better

    Returns:
        curve_df (pd.DataFrame):
            df with Columns: "util", "premium"
    """
    y_axis = []
    x_axis = np.linspace(0.0, 1, n_samples)
    for x_val in x_axis:
        y_axis.append(coef_a * x_val * np.cosh(coef_b * (x_val ** coef_c)) + coef_d)
    return pd.DataFrame({"util": x_axis, "premium": y_axis})


def kelly_curve(coef_a, coef_b, coef_c, coef_d, x_val):
    """Function which describes Kelly Curve"""
    return coef_a * x_val * np.cosh(coef_b * (x_val ** coef_c)) + coef_d


def fit_curve_parameters(utils, raw_premiums):
    """Get fitted params for the kelly_curve functions
    source of the warning: Covariance of the parameters could not be estimated"""
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',
            message="Covariance of the parameters could not be estimated")
        warnings.filterwarnings("ignore",
            message="overflow encountered in cosh")
        warnings.filterwarnings("ignore",
            message="invalid value encountered in double_scalars")
        fit_params, _ = curve_fit(
            lambda t, a, b, c, d: a * t * np.cosh(b * (t ** c)) + d,
            utils,
            raw_premiums,
            maxfev=100000,
            xtol=1*10**(-2)
        )
    return fit_params


def get_kelly_log_expected_payout(
    underlying_returns, strike, premium, util, option_type="put"
):
    """Function to calculate expected payout with the help of Kelly Criteria
    Args:
        underlying_returns (pd.DataFrame):
            df with columns: return, freq
        strike (float):
            Strike price. Expressed as pct from current price.
            e.g. 1.1 stands for 10% above current
        premium (float):
            Option Premium. Expressed as pct from current price.
            e.g. 0.1 stands for 10% above current
        util (float):
            From 0 to 1. Utilization

    Returns:
        log_expected_payout (float):
            How much do we get
    """
    if isinstance(underlying_returns, pd.Series):
        underlying_returns_array = underlying_returns.values
    else:
        underlying_returns_array = underlying_returns

    if option_type == "put":
        payoff_array = np.array(
            [
                put_option_payout(tmp_return, strike, premium)
                for tmp_return in underlying_returns_array
            ]
        )
    elif "call" in option_type:
        payoff_array = np.array(
            [
                call_option_payout(tmp_return, strike, premium)
                for tmp_return in underlying_returns_array
            ]
        )
    else:
        raise ValueError(
            f'Wrong option_type: {option_type}. Should be "put" or "call".'
        )

    # workaround to deal with zeros
    bankroll_array = util * payoff_array + 1
    bankroll_array = convert_zero_to_very_small_value(bankroll_array)

    log_bankroll_array = np.log(bankroll_array)

    return np.sum(log_bankroll_array) / len(underlying_returns_array)


def get_kelly_derivative(
    premium, underlying_returns, strike, util, option_type="put", return_abs_value=False
):
    """Function to calculate derivative  of the expected payout with the help of Kelly Criteria
    Args:
        premium (float):
            Option Premium. Expressed as pct from current price.
            Set as the first arg to pass to scipy.brentq later on
            e.g. 0.1 stands for 10% above current
        underlying_returns (np.array or list or pd.Series):
            sequence of returns
        strike (float):
            Strike price. Expressed as pct from current price.
            e.g. 1.1 stands for 10% above current
        util (float):
            From 0 to 1. Utilization

    Returns:
        dk_du (float):
            first derivative of the log_expected_payout by util
    """
    if isinstance(underlying_returns, pd.Series):
        underlying_returns_array = underlying_returns.values
    else:
        underlying_returns_array = underlying_returns
    if option_type == "put":
        payoff_array = np.array(
            [
                put_option_payout(tmp_return, strike, premium)
                for tmp_return in underlying_returns_array
            ]
        )
    elif "call" in option_type:
        payoff_array = np.array(
            [
                call_option_payout(tmp_return, strike, premium)
                for tmp_return in underlying_returns_array
            ]
        )
    else:
        raise ValueError(
            f'Wrong option_type: {option_type}. Should be "put" or "call".'
        )

    # workaround to deal with zeros
    bankroll_array = util * payoff_array + 1
    # bankroll_array = convert_zero_to_very_small_value(bankroll_array)

    # produces warning: invalid value in double_scalars
    with np.errstate(divide='ignore'):
        dk_du = np.sum(payoff_array / bankroll_array) / len(payoff_array)
    if return_abs_value:
        dk_du = abs(dk_du)

    return dk_du


def get_kelly_curve(underlying_returns, strike, number_of_utils=100, option_type="put"):
    """Rename to get_kelly_curve_df
        Function to find kelly optimal curve for all utils
    Args:
        underlying_returns (np.array or list or pd.Series):
            sequence of returns
        strike (float):
            Strike price. Expressed as pct from current price.
            e.g. 1.1 stands for 10% above current
        number_of_utils (int):
            Number of utils on the [0, 1] segment

    Returns:
        kelly_curve_df (pd.DataFrame):
            first derivative of the log_expected_payout by util
    """

    utils = np.linspace(0, 1, number_of_utils)
    premiums = []
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",
            message="invalid value encountered in double_scalars")
        for util in utils:

            optimal_premium = fminbound(
                get_kelly_derivative,
                0.0,
                1.0,
                args=(underlying_returns, strike, util, option_type, True),
            )

            premiums.append(optimal_premium)
    kelly_curve_df = pd.DataFrame()
    kelly_curve_df["util"] = utils
    kelly_curve_df["premium"] = premiums
    kelly_curve_df.set_index("util").head()

    return kelly_curve_df


def get_premiums_list_with_all_calculations(
    utils, premium_offset=0, fit_params=None, **kwargs
):
    """Got Daily Premiums list from the very start

    Args:
        utils (list):
            list of utils
        duration (int):
            option days before expiration
        simulation_length_days (int):
            days
        premium_offset (float):
            pct offset
        fit_params (list):
            list of curve params

    **kwargs:
        bonding_curve_resolution (int):
            Number of utils on the [0, 1] segment
        underlying_n_daily_returns (np.array or list or pd.Series):
            sequence of returns
        strike (float):
            Strike price. Expressed as pct from current price.
            e.g. 1.1 stands for 10% above current

    Returns:
        daily_premiums (list), kelly_curve_df (pd.DataFrame), fit_params (list):

    """
    if fit_params is None:
        if "option_type" not in kwargs:
            kwargs["option_type"] = "put"
        kelly_curve_df = get_kelly_curve(
            kwargs["underlying_n_daily_returns"],
            kwargs["strike"],
            number_of_utils=kwargs["bonding_curve_resolution"],
            option_type=kwargs["option_type"],
        )
        kelly_curve_df["premium"] *= 1 + premium_offset

        fit_params = fit_curve_parameters(
            kelly_curve_df["util"], kelly_curve_df["premium"]
        )
    else:
        kelly_curve_df = None

    cycle_premiums = kelly_curve(
        *fit_params, np.array([util for util in utils if util != 0])
    )

    # create daily premiums based on cycle_premiums and utils
    daily_premiums = []
    cycle_index = 0
    for util in utils:
        if util == 0:
            daily_premiums.append(0)
        else:
            daily_premiums.append(cycle_premiums[cycle_index])
            cycle_index += 1
    daily_premiums = np.array(daily_premiums)
    # daily_premiums = daily_premiums * (1 + premium_offset)

    return daily_premiums, kelly_curve_df, fit_params

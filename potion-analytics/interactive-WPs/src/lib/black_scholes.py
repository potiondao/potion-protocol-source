#!/usr/bin/env python3
"""Module with functions to utilize/calculate Black-Scholes based option premium
https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model"""

import math
import scipy.stats


def calculate_d1(
    yearly_returns_std,
    years_to_expiry,
    strike_price,
    spot_price=1,
    risk_free_interest_rate=0.01,
):
    """Calculates the d1 parameter of the Black-Scholes equation (sometimes called d+)
    Args:
        yearly_returns_std (float):
            The volatility of the underlying asset, Annualized.
        years_to_expiry (int):
            The time in years from now until the option expiration
        strike_price (float):
            The strike price of the option
        spot_price (float):
            The current price of the underlying asset
        risk_free_interest_rate (float):
            The interest rate (annualized) in the currency which the option was struck

    Returns:
        payout (float):
            Expressed as pct from current price
    """
    return (
        math.log(spot_price / strike_price)
        + (risk_free_interest_rate + yearly_returns_std ** 2 / 2.0) * years_to_expiry
    ) / (yearly_returns_std * math.sqrt(years_to_expiry))


def calculate_d2(
    yearly_returns_std,
    years_to_expiry,
    strike_price,
    spot_price=1,
    risk_free_interest_rate=0.01,
):
    """Calculates the d1 parameter of the Black-Scholes equation (sometimes called d+)
    Args:
        yearly_returns_std (float):
            The volatility of the underlying asset, Annualized.
        years_to_expiry (int):
            The time in years from now until the option expiration
        strike_price (float):
            The strike price of the option
        spot_price (float):
            The current price of the underlying asset
        risk_free_interest_rate (float):
            The interest rate (annualized) in the currency which the option was struck

    Returns:
        payout (float):
            Expressed as pct from current price
    """
    return (
        calculate_d1(
            yearly_returns_std,
            years_to_expiry,
            strike_price,
            spot_price,
            risk_free_interest_rate
        )
        - yearly_returns_std * math.sqrt(years_to_expiry)
    )


def calculate_bs_call_premium(
    yearly_returns_std,
    years_to_expiry,
    strike_price,
    spot_price=1,
    risk_free_interest_rate=0.01,
):
    """Calculates the d1 parameter of the Black-Scholes equation (sometimes called d+)
    Args:
        yearly_returns_std (float):
            The volatility of the underlying asset, Annualized.
        years_to_expiry (int):
            The time in years from now until the option expiration
        strike_price (float):
            The strike price of the option
        spot_price (float):
            The current price of the underlying asset
        risk_free_interest_rate (float):
            The interest rate (annualized) in the currency which the option was struck

    Returns:
        payout (float):
            Expressed as pct from current price
    """
    # questionable way to fix the cases when std of returns sometimes is zero
    if not yearly_returns_std > 0:
        yearly_returns_std = 1e-10

    return spot_price * scipy.stats.norm.cdf(
        calculate_d1(
            yearly_returns_std,
            years_to_expiry,
            strike_price,
            spot_price,
            risk_free_interest_rate
        )
    ) - strike_price * math.exp(
        -risk_free_interest_rate * years_to_expiry
    ) * scipy.stats.norm.cdf(
        calculate_d2(
            yearly_returns_std,
            years_to_expiry,
            strike_price,
            spot_price,
            risk_free_interest_rate
        )
    )


def calculate_bs_put_premium(
    yearly_returns_std,
    years_to_expiry,
    strike_price,
    spot_price=1,
    risk_free_interest_rate=0.01,
):
    """Calculates the d1 parameter of the Black-Scholes equation (sometimes called d+)
    Args:
        yearly_returns_std (float):
            The volatility of the underlying asset, Annualized.
        years_to_expiry (int):
            The time in years from now until the option expiration
        strike_price (float):
            The strike price of the option
        spot_price (float):
            The current price of the underlying asset
        risk_free_interest_rate (float):
            The interest rate (annualized) in the currency which the option was struck

    Returns:
        payout (float):
            Expressed as pct from current price
    """
    return (
        strike_price * math.exp(-risk_free_interest_rate * years_to_expiry)
        - spot_price
        + calculate_bs_call_premium(
            yearly_returns_std,
            years_to_expiry,
            strike_price,
            spot_price,
            risk_free_interest_rate
        )
    )

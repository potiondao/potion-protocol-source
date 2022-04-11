"""
This module contains functions which help the user convert between Kelly curves using different
units. Sometimes, it is helpful to look at the curve in absolute USDC amounts, and sometimes it
is useful to look at the curve how it would be stored on-chain: divided by the strike and number
of contracts the user can afford so that it is viewed in a percentage based unit scale.

These functions let a caller easily switch between units and are named in the convention:
convert\_\[input-unit\]\_to\_\[output-unit\]\_curve()

These functions will do some basic checking and throw a ValueError if there are invalid values
provided by the caller.
"""
import numpy as np


def convert_absolute_to_strike_normalized_curve(strike: float, max_bankroll: float,
                                                bankroll_amounts: np.ndarray,
                                                premium_amounts: np.ndarray):
    """
    This function converts a Kelly curve measured in units of absolute premium and absolute
    units of bankroll wagered on a given bet into the same curve measured in units normalized
    by the strike (max loss) and fraction bet (0 to 1).
    
    This function throws a ValueError if the strike is <= 0 and if max_bankroll <= 0 so there
    is no division by zero.

    Parameters
    ----------
    strike : float
        The strike (max loss) of the option bet the curve represents
    max_bankroll : float
        The maximum amount of money the user has available to wager
    bankroll_amounts : np.ndarray
        The points along the x-axis of the curve representing a value wagered between 0
        and max_bankroll
    premium_amounts : np.ndarray
        The y-value points along the curve representing the total amount of premium collected for
        the given bankroll wagered

    Raises
    -------
    ValueError
        If strike is <= 0.0 or if max_bankroll <= 0.0

    Returns
    -------
    bet_fractions : numpy.ndarray
        Represents the X values of the Kelly curve in bet fraction amount from 0 (bet nothing) to
        1.0 (bet everything)
    strike_normalized_premiums : numpy.ndarray
        Represents the premium Y values of the Kelly curve in amounts normalized by the strike value
    """
    if strike <= 0:
        raise ValueError('Strike must be positive: {}'.format(strike))
    if max_bankroll <= 0:
        raise ValueError('Max Bankroll amount must be positive: {}'.format(max_bankroll))

    bet_fractions = bankroll_amounts / max_bankroll
    strike_normalized_premiums = premium_amounts / strike

    return bet_fractions, strike_normalized_premiums


def convert_strike_normalized_to_fully_normalized_curve(strike: float, max_bankroll: float,
                                                        bet_fractions: np.ndarray,
                                                        strike_normalized_premiums: np.ndarray):
    """
    This function converts a Kelly curve measured in units of premium normalized by the strike
    into the same curve measured in units normalized by the both the strike (max loss) and the
    number of contracts a user with this bankroll can afford (so that we can use the same curve
    across strikes and capital amounts of different users).
    
    This function throws a ValueError if the strike is <= 0 and if
    strike_normalized_premiums.size <= 3 so there is no division by zero. The requirement on
    the premium array being a certain length comes from the fact the initial
    point on the fully normalized curve is lost when you convert it to an absolute curve and then
    convert back to fully normalized. This is because absolute curves always start at 0. Since
    generally we generate the curves fully normalized and convert to absolute it is not a
    problem. This function needs 3 points to extrapolate the missing starting point.

    Parameters
    ----------
    strike : float
        The strike (max loss) of the option bet the curve represents
    max_bankroll : float
        The maximum amount of money the user has available to wager
    bet_fractions : numpy.ndarray
        Represents the X values of the Kelly curve in bet fraction amount from 0 (bet nothing) to
        1.0 (bet everything)
    strike_normalized_premiums : numpy.ndarray
        Represents the premium Y values of the Kelly curve in amounts normalized by the strike value

    Raises
    -------
    ValueError
        If strike is <= 0.0 or if len(strike_normalized_premiums) < 3

    Returns
    -------
    fully_normalized_premiums : numpy.ndarray
        The y-values of the Kelly curve representing the premium normalized by both the strike and
        the number of contracts the user can afford with this max_bankroll
    """
    if strike <= 0:
        raise ValueError('Strike must be positive: {}'.format(strike))
    if strike_normalized_premiums.size < 3:
        raise ValueError('Premium array must have at least 3 points')

    max_num_contracts = max_bankroll / strike
    num_contracts = bet_fractions * max_num_contracts

    # Ensure no divide by zero
    num_contracts = np.where(num_contracts == 0.0, 1e-10, num_contracts)

    fully_normalized_premiums = strike_normalized_premiums / num_contracts

    # Project the last data point assuming the same slope. Going in this direction the information
    # from the first point is lost because the absolute curve always starts at 0 premium
    rise = fully_normalized_premiums[2] - fully_normalized_premiums[1]
    run = bet_fractions[2] - bet_fractions[1]

    # Ensure no divide by zero
    if run == 0.0:
        run = 1e-10

    slope = rise / run
    fully_normalized_premiums[0] = slope * bet_fractions[0] + (
                fully_normalized_premiums[1] - slope * bet_fractions[1])

    return fully_normalized_premiums


def convert_fully_normalized_to_strike_normalized_curve(strike: float, max_bankroll: float,
                                                        bet_fractions: np.ndarray,
                                                        fully_normalized_premiums: np.ndarray):
    """
    This function converts a Kelly curve measured in units of premium normalized by both the
    strike (max loss) and the number of contracts a user with this bankroll can afford into the
    same curve measured in units normalized by only the strike (max loss).
    
    This function throws a ValueError if the strike is <= 0 so there is no division by zero.

    Parameters
    ----------
    strike : float
        The strike (max loss) of the option bet the curve represents
    max_bankroll : float
        The maximum amount of money the user has available to wager
    bet_fractions : numpy.ndarray
        Represents the X values of the Kelly curve in bet fraction amount from 0 (bet nothing) to
        1.0 (bet everything)
    fully_normalized_premiums : numpy.ndarray
        The y-values of the Kelly curve representing the premium normalized by both the strike and
        the number of contracts the user can afford with this max_bankroll

    Raises
    -------
    ValueError
        If strike is <= 0.0

    Returns
    -------
    strike_normalized_premiums : numpy.ndarray
        Represents the premium Y values of the Kelly curve in amounts normalized by the strike value
    """
    if strike <= 0:
        raise ValueError('Strike must be positive: {}'.format(strike))

    max_num_contracts = max_bankroll / strike
    num_contracts = bet_fractions * max_num_contracts

    # Ensure no divide by zero
    num_contracts = np.where(num_contracts == 0.0, 1e-10, num_contracts)

    strike_normalized_premiums = fully_normalized_premiums * num_contracts

    return strike_normalized_premiums


def convert_fully_normalized_value_to_strike_normalized(strike: float, max_bankroll: float,
                                                        bet_fraction: float,
                                                        fully_normalized_premium: float):
    """
    This function converts a Kelly curve value measured in units of premium normalized by both the
    strike (max loss) and the number of contracts a user with this bankroll can afford into the
    same curve measured in units normalized by only the strike (max loss).

    This function throws a ValueError if the strike is <= 0 so there is no division by zero.

    Parameters
    ----------
    strike : float
        The strike (max loss) of the option bet the curve represents
    max_bankroll : float
        The maximum amount of money the user has available to wager
    bet_fraction : float
        Represents the X value of the Kelly curve in bet fraction amount from 0 (bet nothing) to
        1.0 (bet everything)
    fully_normalized_premium : numpy.ndarray
        The y-value of the Kelly curve representing the premium normalized by both the strike and
        the number of contracts the user can afford with this max_bankroll

    Raises
    -------
    ValueError
        If strike is <= 0.0

    Returns
    -------
    strike_normalized_premium : float
        Represents the premium Y value of the Kelly curve in amounts normalized by the strike value
    """
    if strike <= 0:
        raise ValueError('Strike must be positive: {}'.format(strike))

    max_num_contracts = max_bankroll / strike
    num_contracts = bet_fraction * max_num_contracts

    # Ensure no divide by zero
    if num_contracts == 0.0:
        num_contracts = 1e-10

    strike_normalized_premium = fully_normalized_premium * num_contracts

    return strike_normalized_premium


def convert_strike_normalized_to_absolute_curve(strike: float, max_bankroll: float,
                                                bet_fractions: np.ndarray,
                                                strike_normalized_premiums):
    """
    This function converts a Kelly curve measured in units normalized by the strike
    (max loss) and fraction of the user's total capital bet (0 to 1) to a curve measured in
    units of absolute premium and absolute units of bankroll wagered on a given bet. This
    curve represents the absolute amounts purchased and value exchanged in a trade.

    Parameters
    ----------
    strike : float
        The strike (max loss) of the option bet the curve represents
    max_bankroll : float
        The maximum amount of money the user has available to wager
    bet_fractions : Union[numpy.ndarray, float]
        Represents the X values of the Kelly curve in bet fraction amount from 0 (bet nothing) to
        1.0 (bet everything)
    strike_normalized_premiums : Union[float, np.ndarray]
        Represents the premium Y values of the Kelly curve in amounts normalized by the strike value

    Returns
    -------
    absolute_bankroll_amounts : numpy.ndarray
        The X values of the Kelly curve measured in absolute USDC amounts, betting from 0 USDC to
        max_bankroll amount of USDC
    absolute_premium_amounts : numpy.ndarray
        The Y values of the Kelly curve representing premium measured in absolute USDC amounts
    """
    absolute_premium_amounts = strike_normalized_premiums * strike

    absolute_bankroll_amounts = bet_fractions * max_bankroll

    return absolute_bankroll_amounts, absolute_premium_amounts

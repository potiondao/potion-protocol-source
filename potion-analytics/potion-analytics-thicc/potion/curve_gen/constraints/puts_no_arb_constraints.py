
import numpy as np


def monotonic_lb(bound_dict: dict):
    """
    Checks the monotonic lower bound no-arbitrage constraint and returns
    True if the constraint holds, False if the constraint is violated

    Dict Arguments
    ----------
    p_i : float
        The Put price being tested
    p_ii : float
        The Put price at the previous strike

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    mono_lb : float
        The lower bound in terms of premium
    """
    p_ii = bound_dict['p_ii']

    return p_ii


def monotonic_ub(bound_dict: dict):
    """
    Checks the monotonic upper bound no-arbitrage constraint and returns
    True if the constraint holds, False if the constraint is violated

    Dict Arguments
    ----------
    p_i : float
        The Put price being tested
    p_ii : float
        The Put price at the previous strike
    k_i : float
        The current strike
    k_ii : float
        The previous strike
    r : float
        The annualized interest rate
    tau : float
        The time in years until the expiration

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    mono_ub : float
        The upper bound in terms of premium
    """
    p_ii = bound_dict['p_ii']
    k_i = bound_dict['k_i']
    k_ii = bound_dict['k_ii']
    r = bound_dict['r']
    tau = bound_dict['tau']

    return p_ii - k_ii * np.exp(-r * tau) + k_i * np.exp(-r * tau)


def convex_lb(bound_dict: dict):
    """
    Checks the convexity bound no-arbitrage constraint and returns
    True if the constraint holds, False if the constraint is violated

    Dict Arguments
    ----------
    p_i : float
        The Put price being tested
    p_ii : float
        The previous Put price
    p_iii : float
        The next to last Put price
    k_i : float
        The current strike being tested
    k_ii : float
        The previous strike
    k_iii : float
        The next to last strike

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    convex_lb : float
        The lower bound in premium
    """
    p_ii = bound_dict['p_ii']
    p_iii = bound_dict['p_iii']
    k_i = bound_dict['k_i']
    k_ii = bound_dict['k_ii']
    k_iii = bound_dict['k_iii']

    return p_ii + ((p_ii - p_iii) / (k_ii - k_iii)) * (k_i - k_ii)


def zero_bound(bound_dict: dict):
    """
    Checks the zero bound no-arbitrage constraint and returns
    True if the constraint holds, False if the constraint is violated

    Returns
    -------
    zero_lb : float
        The lower bound in premium
    """
    return 0.0


def call_zero_bound_by_pcp(bound_dict: dict):
    """
    Checks the no-arbitrage constraint that comes from put-call parity and the
    fact that calls need to be positive premium and returns
    True if the constraint holds, False if the constraint is violated

    Dict Arguments
    ----------
    p_i : float
        The Put price being tested
    k_i : float
        The current strike being tested
    s : float
        The price of the underlying
    r : float
        The annualized interest rate
    q : float
        The annualized rate of cash flows from the asset
    tau : float
        The time until expiration of the put in years

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    call_zero_bound : float
        The lower bound in premium
    """
    k_i = bound_dict['k_i']
    s = bound_dict['s']
    r = bound_dict['r']
    q = bound_dict['q']
    tau = bound_dict['tau']

    return k_i * np.exp(-r * tau) - s * np.exp(-q * tau)


def calendar_ub(bound_dict: dict):
    """
    Calculates the no-arbitrage constraint between expirations and returns
    the upper bound in premium

    Dict Arguments
    ----------
    p_i : float
        The price at the current expiration
    p_mm : float
        The price at the next expiration
    k_i : float
        The strike price
    s : float
        The price of the underlying
    r : float
        The annualized interest rate
    q : float
        The annualized rate of return from cash flows of the underlying
    tau : float
        The amount of time (t_m - t) until the current expiration in years
    exp_tau : float
        The amount of time (t_mm - t_m) between the current expiration and the next expiration in
        years

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    calendar_bound : float
        The upper bound in premium
    """
    # print('bd: ', bound_dict)

    p_mm = bound_dict['p_mm']
    k_i = bound_dict['k_i']
    s = bound_dict['s']
    r = bound_dict['r']
    q = bound_dict['q']
    tau = bound_dict['tau']

    if np.isnan(p_mm):
        return s

    exp_tau = bound_dict['exp_tau']

    return p_mm * np.exp(r * exp_tau) + s * np.exp(-q * tau) * (
            np.exp(r * exp_tau) - 1.0) + k_i * np.exp(-r * tau) * (1.0 - np.exp(r * exp_tau))


def monotonic_lb_cond(bound_dict):
    """
    Checks the monotonic lower bound no-arbitrage constraint and returns
    True if the constraint holds, False if the constraint is violated

    Dict Arguments
    ----------
    p_i : float
        The Put price being tested
    p_ii : float
        The Put price at the previous strike

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    mono_lb : bool
        True if the constraint holds, False if the constraint is violated
    """
    p_i = bound_dict['p_i']
    return p_i >= monotonic_lb(bound_dict)


def monotonic_ub_cond(bound_dict):
    """
    Checks the monotonic upper bound no-arbitrage constraint and returns
    True if the constraint holds, False if the constraint is violated

    Dict Arguments
    ----------
    p_i : float
        The Put price being tested
    p_ii : float
        The Put price at the previous strike
    k_i : float
        The current strike
    k_ii : float
        The previous strike
    r : float
        The annualized interest rate
    tau : float
        The time in years until the expiration

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    mono_ub : bool
        True if the constraint holds, False if the constraint is violated
    """
    p_i = bound_dict['p_i']
    return p_i <= monotonic_ub(bound_dict)


def convex_lb_cond(bound_dict):
    """
    Checks the convexity bound no-arbitrage constraint and returns
    True if the constraint holds, False if the constraint is violated

    Dict Arguments
    ----------
    p_i : float
        The Put price being tested
    p_ii : float
        The previous Put price
    p_iii : float
        The next to last Put price
    k_i : float
        The current strike being tested
    k_ii : float
        The previous strike
    k_iii : float
        The next to last strike

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    convex_lb : bool
        True if the constraint holds, False if the constraint is violated
    """
    p_i = bound_dict['p_i']
    return p_i >= convex_lb(bound_dict)


def zero_bound_cond(bound_dict):
    """
    Checks the zero bound no-arbitrage constraint and returns
    True if the constraint holds, False if the constraint is violated

    Dict Arguments
    ----------
    p_i : float
        The Put price being tested

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    zero_lb : bool
        True if the constraint holds, False if the constraint is violated
    """
    p_i = bound_dict['p_i']
    return p_i >= zero_bound(bound_dict)


def call_zero_bound_by_pcp_cond(bound_dict):
    """
    Checks the no-arbitrage constraint that comes from put-call parity and the
    fact that calls need to be positive premium and returns
    True if the constraint holds, False if the constraint is violated

    Dict Arguments
    ----------
    p_i : float
        The Put price being tested
    k_i : float
        The current strike being tested
    s : float
        The price of the underlying
    r : float
        The annualized interest rate
    q : float
        The annualized rate of cash flows from the asset
    tau : float
        The time until expiration of the put in years

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    call_zero_bound : bool
        True if the constraint holds, False if the constraint is violated
    """
    p_i = bound_dict['p_i']
    return p_i >= call_zero_bound_by_pcp(bound_dict)


def calendar_ub_cond(bound_dict: dict):
    """
    Checks the no-arbitrage constraint between expirations and returns
    True if the constraint holds, False if the constraint is violated

    Dict Arguments
    ----------
    p_i : float
        The price at the current expiration
    p_mm : float
        The price at the next expiration
    k_i : float
        The strike price
    s : float
        The price of the underlying
    r : float
        The annualized interest rate
    q : float
        The annualized rate of return from cash flows of the underlying
    tau : float
        The amount of time (t_m - t) until the current expiration in years
    t_m : float
        The time until expiration t_m until the current expiration in years
    t_mm : float
        The time until the next expiration in years

    Parameters
    ----------
    bound_dict : dict
        The dict containing all of the function arguments needed to calculate the boundary

    Returns
    -------
    calendar_bound : bool
        True if the constraint holds, False if the constraint is violated
    """
    p_i = bound_dict['p_i']
    return p_i <= calendar_ub(bound_dict)

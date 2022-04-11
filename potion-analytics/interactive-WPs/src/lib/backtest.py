#!/usr/bin/env python3
"""Module with all backtest related functions"""
import numpy as np
import pandas as pd
import lib.helpers as hlp
import lib.kelly as kelly
import lib.random_path_generation as rpg
import lib.black_scholes as bs
import lib.convolution as convolution


def run_backtest(
    random_return_paths_cycles_df, utils, premiums, strike, duration, option_type="put"
):
    """For each returns path calculate corresponding pnl sequence
    Args:
        random_return_paths_cycles_df (pd.DataFrame):
            Returns of the underlying
        utils (list):
            Util to use at each step of the generated price paths
            Path length is gonna be equal to the len(utils)
        premiums (list):
            Premium for each day
        strike (float):
            Strike price. Expressed as pct from current price.
            e.g. 1.1 stands for 10% above current
        duration (int):
            Duration of the put option
    Returns:
        banroll_df (pd.DataFrame):
            bankroll evolution for each price path (each bankroll is column)
    """

    # calculate payoffs at the option expiration
    if option_type == "put":
        payoff_cycles_df = random_return_paths_cycles_df.applymap(
            kelly.put_option_payout, strike=strike, premium=0
        )
    elif "call" in option_type:
        payoff_cycles_df = random_return_paths_cycles_df.applymap(
            kelly.call_option_payout, strike=strike, premium=0
        )
    else:
        raise ValueError(
            f'Wrong option_type: {option_type}. Should be "put" or "call".'
        )

    # add zeros to the payoffs to account for the days before the expiration
    payoff_cycles_df.index = range(
        duration - 1, duration * len(payoff_cycles_df) + duration - 1, duration
    )
    payoff_days_df = payoff_cycles_df.reindex(index=range(len(utils)))
    payoff_days_df.fillna(0, inplace=True)

    payoff_days_df = (payoff_days_df.add(premiums, axis=0)).multiply(utils, axis=0) + 1

    bankroll_df = payoff_days_df.cumprod(axis=0)

    bankroll_df = bankroll_df.astype('float16')

    return bankroll_df


def run_black_scholes_backtest(
    returns_sequence,
    utils,
    number_of_paths,
    duration,
    strike,
    premium_offset=0,
    option_type="put",
):
    """For each returns path calculate corresponding pnl sequence
    Premiums are calculated with the Black-Scholes formula
    Args:
        returns_sequence (list):
            list or other iterable of returns
        utils (list):
            Util to use at each step of the generated price paths
            Path length is gonna be equal to the len(utils)
        number_of_paths (int):
            Number of paths to generate
        duration (int):
            Duration of the put option
        strike (float):
            Strike price. Expressed as pct from current price.
            e.g. 1.1 stands for 10% above current
        premium_offset (float):
            pct offset

    Returns:
        banroll_df (pd.DataFrame):
            bankroll evolution for each price path (each bankroll is column)
    """
    # create returns paths
    random_returns_paths_daily_df = rpg.generate_returns_paths_from_returns(
        returns_sequence, number_of_paths, len(utils), output_as_df=True
    )
    random_returns_paths_daily_df += 1

    # duration cycles and volatility of returns
    yearly_volatility_df = pd.DataFrame(columns=random_returns_paths_daily_df.columns)
    random_returns_paths_cycles_df = pd.DataFrame(
        columns=random_returns_paths_daily_df.columns
    )

    # calculate volatility/returns for cycles
    i = 0
    while i + duration < len(utils):
        yearly_volatility_df = yearly_volatility_df.append(
            random_returns_paths_daily_df[i : i + duration].std() * np.sqrt(365),
            ignore_index=True,
        )
        random_returns_paths_cycles_df = random_returns_paths_cycles_df.append(
            random_returns_paths_daily_df[i : i + duration].cumprod().tail(1),
            ignore_index=True,
        )
        i += duration

    # calculate premiums
    if option_type == "put":
        cycles_premiums_df = yearly_volatility_df.applymap(
            bs.calculate_bs_put_premium,
            spot_price=1,
            strike_price=strike,
            years_to_expiry=duration / 365,
            risk_free_interest_rate=0.01,
        )
    elif "call" in option_type:
        cycles_premiums_df = yearly_volatility_df.applymap(
            bs.calculate_bs_call_premium,
            spot_price=1,
            strike_price=strike,
            years_to_expiry=duration / 365,
            risk_free_interest_rate=0.01,
        )
    else:
        raise ValueError(
            f'Wrong option_type: {option_type}. Should be "put" or "call".'
        )
    cycles_premiums_df *= 1 + premium_offset

    random_returns_paths_cycles_df -= 1
    random_returns_paths_daily_df -= 1

    # calculate payoff
    if option_type == "put":
        payoff_cycles_df = random_returns_paths_cycles_df.applymap(
            kelly.put_option_payout, strike=strike, premium=0
        )
    elif 'call' in option_type:
        payoff_cycles_df = random_returns_paths_cycles_df.applymap(
            kelly.call_option_payout, strike=strike, premium=0
        )
    else:
        raise ValueError(
            f'Wrong option_type: {option_type}. Should be "put" or "call".'
        )

    payoff_cycles_df += cycles_premiums_df

    # switch to daily payoffs
    # add zeros to the payoffs to account for the days before the expiration
    payoff_cycles_df.index = range(
        duration - 1, duration * len(payoff_cycles_df) + duration - 1, duration
    )
    payoff_days_df = payoff_cycles_df.reindex(index=range(len(utils)))
    payoff_days_df.fillna(0, inplace=True)

    payoff_days_df = payoff_days_df.multiply(utils, axis=0) + 1

    bankroll_df = payoff_days_df.cumprod(axis=0)

    return bankroll_df, cycles_premiums_df


def backtest_asset_dict(
    asset_dict,
    simulation_length_days,
    historical_df,
    monte_carlo_paths,
    bonding_curve_resolution,
    number_of_paths,
    premium_offset=0,
    engine="kelly",
    risk_free_rate=0,
    randomize_util=False,
    util_std=0
):
    """Real Monstrosity to wrap all the calculations for the asset_dict
    TODO Restucture"""
    # Create Utils list
    ##########################################################################
    utils = rpg.generate_utils_list(
        simulation_length_days,
        initial_util=asset_dict["util"],
        duration=asset_dict["duration"],
        randomize=randomize_util,
        util_std=util_std
    )
    # Fill basic info
    ##########################################################################
    date_start = hlp.get_date(
        asset_dict["train_start_date"], asset_dict["asset"], historical_df
    )
    date_end = hlp.get_date(
        asset_dict["train_end_date"], asset_dict["asset"], historical_df
    )
    asset_dict["date_start"] = date_start
    asset_dict["date_end"] = date_end
    asset_dict["price_series"] = historical_df[
        (historical_df.index > asset_dict["date_start"])
        & (historical_df.index < asset_dict["date_end"])
    ][asset_dict["asset"]].dropna()
    asset_dict["strike"] = asset_dict["strike_pct"] / 100 + 1
    asset_dict["years"] = simulation_length_days / 365
    if "option_type" not in asset_dict:
        asset_dict["option_type"] = "put"

    # Returns Paths
    ##########################################################################
    underlying_n_daily_returns = convolution.daily_returns_to_n_day_returns(
        asset_dict["price_series"].pct_change()[1:],
        number_of_paths=monte_carlo_paths,
        n_days=asset_dict["duration"],
    )
    random_return_paths_cycles_df = rpg.generate_returns_paths_from_returns(
        underlying_n_daily_returns,
        number_of_paths,
        simulation_length_days // asset_dict["duration"],
        output_as_df=True,
    )

    ##########################################################################
    # Premiums Calculation
    ##########################################################################
    if engine == "kelly":
        (
            premiums,
            premium_vs_util_df,
            fit_params,
        ) = kelly.get_premiums_list_with_all_calculations(
            utils,
            premium_offset=premium_offset,
            fit_params=None,
            bonding_curve_resolution=bonding_curve_resolution,
            underlying_n_daily_returns=underlying_n_daily_returns,
            strike=asset_dict["strike"],
            option_type=asset_dict["option_type"],
        )
        asset_dict["premium_vs_util_df"] = premium_vs_util_df

    if engine == "bs":
        # calc sigma
        daily_std_dev = np.std(asset_dict["price_series"].pct_change()[1:])
        asset_dict["underlying_yearly_return_std"] = daily_std_dev * np.sqrt(365)
        if asset_dict["option_type"] == "put":
            premium = bs.calculate_bs_put_premium(
                asset_dict["underlying_yearly_return_std"],
                asset_dict["duration"] / 365,
                asset_dict["strike"],
                spot_price=1,
                risk_free_interest_rate=risk_free_rate,
            )
        elif "call" in asset_dict["option_type"]:
            premium = bs.calculate_bs_call_premium(
                asset_dict["underlying_yearly_return_std"],
                asset_dict["duration"] / 365,
                asset_dict["strike"],
                spot_price=1,
                risk_free_interest_rate=risk_free_rate,
            )
        premiums = [premium] * simulation_length_days
        fit_params = None
        asset_dict["premium_vs_util_df"] = pd.DataFrame(
            {
                "util": np.linspace(0, 1, bonding_curve_resolution),
                "premium": [premium] * bonding_curve_resolution,
            }
        )

    # Do Actual Backtest
    ##########################################################################
    bankroll_df = run_backtest(
        random_return_paths_cycles_df,
        utils,
        premiums,
        asset_dict["strike"],
        asset_dict["duration"],
        option_type=asset_dict["option_type"],
    )

    asset_dict["bankroll_df"] = bankroll_df
    # Calculate stats
    ##########################################################################

    asset_dict["max_drawdown_percentiles"] = calculate_percentiles(
        calculate_max_drawdown,
        bankroll_df,
        percentiles=(0, 25, 50, 75, 100),
    )

    asset_dict["cagr_percentiles"] = calculate_percentiles(
        calculate_cagr, bankroll_df, percentiles=(0, 25, 50, 75, 100)
    )

    asset_dict["sharpe_percentiles"] = calculate_percentiles(
        calculate_sharpe, bankroll_df, percentiles=(0, 25, 50, 75, 100)
    )

    asset_dict["asset_label"] = (
        f"{asset_dict['asset']}_{asset_dict['option_type']}_S"
        f"={np.round(asset_dict['strike_pct'],1)}_"
        f"D={asset_dict['duration']}_M={asset_dict['mood']}"
    )

    asset_dict["kelly_params"] = fit_params
    asset_dict["engine"] = engine

    return asset_dict


# backtest results_stats
###################################################################################################


def create_kde_df(bankroll_df):
    """bankroll_df => kde_df"""
    kde_df = pd.DataFrame()

    for col in bankroll_df:
        max_drawdown = calculate_max_drawdown(bankroll_df[col])
        cagr = calculate_cagr(bankroll_df[col])
        kde_df = kde_df.append(
            {"cagr": cagr, "max_drawdown": max_drawdown}, ignore_index=True
        )

    return kde_df


# pnl_list functions
###################################################################################################
def calculate_max_drawdown(pnl_list):
    """Function to calculate max drawdown
    Args:
        pnl_list (list):
            sequence of the potfoliovalue
    Returns:
        max_drawdown_seen (float):
            1 is 100%
    """
    if isinstance(pnl_list, pd.Series):
        pnl_list = pnl_list.values
    highest_val_seen = 0.0
    max_drawdown_seen = 0.0
    for value in pnl_list:

        if value >= highest_val_seen:
            highest_val_seen = value

        drawdown = (value - highest_val_seen) / highest_val_seen

        if drawdown < max_drawdown_seen:
            max_drawdown_seen = drawdown

    # Return as a percentage
    return -max_drawdown_seen


def calculate_max_initial_capital_loss(pnl_list):
    """Function to calculate max drawdown
    Args:
        pnl_list (list):
            sequence of the potfoliovalue
    Returns:
        max_drawdown_seen (float):
            1 is 100%
    """
    if isinstance(pnl_list, pd.Series):
        pnl_list = pnl_list.values
    start_capital = pnl_list[0]
    lowest_capital = min(pnl_list)

    return -(lowest_capital / start_capital - 1)


def calculate_sharpe(pnl_series, benchmark_daily_return=0):
    """Function to calculate Sharpe Ratio
    Args:
        pnl_series (DataFrame):
            sequence of pnl (price)
        benchmark_daily_return (pd.Series):
            Series of benchmark returns
    Returns:
        sharpe (float):
            Sharpe Ratio
    """
    # Handling TypeError: No matching signature found
    pnl_series = pnl_series.astype('float32')

    if pnl_series.pct_change().std() != 0:
        sharpe_ratio = (
            pnl_series.pct_change() - benchmark_daily_return
        ).mean() / pnl_series.pct_change().std()
    else:
        sharpe_ratio = np.inf

    return sharpe_ratio


def calculate_information_ratio(pnl_series, benchmark_daily_return=0):
    """Function to calculate Information Ratio
    Args:
        pnl_series (DataFrame):
            sequence of pnl (price)
        benchmark_daily_return (pd.Series):
            Series of benchmark returns
    Returns:
        sharpe (float):
            Sharpe Ratio
    """
    if (pnl_series.pct_change() - benchmark_daily_return).std() != 0:
        information_ratio = (
            pnl_series.pct_change() - benchmark_daily_return
        ).mean() / (pnl_series.pct_change() - benchmark_daily_return).std()
    else:
        information_ratio = np.inf

    return information_ratio


def calculate_cagr(pnl_series):
    """Function to cagr
    Args:
        pnl_series (pd.Series):
            Could be list or np.array as well
    Returns:
        cagr (float):
            CAGR
    """
    if isinstance(pnl_series, pd.Series):
        values = pnl_series.values
    else:
        values = pnl_series
    return (values[-1] / values[0]) ** (365 / len(values)) - 1


def calculate_percentiles(
    metric_function, bankroll_df, percentiles=(0, 25, 50, 75, 100)
):
    """Function to calculate cagr percentiles
    Args:
        metric_function (func):
            with takes pnl_list as input and calulates sharpe or max_loss, etc.
        bankroll_df (DataFrame):
            all the results
        percentiles (tuple):
            which percentiles to calculate
    Returns:
        percentile_values (tuple):
            number of the cagrs
    """
    bankroll_specific_values = []
    for bankroll_col in bankroll_df:
        bankroll_specific_values.append(metric_function(bankroll_df[bankroll_col]))

    with np.errstate(invalid="ignore"):
        res = np.percentile(bankroll_specific_values, percentiles)
    return res

def convert_bankroll_paths_to_cagr_paths(bankroll_df):
    '''bankroll_df => cagr_paths_df'''
    cagr_paths = []
    for path_col in bankroll_df:
        cagrs = [
            (b_last / 1) ** (365 / (periods + 1)) - 1
            for periods, b_last in enumerate(bankroll_df[path_col])
        ]
        cagr_paths.append(cagrs)

    cagr_paths_df = pd.DataFrame(cagr_paths).T

    return cagr_paths_df

#!/usr/bin/env python3
"""Script which runs streamlit app"""

import io
import math
import pandas as pd
import streamlit as st
import joypy
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
from matplotlib import cm
from stqdm import stqdm
import seaborn as sns

import lib.helpers as hlp
import lib.backtest as backtest
import lib.kelly as kelly
import lib.random_path_generation as rpg
import lib.convolution as convolution
import lib.plotting as plotting
import lib.steamlit_components as sc


@st.cache(**sc.CACHE_KWARGS, allow_output_mutation=True)
def plot_all_kelly_curves_with_optimal_bet_annualized(*args, **kwargs):
    """Caching wrapper"""
    return plotting.plot_all_kelly_curves_with_optimal_bet_annualized(*args, **kwargs)


@st.cache(**sc.CACHE_KWARGS)
def create_kde_df(*args, **kwargs):
    """Caching wrapper"""
    return backtest.create_kde_df(*args, **kwargs)


@st.cache(**sc.CACHE_KWARGS)
def get_historical_prices_df():
    """Caching wrapper"""
    return hlp.get_historical_prices_df()


@st.cache(**sc.CACHE_KWARGS)
def generate_returns_paths_from_returns(*args, **kwargs):
    """Caching wrapper"""
    return rpg.generate_returns_paths_from_returns(*args, **kwargs)


@st.cache(**sc.CACHE_KWARGS)
def daily_returns_to_n_day_returns(*args, **kwargs):
    """Caching wrapper"""
    return convolution.daily_returns_to_n_day_returns(*args, **kwargs)


st.cache(**sc.CACHE_KWARGS)


def calculate_kdes(
    historical_df,
    asset,
    initial_util,
    util_std,
    strike,
    duration,
    simulation_length_days,
    monte_carlo_paths,
    bonding_curve_resolution,
    premium_offset=None,
    convolution_n_paths=1000,
    option_type=None,
):
    """create list of kdes"""
    utils_fixed = rpg.generate_utils_list(
        simulation_length_days,
        initial_util=initial_util,
        duration=duration,
        randomize=False,
        util_std=util_std,
    )
    utils_normal = rpg.generate_utils_list(
        simulation_length_days,
        initial_util=initial_util,
        duration=duration,
        randomize=True,
        util_std=util_std,
    )
    utils_uniform = rpg.generate_utils_list(
        simulation_length_days,
        initial_util=initial_util,
        duration=duration,
        randomize=True,
        util_std=-1,
    )
    utils_lists = [utils_fixed, utils_normal, utils_uniform]
    # backtest_dfs_list = []
    kde_dfs_list = []

    price_sequence = historical_df[asset].dropna()
    returns_sequence = price_sequence.pct_change()[1:]
    underlying_n_daily_returns = daily_returns_to_n_day_returns(
        returns_sequence,
        number_of_paths=convolution_n_paths,
        n_days=duration,
    )
    random_return_paths_cycles_df = generate_returns_paths_from_returns(
        underlying_n_daily_returns,
        monte_carlo_paths,
        simulation_length_days // duration,
        output_as_df=True,
    )

    for utils in utils_lists:
        # premiums
        (premiums, _, _,) = kelly.get_premiums_list_with_all_calculations(
            utils,
            premium_offset=premium_offset,
            fit_params=None,
            bonding_curve_resolution=bonding_curve_resolution,
            underlying_n_daily_returns=underlying_n_daily_returns,
            strike=strike,
            option_type=option_type,
        )

        bankroll_df = backtest.run_backtest(
            random_return_paths_cycles_df,
            utils,
            premiums,
            strike,
            duration,
            option_type=option_type,
        )

        kde_dfs_list.append(create_kde_df(bankroll_df))

    return kde_dfs_list


st.cache(**sc.CACHE_KWARGS)


def plot_kde(
    kde_df,
    ylims,
    x_axis_name="max_drawdown",
    y_axis_name="cagr",
):
    """Plot multiple kdes at one chart"""

    fig_kde, _ = plt.subplots()

    sns.kdeplot(
        data=kde_df,
        x=x_axis_name,
        y=y_axis_name,
        shade=True,
        thresh=0.05,
        # cbar=True,
        # cmap=cmaps[i],
        alpha=0.5,
    )
    plt.axhline(y=np.median(kde_df["cagr"].values), color="r", linestyle="dashed")
    plt.axvline(
        x=np.median(kde_df["max_drawdown"].values), color="r", linestyle="dashed"
    )
    median_cagr = np.median(kde_df["cagr"].values)
    median_max_drawdown = np.median(kde_df["max_drawdown"].values)
    max_cagr = np.max(kde_df["cagr"].values)
    plt.xlim(0, 1)
    plt.ylim(ylims[0], ylims[1])
    plt.annotate(f"Median CAGR {round(median_cagr*100, 1)}%", (0.8, median_cagr))
    plt.annotate(
        f"Median Max Drawdown {round(median_max_drawdown*100, 1)}%",
        (median_max_drawdown, max_cagr),
    )

    return fig_kde


@st.cache(**sc.CACHE_KWARGS)
def plot_raw_vs_fitted_bonding_curve(
    historical_df,
    asset,
    strike,
    duration,
    bonding_curve_resolution=10,
    convolution_n_paths=1000,
    premium_offset=0,
    option_type="put",
):
    """Plot two bonding curves, which are supposed to converge"""
    price_sequence = historical_df[asset].dropna()
    returns_sequence = price_sequence.pct_change()[1:]
    underlying_n_daily_returns = convolution.daily_returns_to_n_day_returns(
        returns_sequence,
        number_of_paths=convolution_n_paths,
        n_days=duration,
    )
    premium_vs_util_df = kelly.get_kelly_curve(
        underlying_n_daily_returns,
        strike,
        number_of_utils=bonding_curve_resolution,
        option_type=option_type,
    )
    premium_vs_util_df["premium"] *= 1 + premium_offset

    premium_vs_util_fit_params = kelly.fit_curve_parameters(
        premium_vs_util_df["util"], premium_vs_util_df["premium"]
    )

    fitted_df = kelly.get_curve_df(*premium_vs_util_fit_params, len(premium_vs_util_df))

    fig_premium_vs_util = go.Figure()
    fig_premium_vs_util.add_trace(
        go.Scatter(
            x=premium_vs_util_df["util"],
            y=premium_vs_util_df["premium"],
            mode="lines+markers",
            line_color="green",
            name="Raw Premiums",
        )
    )

    fig_premium_vs_util.add_trace(
        go.Scatter(
            x=fitted_df["util"],
            y=fitted_df["premium"],
            mode="lines+markers",
            line_color="red",
            name="Cosh Premiums",
        )
    )
    min_y_value = premium_vs_util_df["premium"].min()
    max_y_value = max(premium_vs_util_df["premium"].max(), fitted_df["premium"].max())
    if max_y_value < 0.01:
        max_y_value = max_y_value * 3

    fig_premium_vs_util = plotting.custom_figure_layout_update(
        fig_premium_vs_util,
        "Util",
        "Premium charged (%)",
        title=f"Optimal bonding curve: {asset} "
        f"| Insurance_level:{strike} "
        f"Duration:{duration} days",
        x_tick_format=".0%",
        y_tick_format=".2%",
        yaxis_range=(min_y_value, max_y_value),
    )

    return fig_premium_vs_util


def create_n_read_simple_backtest_settings(
    historical_df,
    default_strike,
    default_duration,
    default_simulation_length_days,
    default_montecarlo_paths,
    default_simulation_utilization=None,
    default_premium_offset=None,
    convolution_n_paths=1000,
    additional_space_in_slider_name=0,
    y_axis_name=None,
    streamlit_holders=None,
    max_simulation_paths=250,
    option_type=None,
    max_simulation_days=365,
):
    """generate settings and form a dict"""
    if len(streamlit_holders) == 1:
        streamlit_holders = streamlit_holders * 4
    # cols_asset_settings = st.columns(3)
    params_simple_backtest = {}
    params_simple_backtest["asset"] = streamlit_holders[0].selectbox(
        "Choose the protected asset" + " " * additional_space_in_slider_name,
        historical_df.columns,
    )

    if option_type:
        params_simple_backtest["option_type"] = streamlit_holders[0].selectbox(
            "Choose Option Type" + " " * additional_space_in_slider_name,
            ["put", "call (beta)"],
        )

    if default_strike:
        params_simple_backtest["strike"] = (
            streamlit_holders[1].slider(
                "Insurance level (%)" + " " * additional_space_in_slider_name,
                sc.SLIDER_MIN_STRIKE,
                sc.SLIDER_MAX_STRIKE,
                default_strike,
            )
            / 100
        )  # 1.1 = 10% in the money

    if default_duration:
        if default_duration > 1:
            max_duration = sc.SLIDER_MAX2_DURATION
        else:
            max_duration = sc.SLIDER_MAX_DURATION
        params_simple_backtest["duration"] = streamlit_holders[1].slider(
            "Insurance Duration (days)" + " " * additional_space_in_slider_name,
            sc.SLIDER_MIN_DURATION,
            max_duration,
            default_duration,
        )

    if default_simulation_length_days:
        params_simple_backtest["simulation_length_days"] = streamlit_holders[2].slider(
            "Simulation Time horizon (days)" + " " * additional_space_in_slider_name,
            sc.SLIDER_MIN_DAYS,
            max_simulation_days,
            default_simulation_length_days,
        )  # number of option life cycles to use for backtest

    if default_montecarlo_paths:
        params_simple_backtest["monte_carlo_paths"] = streamlit_holders[2].slider(
            "Number of paths (simulation depth)"
            + " " * additional_space_in_slider_name,
            sc.SLIDER_MIN_PATHS,
            max_simulation_paths,
            default_montecarlo_paths,
            20,
        )  # number of the random paths to do backtest
    params_simple_backtest["convolution_n_paths"] = convolution_n_paths

    if default_simulation_utilization:
        params_simple_backtest["initial_util"] = (
            streamlit_holders[3].slider(
                "Utilization simulated" + " " * additional_space_in_slider_name,
                sc.SLIDER_MIN_UTIL,
                sc.SLIDER_MAX_UTIL,
                default_simulation_utilization,
            )
            / 100
        )

    if default_premium_offset or default_premium_offset == 0:
        params_simple_backtest["premium_offset"] = (
            streamlit_holders[3].slider(
                "Premium offset simulated (%)" + " " * additional_space_in_slider_name,
                sc.SLIDER_MIN_PREMIUM_OFFSET,
                sc.SLIDER_MAX_PREMIUM_OFFSET,
                default_premium_offset,
                5,
            )
            / 100
        )  # 0. # 0.1 = 10% additional relative premium

    if y_axis_name:
        params_simple_backtest["y_axis_name"] = streamlit_holders[3].selectbox(
            "Y Axis Name", ["cagr", "bankroll"]
        )

    return params_simple_backtest


@st.cache(**sc.CACHE_KWARGS, allow_output_mutation=True)
def create_bankrolls_cagrs_figs(bankroll_df, asset, strike, duration):
    """evolution of the bankrolls and cagrs evolution"""
    fig_bankrolls = plotting.plot_paths(
        bankroll_df,
        kind="Bankroll",
        plot_median=True,
        title=f"Simulated Bankrolls paths for {asset} S={strike} D={duration}",
    )
    cagr_paths_df = backtest.convert_bankroll_paths_to_cagr_paths(bankroll_df)
    fig_cagr_paths = plotting.plot_paths(
        cagr_paths_df,
        kind="cagr",
        plot_median=True,
        title=f"Simulated CAGR paths for {asset} S={strike} D={duration}",
    )

    return fig_bankrolls, fig_cagr_paths


@st.cache(**sc.CACHE_KWARGS)
def create_risk_reward_scatter_chart(bankroll_df, settings_dict):
    """plot kde based on bankroll"""
    kde_df = pd.DataFrame()

    for col in bankroll_df:
        max_drawdown = backtest.calculate_max_drawdown(bankroll_df[col])
        cagr = backtest.calculate_cagr(bankroll_df[col])
        kde_df = kde_df.append(
            {"cagr": cagr, "max_drawdown": max_drawdown}, ignore_index=True
        )

    # SCatter plot

    median_max_drawdown = np.median(kde_df["max_drawdown"])
    median_cagr = np.median(kde_df["cagr"])
    max_cagr = np.max(kde_df["cagr"])

    fig_risk_reward = go.Figure()
    fig_risk_reward.add_trace(  # MONTECARLO SAMPLES
        go.Scatter(
            x=kde_df["max_drawdown"],
            y=kde_df["cagr"],
            mode="markers",
            marker_color=plotting.graph_settings.accent_color,
            name="Simulation samples",
            xaxis="x",
            yaxis="y",
        )
    )
    fig_risk_reward.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[median_cagr] * 2,
            mode="lines",
            name="median_CAGR",
            line_dash="dot",
            line_width=1,
            line_color="red",
            xaxis="x",
            yaxis="y",
        )
    )

    fig_risk_reward.add_trace(  # VERTICAL MEDIAN IL
        go.Scatter(
            x=[np.median(kde_df["max_drawdown"])] * 2,
            y=[-1, max_cagr],
            mode="lines",
            name="median_max_drawdown",
            line_dash="dot",
            line_width=1,
            line_color="red",
            xaxis="x",
            yaxis="y",
        )
    )

    fig_risk_reward.add_trace(  # BREAK EVEN LINE
        go.Scatter(
            x=[0, 1],
            y=[0] * 2,
            mode="lines",
            name="break_even",
            line_dash="dash",
            line_width=1,
            line_color=plotting.graph_settings.linecolor,
            xaxis="x",
            yaxis="y",
        )
    )

    fig_risk_reward.add_annotation(  # HORIZONTAL MEDIAN CAGR
        x=0.8,
        y=median_cagr,  # math.log(median_CF),#/10,
        text="Median CAGR {}%".format(np.round(median_cagr * 100, 2)),
        font_color=plotting.graph_settings.zerolinecolor,
        showarrow=True,
        arrowhead=1,
    )

    fig_risk_reward.add_annotation(  # VERTICAL MEDIAN IL
        x=median_max_drawdown,
        y=max_cagr * 0.8,  # math.log(0.5),#/10,
        text="Median Max Drawdown {}%".format(np.round(median_max_drawdown * 100, 2)),
        font_color=plotting.graph_settings.zerolinecolor,
        showarrow=True,
        arrowhead=1,
    )

    fig_risk_reward = plotting.custom_figure_layout_update(
        fig_risk_reward,
        x_axis_name="Max Drawdown (%)",
        y_axis_name="CAGR",
        title=(
            f"Simulation bankroll results for {settings_dict['asset']} "
            f"S_{settings_dict['strike']} D_{settings_dict['duration']} days   "
            f"Paths: {settings_dict['monte_carlo_paths']}   "
            f"Period: {settings_dict['simulation_length_days']} days"
        ),
    )
    fig_risk_reward.update_layout(
        yaxis=dict(
            range=[-1, max_cagr],
        ),
        xaxis=dict(range=[0, 1]),
    )

    return fig_risk_reward


# @st.cache(**sc.CACHE_KWARGS)
def calculate_kpi_summary(bankroll_df, cagr_list, dd_list, sharpe_list, il_list):
    """create summary with stats"""
    median_bankroll = np.median(bankroll_df.tail(1))
    min_bankroll = np.min(bankroll_df.tail(1).values)
    max_bankroll = np.max(bankroll_df.tail(1).values)

    median_return = median_bankroll - 1
    min_return = min_bankroll - 1
    max_return = max_bankroll - 1

    data = {
        "Metric": [
            "Final Bankroll",
            "Return",
            "Annualized Return",
            "Max Drawdown",
            "Sharpe",
            "Impermanent Loss",
        ],
        "Min": [
            min_bankroll,
            min_return,
            min(cagr_list),
            min(dd_list),
            min(sharpe_list),
            min(il_list),
        ],
        "Median": [
            median_bankroll,
            median_return,
            np.median(cagr_list),
            np.median(dd_list),
            np.median(sharpe_list),
            np.median(il_list),
        ],
        "Max": [
            max_bankroll,
            max_return,
            max(cagr_list),
            max(dd_list),
            max(sharpe_list),
            max(il_list),
        ],
    }

    kpi_summary_df_inner = pd.DataFrame(data).style.format(
        {
            "Min": "{:.2%}".format,
            "Max": "{:.2%}".format,
            "Median": "{:.2%}".format,
        }
    )

    return kpi_summary_df_inner


@st.cache(**sc.CACHE_KWARGS)
def plot_metric_histogram(
    bankroll_df, metric_function, name="sharpe", domain=(-1, 1), x_tickformat=".0%"
):
    "Create histogram for the specified metric"
    sharpe_results = [metric_function(bankroll_df[i]) for i in bankroll_df]
    sharpe_results = [v for v in sharpe_results if not (math.isinf(v) or math.isnan(v))]

    median_sharpe = np.median(sharpe_results)

    fig_sharpe = ff.create_distplot(
        [sharpe_results], group_labels=[name.title()], show_hist=False, show_rug=False
    )
    fig_sharpe.add_trace(
        go.Scatter(
            x=[median_sharpe] * 2,
            y=[0, max(fig_sharpe.data[0]["y"])],
            mode="lines",
            name="median {name}",
            line_dash="dot",
            line_width=1,
            line_color=plotting.graph_settings.accent_color,
        )
    )
    fig_sharpe.add_annotation(
        x=np.median(sharpe_results),
        y=0,  # /10,
        text=f"Median {name} {np.round(median_sharpe, 2)}",
        font_color=plotting.graph_settings.text_color,
        showarrow=True,
        arrowhead=1,
    )

    fig_sharpe = plotting.custom_figure_layout_update(
        fig_sharpe,
        f"{name.title()}",
        "Frequency",
        title=None,
        x_tick_format=x_tickformat,
        y_tick_format=".1f",
        x_showgrid=False,
        y_showgrid=False,
        showlegend=False,
        width=400,
        height=450,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        xaxis_range=domain,
    )

    return fig_sharpe, sharpe_results


@st.cache(**sc.CACHE_KWARGS, allow_output_mutation=True)
def calculate_strike_joy_df(
    strikes_joy,
    duration,
    simulation_length_days,
    initial_util,
    premium_offset,
    bonding_curve_resolution,
    historical_df,
    asset,
    monte_carlo_paths=100,
    convolution_n_paths=10000,
    randomize_util=False,
    option_type="put",
    util_std=0.1,
):
    """Calculate cagrs and drawdowns distributions for different strikes"""
    price_sequence_sens = historical_df[asset].dropna()
    returns_sequence_sens = price_sequence_sens.pct_change()[1:]
    underlying_n_daily_returns = convolution.daily_returns_to_n_day_returns(
        returns_sequence_sens,
        number_of_paths=convolution_n_paths,
        n_days=duration,
    )
    random_return_paths_cycles_df = rpg.generate_returns_paths_from_returns(
        underlying_n_daily_returns,
        monte_carlo_paths,
        simulation_length_days // duration,
        output_as_df=True,
    )

    cagr_col = np.array([])

    strike_col = np.array([])
    dd_col = np.array([])

    strike_joy_df = pd.DataFrame()

    for strike_joy in strikes_joy:
        # Create simulated Utils path
        utils = rpg.generate_utils_list(
            simulation_length_days,
            initial_util=initial_util,
            duration=duration,
            randomize=randomize_util,
            util_std=util_std,
        )

        (tmp_premiums, _, _) = kelly.get_premiums_list_with_all_calculations(
            utils,
            premium_offset=premium_offset,
            fit_params=None,
            bonding_curve_resolution=bonding_curve_resolution,
            underlying_n_daily_returns=underlying_n_daily_returns,
            strike=strike_joy,
            option_type=option_type,
        )

        bankroll_df = backtest.run_backtest(
            random_return_paths_cycles_df,
            utils,
            tmp_premiums,
            strike_joy,
            duration,
            option_type=option_type,
        )

        dd_results = [
            backtest.calculate_max_drawdown(bankroll_df[i]) for i in bankroll_df
        ]
        cagr_results = [backtest.calculate_cagr(bankroll_df[i]) for i in bankroll_df]

        strike_col = np.round(
            np.concatenate(
                (strike_col, np.transpose([strike_joy] * len(cagr_results)))
            ),
            2,
        )

        cagr_col = np.concatenate((cagr_col, np.transpose(cagr_results)))
        dd_col = np.concatenate((dd_col, np.transpose(dd_results)))

    strike_joy_df["label"] = strike_col
    strike_joy_df["cagr"] = cagr_col
    strike_joy_df["dd"] = dd_col

    return strike_joy_df


@st.cache(**sc.CACHE_KWARGS, allow_output_mutation=True)
def calculate_duration_joy_df(
    durations_joy,
    strike,
    simulation_length_days,
    initial_util,
    premium_offset,
    bonding_curve_resolution,
    historical_df,
    asset,
    monte_carlo_paths,
    convolution_n_paths=1000,
    randomize_util=False,
    option_type="put",
    util_std=0.1,
):
    """Calculate cagrs and drawdowns distributions for different durations"""
    cagr_col = np.array([])
    duration_col = np.array([])
    dd_col = np.array([])

    duration_joy_df = pd.DataFrame()

    price_sequence = historical_df[asset]
    returns_sequence = price_sequence.pct_change().dropna()

    for duration_joy in durations_joy:
        # Create simulated Utils path
        utils = rpg.generate_utils_list(
            simulation_length_days,
            initial_util=initial_util,
            duration=duration_joy,
            randomize=randomize_util,
            util_std=util_std,
        )

        tmp_underlying_n_daily_returns = convolution.daily_returns_to_n_day_returns(
            returns_sequence,
            number_of_paths=convolution_n_paths,
            n_days=duration_joy,
        )
        tmp_random_return_paths_cycles_df = rpg.generate_returns_paths_from_returns(
            tmp_underlying_n_daily_returns,
            monte_carlo_paths,
            simulation_length_days // duration_joy,
            output_as_df=True,
        )

        (tmp_premiums, _, _) = kelly.get_premiums_list_with_all_calculations(
            utils,
            premium_offset=premium_offset,
            fit_params=None,
            bonding_curve_resolution=bonding_curve_resolution,
            underlying_n_daily_returns=tmp_underlying_n_daily_returns,
            strike=strike,
            option_type=option_type,
        )

        bankroll_df = backtest.run_backtest(
            tmp_random_return_paths_cycles_df,
            utils,
            tmp_premiums,
            strike,
            int(duration_joy),
            option_type=option_type,
        )

        dd_results = [
            backtest.calculate_max_drawdown(bankroll_df[i]) for i in bankroll_df
        ]
        cagr_results = [backtest.calculate_cagr(bankroll_df[i]) for i in bankroll_df]

        duration_col = np.round(
            np.concatenate(
                (duration_col, np.transpose([duration_joy] * len(cagr_results)))
            ),
            2,
        )

        cagr_col = np.concatenate((cagr_col, np.transpose(cagr_results)))
        dd_col = np.concatenate((dd_col, np.transpose(dd_results)))

    duration_joy_df["label"] = duration_col
    duration_joy_df["cagr"] = cagr_col
    duration_joy_df["dd"] = dd_col

    return duration_joy_df


@st.cache(**sc.CACHE_KWARGS, allow_output_mutation=True)
def calculate_mean_err_joy_df(
    mean_errs_joy_yr,
    strike,
    duration,
    simulation_length_days,
    initial_util,
    historical_df,
    asset,
    monte_carlo_paths,
    bonding_curve_resolution,
    premium_offset=0,
    convolution_n_paths=1000,
    randomize_util=False,
    option_type="put",
    util_std=0.1,
):
    """Calculate cagrs and drawdowns distributions for different yearly mean errors"""
    mean_shift_joy_day = [
        yearly_err / np.sqrt(365.0) for yearly_err in mean_errs_joy_yr
    ]

    cagr_col = np.array([])
    mean_err_col = np.array([])
    dd_col = np.array([])

    mean_err_joy_df = pd.DataFrame()

    price_sequence = historical_df[asset]
    returns_sequence = price_sequence.pct_change()[1:]
    underlying_n_daily_returns = convolution.daily_returns_to_n_day_returns(
        returns_sequence,
        number_of_paths=convolution_n_paths,
        n_days=duration,
    )

    for mean_err_joy in mean_shift_joy_day:
        # Create simulated Utils path
        utils = rpg.generate_utils_list(
            simulation_length_days,
            initial_util=initial_util,
            duration=duration,
            randomize=randomize_util,
            util_std=util_std,
        )
        shifted_returns = returns_sequence + mean_err_joy

        tmp_underlying_n_daily_returns = convolution.daily_returns_to_n_day_returns(
            shifted_returns,
            number_of_paths=convolution_n_paths,
            n_days=duration,
        )
        tmp_random_return_paths_cycles_df = rpg.generate_returns_paths_from_returns(
            tmp_underlying_n_daily_returns,
            monte_carlo_paths,
            simulation_length_days // duration,
            output_as_df=True,
        )

        (new_premiums, _, _) = kelly.get_premiums_list_with_all_calculations(
            utils,
            premium_offset=premium_offset,
            fit_params=None,
            bonding_curve_resolution=bonding_curve_resolution,
            underlying_n_daily_returns=underlying_n_daily_returns,
            strike=strike,
            option_type=option_type,
        )

        bankroll_df = backtest.run_backtest(
            tmp_random_return_paths_cycles_df,
            utils,
            new_premiums,
            strike,
            duration,
            option_type=option_type,
        )

        dd_results = [
            backtest.calculate_max_drawdown(bankroll_df[i]) for i in bankroll_df
        ]

        cagr_results = [backtest.calculate_cagr(bankroll_df[i]) for i in bankroll_df]

        mean_err_col = np.concatenate(
            (mean_err_col, np.transpose([mean_err_joy] * len(cagr_results)))
        )

        cagr_col = np.concatenate((cagr_col, np.transpose(cagr_results)))
        dd_col = np.concatenate((dd_col, np.transpose(dd_results)))

    mean_err_joy_df["label"] = mean_err_col
    mean_err_joy_df["cagr"] = cagr_col
    mean_err_joy_df["dd"] = dd_col
    return mean_err_joy_df


@st.experimental_singleton(**sc.CACHE_SINGLETON_KWARGS)
def plot_cagr_n_dd_joyplots(duration_joy_df, labels, label="duration"):
    """Create two joyplots"""
    noise = np.random.normal(0, 0.01, len(duration_joy_df))
    duration_joy_df["dd"] += noise
    duration_joy_df["cagr"] += noise
    fig_durationjoy_cagr, _ = joypy.joyplot(
        duration_joy_df,
        fill=True,
        legend=True,
        kind="kde",
        by="label",
        # ylim='own',
        column="cagr",
        x_range=[-1, 3],
        alpha=0.6,
        linecolor=plotting.graph_settings.linecolor,
        labels=labels,
        overlap=3,
        linewidth=0.75,
        background=plotting.graph_settings.background_color,
        colormap=cm.get_cmap("autumn_r"),
    )
    plt.tick_params(axis="x", colors=plotting.graph_settings.text_color)
    plt.tick_params(axis="y", colors=plotting.graph_settings.text_color)
    plt.xlabel("CAGR")
    plt.title(f"CAGR distributions for different {label}s")
    fig_durationjoy_cagr.patch.set_facecolor(plotting.graph_settings.background_color)

    fig_durationjoy_dd, _ = joypy.joyplot(
        duration_joy_df,
        fill=True,
        legend=True,
        kind="kde",
        by="label",
        # ylim='own',
        column="dd",
        labels=labels,
        x_range=[0, 1],
        alpha=0.6,
        linecolor=plotting.graph_settings.linecolor,
        overlap=3,
        linewidth=0.75,
        background=plotting.graph_settings.background_color,
        colormap=cm.get_cmap("autumn_r"),
    )
    plt.xlabel("Max Drawdown")
    plt.title(f"Max Drawdown distributions for different {label}s")
    plt.tick_params(axis="x", colors=plotting.graph_settings.text_color)
    plt.tick_params(axis="y", colors=plotting.graph_settings.text_color)
    fig_durationjoy_dd.patch.set_facecolor(plotting.graph_settings.background_color)

    return fig_durationjoy_cagr, fig_durationjoy_dd


@st.experimental_singleton(**sc.CACHE_SINGLETON_KWARGS)
def analytical_vs_backtest_match_test(
    historical_df,
    asset,
    strike,
    duration,
    simulation_length_days,
    monte_carlo_paths,
    convolution_n_paths,
    y_axis_name="cagr",
    randomize_util=False,
    option_type="put",
    util_std=0.1,
    premium_offset=0,
):
    """examine backtest results"""
    # Find historical return histogram for the underlying asset at selected duration
    price_sequence = historical_df[asset].dropna()
    returns_sequence = price_sequence.pct_change()[1:]
    underlying_n_daily_returns = convolution.daily_returns_to_n_day_returns(
        returns_sequence,
        number_of_paths=convolution_n_paths,
        n_days=duration,
    )
    random_return_paths_cycles_df = rpg.generate_returns_paths_from_returns(
        underlying_n_daily_returns,
        monte_carlo_paths,
        simulation_length_days // duration,
        output_as_df=True,
    )
    premium_vs_util_df = kelly.get_kelly_curve(
        underlying_n_daily_returns, strike, number_of_utils=11, option_type=option_type
    )

    premium_vs_util_df["premium"] *= 1 + premium_offset

    # calculations
    ############################################################################################
    analytical_kelly_bankrolls = []

    for util, premium in zip(premium_vs_util_df["util"], premium_vs_util_df["premium"]):
        log_return = kelly.get_kelly_log_expected_payout(
            underlying_n_daily_returns, strike, premium, util, option_type=option_type
        )
        analytical_kelly_bankrolls.append(
            np.power(np.exp(log_return), simulation_length_days // duration)
        )

    if y_axis_name == "cagr":
        analytical_kelly_cagrs = [
            hlp.convert_bankroll_to_cagr(bankroll, simulation_length_days / 365)
            for bankroll in analytical_kelly_bankrolls
        ]
        y_axis_range = [-1, 2]
    else:
        analytical_kelly_cagrs = analytical_kelly_bankrolls
        y_axis_range = [0, 2]

    percentiles = (0, 2.5, 25, 50, 75, 97.5, 100)

    cagr_percentiles_df = pd.DataFrame(columns=percentiles)
    drawdown_percentiles_df = pd.DataFrame(columns=percentiles)

    for util, premium in stqdm(
        zip(premium_vs_util_df["util"], premium_vs_util_df["premium"])
    ):
        utils = rpg.generate_utils_list(
            simulation_length_days,
            initial_util=util,
            duration=duration,
            randomize=randomize_util,
            util_std=util_std,
        )

        bankroll_df = backtest.run_backtest(
            random_return_paths_cycles_df,
            utils,
            [premium] * len(utils),
            strike,
            duration,
            option_type=option_type,
        )

        bankroll_df.loc[-1] = [1] * len(bankroll_df.columns)  # adding a row
        bankroll_df.index = bankroll_df.index + 1  # shifting index
        bankroll_df = bankroll_df.sort_index()  # sorting by index

        # calculate cagrs/drawdowns
        ###########################################################################################
        if y_axis_name == "cagr":
            cagrs = [backtest.calculate_cagr(bankroll_df[col]) for col in bankroll_df]
        # elif y_axis_name == "max_drawdown":
        #     cagrs = [
        #         backtest.calculate_max_drawdown(bankroll_df[col]) for col in bankroll_df
        #     ]
        else:
            cagrs = bankroll_df.tail(1).values

        max_drawdowns = [
            backtest.calculate_max_drawdown(bankroll_df[col]) for col in bankroll_df
        ]

        dict_to_append = {}
        cagr_percentiles = np.percentile(cagrs, percentiles)

        for i, cagr in enumerate(cagr_percentiles):
            dict_to_append[percentiles[i]] = cagr

        max_drawdowns_dict = {}
        drawdown_percentiles = np.percentile(max_drawdowns, percentiles)

        for i, drawdown in enumerate(drawdown_percentiles):
            max_drawdowns_dict[percentiles[i]] = drawdown
        ###########################################################################################

        cagr_percentiles_df = cagr_percentiles_df.append(
            dict_to_append, ignore_index=True
        )

        drawdown_percentiles_df = drawdown_percentiles_df.append(
            max_drawdowns_dict, ignore_index=True
        )
    cagr_percentiles_df.replace([np.inf], np.nan, inplace=True)
    cagr_percentiles_df.fillna(100, inplace=True)

    # plot
    ############################################################################################
    traces = [
        cagr_percentiles_df[100],
        cagr_percentiles_df[0],
        cagr_percentiles_df[97.5],
        cagr_percentiles_df[2.5],
        cagr_percentiles_df[75],
        cagr_percentiles_df[25],
        analytical_kelly_cagrs,
        cagr_percentiles_df[50],
    ]

    drawdown_traces = [
        drawdown_percentiles_df[100],
        drawdown_percentiles_df[0],
        drawdown_percentiles_df[97.5],
        drawdown_percentiles_df[2.5],
        drawdown_percentiles_df[75],
        drawdown_percentiles_df[25],
        drawdown_percentiles_df[50],
    ]

    trace_names = [
        "p100",
        "p0",
        "p97.5",
        "p2.5",
        "p75",
        "p25",
        "analytical",
        "backtested_median",
    ]

    line_colors = [
        "yellow",
        "yellow",
        "green",
        "green",
        "red",
        "red",
        plotting.graph_settings.accent_color,
        "red",
    ]

    fills = [None, "tonexty", None, "tonexty", None, "tonexty", None, None]

    fig_analytical_match_log_smoothed = go.Figure()
    for trace, trace_name, line_color, fill in zip(
        traces, trace_names, line_colors, fills
    ):
        if trace_name != "analytical" and "backtested" not in trace_name:
            fig_analytical_match_log_smoothed.add_trace(
                go.Scatter(
                    x=premium_vs_util_df["util"],
                    y=signal.savgol_filter(
                        trace, 5, 4  # window size used for filtering
                    ),
                    name=trace_name,
                    fill=fill,
                    mode="lines",
                    line_color=line_color,
                )
            )
        else:
            fig_analytical_match_log_smoothed.add_trace(
                go.Scatter(
                    x=premium_vs_util_df["util"],
                    y=trace,
                    name=trace_name,
                    mode="lines+markers",
                    line_color=line_color,
                )
            )

    del trace_names[6]
    del line_colors[6]
    del fills[6]

    fig_drawdowns_envelope = go.Figure()
    for trace, trace_name, line_color, fill in zip(
        drawdown_traces, trace_names, line_colors, fills
    ):
        if trace_name != "analytical" and "backtested" not in trace_name:
            fig_drawdowns_envelope.add_trace(
                go.Scatter(
                    x=premium_vs_util_df["util"],
                    y=signal.savgol_filter(
                        trace, 5, 4  # window size used for filtering
                    ),
                    name=trace_name,
                    fill=fill,
                    mode="lines",
                    line_color=line_color,
                )
            )
        else:
            fig_drawdowns_envelope.add_trace(
                go.Scatter(
                    x=premium_vs_util_df["util"],
                    y=trace,
                    name=trace_name,
                    mode="lines+markers",
                    line_color=line_color,
                )
            )

    fig_analytical_match_log_smoothed = plotting.custom_figure_layout_update(
        fig_analytical_match_log_smoothed,
        "Util",
        y_axis_name.upper(),
        title=f"Analytical CAGR Match Test|{asset} " f"S:{strike} D:{duration}",
        x_tick_format=".0%",
        y_tick_format=".0%",
        yaxis_range=y_axis_range,
    )

    fig_drawdowns_envelope = plotting.custom_figure_layout_update(
        fig_drawdowns_envelope,
        "Util",
        "Max Drawdown",
        title=f"Drawdown | {asset} S:{strike} D:{duration}",
        x_tick_format=".0%",
        y_tick_format=".0%",
        yaxis_range=[0, 1],
    )

    # fig_analytical_match_log_smoothed.update_yaxes(type="log")
    ###########################################################################################

    return fig_analytical_match_log_smoothed, fig_drawdowns_envelope


def single_instrument():
    """main function to run"""
    sc.add_cross_app_links_to_sidebar(st.sidebar)
    st.sidebar.title("Settings")
    st.session_state["randomize_util"] = st.sidebar.checkbox("Randomize Utilization")
    if st.session_state["randomize_util"]:
        st.session_state["util_std"] = (
            st.sidebar.slider("Utilization Sigma", 0, 100, 10) / 100
        )
    else:
        st.session_state["util_std"] = 0
    st.sidebar.write(
        "If random util is used, then util at the all"
        " X Axes is initial Util used at the backtest"
    )
    plotting.graph_settings = sc.add_style_settings_to_sidebar(st.sidebar)

    ###############################################################################################
    # SETTINGS
    ###############################################################################################

    # DEFAULT SETTINGs

    default_simulation_utilization = 70
    default_strike = 100
    default_premium_offset = 0

    bonding_curve_resolution = (
        # number of utils on the [0, 1] segment, passed to the get_kelly_curve
        11
    )
    convolution_n_paths = 1000

    historical_df = get_historical_prices_df()

    ###############################################################################################
    # App Markdown After all the Calculations
    ###############################################################################################
    st.title("A risk pricing strategy based on reverse Kelly Criterion")
    st.markdown("##")

    ###############################################################################################

    st.header("Proposition")
    st.markdown(
        """
        Given a pool of capital and a certain risk contract,
        a risk pricing curve exists that enforces the Kelly Criterion.
        This pricing curve is a function of the capital utilization of the pool of capital,
        and can be approximated by a hyperbolic cosine of its util, with 4 paramaters,
        that vary with the location, skewness, scale and variance of the distribution
        of probabilities of the risk taking outcomes.
    """
    )

    # Approach
    st.subheader("Approach")
    st.markdown(
        """
        The expected compounding factor of a pool of capital (1+r),
        can be described as function of the premium being charged, and the utilization of the pool.
    """
    )

    st.latex(
        r"""
            E_{k,u} [ log (1+r)]  =  \sum_{r=-1}^{max}  prob(r)
            \cdot log\left(1+Payout(premium_{k},r) \cdot Util_{u}\right)
        """
    )

    st.markdown(
        """
        In the chart below we display the expected compounding factor $(1+r)$,
        for a particular range of $premium_{k}$'s, and for utilizations from 0 to 100%.
    """
    )

    # Optimal Bonding Curves
    ##############################################################################################
    with st.expander("Optimal bonding chart...", expanded=True):
        cols_bonding_curves = st.columns([1, 4])
        params_bonding_curves = create_n_read_simple_backtest_settings(
            historical_df,
            default_strike=sc.SLIDER_DEFAULT_STRIKE,
            default_duration=sc.SLIDER_DEFAULT_DURATION,
            default_simulation_length_days=None,
            default_montecarlo_paths=None,
            default_simulation_utilization=None,
            default_premium_offset=None,
            convolution_n_paths=sc.CONVOLUTION_N_PATHS,
            additional_space_in_slider_name=5,
            streamlit_holders=[cols_bonding_curves[0]],
            option_type=1,
        )

        with st.spinner("Optimal bonding chart..."):
            (
                fig_bonding_curves,
                _,
                fig_bonding_curves_zoomed,
            ) = plot_all_kelly_curves_with_optimal_bet_annualized(
                historical_df,
                params_bonding_curves["asset"],
                params_bonding_curves["strike"],
                bonding_curve_resolution,
                params_bonding_curves["duration"],
                convolution_n_paths=params_bonding_curves["convolution_n_paths"],
                option_type=params_bonding_curves["option_type"],
                dash_line_color=plotting.graph_settings.zerolinecolor,
            )

            fig_bonding_curves = plotting.custom_figure_layout_update(
                fig_bonding_curves,
                "Util",
                "Expected CAGR",
                title=(
                    f"Expected CAGR when selling {int(params_bonding_curves['strike'])*100}% "
                    f"insurance on {params_bonding_curves['asset']},"
                    f"in {params_bonding_curves['duration']} "
                    f"day periods, priced with Kelly Optimal curves"
                ),
                x_tick_format=".0%",
                y_tick_format=".2%",
            )

            fig_bonding_curves_zoomed = plotting.custom_figure_layout_update(
                fig_bonding_curves_zoomed,
                "Util",
                "Expected CAGR",
                title=(
                    f"Expected CAGR when selling {int(params_bonding_curves['strike'])*100}% "
                    f"insurance on {params_bonding_curves['asset']},"
                    f"in {params_bonding_curves['duration']} "
                    f"day periods, priced with Kelly Optimal curves"
                ),
                x_tick_format=".0%",
                y_tick_format=".2%",
            )

            fig_bonding_curves.add_annotation(
                xref="paper",
                yref="paper",
                x=0,
                y=-0.25,
                showarrow=False,
                text=f"Fig 1. Instrument: {params_bonding_curves['asset']} "
                f"{int(params_bonding_curves['strike'] * 100)}% cover "
                f"{params_bonding_curves['duration']} days duration. "
                f"Training period: {historical_df.index[0]} to {historical_df.index[-1]}",
            )

        cols_bonding_curves[1].plotly_chart(fig_bonding_curves)
        cols_bonding_curves[1].plotly_chart(fig_bonding_curves_zoomed)
    ##############################################################################################

    st.markdown(
        """
        For this particular simulation, premiums below {premiums[0]}
        have analytical expectation of bankrupctcy.
        Premiums above {premiums[-1]} lead to no Kelly Optimal - odds are too positive,
        leaving to under_betting scenarios across the board.
        Kelly Optimal premiums naturally seek low prices that still lead to long term survival
        """
    )

    st.markdown("##")

    st.subheader("Kelly Optimized pricing curves")
    st.markdown(
        """
        The strategy is based on finding pairs of $premium_{k}$ and $util_{u}$,
        that are Kelly Criterion optimal.
        We can find these pairs of $premium_{k}$ and $util_{u}$
        by setting the derivative of $E_{k*,u*}$ to 0:
    """
    )

    st.latex(
        r"""
            \frac{dE}{dutil^{*}} = \sum_{r=-1}^{max} \frac{  prob(r) \cdot
            Payout(premium_{k^{*}},r)   }{ 1+ Payout(premium_{k^{*}},r)  \cdot util^{*} } = 0
        """
    )

    st.markdown(
        """
        Below you can see a Kelly Optimal bonding curve produced
        by finding the solution to the above equation:
    """
    )

    # Generate Bonding Curve plot
    ##############################################################################################
    with st.expander("Optimal bonding chart...", expanded=True):
        cols_optimal_curve = st.columns([1, 4])
        params_optimal_curve = create_n_read_simple_backtest_settings(
            historical_df,
            default_strike=sc.SLIDER_DEFAULT_STRIKE,
            default_duration=2,
            default_simulation_length_days=None,
            default_montecarlo_paths=None,
            default_simulation_utilization=None,
            default_premium_offset=sc.SLIDER_DEFAULT_PREMIUM_OFFSET,
            convolution_n_paths=sc.CONVOLUTION_N_PATHS,
            additional_space_in_slider_name=6,
            streamlit_holders=[cols_optimal_curve[0]],
            option_type=1,
        )

        fig_premium_vs_util = plot_raw_vs_fitted_bonding_curve(
            historical_df,
            params_optimal_curve["asset"],
            params_optimal_curve["strike"],
            params_optimal_curve["duration"],
            bonding_curve_resolution,
            convolution_n_paths,
            premium_offset=params_optimal_curve["premium_offset"],
            option_type=params_optimal_curve["option_type"],
        )
        cols_optimal_curve[1].plotly_chart(fig_premium_vs_util)
    ##############################################################################################

    st.markdown(
        """
        This curve can be used by insurance providers to determine the price they should charge.
        The size of any incoming order is inmediately equivalent to a certain capital utilization,
        and therefore it can be retrieved from the curve.
    """
    )

    st.markdown("##")

    st.subheader("Kelly Curve parametrization")

    st.markdown(
        """
        Kelly Curves produced by this method, have shown to approximate to a hyperbolic
        cosine function of the following family:
    """
    )

    st.latex(
        r"""
        Kelly Optimal Premium(instrument_{k}) \approx  a_{k} \cdot util
        \cdot cosh(b_{k} \cdot util^{c_{k}})+d_{k}
    """
    )

    st.markdown(
        """
        A smart contract storing only 4 paramaters $a_{k}$ $b_{k}$ $c_{k}$ $d_{k}$
        would be able to recreat the entire 0 to 100% utilization range at full resolution.
    """
    )

    # Simulated Bankrolls
    st.header("Montecarlo Backtesting")

    st.markdown(
        """
        The simulation assumes:
        - A participant selling insurance priced with Kelly Optimal curves
        - Random simulated price scenarios have
        the same statistical behaviour as the underlying_asset
        - Utilizations are constant (this is simulated later separately)
    """
    )

    # main values calculation
    ###############################################################################################

    if st.checkbox("Run Backtest"):
        with st.expander("Backtest Settings", expanded=True):
            settings_cols = st.columns(4)
            params_simple_backtest = {}
            params_simple_backtest["asset"] = settings_cols[0].selectbox(
                "Choose the protected asset         ",
                historical_df.columns,
            )

            params_simple_backtest["option_type"] = settings_cols[0].selectbox(
                "Choose Option Type         ",
                ["put", "call (beta)"],
            )

            params_simple_backtest["strike"] = (
                settings_cols[1].slider(
                    "Insurance level (%)         ",
                    70,
                    130,
                    default_strike,
                    1,
                )
                / 100
            )  # 1.1 = 10% in the money

            params_simple_backtest["duration"] = settings_cols[1].slider(
                "Insurance Duration (days)         ",
                1,
                28,
                1,
            )

            params_simple_backtest["simulation_length_days"] = settings_cols[2].slider(
                "Simulation Time horizon (days)         ",
                sc.SLIDER_MIN_DAYS,
                sc.SLIDER_MAX_DAYS,
                sc.SLIDER_DEFAULT_DAYS,
            )  # number of option life cycles to use for backtest

            params_simple_backtest["monte_carlo_paths"] = settings_cols[2].slider(
                "Number of paths (simulation depth)         ",
                sc.SLIDER_MIN_PATHS,
                sc.SLIDER_MAX_PATHS,
                sc.SLIDER_DEFAULT_PATHS,
                20,
            )  # number of the random paths to do backtest

            params_simple_backtest["convolution_n_paths"] = convolution_n_paths

            params_simple_backtest["initial_util"] = (
                settings_cols[3].slider(
                    "Utilization simulated         ",
                    0,
                    100,
                    default_simulation_utilization,
                )
                / 100
            )

            params_simple_backtest["premium_offset"] = (
                settings_cols[3].slider(
                    "Premium offset simulated (%)         ",
                    -100,
                    100,
                    default_premium_offset,
                    5,
                )
                / 100
            )  # 0. # 0.1 = 10% additional relative premium
            # Create simulated Utils path
            params_simple_backtest["utils"] = rpg.generate_utils_list(
                params_simple_backtest["simulation_length_days"],
                initial_util=params_simple_backtest["initial_util"],
                duration=params_simple_backtest["duration"],
                randomize=st.session_state["randomize_util"],
                util_std=st.session_state["util_std"],
            )

            price_sequence = historical_df[params_simple_backtest["asset"]].dropna()
            returns_sequence = price_sequence.pct_change()[1:]
            underlying_n_daily_returns = daily_returns_to_n_day_returns(
                returns_sequence,
                number_of_paths=params_simple_backtest["convolution_n_paths"],
                n_days=params_simple_backtest["duration"],
            )
            random_return_paths_cycles_df = generate_returns_paths_from_returns(
                underlying_n_daily_returns,
                params_simple_backtest["monte_carlo_paths"],
                params_simple_backtest["simulation_length_days"]
                // params_simple_backtest["duration"],
                output_as_df=True,
            )

            # premiums
            (premiums, _, _,) = kelly.get_premiums_list_with_all_calculations(
                params_simple_backtest["utils"],
                premium_offset=params_simple_backtest["premium_offset"],
                fit_params=None,
                bonding_curve_resolution=bonding_curve_resolution,
                underlying_n_daily_returns=underlying_n_daily_returns,
                strike=params_simple_backtest["strike"],
                option_type=params_simple_backtest["option_type"],
            )

            bankroll_df = backtest.run_backtest(
                random_return_paths_cycles_df,
                params_simple_backtest["utils"],
                premiums,
                params_simple_backtest["strike"],
                params_simple_backtest["duration"],
                option_type=params_simple_backtest["option_type"],
            )

            bankroll_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            bankroll_df = bankroll_df.dropna()
            bankroll_df = bankroll_df.reset_index(drop=True)
            bankroll_df.loc[-1] = [1] * len(bankroll_df.columns)  # adding a row
            bankroll_df.index = bankroll_df.index + 1  # shifting index
            bankroll_df.sort_index(inplace=True)

            fig_bankrolls, fig_cagr_paths = create_bankrolls_cagrs_figs(
                bankroll_df,
                params_simple_backtest["asset"],
                params_simple_backtest["strike"],
                params_simple_backtest["duration"],
            )
            st.plotly_chart(fig_bankrolls)

            st.plotly_chart(fig_cagr_paths)

            st.subheader("Results Scatter chart")

            fig_risk_reward = create_risk_reward_scatter_chart(
                bankroll_df, params_simple_backtest
            )
            st.plotly_chart(fig_risk_reward)

            st.subheader("Performance metrics")
            st.markdown(
                """
                Find below fundamental financial performance indicators:
            """
            )

            col1, col2 = st.columns(2)
            fig_sharpe, sharpe_list = plot_metric_histogram(
                bankroll_df,
                backtest.calculate_sharpe,
                name="sharpe",
                domain=[-0.5, 1],
                x_tickformat=".1f",
            )
            fig_cagr, cagr_list = plot_metric_histogram(
                bankroll_df, backtest.calculate_cagr, name="cagr", domain=[-1, 1]
            )
            fig_il, il_list = plot_metric_histogram(
                bankroll_df,
                backtest.calculate_max_initial_capital_loss,
                name="IL",
                domain=[0, 1],
            )
            fig_dd, dd_list = plot_metric_histogram(
                bankroll_df,
                backtest.calculate_max_drawdown,
                name="max drawdown",
                domain=[0, 1],
            )
            col1.plotly_chart(fig_cagr)
            col1.plotly_chart(fig_sharpe)
            col2.plotly_chart(fig_il)
            col2.plotly_chart(fig_dd)

            kpi_summary_df = calculate_kpi_summary(
                bankroll_df, cagr_list, dd_list, sharpe_list, il_list
            )
            st.dataframe(kpi_summary_df)

            st.markdown("##")

    # Analytical Match Test
    ###############################################################################################
    st.subheader("Analytical Match Test")
    st.markdown(
        r"""
        We test how the bankrolls observed in our montercarlo simulations,
        compare with those analytically expected.
        As you can see, when simulations are sufficiently deep,
        the median simulated result perfectly matches analyatically expected one.
        In the chart you can see overlayed
        the various intervals of confidence surrounding the median result.
        """
    )
    checkbox_analytical_match = st.checkbox("Run Analytical Match Test")
    if checkbox_analytical_match:
        with st.expander("Analytical vs Backtest", expanded=True):
            columns_analytical_match = st.columns(4)
            params_analytical_match = create_n_read_simple_backtest_settings(
                historical_df,
                default_strike=sc.SLIDER_DEFAULT_STRIKE,
                default_duration=sc.SLIDER_DEFAULT_DURATION,
                default_simulation_length_days=sc.SLIDER_DEFAULT_DAYS,
                default_montecarlo_paths=sc.SLIDER_DEFAULT_PATHS,
                default_simulation_utilization=None,
                default_premium_offset=0,
                convolution_n_paths=sc.CONVOLUTION_N_PATHS,
                additional_space_in_slider_name=1,
                y_axis_name=1,
                streamlit_holders=columns_analytical_match,
                max_simulation_paths=sc.SLIDER_MAX2_PATHS,
                option_type=1,
                max_simulation_days=sc.SLIDER_MAX2_DAYS,
            )

            with st.spinner("Analytical vs Backtest CAGR match test"):

                (
                    fig_analytical_match_log_smoothed,
                    fig_drawdowns_envelope,
                ) = analytical_vs_backtest_match_test(
                    historical_df,
                    params_analytical_match["asset"],
                    params_analytical_match["strike"],
                    params_analytical_match["duration"],
                    params_analytical_match["simulation_length_days"],
                    params_analytical_match["monte_carlo_paths"],
                    convolution_n_paths=params_analytical_match["convolution_n_paths"],
                    y_axis_name=params_analytical_match["y_axis_name"],
                    randomize_util=st.session_state["randomize_util"],
                    option_type=params_analytical_match["option_type"],
                    util_std=st.session_state["util_std"],
                    premium_offset=params_analytical_match["premium_offset"],
                )
                st.plotly_chart(fig_analytical_match_log_smoothed)
                st.plotly_chart(fig_drawdowns_envelope)

    ###############################################################################################
    # Sensitivity Tests
    ###############################################################################################
    st.subheader("Sensitivity Tests")
    st.markdown(
        r"""
        We test how the CAGRs/Drawdowns observed in our montercarlo simulations
        evolve with params change.
        """
    )
    # Strikes
    ###############################################################################################
    checkbox_strikes = st.checkbox("Run Stike Sensitivity Test")
    if checkbox_strikes:
        with st.expander("Strikes Testing", expanded=True):
            cols_strikes = st.columns(4)
            params_sensitivity_tests_strikes = create_n_read_simple_backtest_settings(
                historical_df,
                default_strike=None,
                default_duration=sc.SLIDER_DEFAULT_DURATION,
                default_simulation_length_days=sc.SLIDER_DEFAULT_DAYS,
                default_montecarlo_paths=sc.SLIDER_DEFAULT_PATHS,
                default_simulation_utilization=sc.SLIDER_DEFAULT_UTIL,
                default_premium_offset=sc.SLIDER_DEFAULT_PREMIUM_OFFSET,
                convolution_n_paths=sc.CONVOLUTION_N_PATHS,
                additional_space_in_slider_name=2,
                streamlit_holders=cols_strikes,
                option_type=1,
            )

            with st.spinner("Strike_Joyplots..."):
                if params_sensitivity_tests_strikes["option_type"] == "put":
                    strikes_joy = np.round(np.linspace(0.8, 1.5, 10, True), 2)
                else:
                    strikes_joy = np.round(np.linspace(0.8, 1.1, 10, True), 2)
                strike_joy_df = calculate_strike_joy_df(
                    strikes_joy,
                    params_sensitivity_tests_strikes["duration"],
                    params_sensitivity_tests_strikes["simulation_length_days"],
                    params_sensitivity_tests_strikes["initial_util"],
                    params_sensitivity_tests_strikes["premium_offset"],
                    bonding_curve_resolution,
                    historical_df,
                    params_sensitivity_tests_strikes["asset"],
                    monte_carlo_paths=params_sensitivity_tests_strikes[
                        "monte_carlo_paths"
                    ],
                    convolution_n_paths=params_sensitivity_tests_strikes[
                        "convolution_n_paths"
                    ],
                    randomize_util=st.session_state["randomize_util"],
                    option_type=params_sensitivity_tests_strikes["option_type"],
                    util_std=st.session_state["util_std"],
                )

                fig_strikejoy_cagr, fig_strikejoy_dd = plot_cagr_n_dd_joyplots(
                    strike_joy_df, strikes_joy, label="strike"
                )

                st.pyplot(fig_strikejoy_cagr)
                st.pyplot(fig_strikejoy_dd)
    ###############################################################################################

    # Durations
    ###############################################################################################
    checkbox_durations = st.checkbox("Run Duration Sensitivity Test")
    if checkbox_durations:
        with st.expander("Durations Testing", expanded=True):
            cols_durations = st.columns(4)
            params_sensitivity_tests_durations = create_n_read_simple_backtest_settings(
                historical_df,
                default_strike=sc.SLIDER_DEFAULT_STRIKE,
                default_duration=None,
                default_simulation_length_days=sc.SLIDER_DEFAULT_DAYS,
                default_montecarlo_paths=sc.SLIDER_DEFAULT_PATHS,
                default_simulation_utilization=sc.SLIDER_DEFAULT_UTIL,
                default_premium_offset=sc.SLIDER_DEFAULT_PREMIUM_OFFSET,
                convolution_n_paths=sc.CONVOLUTION_N_PATHS,
                additional_space_in_slider_name=3,
                streamlit_holders=cols_durations,
                option_type=1,
            )

            with st.spinner("duration_Joyplots..."):
                # def backtest_different_durations():
                durations_joy = np.linspace(1, 30, 10, True).astype(int)

                durations_joy_df = calculate_duration_joy_df(
                    durations_joy,
                    params_sensitivity_tests_durations["strike"],
                    params_sensitivity_tests_durations["simulation_length_days"],
                    params_sensitivity_tests_durations["initial_util"],
                    params_sensitivity_tests_durations["premium_offset"],
                    bonding_curve_resolution,
                    historical_df,
                    params_sensitivity_tests_durations["asset"],
                    monte_carlo_paths=params_sensitivity_tests_durations[
                        "monte_carlo_paths"
                    ],
                    randomize_util=st.session_state["randomize_util"],
                    option_type=params_sensitivity_tests_durations["option_type"],
                    util_std=st.session_state["util_std"],
                )
                fig_duration_joy_cagr, fig_duration_joy_dd = plot_cagr_n_dd_joyplots(
                    durations_joy_df, durations_joy, label="duration"
                )

                st.pyplot(fig_duration_joy_cagr)
                st.pyplot(fig_duration_joy_dd)
    ###############################################################################################
    checkbox_err = st.checkbox("Run Mean Error Sensitivity Test")
    if checkbox_err:
        with st.expander("Mean Error Testing", expanded=True):
            cols_err = st.columns(4)
            params_sensitivity_tests_err = create_n_read_simple_backtest_settings(
                historical_df,
                default_strike=sc.SLIDER_DEFAULT_STRIKE,
                default_duration=sc.SLIDER_DEFAULT_DURATION,
                default_simulation_length_days=sc.SLIDER_DEFAULT_DAYS,
                default_montecarlo_paths=sc.SLIDER_DEFAULT_PATHS,
                default_simulation_utilization=sc.SLIDER_DEFAULT_UTIL,
                default_premium_offset=sc.SLIDER_DEFAULT_PREMIUM_OFFSET,
                convolution_n_paths=sc.CONVOLUTION_N_PATHS,
                additional_space_in_slider_name=4,
                streamlit_holders=cols_err,
                option_type=1,
            )

            with st.spinner("mean_err_Joyplots..."):
                mean_errs_joy_yr = [
                    -1,
                    -0.5,
                    -0.25,
                    0,
                    0.25,
                    0.5,
                    1,
                ]
                mean_err_joy_df = calculate_mean_err_joy_df(
                    mean_errs_joy_yr,
                    params_sensitivity_tests_err["strike"],
                    params_sensitivity_tests_err["duration"],
                    params_sensitivity_tests_err["simulation_length_days"],
                    params_sensitivity_tests_err["initial_util"],
                    historical_df,
                    params_sensitivity_tests_err["asset"],
                    monte_carlo_paths=params_sensitivity_tests_err["monte_carlo_paths"],
                    bonding_curve_resolution=bonding_curve_resolution,
                    premium_offset=params_sensitivity_tests_err["premium_offset"],
                    convolution_n_paths=params_sensitivity_tests_err[
                        "convolution_n_paths"
                    ],
                    randomize_util=st.session_state["randomize_util"],
                    option_type=params_sensitivity_tests_err["option_type"],
                    util_std=st.session_state["util_std"],
                )

                fig_mean_err_joy_cagr, fig_mean_err_joy_dd = plot_cagr_n_dd_joyplots(
                    mean_err_joy_df, mean_errs_joy_yr, label="Yearly Return Error"
                )

                st.pyplot(fig_mean_err_joy_cagr)
                st.pyplot(fig_mean_err_joy_dd)

    ###############################################################################################
    # Random vs non Random Util Chart
    ###############################################################################################
    st.subheader("How does random util affect results?")

    checkbox_utils = st.checkbox("Run Backtest   ")
    if checkbox_utils:
        with st.expander("Random Util effect", expanded=True):

            cols_random_util = st.columns(4)
            params_random_util = create_n_read_simple_backtest_settings(
                historical_df,
                default_strike=sc.SLIDER_DEFAULT_STRIKE,
                default_duration=sc.SLIDER_DEFAULT_DURATION,
                default_simulation_length_days=sc.SLIDER_DEFAULT_DAYS,
                default_montecarlo_paths=sc.SLIDER_DEFAULT_PATHS,
                default_simulation_utilization=sc.SLIDER_DEFAULT_UTIL,
                default_premium_offset=sc.SLIDER_DEFAULT_PREMIUM_OFFSET,
                convolution_n_paths=sc.CONVOLUTION_N_PATHS,
                additional_space_in_slider_name=7,
                streamlit_holders=cols_random_util,
                option_type=1,
            )
            params_random_util["util_std"] = (
                cols_random_util[0].slider("Utilization Sigma ", 0, 100, 50) / 100
            )

            utils_labels = [
                f"Fixed Util @ {params_random_util['initial_util']*100}% ",
                f'Gaussian Util @{params_random_util["initial_util"]},'
                f' std={params_random_util["util_std"]}',
                "Uniform Random Util [0, 1] space",
            ]

            kde_dfs_list = calculate_kdes(
                historical_df,
                params_random_util["asset"],
                params_random_util["initial_util"],
                params_random_util["util_std"],
                params_random_util["strike"],
                params_random_util["duration"],
                params_random_util["simulation_length_days"],
                params_random_util["monte_carlo_paths"],
                bonding_curve_resolution,
                premium_offset=params_random_util["premium_offset"],
                convolution_n_paths=params_random_util["convolution_n_paths"],
                option_type=params_random_util["option_type"],
            )

            # find y_axis_limit
            min_y_lim = 0
            max_y_lim = 0
            for kde_df in kde_dfs_list:
                current_min = np.min(kde_df["cagr"].values)
                current_max = np.max(kde_df["cagr"].values)
                if current_min < min_y_lim:
                    min_y_lim = current_min
                if current_max > max_y_lim:
                    max_y_lim = current_max
            for i, kde_df in enumerate(kde_dfs_list):
                st.write(utils_labels[i])

                fig_kde = plot_kde(kde_df, ylims=(min_y_lim, max_y_lim))
                # trick to control size of the Matplotlib plot
                buf = io.BytesIO()
                fig_kde.savefig(buf, format="png")

                st.image(buf)
                st.markdown("""---""")


if __name__ == "__main__":
    sc.setup_page_config("A RISK PRICING STRATEGY BASED ON REVERSE KELLY CRITERION")
    single_instrument()
    st.markdown(
        sc.get_footer(
            plotting.graph_settings.text_color, plotting.graph_settings.background_color
        ),
        unsafe_allow_html=True,
    )

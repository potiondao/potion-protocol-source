#!/usr/bin/env python3
"""Script which runs flow3 streamlit app"""
import os
import io
import random
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
from stqdm import stqdm

import lib.helpers as hlp
import lib.backtest as backtest
import lib.plotting as plotting
import lib.kelly as kelly
import lib.random_path_generation as rpg
import lib.steamlit_components as sc

# DEFAULT SIDEBAR SETTINGS
DEFAULT_CLUSTERIZATION_PREMIUM_RELATIVE_THRESHOLD = 80

DEFAULT_MAX_DRAWDOWN_PICK = 50

DEFAULT_CAGR_PICK = 10
DEFAULT_PORTFOLIO_UTIL = 50

# OTHER SETTINGS
BONDING_CURVE_RESOLUTION = (
    100  # number of utils on the [0, 1] segment, passed to the get_kelly_curve
)

flow2_plot = st.cache(plotting.flow2_plot, **sc.CACHE_KWARGS)

#############################################################################################
# FUNCTIONS
#############################################################################################

rgb_int = lambda: random.randint(0, 255)

@st.cache(show_spinner=False, suppress_st_warning=True, ttl=3600, max_entries=725)
def backtest_asset_dict(*args, **kwargs):
    '''Caching wrapper'''
    return backtest.backtest_asset_dict(*args, **kwargs)

@st.cache(**sc.CACHE_KWARGS)
def create_kde_df(*args, **kwargs):
    '''Caching wrapper'''
    return backtest.create_kde_df(*args, **kwargs)

@st.experimental_singleton(**sc.CACHE_SINGLETON_KWARGS)
def plot_kdes(*args, **kwargs):
    '''Caching wrapper'''
    return plotting.plot_kdes(*args, **kwargs)

@st.cache(**sc.CACHE_KWARGS)
def get_historical_prices_df():
    '''Caching wrapper'''
    return hlp.get_historical_prices_df()

@st.cache(show_spinner=False, suppress_st_warning=True, ttl=3600, max_entries=1)
def read_dir(dir_to_read):
    """list dir wrapper"""
    input_files = os.listdir(dir_to_read)
    input_files = [
        input_file for input_file in input_files if "backtested" in input_file
    ]
    return input_files


def create_introduction():
    """Write Main text at the page"""
    # Title
    ###########################################################################################
    st.title("Pricing/Backtest of the Portfolio based on Kelly Criteria")
    st.header("Proposition")
    st.write(
        "We could backtest a bunch of instruments with the one bonding curve for all of them"
    )
    # Introduction/Overview
    ###########################################################################################
    intro_expander = st.expander(label="Introduction/Overview", expanded=True)
    with intro_expander:
        st.markdown(" **Introduction/Overview** ")
        st.write(
            "Let's see at the many backtest results and pick region of risk/reward"
        )
        st.write(
            (
                "Now we have a number of instruments:"
                "lets get the Optimal Bonding Curve for each one"
            )
        )
        st.write(
            (
                "Then we cluster the Bonding Curves to make sure "
                "we are left with the instruments"
                ", which are close to each other"
            )
        )
        st.write(
            (
                "We use the highest Bonding Curve from the cluster for all the instruments"
                "and backtest portfolio of all those instruments"
            )
        )


@st.cache(**sc.CACHE_KWARGS)
def calculate_bonding_curves(
    historical_df, picked_instruments, clusterization_premium_relative_threshold
):
    """Calculate Bonding curves for each instrument
    and do clusterization"""
    # calculate bonding curves for each instrument
    ###########################################################################################
    picked_instruments["price_series"] = None
    picked_instruments["returns_series"] = None
    picked_instruments["kelly_curve_df"] = None
    picked_instruments["min_premium"] = None
    picked_instruments["max_premium"] = None
    for index, row in picked_instruments.iterrows():

        picked_instruments.at[index, "price_series"] = historical_df[
            row["asset"]
        ].dropna()
        picked_instruments.at[index, "returns_series"] = picked_instruments.at[
            index, "price_series"
        ].pct_change()[1:]

        picked_instruments.at[index, "kelly_params"] = [
            float(i)
            for i in str(row["kelly_params"])
            .replace("[", "")
            .replace("]", "")
            .replace(",", "")
            .split(" ")
            if i != ""
        ]
        picked_instruments.at[index, "kelly_curve_df"] = kelly.get_curve_df(
            *picked_instruments.at[index, "kelly_params"], BONDING_CURVE_RESOLUTION
        )

        picked_instruments.at[index, "left_premium"] = picked_instruments.at[
            index, "kelly_curve_df"
        ]["premium"].values[0]
        picked_instruments.at[index, "right_premium"] = picked_instruments.at[
            index, "kelly_curve_df"
        ]["premium"].values[-1]

    # clusterization of the curves
    ###########################################################################################
    picked_instruments.sort_values(by="left_premium", inplace=True)
    picked_instruments["cluster"] = None
    cluster_info_dicts = {}
    for index, row in picked_instruments.iterrows():
        found_cluster = False
        for key, info_dict in cluster_info_dicts.items():
            if (
                row["left_premium"] >= info_dict["min_left"]
                and row["left_premium"] <= info_dict["max_left"]
                and row["right_premium"] >= info_dict["min_right"]
                and row["right_premium"] <= info_dict["max_right"]
            ):
                picked_instruments.at[index, "cluster"] = key
                found_cluster = True
                break

        if not found_cluster:
            picked_instruments.at[index, "cluster"] = len(cluster_info_dicts)
            cluster_info_dicts[len(cluster_info_dicts)] = {
                "min_left": row["left_premium"],
                "max_left": row["left_premium"]
                * (1 + clusterization_premium_relative_threshold),
                "min_right": row["right_premium"],
                "max_right": row["right_premium"]
                * (1 + clusterization_premium_relative_threshold),
            }

    # add unique color for each cluster
    ###########################################################################################

    cluster_colors = {}
    picked_instruments["color"] = None
    for index, row in picked_instruments.iterrows():
        if row["cluster"] in cluster_colors:
            picked_instruments.at[index, "color"] = cluster_colors[row["cluster"]]
        else:
            cluster_colors[
                row["cluster"]
            ] = f"rgb({rgb_int()}, {rgb_int()}, {rgb_int()})"
            picked_instruments.at[index, "color"] = cluster_colors[row["cluster"]]

    # plot bonding curves for each instrument
    ###########################################################################################
    fig_bonding_curves = go.Figure()
    for index, row in picked_instruments.iterrows():
        fig_bonding_curves.add_trace(
            go.Scatter(
                x=row["kelly_curve_df"]["util"],
                y=row["kelly_curve_df"]["premium"],
                mode="lines",
                name=(
                    f'Cl={row["cluster"]}_lp={round(row["left_premium"], 3)}'
                    f'rp={round(row["right_premium"], 3)}'
                ),
                line_color=row["color"],
            )
        )

    plotting.custom_figure_layout_update(
        fig_bonding_curves,
        x_axis_name="util",
        y_axis_name="premium",
        title="Bonding Curves",
        x_tick_format=".0%",
        y_tick_format=".1%",
        x_showgrid=False,
        y_showgrid=False,
    )

    return picked_instruments, fig_bonding_curves


@st.cache(**sc.CACHE_KWARGS)
def pick_largest_cluster(picked_instruments):
    """pick the largest cluster"""

    largest_cluster_len = 0
    largest_cluster = None
    for cluster_number, cluster_size in (
        picked_instruments["cluster"].value_counts().items()
    ):
        if cluster_size > largest_cluster_len:
            largest_cluster = cluster_number
            largest_cluster_len = cluster_size

    return largest_cluster, largest_cluster_len


@st.cache(**sc.CACHE_KWARGS)
def get_cluster_info(picked_instruments):
    """Create df with cluster information"""
    cluster_info_df = pd.DataFrame(
        columns=[
            "cluster_id",
            "number of curves",
            "max_premium_diff_pct",
            "max_strike, %",
            "min_strike, %",
            "min_duration, days",
            "max_duration, days",
        ],
        index=range(len(picked_instruments["cluster"].unique())),
    )
    for cluster_number, cluster_size in (
        picked_instruments["cluster"].value_counts().items()
    ):
        tmp_cluster_df = picked_instruments[
            picked_instruments["cluster"] == cluster_number
        ]
        cluster_info_df.at[cluster_number, "cluster_id"] = cluster_number
        cluster_info_df.at[cluster_number, "number of curves"] = cluster_size

        cluster_info_df.at[cluster_number, "max_strike, %"] = tmp_cluster_df[
            "strike"
        ].max()
        cluster_info_df.at[cluster_number, "min_strike, %"] = tmp_cluster_df[
            "strike"
        ].min()
        cluster_info_df.at[cluster_number, "min_duration, days"] = tmp_cluster_df[
            "duration"
        ].min()
        cluster_info_df.at[cluster_number, "max_duration, days"] = tmp_cluster_df[
            "duration"
        ].max()
        cluster_info_df.at[cluster_number, "max_premium_diff_pct"] = (
            max(
                (
                    tmp_cluster_df["left_premium"].max()
                    - tmp_cluster_df["left_premium"].min()
                )
                / tmp_cluster_df["left_premium"].min(),
                (
                    tmp_cluster_df["right_premium"].max()
                    - tmp_cluster_df["right_premium"].min()
                )
                / tmp_cluster_df["right_premium"].min(),
            )
            * 100
        )

    return cluster_info_df.sort_values(by="number of curves", ascending=False)


@st.cache(show_spinner=False, suppress_st_warning=True, ttl=3600, max_entries=1000)
def calculate_bankrolls(
    clustered_instruments,
    simulation_length_days,
    number_of_paths,
    portfolio_util=0.5,
    returns_abs_shift=0,
):
    """calculate bankrolls_df"""
    clustered_instruments_inner = clustered_instruments.copy()
    # random index sampling
    ###########################################################################################
    returns_df = pd.DataFrame()
    assets_proccessed = []
    cols = clustered_instruments_inner.index.to_list()
    list_of_series = clustered_instruments_inner["returns_series"].values
    for col, returns_series in zip(cols, list_of_series):
        if clustered_instruments_inner.at[col, "asset"] in assets_proccessed:
            continue
        if returns_df.empty:
            returns_df = pd.DataFrame(returns_series.rename(col))
        else:
            returns_df = returns_df.merge(
                pd.DataFrame(returns_series.rename(col)), how="outer", on="date"
            )
        assets_proccessed.append(clustered_instruments_inner.at[col, "asset"])
    returns_df.dropna(inplace=True)
    returns_df.rename(
        columns=lambda col_name: clustered_instruments_inner.at[col_name, "asset"],
        inplace=True,
    )
    random_returns_indexes_path_dict = {}
    for i in range(number_of_paths):
        random_returns_indexes_path_dict[i] = np.random.randint(
            0, len(returns_df), simulation_length_days
        )

    # Finally create Monte Carlo returns paths and backtest
    ###########################################################################################
    util_dict = {
        x: portfolio_util / len(clustered_instruments_inner)
        for x in clustered_instruments_inner.index.values
    }

    clustered_instruments_inner["daily_returns_paths"] = None
    clustered_instruments_inner["cycles_returns_paths"] = None
    clustered_instruments_inner["payoff_daily"] = None

    total_payoff_df = pd.DataFrame()
    bankroll_df = pd.DataFrame()

    for index, row in clustered_instruments_inner.iterrows():
        # Create Utils lists
        ##########################################################################
        utils = rpg.generate_utils_list(
            simulation_length_days,
            initial_util=util_dict[index],
            duration=row["duration"],
            randomize=False,
        )
        ##########################################################################
        # Premiums Calculation
        ##########################################################################
        # chosing fit params of the highest curve over here
        premiums, _, _ = kelly.get_premiums_list_with_all_calculations(
            utils,
            premium_offset=0.0,
            fit_params=clustered_instruments_inner.at[
                len(util_dict) - 1, "kelly_params"
            ],
        )
        ##########################################################################

        # Create daily returns paths
        ##########################################################################
        path_list = []
        for i in range(number_of_paths):
            returns_path = returns_df.iloc[random_returns_indexes_path_dict[i]][
                row["asset"]
            ].values

            path_list.append(returns_path)
        # monte_carlo_generated_returns_df[row["asset"]] = path_list[path_num]
        ##########################################################################
        # Convert daily returns path to the option expiration cycles returns path
        ##########################################################################
        daily_paths_df = pd.DataFrame(path_list).T + 1
        daily_paths_df = daily_paths_df + returns_abs_shift

        cycles_returns_paths_df = pd.DataFrame(columns=daily_paths_df.columns)
        i = 0

        while i + row["duration"] < simulation_length_days:
            cycles_returns_paths_df = cycles_returns_paths_df.append(
                daily_paths_df[i : i + row["duration"]].cumprod().tail(1),
                ignore_index=True,
            )
            i += row["duration"]

        cycles_returns_paths_df -= 1

        clustered_instruments_inner.at[index, "daily_returns_paths"] = (
            daily_paths_df - 1
        )
        clustered_instruments_inner.at[
            index, "cycles_returns_paths"
        ] = cycles_returns_paths_df

        ##########################################################################
        # Actual Backtest
        ##########################################################################
        # calculate payoffs at the option expiration with 0 premia
        if clustered_instruments_inner.at[index, "option_type"] == "call":
            payoff_cycles_df = clustered_instruments_inner.at[
                index, "cycles_returns_paths"
            ].applymap(kelly.call_option_payout, strike=row["strike"], premium=0)
        else:
            payoff_cycles_df = clustered_instruments_inner.at[
                index, "cycles_returns_paths"
            ].applymap(kelly.put_option_payout, strike=row["strike"], premium=0)
        # add zeros to the payoffs to account for the days before the expiration
        payoff_cycles_df.index = range(
            row["duration"] - 1,
            row["duration"] * len(payoff_cycles_df) + row["duration"] - 1,
            row["duration"],
        )

        payoff_days_df = payoff_cycles_df.reindex(index=range(simulation_length_days))
        payoff_days_df.fillna(0, inplace=True)

        payoff_days_df = (payoff_days_df.add(premiums, axis=0)).multiply(utils, axis=0)
        clustered_instruments_inner.at[index, "payoff_daily"] = payoff_days_df
        ##########################################################################

        if total_payoff_df.empty:
            total_payoff_df = clustered_instruments_inner.at[index, "payoff_daily"]
        else:
            total_payoff_df += clustered_instruments_inner.at[index, "payoff_daily"]

    total_payoff_df = total_payoff_df + 1
    bankroll_df = total_payoff_df.cumprod(axis=0)

    fig_bankrolls = plotting.plot_paths(
        bankroll_df,
        kind="Banroll",
    )

    return bankroll_df, clustered_instruments_inner, fig_bankrolls


@st.cache(**sc.CACHE_KWARGS)
def calculate_bankroll_df_stats(bankroll_df):
    """bankroll_df => tuple of medians"""
    # Check the final bankroll stats and compare with the original cluster
    ###########################################################################################
    bankroll = np.median(bankroll_df.tail(1).values)
    # number of years is quite questionable thing over here
    cagr = backtest.calculate_percentiles(backtest.calculate_cagr, bankroll_df)[2]
    max_loss_to_initial = backtest.calculate_percentiles(
        backtest.calculate_max_initial_capital_loss, bankroll_df
    )[2]
    max_drawdown = backtest.calculate_percentiles(
        backtest.calculate_max_drawdown, bankroll_df
    )[2]
    final_bankroll_std = np.std(bankroll_df.tail(1).values)
    sharpe_ratio = backtest.calculate_percentiles(
        backtest.calculate_sharpe, bankroll_df
    )[2]
    ir_ratio = backtest.calculate_percentiles(
        backtest.calculate_information_ratio, bankroll_df
    )[2]

    return (
        bankroll,
        cagr,
        max_loss_to_initial,
        max_drawdown,
        final_bankroll_std,
        sharpe_ratio,
        ir_ratio,
    )


@st.cache(**sc.CACHE_KWARGS)
def plot_price_paths(clustered_instruments_outer):
    """Cache plotting Price Paths"""
    price_path_fig = go.Figure()
    for _, row1 in clustered_instruments_outer.iterrows():
        price_path_df = (row1["daily_returns_paths"] + 1).cumprod(axis=0)
        price_path_df.loc[-1] = [1] * len(price_path_df.columns)
        price_path_df.index = price_path_df.index + 1  # shifting index
        price_path_df.sort_index(inplace=True)

        instrument_color = f"rgb({rgb_int()}, {rgb_int()}, {rgb_int()})"
        price_path_df_len = len(price_path_df)

        for column in price_path_df.columns:
            price_path_fig.add_trace(
                go.Scatter(
                    x=list(range(price_path_df_len)),
                    y=price_path_df[column],
                    mode="lines",
                    name=f'{row1["asset"]}_trace{column}',
                    line_color=instrument_color,
                )
            )

    plotting.custom_figure_layout_update(
        price_path_fig,
        x_axis_name="day",
        y_axis_name="price",
        title="Underlying price paths",
        x_tick_format=",d",
        y_tick_format=".1f",
        x_showgrid=False,
        y_showgrid=False,
        yaxis_type="log",
    )

    return price_path_fig


@st.cache(**sc.CACHE_KWARGS)
def create_comparison_df(clustered_instruments, bankroll_df):
    """Clustered instruments with appended instrument, which is portfolio performance"""

    cagr_percentiles = backtest.calculate_percentiles(
        backtest.calculate_cagr, bankroll_df
    )
    drawdown_percentiles = backtest.calculate_percentiles(
        backtest.calculate_max_drawdown, bankroll_df
    )
    backtest_dict = {
        "cluster": -1,
        "asset_label": "Portfolio",
    }
    for i, percentile in enumerate((0, 25, 50, 75, 100)):
        backtest_dict[f"{percentile}_percentile_cagr"] = cagr_percentiles[i]
        backtest_dict[f"{percentile}_percentile_max_drawdown"] = drawdown_percentiles[i]
    comparison_df = clustered_instruments[
        [
            "0_percentile_cagr",
            "25_percentile_cagr",
            "50_percentile_cagr",
            "75_percentile_cagr",
            "100_percentile_cagr",
            "0_percentile_max_drawdown",
            "25_percentile_max_drawdown",
            "50_percentile_max_drawdown",
            "75_percentile_max_drawdown",
            "100_percentile_max_drawdown",
            "cluster",
            "asset_label",
        ]
    ].copy()
    comparison_df = comparison_df.append(backtest_dict, ignore_index=True)

    return comparison_df


@st.cache(**sc.CACHE_KWARGS)
def plot_cagr_percentiles_envelope(
    clustered_instruments, simulation_length_days, number_of_paths
):
    """cagr envelope"""
    cagrs = []
    max_drawdowns = []
    envelope_utils = [i / 10 for i in range(11)]
    percentiles = (0, 25, 50, 75, 100)
    for tmp_util in stqdm(envelope_utils):

        tmp_bankroll_df, _, _ = calculate_bankrolls(
            clustered_instruments,
            simulation_length_days,
            number_of_paths,
            portfolio_util=tmp_util,
        )

        tmp_cagr_percentiles = backtest.calculate_percentiles(
            backtest.calculate_cagr,
            tmp_bankroll_df,
            percentiles=(0, 25, 50, 75, 100),
        )
        tmp_max_drawdown_percentiles = backtest.calculate_percentiles(
            backtest.calculate_max_drawdown,
            tmp_bankroll_df,
            percentiles=(0, 25, 50, 75, 100),
        )

        cagrs.append(tmp_cagr_percentiles)
        max_drawdowns.append(tmp_max_drawdown_percentiles)

    cagrs = np.array(cagrs)
    max_drawdowns = np.array(max_drawdowns)

    envelope_cagr_fig = go.Figure()

    color_dict = {0: "blue", 25: "blue", 50: "blue", 75: "blue", 100: "blue"}
    fill_color = {0: "black", 1: "red", 2: "green", 3: "green", 4: "red"}

    for i, percentile in enumerate(percentiles):
        envelope_cagr_fig.add_trace(
            go.Scatter(
                x=envelope_utils,
                y=cagrs[:, i],
                name=f"p_{percentile}",
                fill="tonexty",
                fillcolor=fill_color[i],
                mode="lines",
                line_color=color_dict[percentile],
            )
        )

    plotting.custom_figure_layout_update(
        envelope_cagr_fig,
        x_axis_name="Util",
        y_axis_name="CAGR",
        title="CAGR percentiles vs Util",
        x_tick_format=".0%",
        y_tick_format=".0%",
        x_showgrid=False,
        y_showgrid=False,
        showlegend=True,
    )

    return envelope_cagr_fig

@st.cache(**sc.CACHE_KWARGS)
def calculate_robustness_tests(
    clustered_instruments,
    simulation_length_days,
    number_of_paths,
    utils_list,
    returns_abs_shifts,
    percentiles=(0, 25, 50, 75, 100),
):
    """calculate cagrs_percentiles_df and max_drawdown_percentiles_df"""

    cagrs_percentiles_df = pd.DataFrame(columns=returns_abs_shifts, index=utils_list)
    max_drawdown_percentiles_df = pd.DataFrame(
        columns=returns_abs_shifts, index=utils_list
    )

    for shift in stqdm(returns_abs_shifts):
        for tmp_util in stqdm(utils_list):
            tmp_bankroll_df, _, _ = calculate_bankrolls(
                clustered_instruments,
                simulation_length_days,
                number_of_paths,
                portfolio_util=tmp_util,
                returns_abs_shift=shift,
            )
            tmp_cagr_percentiles = backtest.calculate_percentiles(
                backtest.calculate_cagr, tmp_bankroll_df, percentiles=percentiles
            )
            tmp_max_drawdown_percentiles = backtest.calculate_percentiles(
                backtest.calculate_max_drawdown,
                tmp_bankroll_df,
                percentiles=percentiles,
            )
            cagrs_percentiles_df.at[tmp_util, shift] = tmp_cagr_percentiles
            max_drawdown_percentiles_df.at[
                tmp_util, shift
            ] = tmp_max_drawdown_percentiles

    return cagrs_percentiles_df, max_drawdown_percentiles_df


@st.cache(**sc.CACHE_KWARGS)
def convert_df_to_csv(some_df):
    """Convert pd.DataFrame to csv string"""
    return some_df.to_csv().encode("utf-8")


#################################################################################################


def portfolio():
    """main function to run, which holds all the app logic"""

    # Initialize settings/texts
    #############################################################################################
    sc.add_cross_app_links_to_sidebar(st.sidebar)
    plotting.graph_settings = sc.add_style_settings_to_sidebar(st.sidebar)
    historical_df = get_historical_prices_df()
    create_introduction()

    # Cached Backtest Results Plot
    #############################################################################################
    cached_expander = st.expander(label="Cached Backtest Results", expanded=True)
    picked_instruments_succesfully = False
    with cached_expander:
        st.markdown(" **Cached Backtest Results** ")
        # get flow2 cached results
        ##########################################################################################
        tmp_cols = st.columns(3)
        input_files = read_dir(hlp.INPUT_DATA_DIR)

        # Load Cached Flow2
        default_flow2_index = input_files.index("backtested_220_samples.csv")
        cached_flow2_filename = tmp_cols[0].selectbox(
            "Select Cached Backtest Results File",
            input_files,
            index=default_flow2_index,
        )
        flow2_cached_results = pd.read_csv(
            os.path.join(hlp.INPUT_DATA_DIR, cached_flow2_filename), sep=","
        )
        if "option_type" not in flow2_cached_results:
            flow2_cached_results["option_type"] = "put"
        ##########################################################################################
        st.write("Filter Instruments by Util, CAGR, Max Drawdown")
        st.write("Pick acceptable Risk and Reward for your Portfolio")
        col1, col2 = st.columns(2)

        min_util_slider = (
            col1.slider(
                "Min Util",
                sc.SLIDER_MIN_UTIL,
                sc.SLIDER_MAX_UTIL,
                0,
                10,
            )
            / 100
        )
        max_util_slider = (
            col2.slider(
                "Max Util",
                sc.SLIDER_MIN_UTIL,
                sc.SLIDER_MAX_UTIL,
                100,
                10,
            )
            / 100
        )

        max_drawdown_pick = (
            col1.slider(
                "Max Drawdown (%)",
                0,
                100,
                DEFAULT_MAX_DRAWDOWN_PICK,
            )
            / 100
        )
        cagr_pick = col2.slider("CAGR (%)", -10, 100, DEFAULT_CAGR_PICK) / 100
        col1, col2, col3 = st.columns(3)

        flow2_hue = col1.selectbox(
            "Select hue", ["strike_pct", "duration", "util", "option_type"]
        )

        cagr_percentile = col2.slider(
            "Select CAGR Percentile as Y Axis", 0, 100, 50, 25
        )

        max_drawdown_percentile = col3.slider(
            "Select Max Drawdown Percentile as X Axis", 0, 100, 50, 25
        )
        x_axis_name = f"{max_drawdown_percentile}_percentile_max_drawdown"
        y_axis_name = f"{cagr_percentile}_percentile_cagr"

        if min_util_slider < max_util_slider:
            filtered_flow2_cached_results = flow2_cached_results[
                (flow2_cached_results["util"] > min_util_slider)
                & (flow2_cached_results["util"] < max_util_slider)
            ]

            fig_flow2_plot_outer = plotting.flow2_plot(
                filtered_flow2_cached_results,
                hue=flow2_hue,
                cagr_pick=cagr_pick,
                max_drawdown_pick=max_drawdown_pick,
                x_axis=x_axis_name,
                y_axis=y_axis_name,
            )

            st.plotly_chart(fig_flow2_plot_outer)

            picked_instruments_outer = filtered_flow2_cached_results[
                (filtered_flow2_cached_results[x_axis_name] < max_drawdown_pick)
                & (filtered_flow2_cached_results[y_axis_name] > cagr_pick)
            ].reset_index(drop=True)
            picked_instruments_outer.drop_duplicates(
                subset=["asset", "strike_pct", "duration"], inplace=True
            )
            st.text("Each point on the graph is performace of one instrument")
            st.text("Use Sliders to pick the Instruments'")

            st.write(f"Picked {len(picked_instruments_outer)} instruments")
            st.dataframe(picked_instruments_outer)
            if len(picked_instruments_outer) > 0:
                picked_instruments_succesfully = True

        else:
            st.write("Error: Please make sure that Min Util < Max Util")
            picked_instruments_succesfully = False

    #############################################################################################
    # Bonding Curves
    #############################################################################################
    st.session_state["bonding_curves_checkbox"] = st.checkbox(
        "Calculate Bonding Curves"
    )

    if picked_instruments_succesfully and st.session_state["bonding_curves_checkbox"]:

        bonding_curve_expander = st.expander(label="Bonding Curves", expanded=True)
        with bonding_curve_expander:

            st.markdown(" **Bonding Curves** ")
            st.session_state["clusterization_premium_relative_threshold"] = (
                st.slider(
                    "Cluster Size (%)",
                    0,
                    100,
                    DEFAULT_CLUSTERIZATION_PREMIUM_RELATIVE_THRESHOLD,
                    10,
                )
                / 100
            )  # number of the random paths to do backtest

            st.text(
                (
                    "That is relative size of the cluster: 100pct "
                    "stands for max 2x premium difference "
                    "inside a cluster. Lesser Cluster size assures "
                    "closer Premiums of the instruments."
                )
            )
            (
                picked_instruments_outer,
                fig_bonding_curves_outer,
            ) = calculate_bonding_curves(
                historical_df,
                picked_instruments_outer,
                st.session_state["clusterization_premium_relative_threshold"],
            )
            largest_cluster_outer, _ = pick_largest_cluster(
                picked_instruments_outer
            )
            st.plotly_chart(fig_bonding_curves_outer)

            clusters_info_df = get_cluster_info(picked_instruments_outer)
            st.write("Clusters Summary")
            st.dataframe(clusters_info_df)

        if len(picked_instruments_outer["cluster"].unique()) > 1:
            st.session_state["cluster_id"] = st.slider(
                "Pick Cluster for the Backtest",
                0,
                picked_instruments_outer["cluster"].max(),
                largest_cluster_outer,
            )
        else:
            st.warning("We have only one cluster")
            st.session_state["cluster_id"] = 0

        st.session_state["clustered_instruments"] = picked_instruments_outer[
            picked_instruments_outer["cluster"] == st.session_state["cluster_id"]
        ]
        st.session_state["clustered_instruments"].reset_index(inplace=True)
        # st.write(f"Number of Instruments in the Cluster: {len(clustered_instruments_outer)}")
        st.write("Instruments for the Backtest:")
        st.write(
            f'Cluster Size: {len(st.session_state["clustered_instruments"])} instruments'
        )
        common_history_df = historical_df[
            st.session_state["clustered_instruments"]["asset"].unique()
        ].dropna()

        st.write(
            (
                f"Common time range for the backtest: ({common_history_df.index.min().date()},"
                f" {common_history_df.index.max().date()})"
            )
        )

        st.dataframe(
            st.session_state["clustered_instruments"][
                ["asset", "option_type", "strike_pct", "duration"]
            ]
        )
        st.download_button(
            "Download Picked Instruments Data",
            convert_df_to_csv(picked_instruments_outer),
            mime="text/csv",
            file_name="picked_instruments.csv",
        )

    else:
        st.warning("Please pick at least one instrument first")
    #############################################################################################
    # Run Simple Backtest
    #############################################################################################
    st.session_state["backtest"] = st.checkbox("Run Backtest")
    if (
        picked_instruments_succesfully
        and st.session_state["bonding_curves_checkbox"]
        and st.session_state["backtest"]
    ):
        backtest_cols = st.columns(3)
        st.session_state["simulation_length_days"] = backtest_cols[0].slider(
            "Simulation Time horizon (days)",
            sc.SLIDER_MIN_DAYS,
            sc.SLIDER_MAX_DAYS,
            100,
        )  # number of option life cycles to use for backtest

        st.session_state["number_of_paths"] = backtest_cols[1].slider(
            "Number of paths (simulation width)",
            sc.SLIDER_MIN_PATHS,
            sc.SLIDER_MAX_PATHS,
            20,
            20,
        )  # number of the random paths to do backtest

        st.session_state["portfolio_util"] = (
            backtest_cols[2].slider(
                "Portfolio Util", 0, 100, DEFAULT_PORTFOLIO_UTIL, 10
            )
            / 100
        )  # number of the random paths to do backtest
        # Bankrolls Plot
        ########################################################################################

        (
            bankroll_df_outer,
            clustered_instruments_outer,
            fig_bankrolls_outer,
        ) = calculate_bankrolls(
            st.session_state["clustered_instruments"],
            st.session_state["simulation_length_days"],
            st.session_state["number_of_paths"],
            portfolio_util=st.session_state["portfolio_util"],
        )
        (
            median_bankroll,
            median_cagr,
            _,
            median_max_drawdown,
            final_bankroll_std,
            median_sharpe_ratio,
            median_ir_ratio,
        ) = calculate_bankroll_df_stats(bankroll_df_outer)
        bankrolls_expander = st.expander(label="Bankrolls", expanded=True)
        with bankrolls_expander:
            st.markdown(" **Bankrolls** ")
            st.plotly_chart(fig_bankrolls_outer)
            st.write("Backtest Performance Stats")
            st.write(f"median_bankroll = {round(median_bankroll, 2)}")
            st.write(f"median_cagr = {round(median_cagr, 2)}")
            st.write(f"median_max_drawdown = {round(median_max_drawdown, 2)}")
            st.write(f"final_bankroll_std = {round(final_bankroll_std, 2)}")
            st.write(f"median_ir_ratio = {round(median_ir_ratio, 2)}")
            st.write(f"median_sharpe_ratio = {round(median_sharpe_ratio, 2)}")
            st.download_button(
                "Download Bankrolls Data",
                convert_df_to_csv(bankroll_df_outer),
                mime="text/csv",
                file_name="bankrolls_df.csv",
            )

        price_path_expander = st.expander(
            label="Underlying Random Price Paths", expanded=True
        )
        with price_path_expander:
            st.markdown(" **Underlying Random Price Paths** ")

            price_path_fig = go.Figure()

            price_path_fig = plot_price_paths(clustered_instruments_outer)

            st.write("Price starts with 1")

            st.plotly_chart(price_path_fig)

        # Portfolio vs Individual Instruments Comparison
        ########################################################################################

        comparison_expander = st.expander(
            label="Portfolio vs Individual Instruments Comparison", expanded=True
        )
        with comparison_expander:

            comparison_df = create_comparison_df(
                st.session_state["clustered_instruments"], bankroll_df_outer
            )

            cols_comparison = st.columns(2)
            cagr_percentile_comparison = cols_comparison[0].slider(
                "Select CAGR Percentile as Y Axis ", 0, 100, 50, 25
            )

            max_drawdown_percentile_comparison = cols_comparison[1].slider(
                "Select Max Drawdown Percentile as X Axis ", 0, 100, 50, 25
            )
            x_axis_name_comparison = (
                f"{max_drawdown_percentile_comparison}_percentile_max_drawdown"
            )
            y_axis_name_comparison = f"{cagr_percentile_comparison}_percentile_cagr"

            fig_flow2_plot_outer = plotting.flow2_plot(
                comparison_df,
                hue="cluster",
                x_axis=x_axis_name_comparison,
                y_axis=y_axis_name_comparison,
            )
            st.plotly_chart(fig_flow2_plot_outer)

    elif (
        not st.session_state["bonding_curves_checkbox"] and st.session_state["backtest"]
    ):
        st.warning("Please calculate Bonding Curves before the Backtest")
    #############################################################################################
    # Tests
    #############################################################################################
    st.session_state["run_tests_checkbox"] = st.checkbox("Run Tests")
    if (
        picked_instruments_succesfully
        and st.session_state["bonding_curves_checkbox"]
        and st.session_state["backtest"]
        and st.session_state["run_tests_checkbox"]
    ):
        # kde of bankrolls vs drawdowns
        ###########################################################################################
        kde_expander = st.expander(label="Bankoll Risk/Reward Graph", expanded=True)
        with kde_expander:

            max_row = st.session_state["clustered_instruments"][
                "50_percentile_cagr"
            ].argmax()

            st.session_state["best_instrument_dict"] = (
                st.session_state["clustered_instruments"]
                .loc[max_row][
                    [
                        "asset",
                        "strike_pct",
                        "duration",
                        "util",
                        "train_start_date",
                        "train_end_date",
                        "mood",
                    ]
                ]
                .to_dict()
            )
            # calculate bankroll for best instrument
            best_instrument_dict = backtest_asset_dict(
                st.session_state["best_instrument_dict"],
                st.session_state["simulation_length_days"],
                historical_df,
                10000,
                BONDING_CURVE_RESOLUTION,
                st.session_state["number_of_paths"],
                premium_offset=0,
                engine="kelly",
                risk_free_rate=0,
            )

            best_instrument_kde_df = create_kde_df(best_instrument_dict["bankroll_df"])
            kde_df = create_kde_df(bankroll_df_outer)

            fig_kde = plot_kdes(
                [kde_df, best_instrument_kde_df],
                ["Portfolio", "Best Instrument"],
            )

            # trick to control size of the Matplotlib plot
            buf = io.BytesIO()
            fig_kde.savefig(buf, format="png")

            st.image(buf)
            # st.pyplot(kde_fig_outer)
            risk_reward_heatmap = px.density_heatmap(
                kde_df,
                x=kde_df["max_drawdown"],
                y=kde_df["cagr"],
                marginal_x="histogram",
                marginal_y="histogram",
                nbinsx=10,
                nbinsy=10,
                # tickformat="%"
            )

            st.plotly_chart(risk_reward_heatmap)

            # envelope chart
            #######################################################################################

            envelope_cagr_fig = plot_cagr_percentiles_envelope(
                st.session_state["clustered_instruments"],
                st.session_state["simulation_length_days"],
                st.session_state["number_of_paths"],
            )
            st.plotly_chart(envelope_cagr_fig)

    elif (
        not st.session_state["bonding_curves_checkbox"]
        and st.session_state["run_tests_checkbox"]
    ):
        st.warning("Please calculate Bonding Curves first")

    elif not st.session_state["backtest"] and st.session_state["run_tests_checkbox"]:
        st.warning("Please run the Backtest first")
    #############################################################################################
    # Robustness Tests
    #############################################################################################
    st.session_state["robust_checkbox"] = st.checkbox("Run Robustness Tests")
    if (
        picked_instruments_succesfully
        and st.session_state["bonding_curves_checkbox"]
        and st.session_state["backtest"]
        and st.session_state["robust_checkbox"]
    ):
        returns_abs_shifts = [-0.1, -0.05, 0.0, 0.05, 0.1]
        utils_list = [round(i / 10, 1) for i in range(11)]
        percentiles = (0, 25, 50, 75, 100)
        cagrs_df = pd.DataFrame(columns=returns_abs_shifts, index=utils_list)
        max_drawdown_df = pd.DataFrame(columns=returns_abs_shifts, index=utils_list)

        cagrs_percentiles_df, max_drawdown_percentiles_df = calculate_robustness_tests(
            st.session_state['clustered_instruments'],
            st.session_state['simulation_length_days'],
            st.session_state['number_of_paths'],
            utils_list,
            returns_abs_shifts,
            percentiles=(0, 25, 50, 75, 100),
        )

        robustness_expander = st.expander(label="Robustness Heatmaps", expanded=True)
        with robustness_expander:
            heatmap_cagr_percentile = st.selectbox(
                "Select CAGR Percentile", percentiles, index=2
            )
            heatmap_cagr_percentile_index = percentiles.index(heatmap_cagr_percentile)

            heatmap_max_drawdown_percentile = st.selectbox(
                "Select Max Drawdown Percentile", percentiles, index=2
            )
            heatmap_max_drawdown_percentile_index = percentiles.index(
                heatmap_max_drawdown_percentile
            )

            for index2 in cagrs_percentiles_df.index:
                for col in cagrs_percentiles_df.columns:
                    cagrs_df.at[index2, col] = cagrs_percentiles_df.at[index2, col][
                        heatmap_cagr_percentile_index
                    ]
                    max_drawdown_df.at[index2, col] = max_drawdown_percentiles_df.at[
                        index2, col
                    ][heatmap_max_drawdown_percentile_index]
            layout = go.Layout(
                title="CARG Robustness",
                xaxis=dict(title="Abs Return Shift"),
                yaxis=dict(title="Util"),
            )
            cagrs_heatmap = go.Heatmap(
                x=cagrs_df.columns,
                y=cagrs_df.index,
                z=cagrs_df,
                type="heatmap",
            )
            fig = go.Figure(data=[cagrs_heatmap], layout=layout)

            st.plotly_chart(fig)

            layout = go.Layout(
                title="Max Drawdown Robustness",
                xaxis=dict(title="Abs Return Shift"),
                yaxis=dict(title="Util"),
            )
            max_drawdown_heatmap = go.Heatmap(
                x=max_drawdown_df.columns,
                y=max_drawdown_df.index,
                z=max_drawdown_df,
                type="heatmap",
            )
            fig = go.Figure(data=[max_drawdown_heatmap], layout=layout)

            st.plotly_chart(fig)

    elif (
        not st.session_state["bonding_curves_checkbox"]
        and st.session_state["robust_checkbox"]
    ):
        st.warning("Please calculate Bonding Curves first")

    elif not st.session_state["backtest"] and st.session_state["robust_checkbox"]:
        st.warning("Please run the Backtest first")


if __name__ == "__main__":

    sc.setup_page_config("MultiAsset portfolio creation/backtest")
    portfolio()
    st.markdown(
        sc.get_footer(
            plotting.graph_settings.text_color, plotting.graph_settings.background_color
        ),
        unsafe_allow_html=True,
    )

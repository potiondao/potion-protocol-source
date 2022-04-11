#!/usr/bin/env python3
"""Script which runs BSM vs Kelly premiums comparison"""
import os

import plotly.graph_objects as go
import plotly.express as px
import spectra
import numpy as np
import pandas as pd
import streamlit as st
import scipy.stats as scs
from scipy import signal
from stqdm import stqdm

import lib.helpers as hlp
import lib.kelly as kelly
import lib.convolution as convolution
import lib.black_scholes as bs
import lib.backtest as backtest
import lib.steamlit_components as sc
import lib.distributions as dst
import lib.random_path_generation as rpg
import lib.plotting as plotting

# @st.cache(suppress_st_warning=True)
backtest_asset_dict = st.cache(
    backtest.backtest_asset_dict,
    show_spinner=False,
    suppress_st_warning=True,
    ttl=3600,
    max_entries=725,
)


def transform_x_axis_name(axis_name):
    """Make a name more expressive"""
    if "_pctl_" in axis_name:
        return axis_name.replace("_pctl_", "_percentile_")
    else:
        return axis_name

@st.cache(**sc.CACHE_KWARGS)
def get_historical_prices_df():
    """Caching wrapper"""
    return hlp.get_historical_prices_df()

@st.cache(show_spinner=False, suppress_st_warning=True, ttl=3600, max_entries=1)
def read_dir(dir_to_read):
    """list dir wrapper"""
    input_files = os.listdir(dir_to_read)
    input_files = [
        input_file for input_file in input_files if "instruments" in input_file
    ]
    return input_files


@st.cache(**sc.CACHE_KWARGS)
def read_instruments_batch(input_filename):
    """Read Instruments from csv"""
    instruments_batch_df = pd.read_csv(
        os.path.join(hlp.INPUT_DATA_DIR, input_filename), sep=","
    )
    return instruments_batch_df


@st.cache(**sc.CACHE_KWARGS, allow_output_mutation=True)
def create_bsm_drawback_figures(
    historical_df,
    simulation_length_days,
    number_of_paths,
    initial_util,
    asset="Bitcoin",
    strike=1,
    duration=1,
    risk_free_interest_rate=0,
    yearly_returns_abs_shift=0.2,
    returns_filter=10,
    static_y_axis=True,
    randomize_util=False,
    option_type="put",
    util_std=0.1,
):
    """create graphs which illustrate bsm difference in perfrormance"""
    n_bins = np.linspace(-1, 5, 1000)
    underlying_price_sequence = historical_df[asset].dropna()
    original_daily_returns_sequence = underlying_price_sequence.pct_change()[1:]
    original_daily_returns_sequence.dropna(inplace=True)
    original_daily_returns_sequence = original_daily_returns_sequence[
        original_daily_returns_sequence != 0
    ]

    # if duration > 1:
    original_returns_sequence = convolution.daily_returns_to_n_day_returns(
        original_daily_returns_sequence, number_of_paths=10000, n_days=duration
    )
    # else:
    #     original_returns_sequence = original_daily_returns_sequence

    # filter returns to skip too high ones
    original_returns_sequence = [
        return_val
        for return_val in original_returns_sequence
        if return_val < returns_filter
    ]
    original_returns_sequence = np.array(original_returns_sequence)
    original_returns_histogram = dst.get_returns_histogram_from_returns_sequence(
        original_daily_returns_sequence, n_bins
    )

    yearly_original_returns_sequence = original_returns_sequence * np.sqrt(
        365 / duration
    )
    yearly_original_returns_sequence = np.array(
        [
            return_val if return_val > -1 else -1
            for return_val in yearly_original_returns_sequence
        ]
    )
    yearly_left_shift_returns_sequence = (
        original_returns_sequence * np.sqrt(365 / duration) - yearly_returns_abs_shift
    )
    yearly_left_shift_returns_sequence = np.array(
        [
            return_val if return_val > -1 else -1
            for return_val in yearly_left_shift_returns_sequence
        ]
    )
    yearly_right_shift_returns_sequence = (
        original_returns_sequence * np.sqrt(365 / duration) + yearly_returns_abs_shift
    )
    yearly_right_shift_returns_sequence = np.array(
        [
            return_val if return_val > -1 else -1
            for return_val in yearly_right_shift_returns_sequence
        ]
    )

    # convert histogram to yearly returns in the meantime
    no_shift_histogram_df = dst.get_returns_histogram_from_returns_sequence(
        yearly_original_returns_sequence, n_bins
    )
    left_shift_histogram_df = dst.get_returns_histogram_from_returns_sequence(
        yearly_left_shift_returns_sequence, n_bins
    )
    right_shift_histogram_df = dst.get_returns_histogram_from_returns_sequence(
        yearly_right_shift_returns_sequence, n_bins
    )

    x_axis_cutoff = left_shift_histogram_df["return"][10]

    convolved_returns_std = dst.calculate_std(no_shift_histogram_df)
    returns_bins = no_shift_histogram_df["return"].to_list()

    fitted_histogram_freq = scs.norm.pdf(returns_bins, 0, convolved_returns_std)

    fitted_histogram_freq = fitted_histogram_freq / sum(fitted_histogram_freq)

    histograms_plot_df = pd.DataFrame()

    # make return yearly
    histograms_plot_df["return"] = no_shift_histogram_df["return"]
    histograms_plot_df["original"] = no_shift_histogram_df["freq"]
    histograms_plot_df["mean_shift_left"] = left_shift_histogram_df["freq"]
    histograms_plot_df["mean_shift_right"] = right_shift_histogram_df["freq"]
    histograms_plot_df.set_index("return", inplace=True)

    if static_y_axis:
        y_axis_cutoff = np.max(original_returns_histogram["freq"].values[10:]) + 0.005
    else:
        y_axis_cutoff = (
            np.max(histograms_plot_df["mean_shift_right"].values[10:]) + 0.005
        )
    fig_shifted_histograms = go.Figure()

    for col in histograms_plot_df.columns:
        fig_shifted_histograms.add_trace(
            go.Scatter(
                x=histograms_plot_df.index,
                y=signal.savgol_filter(histograms_plot_df[col], 9, 1),
                mode="lines",
                name=col,
            )
        )

    fig_shifted_histograms.add_trace(
        go.Scatter(
            x=histograms_plot_df.index,
            y=fitted_histogram_freq,
            mode="lines",
            name="fitted_normal",
            line_dash="dot",
            line_color=plotting.graph_settings.zerolinecolor,
        ),
    )

    plotting.custom_figure_layout_update(
        fig_shifted_histograms,
        x_axis_name="Yearly Return",
        y_axis_name="Probability density",
        title=f"Histogram of {asset} +/- {yearly_returns_abs_shift*100}% yearly mean shift",
        x_tick_format=".1%",
        y_tick_format=".1%",
        xaxis_range=(x_axis_cutoff, 2),
        yaxis_range=(0, y_axis_cutoff / 15),
    )

    if option_type == "put":

        premium = bs.calculate_bs_put_premium(
            original_daily_returns_sequence.std() * np.sqrt(365),
            duration / 365,
            strike_price=strike,
            risk_free_interest_rate=risk_free_interest_rate,
        )
    else:
        premium = bs.calculate_bs_call_premium(
            original_daily_returns_sequence.std() * np.sqrt(365),
            duration / 365,
            strike_price=strike,
            risk_free_interest_rate=risk_free_interest_rate,
        )

    premiums = [premium] * simulation_length_days

    results_df = pd.DataFrame(
        columns=["cagr", "drawdown", "shift"], index=range(number_of_paths * 3)
    )

    cagrs_list = []
    drawdown_list = []
    shift_list = []
    utils = rpg.generate_utils_list(
        simulation_length_days,
        initial_util=initial_util,
        duration=duration,
        randomize=randomize_util,
        util_std=util_std,
    )

    for shift_sign in [-1, 0, 1]:
        random_return_paths_cycles_df = rpg.generate_returns_paths_from_returns(
            original_returns_sequence
            + shift_sign * yearly_returns_abs_shift / np.sqrt(365 / duration),
            number_of_paths,
            simulation_length_days // duration,
            output_as_df=True,
        )

        bankroll_df = backtest.run_backtest(
            random_return_paths_cycles_df,
            utils,
            premiums,
            strike,
            duration,
            option_type,
        )

        for col in bankroll_df:
            cagrs_list.append(
                backtest.calculate_cagr(bankroll_df[col])
                # hlp.convert_bankroll_to_cagr(
                #     bankroll_df[col].values[-1],
                #     years=simulation_length_days / 365,
                #     # begin_bankroll=1 #bankroll_df[col].values[0]
                # )
            )
            drawdown_list.append(backtest.calculate_max_drawdown(bankroll_df[col]))
            shift_list.append(shift_sign * yearly_returns_abs_shift)

    results_df = pd.DataFrame(
        {"cagr": cagrs_list, "drawdown": drawdown_list, "shift": shift_list}
    )

    results_df["shift"] = results_df["shift"].astype(str)

    fig_backtest = px.scatter(
        x=results_df["drawdown"],
        y=results_df["cagr"],
        color=results_df["shift"],
        color_discrete_sequence=["#E85143", "#2C6ADD", "#00CC96"],
    )

    plotting.custom_figure_layout_update(
        fig_backtest,
        x_axis_name="Drawdown",
        y_axis_name="CAGR",
        title="BSM montecarlo backtest for three histograms with equal volatility",
        x_tick_format=".0%",
        y_tick_format=".0%",
        xaxis_range=[0, 1],
    )

    return fig_shifted_histograms, fig_backtest


@st.cache(**sc.CACHE_KWARGS)
def caclulate_single_premium(
    underlying_n_daily_returns,
    util,
    strike,
    premium_offset,
    bonding_curve_resolution=11,
    option_type="put",
):
    """Calculate single kelly premium value"""
    kelly_curve_df = kelly.get_kelly_curve(
        underlying_n_daily_returns,
        strike,
        number_of_utils=bonding_curve_resolution,
        option_type=option_type,
    )
    kelly_curve_df["premium"] *= 1 + premium_offset

    return kelly_curve_df[kelly_curve_df["util"] == util]["premium"].values[0]


@st.cache(**sc.CACHE_KWARGS)
def calculate_premiums_for_strikes(
    underlying_returns_sequence,
    strike_price_linspace,
    duration,
    risk_free_rate=0,
    premium_offset=0,
    spot_price=1,
    convolution_n_paths=1000,
    option_type="put",
):
    """Caching wrapper for loop calculations"""
    # underlying_price_sequence = historical_df[asset]
    # underlying_returns_sequence = underlying_price_sequence.pct_change()[1:]
    # underlying_returns_sequence.dropna(inplace=True)
    yearly_returns_std = underlying_returns_sequence.std() * np.sqrt(365)
    underlying_n_daily_returns = convolution.daily_returns_to_n_day_returns(
        underlying_returns_sequence,
        number_of_paths=convolution_n_paths,
        n_days=duration,
    )

    if option_type == "put":
        black_scholes_premiums_vs_strike_inner = [
            bs.calculate_bs_put_premium(
                yearly_returns_std,
                duration / 365,
                tmp_strike,
                spot_price,
                risk_free_rate,
            )
            for tmp_strike in strike_price_linspace
        ]
    else:
        black_scholes_premiums_vs_strike_inner = [
            bs.calculate_bs_call_premium(
                yearly_returns_std,
                duration / 365,
                tmp_strike,
                spot_price,
                risk_free_rate,
            )
            for tmp_strike in strike_price_linspace
        ]

    kelly_premium_vs_strike_util_0_inner = []
    for tmp_strike in stqdm(strike_price_linspace):
        tmp_premium = caclulate_single_premium(
            underlying_n_daily_returns,
            0,
            tmp_strike,
            premium_offset,
            option_type=option_type,
        )
        kelly_premium_vs_strike_util_0_inner.append(tmp_premium)

    kelly_premium_vs_strike_util_100_inner = []
    for tmp_strike in stqdm(strike_price_linspace):
        tmp_premium = caclulate_single_premium(
            underlying_n_daily_returns,
            1,
            tmp_strike,
            premium_offset,
            option_type=option_type,
        )
        kelly_premium_vs_strike_util_100_inner.append(tmp_premium)

    return (
        black_scholes_premiums_vs_strike_inner,
        kelly_premium_vs_strike_util_0_inner,
        kelly_premium_vs_strike_util_100_inner,
    )


@st.cache(**sc.CACHE_KWARGS)
def calculate_premiums_for_durations(
    underlying_returns_sequence,
    yearly_returns_std,
    duration_linspace,
    strike,
    risk_free_rate=0,
    premium_offset=0,
    convolution_n_paths=1000,
    spot_price=1,
    option_type="put",
):
    """Caching wrapper for loop calculations"""
    if option_type == "put":
        black_scholes_premiums_vs_duration_inner = [
            bs.calculate_bs_put_premium(
                yearly_returns_std,
                tmp_duration / 365,
                strike,
                spot_price,
                risk_free_rate,
            )
            for tmp_duration in duration_linspace
        ]
    else:
        black_scholes_premiums_vs_duration_inner = [
            bs.calculate_bs_call_premium(
                yearly_returns_std,
                tmp_duration / 365,
                strike,
                spot_price,
                risk_free_rate,
            )
            for tmp_duration in duration_linspace
        ]

    kelly_premium_vs_duration_util_0_inner = []
    kelly_premium_vs_duration_util_100_inner = []
    random_returns_paths = pd.DataFrame()

    for tmp_duration in stqdm(duration_linspace):
        additional_random_returns_paths = rpg.generate_returns_paths_from_returns(
            underlying_returns_sequence,
            convolution_n_paths,
            path_length=tmp_duration - len(random_returns_paths),
            output_as_df=True,
        )

        random_returns_paths = random_returns_paths.append(
            additional_random_returns_paths
        )
        underlying_n_daily_returns = (random_returns_paths + 1).prod().values - 1

        premium_0 = caclulate_single_premium(
            underlying_n_daily_returns,
            0,
            strike,
            premium_offset,
            option_type=option_type,
        )
        kelly_premium_vs_duration_util_0_inner.append(premium_0)

        premium_1 = caclulate_single_premium(
            underlying_n_daily_returns,
            1,
            strike,
            premium_offset,
            option_type=option_type,
        )
        kelly_premium_vs_duration_util_100_inner.append(premium_1)

    return (
        black_scholes_premiums_vs_duration_inner,
        kelly_premium_vs_duration_util_0_inner,
        kelly_premium_vs_duration_util_100_inner,
    )


@st.cache(**sc.CACHE_KWARGS)
def calculate_premium_surface(
    returns_sequence,
    underlying_yearly_returns_std,
    duration_linspace,
    strike_price_linspace,
    convolution_n_paths=1000,
    premium_offset=0,
    risk_free_rate=0,
    spot_price=1,
    option_type="put",
):
    """Wrapper to calculate/cache premium surface"""
    kelly_premium_util_0_surface_inner = []
    kelly_premium_util_100_surface_inner = []
    black_scholes_premium_surface_inner = []
    random_returns_paths = pd.DataFrame()
    for tmp_duration in stqdm(duration_linspace):
        additional_random_returns_paths = rpg.generate_returns_paths_from_returns(
            returns_sequence,
            convolution_n_paths,
            path_length=tmp_duration - len(random_returns_paths),
            output_as_df=True,
        )

        random_returns_paths = random_returns_paths.append(
            additional_random_returns_paths
        )
        underlying_n_daily_returns = (random_returns_paths + 1).prod().values - 1
        kelly_premium_vs_strike_util_0 = []
        kelly_premium_vs_strike_util_100 = []
        for tmp_strike in stqdm(strike_price_linspace):

            premium_0 = caclulate_single_premium(
                underlying_n_daily_returns,
                0,
                tmp_strike,
                premium_offset,
                option_type=option_type,
            )
            kelly_premium_vs_strike_util_0.append(premium_0)

            premium_1 = caclulate_single_premium(
                underlying_n_daily_returns,
                1,
                tmp_strike,
                premium_offset,
                option_type=option_type,
            )
            kelly_premium_vs_strike_util_100.append(premium_1)

        if option_type == "put":
            black_scholes_premiums_vs_strike = [
                bs.calculate_bs_put_premium(
                    underlying_yearly_returns_std,
                    tmp_duration / 365,
                    tmp_strike,
                    spot_price,
                    risk_free_rate,
                )
                for tmp_strike in strike_price_linspace
            ]
        else:
            black_scholes_premiums_vs_strike = [
                bs.calculate_bs_call_premium(
                    underlying_yearly_returns_std,
                    tmp_duration / 365,
                    tmp_strike,
                    spot_price,
                    risk_free_rate,
                )
                for tmp_strike in strike_price_linspace
            ]

        black_scholes_premium_surface_inner.append(black_scholes_premiums_vs_strike)
        kelly_premium_util_0_surface_inner.append(hlp.apply_sma(kelly_premium_vs_strike_util_0, 5))
        kelly_premium_util_100_surface_inner.append(
            hlp.apply_sma(kelly_premium_vs_strike_util_100, 5))

    return (
        black_scholes_premium_surface_inner,
        kelly_premium_util_0_surface_inner,
        kelly_premium_util_100_surface_inner,
    )


@st.cache(**sc.CACHE_KWARGS)
def create_comparison_df(backtest_restults_df):
    """Visualize kelly vs black scholes backtest results"""
    comparison_df = pd.DataFrame(
        columns=[
            # "label",
            "mood",
            "bs_sharpe",
            "kelly_sharpe",
            "bs_cagr",
            "kelly_cagr",
            "bs_max_drawdown",
            "kelly_max_drawdown",
        ],
        index=backtest_restults_df["asset_label"].unique(),
    )

    for _, row in backtest_restults_df.iterrows():
        comparison_df.at[row["asset_label"], f'{row["engine"]}_sharpe'] = row[
            "50_percentile_sharpe"
        ]
        comparison_df.at[row["asset_label"], f'{row["engine"]}_cagr'] = row[
            "50_percentile_cagr"
        ]
        comparison_df.at[row["asset_label"], f'{row["engine"]}_max_drawdown'] = row[
            "50_percentile_max_drawdown"
        ]
        comparison_df.at[row["asset_label"], "mood"] = row["mood"]
    # comparison_df["label"] = comparison_df.index
    comparison_df.fillna(0, inplace=True)
    comparison_df = comparison_df.round(decimals=2)

    return comparison_df


def kelly_vs_bs_comparison():
    """main function to run"""
    sc.add_cross_app_links_to_sidebar(st.sidebar)
    st.sidebar.title("Settings")
    st.session_state["randomize_util"] = st.sidebar.checkbox("Randomize Utilization")
    if st.session_state["randomize_util"]:
        st.session_state["util_std"] = (
            st.sidebar.slider(
                "Utilization Sigma", sc.SLIDER_MIN_UTIL, sc.SLIDER_MAX_UTIL, 10
            )
            / 100
        )
    else:
        st.session_state["util_std"] = 0
    st.sidebar.write(
        "If random util is used, then util at the all"
        " X Axes is initial Util used at the backtest"
    )
    plotting.graph_settings = sc.add_style_settings_to_sidebar(st.sidebar)
    # SETTINGS
    ###############################################################################################

    # DEFAULT SETTINGs
    bonding_curve_resolution = (
        11  # number of utils on the [0, 1] segment, passed to the get_kelly_curve
    )
    monte_carlo_paths = 1000
    st.session_state["strike_resolution"] = 10  # c4.slider('Resolution',10,100,10)
    st.session_state["duration_resolution"] = 20  # c4.slider('Resolution ',10,100,10)

    historical_df = get_historical_prices_df()

    # main page settings
    ###############################################################################################

    # HEADER
    st.title("Benchmarking Kelly pricing model vs Black-Scholes pricing model")
    st.header("Abstract")
    st.markdown("Kelly prices vary with utilization.")

    ###############################################################################################
    # Approach
    ###############################################################################################
    approach_expander = st.expander(label="Approach", expanded=True)
    with approach_expander:
        st.markdown(
            """ **Approach**
            We backtest performance of a permanent seller pricing with Black-SCholes,
            vs same permanent seller pricing with Kelly-Criterion
            """
        )

    ###############################################################################################
    # APP LOGIC
    ###############################################################################################
    if st.checkbox("BSM Drawbacks"):
        bsm_drawbacks_expander = st.expander(label="BSM inconcistency", expanded=True)
        with bsm_drawbacks_expander:
            col1_drawbacks, col2_drawbacks = st.columns([1, 4])
            col1_drawbacks.markdown("")
            col1_drawbacks.markdown("")
            col1_drawbacks.markdown("")
            bsm_drawbacks_params = {}
            bsm_drawbacks_params["asset"] = col1_drawbacks.selectbox(
                "Asset", historical_df.columns, 9
            )
            default_duration = 28
            bsm_drawbacks_params["duration"] = col1_drawbacks.slider(
                "Duration (days)",
                sc.SLIDER_MIN_DURATION,
                sc.SLIDER_MAX_DURATION,
                value=default_duration,
            )

            bsm_drawbacks_params["yearly_returns_abs_shift"] = (
                col1_drawbacks.slider("Yearly Returns Shift, %", 0, 100, 100, 1) / 100
            )

            static_y_axis = col1_drawbacks.checkbox("Static Y Axis", value=True)
            col1_drawbacks.markdown("**********")

            bsm_drawbacks_params["option_type"] = col1_drawbacks.selectbox(
                "Option Type", ["put", "call (beta)"]
            )

            bsm_drawbacks_params["strike"] = (
                col1_drawbacks.slider(
                    "Strike (%) ",
                    sc.SLIDER_MIN_STRIKE,
                    sc.SLIDER_MAX_STRIKE,
                    sc.SLIDER_DEFAULT_STRIKE,
                    5,
                )
                / 100
            )

            bsm_drawbacks_params["simulation_length_days"] = col1_drawbacks.slider(
                "Simulation Time horizon (days)",
                sc.SLIDER_MIN_DAYS,
                sc.SLIDER_MAX_DAYS,
                default_duration * 2,
            )  # number of option life cycles to use for backtest

            bsm_drawbacks_params["initial_util"] = (
                col1_drawbacks.slider(
                    "Utilization simulated",
                    sc.SLIDER_MIN_UTIL,
                    sc.SLIDER_MAX_UTIL,
                    sc.SLIDER_DEFAULT_UTIL,
                )
                / 100
            )
            bsm_drawbacks_params["number_of_paths"] = col1_drawbacks.slider(
                "Number of paths (simulation depth)",
                sc.SLIDER_MIN_PATHS,
                sc.SLIDER_MAX_PATHS,
                sc.SLIDER_DEFAULT_PATHS,
                20,
            )  # number of the random paths to do backtest

            bsm_drawbacks_params["risk_free_rate"] = (
                col1_drawbacks.slider("Risk Free rate (% annual)", -100, 100, 0) / 100
            )

            (
                fig_shifted_histograms_outer,
                fig_shifted_backtest,
            ) = create_bsm_drawback_figures(
                historical_df,
                bsm_drawbacks_params["simulation_length_days"],
                bsm_drawbacks_params["number_of_paths"],
                bsm_drawbacks_params["initial_util"],
                asset=bsm_drawbacks_params["asset"],
                strike=bsm_drawbacks_params["strike"],
                duration=bsm_drawbacks_params["duration"],
                risk_free_interest_rate=bsm_drawbacks_params["risk_free_rate"],
                yearly_returns_abs_shift=bsm_drawbacks_params[
                    "yearly_returns_abs_shift"
                ],
                static_y_axis=static_y_axis,
                randomize_util=st.session_state["randomize_util"],
                option_type=bsm_drawbacks_params["option_type"],
                util_std=st.session_state["util_std"],
            )
            col2_drawbacks.plotly_chart(fig_shifted_histograms_outer)
            col2_drawbacks.plotly_chart(fig_shifted_backtest)

    if st.checkbox("Run 1D Premiums comparison"):
        # SWEEP STRIKES

        premium_strike_1d_expander = st.expander(
            label="Premiums Comparison", expanded=True
        )
        with premium_strike_1d_expander:
            col_1d_1, col1d_2 = st.columns([1, 4])
            comparison_1d_params = {}
            comparison_1d_params["asset"] = col_1d_1.selectbox(
                "Asset Name", historical_df.columns, 9
            )
            comparison_1d_params["option_type"] = col_1d_1.selectbox(
                "Option Type   ", ["put", "call (beta)"]
            )
            comparison_1d_params["mood"] = col_1d_1.selectbox(
                "Mood", ["full", "bull", "bear"]
            )
            comparison_1d_params["mood_len"] = col_1d_1.slider(
                "Mood Segment length (days) ", 1, 365, value=28
            )
            comparison_1d_params["duration"] = col_1d_1.slider(
                "Duration (days) ",
                sc.SLIDER_MIN_DURATION,
                sc.SLIDER_MAX2_DURATION,
                value=28,
            )

            comparison_1d_params["strike"] = (
                col_1d_1.slider(
                    "Strike (%)",
                    sc.SLIDER_MIN_STRIKE,
                    sc.SLIDER_MAX_STRIKE,
                    sc.SLIDER_DEFAULT_STRIKE,
                    5,
                )
                / 100
            )

            comparison_1d_params["risk_free_rate"] = (
                col_1d_1.slider("Risk Free rate (% annual) ", 0, 100, 0) / 100
            )
            comparison_1d_params["premium_offset"] = (
                col_1d_1.slider(
                    "Premium Offset",
                    sc.SLIDER_MIN_PREMIUM_OFFSET,
                    sc.SLIDER_MAX_PREMIUM_OFFSET,
                    sc.SLIDER_DEFAULT_PREMIUM_OFFSET,
                )
                / 100
            )
            comparison_1d_params["convolution_n_paths"] = col_1d_1.slider(
                "Generative paths", 100, sc.SLIDER_MAX_PATHS, 100
            )

            comparison_1d_params["duration_range"] = col_1d_1.slider(
                "Duration Range ", 1, 760, value=[1, 365], step=5
            )

            comparison_1d_params["strike_range"] = col_1d_1.slider(
                "Strike Range", 1, 200, value=[75, 125], step=10
            )

            comparison_1d_params["strike_price_linspace"] = np.linspace(
                comparison_1d_params["strike_range"][0] / 100,
                comparison_1d_params["strike_range"][1] / 100,
                st.session_state["strike_resolution"],
            )
            comparison_1d_params["duration_linspace"] = np.linspace(
                comparison_1d_params["duration_range"][0],
                comparison_1d_params["duration_range"][1],
                st.session_state["duration_resolution"],
            ).astype(int)

            comparison_1d_params["underlying_price_sequence"] = historical_df[
                comparison_1d_params["asset"]
            ].dropna()
            start_date, end_date = hlp.get_mood_segment_dates(
                comparison_1d_params["underlying_price_sequence"],
                segment_len_days=comparison_1d_params["mood_len"],
                mood=comparison_1d_params["mood"],
                metric="sharpe",
            )

            comparison_1d_params["underlying_price_sequence"] = comparison_1d_params[
                "underlying_price_sequence"
            ][
                (comparison_1d_params["underlying_price_sequence"].index > start_date)
                & (comparison_1d_params["underlying_price_sequence"].index < end_date)
            ]

            comparison_1d_params["underlying_returns_sequence"] = comparison_1d_params[
                "underlying_price_sequence"
            ].pct_change()[1:]

            comparison_1d_params["underlying_returns_sequence"].dropna(inplace=True)
            comparison_1d_params[
                "underlying_yearly_returns_std"
            ] = comparison_1d_params["underlying_returns_sequence"].std() * np.sqrt(365)

            # Calculate Premiums for the strike_price_linspace
            ########################################################################################
            (
                black_scholes_premiums_vs_strike,
                kelly_premium_vs_strike_util_0,
                kelly_premium_vs_strike_util_100,
            ) = calculate_premiums_for_strikes(
                comparison_1d_params["underlying_returns_sequence"],
                comparison_1d_params["strike_price_linspace"],
                duration=comparison_1d_params["duration"],
                risk_free_rate=comparison_1d_params["risk_free_rate"],
                premium_offset=comparison_1d_params["premium_offset"],
                convolution_n_paths=comparison_1d_params["convolution_n_paths"],
                option_type=comparison_1d_params["option_type"],
            )
            ########################################################################################
            # Plot 1d Premiums comparison for all strikes
            ########################################################################################
            fig_bs_vs_kelly_strike_comparison = px.line()
            fig_bs_vs_kelly_strike_comparison.add_trace(
                go.Scatter(
                    x=comparison_1d_params["strike_price_linspace"],
                    y=black_scholes_premiums_vs_strike,
                    name="BSM",
                    mode="lines",
                    fill=None,
                    line_color="red",
                )
            )
            fig_bs_vs_kelly_strike_comparison.add_trace(
                go.Scatter(
                    x=comparison_1d_params["strike_price_linspace"],
                    y=kelly_premium_vs_strike_util_100,
                    name="Kellu_u100",
                    mode="lines",
                    fill=None,
                    line_color="yellow",
                )
            )
            fig_bs_vs_kelly_strike_comparison.add_trace(
                go.Scatter(
                    x=comparison_1d_params["strike_price_linspace"],
                    y=kelly_premium_vs_strike_util_0,
                    name="Kellu_u0",
                    mode="lines",
                    fill="tonexty",
                    line_color="yellow",
                )
            )

            plotting.custom_figure_layout_update(
                fig_bs_vs_kelly_strike_comparison,
                x_axis_name="Strike",
                y_axis_name="Premium charged",
                title=(
                    f"Optimal BSM and Kelly curves // Asset: {comparison_1d_params['asset']}"
                    f" / Duration: {comparison_1d_params['duration']}"
                ),
                x_tick_format=".0%",
                y_tick_format=".0%",
            )

            col1d_2.plotly_chart(fig_bs_vs_kelly_strike_comparison)

            # Calculate Premiums for the duration_linspace
            ########################################################################################
            (
                black_scholes_premiums_vs_duration,
                kelly_premium_vs_duration_util_0,
                kelly_premium_vs_duration_util_100,
            ) = calculate_premiums_for_durations(
                comparison_1d_params["underlying_returns_sequence"],
                comparison_1d_params["underlying_yearly_returns_std"],
                comparison_1d_params["duration_linspace"],
                strike=comparison_1d_params["strike"],
                risk_free_rate=comparison_1d_params["risk_free_rate"],
                premium_offset=comparison_1d_params["premium_offset"],
                convolution_n_paths=comparison_1d_params["convolution_n_paths"],
                option_type=comparison_1d_params["option_type"],
            )
            ########################################################################################
            # Plot 1d Premiums comparison for all durations
            ########################################################################################
            fig_bs_vs_kelly_duration_comparison = px.line()
            fig_bs_vs_kelly_duration_comparison.add_trace(
                go.Scatter(
                    x=comparison_1d_params["duration_linspace"],
                    y=black_scholes_premiums_vs_duration,
                    name="BSM",
                    mode="lines",
                    fill=None,
                    line_color="red",
                )
            )
            fig_bs_vs_kelly_duration_comparison.add_trace(
                go.Scatter(
                    x=comparison_1d_params["duration_linspace"],
                    y=hlp.apply_sma(kelly_premium_vs_duration_util_100),
                    name="Kellu_u100",
                    mode="lines",
                    fill=None,
                    line_color="yellow",
                )
            )
            fig_bs_vs_kelly_duration_comparison.add_trace(
                go.Scatter(
                    x=comparison_1d_params["duration_linspace"],
                    y=hlp.apply_sma(kelly_premium_vs_duration_util_0),
                    name="Kellu_u0",
                    mode="lines",
                    fill="tonexty",
                    line_color="yellow",
                )
            )

            plotting.custom_figure_layout_update(
                fig_bs_vs_kelly_duration_comparison,
                x_axis_name="Duration",
                y_axis_name="Premium charged",
                title=(
                    f"Optimal BSM and Kelly curves // Asset: "
                    f"{comparison_1d_params['asset']} / Strike: {comparison_1d_params['strike']}"
                ),
                x_tick_format=",d",
                y_tick_format=".0%",
            )

            col1d_2.plotly_chart(fig_bs_vs_kelly_duration_comparison)

    if st.checkbox("Generate Premium vs Strike vs Duration Surface"):
        premium_surface_expander = st.expander(
            label="Premium vs Strike vs Duration Surface Graph", expanded=True
        )
        with premium_surface_expander:
            col_surface_1, col_surface_2 = st.columns([1, 4])
            premium_surface_params = {}

            premium_surface_params["asset"] = col_surface_1.selectbox(
                "Asset  ", historical_df.columns, 9
            )
            premium_surface_params["option_type"] = col_surface_1.selectbox(
                "Option Type    ", ["put", "call (beta)"]
            )
            premium_surface_params["premium_offset"] = (
                col_surface_1.slider(
                    "Premium Offset  ",
                    sc.SLIDER_MIN_PREMIUM_OFFSET,
                    sc.SLIDER_MAX_PREMIUM_OFFSET,
                    sc.SLIDER_DEFAULT_PREMIUM_OFFSET,
                )
                / 100
            )
            premium_surface_params["convolution_n_paths"] = col_surface_1.slider(
                "Generative paths  ", 100, sc.SLIDER_MAX_PATHS, 100
            )
            premium_surface_params["duration_range"] = col_surface_1.slider(
                "Duration Range  ", 1, 760, value=[1, 365], step=5
            )

            premium_surface_params["strike_range"] = col_surface_1.slider(
                "Strike Range ", 1, 200, value=[75, 125], step=10
            )

            premium_surface_params["strike_price_linspace"] = np.linspace(
                premium_surface_params["strike_range"][0] / 100,
                premium_surface_params["strike_range"][1] / 100,
                st.session_state["strike_resolution"],
            )
            premium_surface_params["duration_linspace"] = np.linspace(
                premium_surface_params["duration_range"][0],
                premium_surface_params["duration_range"][1],
                st.session_state["duration_resolution"],
            ).astype(int)

            premium_surface_params["underlying_price_sequence"] = historical_df[
                premium_surface_params["asset"]
            ].dropna()
            premium_surface_params[
                "underlying_returns_sequence"
            ] = premium_surface_params["underlying_price_sequence"].pct_change()[1:]
            premium_surface_params["underlying_returns_sequence"].dropna(inplace=True)
            premium_surface_params[
                "underlying_yearly_returns_std"
            ] = premium_surface_params["underlying_returns_sequence"].std() * np.sqrt(
                365
            )

            # Calculate Premiums for the strike_price_linspace and duration_linspace
            #######################################################################################

            (
                black_scholes_premium_surface,
                kelly_premium_util_0_surface,
                kelly_premium_util_100_surface,
            ) = calculate_premium_surface(
                premium_surface_params["underlying_returns_sequence"],
                premium_surface_params["underlying_yearly_returns_std"],
                premium_surface_params["duration_linspace"],
                premium_surface_params["strike_price_linspace"],
                convolution_n_paths=premium_surface_params["convolution_n_paths"],
                premium_offset=premium_surface_params["premium_offset"],
                option_type=premium_surface_params["option_type"],
            )
            # Plot Premiums for the strike_price_linspace and duration_linspace
            ########################################################################################
            fig_premium_strike_duration_surface = go.Figure()
            fig_premium_strike_duration_surface.add_trace(
                go.Surface(
                    x=premium_surface_params["strike_price_linspace"],
                    y=premium_surface_params["duration_linspace"],
                    z=black_scholes_premium_surface,
                    opacity=0.9,
                    colorscale="Electric"
                    # color='red'
                )
            )
            fig_premium_strike_duration_surface.add_trace(
                go.Surface(
                    x=premium_surface_params["strike_price_linspace"],
                    y=premium_surface_params["duration_linspace"],
                    z=kelly_premium_util_100_surface,
                    opacity=0.9,
                    colorscale="Viridis"
                    # color='yellow'
                )
            )
            fig_premium_strike_duration_surface.add_trace(
                go.Surface(
                    x=premium_surface_params["strike_price_linspace"],
                    y=premium_surface_params["duration_linspace"],
                    z=kelly_premium_util_0_surface,
                    opacity=0.5,
                    colorscale="Blues"
                    # color='yellow'
                )
            )
            fig_premium_strike_duration_surface.update_layout(
                title=(
                    f"Pricing surface Strike/Duration // Asset:"
                    f" {premium_surface_params['asset']}"
                ),
                scene=dict(
                    xaxis_title="Strike",
                    yaxis_title="Duration",
                    zaxis_title="Price",
                    xaxis_visible=True,
                    yaxis_visible=True,
                    zaxis_visible=False,
                    xaxis=dict(
                        backgroundcolor=plotting.graph_settings.background_color,
                        gridcolor=plotting.graph_settings.zerolinecolor,
                        showbackground=True,
                        zerolinecolor=plotting.graph_settings.zerolinecolor,
                    ),
                    yaxis=dict(
                        backgroundcolor=plotting.graph_settings.background_color,
                        gridcolor=plotting.graph_settings.zerolinecolor,
                        showbackground=True,
                        zerolinecolor=plotting.graph_settings.zerolinecolor,
                    ),
                    zaxis=dict(
                        backgroundcolor=plotting.graph_settings.background_color,
                        gridcolor=plotting.graph_settings.zerolinecolor,
                        showbackground=True,
                        zerolinecolor=plotting.graph_settings.zerolinecolor,
                    ),
                ),
            )

            col_surface_2.plotly_chart(fig_premium_strike_duration_surface)

    if st.checkbox("Backtest Multiple Instruments"):
        multiple_instruments_backtest_params = {}
        input_files = read_dir(hlp.INPUT_DATA_DIR)
        default_instruments_batch_index = input_files.index(
            "instruments_multi_mood_72_samples.csv"
        )
        input_filename = st.selectbox(
            "Select instruments range",
            input_files,
            index=default_instruments_batch_index,
        )
        input_df = read_instruments_batch(input_filename)

        assets_info_dicts = input_df.to_dict(orient="records")
        filtered_assets_info_dicts = []
        for asset_dict in assets_info_dicts:
            if isinstance(asset_dict["train_start_date"], str):
                filtered_assets_info_dicts.append(asset_dict)
        assets_info_dicts = filtered_assets_info_dicts
        multiple_instruments_backtest_params["simulation_length_days"] = st.slider(
            "Simulation Time horizon (days)   ",
            sc.SLIDER_MIN_DAYS,
            sc.SLIDER_MAX_DAYS,
            sc.SLIDER_DEFAULT_DAYS,
        )  # number of option life cycles to use for backtest

        multiple_instruments_backtest_params["number_of_paths"] = st.slider(
            "Number of paths (simulation depth)   ",
            sc.SLIDER_MIN_PATHS,
            sc.SLIDER_MAX_PATHS,
            sc.SLIDER_DEFAULT_PATHS,
            20,
        )  # number of the random paths to do backtest
        # LAUNCH OF MULTIPROCESS AND SUMMARY_DF GENERATION
        curves_comparison_expander = st.expander(
            label="Batch Curves Comparison", expanded=True
        )
        with curves_comparison_expander:
            # creates arguments
            ####################################################################################
            multiproc_args_kelly_list = []
            multiproc_args_bs_list = []

            for asset_dict in assets_info_dicts:
                multiproc_args_kelly = [
                    asset_dict.copy(),
                    multiple_instruments_backtest_params["simulation_length_days"],
                    historical_df,
                    monte_carlo_paths,
                    bonding_curve_resolution,
                    multiple_instruments_backtest_params["number_of_paths"],
                    0,
                    "kelly",
                    0,
                    st.session_state["randomize_util"],
                    st.session_state["util_std"],
                ]
                multiproc_args_bs = [
                    asset_dict.copy(),
                    multiple_instruments_backtest_params["simulation_length_days"],
                    historical_df,
                    monte_carlo_paths,
                    bonding_curve_resolution,
                    multiple_instruments_backtest_params["number_of_paths"],
                    0,
                    "bs",
                    0,
                    st.session_state["randomize_util"],
                    st.session_state["util_std"],
                ]

                multiproc_args_kelly_list.append(multiproc_args_kelly)
                multiproc_args_bs_list.append(multiproc_args_bs)

            # backtest kelly
            ####################################################################################
            updated_asset_dicts = []

            for i in stqdm(range(len(multiproc_args_kelly_list))):
                tmp_updated_asset_dict_kelly = backtest_asset_dict(
                    *multiproc_args_kelly_list[i]
                )
                tmp_updated_asset_dict_bs = backtest_asset_dict(
                    *multiproc_args_bs_list[i]
                )
                updated_asset_dicts.append(tmp_updated_asset_dict_kelly)
                updated_asset_dicts.append(tmp_updated_asset_dict_bs)
            # kelly_updated_asset_dicts = multiproc_pool.starmap(
            #     backtest_asset_dict, multiproc_args_kelly_list
            # )
            summary_df = pd.DataFrame(updated_asset_dicts)
            # unpack percentiles to be columns kelly
            ####################################################################################
            max_drawdown_percentile_df = pd.DataFrame(
                summary_df.max_drawdown_percentiles.tolist(),
                index=summary_df.index,
            )
            max_drawdown_percentile_df.rename(
                columns=lambda col: f"{(0, 25, 50, 75, 100)[col]}_percentile_max_drawdown",
                inplace=True,
            )
            cagr_percentile_df = pd.DataFrame(
                summary_df.cagr_percentiles.tolist(), index=summary_df.index
            )
            cagr_percentile_df.rename(
                columns=lambda col: f"{(0, 25, 50, 75, 100)[col]}_percentile_cagr",
                inplace=True,
            )

            sharpe_percentile_df = pd.DataFrame(
                summary_df.sharpe_percentiles.tolist(), index=summary_df.index
            )
            sharpe_percentile_df.rename(
                columns=lambda col: f"{(0, 25, 50, 75, 100)[col]}_percentile_sharpe",
                inplace=True,
            )

            summary_df = summary_df.merge(
                max_drawdown_percentile_df, left_index=True, right_index=True
            )
            summary_df = summary_df.merge(
                cagr_percentile_df, left_index=True, right_index=True
            )
            summary_df = summary_df.merge(
                sharpe_percentile_df, left_index=True, right_index=True
            )

            ####################################################################################
            # plot kelly Bonding Curves vs bs Bonding Curves
            ####################################################################################
            col1, col2 = st.columns(2)
            fig_kelly_bonding_curves = go.Figure()
            fig_bs_bonding_curves = go.Figure()
            for _, row in stqdm(summary_df.iterrows()):
                if row["engine"] == "kelly":
                    fig_kelly_bonding_curves.add_trace(
                        go.Scatter(
                            x=row["premium_vs_util_df"]["util"],
                            y=row["premium_vs_util_df"]["premium"],
                            mode="lines",
                            name=row["asset_label"],
                        )
                    )

            fig_kelly_bonding_curves = plotting.custom_figure_layout_update(
                fig_kelly_bonding_curves,
                x_axis_name="Utilization",
                y_axis_name="Premium charged",
                title="Kelly Optimal pricing curves",
                x_tick_format=".0%",
                y_tick_format=".1%",
                x_showgrid=False,
                y_showgrid=False,
            )

            for _, row in stqdm(summary_df.iterrows()):
                if row["engine"] == "bs":
                    fig_bs_bonding_curves.add_trace(
                        go.Scatter(
                            x=row["premium_vs_util_df"]["util"],
                            y=row["premium_vs_util_df"]["premium"],
                            mode="lines",
                            name=row["asset_label"],
                        )
                    )

            fig_bs_bonding_curves = plotting.custom_figure_layout_update(
                fig_bs_bonding_curves,
                x_axis_name="Utilization",
                y_axis_name="Premium charged",
                title="BSM pricing curves",
                x_tick_format=".0%",
                y_tick_format=".1%",
                x_showgrid=False,
                y_showgrid=False,
            )

            col1.plotly_chart(fig_kelly_bonding_curves)
            col2.plotly_chart(fig_bs_bonding_curves)

        backtest_3d = st.expander(label="Backtest 3D Graph", expanded=True)
        with backtest_3d:
            cols_backtest = st.columns(5)
            dimensions = cols_backtest[0].selectbox(
                "Select View",
                ["2D", "3D"],
            )
            x_axis = cols_backtest[1].selectbox(
                "Select X axis",
                [
                    "100_pctl_max_drawdown",
                    "50_pctl_cagr",
                    "50_pctl_sharpe",
                    "50_pctl_max_drawdown",
                    "strike_pct",
                    "duration",
                    "util",
                ],
            )
            y_axis = cols_backtest[2].selectbox(
                "Select Y axis",
                [
                    "50_pctl_cagr",
                    "50_pctl_sharpe",
                    "50_pctl_max_drawdown",
                    "100_pctl_max_drawdown",
                    "strike_pct",
                    "duration",
                    "util",
                ],
            )
            z_axis = cols_backtest[3].selectbox(
                "Select Z axis",
                [
                    "50_pctl_sharpe",
                    "50_pctl_cagr",
                    "50_pctl_max_drawdown",
                    "100_pctl_max_drawdown",
                    "strike_pct",
                    "duration",
                    "util",
                ],
            )
            show_labels = cols_backtest[4].checkbox("Show Labels")
            x_axis = transform_x_axis_name(x_axis)
            y_axis = transform_x_axis_name(y_axis)
            z_axis = transform_x_axis_name(z_axis)

            if dimensions == "2D":
                summary_df["label"] = (
                    summary_df["asset"]
                    + "_"
                    + summary_df["strike_pct"].astype(str)
                    + "_"
                    + summary_df["duration"].astype(str)
                    + "_"
                    + summary_df["mood"].apply(lambda x: x[0:4])
                )

                summary_df["label"] = (
                    summary_df["label"].str.len().apply(lambda x: " " * (x + 2))
                    + summary_df["label"]
                )

                if show_labels:
                    font_dict = dict(
                        family="Courier New, monospace", size=7, color="#7f7f7f"
                    )
                    show_legend = True
                    fig_scatter = go.Figure()
                    fig_scatter.add_trace(
                        go.Scatter(
                            x=summary_df[summary_df["engine"] == "kelly"][x_axis],
                            y=summary_df[summary_df["engine"] == "kelly"][y_axis],
                            mode="markers+text",
                            text=summary_df[summary_df["engine"] == "kelly"]["label"],
                            line_color="blue",
                            name="Kelly",
                        ),
                    )
                    fig_scatter.add_trace(
                        go.Scatter(
                            x=summary_df[summary_df["engine"] == "bs"][x_axis],
                            y=summary_df[summary_df["engine"] == "bs"][y_axis],
                            mode="markers+text",
                            text=summary_df[summary_df["engine"] == "bs"]["label"],
                            line_color="red",
                            name="Black Scholes",
                        ),
                    )
                else:
                    fig_scatter = px.scatter(
                        summary_df,
                        x=x_axis,
                        y=y_axis,
                        color="engine",
                        symbol="engine",
                    )
                    font_dict = dict()
                    show_legend = True

                fig_scatter = plotting.custom_figure_layout_update(
                    fig_scatter,
                    x_axis_name=x_axis,
                    y_axis_name=y_axis,
                    title="Backtest 2d",
                    x_tick_format=plotting.get_tick_format(x_axis),
                    y_tick_format=plotting.get_tick_format(y_axis),
                    x_showgrid=False,
                    y_showgrid=False,
                    showlegend=show_legend,
                    xaxis_range=plotting.get_range(x_axis),
                    yaxis_range=plotting.get_range(y_axis),
                    font=font_dict,
                )

            elif dimensions == "3D":
                fig_scatter = px.scatter_3d(
                    summary_df,
                    x=summary_df[x_axis],
                    y=summary_df[y_axis],
                    z=summary_df[z_axis],
                    opacity=0.9,
                    color=summary_df["engine"],
                    labels=summary_df["asset_label"],
                )

                fig_scatter.update_layout(
                    title="Backtest 3d",
                    scene=dict(
                        xaxis_title=x_axis,
                        yaxis_title=y_axis,
                        zaxis_title=y_axis,
                        xaxis_visible=True,
                        yaxis_visible=True,
                        zaxis_visible=True,
                        xaxis=dict(
                            backgroundcolor=plotting.graph_settings.background_color,
                            gridcolor=plotting.graph_settings.zerolinecolor,
                            showbackground=True,
                            range=plotting.get_range(x_axis),
                            zerolinecolor="red",
                            tickformat=plotting.get_tick_format(x_axis),
                        ),
                        # autorange="reversed"),
                        yaxis=dict(
                            backgroundcolor=plotting.graph_settings.background_color,
                            gridcolor=plotting.graph_settings.zerolinecolor,
                            showbackground=True,
                            # zerolinecolor="red",
                            # type="log",
                            range=plotting.get_range(y_axis),
                            tickformat=plotting.get_tick_format(y_axis),
                        ),
                        # autorange="reversed"),
                        zaxis=dict(
                            backgroundcolor=plotting.graph_settings.background_color,
                            gridcolor=plotting.graph_settings.zerolinecolor,
                            showbackground=True,
                            zerolinecolor="white",
                            range=plotting.get_range(z_axis),
                            tickformat=plotting.get_tick_format(z_axis),
                        ),
                    ),
                )

            st.header("Backtest Results")

            st.plotly_chart(fig_scatter)
            st.dataframe(
                summary_df.drop(
                    columns=[
                        "price_series",
                        "premium_vs_util_df",
                        "max_drawdown_percentiles",
                        "cagr_percentiles",
                        "bankroll_df",
                    ]
                )
            )

        kelly_vs_bs_table = st.expander(
            label="Kelly vs Black Scholes Table", expanded=True
        )
        with kelly_vs_bs_table:
            colors_list = ["red", plotting.graph_settings.background_color, "green"]
            sharpe_color_scale = spectra.scale(colors_list).domain([-0.5, 0, 0.5])

            def sharpe_color_mapping(value):
                """get color for the sharpe"""
                if value > 0.5:
                    value = 0.5
                elif value < -0.5:
                    value = -0.5
                return f"background-color:{sharpe_color_scale(value).hexcode}"

            cagr_color_scale = spectra.scale(colors_list).domain([-1, 0, 1])

            def cagr_color_mapping(value):
                """get color for the sharpe"""
                if value > 1:
                    value = 1
                elif value < -1:
                    value = -1
                return f"background-color:{cagr_color_scale(value).hexcode}"

            drawdown_color_scale = spectra.scale(
                ["green", plotting.graph_settings.background_color, "red"]
            ).domain([-1, 0, 1])

            def drawdown_color_mapping(value):
                """get color for the sharpe"""
                if value > 1:
                    value = 1
                elif value < -1:
                    value = -1
                return f"background-color:{drawdown_color_scale(value).hexcode}"

            pd.set_option("precision", 2)
            kelly_vs_bs_df = create_comparison_df(summary_df)

            kelly_vs_bs_df_style = (
                kelly_vs_bs_df.style.applymap(
                    sharpe_color_mapping, subset=["bs_sharpe", "kelly_sharpe"]
                )
                .applymap(cagr_color_mapping, subset=["bs_cagr", "kelly_cagr"])
                .applymap(
                    drawdown_color_mapping,
                    subset=["bs_max_drawdown", "kelly_max_drawdown"],
                )
            )
            kelly_vs_bs_df_style = kelly_vs_bs_df_style.format()
            kelly_vs_bs_df_style = kelly_vs_bs_df_style.format(
                {
                    "bs_cagr": "{:,.2%}",
                    "kelly_cagr": "{:,.2%}",
                    "bs_max_drawdown": "{:,.2%}",
                    "kelly_max_drawdown": "{:,.2%}",
                }
            )

            st.dataframe(kelly_vs_bs_df_style)


if __name__ == "__main__":
    sc.setup_page_config(
        "Benchmarking Kelly pricing model vs Black-Scholes pricing model"
    )
    kelly_vs_bs_comparison()
    st.markdown(
        sc.get_footer(
            plotting.graph_settings.text_color, plotting.graph_settings.background_color
        ),
        unsafe_allow_html=True,
    )

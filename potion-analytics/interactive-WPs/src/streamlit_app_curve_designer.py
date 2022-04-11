#!/usr/bin/env python3
"""Script which calculate curves/runs backtest for a single instrument
with an option to adjust
the bonding curve according to users personal needs"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from stqdm import stqdm
from scipy import signal

import lib.kelly as kelly
import lib.convolution as convolution
import lib.backtest as backtest
import lib.helpers as hlp
import lib.random_path_generation as rpg
import lib.distributions as dst
import lib.plotting as plotting
import lib.steamlit_components as sc


# DEFAULT SIDEBAR SETTINGS
DEFAULT_DURATION = 7
DEFAULT_SIMULATION_HORIZON = 100
DEFAULT_SIMULATION_UTILIZATION = 50
DEFAULT_STRIKE = 100
DEFAULT_CONVOLUTION_PATHS = 1000
DEFAULT_BACKTEST_PATHS = 20
# number of utils on the [0, 1] segment, passed to the get_kelly_curve
DEFAULT_BONDING_CURVE_RESOLUTION = 30

# Whatever complies with np.histogram
MOODS = ["full", "bear", "bull"]
mood_color_map = {"full": "#cab414", "bear": "red", "bull": "green"}


@st.cache(**sc.CACHE_KWARGS)
def get_historical_prices_df():
    """Caching wrapper"""
    return hlp.get_historical_prices_df()


@st.cache(**sc.CACHE_KWARGS)
def calculate_price_segments(price_sequence, mood_window, monte_carlo_paths, duration):
    "Calculate Bonding Curves for each mood in a loop"
    instrument_info_dicts = []
    # returns_bins = np.linspace(-1, 3)
    returns_bins = []
    for mood in stqdm(MOODS):
        tmp_instrument_dict = {}
        tmp_instrument_dict["mood"] = mood
        tmp_instrument_dict["price_df"] = hlp.get_price_for_mood_segment(
            price_sequence,
            segment_len_days=mood_window,
            mood=mood,
        )
        # handle cases of absence of mood segments
        if tmp_instrument_dict["price_df"].empty:
            return []
        tmp_instrument_dict["returns_sequence"] = tmp_instrument_dict["price_df"][
            "price"
        ].pct_change()[1:]

        tmp_instrument_dict[
            "underlying_n_daily_returns"
        ] = convolution.daily_returns_to_n_day_returns(
            tmp_instrument_dict["returns_sequence"],
            number_of_paths=monte_carlo_paths,
            n_days=duration,
        )
        # we have that only for illustrational purposes
        if len(returns_bins) > 0:

            tmp_instrument_dict[
                "convolved_returns_histogram"
            ] = dst.get_returns_histogram_from_returns_sequence(
                tmp_instrument_dict["underlying_n_daily_returns"], returns_bins
            )
        else:
            tmp_instrument_dict[
                "convolved_returns_histogram"
            ] = dst.get_returns_histogram_from_returns_sequence(
                tmp_instrument_dict["underlying_n_daily_returns"]
            )
            returns_bins = tmp_instrument_dict["convolved_returns_histogram"][
                "return"
            ].values

        instrument_info_dicts.append(tmp_instrument_dict)
    return instrument_info_dicts


@st.cache(**sc.CACHE_KWARGS)
def calculate_bonding_curves(
    price_sequence, mood_window, monte_carlo_paths, duration, strike, option_type="put"
):
    "Calculate Bonding Curves for each mood in a loop"
    instrument_info_dicts = []
    for mood in stqdm(MOODS):
        tmp_instrument_dict = {}
        tmp_instrument_dict["mood"] = mood
        tmp_instrument_dict["price_df"] = hlp.get_price_for_mood_segment(
            price_sequence,
            segment_len_days=mood_window,
            mood=mood,
        )
        tmp_instrument_dict["returns_sequence"] = tmp_instrument_dict["price_df"][
            "price"
        ].pct_change()[1:]

        tmp_instrument_dict[
            "underlying_n_daily_returns"
        ] = convolution.daily_returns_to_n_day_returns(
            tmp_instrument_dict["returns_sequence"],
            number_of_paths=monte_carlo_paths,
            n_days=duration,
        )

        tmp_instrument_dict["kelly_curve_df"] = kelly.get_kelly_curve(
            tmp_instrument_dict["underlying_n_daily_returns"],
            strike,
            number_of_utils=DEFAULT_BONDING_CURVE_RESOLUTION,
            option_type=option_type,
        )
        tmp_instrument_dict["fit_params"] = kelly.fit_curve_parameters(
            tmp_instrument_dict["kelly_curve_df"]["util"],
            tmp_instrument_dict["kelly_curve_df"]["premium"],
        )

        instrument_info_dicts.append(tmp_instrument_dict)
    return instrument_info_dicts


# @st.cache(**sc.CACHE_KWARGS)
def add_custom_curve_to_the_fig(curves_fig, param_a, param_b, param_c, param_d):
    """Add curve to the plot"""
    util_space = np.linspace(0, 1, 100)
    custom_curve = (
        param_a * util_space * np.cosh(param_b * util_space ** param_c) + param_d
    )
    curves_fig.add_trace(
        go.Scatter(
            x=util_space,
            y=custom_curve,
            mode="lines",
            name="Bespoke curve",
            line=dict(
                dash="dash", width=2, color=plotting.graph_settings.zerolinecolor
            ),
        )
    )
    return curves_fig


@st.cache(**sc.CACHE_KWARGS)
def plot_price_segments(instrument_info_dicts, asset, mood_window):
    """Create all training params"""
    fig_mood_price_path = go.Figure()
    if len(instrument_info_dicts) == 0:
        st.error(
            f"Failed to find mood segment for {asset} of "
            f"len {mood_window} days."
            f" Please try smaller mood_window or another asset"
        )

    else:

        for instrument_dict in instrument_info_dicts:
            fig_mood_price_path.add_trace(
                go.Scatter(
                    x=instrument_dict["price_df"].index,
                    y=instrument_dict["price_df"]["price"],
                    # mode="lines",
                    name=instrument_dict["mood"],
                    line_color=mood_color_map[instrument_dict["mood"]],
                )
            )
        fig_mood_price_path = plotting.custom_figure_layout_update(
            fig_mood_price_path,
            "Date",
            "Price",
            f"Training segments for {asset}",
            y_tick_format="$,.0f",
            x_tick_format="%d/%m/%Y",
            yaxis_type="log",
        )
    return fig_mood_price_path


@st.cache(**sc.CACHE_KWARGS)
def plot_histograms(instrument_info_dicts, strike, premium, option_type):
    """Create all training params"""
    fig_histograms = make_subplots(specs=[[{"secondary_y": True}]])
    for instrument_dict in instrument_info_dicts:
        fig_histograms.add_trace(
            go.Scatter(
                x=instrument_dict["convolved_returns_histogram"]["return"],
                y=instrument_dict["convolved_returns_histogram"]["freq"],
                mode="lines",
                name=instrument_dict["mood"],
                line_color=mood_color_map[instrument_dict["mood"]],
            ),
            secondary_y=False,
        )
    if option_type == "put":
        payouts_list = [
            kelly.put_option_payout(
                tmp_return,
                strike,
                premium,
            )
            for tmp_return in np.linspace(-1, 1, 200)
        ]
    else:
        payouts_list = [
            kelly.call_option_payout(
                tmp_return,
                strike,
                premium,
            )
            for tmp_return in np.linspace(-1, 1, 200)
        ]

    fig_histograms.add_trace(
        go.Scatter(
            x=np.linspace(-1, 1, 200),
            y=payouts_list,
            mode="lines",
            name="Put Option Payout",
            line_color=plotting.graph_settings.zerolinecolor,
        ),
        secondary_y=True,
    )
    fig_histograms.add_trace(
        go.Scatter(
            x=np.linspace(-1, 1, 200),
            y=[0] * len(payouts_list),
            mode="lines",
            name="Zero Payout line",
            line=dict(
                dash="dash", width=2, color=plotting.graph_settings.zerolinecolor
            ),
        ),
        secondary_y=True,
    )

    fig_histograms = plotting.custom_figure_layout_update(
        fig_histograms,
        x_axis_name="Return",
        y_axis_name="Observed Frequency",
        title="Histogram of returns in training segments",
        x_tick_format="%,.0f",
        y_tick_format=".2f",
        xaxis_range=[-1, 2],
    )

    return fig_histograms


@st.cache(**sc.CACHE_KWARGS)
def plot_bonding_curves(instrument_info_dicts, param_a, param_b, param_c, param_d):
    """Create all training params"""
    # Kelly curves for each mood
    fig_kelly_curves = go.Figure()
    for instrument_dict in instrument_info_dicts:
        # Convolved PDF for each mood
        fig_kelly_curves.add_trace(
            go.Scatter(
                x=instrument_dict["kelly_curve_df"]["util"],
                y=instrument_dict["kelly_curve_df"]["premium"],
                # mode="lines",
                name=instrument_dict["mood"],
                marker=dict(color=mood_color_map[instrument_dict["mood"]]),
            ),
            # line=dict()
        )

    fig_kelly_curves = plotting.custom_figure_layout_update(
        fig_kelly_curves,
        x_axis_name="Utilization",
        y_axis_name="Premium (%)",
        title="KELLY CURVES / Custom vs Optimal",
        x_tick_format="%,.0f",
        y_tick_format="%,.1f",
    )

    fig_kelly_curves = add_custom_curve_to_the_fig(
        fig_kelly_curves,
        param_a,
        param_b,
        param_c,
        param_d,
    )

    return fig_kelly_curves


# @st.experimental_singleton(**sc.CACHE_SINGLETON_KWARGS)
# @st.cache(**sc.CACHE_KWARGS)
@st.cache(**sc.CACHE_KWARGS, allow_output_mutation=True)
def plot_backtest(
    instrument_info_dicts,
    duration,
    strike,
    option_type,
    bonding_curve_resolution,
    monte_carlo_paths,
    simulation_length_days,
    randomize_util=False,
    util_std=0,
    param_a=0,
    param_b=0,
    param_c=0,
    param_d=0,
):
    """Backtest and plot instruments"""
    bull_max = []
    bull_min = []
    bear_max = []
    bear_min = []
    full_max = []
    full_min = []

    drawdown_bull_max = []
    drawdown_bull_min = []
    drawdown_bear_max = []
    drawdown_bear_min = []
    drawdown_full_max = []
    drawdown_full_min = []

    for instrument_dict in instrument_info_dicts:
        underlying_n_daily_returns = instrument_dict["underlying_n_daily_returns"]
        random_return_paths_cycles_df = rpg.generate_returns_paths_from_returns(
            underlying_n_daily_returns,
            monte_carlo_paths,
            simulation_length_days // duration,
            output_as_df=True,
        )
        for util in instrument_dict["kelly_curve_df"]["util"]:

            premium = (
                param_a * util * np.cosh(param_b * (util ** param_c)) + param_d
            )  # instrument_dict["kelly_curve_df"]["premium"][j]

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
                [premium] * len(utils),  # ||||||||||||
                strike,
                duration,
                option_type=option_type,
            )

            cagrs = [
                hlp.convert_bankroll_to_cagr(final_br, simulation_length_days / 365)
                for final_br in bankroll_df.iloc[-1].tolist()
            ]
            drawdowns = [
                backtest.calculate_max_drawdown(bankroll_df[col]) for col in bankroll_df
            ]

            # st.plotly_chart(px.line(cagrs))

            if instrument_dict["mood"] == "bull":
                bull_max.append(np.percentile(cagrs, percentile))
                bull_min.append(np.percentile(cagrs, 100 - percentile))
                drawdown_bull_max.append(np.percentile(drawdowns, percentile))
                drawdown_bull_min.append(np.percentile(drawdowns, 100 - percentile))
            elif instrument_dict["mood"] == "bear":
                bear_max.append(np.percentile(cagrs, percentile))
                bear_min.append(np.percentile(cagrs, 100 - percentile))
                drawdown_bear_max.append(np.percentile(drawdowns, percentile))
                drawdown_bear_min.append(np.percentile(drawdowns, 100 - percentile))
            elif instrument_dict["mood"] == "full":
                full_max.append(np.percentile(cagrs, percentile))
                full_min.append(np.percentile(cagrs, 100 - percentile))
                drawdown_full_max.append(np.percentile(drawdowns, percentile))
                drawdown_full_min.append(np.percentile(drawdowns, 100 - percentile))

    util_bins = np.linspace(0, 1, bonding_curve_resolution)

    fig_envelope_backtest = go.Figure()
    fig_drawdown_envelope_backtest = go.Figure()
    sigmals = [bear_max, bear_min, full_max, full_min, bull_max, bull_min]
    drawdown_sigmals = [
        drawdown_bear_max,
        drawdown_bear_min,
        drawdown_full_max,
        drawdown_full_min,
        drawdown_bull_max,
        drawdown_bull_min,
    ]
    names = [
        "Bear_max",
        "Bear_min",
        "Full_max",
        "Full_min",
        "Bull_max",
        "Bull_min",
    ]
    fills = [None, "tonexty", None, "tonexty", None, "tonexty"]
    line_colors = ["red", "red", "yellow", "yellow", "green", "green"]

    for cagr_list, drawdown_list, name, fill, line_color in zip(
        sigmals, drawdown_sigmals, names, fills, line_colors
    ):
        cagr_list_first_elem = cagr_list[0]
        cagr_list = signal.savgol_filter(cagr_list, 5, 4)
        cagr_list[0] = cagr_list_first_elem

        drawdowns_list_first_elem = drawdown_list[0]
        drawdown_list = signal.savgol_filter(drawdown_list, 5, 4)
        drawdown_list[0] = drawdowns_list_first_elem
        # cagr_list = rpg.simple_moving_average(cagr_list, 3)
        # drawdown_list = rpg.simple_moving_average(drawdown_list, 3)

        fig_envelope_backtest.add_trace(
            go.Scatter(
                x=util_bins,
                y=cagr_list,
                name=name,
                fill=fill,
                mode="lines",
                line_color=line_color,
            )
        )

        fig_drawdown_envelope_backtest.add_trace(
            go.Scatter(
                x=util_bins,
                y=drawdown_list,
                name=name,
                fill=fill,
                mode="lines",
                line_color=line_color,
            )
        )

    fig_envelope_backtest = plotting.custom_figure_layout_update(
        fig_envelope_backtest,
        x_axis_name="Utilization",
        y_axis_name="CAGR (%)",
        title="CAGRs Envelope",
        x_tick_format=".0%",
        y_tick_format=".0%",
        yaxis_range=[-1, 1],
    )

    fig_drawdown_envelope_backtest = plotting.custom_figure_layout_update(
        fig_drawdown_envelope_backtest,
        x_axis_name="Utilization",
        y_axis_name="Drawdown (%)",
        title="Drawdowns Envelope",
        x_tick_format=".0%",
        y_tick_format=".0%",
        yaxis_range=[0, 1],
    )
    return fig_envelope_backtest, fig_drawdown_envelope_backtest


sc.setup_page_config("Curve Designer")

st.title("Custom Kelly Curve Maker")
st.markdown("")
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
instrument_info_dicts_outer = []
instrument_info_dicts1 = []

st.subheader("Step 1. Select Input Information")
if st.checkbox("Set up training parameters"):
    with st.expander("Training Data", expanded=True):
        col1, col2 = st.columns((1, 4))
        col1.caption("Training data settings")

        historical_df = get_historical_prices_df()
        asset_outer = col1.selectbox("Protected asset", historical_df.columns[:])

        mood_window_outer = col1.slider(
            "Mood length (days)",
            30,
            365,
            100,
            step=30,
        )

        price_sequence_outer = historical_df[asset_outer].dropna()

        # Insurance Settings
        col1.markdown("-" * 100)

        col1.caption("Product Settings")
        option_type_outer = col1.selectbox("Option Type", ["put", "call (beta)"])
        strike_outer = (
            col1.slider(
                "Insurance level (%)",
                sc.SLIDER_MIN_STRIKE,
                sc.SLIDER_MAX_STRIKE,
                sc.SLIDER_DEFAULT_STRIKE,
                1,
            )
            / 100
        )  # 1.1 = 10% in the money

        premium_outer = (
            col1.slider(
                "Premium Charged (%)",
                sc.SLIDER_MIN_PREMIUM_OFFSET,
                sc.SLIDER_MAX_PREMIUM_OFFSET,
                10,
                1,
            )
            / 100
        )  #
        duration_outer = col1.slider(
            "Insurance Duration (days)",
            sc.SLIDER_MIN_DURATION,
            sc.SLIDER_MAX_DURATION,
            sc.SLIDER_DEFAULT_DURATION,
        )

        instrument_info_dicts1 = calculate_price_segments(
            price_sequence_outer,
            mood_window_outer,
            DEFAULT_CONVOLUTION_PATHS,
            duration_outer,
        )

        fig_mood_price_path_outer = plot_price_segments(
            instrument_info_dicts1, asset_outer, mood_window_outer
        )
        fig_histograms_outer = plot_histograms(
            instrument_info_dicts1, strike_outer, premium_outer, option_type_outer
        )

        col2.plotly_chart(fig_mood_price_path_outer, use_container_width=True)
        col2.plotly_chart(fig_histograms_outer, use_container_width=True)


st.subheader("Step 2. Compute the bonding curves")
bonding_curves_checkbox = st.checkbox("Calculate Bonding Curves")
if bonding_curves_checkbox and len(instrument_info_dicts1) != 0:
    with st.expander("Bonding Curves", expanded=True):
        st.write("")
        instrument_info_dicts_outer = calculate_bonding_curves(
            price_sequence_outer,
            mood_window_outer,
            DEFAULT_CONVOLUTION_PATHS,
            duration_outer,
            strike_outer,
            option_type=option_type_outer,
        )

        col1, col2 = st.columns((1, 3))
        curve_choice = col1.radio(
            "Select Premiums Curve",
            ["full", "bear", "bull", "0.5 * bear + 0.5 * bull", "custom"],
            index=0,
        )
        if "0.5" in curve_choice:
            for instrument_dict_outer in instrument_info_dicts_outer:
                if instrument_dict_outer["mood"] == "bear":
                    bear_df = instrument_dict_outer["kelly_curve_df"]
                elif instrument_dict_outer["mood"] == "bull":
                    bull_df = instrument_dict_outer["kelly_curve_df"]
            mean_premium_df = bear_df.copy()
            mean_premium_df["premium"] += bull_df["premium"]
            mean_premium_df["premium"] /= 2
            (
                curve_param_a,
                curve_param_b,
                curve_param_c,
                curve_param_d,
            ) = kelly.fit_curve_parameters(
                mean_premium_df["util"].values, mean_premium_df["premium"].values
            )

        elif curve_choice not in MOODS:
            curve_param_a = col1.slider(
                "A", value=0.0, min_value=0.0, max_value=1.0, step=0.001, format="%.4f"
            )
            curve_param_b = col1.slider(
                "B", value=0.0, min_value=0.0, max_value=5.0, step=0.001, format="%.4f"
            )
            curve_param_c = col1.slider(
                "C", value=0.0, min_value=0.0, max_value=10.0, step=0.001, format="%.4f"
            )
            curve_param_d = col1.slider(
                "D", value=0.0, min_value=0.0, max_value=0.5, step=0.001, format="%.4f"
            )
        else:
            for instrument_dict_outer in instrument_info_dicts_outer:
                if instrument_dict_outer["mood"] == curve_choice:
                    (
                        curve_param_a,
                        curve_param_b,
                        curve_param_c,
                        curve_param_d,
                    ) = instrument_dict_outer["fit_params"]
            col1.write("a")
            col1.write(round(curve_param_a, 4))
            col1.write("b")
            col1.write(round(curve_param_b, 4))
            col1.write("c")
            col1.write(round(curve_param_c, 4))
            col1.write("d")
            col1.write(round(curve_param_d, 4))
            st.write("Select 'custom' Premium Curve if you want to set curve manually.")

        fig_bonding_curves = plot_bonding_curves(
            instrument_info_dicts_outer,
            curve_param_a,
            curve_param_b,
            curve_param_c,
            curve_param_d,
        )

        col2.plotly_chart(
            fig_bonding_curves,
            use_container_width=True,
        )

elif bonding_curves_checkbox:
    st.warning("Please set up training parameters first")

st.markdown("")
st.markdown("")
st.header("Step 3: Montecarlo Simulation")
if st.checkbox("Run Montecarlo") and len(instrument_info_dicts_outer) != 0:
    if "kelly_curve_df" in instrument_info_dicts_outer[0]:
        with st.expander("Backtest The Bonding Curve", expanded=True):
            col1, col2 = st.columns((1, 4))
            percentile = col1.slider("Interval of confidence", 50, 100, 80, step=5)
            monte_carlo_paths_outer = col1.slider(
                "Backtest Paths", sc.SLIDER_MIN_PATHS, sc.SLIDER_MAX_PATHS, 20, 25
            )
            simulation_length_days_outer = col1.slider(
                "Simulation horizon (days)",
                sc.SLIDER_MIN_DAYS,
                sc.SLIDER_MAX_DAYS,
                step=30,
            )

            (
                fig_envelope_backtest_outer,
                fig_drawdown_envelope_backtest_outer,
            ) = plot_backtest(
                instrument_info_dicts_outer,
                duration_outer,
                strike_outer,
                option_type_outer,
                DEFAULT_BONDING_CURVE_RESOLUTION,
                monte_carlo_paths_outer,
                simulation_length_days_outer,
                randomize_util=st.session_state["randomize_util"],
                util_std=st.session_state["util_std"],
                param_a=curve_param_a,
                param_b=curve_param_b,
                param_c=curve_param_c,
                param_d=curve_param_d,
            )
            col2.plotly_chart(fig_envelope_backtest_outer)
            col2.plotly_chart(fig_drawdown_envelope_backtest_outer)
    else:
        st.warning("Please Calculate the Bonding Curves first")

st.markdown(
    sc.get_footer(
        plotting.graph_settings.text_color, plotting.graph_settings.background_color
    ),
    unsafe_allow_html=True,
)

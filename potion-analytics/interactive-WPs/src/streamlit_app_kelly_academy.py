#!/usr/bin/env python3
"""Script which runs flow1 with an option to adjust
the bonding curve according to users personal needs"""

import pandas as pd
import streamlit as st
import plotly.express as px

import numpy as np
from lib import backtest

import lib.plotting as plotting
import lib.steamlit_components as sc
import lib.helpers as hlp


@st.cache(**sc.CACHE_KWARGS)
def get_gain_vs_bet_size(bet_win_rate, n_bets, resolution_bet_size=50):
    """Calculate gain_vs_bet_df"""
    bet_size_array = np.arange(
        0.0, 1.0 + 1 / resolution_bet_size, 1 / resolution_bet_size
    )  # np.array([i/resolution_f for i in range(resolution_f+1)])

    gain_vs_bet_df = pd.DataFrame({"Bet Fraction": bet_size_array})

    exp_values = []

    for bet_size in np.arange(
        0.0, 1.0 + 1 / resolution_bet_size, 1 / resolution_bet_size
    ):
        geometric_growth_rate = ((1 + bet_size) ** bet_win_rate) * (
            (1 - bet_size) ** (1 - bet_win_rate)
        ) - 1
        expected_gain = (1 + geometric_growth_rate) ** n_bets
        exp_values.append(expected_gain)

    gain_vs_bet_df["Terminal Capital"] = exp_values

    gain_vs_bet_df["CAGR"] = gain_vs_bet_df["Terminal Capital"].map(
        lambda x: hlp.convert_bankroll_to_cagr(x, n_bets / 365)
    )

    return gain_vs_bet_df


@st.cache(**sc.CACHE_KWARGS)
def calculate_capital_paths(bet_win_rate, n_bets, monte_carlo_paths, bet_size):
    """Calculate gain_vs_bet_df"""
    rnd_seed = np.random.rand(n_bets, monte_carlo_paths)

    for i in range(n_bets):
        rnd_seed[[i]] = np.where(
            rnd_seed[[i]] <= bet_win_rate, 1 + bet_size, 1 - bet_size
        )

    rnd_seed = np.concatenate((np.full((1, monte_carlo_paths), 1), rnd_seed))

    for i in range(n_bets + 1):
        if i != 0:
            rnd_seed[i] = rnd_seed[i - 1] * (rnd_seed[i])

    capital_paths_df = pd.DataFrame(rnd_seed)

    return capital_paths_df


def cointoss():
    """Bankroll Calculation for the biased Coin Toss"""
    with st.container():
        st.header("Kelly Basics: Coin toss")
        st.write("")
        st.info(
            """Someone offers you to bet on a biased coin toss.
               How much of your bankroll should bet?
               You double when you win, lose everything when you lose."""
        )

        col1, col2 = st.columns(2)

        col1.subheader("Settings")
        # WIN RATE SLIDER
        bet_win_rate = (
            col1.slider(
                "Toss win_rate (%)",
                min_value=0,
                max_value=100,
                value=60,
                help="How many times you win per every 100 trials",
            )
            / 100
        )

        # ITERATIONS SLIDERS
        n_bets = col1.slider(
            "Number of bets",
            min_value=sc.SLIDER_MIN_DAYS,
            max_value=sc.SLIDER_MAX_DAYS,
            value=30,
            help="Number of consecutive bets",
        )

        # log_scale1 = col1.radio("Log Scale ", [False, True])
        log_scale1 = False

        # y_axis = col1.radio("Y Axis", ["Terminal Capital", "CAGR"])
        y_axis = "Terminal Capital"

        resolution_bet_size = 50

        gain_vs_bet_df = get_gain_vs_bet_size(
            bet_win_rate, n_bets, resolution_bet_size=resolution_bet_size
        )
        # range_y_axis = (gain_vs_bet_df[y_axis].min(), gain_vs_bet_df[y_axis].max())
        if y_axis == "CAGR":
            baseline_y = 0
            # yaxis_range = (-1, abs(range_y_axis[1]))
        else:
            baseline_y = 1
            # yaxis_range = None

        gain_vs_bet_chart = px.line(
            gain_vs_bet_df,
            x="Bet Fraction",
            y=y_axis,
            log_y=log_scale1,
        )

        gain_vs_bet_chart = plotting.custom_figure_layout_update(
            gain_vs_bet_chart,
            x_axis_name="Bet Size (% of Capital)",
            y_axis_name=f"Expected {y_axis}",
            title=f"{y_axis} for each Bet Size",
            x_tick_format=".0%",
            y_tick_format=".1%",
            x_showgrid=True,
            y_showgrid=True,
            # yaxis_range=yaxis_range,
        )

        gain_vs_bet_chart.add_hline(
            y=baseline_y,
            line_dash="dash",
            line_color=plotting.graph_settings.zerolinecolor,
        )

        max_exp = (
            gain_vs_bet_df["Terminal Capital"].idxmax() / resolution_bet_size * 100
        )

        # CHART LEFT
        col1.subheader("Expected Growth")
        col1.write("Optimal bet fraction: {:.1%}".format(max_exp / 100))
        col1.plotly_chart(
            gain_vs_bet_chart,
            use_container_width=True,
        )

        # CHART RIGHT
        col2.subheader("Simulation")

        # NUMBER OF SIMULATIONS SLIDERS
        monte_carlo_paths = col2.slider(
            "Number of simulation paths: ",
            min_value=sc.SLIDER_MIN_PATHS,
            max_value=sc.SLIDER_MAX_PATHS,
            value=20,
            help="Each simulation is a sequence of bets as long as number of bets defined",
        )
        # BET % SLIDER
        bet_size = (
            col2.slider(
                "Simulated bet_fraction (%): ",
                min_value=1,
                max_value=100,
                value=10,
                help="How much of your capital are you risking on each bet",
            )
            / 100
        )
        # log_scale2 = col2.radio("Log Scale  ", [False, True])
        log_scale2 = False

        # y_axis_paths = col2.radio("Y Axis ", ["Capital", "CAGR"])
        y_axis_paths = "Capital"

        capital_paths_df = calculate_capital_paths(
            bet_win_rate, n_bets, monte_carlo_paths, bet_size
        )

        if y_axis_paths == "CAGR":
            baseline_y_paths = 0
            plot_paths_df = backtest.convert_bankroll_paths_to_cagr_paths(
                capital_paths_df
            )
            range_cagr = plot_paths_df.max(axis=1).values[-1]
            yaxis_range = (-1, abs(range_cagr) * 2)
        else:
            baseline_y_paths = 1
            plot_paths_df = capital_paths_df.copy()
            yaxis_range = None
        median_final_bankroll = np.median(plot_paths_df.tail(1).values)

        col2.subheader(f"Simulated {y_axis_paths} Paths")
        col2.write(
            "Median terminal {} (dashed line): {:.0%}".format(
                y_axis_paths, median_final_bankroll
            )
        )

        chart2 = px.line(
            plot_paths_df,
            labels={
                "index": "Bet sequence index",
                "value": "capital as % of initial",
            },
            log_y=log_scale2,

        )
        chart2 = plotting.custom_figure_layout_update(
            chart2,
            x_axis_name="Bet sequence index",
            y_axis_name=f"{y_axis_paths} as % of initial",
            title=f"{y_axis_paths} Evolution",
            x_tick_format=",d",
            y_tick_format="%{3}f",
            x_showgrid=False,
            y_showgrid=False,
            yaxis_range=yaxis_range,
        )

        chart2.add_hline(
            y=median_final_bankroll,
            line_dash="dash",
            line_color=plotting.graph_settings.zerolinecolor,
        )

        chart2.add_hline(
            y=baseline_y_paths,
            line_dash="solid",
            line_color=plotting.graph_settings.zerolinecolor,
        )

        col2.plotly_chart(
            chart2,
            use_container_width=True,
        )

        col2.write(
            """Median terminal capital observed through {} bets
               at {:.0%} bet_fraction: {:.0%} (%)""".format(
                n_bets, bet_size, median_final_bankroll
            )
        )
        col2.empty()
        col2.empty()

        st.markdown(
            """The Kelly Criterion allows us to identify which
               bet fractions lead to capital growth, and which to ruin."""
        )
        st.write("")


@st.cache(**sc.CACHE_KWARGS)
def get_expected_gains_for_premiums(
    premiums,
    bet_win_rate,
    n_bets,
    log_scale=False,
    yaxis="Expected Terminal Capital (% of initial)",
):
    """Get Gains for multiple premiums and bets"""
    resolution_bet_size = 40
    bet_size_arr = np.array(
        [i / resolution_bet_size for i in range(resolution_bet_size + 1)]
    )
    gain_vs_premium_df = pd.DataFrame(columns=premiums)

    gain_vs_premium_df["Bet Fraction"] = bet_size_arr

    # premiums = premiums +prem_factor/10
    premiums = premiums.round(2)

    for premium in premiums:
        for bet_size in bet_size_arr:
            geometric_growth_rate = ((1 + bet_size * (1 + premium)) ** bet_win_rate) * (
                (1 - bet_size * (1 - premium)) ** (1 - bet_win_rate)
            ) - 1

            expected_gain = (1 + geometric_growth_rate) ** n_bets

            gain_vs_premium_df.at[
                bet_size * resolution_bet_size, premium
            ] = expected_gain

    gain_vs_premium_df = gain_vs_premium_df.melt(
        "Bet Fraction", value_vars=premiums
    ).rename(columns={"variable": "Premium", "value": yaxis})

    gain_bet_chart = px.line(
        gain_vs_premium_df,
        x="Bet Fraction",
        y=yaxis,
        color="Premium",
        log_y=log_scale,
    )

    gain_bet_chart = plotting.custom_figure_layout_update(
        gain_bet_chart,
        x_axis_name="Bet Size (% of Capital)",
        y_axis_name=yaxis,
        title="",
        x_tick_format=".0%",
        y_tick_format=".0%",
        x_showgrid=False,
        y_showgrid=False,
        # yaxis_range=y_axis_range
    )

    gain_bet_chart.add_hline(
        y=1, line_dash="dash", line_color=plotting.graph_settings.zerolinecolor
    )

    return gain_bet_chart, gain_vs_premium_df


def cointoss_with_premium():
    """Bankroll Calculation for the biased Coin Toss with Premiums"""

    # MULTIPLE PREMIUMS
    with st.container():
        st.subheader("Introduction of Premium")
        st.info("Now imagine that there is a premium involved in the cointoss.")

        st.latex(
            """{ Win }_{ {Bankroll }_{n}}= { Bankroll }_{n-1}
               \\cdot(1+ { betfraction }+ { premium } \\cdot { betfraction })"""
        )
        st.latex(
            """ { Loss }_{ {Bankroll }_{n}}= { Bankroll }_{n-1}
               \\cdot(1- { betfraction }+ { premium } \\cdot { betfraction })"""
        )

        st.write("")
        st.write("")
        st.write(
            """Negative premium means you have to pay to take the bet.
               Positive means you charge to take the bet."""
        )
        st.write("")

        col1, col2 = st.columns(2)
        col1.empty()
        col2.empty()
        col1.subheader("Bet parameters")
        # BET ODDS SLIDER
        bet_win_rate = (
            col1.slider("Win_rate of the bet: ", min_value=0, max_value=100, value=66)
            / 100
        )
        # ITERATIONS SLIDER
        n_bets = col1.slider(
            "Number of trials: ",
            min_value=sc.SLIDER_MIN_DAYS,
            max_value=sc.SLIDER_MAX_DAYS,
            value=25,
        )

        col2.subheader("Premium parameters")
        # PREMIUM RANGE
        start_prem, end_prem = col2.slider(
            "Premium range (%):",
            0.1,
            100.0,
            (0.1, 40.0),
            help="The lowest premium that will be plotted",
        )
        # PREMIUM STEPS SLIDER
        prem_steps = col2.number_input(
            "Number of premium scenarios: ",
            min_value=1,
            max_value=40,
            value=15,
            help="The number of premium examples that will be shown",
        )
        # LOG SCALE RADIO
        log_scale = col1.radio("Log Scale", [False, True])  #

        y_axis = "Expected Terminal Capital (% of initial)"

        if start_prem == end_prem or prem_steps == 1:
            premiums = np.array([start_prem])
        else:
            premiums = np.arange(
                start_prem / 100,
                end_prem / 100 + (end_prem - start_prem) / prem_steps / 100,
                (end_prem - start_prem) / (prem_steps - 1) / 100,
            )

        gain_vs_bet_chart, _ = get_expected_gains_for_premiums(
            premiums, bet_win_rate, n_bets, log_scale=log_scale, yaxis=y_axis
        )

        st.write("")
        st.write("")
        st.subheader(
            f"{y_axis} as function of premium and bet size after {n_bets} trials"
        )
        st.plotly_chart(
            gain_vs_bet_chart,
        )  # use_container_width=True,

        st.markdown(
            """
            In this visual you can see how there are combinations of premiums
            and bet fractions that lead to positive growth expectation,
            and combinations that lead to ruin.
            This crucial factor allows us to find a relationship between trade size,
            premium, and expected return.
            """
        )


if __name__ == "__main__":
    sc.setup_page_config("Kelly Criterion for Option Pricing")
    sc.add_cross_app_links_to_sidebar(st.sidebar)
    plotting.graph_settings = sc.add_style_settings_to_sidebar(st.sidebar)
    cointoss()

    cointoss_with_premium()

    st.markdown(
        sc.get_footer(
            plotting.graph_settings.text_color, plotting.graph_settings.background_color
        ),
        unsafe_allow_html=True,
    )

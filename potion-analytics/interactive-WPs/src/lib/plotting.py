#!/usr/bin/env python3
"""Module with various plot functions"""
from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import matplotlib.patches as mpatches
import seaborn as sns

import lib.kelly as kelly
import lib.distributions as dst
import lib.random_path_generation as rpg
import lib.convolution as convolution


@dataclass
class GraphSettings:
    """Class to pack all the project graph settings"""

    background_color: str
    template_pick: str
    linewidth: int
    linecolor: str
    gridcolor: str
    zerolinecolor: str
    showline: bool
    text_color: str
    accent_color: str
    second_accent: str


graph_settings = GraphSettings(
    background_color="black",
    template_pick="plotly_dark",
    linewidth=1,
    linecolor="#1b003d",
    gridcolor="#1b003d",
    zerolinecolor="#ffffff",  # "#813eed",
    showline=False,
    text_color="#ffffff",  # duplicate of the setting from "config.toml"
    accent_color="#f3ff0f",
    second_accent="#e7e311",
)


def get_tick_format(axis_name):
    """get tick format for the axis"""
    res = None
    if (
        "max_drawdown" in axis_name
        or "cagr" in axis_name
        or "premium" in axis_name
        or "strike_pct" in axis_name
        or "util" in axis_name
    ):
        res = ".0%"
    elif "duration" in axis_name:
        res = ",d"
    elif "sharpe" in axis_name:
        res = ".1f"

    return res


def get_range(axis_name):
    """get range for the axis"""
    res = None
    if "max_drawdown" in axis_name or "util" in axis_name:
        res = [0, 1]
    elif "cagr" in axis_name:
        res = [-1, 2]
    elif "sharpe" in axis_name:
        res = [-2, 2]

    return res


def custom_figure_layout_update(
    figure,
    x_axis_name,
    y_axis_name,
    title,
    x_tick_format=".0%",
    y_tick_format=".0%",
    x_showgrid=True,
    y_showgrid=True,
    **kwargs,
):
    """Update fig with axis names and title"""
    figure.update_layout(
        title=title,
        plot_bgcolor=graph_settings.background_color,
        paper_bgcolor=graph_settings.background_color,
        template=graph_settings.template_pick,
        yaxis=dict(
            title=y_axis_name,
            showline=graph_settings.showline,
            linewidth=graph_settings.linewidth,
            linecolor=graph_settings.linecolor,
            gridcolor=graph_settings.gridcolor,
            tickformat=y_tick_format,
            showgrid=y_showgrid,
        ),
        xaxis=dict(
            title=x_axis_name,
            showline=graph_settings.showline,
            linewidth=graph_settings.linewidth,
            linecolor=graph_settings.linecolor,
            gridcolor=graph_settings.gridcolor,
            tickformat=x_tick_format,
            showgrid=x_showgrid,
        ),
        **kwargs,
    )

    return figure


def plot_kelly_curve(kelly_curve_df):
    """Plot Kelly Curve"""
    return px.line(kelly_curve_df.copy(), x="util", y="premium")


def plot_bankroll_df(bankroll_df):
    """Plot bankroll_df"""
    fig = go.Figure()
    bankroll_df_len = len(bankroll_df)
    for column in bankroll_df.columns:
        fig.add_trace(
            go.Scatter(
                x=list(range(bankroll_df_len)), y=bankroll_df[column], mode="lines"
            )
        )
    return fig


def plot_histogram_df(returns_histogram_df):
    """Plot Histomram_df"""
    return px.line(
        returns_histogram_df[["return", "freq"]].copy(), x="return", y="freq"
    )


def flow2_plot(
    flow2_cached_results,
    hue="strike_pct",
    cagr_pick=None,
    max_drawdown_pick=None,
    x_axis="100_percentile_max_drawdown",
    y_axis="50_percentile_cagr",
    title="Cached Backtest Results",
):
    """Plot flow2 graph"""
    # Flow2 Plot
    ###########################################################################################
    # hue = "cluster"  # 'strike_pct', 'duration', 'util'

    fig_flow2_plot_inner = go.Figure(layout_xaxis_range=[0, 100])
    fig_flow2_plot_inner = px.scatter(
        flow2_cached_results, x=x_axis, y=y_axis, color=hue, symbol="asset_label"
    )

    fig_flow2_plot_inner = custom_figure_layout_update(
        fig_flow2_plot_inner,
        x_axis_name=x_axis,
        y_axis_name=y_axis,
        title=title,
        x_tick_format=".0%",
        y_tick_format=".0%",
        x_showgrid=False,
        y_showgrid=False,
        showlegend=False,
        xaxis_range=[0, 1],
    )
    if not cagr_pick is None and not max_drawdown_pick is None:

        fig_flow2_plot_inner.add_shape(
            type="line",
            x0=0,
            y0=cagr_pick,
            x1=max_drawdown_pick,
            y1=cagr_pick,
            line=dict(
                color="Red",
            ),
            xref="x",
            yref="y",
        )

        fig_flow2_plot_inner.add_shape(
            type="line",
            x0=max_drawdown_pick,
            y0=cagr_pick,
            x1=max_drawdown_pick,
            y1=flow2_cached_results["50_percentile_cagr"].max(),
            line=dict(
                color="Red",
            ),
            xref="x",
            yref="y",
        )

    return fig_flow2_plot_inner


###################################################################################################
# Testing
###################################################################################################
def plot_all_kelly_curves_with_optimal_bet(
    underlying_returns, strike, number_of_utils, option_type="put"
):
    """Plot Kelly Curves which have extremum on the fig1
    Plot Kelly Curves from the fig1 derivatives at the fig2"""
    kelly_curve_df = kelly.get_kelly_curve(
        underlying_returns, strike, number_of_utils, option_type=option_type
    )
    premiums = kelly_curve_df.premium
    utils = np.linspace(0, 1, 10)

    fig1 = go.Figure()
    fig2 = go.Figure()

    # loop over each premium/util to calculate log_expected_return
    # and derivative of the log_expected_return
    for premium in premiums:
        expected_log_returns = []
        expected_log_returns_derivatives = []
        for util in utils:
            expected_log_returns.append(
                kelly.get_kelly_log_expected_payout(
                    underlying_returns, strike, premium, util, option_type=option_type
                )
            )
            expected_log_returns_derivatives.append(
                kelly.get_kelly_derivative(
                    premium, underlying_returns, strike, util, option_type=option_type
                )
            )
        fig1.add_trace(
            go.Scatter(x=utils, y=expected_log_returns, mode="lines", name=str(premium))
        )
        fig2.add_trace(
            go.Scatter(
                x=utils,
                y=expected_log_returns_derivatives,
                mode="lines",
                name=str(premium),
            )
        )

    fig1.update_layout(title="E[log(1+r(u))] = Expected Log of Bankroll")
    return fig1, fig2


def plot_all_kelly_curves_with_optimal_bet_annualized(
    historical_df,
    asset,
    strike,
    number_of_utils,
    duration=1,
    convolution_n_paths=10000,
    option_type="put",
    dash_line_color="white",
):
    """Plot Kelly Curves which have extremum on the fig1
    Plot Kelly Curves from the fig1 derivatives at the fig2"""
    price_sequence = historical_df[asset].dropna()
    returns_sequence = price_sequence.pct_change()[1:]
    underlying_returns = convolution.daily_returns_to_n_day_returns(
        returns_sequence,
        number_of_paths=convolution_n_paths,
        n_days=duration,
    )

    kelly_curve_df = kelly.get_kelly_curve(
        underlying_returns, strike, number_of_utils, option_type=option_type
    )
    premiums = kelly_curve_df.premium

    f_len = len(premiums) - 1

    new_max_premiums = pd.Series(
        [premiums[f_len] * (1 + i) for i in [0.1, 0.25, 0.5, 0.75, 1.25]]
    )
    new_min_premiums = pd.Series(
        [premiums[0] * (1 - i) for i in [0.1, 0.25, 0.5, 0.75, 1.25]]
    )
    new_min_premiums = new_min_premiums.reindex(
        index=new_min_premiums.index[::-1]
    ).to_numpy()
    extended_premiums = new_min_premiums
    extended_premiums2 = new_max_premiums.to_numpy()

    utils = np.linspace(0, 1, 40)  # THE MOVE TO 40 HERE LET'S CHECK PERFORMANCE HIT

    fig1 = go.Figure()
    fig2 = go.Figure()
    fig_bonding_curves_zoomed = go.Figure()

    extremum_utils = []
    extremum_cagrs = []
    # loop over each premium/util to calculate log_expected_return
    # and derivative of the log_expected_return
    for premium in premiums:
        expected_log_returns = []
        # expected_compound_factor = []
        expected_log_returns_derivatives = []
        for util in utils:
            expected_log_returns.append(
                math.exp(
                    kelly.get_kelly_log_expected_payout(
                        underlying_returns,
                        strike,
                        premium,
                        util,
                        option_type=option_type,
                    )
                )
                ** (365 / duration)
                - 1
            )
            expected_log_returns_derivatives.append(
                kelly.get_kelly_derivative(
                    premium, underlying_returns, strike, util, option_type=option_type
                )
            )
            # expected_compound_factor.append(
            #     math.exp(expected_log_returns[-1] * simulation_length_days)
            # )

        fig1.add_trace(
            go.Scatter(
                x=utils,
                y=expected_log_returns,  # expected_compound_factor
                mode="lines",
                name="Premium" + str(np.round(premium * 100, 2)) + "%",
            )
        )
        fig_bonding_curves_zoomed.add_trace(
            go.Scatter(
                x=utils,
                y=expected_log_returns,  # expected_compound_factor
                mode="lines",
                name="Premium" + str(np.round(premium * 100, 2)) + "%",
            )
        )

        max_ret = max(expected_log_returns)
        index_max = expected_log_returns.index(max_ret)
        max_util = utils[index_max]

        extremum_utils.append(max_util)
        extremum_cagrs.append(max_ret)

        # We add markers with optimal premium points
        fig1.add_trace(
            go.Scatter(
                x=[max_util],
                y=[max_ret],
                mode="markers",
                name="optimal_u_{}%".format(round(max_util * 100, 0)),
            )
        )

        # We add markers with optimal premium points
        fig_bonding_curves_zoomed.add_trace(
            go.Scatter(
                x=[max_util],
                y=[max_ret],
                mode="markers",
                name="optimal_u_{}%".format(round(max_util * 100, 0)),
            )
        )

    fig_bonding_curves_zoomed.add_trace(
        go.Scatter(
            x=extremum_utils,
            y=extremum_cagrs,
            mode="lines",
            name="Optimal Bonding Curve",
            line_color=dash_line_color,
        )
    )

    for premium in extended_premiums:
        expected_log_returns = []
        for util in utils:
            expected_log_returns.append(
                math.exp(
                    kelly.get_kelly_log_expected_payout(
                        underlying_returns, strike, premium, util
                    )
                )
                ** (365 / duration)
                - 1
            )
        fig1.add_trace(
            go.Scatter(
                x=utils,
                y=expected_log_returns,  # expected_compound_factor
                mode="lines",
                line={"dash": "dash", "color": dash_line_color},
                name="belowoptimal" + str(np.round(premium * 100, 2)) + "%",
            )
        )

        # Derivatives figures
        fig2.add_trace(
            go.Scatter(
                x=utils,
                y=expected_log_returns_derivatives,
                mode="lines",
                name="Premium" + str(np.round(premium * 100, 2)) + "%",
            )
        )

    for premium in extended_premiums2:
        expected_log_returns = []
        for util in utils:
            expected_log_returns.append(
                math.exp(
                    kelly.get_kelly_log_expected_payout(
                        underlying_returns,
                        strike,
                        premium,
                        util,
                        option_type=option_type,
                    )
                )
                ** (365 / duration)
                - 1
            )
        fig1.add_trace(
            go.Scatter(
                x=utils,
                y=expected_log_returns,  # expected_compound_factor
                mode="lines",
                line={"dash": "dash", "color": dash_line_color},
                name="aboveoptimal" + str(np.round(premium * 100, 2)) + "%",
            )
        )

        # Derivatives figures
        fig2.add_trace(
            go.Scatter(
                x=utils,
                y=expected_log_returns_derivatives,
                mode="lines",
                name="Premium" + str(np.round(premium * 100, 2)) + "%",
            )
        )

        fig1.update_layout(yaxis=dict(range=[-1, 1]))

    return fig1, fig2, fig_bonding_curves_zoomed


def visualize_returns_histogram_vs_random_path_consistency(
    price_sequence, number_of_paths, path_length, number_of_bins=100
):
    """Function to check consistency between random price path generation
    and creating a returns histogram from the price path"""
    # fix bin edges before we start
    returns = pd.Series(price_sequence).pct_change().values[1:]
    _, bin_edges = np.histogram(returns, bins=number_of_bins, density=False)

    # random price paths
    random_price_paths = rpg.generate_price_paths_from_returns(
        returns, number_of_paths, path_length, current_price=1
    )
    initial_returns_histogram = dst.get_returns_histogram_from_price_sequence(
        price_sequence=price_sequence, n_bins=bin_edges
    )

    # add returns histogram from each price path to the figure
    fig = go.Figure()
    for price_path in random_price_paths:
        path_returns_histogram = dst.get_returns_histogram_from_price_sequence(
            price_sequence=price_path, n_bins=bin_edges
        )
        fig.add_trace(
            go.Scatter(
                x=initial_returns_histogram["return"],
                y=path_returns_histogram["freq"].values,
                mode="lines",
            )
        )

    # add initial returns histogram
    fig.add_trace(
        go.Scatter(
            x=initial_returns_histogram["return"],
            y=initial_returns_histogram["freq"],
            mode="lines",
            line={"dash": "dash", "color": "black"},
            name="original path pdf",
        )
    )
    return fig


def plot_kdes(
    kde_dfs_sequence,
    labels,
    cmaps=("Reds", "Blues", "Greens", "Greys", "Purples"),
    x_axis_name="max_drawdown",
    y_axis_name="cagr",
):
    """Plot multiple kdes at one chart"""
    handles = []
    fig_kde, _ = plt.subplots()
    for i, kde_df in enumerate(kde_dfs_sequence):
        sns.kdeplot(
            data=kde_df,
            x=x_axis_name,
            y=y_axis_name,
            shade=True,
            thresh=0.05,
            # cbar=True,
            cmap=cmaps[i],
            alpha=0.5,
        )
        handles.append(
            mpatches.Patch(facecolor=plt.get_cmap(cmaps[i])(100), label=labels[i]),
        )

    for axis in fig_kde.axes:
        axis.yaxis.set_major_formatter(PercentFormatter(1))
        axis.xaxis.set_major_formatter(PercentFormatter(1))

    plt.legend(handles=handles)

    return fig_kde


def plot_paths(
    paths_df, kind="cagr", plot_median=False, title=None, x_axis_name="Days"
):
    """plot bankrolls_df or cagrs df"""

    fig_paths = go.Figure()

    if kind != "cagr":
        top_range_y = 3
        bottom_range_y = 0
        y_axis_name = "Bankroll (x times)"
    else:
        top_range_y = max(0.5, paths_df.max(axis=1).values[-1])
        bottom_range_y = min(-0.5, paths_df.min(axis=1).values[-1])
        y_axis_name = kind.upper()

    if plot_median:
        fig_paths.add_trace(
            go.Scatter(
                x=paths_df.index,
                y=paths_df.median(axis=1),
                mode="lines+markers",
                name=f"median_{kind}",
                # line_dash = 'lines+markers',
                line_width=3,
                line_color=graph_settings.zerolinecolor,
            )
        )
    for col in paths_df:
        fig_paths.add_trace(
            go.Scatter(
                x=paths_df.index,
                y=paths_df[col],
                mode="lines",
                name=col,
                # line_dash = 'lines+markers',
                line_width=3,
            )
        )
    if plot_median:
        fig_paths.add_trace(
            go.Scatter(
                x=paths_df.index,
                y=paths_df.median(axis=1),
                mode="lines+markers",
                name=f"median_{kind}",
                # line_dash = 'lines+markers',
                line_width=3,
                line_color=graph_settings.zerolinecolor,
            )
        )

    if not title:
        title = f"Simulated {kind.upper()} paths"
    if kind == "cagr":
        y_tick_format = ".0%"
    else:
        y_tick_format = ".0"

    custom_figure_layout_update(
        fig_paths,
        x_axis_name=x_axis_name,
        y_axis_name=y_axis_name,
        title=title,
        x_tick_format="0",
        y_tick_format=y_tick_format,
        yaxis_range=(bottom_range_y, abs(top_range_y)),
    )

    return fig_paths


###################################################################################################

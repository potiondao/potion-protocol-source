"""
This module contains helpful functions for producing analysis plots which help the user examine
the curve generation process.
"""
import numpy as np

from typing import List

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import io
import plotly.io as pio
from PIL import Image

from potion.curve_gen.kelly import (probability_from_density, kelly_formula,
                                    kelly_formula_derivative, evaluate_premium_curve)
from potion.curve_gen.payoff.payoff import get_payoff_odds


def pdf_and_payout_sweep(pdf_x_vals: np.ndarray, pdf_y_vals: np.ndarray,
                         kelly_premiums: np.ndarray, ticker: str, legend=False, upper_x_lim=2.0):
    """
    Plots the PDF and payout for a sweep of premium values to demonstrate how the values are
    changing as the optimizer runs during curve generation.

    Parameters
    ----------
    pdf_x_vals : numpy.ndarray
        The X values of the plot where PDF and payout values will be plotted
    pdf_y_vals : numpy.ndarray
        The Y values of the PDF plot
    kelly_premiums : numpy.ndarray
        The premium values which will each produce a payout graph to compare
    ticker : str
        The name of the asset to include in the title
    legend : bool
        (Optional. Default: False) Whether to show the legend or not
    upper_x_lim: float
        (Optional. Default: 2.0) The value of the largest x-value to include in the plot. Used
        in scaling axes

    Returns
    -------
    fig : figure
        The plotly figure object
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=pdf_x_vals, y=pdf_y_vals,
                             mode='lines',
                             name='{} Price PDF'.format(ticker),
                             showlegend=False), secondary_y=False)

    # Get where the max X value is so that we know where to stop checking Y values when
    # we pick the plot's scale
    x_lim_idx = np.where(pdf_x_vals < upper_x_lim)[0][-1]

    max_y = 0.0
    for premium in kelly_premiums:
        odds = get_payoff_odds(premium)

        # Get the max Y value being displayed
        my = np.amax(odds[:x_lim_idx])
        if my > max_y:
            max_y = my

        fig.add_trace(go.Scatter(x=pdf_x_vals, y=odds,
                                 mode='lines',
                                 name='Put Payout @{} Premium'.format(premium),
                                 showlegend=False), secondary_y=True)

    if legend:
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Price at Expiration (Relative to Current Price)'
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    fig.update_yaxes(title_text='Probability Density', secondary_y=False)
    fig.update_yaxes(title_text='Profit and Loss (%)', secondary_y=True)
    fig.update_xaxes(range=[0.0, upper_x_lim])
    fig.update_yaxes(range=[-1.0, max_y], secondary_y=True)

    return fig


def kelly_growth_sweep(pdf_x_vals: np.ndarray, pdf_y_vals: np.ndarray,
                       kelly_premiums: np.ndarray, bet_fractions: np.ndarray):
    """
    Plots the log expected growth rate curve which is output from the Kelly formula for
    a sweep of premium values to demonstrate how the values are changing as the optimizer
    runs during curve generation.

    Parameters
    ----------
    pdf_x_vals : numpy.ndarray
        The X values of the plot where PDF and payout values will be plotted
    pdf_y_vals : numpy.ndarray
        The Y values of the PDF plot
    kelly_premiums : numpy.ndarray
        The premium values which will each produce a payout graph to compare
    bet_fractions : numpy.ndarray
        The bet fraction points from 0 to 1 which are the X values of the Kelly curve

    Returns
    -------
    fig : figure
        The plotly figure object
    """
    fig = go.Figure()

    prob_bins = probability_from_density(pdf_x_vals, pdf_y_vals)

    for premium in kelly_premiums:
        log_ex_growth_curve = kelly_formula(prob_bins, get_payoff_odds(premium), bet_fractions)

        fig.add_trace(go.Scatter(x=bet_fractions, y=log_ex_growth_curve,
                                 mode='lines',
                                 name='Log Expected Growth @{} Premium'.format(premium),
                                 showlegend=False))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Bet Fraction (0% to 100%)'
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    fig.update_yaxes(title_text='Log Expected Growth Rate')
    fig.update_xaxes(range=[0.0, 1.0])

    return fig


def kelly_derivative_sweep(pdf_x_vals: np.ndarray, pdf_y_vals: np.ndarray,
                           kelly_premiums: np.ndarray, bet_fractions: np.ndarray):
    """
    Plots the derivative of the Kelly formula for a sweep of premium values to demonstrate
    how the values are changing as the optimizer runs during curve generation.

    Parameters
    ----------
    pdf_x_vals : numpy.ndarray
        The X values of the plot where PDF and payout values will be plotted
    pdf_y_vals : numpy.ndarray
        The Y values of the PDF plot
    kelly_premiums : numpy.ndarray
        The premium values which will each produce a payout graph to compare
    bet_fractions : numpy.ndarray
        The bet fraction points from 0 to 1 which are the X values of the Kelly curve

    Returns
    -------
    fig : figure
        The plotly figure object
    """
    fig = go.Figure()

    prob_bins = probability_from_density(pdf_x_vals, pdf_y_vals)

    min_y = 0.0
    max_y = 0.0
    for premium in kelly_premiums:
        derivative_curve = kelly_formula_derivative(prob_bins, get_payoff_odds(premium),
                                                    bet_fractions)

        ly = np.amin(derivative_curve)
        uy = np.amax(derivative_curve)

        if ly < min_y:
            min_y = ly
        if uy > max_y:
            max_y = uy

        fig.add_trace(go.Scatter(x=bet_fractions, y=derivative_curve,
                                 mode='lines',
                                 name='Derivative @{} Premium'.format(premium), showlegend=False))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Bet Fraction (0% to 100%)'
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    if max_y > 5.0:
        max_y = 5.0
    if min_y < -5.0:
        min_y = -5.0

    fig.update_yaxes(title_text='Kelly Derivative')
    fig.update_xaxes(range=[0.0, 1.0])
    fig.update_yaxes(range=[min_y, max_y])

    return fig


def plot_convolutions(pdf_x_values: np.ndarray, pdf_y_value_list: List[np.ndarray],
                      x_lims=(0.0, 2.0)):
    """
    Creates a plotly figure of the convolutions of the PDF forward in time

    Parameters
    ----------
    pdf_x_values : numpy.ndarray
        The X values of the PDF functions output from convolution
    pdf_y_value_list : List[numpy.ndarray]
        The Y values of the PDFs output from convolution. Each element of the List corresponds to
        one day's PDF
    x_lims : tuple
        (Optional. Default: (0.0, 2.0)) The limits on the X values for the plot

    Returns
    -------
    fig : figure
        The plotly figure object
    """
    fig = go.Figure()

    for i, pdf_y_value in enumerate(pdf_y_value_list):
        fig.add_trace(go.Scatter(x=pdf_x_values, y=pdf_y_value,
                                 mode='lines',
                                 name='pdf_{}'.format(i)))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Relative Price'
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    fig.update_yaxes(title_text='Probability Density')
    fig.update_xaxes(range=x_lims)

    return fig


def plot_curve(fit_params: List[float], bf: np.ndarray, opt: np.ndarray,
               label='Calculated Optimal Curve', u_label='User ABCD Curve',
               x_label='Utilization', y_label='Premium (%)'):
    """
    Creates a plotly figure of the specified Kelly curve

    Parameters
    ----------
    fit_params : List[float]
        The A, B, C, D parameters fit to the Kelly curve
    bf : numpy.ndarray
        The X points of the Kelly curve from 0 to 1
    opt : numpy.ndarray
        The Y points of the Kelly curve output by the optimizer
    label : str
        (Optional. Default: 'Calculated Optimal Curve') The legend label for the User ABCD curve
    u_label : str
        (Optional. Default: 'User ABCD Curve') The legend label for the User ABCD curve
    x_label : str
        (Optional. Default: 'Calculated Optimal Curve') The X-axis plot label
    y_label : str
        (Optional. Default: 'Premium (%)') The Y-axis plot label

    Returns
    -------
    fig : figure
        The plotly figure object
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bf, y=opt,
                             mode='lines',
                             name=label))

    range_to_use = np.where((np.asarray(
        opt) > 1e-10) | (np.asarray(opt) < -1e-10))[0][-1]

    fig.add_trace(
        go.Scatter(x=bf[:range_to_use+1], y=evaluate_premium_curve(fit_params, bf)[:range_to_use+1],
                   mode='lines', name=u_label))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title=x_label,
        yaxis_title=y_label).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    return fig


def show(fig):
    """
    Displays a plotly figure using the system viewer

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The figure to display

    Returns
    -------
    None
    """
    buf = io.BytesIO()
    pio.write_image(fig, buf)
    img = Image.open(buf)
    img.show()

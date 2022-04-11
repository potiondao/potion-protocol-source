"""
This module provides the plots which the curve generation tool produces for the GUI
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from potion.curve_gen.kelly import evaluate_premium_curve
from potion.curve_gen.payoff.builder import PayoffConfigBuilder
from potion.curve_gen.payoff.payoff import configure_payoff, get_payoff_odds
from potion.curve_gen.training.train import parse_date_from_str, get_training_dates


def plot_curves_from_csv(curve_df):
    """
    Opens the curves CSV from the curve generator output and generates Plotly plots for each

    Parameters
    ----------
    curve_df : pandas.DataFrame
        The DataFrame containing the output curve data

    Returns
    ----------
    figures : List[plotly.graph_objects.Figure]
        The List of plotly figures for each curve
    curve_df : pandas.DataFrame
        A DataFrame containing the curve info read from the CSV file
    """
    figures = []
    for i, train_row in curve_df.iterrows():

        fit_params = [train_row.A, train_row.B, train_row.C, train_row.D]

        bf = train_row.bet_fractions
        opt = train_row.curve_points

        lab = 'Minimum Optimal Curve'
        lab_u = 'User ABCD Curve'

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bf, y=opt,
                                 mode='lines',
                                 name=lab))
        fig.add_trace(go.Scatter(x=bf, y=evaluate_premium_curve(
            fit_params, bf), mode='lines', name=lab_u))

        fig.update_layout(
            plot_bgcolor='rgb(230,230,230)',
            xaxis_title='Utilisation',
            yaxis_title='Premium (%)').update_xaxes(showgrid=True).update_yaxes(showgrid=True)

        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

        figures.append(fig)

    return figures


def plot_pdf_and_option_payout(pdf_df, curves_df):
    """
    Generates a Plotly plot containing a graph of the PDF and payout functions
    used in generating the curves

    Parameters
    ----------
    pdf_df : pandas.DataFrame
        Dataframe containing the PDF at each expiration
    curves_df : pandas.DataFrame
        Dataframe containing the curve info

    Returns
    -------
    figures : List[Figure]
        A List of plotly figure objects corresponding to each curve
    """
    figures = []
    for i, train_row in curves_df.iterrows():

        # Get the arrays of the PDF function
        pdf_x_vals = pdf_df['Prices']
        pdf_y_vals = pdf_df[str(train_row.Ticker) + '-' + str(
            train_row.Label) + '|' + str(train_row.Expiration)]

        # Get the premium amount at util 0.1 for plotting payout
        idx = (np.abs(train_row.bet_fractions - 0.1)).argmin()
        prem01 = train_row.curve_points[idx]

        payoff_cfg = PayoffConfigBuilder().set_x_points(pdf_x_vals.to_numpy()).add_option_leg(
            'put', 'short', 1.0, train_row.StrikePercent).build_config()
        configure_payoff(payoff_cfg)

        odds01 = get_payoff_odds(prem01)

        odds01 = odds01 * 100.0

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=pdf_x_vals, y=pdf_y_vals,
                                 mode='lines',
                                 name='{} Price PDF'.format(str(
                                     train_row.Ticker))), secondary_y=False)
        fig.add_trace(go.Scatter(x=pdf_x_vals, y=odds01,
                                 mode='lines',
                                 name='Put Payout @0.1 Util'), secondary_y=True)

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
        fig.update_xaxes(range=[0.0, 2.0])

        figures.append(fig)

    return figures


def plot_training_data_sets(history_df: pd.DataFrame, training_df: pd.DataFrame,
                            log_plot=False):
    """
    Generates Plotly plots for each curve containing the training data price paths

    Parameters
    ----------
    history_df : pandas.DataFrame
        The history of prices that was used in training
    training_df : pandas.DataFrame
        The output of the training process containing all of the windows for each asset
    log_plot : bool
        (Optional. Default: False) Whether to plot the training data in log prices or prices

    Returns
    -------
    fig_map : dict
        dict mapping asset-label combinations to Plotly figure objects
    """
    full_dates = get_training_dates(history_df)

    fig_map = {}
    for i, training_row in training_df.iterrows():

        # Graph each training set as a separate color
        training_path = training_row.TrainingPrices
        full_price_history = history_df[training_row.Ticker].to_numpy()
        start_date, start_index = parse_date_from_str(
            training_row.StartDate, full_dates, full_price_history)
        end_date, end_index = parse_date_from_str(
            training_row.EndDate, full_dates, full_price_history)

        training_dates = full_dates[(full_dates >= start_date) & (full_dates <= end_date)]

        if log_plot:
            x_label = 'Log Number of Days'
            y_label = 'Log Price USD'

            x_t = training_dates
            x_in = full_dates

            x_in = np.where(x_in < 0, 1e-20, x_in)
            x_in = np.where(x_in == 0, 1e-20, x_in)
            x_t = np.where(x_t < 0, 1e-20, x_t)
            x_t = np.where(x_t == 0, 1e-20, x_t)

            y_t = training_path
            y_in = full_price_history

            y_in = np.where(y_in < 0, 1e-20, y_in)
            y_in = np.where(y_in == 0, 1e-20, y_in)
            y_t = np.where(y_t < 0, 1e-20, y_t)
            y_t = np.where(y_t == 0, 1e-20, y_t)

            x_vals_train = np.log(x_t)
            y_vals_train = np.log(y_t)

            x_vals_full = np.log(x_in)
            y_vals_full = np.log(y_in)
        else:
            x_label = 'Number of Days'
            y_label = 'Price USD'

            x_vals_train = training_dates
            y_vals_train = training_path

            x_vals_full = full_dates
            y_vals_full = full_price_history

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals_full, y=y_vals_full,
                                 mode='lines',
                                 name='{} Full Path'.format(training_row.Ticker),
                                 customdata=[log_plot]))
        fig.add_trace(go.Scatter(x=x_vals_train, y=y_vals_train,
                                 mode='lines',
                                 name='{} Training Path'.format(training_row.Ticker + '-' +
                                                                training_row.Label),
                                 customdata=[log_plot]))

        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

        fig.update_layout(
            plot_bgcolor='rgb(230,230,230)', xaxis_title=x_label,
            yaxis_title=y_label).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

        fig_map[training_row.Ticker + '-' + training_row.Label] = fig

    return fig_map

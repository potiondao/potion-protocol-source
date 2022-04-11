"""
This module provides the plots which the backtesting tool produces for the GUI
"""
import streamlit as st
import numpy as np
import pandas as pd
import logging
import vaex
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from potion.curve_gen.utils import (get_ticker_from_key, get_sentiment_label_from_key)
from potion.curve_gen.payoff.builder import PayoffConfigBuilder
from potion.curve_gen.payoff.payoff import (configure_payoff, get_payoff_odds)
from potion.curve_gen.kelly import (kelly_formula, probability_from_density,
                                    kelly_value_to_growth_per_bet, growth_per_bet_to_cagr)
from potion.streamlitapp.backt.bt_utils import calculate_max_drawdown


@st.cache
def plot_performance_scatter_plot(full_df):
    """
    This function takes all of the performance and drawdown statistics from each of the
    backtesting runs, and plots them as a Plotly plot on a 2-D XY plane. On the X axis is the
    median max drawdown % and the y axis the median CAGR %.

    Parameters
    ----------
    full_df : pandas.DataFrame
        The full merged DF containing the performance statistics from all of the runs

    Returns
    ----------
    fig : plotly.graph_objects.Figure
        The figure object containing the plot
    """
    x = full_df.p50_user_maxDD.to_numpy()
    y = full_df.p50_user_cagr.to_numpy()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='Performance Scatter'))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Median Max Drawdown (%)',
        yaxis_title='Median CAGR (%)',
        hovermode='closest'
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    fig.update_xaxes(range=[-100.0, 0.0])
    fig.update_yaxes(range=[-100.0, 200.0])

    return fig


def plot_backtesting_paths(backtester, path_length, paths_to_plot=300):
    """
    This function plots the backtesting paths as Plotly plots. On the X axis is the number
    of days of the simulation and the y axis is the price on the simulated path

    Parameters
    ----------
    backtester : BatchBacktester
        The batch backtesting object for which the paths are being plotted
    path_length : int
        The length of the path being plotted
    paths_to_plot : int
        The number of paths out of the total we wish to plot

    Returns
    -------
    figures : List[plotly.graph_objects.Figure]
        The List of figure objects containing the plots
    """
    # Number of days along the path for plotting
    days = np.linspace(0, path_length - 1, path_length)

    # Loop over all the training data scenarios
    figures = []
    for key in backtester.keys:

        # Get all of the paths for the simulation
        paths = backtester.path_mapping[key]

        fig = go.Figure()

        # Plot each path
        final_price = []
        for i, path in enumerate(paths):
            if i < paths_to_plot:
                # print('i: {} path: {}'.format(i, path))
                fig.add_trace(go.Scatter(x=days, y=path,
                                         mode='lines',
                                         name='Price Path #{}'.format(i)))
                final_price.append(path[-1])

        fig.update_layout(
            title='Simulated Backtesting Paths',
            plot_bgcolor='rgb(230,230,230)',
            xaxis_title='Number of Days',
            yaxis_title='Price',
            showlegend=False
        ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

        median_price = np.median(final_price)
        # sigma = np.std(final_price)
        # low_bound = median_price - 3.0 * sigma
        # up_bound = median_price + 3.0 * sigma
        low_bound = 0.0
        up_bound = median_price * 3.0

        # print('med: {} sigma: {} low: {} up: {}'.format(median_price, sigma, low_bound, up_bound))

        fig.update_yaxes(range=[low_bound, up_bound])

        figures.append(fig)

    return figures


def create_backtesting_scenario_plots(results_df, key, util, training_key_index, duration,
                                      strike_pct, num_paths, pdf_x, pdf_y, odds, current_price,
                                      num_hist_bins=200, num_paths_to_plot=300,
                                      plot_progress_bar=None, current_count=None, total_tasks=None,
                                      plot_filename_dict=None):
    """
    This function filters the log file DF for the needed results of the backtesting
    simulation for a specific curve and generates 9 Plotly plots containing the results.

    Parameters
    ----------
    results_df : pandas.DataFrame
        The DF containing the backtesting log file
    key : str
        The training key used to identify the training data
    util : Union[float, numpy.ndarray]
        The util used in the backtesting simulation
    training_key_index : int
        The index number in the log file corresponding to the training key
    duration : int
        The number of days until the expiration of the contract
    strike_pct : float
        The strike price of the contract
    num_paths : int
        The number of paths used in the backtesting simulation
    pdf_x : numpy.ndarray
        The X values for the PDF points
    pdf_y : numpy.ndarray
        The Y values for the PDF points
    odds : numpy.ndarray
        The payout odds for the contract
    current_price : float
        The current price
    num_hist_bins : int
        The number of bins in the results histogram being plot
    num_paths_to_plot : int
        The number of paths to include in the plots
    plot_progress_bar : streamlit.progress
        The progress bar to update the UI
    current_count : int
        The current count in the progress bar update
    total_tasks : int
        The number of backtesting tasks which were simulated
    plot_filename_dict : dict
        The dict mapping each figure to its filename when saving plotly figs to file

    Returns
    -------
    output : tuple
        A tuple containing performance statistics, 9 plots of backtesting results, and an
        updated current_count for any progress bar
    """
    user_bankroll_fig = go.Figure()
    opt_bankroll_fig = go.Figure()
    user_cagr_fig = go.Figure()
    opt_cagr_fig = go.Figure()
    user_util_fig = go.Figure()
    opt_util_fig = go.Figure()
    user_amt_fig = go.Figure()
    opt_amt_fig = go.Figure()

    final_user_cagrs = []
    final_opt_cagrs = []

    user_max_dd_per_path = []
    opt_max_dd_per_path = []

    start_user_amts = []
    start_opt_amts = []
    final_user_amts = []
    final_opt_amts = []

    prob_bins = probability_from_density(pdf_x, pdf_y)
    kelly_value = kelly_formula(prob_bins, odds, util)
    growth_per_bet = kelly_value_to_growth_per_bet(kelly_value)
    bets_per_year = 365.0 / duration
    expected_cagr = growth_per_bet_to_cagr(growth_per_bet, bets_per_year)

    results_df_filtered = results_df.filter(results_df.Training_Key == training_key_index)
    results_df_filtered = results_df_filtered.filter(results_df_filtered.Exp_Duration == duration)
    results_df_filtered = results_df_filtered.filter(results_df_filtered.Strike_Pct == strike_pct)

    days = None
    for path_index in range(num_paths):

        rdff = results_df_filtered.filter(results_df_filtered.Path_ID == path_index)

        results = rdff.extract()

        if plot_progress_bar is not None and current_count is not None and total_tasks is not None:
            # print('eid: {} total: {}'.format(current_count, total_tasks))
            # print('progress: {}'.format(val))

            val = current_count / float(total_tasks)
            plot_progress_bar.progress(val)
            current_count += 1

        days = results['Timestamp'].to_numpy()[1:]

        user_bankroll = results['User_Bankroll'].to_numpy()
        opt_bankroll = results['Opt_Bankroll'].to_numpy()

        user_cagr = results['User_CAGR'].to_numpy()[1:]
        opt_cagr = results['Opt_CAGR'].to_numpy()[1:]

        final_user_cagrs.append(user_cagr[-1])
        final_opt_cagrs.append(opt_cagr[-1])

        user_maxdd = calculate_max_drawdown(user_bankroll)
        opt_maxdd = calculate_max_drawdown(opt_bankroll)

        # print('User MaxDD: {}'.format(user_maxDD))

        user_max_dd_per_path.append(user_maxdd)
        opt_max_dd_per_path.append(opt_maxdd)

        user_util = results['User_Util'].to_numpy()[1:]
        opt_util = results['Opt_Util'].to_numpy()[1:]

        user_amts = results['User_Amount'].to_numpy()[1:]
        opt_amts = results['Opt_Amount'].to_numpy()[1:]

        start_user_amts.append(user_amts[0])
        start_opt_amts.append(opt_amts[0])
        final_user_amts.append(user_amts[-1])
        final_opt_amts.append(opt_amts[-1])

        if path_index < num_paths_to_plot:
            user_bankroll_fig.add_trace(go.Scatter(x=days, y=user_bankroll[1:], mode='lines',
                                                   name='Bankroll Path #{}'.format(path_index)))
            opt_bankroll_fig.add_trace(go.Scatter(x=days, y=opt_bankroll[1:], mode='lines',
                                                  name='Bankroll Path #{}'.format(path_index)))
            user_cagr_fig.add_trace(go.Scatter(x=days, y=user_cagr, mode='lines',
                                               name='CAGR Path #{}'.format(path_index),
                                               showlegend=False))
            opt_cagr_fig.add_trace(go.Scatter(x=days, y=opt_cagr, mode='lines',
                                              name='CAGR Path #{}'.format(path_index),
                                              showlegend=False))
            user_util_fig.add_trace(go.Scatter(x=days, y=user_util, mode='lines',
                                               name='Util Path #{}'.format(path_index)))
            opt_util_fig.add_trace(go.Scatter(x=days, y=opt_util, mode='lines',
                                              name='Util Path #{}'.format(path_index)))
            user_amt_fig.add_trace(go.Scatter(x=days, y=user_amts, mode='lines',
                                              name='Amount Path #{}'.format(path_index)))
            opt_amt_fig.add_trace(go.Scatter(x=days, y=opt_amts, mode='lines',
                                             name='Amount Path #{}'.format(path_index)))

    user_cagr_fig.add_trace(
        go.Scatter(x=days, y=np.full_like(days, expected_cagr, dtype=float), mode='lines',
                   name='CAGR Expected: {}'.format(expected_cagr), line=dict(color="#000000"),
                   showlegend=False))
    opt_cagr_fig.add_trace(
        go.Scatter(x=days, y=np.full_like(days, expected_cagr, dtype=float), mode='lines',
                   name='CAGR Expected: {}'.format(expected_cagr), line=dict(color="#000000"),
                   showlegend=True))

    user_cagr_arr = np.asarray(final_user_cagrs)
    opt_cagr_arr = np.asarray(final_opt_cagrs)
    user_maxdd_arr = np.asarray(user_max_dd_per_path)
    opt_maxdd_arr = np.asarray(opt_max_dd_per_path)
    # print('{} s: {} e: {}\ncagr: {}'.format(key, strike_pct, duration, user_cagr_arr))

    performance_dict = {
        'key': key,
        'util': util,
        'duration': duration,
        'strike': strike_pct,
        'p00_user_cagr': np.percentile(user_cagr_arr, 0),
        'p25_user_cagr': np.percentile(user_cagr_arr, 25),
        'p50_user_cagr': np.percentile(user_cagr_arr, 50),
        'p75_user_cagr': np.percentile(user_cagr_arr, 75),
        'p100_user_cagr': np.percentile(user_cagr_arr, 100),
        'p00_opt_cagr': np.percentile(opt_cagr_arr, 0),
        'p25_opt_cagr': np.percentile(opt_cagr_arr, 25),
        'p50_opt_cagr': np.percentile(opt_cagr_arr, 50),
        'p75_opt_cagr': np.percentile(opt_cagr_arr, 75),
        'p100_opt_cagr': np.percentile(opt_cagr_arr, 100),
        'p00_user_maxDD': np.percentile(user_maxdd_arr, 0),
        'p25_user_maxDD': np.percentile(user_maxdd_arr, 25),
        'p50_user_maxDD': np.percentile(user_maxdd_arr, 50),
        'p75_user_maxDD': np.percentile(user_maxdd_arr, 75),
        'p100_user_maxDD': np.percentile(user_maxdd_arr, 100),
        'p00_opt_maxDD': np.percentile(opt_maxdd_arr, 0),
        'p25_opt_maxDD': np.percentile(opt_maxdd_arr, 25),
        'p50_opt_maxDD': np.percentile(opt_maxdd_arr, 50),
        'p75_opt_maxDD': np.percentile(opt_maxdd_arr, 75),
        'p100_opt_maxDD': np.percentile(opt_maxdd_arr, 100)
    }

    dff = results_df.filter(results_df.Timestamp == duration)
    dff = dff.filter(dff.Exp_Duration == duration)
    dff = dff.filter(dff.Strike_Pct == strike_pct)
    dff = dff.filter(dff.Training_Key == training_key_index)

    dff_ex = dff.extract()
    exp_prices = dff_ex['Expiration_Price'].to_numpy()

    exp_prices = exp_prices / current_price

    pdf_payout_and_hist_fig = make_subplots(specs=[[{"secondary_y": True}]])
    pdf_payout_and_hist_fig.add_trace(go.Scatter(x=pdf_x, y=pdf_y,
                                                 mode='lines',
                                                 name='Price PDF'), secondary_y=False)
    pdf_payout_and_hist_fig.add_trace(go.Scatter(x=pdf_x, y=odds,
                                                 mode='lines',
                                                 name='Put Payout'), secondary_y=True)
    pdf_payout_and_hist_fig.update_xaxes(range=[0.0, 2.0])

    pdf_payout_and_hist_fig.add_trace(go.Histogram(
        x=exp_prices,
        # nbinsx=num_hist_bins,
        xbins=dict(
            start=0.0,
            end=2.0,
            size=2.0 / num_hist_bins
        ),
        opacity=0.6,
        histnorm='probability density',
        name='Price Path Distribution'
    ), secondary_y=False)

    pdf_payout_and_hist_fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    pdf_payout_and_hist_fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Price at Expiration (Relative to Current Price)'
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    pdf_payout_and_hist_fig.update_yaxes(title_text='Probability Density', secondary_y=False)
    pdf_payout_and_hist_fig.update_yaxes(title_text='Profit and Loss (%)', secondary_y=True)

    user_bankroll_fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Number of Days',
        yaxis_title='Bankroll Amount',
        showlegend=False
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    opt_bankroll_fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Number of Days',
        yaxis_title='Bankroll Amount',
        showlegend=False
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    user_cagr_fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Number of Days',
        yaxis_title='CAGR (%)',
        title='CAGR Expected: {}'.format(expected_cagr),
        showlegend=False
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)
    user_cagr_fig.update_yaxes(range=[-100.0, 300.0])

    opt_cagr_fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Number of Days',
        yaxis_title='CAGR (%)',
        title='CAGR Expected: {}'.format(expected_cagr),
        showlegend=False
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)
    opt_cagr_fig.update_yaxes(range=[-100.0, 300.0])

    user_util_fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Number of Days',
        yaxis_title='Util Used',
        showlegend=False
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    opt_util_fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Number of Days',
        yaxis_title='Util Used',
        showlegend=False
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    user_amt_fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Number of Days',
        yaxis_title='Amount of Contracts Traded',
        showlegend=False
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    opt_amt_fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Number of Days',
        yaxis_title='Amount of Contracts Traded',
        showlegend=False
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    median_start_user_amts = np.median(start_user_amts)
    median_start_opt_amts = np.median(start_opt_amts)
    median_final_user_amts = np.median(final_user_amts)
    median_final_opt_amts = np.median(final_opt_amts)
    user_low_bound = 0.0
    user_up_bound = np.max([median_final_user_amts * 3.0, median_start_user_amts * 3.0])
    opt_low_bound = 0.0
    opt_up_bound = np.max([median_final_opt_amts * 3.0, median_start_opt_amts * 3.0])

    user_amt_fig.update_yaxes(range=[user_low_bound, user_up_bound])
    opt_amt_fig.update_yaxes(range=[opt_low_bound, opt_up_bound])

    if plot_filename_dict is not None:

        if 'user_br' in plot_filename_dict:
            user_bankroll_fig.write_image(
                plot_filename_dict['user_br'](key, strike_pct, duration))

        if 'opt_br' in plot_filename_dict:
            opt_bankroll_fig.write_image(
                plot_filename_dict['opt_br'](key, strike_pct, duration))

        if 'user_cagr' in plot_filename_dict:
            user_cagr_fig.write_image(
                plot_filename_dict['user_cagr'](key, strike_pct, duration))

        if 'opt_cagr' in plot_filename_dict:
            opt_cagr_fig.write_image(
                plot_filename_dict['opt_cagr'](key, strike_pct, duration))

        if 'user_util' in plot_filename_dict:
            user_util_fig.write_image(
                plot_filename_dict['user_util'](key, strike_pct, duration))

        if 'opt_util' in plot_filename_dict:
            opt_util_fig.write_image(
                plot_filename_dict['opt_util'](key, strike_pct, duration))

        if 'user_amt' in plot_filename_dict:
            user_amt_fig.write_image(
                plot_filename_dict['user_amt'](key, strike_pct, duration))

        if 'opt_amt' in plot_filename_dict:
            opt_amt_fig.write_image(
                plot_filename_dict['opt_amt'](key, strike_pct, duration))

        if 'pdf_and_pay' in plot_filename_dict:
            pdf_payout_and_hist_fig.write_image(
                plot_filename_dict['pdf_and_pay'](key, strike_pct, duration))

    return (performance_dict, user_bankroll_fig, opt_bankroll_fig, user_cagr_fig, opt_cagr_fig,
            user_util_fig, opt_util_fig, user_amt_fig, opt_amt_fig, pdf_payout_and_hist_fig,
            current_count)


def create_backtesting_plots(log_file_name, bt_dict, util, num_paths, plot_progress_bar=None,
                             plot_filename_dict=None):
    """
    Opens the backtesting log file and iterates over all of the backtesting scenarios
    which were simulated, and generates plots for each to be displayed on the UI

    Parameters
    ----------
    log_file_name : str
        The name of the log file containing the backtesting results
    bt_dict : dict
        A dict containing results from backtesting
    util : float
        The util used for backtesting
    num_paths : int
        The number of paths that were simulated
    plot_progress_bar : streamlit.progress
        A progress bar to update the UI on plot generation status
    plot_filename_dict : dict
        (Optional. Default: None) A dict containing function lambdas that control the
        filenames of all the plots. By default no plots are saved

    Returns
    -------
    performace_df : pandas.DataFrame
        A DF containing performance statistics
    plot_dicts : List[dict]
        A List of dicts containing plotly figures
    """
    keys = bt_dict['keys']
    pdf_df = bt_dict['pdf']
    curve_df = bt_dict['curves']
    training_df = bt_dict['training']

    # Make unique
    exps = list(set(curve_df.Expiration.tolist()))
    strike_pcts = list(set(curve_df.StrikePercent.tolist()))
    exps.sort()
    strike_pcts.sort()

    # print('Exps: {}'.format(exps))
    # print('Strikes: {}'.format(strike_pcts))

    total_num_tasks = len(keys) * len(exps) * len(strike_pcts) * num_paths

    df = vaex.open(log_file_name + '.hdf5')

    performance_dict_list = []

    plot_dicts = []
    current_count = 0
    # Loop over all the training data scenarios
    for key_index, key in enumerate(keys):

        # print('key_index: {} key: {}'.format(key_index, key))

        # Loop over durations
        for duration_index, duration in enumerate(exps):

            # Get the arrays of the PDF function
            pdf_x_vals = pdf_df['Prices'].to_numpy()
            pdf_y_vals = pdf_df[key + '|' + str(duration)]

            # Loop over strikes and store the histories along the path
            for strike_index, strike_pct in enumerate(strike_pcts):
                # print('key: {} duration: {} strike_pct: {}'.format(key, duration, strike_pct))

                ticker = get_ticker_from_key(key)
                label = get_sentiment_label_from_key(key)
                query_str = 'Ticker == "{}" and Label == "{}" and ' \
                            'Expiration == {} and StrikePercent == {}'.format(ticker, label,
                                                                              duration, strike_pct)
                logging.debug('Plotting Results for: {}'.format(query_str))

                results = curve_df.query(query_str)

                training_query = 'Ticker == "{}" and Label == "{}"'.format(ticker, label)
                t_results = training_df.query(training_query)

                current_price = t_results.CurrentPrice.values[0]

                # print(results)
                # print(results.bet_fractions)

                bet_fractions = results.bet_fractions.values[0]
                curve_points = results.curve_points.values[0]

                # Get the premium amount at util for plotting payout
                idx = (np.abs(bet_fractions - util)).argmin()
                prem = curve_points[idx]

                cfg = PayoffConfigBuilder().set_x_points(pdf_x_vals).add_option_leg(
                    'put', 'short', 1.0, strike_pct).build_config()
                configure_payoff(cfg)
                odds = get_payoff_odds(prem)

                (performance_dict, user_bankroll_fig, opt_bankroll_fig, user_cagr_fig,
                 opt_cagr_fig, user_util_fig, opt_util_fig, user_amt_fig, opt_amt_fig,
                 pdf_payout_and_hist_fig, out_count) = create_backtesting_scenario_plots(
                    df, key, util, key_index, duration, strike_pct, num_paths,
                    pdf_x_vals, pdf_y_vals, odds, current_price,
                    plot_progress_bar=plot_progress_bar, current_count=current_count,
                    total_tasks=total_num_tasks, plot_filename_dict=plot_filename_dict)

                # Update for future loops
                current_count = out_count

                plot_dicts.append({
                    'user_br': user_bankroll_fig,
                    'opt_br': opt_bankroll_fig,
                    'user_cagr': user_cagr_fig,
                    'opt_cagr': opt_cagr_fig,
                    'user_util': user_util_fig,
                    'opt_util': opt_util_fig,
                    'user_amt': user_amt_fig,
                    'opt_amt': opt_amt_fig,
                    'pdf_and_pay': pdf_payout_and_hist_fig
                })

                # print(performance_dict)
                performance_dict_list.append(performance_dict)

    if plot_progress_bar is not None:
        plot_progress_bar.progress(1.0)

    # Clean up the memory map we were reading from
    df.close()
    del df

    performace_df = pd.DataFrame(performance_dict_list)
    performace_df.to_csv(log_file_name + '_performance.csv', index=False)

    return performace_df, plot_dicts

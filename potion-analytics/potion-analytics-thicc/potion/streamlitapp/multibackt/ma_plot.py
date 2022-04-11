"""
This module provides the plots which the portfolio backtesting tool produces for the GUI
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import vaex
from scipy.stats import multivariate_normal

from itertools import combinations
from potion.streamlitapp.backt.bt_utils import calculate_max_drawdown
from potion.curve_gen.training.distributions.multivariate_students_t import MultiVarStudentT
from potion.curve_gen.payoff.builder import PayoffConfigBuilder
from potion.curve_gen.payoff.payoff import (configure_payoff, get_payoff_odds)
from potion.backtest.multi_asset_backtester import PathGenMethod


def calculate_marginal_pdf(deltas, axes, marginal_axis_index, probs):
    """
    Takes an N-dimensional PDF and calculates the marginal PDF along a specified axis

    Parameters
    ----------
    deltas : List[float]
        A list of the deltas along each axis (dx, dy, etc.) length N
    axes : List[numpy.ndarray]
        A list of axes length N, where each axis is an array of points delta apart
    marginal_axis_index : int
        The index of the axis we want to calculate the marginal PDF. Must be between 0 and N
    probs : numpy.ndarray
        The N-dimensional array containing the N-dimensional PDF values

    Returns
    -------
    marginal_values : List[float]
        The marginal PDF values along the specified axis so that
        plot(axes[marginal_axis_index], marginal_values) would plot the marginal PDF at
        each point along the axis
    """
    # Calculate the area of one element in the N-dimensional grid
    area_of_one_element = 1.0
    for delta in deltas:
        area_of_one_element *= delta

    # Calculate the area of a row in the N-dimensional grid and the
    # slices we need to calculate the marginal PDF
    area_of_row = area_of_one_element
    slice_list = []
    axes_lens = []
    for i, axis in enumerate(axes):

        axes_lens.append(len(axis))
        if i != marginal_axis_index:
            area_of_row *= len(axis)
            slice_list.append(slice(-1))
        else:
            # To be replaced in next loop
            slice_list.append(0)

    # Calculate the marginal PDF values
    marginal_values = []
    probs_reshaped = probs.reshape(tuple(axes_lens))
    for j, value in enumerate(axes[marginal_axis_index]):

        marginal_sum = 0.0

        # Replace the index with the axis we are calculating the marginal distribution for
        slice_list[marginal_axis_index] = j

        # Create the multidimensional index slice from the list of slices
        prob_index = tuple(s for s in slice_list)

        # Sum to get the marginal probability and divide by the area of a 'row' to get the density
        marginal_sum += np.sum(probs_reshaped[prob_index] * area_of_one_element)
        marginal_values.append(marginal_sum / area_of_row)
    return marginal_values


def plot_multi_asset_paths(backtester, path_length, progress_bar_count, paths_to_plot=300):
    """
    Generates all of the output plots related to the multiple asset backtesting.
    These plots include the 2-D marginal return distributions and the simulated
    path plots for each asset

    Parameters
    ----------
    backtester : MultiAssetBacktester
        The backtester object containing the results of the simulation
    path_length : int
        The length of the generated backtesting path
    progress_bar_count : int
        The current count for the progress bar
    paths_to_plot : int
        The number of paths to include in the image

    Returns
    -------
    marginal_distributions_by_curve : dict
        The marginal distributions for each curve to use with the payout plot
    two_d_fig_map : dict
        The map of each 2-D marginal distribution plot
    path_figure_map : dict
        The map of each path plot to each asset
    progress_bar_count : int
        An updated count for the progress bar
    """
    cov_matrix = backtester.covariance_matrix
    asset_list = cov_matrix.columns

    # Get all combinations of two for the assets
    combos = combinations(asset_list, 2)

    # print(cov_matrix)

    mean_matrix = []
    scale_matrix = []
    asset_map = {}
    for i, param_dict in enumerate(backtester.asset_params):
        mean_matrix.append(param_dict['loc'])
        scale_matrix.append(param_dict['scale'])
        asset_map[param_dict['key']] = i

    # Get the frozen function
    # print(mean_matrix)

    if backtester.path_gen_method == PathGenMethod.MV_NORMAL:
        rv = multivariate_normal(mean_matrix, cov_matrix)
    elif backtester.path_gen_method == PathGenMethod.MV_STUDENT_T:
        rv = MultiVarStudentT(mean_matrix, cov_matrix, 2.5)
    else:
        raise ValueError('Unknown Path Generation Method')

    num_dimensions = len(mean_matrix)
    delta = 0.001
    ax_limits = [-0.2, 0.2]

    slice_list = []
    axes_deltas = []
    axes = []
    for i in range(num_dimensions):
        slice_list.append(slice(ax_limits[0], ax_limits[1], delta))
        axes_deltas.append(delta)
        axes.append(np.arange(ax_limits[0], ax_limits[1], delta))

    mgrid_index = tuple(s for s in slice_list)

    grid = np.mgrid[mgrid_index]

    pos = grid.reshape((num_dimensions, -1)).T

    probs = rv.pdf(pos)

    marginal_dist_dict = {}
    for i in range(num_dimensions):
        marginal_values = calculate_marginal_pdf(axes_deltas, axes, i, probs)
        marginal_dist_dict[i] = axes[i]
        marginal_dist_dict['m{}'.format(i)] = marginal_values

    # print('Asset combos:')

    two_d_fig_map = {}
    for combo in combos:
        # print(combo)

        asset_0 = combo[0]
        asset_1 = combo[1]
        asset_index_0 = asset_map[asset_0]
        asset_index_1 = asset_map[asset_1]
        mean_0 = mean_matrix[asset_index_0]
        mean_1 = mean_matrix[asset_index_1]

        cov_00 = cov_matrix.iloc[asset_index_0, asset_index_0]
        cov_01 = cov_matrix.iloc[asset_index_0, asset_index_1]
        cov_10 = cov_matrix.iloc[asset_index_1, asset_index_0]
        cov_11 = cov_matrix.iloc[asset_index_1, asset_index_1]

        two_asset_cov_matrix = {asset_0: [cov_00, cov_10], asset_1: [cov_01, cov_11]}
        two_asset_cov_matrix = pd.DataFrame(two_asset_cov_matrix)
        two_asset_cov_matrix = two_asset_cov_matrix.rename(index={0: asset_0, 1: asset_1})

        # print(two_asset_cov_matrix.to_string())

        # Get the frozen function
        if backtester.path_gen_method == PathGenMethod.MV_NORMAL:
            ta_rv = multivariate_normal([mean_0, mean_1], two_asset_cov_matrix)
        elif backtester.path_gen_method == PathGenMethod.MV_STUDENT_T:
            ta_rv = MultiVarStudentT([mean_0, mean_1], two_asset_cov_matrix, 2.5)
        else:
            raise ValueError('Unknown Path Generation Method')

        ta_slice_list = []
        for i in range(2):
            delta = 0.001
            ax_limits = [-0.2, 0.2]
            ta_slice_list.append(slice(ax_limits[0], ax_limits[1], delta))

        ta_mgrid_index = tuple(s for s in ta_slice_list)
        ta_grid = np.mgrid[ta_mgrid_index]
        ta_pos = np.dstack(ta_grid)
        ta_probs = ta_rv.pdf(ta_pos)

        # make the args dict for Surface
        args = {
            'z': ta_probs,
            'x': marginal_dist_dict[asset_index_0],
            'y': marginal_dist_dict[asset_index_1]
        }

        fig = go.Figure()
        surf = go.Surface(**args)
        fig.add_trace(surf)

        fig.update_layout(
            scene=dict(
                xaxis=dict(
                    nticks=20,
                    range=[-0.2, 0.2]
                ),
                xaxis_title='{}'.format(asset_0),
                yaxis=dict(
                    nticks=20,
                    range=[-0.2, 0.2]
                ),
                yaxis_title='{}'.format(asset_1),
                zaxis_title='Probability Density',

            ),
            title='Asset Return PDF {} vs. {}'.format(asset_0, asset_1),
            width=800,
            height=800,
            autosize=False
        )

        fig.update_traces(showscale=False)
        two_d_fig_map[combo] = fig

    # Number of days along the path for plotting
    days = np.linspace(0, path_length - 1, path_length)

    # Loop over all the training data scenarios
    path_figure_map = {}
    marginal_distributions_by_curve = {}
    for index, row in backtester.curve_df.iterrows():

        asset = row.Asset
        curve_id = row.Curve_ID

        asset_index = asset_map[asset]
        marginal_distributions_by_curve[curve_id] = {
            'x': marginal_dist_dict[asset_index],
            'y': marginal_dist_dict['m{}'.format(asset_index)],
            'mu': mean_matrix[asset_index],
            'scale': scale_matrix[asset_index]
        }

        # Get all of the paths for the simulation
        paths_for_asset = backtester.path_mapping[curve_id]

        # If a figure already exists for this asset, skip
        if asset in path_figure_map:
            continue

        # Create a figure for each separate asset
        fig = go.Figure()

        # Plot each path
        final_price = []
        for i, path in enumerate(paths_for_asset):
            if i < paths_to_plot:

                fig.add_trace(go.Scatter(x=days, y=path,
                                         mode='lines',
                                         name='Price Path #{}'.format(i)))
                final_price.append(path[-1])
                progress_bar_count += 1

        fig.update_layout(
            title='{} Simulated Backtesting Paths'.format(asset),
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

        fig.update_yaxes(range=[low_bound, up_bound])

        path_figure_map[asset] = fig

    return marginal_distributions_by_curve, two_d_fig_map, path_figure_map, progress_bar_count


def create_backtesting_performance_plots(results_df, backtest_id, num_paths, curve_ids,
                                         num_paths_to_plot=300, plot_progress_bar=None,
                                         progress_bar_count=None, total_num_plot_tasks=None):
    """
    Generates the performance plots for multi asset backtesting from the backtesting results.
    This includes the bankroll, CAGR plots, amounts, and util plots for the curve tested
    in the simulation

    Parameters
    ----------
    results_df : vaex.core.dataframe
        The Vaex dataframe containing the log results of the backtest
    backtest_id : int
        The ID number identifying the backtest
    num_paths : int
        The number of paths in the backtesting simulation
    curve_ids : List[int]
        The ID numbers for the curves being tested in the backtesting simulation
    num_paths_to_plot : int
        The number of paths to include in the plots
    plot_progress_bar : streamlit.progress
        The progress bar on the streamlit UI which is updated as progress is made
    progress_bar_count : int
        The count tracking plot_progress_bar progress between calls of this function
    total_num_plot_tasks: int
        The total number of calls to this function which will be made by the main plotting function

    Returns
    -------
    performance_dict : dict
        A dict containing performance results
    user_bankroll_fig : plotly.graph_object.Figure
        The plotly Figure containing the user's bankroll
    opt_bankroll_fig : plotly.graph_object.Figure
        The plotly Figure containing the minimum curve bankroll
    user_cagr_fig : plotly.graph_object.Figure
        The plotly Figure containing the user's CAGR
    opt_cagr_fig : plotly.graph_object.Figure
        The plotly Figure containing the minimum curve CAGR
    user_util_figs : dict
        Dict containing the util for each asset for the user
    opt_util_figs : dict
        Dict containing the util for each asset for minimum curve
    user_amt_figs : dict
        Dict containing amounts for each asset for the user
    opt_amt_figs : dict
        Dict containing amounts for each asset for minimum curve
    progress_bar_count : int
        An updated count for the progress bar
    """
    user_bankroll_fig = go.Figure()
    opt_bankroll_fig = go.Figure()
    user_cagr_fig = go.Figure()
    opt_cagr_fig = go.Figure()

    user_util_figs = {}
    opt_util_figs = {}
    user_amt_figs = {}
    opt_amt_figs = {}

    for curve_id in curve_ids:
        user_util_fig = go.Figure()
        opt_util_fig = go.Figure()
        user_amt_fig = go.Figure()
        opt_amt_fig = go.Figure()

        start_user_amts = []
        start_opt_amts = []
        final_user_amts = []
        final_opt_amts = []

        user_util_figs[curve_id] = user_util_fig
        opt_util_figs[curve_id] = opt_util_fig
        user_amt_figs[curve_id] = {
            'f': user_amt_fig,
            's': start_user_amts,
            'e': final_user_amts
        }
        opt_amt_figs[curve_id] = {
            'f': opt_amt_fig,
            's': start_opt_amts,
            'e': final_opt_amts
        }

    start_user_cagrs = []
    start_opt_cagrs = []
    final_user_cagrs = []
    final_opt_cagrs = []

    user_max_dd_per_path = []
    opt_max_dd_per_path = []

    # rdff = results_df.filter(getattr(results_df, '{}_Training_Key'.format(curve_id)) == curve_id)
    # rdff = rdff.filter(getattr(rdff, '{}_Exp_Duration'.format(curve_id)) == duration)
    # rdff = rdff.filter(getattr(rdff, '{}_Strike_Pct'.format(curve_id)) == strike_pct)

    for path_id in range(num_paths):

        rdff = results_df.filter(results_df.Path_ID == path_id)

        results = rdff.extract()

        if plot_progress_bar is not None and progress_bar_count is not None and \
                total_num_plot_tasks is not None:

            val = progress_bar_count / float(total_num_plot_tasks)
            plot_progress_bar.progress(val)
            # Add the number of plots created for this path
            progress_bar_count += 2 + 2 * len(curve_ids)

        days = np.unique(results['Timestamp'].to_numpy())

        user_bankroll = results['User_Bankroll'].to_numpy()
        user_bankroll = user_bankroll[user_bankroll != 0]

        opt_bankroll = results['Opt_Bankroll'].to_numpy()
        opt_bankroll = opt_bankroll[opt_bankroll != 0]

        user_cagr = results['User_CAGR'].to_numpy()
        user_cagr = user_cagr[user_cagr != 0]
        user_cagr = user_cagr[user_cagr != np.inf]

        opt_cagr = results['Opt_CAGR'].to_numpy()
        opt_cagr = opt_cagr[opt_cagr != 0]
        opt_cagr = opt_cagr[opt_cagr != np.inf]

        start_user_cagrs.append(user_cagr[0])
        start_opt_cagrs.append(opt_cagr[0])
        final_user_cagrs.append(user_cagr[-1])
        final_opt_cagrs.append(opt_cagr[-1])

        user_maxdd = calculate_max_drawdown(user_bankroll)
        opt_maxdd = calculate_max_drawdown(opt_bankroll)

        user_max_dd_per_path.append(user_maxdd)
        opt_max_dd_per_path.append(opt_maxdd)

        if path_id < num_paths_to_plot:
            user_bankroll_fig.add_trace(go.Scatter(x=days, y=user_bankroll, mode='lines',
                                                   name='Bankroll Path #{}'.format(path_id)))
            opt_bankroll_fig.add_trace(go.Scatter(x=days, y=opt_bankroll, mode='lines',
                                                  name='Bankroll Path #{}'.format(path_id)))
            user_cagr_fig.add_trace(go.Scatter(x=days[1:], y=user_cagr[1:], mode='lines',
                                               name='CAGR Path #{}'.format(path_id)))
            opt_cagr_fig.add_trace(go.Scatter(x=days[1:], y=opt_cagr[1:], mode='lines',
                                              name='CAGR Path #{}'.format(path_id)))

        for curve_id in curve_ids:
            user_util = results['{}_User_Util'.format(curve_id)].to_numpy()[1:]
            opt_util = results['{}_Opt_Util'.format(curve_id)].to_numpy()[1:]
            user_util = user_util[user_util != 0]
            opt_util = opt_util[opt_util != 0]

            user_amts = results['{}_User_Amount'.format(curve_id)].to_numpy()[1:]
            opt_amts = results['{}_Opt_Amount'.format(curve_id)].to_numpy()[1:]
            user_amts = user_amts[user_amts != 0]
            opt_amts = opt_amts[opt_amts != 0]

            user_amt_figs[curve_id]['s'].append(user_amts[0])
            opt_amt_figs[curve_id]['s'].append(opt_amts[0])
            user_amt_figs[curve_id]['e'].append(user_amts[-1])
            opt_amt_figs[curve_id]['e'].append(opt_amts[-1])

            if path_id < num_paths_to_plot:
                user_util_figs[curve_id].add_trace(go.Scatter(
                    x=days[1:], y=user_util, mode='lines', name='Util Path #{}'.format(path_id)))
                opt_util_figs[curve_id].add_trace(go.Scatter(
                    x=days[1:], y=opt_util, mode='lines', name='Util Path #{}'.format(path_id)))
                user_amt_figs[curve_id]['f'].add_trace(go.Scatter(
                    x=days[1:], y=user_amts, mode='lines', name='Amount Path #{}'.format(path_id)))
                opt_amt_figs[curve_id]['f'].add_trace(go.Scatter(
                    x=days[1:], y=opt_amts, mode='lines', name='Amount Path #{}'.format(path_id)))

    # start_user_cagr_arr = np.asarray(start_user_cagrs)
    # start_opt_cagr_arr = np.asarray(start_opt_cagrs)
    user_cagr_arr = np.asarray(final_user_cagrs)
    opt_cagr_arr = np.asarray(final_opt_cagrs)
    user_maxdd_arr = np.asarray(user_max_dd_per_path)
    opt_maxdd_arr = np.asarray(opt_max_dd_per_path)

    performance_dict = {
        'backtest_id': backtest_id,
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
        showlegend=False
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    opt_cagr_fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Number of Days',
        yaxis_title='CAGR (%)',
        showlegend=False
    ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    # median_start_user_cagrs = np.median(start_user_cagr_arr)
    # median_start_opt_cagrs = np.median(start_opt_cagr_arr)
    median_final_user_cagrs = np.median(user_cagr_arr)
    median_final_opt_cagrs = np.median(opt_cagr_arr)
    # user_up_bound = np.max([median_final_user_cagrs * 3.0, median_start_user_cagrs * 3.0])
    # opt_up_bound = np.max([median_final_opt_cagrs * 3.0, median_start_opt_cagrs * 3.0])
    user_up_bound = median_final_user_cagrs * 3.0
    opt_up_bound = median_final_opt_cagrs * 3.0

    user_cagr_fig.update_yaxes(range=[-100.0, user_up_bound])
    opt_cagr_fig.update_yaxes(range=[-100.0, opt_up_bound])

    for curve_id in curve_ids:

        user_util_figs[curve_id].update_layout(
            plot_bgcolor='rgb(230,230,230)',
            xaxis_title='Number of Days',
            yaxis_title='Util Used',
            showlegend=False
        ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

        opt_util_figs[curve_id].update_layout(
            plot_bgcolor='rgb(230,230,230)',
            xaxis_title='Number of Days',
            yaxis_title='Util Used',
            showlegend=False
        ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

        user_amt_figs[curve_id]['f'].update_layout(
            plot_bgcolor='rgb(230,230,230)',
            xaxis_title='Number of Days',
            yaxis_title='Amount of Contracts Traded',
            showlegend=False
        ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

        opt_amt_figs[curve_id]['f'].update_layout(
            plot_bgcolor='rgb(230,230,230)',
            xaxis_title='Number of Days',
            yaxis_title='Amount of Contracts Traded',
            showlegend=False
        ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

        median_start_user_amts = np.median(user_amt_figs[curve_id]['s'])
        median_start_opt_amts = np.median(opt_amt_figs[curve_id]['s'])
        median_final_user_amts = np.median(user_amt_figs[curve_id]['e'])
        median_final_opt_amts = np.median(opt_amt_figs[curve_id]['e'])
        user_low_bound = 0.0
        user_up_bound = np.max([median_final_user_amts * 3.0, median_start_user_amts * 3.0])
        opt_low_bound = 0.0
        opt_up_bound = np.max([median_final_opt_amts * 3.0, median_start_opt_amts * 3.0])

        user_amt_figs[curve_id]['f'].update_yaxes(range=[user_low_bound, user_up_bound])
        opt_amt_figs[curve_id]['f'].update_yaxes(range=[opt_low_bound, opt_up_bound])

    return (performance_dict, user_bankroll_fig, opt_bankroll_fig, user_cagr_fig,
            opt_cagr_fig, user_util_figs, opt_util_figs, user_amt_figs, opt_amt_figs,
            progress_bar_count)


def create_pdf_and_payout_plots(results_df, curve_id, strike_pct, duration,
                                util, bet_fractions, curve_points, pdf_df, current_price,
                                marginal_dist_list, num_hist_bins=200):
    """
    This function filters the log file DF for the needed results of the backtesting
    simulation for a specific curve and generates 9 Plotly plots containing the results.

    Parameters
    ----------
    results_df : vaex.core.dataframe
        The Vaex DF containing the backtesting log file
    curve_id : int
        An ID number identifying the curve which was being tested
    strike_pct : float
        The strike price of the contract in percent of the ATM price
    duration : int
        The number of days until the expiration of the contract
    util : float
        The util used in the backtesting simulation
    bet_fractions: numpy.ndarray
        The array of bet fractions containing sample points on the x axis of the curve
    curve_points : numpy.ndarray
        The array containing the curve values (y axis) at the sample points bet_fractions
    pdf_df : pandas.DataFrame
        Dataframe containing the distributions which were used to generate the curves in
        the curve generator
    current_price : float
        The starting price for the asset path
    marginal_dist_list : List[numpy.ndarray]
        The list of marginal distributions of the backtester path generation distribution
    num_hist_bins : int
        The number of bins to include in the histogram of path prices

    Returns
    -------
    pdf_payout_and_hist_fig : plotly.graph_object.Figure
        The plotly figure containing the PDF, payout, and price histogram
    """
    # Filter the log df to find the expiration prices to make the histogram
    dff = results_df.filter(results_df.Timestamp == duration)
    dff = dff.filter(dff['{}_Exp_Duration'.format(curve_id)] == duration)
    dff = dff.filter(dff['{}_Strike_Pct'.format(curve_id)] == strike_pct)
    dff = dff.filter(dff['{}_Training_Key'.format(curve_id)] == curve_id)

    dff_ex = dff.extract()

    col_name = '{}_Price'.format(curve_id)
    exp_prices = getattr(dff_ex, col_name)

    exp_prices = exp_prices.to_numpy()

    exp_prices = exp_prices / current_price

    # Get the arrays of the PDF function
    pdf_x_vals = pdf_df['Prices']
    pdf_y_vals = None
    for col_name in pdf_df.columns:
        # print(col_name)
        col_arr = col_name.split('|')

        if len(col_arr) > 1:
            col_duration = int(col_arr[1])

            if col_duration == duration:
                # pdf_y_vals = pdf_df[asset + '|' + str(duration)]
                pdf_y_vals = pdf_df[col_name]
                break

    # Get the premium amount at specified util for plotting payout
    idx = (np.abs(bet_fractions - util)).argmin()
    prem = curve_points[idx]

    # Calculate the payout function for plot
    x_values = np.linspace(0.000001, 2.0, 20000)
    cfg = PayoffConfigBuilder().set_x_points(x_values).add_option_leg(
        'put', 'short', 1.0, strike_pct).build_config()
    configure_payoff(cfg)
    odds = get_payoff_odds(prem)

    pdf_payout_and_hist_fig = make_subplots(specs=[[{"secondary_y": True}]])
    pdf_payout_and_hist_fig.add_trace(go.Scatter(x=pdf_x_vals, y=pdf_y_vals,
                                                 mode='lines',
                                                 name='Single Asset PDF'), secondary_y=False)
    pdf_payout_and_hist_fig.add_trace(go.Scatter(x=x_values, y=odds,
                                                 mode='lines',
                                                 name='Put Payout'), secondary_y=True)
    # pdf_payout_and_hist_fig.add_trace(go.Scatter(x=price_points, y=marginal_price_pdf,
    #                                              mode='lines',
    #                                              name='Backtester Marginal PDF'))
    pdf_payout_and_hist_fig.update_xaxes(range=[0.0, 2.0])

    pdf_payout_and_hist_fig.add_trace(go.Histogram(
        x=exp_prices,
        xbins=dict(
            start=0.0,
            end=2.0,
            size=2.0 / num_hist_bins
        ),
        opacity=0.6,
        histnorm='probability density',
        name='Multi Asset Histogram'
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

    return pdf_payout_and_hist_fig


def create_backtesting_plots(backtester_id, backtester, log_file_name, pdf_df, marginal_dist_list,
                             num_paths, progress_bar_count, total_num_plot_tasks,
                             plot_progress_bar=None):
    """
    Opens the backtesting log file and iterates over all of the backtesting scenarios which
    were simulated, and generates plots for each to be displayed on the UI

    Parameters
    ----------
    backtester_id : int
        An ID number identifying the backtester run
    backtester : MultiAssetBacktester
        The backtester object containing all of the results
    log_file_name : str
        The name of the log file containing the backtesting results
    pdf_df : pandas.DataFrame
        A Dataframe containing the PDFs used during curve generation (for plot comparison)
    marginal_dist_list : List[numpy.ndarray]
        The list of marginal distributions of the backtester path generation distribution
    num_paths : int
        The number of paths that were simulated in the backtest
    progress_bar_count : int
        The current count of the progress bar
    total_num_plot_tasks : int
        The total number of plots to create
    plot_progress_bar : streamlit.progress
        A progress bar to update the UI on plot generation status

    Returns
    -------
    performance_dict : dict
        A dict containing the performance info from the backtests
    plot_dicts : List
        A List containing the dicts of the plotly figures
    pdf_payout_figs : dict
        Maps curve id number to plotly Figure
    progress_bar_count : int
        An updated count for the progress bar
    """
    curve_ids = backtester.curve_df.Curve_ID.values

    df = vaex.open(log_file_name + '.hdf5')

    # print('Opening: {}'.format(log_file_name + '.hdf5'))

    num_hist_bins = 200
    num_paths_to_plot = 300

    # Loop over all the contracts
    pdf_payout_figs = {}
    for i, row in backtester.curve_df.iterrows():

        curve_id = row.Curve_ID
        curve_asset = row.Asset
        bet_fractions = row.bet_fractions
        curve_points = row.curve_points
        util = backtester.util_map[curve_id]
        strike_pct = row.StrikePercent
        duration = row.Expiration
        current_price = backtester.current_price_map[curve_asset]

        pdf_payout_and_hist_fig = create_pdf_and_payout_plots(
            df, curve_id, strike_pct, duration, util, bet_fractions,
            curve_points, pdf_df, current_price, marginal_dist_list, num_hist_bins=num_hist_bins)

        progress_bar_count += 1

        pdf_payout_figs[curve_id] = pdf_payout_and_hist_fig

    (performance_dict, user_bankroll_fig, opt_bankroll_fig, user_cagr_fig,
     opt_cagr_fig, user_util_figs, opt_util_figs, user_amt_figs, opt_amt_figs,
     progress_bar_count) = create_backtesting_performance_plots(
        df, backtester_id, num_paths, curve_ids, num_paths_to_plot,
        plot_progress_bar, progress_bar_count, total_num_plot_tasks)

    plot_dicts = [
        user_bankroll_fig, opt_bankroll_fig, user_cagr_fig, opt_cagr_fig, user_util_figs,
        opt_util_figs, user_amt_figs, opt_amt_figs
    ]

    return performance_dict, plot_dicts, pdf_payout_figs, progress_bar_count


def calc_total_num_plot_tasks(backtester_map):
    """
    Calculates the total number of plots that need to be created for a backtesting batch

    Parameters
    ----------
    backtester_map : dict
        Matches backtester_id to a backtester object

    Returns
    -------
    total_tasks : int
        The total number of tasks
    """
    total_tasks = 0
    for backtest_id, backtester in backtester_map.items():

        cov_matrix = backtester.covariance_matrix
        asset_list = cov_matrix.columns

        num_curves = len(backtester.curve_df)
        num_assets = len(asset_list)
        num_paths = backtester.num_paths
        num_2d_return_pdfs = len(list(combinations(asset_list, 2)))

        num_backtester_tasks = (num_2d_return_pdfs +  # the 2d return distributions
                                num_curves +  # the PDF and payout plots
                                num_assets * num_paths +  # the backtester paths
                                num_paths +  # the bankroll plot
                                num_paths +  # the cagr plot
                                num_curves * num_paths +  # the util plots
                                num_curves * num_paths)  # the amount plots
        total_tasks += num_backtester_tasks

    return total_tasks

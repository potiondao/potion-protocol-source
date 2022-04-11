"""
This module provides the backend code for the backtesting tool and implements the calls from
the GUI to the backtesting library. These functions primarily provide the inputs from the GUI in
the format the library expects and provides the outputs of the library in the format the
GUI expects.
"""
import time
import pandas as pd
import os
import sys
import logging
from pathlib import Path

# Add the root to the path so we can import our potion files from a jupyter
module_path = os.path.abspath(os.path.join('.'))

if module_path not in sys.path:
    sys.path.append(module_path)
# print('Current Module Path: {}'.format(module_path))

from potion.backtest.batch_backtester import BatchBacktester, create_backtester_config

from potion.streamlitapp.curvegen.cg_file_io import (read_pdfs_from_csv, read_curves_from_csv,
                                                     read_training_data_from_csv)
from potion.streamlitapp.backt.bt_plot import create_backtesting_plots


def merge_performance_dfs(utils, res_dir):
    """
    Merges the DFs containing performance statistics stored in each util spreadsheet and returns it
    to the function caller

    Parameters
    ----------
    utils : List[float]
        List of utils there were simulations for
    res_dir : str
        (Optional. Default: './batch_results') The directory in which to save plot results

    Returns
    -------
    full_df : pandas.DataFrame
        The merged performance DF
    """
    full_df = pd.DataFrame()
    for u in utils:
        perf_log_file_name = res_dir + 'backtest_u{}_performance.csv'.format(u)

        df = pd.read_csv(perf_log_file_name, sep=',')
        full_df = pd.concat([full_df, df])
        os.remove(perf_log_file_name)

    full_df = full_df.reset_index(drop=True)

    full_df = full_df.sort_values(['duration', 'strike'], ascending=[True, True])
    full_df.to_csv(res_dir + 'backtest_performance.csv', index=False)

    return full_df


def do_backtest(log_file_name, curve_filename, training_filename, pdf_filename, util, method,
                num_paths, path_length, initial_bankroll, progress_bar=None):
    """
    This function creates a batch backtester object and runs the full batch simulation.
    A dict containing results info is returned to the caller of the function.

    Parameters
    ----------
    log_file_name : str
        The name of the backtesting log file
    curve_filename : str
        The name of the CSV file containing the curve info from the curve generation
    training_filename : str
        The name of the CSV file containing the training info from the curve generation
    pdf_filename : str
        The name of the CSV file containing the PDF info from the curve generation
    util : float
        The util to use with the batch of simulations
    method : PathGenMethod
        Enum specifies the statistical distribution used to generate backtesting paths
    num_paths : int
        The number of paths to simulate in the backtest
    path_length : int
        The length of the paths simulated
    initial_bankroll : float
        The initial starting bankroll at the beginning of the simulation
    progress_bar : streamlit.progress
        Specifies a streamlit progressbar to update the UI on progress

    Returns
    -------
    bt_dict : dict
        A dict containing the results information from the backtesting used to generate plots of
        results
    """

    # Read the CSV output from the curve generator and initialize the batch backtesting object
    backtest_config = create_backtester_config(num_paths, path_length, util,
                                               initial_bankroll, path_gen_method=method)

    pdf_df = read_pdfs_from_csv(pdf_filename)
    curve_df = read_curves_from_csv(curve_filename)
    training_df = read_training_data_from_csv(training_filename)

    ticker = training_df.Ticker
    label = training_df.Label

    keys = [x + '-' + y for x, y in zip(ticker, label)]

    backtester = BatchBacktester(config=backtest_config, curve_df=curve_df, training_df=training_df)

    logging.debug('Generating paths')

    backtester.generate_backtesting_paths()

    logging.debug('Running backtest')

    backtester.evaluate_backtest_sequentially(log_file_name, progress_bar=progress_bar)

    bt_dict = {
        'sim_type': True,
        'keys': keys,
        'pdf': pdf_df,
        'curves': curve_df,
        'training': training_df,
        'backtester': backtester
    }
    return bt_dict


def run_backtesting_script(batch, curve_filename, training_filename, pdf_filename, utils, method,
                           num_paths, path_length, initial_bankroll, backtest_progress_bar=None,
                           plot_progress_bar=None):
    """
    Runs the full batch backtesting process and generates the results plots to return to the
    function caller.

    Parameters
    ----------
    batch : int
        An ID number uniquely specifying the batch of results files for this run
    curve_filename : str
        The name of the CSV file containing the curve info from the curve generation
    training_filename : str
        The name of the CSV file containing the training info from the curve generation
    pdf_filename : str
        The name of the CSV file containing the PDF info from the curve generation
    utils : List[float]
        A List of the utils to use with the batch of simulations
    method : PathGenMethod
        Enum specifies the statistical distribution used to generate backtesting paths
    num_paths : int
        The number of paths to simulate in the backtest
    path_length : int
        The length of the paths simulated
    initial_bankroll : float
        The initial starting bankroll at the beginning of the simulation
    backtest_progress_bar : streamlit.progress
        Specifies a streamlit progressbar to update the UI on progress of the backtest
    plot_progress_bar : streamlit.progress
        Specifies a streamlit progressbar to update the UI on progress of the plot creation

    Returns
    -------
    backtester_map : dict
        Maps util simulations to backtester objects for the caller to use
    log_file_names : List[str]
        A List of the names of log files for each util
    full_performance_df : pandas.DataFrame
        The dataframe containing the performance statistics across all of the backtest runs
    plot_dicts_list : List[dict]
        A List of dicts containing plotly figures
    """
    start = time.perf_counter()

    num_paths = int(num_paths)
    path_length = int(path_length)

    res_dir = './batch_results/batch_{}/backtesting/'.format(batch)
    Path(res_dir).mkdir(parents=True, exist_ok=True)

    backtester_map = {}
    log_file_names = []
    plot_dicts_list = []
    for util in utils:
        log_file_name = res_dir + 'backtest_u{}'.format(util)

        bt_dict = do_backtest(log_file_name, curve_filename, training_filename, pdf_filename, util,
                              method, num_paths, path_length, initial_bankroll,
                              progress_bar=backtest_progress_bar)

        performace_df, plot_dicts = create_backtesting_plots(
            log_file_name, bt_dict, util, num_paths, plot_progress_bar=plot_progress_bar)
        backtester_map[util] = bt_dict['backtester']
        log_file_names.append(log_file_name)
        plot_dicts_list.extend(plot_dicts)

    full_performance_df = merge_performance_dfs(utils, res_dir)

    # plot_performance_scatter_plot(batch, full_performance_df)

    end = time.perf_counter()
    logging.debug('Time to complete: {} seconds'.format(end - start))

    return backtester_map, log_file_names, full_performance_df, plot_dicts_list

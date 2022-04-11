"""
This module provides the backend code for the portfolio backtesting tool and implements the
calls from the GUI to the portfolio backtesting library. These functions primarily provide the
inputs from the GUI in the format the library expects and provides the outputs of the library
in the format the GUI expects.
"""
import logging
import time

from potion.backtest.multi_asset_backtester import (
    create_ma_backtester_config, MultiAssetBacktester)


def calculate_max_drawdown(bankroll):
    """
    Calculates the maximum drawdown of a 1-D numpy array

    Parameters
    ----------
    bankroll : numpy.ndarray
        The array representing the betting bankroll

    Returns
    -------
    max_dd : numpy.ndarray
        Maximum drawdown along the path as a percentage
    """
    highest_val_seen = 0.0
    max_drawdown_seen = 0.0
    for value in bankroll:

        if value >= highest_val_seen:
            highest_val_seen = value

        drawdown = (value - highest_val_seen) / highest_val_seen

        if drawdown < max_drawdown_seen:
            max_drawdown_seen = drawdown

    # Return as a percentage
    return max_drawdown_seen * 100.0


def do_backtest(backtest_id, total_num_backtests, log_file_name, util_map, gen_method,
                num_paths, path_length, initial_bankroll, training_df, curve_df, user_alpha,
                cov_df=None, progress_bar=None):
    """
    This function creates a batch backtester object and runs the full batch simulation. A dict
    containing results info is returned to the caller of the function.

    Parameters
    ----------
    backtest_id : int
        ID number corresponding to the backtest being performed
    total_num_backtests : int
        The total number of backtests being performed
    log_file_name : str
        The name of the backtesting log file
    util_map : dict
        A dict mapping an asset key to a util to bet for that asset. Total util must be
        between 0 and 1
    gen_method : PathGenMethod
        Enum specifies the statistical distribution used to generate backtesting paths
    num_paths : int
        The number of paths to simulate in the backtest
    path_length : int
        The length of the paths simulated
    initial_bankroll : float
        The initial starting bankroll at the beginning of the simulation
    training_df : pandas.DataFrame
        A dataframe containing the training data information for the curves being tested
    curve_df : pandas.DataFrame
        A dataframe containing all of the curve information for the curves being tested
    user_alpha : float
        (Optional) User specified custom tail alpha
    cov_df : pandas.DataFrame
        (Optional) Covariance dataframe if user wants to specify a custom covariance for
        path generation
    progress_bar : streamlit.progress
        (Optional) Specifies a streamlit progressbar to update the UI on progress

    Returns
    -------
    backtester : backtester object that was used in the simulation
    """
    config = create_ma_backtester_config(gen_method, num_paths, path_length, util_map,
                                         initial_bankroll)

    result_df = curve_df.query('Backtest_ID == {}'.format(backtest_id))

    backtester = MultiAssetBacktester(config=config, curve_df=result_df,
                                      training_df=training_df, cov_matrix=cov_df,
                                      user_alpha=user_alpha)

    logging.debug('Generating paths')

    backtester.generate_backtesting_paths()

    logging.debug('Running backtest')

    backtester.evaluate_backtest_sequentially(log_file_name, backtest_id, total_num_backtests,
                                              progress_bar=progress_bar)

    logging.debug('Backtesting Complete')

    return backtester


def run_backtesting_script(log_dir, ma_curve_df, training_df, gen_method, num_paths,
                           path_length, initial_bankroll, backtest_util_list, tail_alpha_list,
                           progress_bar=None):
    """
    Runs a full set of backtesting simulations for the specified input parameters

    Parameters
    ----------
    log_dir : str
        The directory in which the log files will be stored
    ma_curve_df : pandas.DataFrame
        The input DataFrame containing the curve info
    training_df : pandas.DataFrame
        The input DataFrame containing the asset training window info
    gen_method : PathGenMethod
        Enum corresponding to the distribution to use to generate backtesting paths
    num_paths : int
        The number of paths to generate in the backtesting simulation
    path_length : int
        The length of each path in the backtesting simulation
    initial_bankroll : float
        The amount of money the user starts with in the simulation
    backtest_util_list : List[dict]
        A List containing each util_map (mapping of asset and util) for each backtesting
        simulation which will be run by this function
    tail_alpha_list : List[float]
        A List containing each user specified custom tail alpha
    progress_bar : streamlit.progress
        A progress bar used to update the UI on the progress of the script

    Returns
    -------
    backtester_map : dict
        A dict mapping the backtester ID number to the backtester object which performed
        the simulation
    """
    start = time.perf_counter()

    num_paths = int(num_paths)
    path_length = int(path_length)
    num_ma_backtests = len(backtest_util_list)

    backtester_map = {}

    for backtest_id, util_map in enumerate(backtest_util_list):

        log_file_name = log_dir + 'ma_backtest_pool_{}'.format(backtest_id)

        user_alpha = tail_alpha_list[backtest_id]
        backtester = do_backtest(backtest_id, num_ma_backtests, log_file_name, util_map,
                                 gen_method, num_paths, path_length, initial_bankroll,
                                 training_df, ma_curve_df, user_alpha, progress_bar=progress_bar)

        backtester_map[backtest_id] = backtester

    if progress_bar is not None:
        progress_bar.progress(1.0)

    end = time.perf_counter()
    logging.debug('Time to complete: {} seconds'.format(end - start))

    return backtester_map

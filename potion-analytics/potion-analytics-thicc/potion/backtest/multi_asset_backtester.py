"""
This module allows the user to run multi asset simulations of generated curves.

Currently, the code only supports simulating short put options.

Results are efficiently stored in a binary log file ending in *.hdf5 using the Vaex library.
Conversion utilities exist within the tool for the user's convenience that will convert these
output files into CSV.
"""
import numpy as np
import logging
import time
import vaex

from multiprocessing import Pool, cpu_count
from enum import Enum

from potion.backtest.path_gen import (prices_to_sample_covariance_matrix,
                                      prices_to_t_covariance_matrix,
                                      multivariate_normal_path_sampling,
                                      multivariate_t_path_sampling)
from potion.backtest.multi_asset_expiration_evaluator import (
    MultiAssetExpirationEvaluator, create_eval_config)

log = logging.getLogger(__name__)

COL_KEY_PRICE_HIST_DATES = 'Master calendar'


class PathGenMethod(Enum):
    """
    An Enum specifying the method to use when generating paths for backtesting
    """
    MV_NORMAL = 0
    """Generate paths based on a multivariate normal distribution"""
    MV_STUDENT_T = 1
    """Generate paths based on a multivariate Student's T distribution"""


TICKER_KEY = 'tickers'
EXP_KEY = 'expiration_days'
STRIKE_KEY = 'strike_percentages'
BET_FRAC_KEY = 'bet_fraction_array'
PATH_GEN_KEY = 'path_generation_method'
NUM_PATHS_KEY = 'number_of_paths'
PATH_LEN_KEY = 'path_length'
UTIL_KEY = 'util'
INIT_BANK_KEY = 'initial_bankroll'
SIM_TYPE_KEY = 'simulation_type'
PAYOFF_TYPE_KEY = 'payoff_type'
PAYOFF_PARAMS = 'payoff_params'


def create_ma_backtester_config(path_gen_method: PathGenMethod, num_paths: int, path_length: int,
                                util_map, initial_bankroll: float):
    """
    Helper function to easily create a configuration object for the backtester

    Parameters
    ----------
    path_gen_method : PathGenMethod
        The distribution to use to generate paths see PathGenMethod enum.
    num_paths : int
        The number of price paths to use in the simulation
    path_length : int
        The number of days to use as the length of the simulated path
    util_map : dict
        Constant util for each asset
    initial_bankroll : float
        The starting capital at the beginning of the simulation

    Returns
    -------
    config : dict
        The config dict
    """
    config = {
        PATH_GEN_KEY: path_gen_method,
        NUM_PATHS_KEY: num_paths,
        PATH_LEN_KEY: path_length,
        UTIL_KEY: util_map,
        INIT_BANK_KEY: initial_bankroll
    }

    return config


def eval_work(curve_ids, duration_dict, strike_percent_dict, path, path_id, util_dict, fit_params,
              initial_bankroll, current_price_dict, bf, ocp, logging_df, row_slice):
    """
    This function processes one set of evaluation work corresponding to a combination of
    key, duration, strike, and path of the backtesting simulation. This function can either
    be called sequentially in a nested for-loop, or in parallel on different processing cores.
    When the processing is complete, the results are returned to be stored in the performance
    mappings of this backtester object

    Parameters
    ----------
    curve_ids : List[int]
        The ID numbers identifying each curve
    duration_dict : dict
        A dict mapping an asset key to a duration representing the number of days between each
        expiration. 1 is every day, 2 every other, etc.
    strike_percent_dict : dict
        A dict mapping an asset key to a strike in percentage ATM  where 1.0 is ATM
    path : List[float]
        The path corresponding to this set of simulation data
    path_id : int
        The index in the array of all paths
    util_dict : dict
        A dict mapping an asset key to a util to bet for that asset. Total util must
        be between 0 and 1
    fit_params : List[float]
        The parameters of the fit to the premium curve
    initial_bankroll : float
        The initial starting bankroll for the simulation
    current_price_dict : dict
        The price we are starting the simulation at for each asset
    bf : numpy.ndarray
        The bet fraction array (X values of curve)
    ocp : numpy.ndarray
        The optimal curve points (Y values of curve)
    logging_df : vaex.dataframe.DataFrame
        The vaex dataframe which is our memory mapped log file
    row_slice : slice
        The row slice for this task

    Returns
    -------
    True
    """
    # Calculate all of the results along the path
    input_dict = create_eval_config(path, util_dict, duration_dict, strike_percent_dict, fit_params,
                                    initial_bankroll, bf, ocp)

    evaluator = MultiAssetExpirationEvaluator(input_dict)

    evaluator.evaluate_expirations_along_path(logging_df, curve_ids, path_id, current_price_dict,
                                              row_slice)

    # Needs to return for async result
    return True


def calculate_row_slices(path_length: int, num_paths, log_length):
    """
    This function calculates the slices of row indices in the log file that correspond to one
    given simulation. These slices will be passed to each separate MultiAssetExpirationEvaluator
    so that it writes into the correct memory map location the data for its simulation

    Parameters
    ----------
    path_length : int
        The length of the simulated price path
    num_paths : int
        The number of paths in the simulation
    log_length : int
        The total number of rows in the CSV log

    Returns
    -------
    row_slices : dict
        Maps async task id number to row in dataframe log file
    """
    # Create the full index of each row in the log
    row_index = np.arange(log_length)
    start_index = 0
    end_index = path_length
    evaluator_id = 0
    row_slices = {}

    for _ in np.arange(num_paths):
        row_slice = row_index[start_index:end_index]

        row_slices[evaluator_id] = row_slice

        evaluator_id += 1
        start_index += path_length
        end_index += path_length

    # Return the slices for each ExpirationEvaluator
    return row_slices


def initialize_logging_df(log_file_name, total_rows, curve_ids):
    """
    Creates an empty Vaex DataFrame which will be used for logging

    Parameters
    ----------
    log_file_name : str
        The name of the log file
    total_rows : int
        The total number of rows in the DataFrame
    curve_ids : List[int]
        An id number identifying one curve uniquely

    Returns
    -------
    dfw : vaex.dataframe.DataFrame
        The Vaex dataframe log object
    """

    # Create the dummy typed columns which take no space
    kwargs_dict = {}

    dummy_timestamp = vaex.vrange(0, total_rows, dtype='i4')
    # dummy_curve_key = vaex.vrange(0, total_rows, dtype='i4')
    dummy_pathid = vaex.vrange(0, total_rows, dtype='i4')
    dummy_a = vaex.vrange(0, total_rows, dtype='f8')
    dummy_b = vaex.vrange(0, total_rows, dtype='f8')
    dummy_c = vaex.vrange(0, total_rows, dtype='f8')
    dummy_d = vaex.vrange(0, total_rows, dtype='f8')

    kwargs_dict['dummy_timestamp'] = dummy_timestamp
    # kwargs_dict['dummy_curve_key'] = dummy_curve_key
    kwargs_dict['dummy_pathid'] = dummy_pathid
    kwargs_dict['dummy_a'] = dummy_a
    kwargs_dict['dummy_b'] = dummy_b
    kwargs_dict['dummy_c'] = dummy_c
    kwargs_dict['dummy_d'] = dummy_d

    dummy_opt_br = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_cagr = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_ar = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_br = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_cagr = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_ar = vaex.vrange(0, total_rows, dtype='f8')

    kwargs_dict['dummy_opt_br'] = dummy_opt_br
    kwargs_dict['dummy_opt_cagr'] = dummy_opt_cagr
    kwargs_dict['dummy_opt_ar'] = dummy_opt_ar
    kwargs_dict['dummy_user_br'] = dummy_user_br
    kwargs_dict['dummy_user_cagr'] = dummy_user_cagr
    kwargs_dict['dummy_user_ar'] = dummy_user_ar

    # Loop over all of the assets in our simulation
    for i, curve_id in enumerate(curve_ids):
        dummy_training_key = vaex.vrange(0, total_rows, dtype='i4')
        dummy_exp = vaex.vrange(0, total_rows, dtype='i4')
        dummy_strike = vaex.vrange(0, total_rows, dtype='f8')
        dummy_price = vaex.vrange(0, total_rows, dtype='f8')
        dummy_is_exp = vaex.vrange(0, total_rows, dtype='i4')

        kwargs_dict['{}_training_key'.format(curve_id)] = dummy_training_key
        kwargs_dict['{}_exp'.format(curve_id)] = dummy_exp
        kwargs_dict['{}_strike'.format(curve_id)] = dummy_strike
        kwargs_dict['{}_price'.format(curve_id)] = dummy_price
        kwargs_dict['{}_is_exp'.format(curve_id)] = dummy_is_exp

        dummy_opt_prem = vaex.vrange(0, total_rows, dtype='f8')
        dummy_opt_loss = vaex.vrange(0, total_rows, dtype='f8')
        dummy_opt_payout = vaex.vrange(0, total_rows, dtype='f8')
        dummy_opt_amount = vaex.vrange(0, total_rows, dtype='f8')
        dummy_opt_util = vaex.vrange(0, total_rows, dtype='f8')
        dummy_opt_locked = vaex.vrange(0, total_rows, dtype='f8')

        kwargs_dict['{}_opt_prem'.format(curve_id)] = dummy_opt_prem
        kwargs_dict['{}_opt_loss'.format(curve_id)] = dummy_opt_loss
        kwargs_dict['{}_opt_payout'.format(curve_id)] = dummy_opt_payout
        kwargs_dict['{}_opt_amount'.format(curve_id)] = dummy_opt_amount
        kwargs_dict['{}_opt_util'.format(curve_id)] = dummy_opt_util
        kwargs_dict['{}_opt_locked'.format(curve_id)] = dummy_opt_locked

        dummy_user_prem = vaex.vrange(0, total_rows, dtype='f8')
        dummy_user_loss = vaex.vrange(0, total_rows, dtype='f8')
        dummy_user_payout = vaex.vrange(0, total_rows, dtype='f8')
        dummy_user_amount = vaex.vrange(0, total_rows, dtype='f8')
        dummy_user_util = vaex.vrange(0, total_rows, dtype='f8')
        dummy_user_locked = vaex.vrange(0, total_rows, dtype='f8')

        kwargs_dict['{}_user_prem'.format(curve_id)] = dummy_user_prem
        kwargs_dict['{}_user_loss'.format(curve_id)] = dummy_user_loss
        kwargs_dict['{}_user_payout'.format(curve_id)] = dummy_user_payout
        kwargs_dict['{}_user_amount'.format(curve_id)] = dummy_user_amount
        kwargs_dict['{}_user_util'.format(curve_id)] = dummy_user_util
        kwargs_dict['{}_user_locked'.format(curve_id)] = dummy_user_locked

    dummy_opt_total_util = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_total_amt = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_total_util = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_total_amt = vaex.vrange(0, total_rows, dtype='f8')

    kwargs_dict['dummy_opt_total_util'] = dummy_opt_total_util
    kwargs_dict['dummy_opt_total_amt'] = dummy_opt_total_amt
    kwargs_dict['dummy_user_total_util'] = dummy_user_total_util
    kwargs_dict['dummy_user_total_amt'] = dummy_user_total_amt

    # Create the logging dataframe with dummy columns
    df = vaex.from_arrays(**kwargs_dict)

    # Add columns of zeros with a type or cast

    column_names = []

    df['Timestamp'] = df.dummy_timestamp * 0
    # df['Curve_Key'] = df.dummy_curve_key * 0
    df['Path_ID'] = df.dummy_pathid * 0
    df['A'] = (df.dummy_a * 0).astype('float32')
    df['B'] = (df.dummy_b * 0).astype('float32')
    df['C'] = (df.dummy_c * 0).astype('float32')
    df['D'] = (df.dummy_d * 0).astype('float32')

    column_names.append('Timestamp')
    # column_names.append('Curve_Key')
    column_names.append('Path_ID')
    column_names.append('A')
    column_names.append('B')
    column_names.append('C')
    column_names.append('D')

    df['Opt_Bankroll'] = (df.dummy_opt_br * 0).astype('float32')
    df['Opt_CAGR'] = (df.dummy_opt_cagr * 0).astype('float32')
    df['Opt_Absolute_Return'] = (df.dummy_opt_ar * 0).astype('float32')
    df['User_Bankroll'] = (df.dummy_user_br * 0).astype('float32')
    df['User_CAGR'] = (df.dummy_user_cagr * 0).astype('float32')
    df['User_Absolute_Return'] = (df.dummy_user_ar * 0).astype('float32')

    column_names.append('Opt_Bankroll')
    column_names.append('Opt_CAGR')
    column_names.append('Opt_Absolute_Return')
    column_names.append('User_Bankroll')
    column_names.append('User_CAGR')
    column_names.append('User_Absolute_Return')

    # Create the columns that depend on the asset
    for i, curve_id in enumerate(curve_ids):
        df['{}_Training_Key'.format(curve_id)] = getattr(df,
                                                         '{}_training_key'.format(curve_id)) * 0
        df['{}_Exp_Duration'.format(curve_id)] = getattr(df, '{}_exp'.format(curve_id)) * 0
        df['{}_Strike_Pct'.format(curve_id)] = (
                    getattr(df, '{}_strike'.format(curve_id)) * 0).astype('float32')
        df['{}_Price'.format(curve_id)] = (getattr(df, '{}_price'.format(curve_id)) * 0).astype(
            'float32')
        df['{}_Is_Expired'.format(curve_id)] = getattr(df, '{}_is_exp'.format(curve_id)) * 0

        column_names.append('{}_Training_Key'.format(curve_id))
        column_names.append('{}_Exp_Duration'.format(curve_id))
        column_names.append('{}_Strike_Pct'.format(curve_id))
        column_names.append('{}_Price'.format(curve_id))
        column_names.append('{}_Is_Expired'.format(curve_id))

        df['{}_Opt_Premium'.format(curve_id)] = (getattr(df,
                                                         '{}_opt_prem'.format(
                                                             curve_id)) * 0).astype('float32')
        df['{}_Opt_Loss'.format(curve_id)] = (getattr(df,
                                                      '{}_opt_loss'.format(
                                                          curve_id)) * 0).astype('float32')
        df['{}_Opt_Payout'.format(curve_id)] = (getattr(df,
                                                        '{}_opt_payout'.format(
                                                            curve_id)) * 0).astype('float32')
        df['{}_Opt_Amount'.format(curve_id)] = (getattr(df,
                                                        '{}_opt_amount'.format(
                                                            curve_id)) * 0).astype('float32')
        df['{}_Opt_Util'.format(curve_id)] = (getattr(df,
                                                      '{}_opt_util'.format(
                                                          curve_id)) * 0).astype('float32')
        df['{}_Opt_Locked'.format(curve_id)] = (getattr(df,
                                                        '{}_opt_locked'.format(
                                                            curve_id)) * 0).astype('float32')

        column_names.append('{}_Opt_Premium'.format(curve_id))
        column_names.append('{}_Opt_Loss'.format(curve_id))
        column_names.append('{}_Opt_Payout'.format(curve_id))
        column_names.append('{}_Opt_Amount'.format(curve_id))
        column_names.append('{}_Opt_Util'.format(curve_id))
        column_names.append('{}_Opt_Locked'.format(curve_id))

        df['{}_User_Premium'.format(curve_id)] = (getattr(df,
                                                          '{}_user_prem'.format(
                                                              curve_id)) * 0).astype('float32')
        df['{}_User_Loss'.format(curve_id)] = (getattr(df,
                                                       '{}_user_loss'.format(
                                                           curve_id)) * 0).astype('float32')
        df['{}_User_Payout'.format(curve_id)] = (getattr(df,
                                                         '{}_user_payout'.format(
                                                             curve_id)) * 0).astype('float32')
        df['{}_User_Amount'.format(curve_id)] = (getattr(df,
                                                         '{}_user_amount'.format(
                                                             curve_id)) * 0).astype('float32')
        df['{}_User_Util'.format(curve_id)] = (getattr(df,
                                                       '{}_user_util'.format(
                                                           curve_id)) * 0).astype('float32')
        df['{}_User_Locked'.format(curve_id)] = (getattr(df,
                                                         '{}_user_locked'.format(
                                                             curve_id)) * 0).astype('float32')

        column_names.append('{}_User_Premium'.format(curve_id))
        column_names.append('{}_User_Loss'.format(curve_id))
        column_names.append('{}_User_Payout'.format(curve_id))
        column_names.append('{}_User_Amount'.format(curve_id))
        column_names.append('{}_User_Util'.format(curve_id))
        column_names.append('{}_User_Locked'.format(curve_id))

    df['Opt_Total_Util'] = (df.dummy_opt_total_util * 0).astype('float32')
    df['Opt_Total_Amt'] = (df.dummy_opt_total_amt * 0).astype('float32')
    df['User_Total_Util'] = (df.dummy_user_total_util * 0).astype('float32')
    df['User_Total_Amt'] = (df.dummy_user_total_amt * 0).astype('float32')

    column_names.append('Opt_Total_Util')
    column_names.append('Opt_Total_Amt')
    column_names.append('User_Total_Util')
    column_names.append('User_Total_Amt')

    # export what is needed
    # print('exporting col names: {}'.format(column_names))
    df[[*column_names]].export(log_file_name + '.hdf5')

    df.close()
    del df

    # Open the HDF5 file for writing our log data
    # print('Opening HDF5')
    dfw = vaex.open(log_file_name + '.hdf5', write=True)

    # Initialize the internal Vaex variables needed to write to the dataframe and print its contents
    dfw._length_unfiltered = total_rows
    dfw._length_original = total_rows
    state = dfw.state_get()
    state['active_range'] = [0, total_rows]
    dfw.state_set(state, use_active_range=True)

    return dfw


class MultiAssetBacktester:
    """
    This class runs a batch of backtests on a batch of generated curves
    """

    def __init__(self, config=None, curve_df=None, training_df=None, cov_matrix=None,
                 user_alpha=None):
        """
        Initializes the backtesting class with a given config and set of generated curves

        Parameters
        ----------
        config : dict
            The configuration object. See helper function
        curve_df : pandas.DataFrame
            The dataframe containing the generated curve portfolio
        training_df : pandas.DataFrame
            The dataframe containing the asset training windows
        cov_matrix : pandas.DataFrame
            (Optional) The dataframe containing a custom covariance matrix
        user_alpha : float
            (Optional) A custom user tail alpha

        Raises
        ------
        ValueError
            If not configured correctly
        """
        # Check we have a config object and save the data from it
        if config is None:
            raise ValueError('Config object must be specified')

        # Check we have the curve data and training data
        if curve_df is None:
            raise ValueError('Must specify a DataFrame containing the curve info')
        if training_df is None:
            raise ValueError('Must specify a DataFrame containing the training data')

        self.path_gen_method = config[PATH_GEN_KEY]
        self.num_paths = config[NUM_PATHS_KEY]
        self.path_length = config[PATH_LEN_KEY]
        self.initial_bankroll = config[INIT_BANK_KEY]
        self.util_map = config[UTIL_KEY]

        self.asset_keys = None
        self.fit_params = None
        self.dist_params = None
        self.bf_dict = None
        self.ocp_dict = None
        self.current_price_map = None

        self.curve_df = curve_df
        self.training_data_df = training_df

        self.covariance_matrix = cov_matrix
        self.asset_params = None
        self.user_alpha = user_alpha

        self.path_mapping = {}
        self.log_delta_mapping = {}

    def generate_backtesting_paths(self):
        """
        Iterates over each ticker and sentiment combination and generates the sample paths
        for backtesting. This generation uses the process specified by the PathGenMethod
        passed to the constructor of this class.

        Returns
        -------
        None
        """
        self.current_price_map = {}
        price_history_dict = {}

        for index, row in self.curve_df.iterrows():

            curve_id = row.Curve_ID
            asset = row.Asset

            # If we already did this asset skip it
            if asset in self.current_price_map:
                continue

            training_row = self.training_data_df.query('Ticker == "{}"'.format(asset))
            self.current_price_map[asset] = training_row.CurrentPrice.values[0]

            if self.covariance_matrix is None:

                vals = training_row.TrainingPrices.values[0]
                vals = [x for x in vals if ~np.isnan(x)]

                price_history_dict[asset] = vals
            else:
                # Save the marginal dist parameters for later by using the diagonal
                # of the cov matrix
                asset_index = self.covariance_matrix.columns.index(asset)
                self.asset_params[curve_id] = {
                    'key': asset,
                    'loc': 0.0,
                    'scale': np.sqrt(self.covariance_matrix.iat[asset_index, asset_index]),
                }

        if self.covariance_matrix is None:
            self.asset_keys = self.curve_df.Asset.unique()

            if self.path_gen_method == PathGenMethod.MV_NORMAL:
                self.covariance_matrix, self.asset_params = prices_to_sample_covariance_matrix(
                    price_history_dict)
                nu = -1  # Unused for MV_NORMAL. Here to clear uninitialized warning
            else:
                self.covariance_matrix, self.asset_params, nu = prices_to_t_covariance_matrix(
                    price_history_dict)
        else:
            self.asset_keys = self.covariance_matrix.columns
            nu = self.user_alpha

        # Generate the paths, if unknown type paths are 0
        if self.path_gen_method == PathGenMethod.MV_NORMAL:
            path_dict, log_delta_list = multivariate_normal_path_sampling(self.num_paths,
                                                                          self.path_length,
                                                                          self.covariance_matrix,
                                                                          self.current_price_map)
        elif self.path_gen_method == PathGenMethod.MV_STUDENT_T:
            path_dict, log_delta_list = multivariate_t_path_sampling(self.num_paths,
                                                                     self.path_length,
                                                                     self.covariance_matrix,
                                                                     nu,
                                                                     self.current_price_map)
        else:
            path_dict = {}
            log_delta_list = []
            for asset_key in self.asset_keys:

                path_dict[asset_key] = []
                log_delta_list.append(0.0)

                for i in range(self.num_paths):
                    path_dict[asset_key].append([0.0] * self.path_length)

        for index, row in self.curve_df.iterrows():
            curve_id = row.Curve_ID
            asset = row.Asset

            # print('path key: {}'.format(key))
            # print(paths)
            self.path_mapping[curve_id] = path_dict[asset]
            self.log_delta_mapping[curve_id] = log_delta_list

    def evaluate_backtest_sequentially(self, log_file_name, backtest_id, num_ma_backtests,
                                       progress_bar=None):
        """
        This function iterates over each ticker and sentiment and calculates the bankroll
        and cagr along each simulated path in the backtest. Writes the results to a CSV
        file for later analysis

        Parameters
        ----------
        log_file_name : str
            The name of the log file to use in the backtest
        backtest_id : int
            The id number identifying this backtesting
        num_ma_backtests : int
            The number of backtests to run
        progress_bar : streamlit.progress
            The streamlit progress bar to update for the UI

        Returns
        -------
        None
        """
        curve_ids = self.curve_df.Curve_ID.values

        # Define the total number of tasks so we can pre-allocate the logging dataframe
        total_rows = self.num_paths * self.path_length
        total_num_tasks = self.num_paths * num_ma_backtests

        df = initialize_logging_df(log_file_name, total_rows, curve_ids)
        log_length = len(df)

        # Calculate the row index slices for each task
        row_slices = calculate_row_slices(self.path_length, self.num_paths, log_length)

        duration_dict = {}
        strike_percent_dict = {}
        fit_params = {}
        bf_dict = {}
        ocp_dict = {}
        current_price_dict = {}
        for curve_row_index, row in self.curve_df.iterrows():

            duration_dict[row.Curve_ID] = row.Expiration
            strike_percent_dict[row.Curve_ID] = row.StrikePercent
            fit_params[row.Curve_ID] = [row.A, row.B, row.C, row.D]
            bf_dict[row.Curve_ID] = row.bet_fractions
            ocp_dict[row.Curve_ID] = row.curve_points
            current_price_dict[row.Curve_ID] = self.current_price_map[row.Asset]

        # Loop over all paths
        for path_index in range(self.num_paths):

            if progress_bar is not None:
                val = (path_index + self.num_paths * backtest_id) / float(total_num_tasks)
                progress_bar.progress(val)

            # Get the path from the mapping for each curve
            path = {}
            for curve_row_index, row in self.curve_df.iterrows():
                path[row.Curve_ID] = self.path_mapping[row.Curve_ID][path_index]

            # Get all of the parameters we need for this combo of key, duration, strike, and path
            row_slice = row_slices[path_index]

            # Build the argument list of parameters
            args = [self.curve_df.Curve_ID.values, duration_dict, strike_percent_dict, path,
                    path_index,
                    self.util_map, fit_params, self.initial_bankroll, current_price_dict, bf_dict,
                    ocp_dict, df,
                    row_slice]

            # Run the MultiAssetExpirationEvaluator for the path
            eval_work(*args)

        # Clean up the memory map we were writing to
        df.close()
        del df

        logging.debug('All results ready, simulation complete.')

    def evaluate_backtest_parallel(self, log_file_name):
        """
        This function iterates over each ticker and sentiment and launches parallel processes
        that calculate the bankroll and cagr along each simulated path in the backtest

        Parameters
        ----------
        log_file_name : str
            The name of the log file to use in the backtest

        Returns
        -------
        None
        """
        # One core less so the user's computer doesn't freeze up running the program
        p = Pool(cpu_count() - 1)

        # Define the total number of tasks so we can pre-allocate the logging dataframe
        total_num_tasks = len(self.curve_df.Label) * len(self.asset_keys[0]) * self.num_paths
        total_rows = total_num_tasks * self.path_length

        curve_ids = self.curve_df.Curve_ID.values
        # print('Curve IDs: {}'.format(curve_ids))

        df = initialize_logging_df(log_file_name, total_rows, curve_ids)
        log_length = len(df)

        # Calculate the row index slices for each async task
        row_slices = calculate_row_slices(self.path_length, self.num_paths, log_length)

        results = []
        evaluator_id = 0
        for key_index, key in enumerate(self.curve_df.Label):

            curve_id = curve_ids[key_index]

            duration_dict = {}
            strike_percent_dict = {}
            for asset_key in self.asset_keys[key_index]:
                duration_dict[asset_key] = getattr(
                    self.curve_df, '{}_Expiration'.format(asset_key))
                strike_percent_dict[asset_key] = getattr(
                    self.curve_df, '{}_StrikePercent'.format(asset_key))

            paths = self.path_mapping[key]

            # Loop over all paths
            for path_index, path in enumerate(paths):

                # Get all of the parameters we need for this combo of key,
                # duration, strike, and path
                current_price_map = self.current_price_map[curve_id]
                fit_params = self.fit_params[key]
                bf = self.bf_dict[key]
                ocp = self.ocp_dict[key]
                row_slice = row_slices[evaluator_id]

                # Run the MultiAssetExpirationEvaluator for the path

                # Build the argument list of parameters
                args = [self.asset_keys[key_index], duration_dict, strike_percent_dict, path,
                        path_index,
                        self.util_map, fit_params, self.initial_bankroll, current_price_map, bf,
                        ocp, df, row_slice]

                # Launch each async task and store the AsyncResult object used to query the status
                # of the parallel processes
                result = p.apply_async(eval_work, args)
                results.append(result)
                evaluator_id += 1

        logging.debug('Waiting for path evaluations to complete')

        # Check all of the paths have been evaluated
        async_complete_count = 0
        while async_complete_count < total_num_tasks:

            time.sleep(0.1)

            # Count the
            async_complete_count = 0
            for result in results:
                if result.get():
                    async_complete_count = async_complete_count + 1

        logging.debug('All results ready, simulation complete.')

        # Clean up the memory map we were writing to
        df.close()
        del df

        # Close the pool
        p.close()
        p.join()

"""
The batch_backtester module allows the user to run simulations of generated curves.

Currently, the backtesting code only supports simulating short put options.

Results are efficiently stored in a binary log file ending in *.hdf5 using the Vaex library.
Conversion utilities exist within the tool for the user's convenience that will convert these
output files into CSV.
"""
import pandas as pd
import numpy as np
import logging
import time
import vaex

from multiprocessing import Pool, cpu_count
from enum import Enum

from potion.backtest.path_gen import path_sampling, t_path_sampling
from potion.backtest.expiration_evaluator import ExpirationEvaluator, create_eval_config

log = logging.getLogger(__name__)

COL_KEY_PRICE_HIST_DATES = 'Master calendar'


class PathGenMethod(Enum):
    """
    An Enum specifying the method to use when generating paths for backtesting
    """
    HISTOGRAM = 0
    """Generate paths based on a histogram of return samples"""
    SKEWED_T = 1
    """Generate paths based on a Student's T distribution which can also capture skew"""


TICKER_KEY = 'tickers'
EXP_KEY = 'expiration_days'
STRIKE_KEY = 'strike_percentages'
BET_FRAC_KEY = 'bet_fraction_array'
PATH_GEN_KEY = 'path_generation_method'
NUM_PATHS_KEY = 'number_of_paths'
PATH_LEN_KEY = 'path_length'
AMOUNT_OR_UTIL_KEY = 'amount'
INIT_BANK_KEY = 'initial_bankroll'
SIM_TYPE_KEY = 'simulation_type'
PAYOFF_TYPE_KEY = 'payoff_type'
PAYOFF_PARAMS = 'payoff_params'


def _safe_multi_dict_store(mapping: dict, key, duration, strike_pct, value):
    """
    Helper function that stores a value in a nested dict. If the entry does not exist,
    it is created and the value is stored.

    Parameters
    ----------
    mapping : dict
        The dict in which we want to store a value
    key : str
        The training key in the map
    duration : int
        The expiration or duration of the contract used as a key in the map
    strike_pct : float
        The strike percentage used as a key in the map
    value
        The value to store

    Returns
    ----------
    None
    """
    if mapping.get(key) is None:
        mapping[key] = {}
    if mapping[key].get(duration) is None:
        mapping[key][duration] = {}
    if mapping[key][duration].get(strike_pct) is None:
        mapping[key][duration][strike_pct] = {}
    mapping[key][duration][strike_pct] = value


def _safe_store_dict(mapping: dict, key, value):
    """
    Helper function that stores a value in a dict and creates an entry for the key
    if it does not exist

    Parameters
    ----------
    mapping : dict
        The dict in which we want to store a value
    key : object
        The key at which we want to store
    value : object
        The value

    Returns
    -------
    None
    """
    if mapping.get(key) is None:
        mapping[key] = {}
    mapping[key] = value


def _absorb_paths_hitting_zero(paths):
    """
    Helper function which loops over all of the generated backtesting paths and checks if they
    hit zero. If they do, they are 'absorbed' and all of the path values after this point are
    also set to zero. The paths are returned afterwards

    Parameters
    ----------
    paths : List[List[float]]
        A List which is num_paths in size containing Lists of the path data which are
        path_length long

    Returns
    ----------
    List[List[float]]
        The modified path array
    """

    # paths[0][1] = 0.0

    # Sets all the values to zero after a path hits zero
    for path in paths:
        # Check if any of the paths go to zero
        result = np.where(path == 0.0)

        # Get array from result tuple
        index_array = result[0]

        # If result isn't empty it contains index path hit zero
        if index_array.size > 0:
            indices_to_set_zero = np.arange(index_array[0], len(path))
            np.put(path, indices_to_set_zero, 0.0)

    return paths


def _eval_work(key, duration, strike_percent, path, path_id, util: float, fit_params,
               initial_bankroll, current_price, bf, ocp, logging_df, row_slice):
    """
    This function processes one set of evaluation work corresponding to a combination of
    key, duration, strike, and path of the backtesting simulation. This function can
    either be called sequentially in a nested for-loop, or in parallel on different processing cores

    Parameters
    -----------
    key : str
        The key labeling the training data
    duration : int
        The duration of the contract in number of days
    strike_percent : float
        The strike percent corresponding to this set of simulation data. 1.0 corresponds
        to at-the-money
    path : List[float]
        The price path corresponding to this set of simulation data
    path_id : int
        The index in the array of all paths
    util : float
        The fixed util which is bought by (from) the user at each expiration
    fit_params : List[float]
        The parameters of the fit to the premium curve [A, B, C, D]
    initial_bankroll : float
        The initial starting bankroll for the simulation
    current_price : float
        The price we are starting the simulation at
    bf : List[float]
        The bet fraction array (X values of curve)
    ocp : List[float]
        The optimal curve points (Y values of curve)
    logging_df : vaex.dataframe.DataFrame
        The vaex dataframe which is our memory mapped log file
    row_slice : List[int]
        The row slice for this task which is a List of ints containing the
        row numbers to write to for this task in the vaex log df

    Returns
    ----------
    bool
        Function always returns True, simply because the multiprocessing interface requires
        the function to return something
    """
    # Calculate all of the results along the path
    input_dict = create_eval_config(path, util, duration, strike_percent, fit_params,
                                    initial_bankroll, bf, ocp)

    evaluator = ExpirationEvaluator(input_dict)

    evaluator.evaluate_expirations_along_path(logging_df, key, path_id, current_price, row_slice)

    # Needs to return for async result
    return True


def _calculate_log_df_slices(path_length: int, keys, exps, strike_pcts, num_paths, log_length):
    """
    This function calculates the slices of the logging dataframe that corresponds to one given
    simulation. These slices will be passed to each computer core so that it writes into the
    correct location in the log file. This ensures that the different computer cores are
    independent and do not overwrite each other in the log file.

    Parameters
    -----------
    path_length : int
        The length of the simulated price path in days. Example: 300
    keys : List[str]
        The training keys for the backtesting simulation. Example: ['ETH-bull', 'BTC-bear']
    exps : List[int]
        The List of expiration days for the backtesting simulation. Example: [1, 7, 14]
    strike_pcts : List[float]
        The List of strike percentages for the backtesting simulation where 1.0 is at-the-money.
        Example: [0.9, 1.0, 1.1]
    num_paths : int
        The number of paths in the simulation. Example: 300
    log_length : int
        The total number of rows in the logging dataframe. Example: 1000

    Returns
    -----------
    row_slices : dict
        A dict of {int: List[int]} mapping the id number of the evaluation task to a List of
        ints containing the log df row numbers to write to
    """

    # Create the full index of each row in the log
    row_index = np.arange(log_length)
    start_index = 0
    end_index = path_length
    evaluator_id = 0
    row_slices = {}

    # Loop over all the combinations and create the slices for each simulation
    for _ in keys:
        for _ in exps:
            for _ in strike_pcts:
                for _ in np.arange(num_paths):
                    row_slice = row_index[start_index:end_index]

                    row_slices[evaluator_id] = row_slice

                    evaluator_id += 1
                    start_index += path_length
                    end_index += path_length

    # Return the slices for each ExpirationEvaluator
    return row_slices


def _initialize_vaex_logging_df(log_file_name: str, total_rows: int):
    """
    Initializes the Vaex DataFrame which is used for logging. The df needs to have the columns
    and types defined with dummy variables and exported to the disk, afterwards the file is
    opened in write mode and returned to the caller so that logging data from the backtest
    can be recorded

    Parameters
    ----------
    log_file_name : str
        A string specifying the name of the log file which will be opened for writing
    total_rows : int
        The total number of rows in the log file

    Returns
    -------
    log_df : vaex.dataframe.DataFrame
        The logging df which will have backtesting results recorded
    """

    # Create the dummy typed columns which take no space
    dummy_timestamp = vaex.vrange(0, total_rows, dtype='i4')
    dummy_training_key = vaex.vrange(0, total_rows, dtype='i4')
    dummy_exp = vaex.vrange(0, total_rows, dtype='i4')
    dummy_strike = vaex.vrange(0, total_rows, dtype='f8')
    dummy_pathid = vaex.vrange(0, total_rows, dtype='i4')
    dummy_exp_price = vaex.vrange(0, total_rows, dtype='f8')
    dummy_a = vaex.vrange(0, total_rows, dtype='f8')
    dummy_b = vaex.vrange(0, total_rows, dtype='f8')
    dummy_c = vaex.vrange(0, total_rows, dtype='f8')
    dummy_d = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_prem = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_loss = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_payout = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_amount = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_util = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_locked = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_br = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_cagr = vaex.vrange(0, total_rows, dtype='f8')
    dummy_opt_ar = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_prem = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_loss = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_payout = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_amount = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_util = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_locked = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_br = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_cagr = vaex.vrange(0, total_rows, dtype='f8')
    dummy_user_ar = vaex.vrange(0, total_rows, dtype='f8')

    # Create the logging dataframe with dummy columns
    df = vaex.from_arrays(dummy_timestamp=dummy_timestamp,
                          dummy_training_key=dummy_training_key,
                          dummy_exp=dummy_exp,
                          dummy_strike=dummy_strike,
                          dummy_pathid=dummy_pathid,
                          dummy_exp_price=dummy_exp_price,
                          dummy_a=dummy_a,
                          dummy_b=dummy_b,
                          dummy_c=dummy_c,
                          dummy_d=dummy_d,
                          dummy_opt_prem=dummy_opt_prem,
                          dummy_opt_loss=dummy_opt_loss,
                          dummy_opt_payout=dummy_opt_payout,
                          dummy_opt_amount=dummy_opt_amount,
                          dummy_opt_util=dummy_opt_util,
                          dummy_opt_locked=dummy_opt_locked,
                          dummy_opt_br=dummy_opt_br,
                          dummy_opt_cagr=dummy_opt_cagr,
                          dummy_opt_ar=dummy_opt_ar,
                          dummy_user_prem=dummy_user_prem,
                          dummy_user_loss=dummy_user_loss,
                          dummy_user_payout=dummy_user_payout,
                          dummy_user_amount=dummy_user_amount,
                          dummy_user_util=dummy_user_util,
                          dummy_user_locked=dummy_user_locked,
                          dummy_user_br=dummy_user_br,
                          dummy_user_cagr=dummy_user_cagr,
                          dummy_user_ar=dummy_user_ar)

    # Add columns of zeros with a type or cast
    df['Timestamp'] = df.dummy_timestamp * 0
    df['Training_Key'] = df.dummy_training_key * 0
    df['Exp_Duration'] = df.dummy_exp * 0
    df['Strike_Pct'] = (df.dummy_strike * 0).astype('float32')
    df['Path_ID'] = df.dummy_pathid * 0
    df['Expiration_Price'] = (df.dummy_exp_price * 0).astype('float32')
    df['A'] = (df.dummy_a * 0).astype('float32')
    df['B'] = (df.dummy_b * 0).astype('float32')
    df['C'] = (df.dummy_c * 0).astype('float32')
    df['D'] = (df.dummy_d * 0).astype('float32')
    df['Opt_Premium'] = (df.dummy_opt_prem * 0).astype('float32')
    df['Opt_Loss'] = (df.dummy_opt_loss * 0).astype('float32')
    df['Opt_Payout'] = (df.dummy_opt_payout * 0).astype('float32')
    df['Opt_Amount'] = (df.dummy_opt_amount * 0).astype('float32')
    df['Opt_Util'] = (df.dummy_opt_util * 0).astype('float32')
    df['Opt_Locked'] = (df.dummy_opt_locked * 0).astype('float32')
    df['Opt_Bankroll'] = (df.dummy_opt_br * 0).astype('float32')
    df['Opt_CAGR'] = (df.dummy_opt_cagr * 0).astype('float32')
    df['Opt_Absolute_Return'] = (df.dummy_opt_ar * 0).astype('float32')
    df['User_Premium'] = (df.dummy_user_prem * 0).astype('float32')
    df['User_Loss'] = (df.dummy_user_loss * 0).astype('float32')
    df['User_Payout'] = (df.dummy_user_payout * 0).astype('float32')
    df['User_Amount'] = (df.dummy_user_amount * 0).astype('float32')
    df['User_Util'] = (df.dummy_user_util * 0).astype('float32')
    df['User_Locked'] = (df.dummy_user_locked * 0).astype('float32')
    df['User_Bankroll'] = (df.dummy_user_br * 0).astype('float32')
    df['User_CAGR'] = (df.dummy_user_cagr * 0).astype('float32')
    df['User_Absolute_Return'] = (df.dummy_user_ar * 0).astype('float32')

    # export what is needed
    df[[
        'Timestamp',
        'Training_Key',
        'Exp_Duration',
        'Strike_Pct',
        'Path_ID',
        'Expiration_Price',
        'A',
        'B',
        'C',
        'D',
        'Opt_Premium',
        'Opt_Loss',
        'Opt_Payout',
        'Opt_Amount',
        'Opt_Util',
        'Opt_Locked',
        'Opt_Bankroll',
        'Opt_CAGR',
        'Opt_Absolute_Return',
        'User_Premium',
        'User_Loss',
        'User_Payout',
        'User_Amount',
        'User_Util',
        'User_Locked',
        'User_Bankroll',
        'User_CAGR',
        'User_Absolute_Return'
    ]].export(log_file_name + '.hdf5')

    # Open the HDF5 file for writing our log data
    df = vaex.open(log_file_name + '.hdf5', write=True)

    # Initialize the internal Vaex variables needed to write to the dataframe and print its contents
    df._length_unfiltered = total_rows
    df._length_original = total_rows
    state = df.state_get()
    state['active_range'] = [0, total_rows]
    df.state_set(state, use_active_range=True)

    return df


def create_backtester_config(num_paths: int, path_length: int,
                             amount_or_util: float, initial_bankroll: float,
                             path_gen_method=PathGenMethod.SKEWED_T, simulation_type=True):
    """
    Helper function to easily create a configuration object for the backtester.

    Parameters
    -----------

    num_paths : int
        The number of price paths to use in the simulation
    path_length : int
        The number of days to use as the length of the simulated path
    amount_or_util : float
        The amount of otokens the buyer will buy at each timestep along the path, or constant util
    initial_bankroll : float
        The starting capital at the beginning of the simulation
    path_gen_method : PathGenMethod
        (Optional. Default: SKEWED_T) The distribution to use to generate paths see
        PathGenMethod enum.
    simulation_type : bool
        (Optional. Default: True) The type of simulation to run. Constant util or array of
        amounts of otokens traded, True for util

    Returns
    -----------
    config : dict
        The config dict
    """
    config = {
        PATH_GEN_KEY: path_gen_method,
        NUM_PATHS_KEY: num_paths,
        PATH_LEN_KEY: path_length,
        AMOUNT_OR_UTIL_KEY: amount_or_util,
        INIT_BANK_KEY: initial_bankroll,
        SIM_TYPE_KEY: simulation_type
    }

    return config


class BatchBacktester:

    def __init__(self, *args, **kwargs):
        """
        This class runs a batch of backtests on a set of generated curves. The results of
        the backtesting is stored in a log file which is in the format of a DataFrame and is
        directly memory-mapped using Vaex for high speed.

        This constructor initializes the backtesting class with a given config and set of
        generated curves to simulate

        Parameters
        -----------
        config : dict
            The configuration object. See helper function create_backtester_config
        curve_df : pandas.DataFrame
            The DataFrame containing the input curves which we would like to simulate
        training_df: pandas.DataFrame
            The DataFrame containing the information about training data for each asset

        Raises
        -----------
        ValueError
            If the config dict is None, if the curve_df is None, or if the training_df is None
        """
        if len(args) == 2:
            config = args[0]
            curve_gen = args[1]
            curve_df = None
            training_df = None
        else:
            config = kwargs.get('config', None)
            curve_gen = kwargs.get('curve_gen', None)
            curve_df = kwargs.get('curve_df', None)
            training_df = kwargs.get('training_df', None)

        # Check we have a config object and save the data from it
        if config is None:
            raise ValueError('Config object must be specified')

        self.path_gen_method = config[PATH_GEN_KEY]
        self.num_paths = config[NUM_PATHS_KEY]
        self.path_length = config[PATH_LEN_KEY]
        self.initial_bankroll = config[INIT_BANK_KEY]

        if config[SIM_TYPE_KEY] is True:
            self.amounts_or_util = config[AMOUNT_OR_UTIL_KEY]
        else:
            self.amounts_or_util = np.asarray([config[AMOUNT_OR_UTIL_KEY]] * (self.path_length - 1))

        # Check we have the curve data and training data
        if curve_gen is None:

            if curve_df is None:
                raise ValueError('Must specify either a BatchCurveGenerator object '
                                 'or a DataFrame containing the curve info')
            if training_df is None:
                raise ValueError('Must specify either a BatchCurveGenerator object or a '
                                 'DataFrame containing the training data')

            keys = []
            current_price_dict = {}
            training_start_dict = {}
            training_end_dict = {}
            training_price_dict = {}
            for index, row in training_df.iterrows():

                key = row.Ticker + '-' + row.Label
                keys.append(key)

                if current_price_dict.get(key) is None:
                    current_price_dict[key] = {}
                current_price_dict[key] = row.CurrentPrice

                if training_start_dict.get(key) is None:
                    training_start_dict[key] = {}
                training_start_dict[key] = row.StartDate

                if training_end_dict.get(key) is None:
                    training_end_dict[key] = {}
                training_end_dict[key] = row.EndDate

                if training_price_dict.get(key) is None:
                    training_price_dict[key] = {}
                training_price_dict[key] = row.TrainingPrices

            exps = []
            strike_pcts = []
            fit_dict = {}
            bf_dict = {}
            ocp_dict = {}
            dist_dict = {}
            for index, row in curve_df.iterrows():

                key = row.Ticker + '-' + row.Label

                exps.append(row.Expiration)
                strike_pcts.append(row.StrikePercent)
                _safe_multi_dict_store(
                    fit_dict, key, row.Expiration, row.StrikePercent, [row.A, row.B, row.C, row.D])
                _safe_multi_dict_store(
                    bf_dict, key, row.Expiration, row.StrikePercent, row.bet_fractions)
                _safe_multi_dict_store(
                    ocp_dict, key, row.Expiration, row.StrikePercent, row.curve_points)

                if dist_dict.get(key) is None:
                    dist_dict[key] = {}
                dist_dict[key] = row.t_params

            # Save the unique values using set
            self.keys = list(dict.fromkeys(keys))
            self.exp_days = list(dict.fromkeys(exps))
            self.strike_pcts = list(dict.fromkeys(strike_pcts))
            self.fit_params = fit_dict
            self.dist_params = dist_dict
            self.bf_dict = bf_dict
            self.ocp_dict = ocp_dict

            self.training_data_mapping = training_price_dict
            self.current_price_map = current_price_dict
            self.training_start_mapping = training_start_dict
            self.training_end_mapping = training_end_dict
        else:
            self.keys = curve_gen.keys
            self.exp_days = curve_gen.exp_days
            self.strike_pcts = curve_gen.strike_pcts
            self.training_data_mapping = curve_gen.training_data_mapping

            current_price_dict = {}
            dist_params = {}
            fit_dict = {}
            bf_dict = {}
            ocp_dict = {}
            for key in self.keys:

                current_price = curve_gen.full_price_path[key][-1:].values[0]
                params = curve_gen.generator_mapping[key].fit_params

                for exp in self.exp_days:
                    for strike_pct in self.strike_pcts:
                        curve_params = curve_gen.generator_mapping[key].opt_premium_fit_map[exp][
                            strike_pct]
                        bet_fractions = curve_gen.generator_mapping[key].bet_fraction_map[exp][
                            strike_pct]
                        opt_premiums = curve_gen.generator_mapping[key].optimal_premium_map[exp][
                            strike_pct]
                        _safe_multi_dict_store(fit_dict, key, exp, strike_pct, curve_params)
                        _safe_multi_dict_store(bf_dict, key, exp, strike_pct, bet_fractions)
                        _safe_multi_dict_store(ocp_dict, key, exp, strike_pct, opt_premiums)

                if current_price_dict.get(key) is None:
                    current_price_dict[key] = {}
                current_price_dict[key] = current_price

                if dist_params.get(key) is None:
                    dist_params[key] = {}
                dist_params[key] = params

            self.dist_params = dist_params
            self.fit_params = fit_dict
            self.bf_dict = bf_dict
            self.ocp_dict = ocp_dict
            self.current_price_map = current_price_dict
            self.training_start_mapping = curve_gen.training_start_mapping
            self.training_end_mapping = curve_gen.training_end_mapping

        self.path_mapping = {}

    def generate_backtesting_paths(self):
        """
        Iterates over each training data set and generates the sample paths for backtesting. This
        generation uses the process specified by the PathGenMethod passed in the config object
        to the constructor of this class.

        Returns
        -----------
        None
        """
        for key in self.keys:

            prices = pd.DataFrame(self.training_data_mapping[key])
            # gen = Generator(price_series=prices, fit_params=self.dist_params[key])

            log.debug('Generating paths for {} {} {}'.format(key, self.num_paths, self.path_length))

            # Set this because we may be training with a section of history
            # that's not the full history
            current_price = self.current_price_map[key]

            # Generate the paths, if unknown type paths are 0
            if self.path_gen_method == PathGenMethod.SKEWED_T:
                paths = t_path_sampling(t_fit_params=self.dist_params[key], n_paths=self.num_paths,
                                        path_length=self.path_length, current_price=current_price)
            elif self.path_gen_method == PathGenMethod.HISTOGRAM:
                paths = path_sampling(prices=prices, n_paths=self.num_paths,
                                      path_length=self.path_length,
                                      current_price=current_price)
            else:
                paths = [0] * self.num_paths

            paths = _absorb_paths_hitting_zero(paths)

            _safe_store_dict(self.path_mapping, key, paths)

    def evaluate_backtest_sequentially(self, log_file_name, progress_bar=None):
        """
        This function iterates over each path/strike/expiration/asset specified and calculates
        the bankroll and cagr along each simulated path in the backtest. Writes the results to
        a dataframe which is a log file for later analysis

        Parameters
        -----------
        log_file_name : str
            A string specifying the name of the log file which will be opened for writing
        progress_bar: optional
            The progress bar object used to update a UI on backtest progress. If None, there are
            no updates

        Returns
        -----------
        dfr : vaex.dataframe.DataFrame
            The logging df opened read-only which has the backtesting results recorded
        row_slices : dict
            A dict of {int: List[int]} mapping the id number of the evaluation task to a List
            of ints containing the log df row numbers. These row numbers correspond to the
            relevant rows for that task
        """

        # Define the total number of tasks so we can pre-allocate the logging dataframe
        total_num_tasks = len(self.keys) * len(self.exp_days) * len(
            self.strike_pcts) * self.num_paths
        total_rows = total_num_tasks * self.path_length

        df = _initialize_vaex_logging_df(log_file_name, total_rows)
        log_length = len(df)

        # Calculate the row index slices for each async task
        row_slices = _calculate_log_df_slices(self.path_length, self.keys, self.exp_days,
                                              self.strike_pcts,
                                              self.num_paths, log_length)

        evaluator_id = 0
        for key_index, key in enumerate(self.keys):
            logging.debug('Running Backtest for {}'.format(key))

            current_price = self.current_price_map[key]

            # Loop over durations
            for duration_index, duration in enumerate(self.exp_days):

                # Loop over strikes
                for strike_index, strike_pct in enumerate(self.strike_pcts):

                    # Loop over all paths
                    for path_index, path in enumerate(self.path_mapping[key]):
                        # print('Evaluating Key: {} ({}) Duration: {} ({}) Strike: {} ({}) Path: {}'
                        #       .format(key, key_index, duration, duration_index, strike_pct,
                        #               strike_index, path_index))

                        if progress_bar is not None:
                            val = evaluator_id / float(total_num_tasks)
                            progress_bar.progress(val)

                        # Get all of the parameters we need for this combo of key, duration,
                        # strike, and path
                        fit_params = self.fit_params[key][duration][strike_pct]
                        bf = self.bf_dict[key][duration][strike_pct]
                        ocp = self.ocp_dict[key][duration][strike_pct]
                        row_slice = row_slices[evaluator_id]

                        # Build the argument list of parameters
                        args = [key_index, duration, strike_pct, path, path_index,
                                self.amounts_or_util, fit_params,
                                self.initial_bankroll, current_price, bf, ocp, df, row_slice]

                        # Run the ExpirationEvaluator for the path
                        _eval_work(*args)
                        evaluator_id += 1

        logging.debug('All results ready, simulation complete.')

        if progress_bar is not None:
            progress_bar.progress(1.0)

        # Clean up the memory map we were writing to
        df.close()
        del df

        return row_slices

    def evaluate_backtest_parallel(self, log_file_name, progress_bar=None):
        """
        This function iterates over each path/strike/expiration/asset specified and launches
        parallel processes that calculate the bankroll and cagr along each simulated path in
        the backtest. Writes the results to a dataframe which is a log file for later analysis

        Parameters
        -----------
        log_file_name : str
            A string specifying the name of the log file which will be opened for writing
        progress_bar: optional
            The progress bar object used to update a UI on backtest progress. If None, there
            are no updates

        Returns
        -----------
        dfr : vaex.dataframe.DataFrame
            The logging df opened read-only which has the backtesting results recorded
        row_slices : dict
            A dict of {int: List[int]} mapping the id number of the evaluation task to a List
            of ints containing the log df row numbers. These row numbers correspond to the
            relevant rows for that task
        """
        # One core less so the user's computer doesn't freeze up running the program
        p = Pool(cpu_count() - 1)

        # Define the total number of tasks so we can pre-allocate the logging dataframe
        total_num_tasks = len(self.keys) * len(self.exp_days) * len(
            self.strike_pcts) * self.num_paths
        total_rows = total_num_tasks * self.path_length

        df = _initialize_vaex_logging_df(log_file_name, total_rows)
        log_length = len(df)

        # Calculate the row index slices for each async task
        row_slices = _calculate_log_df_slices(self.path_length, self.keys, self.exp_days,
                                              self.strike_pcts,
                                              self.num_paths, log_length)

        results = []
        evaluator_id = 0
        for key_index, key in enumerate(self.keys):

            current_price = self.current_price_map[key]

            # Loop over durations
            for duration_index, duration in enumerate(self.exp_days):

                # Loop over strikes
                for strike_index, strike_pct in enumerate(self.strike_pcts):

                    # Loop over all paths
                    for path_index, path in enumerate(self.path_mapping[key]):

                        # Get all of the parameters we need for this combo of key,
                        # duration, strike, and path
                        fit_params = self.fit_params[key][duration][strike_pct]
                        bf = self.bf_dict[key][duration][strike_pct]
                        ocp = self.ocp_dict[key][duration][strike_pct]
                        row_slice = row_slices[evaluator_id]

                        # Build the argument list of parameters
                        args = [key_index, duration, strike_pct, path, path_index,
                                self.amounts_or_util, fit_params,
                                self.initial_bankroll, current_price, bf, ocp, df, row_slice]

                        # Launch each async task and store the AsyncResult object used
                        # to query the status of the parallel processes
                        result = p.apply_async(_eval_work, args)
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

        return row_slices

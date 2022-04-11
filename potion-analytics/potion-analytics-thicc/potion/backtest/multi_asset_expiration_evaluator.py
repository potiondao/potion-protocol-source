"""
This module provides a helper object which encapsulates the logic of iterating over a multi asset
path in the simulation and calculating the profit, loss, and performance statistics of the
configured payoff. This object can be run in sequence or in parallel
"""
import numpy as np

from potion.curve_gen.payoff.builder import PayoffConfigBuilder
from potion.curve_gen.payoff.payoff import (configure_payoff, get_position_max_loss)
from potion.curve_gen.curve_conversion import (convert_fully_normalized_value_to_strike_normalized,
                                               convert_strike_normalized_to_absolute_curve)

PATH_KEY = 'Paths'
UTIL_KEY = 'Utils'
DURATION_KEY = 'Durations'
STRIKE_KEY = 'Strikes'
FIT_PARAMS_KEY = 'Fit'
INIT_BR_KEY = 'InitBR'
BF_KEY = 'BetFr'
CURVE_PTS_KEY = 'CurvePts'


def create_eval_config(paths, utils, durations, strike_percents, fit_params,
                       initial_bankroll, bf, ocp):
    """
    Creates a config dict to initialize the ExpirationEvaluator class. The util parameter can
    configure the object to be using either a constant util during the test, or simulating
    a buyer purchasing a certain number of contracts. If a float is passed the parameter is
    interpreted as a fixed util. If it is a numpy ndarray it is
    interpreted as purchasing a fixed number of contracts at each time step.

    Parameters
    ----------
    paths : dict
        A dict mapping an asset key to a path being evaluated in the backtesting simulation
    utils : dict
        A dict mapping an asset key to a util to bet for that asset. Total util must be
        between 0 and 1
    durations : dict
        A dict mapping an asset key to a duration representing the number of days between each
        expiration. 1 is every day, 2 every other, etc.
    strike_percents : dict
        A dict mapping an asset key to a strike in percentage ATM where 1.0 is ATM
    fit_params : List[float]
        The fit parameters for the user curve A, B, C, D
    initial_bankroll : float
        The initial starting capital in our backtesting simulation
    bf : numpy.ndarray
        The bet fractions (X axis) of the kelly generated bonding curve
    ocp : numpy.ndarray
        The optimal curve points (Y axis) of the kelly generated bonding curve

    Returns
    -------
    config : dict
        The configuration dict
    """
    config = {
        PATH_KEY: paths,
        UTIL_KEY: utils,
        DURATION_KEY: durations,
        STRIKE_KEY: strike_percents,
        FIT_PARAMS_KEY: fit_params,
        INIT_BR_KEY: initial_bankroll,
        BF_KEY: bf,
        CURVE_PTS_KEY: ocp
    }

    return config


def evaluate_premium_curve(fit_params, util):
    """
    Function to calculate the premium of a fit curve

    Parameters
    ----------
    fit_params : List[float]
        The A, B, C, D values of the curve
    util : Union[float, numpy.ndarray]
        The util percentage that is the function input

    Returns
    -------
    premium : numpy.ndarray
        The premium to charge
    """
    a = fit_params[0]
    b = fit_params[1]
    c = fit_params[2]
    d = fit_params[3]

    if np.isscalar(util):
        if util > 1.0 or util < 0.0:
            raise ValueError('Util must be between 0 and 1.0: {}'.format(util))
    if a < 0.0 or b < 0.0 or c < 0.0 or d < 0.0:
        raise ValueError('Fit Parameters must be positive: {}'.format(fit_params))

    return a * util * np.cosh(b * util ** c) + d


def calculate_loss_if_any(expiration_price, amount, strike_pct):
    """
    Calculates the payout of the expired contract.

    Parameters
    ----------
    expiration_price : float
        The price at which the token expired
    amount : float
        The number of contract tokens which were purchased by the buyer
    strike_pct : float
        The strike price of the oToken contract

    Returns
    -------
    payout : numpy.ndarray
        Payout outcome for the given expiration price and the max loss of the position
    max_loss : float
        The maximum amount the position could lose
    """
    if amount < 0.0:
        raise ValueError('The amount of contracts traded must be positive')

    sample_points = np.asarray([1e-20, expiration_price])

    cfg = PayoffConfigBuilder().set_x_points(sample_points).add_option_leg(
        'put', 'short', amount, strike_pct).build_config()
    configure_payoff(cfg)
    max_loss = get_position_max_loss()

    # Get the outcome corresponding to our sample point
    return cfg.total_payoff[1], max_loss


def calc_premium_and_locked_collateral(strike, current_bankroll, fully_norm_prem, util_total):
    """
    Calculates the amount of premium collected and collateral locked in absolute terms to be
    added to the bankroll

    Parameters
    ----------
    strike : float
        The strike in absolute value
    current_bankroll : float
        The current bankroll along the path
    fully_norm_prem : Union[float, numpy.ndarray]
        The premium output from the curve generator
    util_total : Union[float, numpy.ndarray]
        The total util along the curve in use

    Returns
    -------
    absolute_locked_collateral : numpy.ndarray
        The amount of collateral locked in absolute terms
    absolute_premium : numpy.ndarray
        The premium collected in absolute terms
    """
    strike_normalized_premium = convert_fully_normalized_value_to_strike_normalized(
        strike, current_bankroll, util_total, fully_norm_prem)

    (absolute_locked_collateral,
     absolute_premium) = convert_strike_normalized_to_absolute_curve(
        strike, current_bankroll, util_total, strike_normalized_premium)

    return absolute_locked_collateral, absolute_premium


def log_expiration_info(log_df, curve_ids, expired_curve_id, path_id, fit_params,
                        path_index, price_dict, duration_dict, strike_dict, user_current_br,
                        opt_current_br, user_cagr, user_ar, opt_cagr, opt_ar, user_util_dict,
                        opt_util_dict, user_amts_dict, opt_amts_dict, trade_dict, results_dict,
                        row_index):
    """
    Logs information about one expiration along the path.

    Parameters
    ----------
    log_df : vaex.dataframe.DataFrame
        The logging dataframe
    curve_ids : List[int]
        The List of curve ids corresponding to the options
    expired_curve_id : int
        The key for the option which is expired
    path_id : int
        The id number for the backtesting path
    fit_params : List[float]
        The A,B,C,D parameters fit to the premium curve
    path_index : int
        The timestamp along the path
    price_dict : dict
        The price along the path for each curve_id
    duration_dict : dict
        The duration of the option for each curve_id
    strike_dict : dict
        The strike of the option for each curve_id
    user_current_br : float
        The current bankroll for the A,B,C,D curve
    opt_current_br : float
        The current bankroll for the minimum Kelly curve
    user_cagr : float
        The current CAGR for the A,B,C,D curve
    user_ar : float
        The absolute return for the A,B,C,D curve
    opt_cagr : float
        The current CAGR for the minimum Kelly curve
    opt_ar : float
        The current absolute return for the minimum Kelly curve
    user_util_dict : dict
        Dict maps curve id to ABCD util
    opt_util_dict : dict
        Dict maps curve id to minimum curve util
    user_amts_dict : dict
        Dict maps curve id to ABCD curve amounts
    opt_amts_dict : dict
        Dict maps curve id to minimum curve amounts
    trade_dict : dict
        Dict containing info about when the trade was entered
    results_dict : dict
        Dict containing info about the results of the trade
    row_index : int
        The index of the row in the logging dataframe

    Returns
    -------
    None
    """
    log_df.columns['Timestamp'][row_index] = int(path_index)
    log_df.columns['Path_ID'][row_index] = path_id
    log_df.columns['A'][row_index] = fit_params[expired_curve_id][0]
    log_df.columns['B'][row_index] = fit_params[expired_curve_id][1]
    log_df.columns['C'][row_index] = fit_params[expired_curve_id][2]
    log_df.columns['D'][row_index] = fit_params[expired_curve_id][3]

    log_df.columns['Opt_Bankroll'][row_index] = opt_current_br
    log_df.columns['Opt_CAGR'][row_index] = opt_cagr
    log_df.columns['Opt_Absolute_Return'][row_index] = opt_ar
    log_df.columns['User_Bankroll'][row_index] = user_current_br
    log_df.columns['User_CAGR'][row_index] = user_cagr
    log_df.columns['User_Absolute_Return'][row_index] = user_ar

    opt_total_util = 0.0
    opt_total_amt = 0.0
    user_total_util = 0.0
    user_total_amt = 0.0
    # Log the columns that depend on the asset
    for i, curve_id in enumerate(curve_ids):

        if curve_id == expired_curve_id:
            is_expired = 1
        else:
            is_expired = 0

        log_df.columns['{}_Training_Key'.format(curve_id)][row_index] = curve_id
        log_df.columns['{}_Exp_Duration'.format(curve_id)][row_index] = duration_dict[curve_id]
        log_df.columns['{}_Strike_Pct'.format(curve_id)][row_index] = strike_dict[curve_id]

        log_df.columns['{}_Price'.format(curve_id)][row_index] = price_dict[curve_id]
        log_df.columns['{}_Is_Expired'.format(curve_id)][row_index] = is_expired
        log_df.columns['{}_Opt_Premium'.format(curve_id)][row_index] = trade_dict['opt_premium']
        log_df.columns['{}_Opt_Loss'.format(curve_id)][row_index] = results_dict['opt_loss']
        log_df.columns['{}_Opt_Payout'.format(
            curve_id)][row_index] = trade_dict['opt_premium'] + results_dict['opt_loss']
        log_df.columns['{}_Opt_Amount'.format(curve_id)][row_index] = opt_amts_dict[curve_id]
        log_df.columns['{}_Opt_Util'.format(curve_id)][row_index] = opt_util_dict[curve_id]
        log_df.columns['{}_Opt_Locked'.format(curve_id)][row_index] = trade_dict['opt_locked']
        # opt_total_util += trade_dict['opt_util']
        # opt_total_amt += trade_dict['opt_amt']

        log_df.columns['{}_User_Premium'.format(curve_id)][row_index] = trade_dict['user_premium']
        log_df.columns['{}_User_Loss'.format(curve_id)][row_index] = results_dict['user_loss']
        log_df.columns['{}_User_Payout'.format(
            curve_id)][row_index] = trade_dict['user_premium'] + results_dict['user_loss']
        log_df.columns['{}_User_Amount'.format(curve_id)][row_index] = user_amts_dict[curve_id]
        log_df.columns['{}_User_Util'.format(curve_id)][row_index] = user_util_dict[curve_id]
        log_df.columns['{}_User_Locked'.format(curve_id)][row_index] = trade_dict['user_locked']
        # user_total_util += trade_dict['user_util']
        # user_total_amt += trade_dict['user_amt']

    log_df.columns['Opt_Total_Util'][row_index] = opt_total_util
    log_df.columns['Opt_Total_Amt'][row_index] = opt_total_amt
    log_df.columns['User_Total_Util'][row_index] = user_total_util
    log_df.columns['User_Total_Amt'][row_index] = user_total_amt


def validate_inputs(config_dict):
    """
    Checks that the inputs from the config dict needed for the simulation are valid and
    raises a ValueError if not. See create_eval_config()

    Parameters
    ----------
    config_dict : dict
        The dict which configures the object

    Raises
    ------
    ValueError
        If the config is incorrect

    Returns
    -------
    path_length : int
        The length of paths in the simulation
    """
    path_dict = config_dict[PATH_KEY]
    duration_dict = config_dict[DURATION_KEY]
    fit_params = config_dict[FIT_PARAMS_KEY]
    initial_bankroll = config_dict[INIT_BR_KEY]
    util_dict = config_dict[UTIL_KEY]
    strike_dict = config_dict[STRIKE_KEY]
    bf = config_dict[BF_KEY]
    ocp = config_dict[CURVE_PTS_KEY]

    # Check the parameter sizes are correct for the number of assets
    num_assets = len(path_dict.items())
    num_duration_items = len(duration_dict.items())
    num_util_items = len(util_dict.items())
    num_strike_items = len(strike_dict.items())

    if num_duration_items != num_assets:
        raise ValueError('Duration dict incorrect size for '
                         'the number of assets specified: {}'.format(num_duration_items))

    if num_util_items != num_assets:
        raise ValueError('Util dict incorrect size for '
                         'the number of assets specified: {}'.format(num_util_items))

    if num_strike_items != num_assets:
        raise ValueError('Strike dict incorrect size for '
                         'the number of assets specified: {}'.format(num_strike_items))

    # Check the path lengths are all the same
    path_lengths = []
    for i, (key, path) in enumerate(path_dict.items()):
        path_lengths.append(len(path))

    path_len_diff = np.diff(np.asarray(path_lengths))
    diff_sum = np.sum(path_len_diff)

    if diff_sum != 0:
        raise ValueError('The path length for each asset must be equal')

    # Check the path length is valid
    path_length = path_lengths[0]

    if path_length < 2:
        raise ValueError(
            'The path length must be at least 2 to include the start and one expiration')

    # Check each of the durations is valid
    for i, (key, duration) in enumerate(duration_dict.items()):

        if duration < 1 or duration > (path_length - 1):
            raise ValueError('Duration for {} must be at least 1 and less than or equal '
                             'to path_length - 1. Was {}'.format(key, duration))

    for i, (curve_id, params) in enumerate(fit_params.items()):
        if len(params) != 4:
            raise ValueError('Number of fit parameters must be equal to 4 (A, B, C, D)')

    if initial_bankroll < 0.0:
        raise ValueError('Initial Bankroll must be positive')

    # Check the util values are appropriate
    util_sum = 0
    for i, (key, util) in enumerate(util_dict.items()):

        util_sum += util
        if util < 0.0 or util > 1.0:
            raise ValueError('Util for asset {} must be 0 <= u <= 1. Was: {}'.format(key, util))

    if util_sum > 1.0:
        raise ValueError('Sum of all utils must be less than 1.0. Was: {}'.format(util_sum))

    # Check the strikes are valid
    for i, (key, strike_pct) in enumerate(strike_dict.items()):

        if strike_pct <= 0.0:
            raise ValueError('Strike Pct must be positive: {}: {}'.format(key, strike_pct))

    # Check the optimal curve is sized correctly
    if len(bf) != len(ocp):
        raise ValueError('The X and Y points of the optimal premium curve '
                         'must be equal lengths: X:{} Y:{}'.format(len(bf), len(ocp)))

    return path_length


class MultiAssetExpirationEvaluator:
    """
    Helper class that iterates over a given path in the multi asset backtesting simulation and
    checks the outcomes of oToken bets on each expiration
    """

    def __init__(self, config_dict):
        """
        Initializes the MultiAssetExpirationEvaluator according to the config dict passed. See
        create_eval_config()

        Parameters
        ----------
        config_dict : dict
            The dict which configures the object
        """
        path_length = validate_inputs(config_dict)

        path_dict = config_dict[PATH_KEY]
        duration_dict = config_dict[DURATION_KEY]
        fit_params = config_dict[FIT_PARAMS_KEY]
        initial_bankroll = config_dict[INIT_BR_KEY]
        util_dict = config_dict[UTIL_KEY]
        strike_dict = config_dict[STRIKE_KEY]
        bf = config_dict[BF_KEY]
        ocp = config_dict[CURVE_PTS_KEY]

        # Mapping of curve_id -> path
        self.path_dict = path_dict
        self.path_length = path_length
        self.duration_dict = duration_dict
        self.strike_dict = strike_dict
        self.fit_params = fit_params
        self.initial_bankroll = initial_bankroll
        self.user_current_bankroll = initial_bankroll
        self.opt_current_bankroll = initial_bankroll
        self.util_dict = util_dict
        self.bf = bf
        self.ocp = ocp

        self.user_util_state = {}
        self.opt_util_state = {}

        # print(path_dict)
        self.user_amt_state = {}
        self.opt_amt_state = {}
        for i, (curve_id, path) in enumerate(path_dict.items()):
            self.user_util_state[curve_id] = 0.0
            self.opt_util_state[curve_id] = 0.0
            self.user_amt_state[curve_id] = 0.0
            self.opt_amt_state[curve_id] = 0.0

    def calculate_util_and_amount_to_trade(self, current_bankroll, strike_usd, curve_id):
        """
        For a given expiration along the path, calculates the utilization of the LP for
        amount number of oToken contracts

        Parameters
        ----------
        current_bankroll : float
            The bankroll to use in calculations
        strike_usd : float
            The strike of the oToken contract in USD
        curve_id : int
            The id number for the curve

        Returns
        -------
        current_util : float
            The util of the LP at this point along the path
        amount : float
            The amount of otoken contracts to simulate trading
        """
        if strike_usd <= 0.0:
            raise ValueError('Strike must be positive: {}'.format(strike_usd))

        current_util = self.util_dict[curve_id]
        amount = (current_util * current_bankroll) / strike_usd

        return current_util, amount

    def calculate_current_cagr(self, next_bankroll, path_index):
        """
        For a given expiration along the path, calculates the CAGR from the start of the
        simulation until now

        Parameters
        ----------
        next_bankroll : float
            The value of the bankroll at this expiration
        path_index : int
            The index along the path of this expiration (number of days since start)

        Raises
        ------
        ValueError
            If inputs are negative

        Returns
        -------
        current_cagr : float
            The CAGR value for this expiration
        absolute_return : float
            The absolute return for this expiration
        """
        if next_bankroll < 0.0:
            raise ValueError('Next Bankroll is negative: {}'.format(next_bankroll))
        if path_index < 0:
            raise ValueError('Path index is negative: {}'.format(path_index))

        absolute_return = next_bankroll / self.initial_bankroll

        # Note: Assumes one timestep is one day and we can trade every day
        times_per_year = 365.0 / (path_index + 1)

        current_cagr = 100.0 * ((absolute_return ** times_per_year) - 1)

        return current_cagr, absolute_return

    def enter_into_new_trade(self, current_price_dict, curve_id):
        """
        Enters into a new trade of the same type long the path. Input is the current price
        the trade was opened at

        Parameters
        ----------
        current_price_dict : dict
            The current price for each underlying asset along the path
        curve_id : int
            The ID corresponding to the asset we are entering into a trade in

        Returns
        -------
        trade_info : dict
            Dict containing info about the trade
        """
        strike = self.strike_dict[curve_id] * current_price_dict[curve_id]

        # Calculate the amounts to trade for the user's A, B, C, D curve and the optimal curve
        user_util_to_trade, user_amount_to_trade = self.calculate_util_and_amount_to_trade(
            self.user_current_bankroll, strike, curve_id)
        opt_util_to_trade, opt_amount_to_trade = self.calculate_util_and_amount_to_trade(
            self.opt_current_bankroll, strike, curve_id)

        # Get the premium from the on chain curve (fully normalized)
        user_fnp = evaluate_premium_curve(self.fit_params[curve_id], user_util_to_trade)
        idx = (np.abs(np.asarray(self.bf[curve_id]) - opt_util_to_trade)).argmin()
        opt_fnp = self.ocp[curve_id][idx]

        # Calculate the absolute premium and locked collateral to adjust bankrolls
        user_locked, user_premium = calc_premium_and_locked_collateral(
            strike, self.user_current_bankroll, user_fnp, user_util_to_trade)
        opt_locked, opt_premium = calc_premium_and_locked_collateral(
            strike, self.opt_current_bankroll, opt_fnp, opt_util_to_trade)

        # Update the bankroll with the collected premium
        self.user_current_bankroll = self.user_current_bankroll + user_premium
        self.opt_current_bankroll = self.opt_current_bankroll + opt_premium

        # Update the util for the next trade
        self.user_util_state[curve_id] = user_util_to_trade
        self.opt_util_state[curve_id] = opt_util_to_trade

        self.user_amt_state[curve_id] = user_amount_to_trade
        self.opt_amt_state[curve_id] = opt_amount_to_trade

        # Return the util, amount, and locked collateral for the trade
        return {
            'trade_open_price': current_price_dict[curve_id],
            'user_locked': user_locked,
            'user_premium': user_premium,
            'opt_locked': opt_locked,
            'opt_premium': opt_premium
        }

    def determine_trade_results(self, expiration_price, trade_open_price, curve_id):
        """
        Determines the results of the trade and returns the results as a dict for logging

        Parameters
        ----------
        expiration_price : float
            The price along the path at which the contract expired
        trade_open_price : float
            The price at which the trade was originally opened
        curve_id : int
            The ID to use for dicts corresponding to the asset that expired

        Returns
        -------
        trade_dict : dict
            Dict containing the results of the trade
        """
        # Determine the loss (if any)
        relative_exp_price = expiration_price / trade_open_price

        user_loss_pct, user_max_loss = calculate_loss_if_any(
            relative_exp_price, self.user_amt_state[curve_id], self.strike_dict[curve_id])
        opt_loss_pct, opt_max_loss = calculate_loss_if_any(
            relative_exp_price, self.opt_amt_state[curve_id], self.strike_dict[curve_id])

        user_loss = user_loss_pct * trade_open_price
        opt_loss = opt_loss_pct * trade_open_price

        # Update the bankrolls
        self.user_current_bankroll = self.user_current_bankroll + user_loss
        self.opt_current_bankroll = self.opt_current_bankroll + opt_loss

        return {
            'user_loss': user_loss,
            'opt_loss': opt_loss
        }

    def evaluate_expirations_along_path(self, log_df, curve_ids, path_id, current_price_dict,
                                        row_slice):
        """
        Iterates down the path and evaluates the performance of each bet at each expiration. Stores
        performance results in a CSV file. At each timestamp which is an expiration, the trade
        is evaluated for the profit and loss and performance statistics. These values are logged
        to the CSV and the next trade is entered for the next timestamp along the path.

        Parameters
        ----------
        log_df : vaex.dataframe.DataFrame
            The logging dataframe where results are being written
        curve_ids : List[int]
            The list of curve ids in the portfolio being tested
        path_id : int
            The id number for the path in the simulation
        current_price_dict : dict
            The name of each asset mapped to the current price
        row_slice : List[int]
            A slice containing the rows in the dataframe where results will be written for this
            simulation

        Returns
        -------
        None
        """
        # Enter into the initial trades
        last_trade_map = {}
        for i, curve_id in enumerate(curve_ids):

            trade_dict = self.enter_into_new_trade(current_price_dict, curve_id)
            last_trade_map[curve_id] = trade_dict

        user_absolute_return = 1.0
        opt_absolute_return = 1.0
        user_cagr = 0.0
        opt_cagr = 0.0
        for path_index in range(self.path_length):

            # Build map of curve_id to price
            path_dict_at_index = {}
            for curve_id, path in self.path_dict.items():
                path_dict_at_index[curve_id] = path[path_index]

            # Check if each asset has its expiration at this index
            for i, (curve_id, duration) in enumerate(self.duration_dict.items()):

                # If evenly divisible, expires at this index
                if path_index % duration == 0:

                    results_dict = self.determine_trade_results(
                        path_dict_at_index[curve_id], last_trade_map[curve_id]['trade_open_price'],
                        curve_id)
                    row_index = row_slice[path_index]

                    log_expiration_info(
                        log_df, curve_ids, curve_id, path_id, self.fit_params, path_index,
                        path_dict_at_index, self.duration_dict, self.strike_dict,
                        self.user_current_bankroll, self.opt_current_bankroll,
                        user_cagr, user_absolute_return, opt_cagr, opt_absolute_return,
                        self.user_util_state, self.opt_util_state,
                        self.user_amt_state, self.opt_amt_state,
                        last_trade_map[curve_id], results_dict, row_index)

                    trade_dict = self.enter_into_new_trade(path_dict_at_index, curve_id)
                    last_trade_map[curve_id] = trade_dict

            # Calculate performance metrics
            user_cagr, user_absolute_return = self.calculate_current_cagr(
                self.user_current_bankroll, path_index)
            opt_cagr, opt_absolute_return = self.calculate_current_cagr(
                self.opt_current_bankroll, path_index)

"""
This module provides a helper object which encapsulates the logic of iterating over a
path in the simulation and calculating the profit, loss, and performance statistics of the
configured payoff. This object can be run in sequence or in parallel
"""
import numpy as np

from typing import Union
from potion.curve_gen.payoff.builder import PayoffConfigBuilder
from potion.curve_gen.payoff.helpers import expiration_only
from potion.curve_gen.payoff.payoff import (configure_payoff, get_position_max_loss)
from potion.curve_gen.curve_conversion import (convert_fully_normalized_value_to_strike_normalized,
                                               convert_strike_normalized_to_absolute_curve)


PATH_KEY = 'Path'
UTIL_KEY = 'Util'
DURATION_KEY = 'Duration'
STRIKE_KEY = 'Strike'
FIT_PARAMS_KEY = 'Fit'
INIT_BR_KEY = 'InitBR'
BF_KEY = 'BetFr'
CURVE_PTS_KEY = 'CurvePts'


def create_eval_config(path, util: Union[float, np.ndarray], duration, strike_percent, fit_params,
                       initial_bankroll, bf, ocp):
    """
    Creates a config dict to initialize the ExpirationEvaluator class. The class is simulating a
    buyer purchasing a certain number of contracts over time.

    Parameters
    -----------
    path : List[float]
        The path being evaluated in the backtesting simulation
    util : float
        The amount the user buys as a new bet at each expiration or a fixed util
    duration : int
        The number of days between each expiration. 1 is every day, 2 every other, etc.
    strike_percent : float
        The strike in percentage ATM where 1.0 is ATM
    fit_params : List[float]
        The fit parameters for the user curve A, B, C, D
    initial_bankroll : float
        The initial starting capital in our backtesting simulation
    bf : List[float]
        The bet fractions (X axis) of the kelly generated bonding curve
    ocp : List[float]
        The optimal curve points (Y axis) of the kelly generated bonding curve

    Returns
    -----------
    config : dict
        The config dict
    """
    config = {
        PATH_KEY: path,
        UTIL_KEY: util,
        DURATION_KEY: duration,
        STRIKE_KEY: strike_percent,
        FIT_PARAMS_KEY: fit_params,
        INIT_BR_KEY: initial_bankroll,
        BF_KEY: bf,
        CURVE_PTS_KEY: ocp
    }

    return config


def _evaluate_premium_curve(fit_params, util):
    """
    Function to calculate the premium of a fit curve

    Parameters
    -----------
    fit_params : List[float]
        The A, B, C, D values of the curve
    util : float
        The util percentage that is the function input

    Raises
    -----------
    ValueError
        If the util is not between 0.0 and 1.0, or if the fit_params are not positive numbers

    Returns
    -----------
    float
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


def _calculate_loss_if_any(expiration_price, amount, strike_pct):
    """
    Calculates the payout of the expired contract.

    Parameters
    -----------
    expiration_price : float
        The price at which the contract expired
    amount : float
        The number of contracts which were purchased by the buyer
    strike_pct : float
        The strike price of the contract

    Raises
    -----------
    ValueError
        If the amount of contracts traded is not a positive number

    Returns
    -----------
    payout: List[float]
        The payout value of the contract at the expiration price
    position_max_loss: float
        The max possible loss of the position
    """
    if amount < 0.0:
        raise ValueError('The amount of contracts traded must be positive')

    sample_points = np.linspace(1e-20, 2.0, 100)
    sample_points = np.append(sample_points, expiration_price)
    sample_points = np.sort(sample_points)
    exp_price_index = np.where(sample_points == expiration_price)[0][0]

    cfg = PayoffConfigBuilder().set_x_points(sample_points).add_option_leg(
        'put', 'short', amount, strike_pct).set_payoff_function(expiration_only).build_config()
    configure_payoff(cfg)
    max_loss = get_position_max_loss()

    # Get the outcome corresponding to our sample point
    return cfg.total_payoff[exp_price_index], max_loss


def _calc_premium_and_locked_collateral(strike, current_bankroll, fully_norm_prem, util_total):
    """
    Calculates the amount of premium collected and collateral locked in absolute terms to be
    added to the bankroll

    Parameters
    -----------
    strike : float
        The strike in absolute value
    current_bankroll : float
        The current bankroll along the path
    fully_norm_prem : float
        The premium output from the curve generator
    util_total
        The total util along the curve in use

    Returns
    -----------
    absolute_locked_collateral: float
        The amount of collateral locked in absolute terms
    absolute_premium: float
        The premium collected in absolute terms
    """
    # print('fnp: {}'.format(fully_norm_prem))

    strike_normalized_premium = convert_fully_normalized_value_to_strike_normalized(
        strike, current_bankroll, util_total, fully_norm_prem)

    # print(strike_normalized_premium)

    (absolute_locked_collateral,
     absolute_premium) = convert_strike_normalized_to_absolute_curve(strike,
                                                                     current_bankroll,
                                                                     util_total,
                                                                     strike_normalized_premium)

    return absolute_locked_collateral, absolute_premium


def _validate_inputs(config_dict):
    """
    Checks that the inputs from the config dict needed for the simulation are valid and
    raises a ValueError if not. See create_eval_config()

    Parameters
    -----------
    config_dict : dict
        The dict which configures the object

    Raises
    -----------
    ValueError
        If the dict is not correctly configured

    Returns
    -----------
    util: float
        The amount the user buys as a new bet at each expiration or a fixed util
    simulation_type: bool
        The simulation type whether the a_or_u array represents an amount bought or sold
        along the path or a util for the LP to keep constant
    """
    path = config_dict[PATH_KEY]
    duration = config_dict[DURATION_KEY]
    fit_params = config_dict[FIT_PARAMS_KEY]
    initial_bankroll = config_dict[INIT_BR_KEY]
    amounts_or_util = config_dict[UTIL_KEY]

    if len(path) < 2:
        raise ValueError(
            'The path length must be at least 2 to include the start and one expiration')
    if duration < 1 or duration > (len(path) - 1):
        raise ValueError('Duration must be at least 1 and less than path length - 1')
    if len(fit_params) != 4:
        raise ValueError('Number of fit parameters must be equal to 4 (A, B, C, D)')
    if initial_bankroll < 0.0:
        raise ValueError('Initial Bankroll must be positive')

    # Get the indices along the path where there is an expiration to evaluate
    path_length = len(path)

    if type(amounts_or_util) is float:

        # As a float, util is a fixed util
        if amounts_or_util > 1.0 or amounts_or_util < 0.0:
            raise ValueError('As a float specifying a fixed util, util must be between 0 and 1')

        util = amounts_or_util
        sim_type = True

    elif type(amounts_or_util) is np.ndarray:

        expiration_indices = np.arange(duration, path_length, duration)
        # As an array, util is the amount of otoken contracts to buy at each timestep
        if len(amounts_or_util) > (len(path) - 1):
            raise ValueError(
                'The history of user buys (amounts array) must be less than the length of the path')
        if len(amounts_or_util) != len(expiration_indices):
            raise ValueError('Amounts and Expiration Indices must be same length a: {} and ei: {}'
                             .format(len(amounts_or_util), len(expiration_indices)))
        util = amounts_or_util[(expiration_indices - 1)]
        sim_type = False

    else:
        raise ValueError('Unknown type for parameter amounts: {}'.format(amounts_or_util))

    return util, sim_type


class ExpirationEvaluator:

    def __init__(self, config_dict):
        """
        Helper class that iterates over a given path in the backtesting simulation and
        checks the outcomes of contract bets on each expiration. Initializes the class
        according to the config dict passed. See create_eval_config()

        Parameters
        -----------
        config_dict : dict
            The dict which configures the object
        """
        a_or_u, sim_type = _validate_inputs(config_dict)

        path = config_dict[PATH_KEY]
        duration = config_dict[DURATION_KEY]
        fit_params = config_dict[FIT_PARAMS_KEY]
        initial_bankroll = config_dict[INIT_BR_KEY]
        strike_percent = config_dict[STRIKE_KEY]

        self.path = path
        self.duration = duration
        self.strike_percent = strike_percent
        self.fit_params = fit_params
        self.initial_bankroll = initial_bankroll
        self.user_current_bankroll = initial_bankroll
        self.opt_current_bankroll = initial_bankroll
        self.amounts_or_util = a_or_u
        self.sim_type = sim_type
        self.bf = config_dict[BF_KEY]
        self.ocp = config_dict[CURVE_PTS_KEY]

    def _calculate_util_and_amount_to_trade(self, current_bankroll, strike_usd, index):
        """
        For a given expiration along the path, calculates the utilization of the LP for
        amount number of contracts

        Parameters
        -----------
        current_bankroll : float
            The bankroll to use in calculations
        strike_usd : float
            The strike of the oToken contract in USD
        index : int
            The index in the array of amounts in our loop

        Raises
        -----------
        ValueError
            If strike_usd is not positive

        Returns
        -----------
        current_util: float
            The util of the LP at this time step along the path
        amount: float
            The amount of contracts to trade at this time step
        """
        if strike_usd <= 0.0:
            raise ValueError('Strike must be positive: {}'.format(strike_usd))

        # When configured as a constant util, the util parameter is a float representing the util
        if self.sim_type:

            current_util = self.amounts_or_util
            amount = (current_util * current_bankroll) / strike_usd
        else:

            # The collateral here will equal the strike because the contract multiplier is 1
            amount = self.amounts_or_util[index]
            current_util = (strike_usd * amount) / current_bankroll

        return current_util, amount

    def _calculate_current_cagr(self, next_bankroll, duration, path_index):
        """
        For a given expiration along the path, calculates the CAGR from the start of the
        simulation until now

        Parameters
        -----------
        next_bankroll : float
            The value of the bankroll at this expiration
        duration : int
            The duration until the option expires
        path_index : int
            The index along the path of this expiration (number of days since start)

        Raises
        -----------
        ValueError
            If next_bankroll is negative, if the path_index is negative, or if duration < 1

        Returns
        -----------
        current_cagr: float
            The CAGR value for this expiration
        absolute_return: float
            The absolute return from the start until now
        """
        if next_bankroll < 0.0:
            raise ValueError('Next Bankroll is negative: {}'.format(next_bankroll))
        if path_index < 0:
            raise ValueError('Path index is negative: {}'.format(path_index))
        if duration < 1:
            raise ValueError('Duration must be 1 or more: {}'.format(duration))

        absolute_return = next_bankroll / self.initial_bankroll

        # Note: Assumes one timestep is one day and we can trade every day
        times_per_year = 365.0 / (path_index + 1)

        current_cagr = 100.0 * ((absolute_return ** times_per_year) - 1)

        return current_cagr, absolute_return

    def _enter_into_new_trade(self, current_price):
        """
        Enters into a new trade of the same type long the path. Input is the current price
        the trade was opened at

        Parameters
        -----------
        current_price : float
            The current price along the path

        Returns
        -----------
        results : dict
            Dict containing info about the trade
        """
        user_util_before = 0.0
        opt_util_before = 0.0
        strike = self.strike_percent * current_price

        # Calculate the amounts to trade for the user's A, B, C, D curve and the optimal curve
        user_util_to_trade, user_amount_to_trade = self._calculate_util_and_amount_to_trade(
            self.user_current_bankroll, strike, 0)
        opt_util_to_trade, opt_amount_to_trade = self._calculate_util_and_amount_to_trade(
            self.opt_current_bankroll, strike, 0)

        # Get the total util
        user_util_on_curve = user_util_before + user_util_to_trade
        opt_util_on_curve = opt_util_before + opt_util_to_trade

        # Get the premium from the on chain curve (fully normalized)
        user_fnp = _evaluate_premium_curve(self.fit_params, user_util_on_curve)
        idx = (np.abs(self.bf - opt_util_on_curve)).argmin()
        opt_fnp = self.ocp[idx]

        # Calculate the absolute premium and locked collateral to adjust bankrolls
        user_locked, user_premium = _calc_premium_and_locked_collateral(
            strike, self.user_current_bankroll, user_fnp, user_util_on_curve)
        opt_locked, opt_premium = _calc_premium_and_locked_collateral(
            strike, self.opt_current_bankroll, opt_fnp, opt_util_on_curve)

        # Update the bankroll with the collected premium
        user_original = self.user_current_bankroll
        opt_original = self.opt_current_bankroll
        self.user_current_bankroll = self.user_current_bankroll + user_premium
        self.opt_current_bankroll = self.opt_current_bankroll + opt_premium

        # Return the util, amount, and locked collateral for the trade
        return {
            'trade_open_price': current_price,
            'user_util': user_util_on_curve,
            'user_amt': user_amount_to_trade,
            'user_locked': user_locked,
            'user_br': user_original,
            'user_premium': user_premium,
            'opt_util': opt_util_on_curve,
            'opt_amt': opt_amount_to_trade,
            'opt_locked': opt_locked,
            'opt_br': opt_original,
            'opt_premium': opt_premium
        }

    def _determine_trade_results(self, path_index, expiration_price, trade_dict):
        """
        Determines the results of the trade and returns the results as a dict for logging

        Parameters
        -----------
        path_index : int
            The index identifying the backtesting path
        expiration_price : float
            The price at which the expiration happened
        trade_dict : dict
            Dict containing info about the open trade

        Returns
        -----------
        results : dict
            Dict containing the results of the trade
        """

        # Determine the loss (if any)
        trade_open_price = trade_dict['trade_open_price']
        relative_exp_price = expiration_price / trade_open_price

        user_loss_pct, user_max_loss = _calculate_loss_if_any(
            relative_exp_price, trade_dict['user_amt'], self.strike_percent)
        opt_loss_pct, opt_max_loss = _calculate_loss_if_any(
            relative_exp_price, trade_dict['opt_amt'], self.strike_percent)

        user_loss = user_loss_pct * trade_open_price
        opt_loss = opt_loss_pct * trade_open_price

        # print('ul: {} ol: {}'.format(user_loss_pct, opt_loss_pct))

        # Update the bankrolls
        self.user_current_bankroll = self.user_current_bankroll + user_loss
        self.opt_current_bankroll = self.opt_current_bankroll + opt_loss

        # Calculate performance metrics
        user_cagr, user_absolute_return = self._calculate_current_cagr(
            self.user_current_bankroll, self.duration, path_index)
        opt_cagr, opt_absolute_return = self._calculate_current_cagr(
            self.opt_current_bankroll, self.duration, path_index)

        return {
            'user_cagr': user_cagr,
            'user_ar': user_absolute_return,
            'user_loss': user_loss,
            'opt_cagr': opt_cagr,
            'opt_ar': opt_absolute_return,
            'opt_loss': opt_loss
        }

    def _log_expiration_info(self, log_df, training_key, path_id, path_index, expiration_price,
                             trade_dict, results_dict, row_index):
        """
        Logs information about one expiration along the path.

        Parameters
        -----------
        log_df : vaex.dataframe.DataFrame
            The logging dataframe
        training_key : str
            The key identifying the training data
        path_id : int
            The id number for the backtesting path
        path_index : int
            The timestamp along the path
        expiration_price : float
            The price along the path at the expiration
        trade_dict : dict
            Dict containing info about when the trade was entered
        results_dict : dict
            Dict containing info about the results of the trade
        row_index : int
            The log df row number to write to

        Returns
        -----------
        None
        """
        log_df.columns['Timestamp'][row_index] = int(path_index)
        log_df.columns['Training_Key'][row_index] = training_key
        log_df.columns['Exp_Duration'][row_index] = self.duration
        log_df.columns['Strike_Pct'][row_index] = self.strike_percent
        log_df.columns['Path_ID'][row_index] = path_id
        log_df.columns['Expiration_Price'][row_index] = expiration_price
        log_df.columns['A'][row_index] = self.fit_params[0]
        log_df.columns['B'][row_index] = self.fit_params[1]
        log_df.columns['C'][row_index] = self.fit_params[2]
        log_df.columns['D'][row_index] = self.fit_params[3]
        log_df.columns['Opt_Premium'][row_index] = trade_dict['opt_premium']
        log_df.columns['Opt_Loss'][row_index] = results_dict['opt_loss']
        log_df.columns['Opt_Payout'][row_index] = trade_dict[
                                                      'opt_premium'] + results_dict['opt_loss']
        log_df.columns['Opt_Amount'][row_index] = trade_dict['opt_amt']
        log_df.columns['Opt_Util'][row_index] = trade_dict['opt_util']
        log_df.columns['Opt_Locked'][row_index] = trade_dict['opt_locked']
        log_df.columns['Opt_Bankroll'][row_index] = trade_dict['opt_br']
        log_df.columns['Opt_CAGR'][row_index] = results_dict['opt_cagr']
        log_df.columns['Opt_Absolute_Return'][row_index] = results_dict['opt_ar']
        log_df.columns['User_Premium'][row_index] = trade_dict['user_premium']
        log_df.columns['User_Loss'][row_index] = results_dict['user_loss']
        log_df.columns['User_Payout'][row_index] = trade_dict[
                                                       'user_premium'] + results_dict['user_loss']
        log_df.columns['User_Amount'][row_index] = trade_dict['user_amt']
        log_df.columns['User_Util'][row_index] = trade_dict['user_util']
        log_df.columns['User_Locked'][row_index] = trade_dict['user_locked']
        log_df.columns['User_Bankroll'][row_index] = trade_dict['user_br']
        log_df.columns['User_CAGR'][row_index] = results_dict['user_cagr']
        log_df.columns['User_Absolute_Return'][row_index] = results_dict['user_ar']

    def evaluate_expirations_along_path(self, log_df, training_key, path_id,
                                        current_price, row_slice):
        """
        Iterates down the path and evaluates the performance of each bet at each expiration. Stores
        performance results in a dataframe file. At each timestamp which is an expiration,
        the trade is evaluated for the profit and loss and performance statistics. These values
        are logged to the file and the next trade is entered for the next timestamp along the path.

        Parameters
        -----------
        log_df : vaex.dataframe.DataFrame
            The logging dataframe
        training_key : str
            The key identifying the training data
        path_id : int
            The id number for the backtesting path
        current_price : float
            The current price of the asset when we start the simulation
        row_slice: List[int]
            The list of ints corresponding to the rows in log_df to write to

        Returns
        -----------
        None
        """
        # Enter into the initial trade
        trade_dict = self._enter_into_new_trade(current_price)
        count = 0
        for path_index, path_price in enumerate(self.path):

            # If the index along the path is one with an expiration
            if path_index % self.duration == 0:

                results_dict = self._determine_trade_results(path_index, path_price, trade_dict)

                self._log_expiration_info(log_df, training_key, path_id, path_index, path_price,
                                          trade_dict, results_dict, row_slice[count])

                trade_dict = self._enter_into_new_trade(path_price)
                count += 1

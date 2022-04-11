"""
This module contains utility functions which are helpful for the curve generation process
"""
import pandas as pd
import numpy as np

from typing import List
from datetime import datetime

from potion.curve_gen.payoff.helpers import black_scholes_payoff
from potion.curve_gen.payoff.builder import PayoffConfigBuilder
from potion.curve_gen.convolution.builder import ConvolutionConfigBuilder
from potion.curve_gen.convolution.convolution import get_pdf_arrays
from potion.curve_gen.training.distributions.skewed_students_t import skewed_t
from potion.curve_gen.training.builder import TrainingConfigBuilder
from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder
from potion.curve_gen.kelly_fit.builder import FitConfigBuilder
from potion.curve_gen.builder import GeneratorConfigBuilder


def make_payoff_dict(call_or_put='call', direction='long', amount=1.0,
                     time_to_exp=0.0, sigma=0.0, r=0.0, q=0.0):
    """
    Helper function to easily create a payoff dict for configuring the payoff of the curve
    generator using the helper functions. By specifying the default parameters the user
    is free to only specify the parameters they are interested in changing.

    Parameters
    ----------
    call_or_put : str
        (Optional. Default: 'call') Whether the leg is a Call or a Put. Use 'call' or 'put'
    direction : str
        (Optional. Default: 'long') Whether the leg is Long or Short. Use 'long' or 'short'
    amount : float
        (Optional. Default: 1.0) The contract multiplier for the simulated option
    time_to_exp : float
        (Optional. Default: 0.0) The time until expiration in years, where 0.0 is expired
    sigma : float
        (Optional. Default: 0.0) The annualized volatility. Default 0.0 at expiration
    r : float
        (Optional. Default: 0.0) The annualized interest rate.
    q : float
        (Optional. Default: 0.0) The annualized rate of return from cash flows of the underlying
        like a dividend or payouts from staking.

    Returns
    -------
    payoff_dict : dict
        The dict containing all of the parameters for a payoff calculation
    """
    return {
        'type': call_or_put,
        'dir': direction,
        'amt': amount,
        't': time_to_exp,
        'sigma': sigma,
        'r': r,
        'q': q
    }


def add_leg_to_dict(payoff_dict, strike, call_or_put='call', direction='long', amount=1.0,
                    time_to_exp=0.0, sigma=0.0, r=0.0, q=0.0):
    """
    Adds a new leg to the payoff and returns the updated dict for use

    Parameters
    ----------
    payoff_dict : dict
        The payoff dict which is having a leg added
    strike : float
        The strike at which to add this leg
    call_or_put : str
        (Optional. Default: 'call') Whether the leg is a Call or a Put. Use 'call' or 'put'
    direction : str
        (Optional. Default: 'long') Whether the leg is Long or Short. Use 'long' or 'short'
    amount : float
        (Optional. Default: 1.0) The contract multiplier for the simulated option
    time_to_exp : float
        (Optional. Default: 0.0) The time until expiration in years, where 0.0 is expired
    sigma : float
        (Optional. Default: 0.0) The annualized volatility. Default 0.0 at expiration
    r : float
        (Optional. Default: 0.0) The annualized interest rate.
    q : float
        (Optional. Default: 0.0) The annualized rate of return from cash flows of the underlying
        like a dividend or payouts from staking.

    Returns
    -------
    payoff_dict : dict
        The dict containing all of the parameters for a payoff calculation
    """
    if 'other_legs' not in payoff_dict:
        payoff_dict['other_legs'] = []
    payoff_dict['other_legs'].append({
        'type': call_or_put,
        'dir': direction,
        'amt': amount,
        'strike': strike,
        't': time_to_exp,
        'sigma': sigma,
        'r': r,
        'q': q
    })

    return payoff_dict


def make_payoff_cfg(x_pts, strike_pct: float, payoff_dict, payoff_fcn=black_scholes_payoff):
    """
    Creates a PayoffConfig object from the payoff configuration dict and convolution info using
    the builder objects.

    Parameters
    ----------
    x_pts : numpy.ndarray
        The price points at which the payoff function will be calculated
    strike_pct : float
        The strike at which the payoff function is being calculated in percent of ATM
    payoff_dict : dict
        A dict specifying the payoff or spread being calculated. See make_payoff_dict for more info
    payoff_fcn
        (Optional. Default: black_scholes_payoff) The payoff function to use calculating the curves

    Returns
    -------
    cfg : PayoffConfig
        The configuration object for the payoff
    """
    builder = PayoffConfigBuilder().set_x_points(x_pts).set_payoff_function(payoff_fcn)

    if 'type' in payoff_dict and 'dir' in payoff_dict and 'amt' in payoff_dict:
        builder.add_option_leg(
            call_or_put=payoff_dict['type'], direction=payoff_dict['dir'],
            amount=payoff_dict['amt'], time_to_exp=payoff_dict['t'], sigma=payoff_dict['sigma'],
            r=payoff_dict['r'], q=payoff_dict['q'], strike=strike_pct
        )

    if 'und_price' in payoff_dict and 'und_amt' in payoff_dict:
        builder.set_underlying_payoff_leg(
            underlying_price=payoff_dict['und_price'], underlying_amount=payoff_dict['und_amt'])

    if 'other_legs' in payoff_dict:
        for leg in payoff_dict['other_legs']:
            builder.add_option_leg(call_or_put=leg['type'], direction=leg['dir'], amount=leg['amt'],
                                   strike=leg['strike'], time_to_exp=leg['t'], sigma=leg['sigma'],
                                   r=leg['r'], q=leg['q'])

    return builder.build_config()


def build_generator_config(input_file: str, training_history_file: str, payoff_dict=None,
                           lower_bounds_fcns=None, upper_bounds_fcns=None):
    """
    Creates a configuration object for the curve generation process from the two
    input file names

    Parameters
    ----------
    input_file : str
        The input file specifying the curves to generate
    training_history_file : str
        The input file containing the price histories for training data
    payoff_dict : dict
        A dict containing information about the payoff like long/short, put/call, etc.
    lower_bounds_fcns : List[Callable]
        A List containing the callable lower bound functions for the premiums when
        running the optimizer
    upper_bounds_fcns : List[Callable]
        A List containing the callable upper bound functions for the premiums when
        running the optimizer

    Returns
    -------
    config : GeneratorConfig
        The configuration to use for curve generation
    """
    training_config = TrainingConfigBuilder().set_input_csv_filename(
        input_file).set_training_history_filename(training_history_file)

    bounds_cfg = ConstraintsConfigBuilder()
    if payoff_dict is not None:

        if 'dir' not in payoff_dict or payoff_dict['dir'] == 'long':
            bounds_cfg.add_upper_bound(lambda a: -1e-10)
            bounds_cfg.add_lower_bound(lambda a: -1.0)
        else:
            bounds_cfg.add_upper_bound(lambda a: 1.0)
            bounds_cfg.add_lower_bound(lambda a: 1e-10)
    else:
        bounds_cfg.add_upper_bound(lambda a: 1.0)
        bounds_cfg.add_lower_bound(lambda a: 1e-10)

    if lower_bounds_fcns is not None:
        [bounds_cfg.add_lower_bound(func) for func in lower_bounds_fcns]

    if upper_bounds_fcns is not None:
        [bounds_cfg.add_upper_bound(func) for func in upper_bounds_fcns]

    return GeneratorConfigBuilder().set_training_builder(training_config).set_bounds_builder(
        bounds_cfg).set_fit_builder(FitConfigBuilder()).build_config()


def training_output_to_csv(dfs: List[pd.DataFrame]):
    """
    Takes the DataFrames output from the training process and repackages the output
    into the CSV format expected by the backtester and other areas of the tool

    Parameters
    ----------
    dfs : List[pandas.DataFrame]
        The List of DataFrames output by the training process which needs repackaging

    Returns
    -------
    training_df : pandas.DataFrame
        The DataFrame containing all of the information obtained from the training process
    """
    rows = [{
        'Ticker': row.Asset,
        'Label': row.TrainingLabel,
        'CurrentPrice': row.CurrentPrice,
        'StartDate': datetime.strftime(row.TrainingStart, '%d/%m/%Y'),
        'EndDate': datetime.strftime(row.TrainingEnd, '%d/%m/%Y'),
        'TrainingPrices': row.TrainingPrices
    } for df in dfs for index, row in df.iterrows()]

    return pd.DataFrame(rows).drop_duplicates(subset=['Ticker', 'Label',
                                                      'CurrentPrice', 'StartDate',
                                                      'EndDate']).reset_index(drop=True)


def training_output_to_convolution_config(dfs, min_x=-5.0, max_x=5.0, log_only=False,
                                          pdf_pts=20001, dist=skewed_t):
    """
    Takes the DataFrames output from the training process and repackages the output
    into the format needed for the convolution module

    Parameters
    ----------
    dfs : List[pandas.DataFrame]
        The List of DataFrames output by the training process which needs repackaging
    min_x : float
        (Optional. Default: -5.0) The minimum value in the log return domain
    max_x : float
        (Optional. Default: 5.0) The maximum value in the log return domain
    log_only : bool
        (Optional. Default: False) Whether to only use the log return domain in convolution
    pdf_pts : int
        (Optional. Default: 20001) The number of points in the convolution PDF
    dist : scipy.stats.rv_continuous
        (Optional. Default: skewed_t) The probability distribution which is being fit to
        the training data returns

    Returns
    -------
    conv_cfgs : List[ConvolutionConfig]
        The List of ConvolutionConfigs used to configure the convolution module
    """
    conv_cfgs = []
    for df in dfs:
        params = df['DistParams'].values[0]
        args = tuple(params[2:])

        conv_cfgs.append(ConvolutionConfigBuilder().set_num_times_to_convolve(
            df['Expiration'].max()).set_min_x(min_x).set_max_x(max_x).set_log_only(
            log_only).set_points_in_pdf(pdf_pts).set_distribution(
            dist(*args, loc=params[0], scale=params[1]).pdf).set_distribution_params(
            params).build_config())

    return conv_cfgs


def training_output_to_payoff_config(dfs, conv_configs, payoff_dict=None):
    """
    Takes the DataFrames output from the training process and repackages the output
    into the format needed for configuring the payoff during curve generation.

    Parameters
    ----------
    dfs : List[pandas.DataFrame]
        The List of DataFrames output by the training process which is used to configure the payoff
    conv_configs : List[ConvolutionConfig]
        The List of ConvolutionConfigs used to configure the convolution module
    payoff_dict : dict
        (Optional) The payoff dict specifying the info used to calculate the curves. By default,
        this specifies a short put. This can be used to specify other individual options or an
        option spread. See make_payoff_dict for more info

    Returns
    -------
    payoff_cfgs : List[List[PayoffConfig]]
        The PayoffConfig objects which will be used in curve generation for each strike and
        convolution group
    """
    if payoff_dict is None:
        payoff_dict = make_payoff_dict(call_or_put='put', direction='short')

    return [[make_payoff_cfg(conv_cfg.x, strike_pct, payoff_dict)
             for strike_pct in df['StrikePct'].values] for df, conv_cfg in zip(dfs, conv_configs)]


def add_pdf_csv_columns(exp_days: np.ndarray, column_names: List[str],
                        column_data: List[pd.DataFrame], asset_name: str, training_label: str,
                        get_pdfs_fcn=get_pdf_arrays):
    """
    Reformates the output of the convolution process into columns which will be compiled into
    an output DataFrame. This function adds a set of columns to the List from the current output
    batch.

    Parameters
    ----------
    exp_days : numpy.ndarray
        The expiration days
    column_names : List[str]
        The List of names for the columns
    column_data : List[pandas.DataFrame]
        The List of column data
    asset_name : str
        The name of the asset for which the PDFs correspond
    training_label : str
        The label for the training set for which the PDFs correspond
    get_pdfs_fcn : Callable
        (Optional. Default: get_pdf_arrays) The function which gets the current PDFs from the
        convolution module

    Returns
    -------
    column_names : List[str]
        The List of names for the columns in the output DataFrame
    column_data : List[pandas.DataFrame]
        The column data in the output DataFrame
    """
    pdf_x, pdfs_y = get_pdfs_fcn()

    uexps = np.unique(exp_days)
    for exp_idx, exp_day in enumerate(uexps):

        if not column_data:
            column_data = [pd.Series(pdf_x)]
            column_names = ['Prices']

        column_names.append(asset_name + '-' + training_label + '|' + str(exp_day))
        column_data.append(pd.DataFrame(pdfs_y[exp_idx]))

    return column_names, column_data


def add_curve_csv_rows(df: pd.DataFrame, outputs, dist_params,
                       bet_fractions=np.linspace(0.0, 0.9999, 50)):
    """
    Reformats the output of the curve generation process into rows which will be compiled into
    the output DataFrame. This function adds a set of rows to the List from the current output
    batch.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame output by the training process for the current curve batch
    outputs : List[dict]
        The List containing the output dicts for each curve from the curve generation
    dist_params : List[float]
        The List of parameters for the PDF
    bet_fractions : numpy.ndarray
        The X axis points for each curve

    Returns
    -------
    rows : List[dict]
        A List of dicts which will be used to build the curve output CSV
    """
    conv_rows = []
    for df_idx, out_dict in enumerate(outputs):

        if len(out_dict['payoff'].option_legs) > 0:
            strike = out_dict['payoff'].option_legs[0]['strike']
        else:
            strike = 1.0
        exp = out_dict['exp']
        params = out_dict['params']
        premium = out_dict['prem']

        conv_rows.append({
            'Ticker': df['Asset'].values[0],
            'Label': df['TrainingLabel'].values[0],
            'Expiration': exp,
            'StrikePercent': strike,
            'A': params[0],
            'B': params[1],
            'C': params[2],
            'D': params[3],
            't_params': dist_params,
            'bet_fractions': bet_fractions,
            'curve_points': premium
        })

    # Reversed because iterating backwards
    return list(reversed(conv_rows))


def create_key(ticker: str, sentiment: str):
    """
    Helper function which combines a ticker and sentiment label into a single key in a
    common format so that we can iterate over the unique combinations

    Parameters
    ----------
    ticker : str
        The ticker string
    sentiment : str
        A label for the training data to describe it like 'bull' or 'past 6 months'

    Returns
    -------
    key : str
        str containing ticker-sentiment
    """
    return ticker + '-' + sentiment


def get_ticker_from_key(key: str):
    """
    Helper function which extracts just the ticker name from a given key

    Parameters
    ----------
    key : str
        The key from which we want to get the ticker name

    Returns
    -------
    ticker : str
        str The ticker string
    """
    return key.split('-')[0]


def get_sentiment_label_from_key(key: str):
    """
    Helper function which extracts just the sentiment label name from a given key

    Parameters
    ----------
    key : str
        The key from which we want to get the sentiment label name

    Returns
    -------
    label : str
        str The label string
    """
    return key.split('-')[1]

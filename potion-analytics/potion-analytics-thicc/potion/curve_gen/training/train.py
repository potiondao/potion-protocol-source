"""
This module is used by the Generator for importing the input CSV and training data CSVs
used for curve generation. Using the inputs specified in the files, the module will
extract the historical training data, calculate the financial returns of the data,
and fit those returns to a specified probability distribution which will be used as the
mathematical model during curve generation.

This is done using a class which follows the duck typed interface of the Generator
and is used by it to create Kelly curves.

Callers who wish to replace or customize the behavior of this module need only implement
three duck typed functions:

    configure_training(TrainingConfig)
        'Configures the settings of this module. See builder for more info
        on TrainingConfig'
    train(*args)
        'Which performs the training using the specified CSV files'

Like many python libraries, this module uses a global object with the methods prebound so that
the same library can be used by object-oriented and functional programmers alike. Object-oriented
users can use the Payoff class, and functional programmers can use the functions described above.
"""
import numpy as np
import pandas as pd
import datetime
from typing import List

from potion.curve_gen.training.fit.helpers import calc_log_returns
from potion.curve_gen.training.distributions.skewed_students_t import skewed_t
from potion.curve_gen.training.builder import TrainingConfig, TrainingConfigBuilder

# Date column name in backtesting input CSV
COL_KEY_PRICE_HIST_DATES = 'Master calendar'


def get_training_dates(csv_df):
    """
    Loads the training data from a CSV file

    Parameters
    ----------
    csv_df : pandas.DataFrame
        The DataFrame containing the training data history

    Returns
    -------
    price_history_dates : numpy.ndarray
        A numpy array containing the datetime objects of the training data samples
        parsed from the input
    """
    price_history_dates = csv_df[COL_KEY_PRICE_HIST_DATES]
    price_history_dates = np.asarray([datetime.datetime.strptime(day, '%d/%m/%Y').date()
                                      for day in price_history_dates])

    return price_history_dates


def parse_date_from_str(date_str: str, path_dates: np.ndarray, path_prices: pd.DataFrame,
                        limit_str='min', limit_idx=0, frmt='%d/%m/%Y'):
    """
    Parses a date object from a date string according to the format of the input CSV.

    Parameters
    ----------
    date_str : str
        The string being parsed into a date
    path_dates : numpy.ndarray
        The dates along the historical price path where we have price values
    path_prices : pd.DataFrame
        The price values along the historical price path
    limit_str : str
        (Optional. Default: 'min') The string to identify a unique index like 'min' or 'max' date
    limit_idx
        (Optional. Default: 0) The index identified by limit_str, like 0 or -1 for
        'min' and 'max' date
    frmt : str
        (Optional. Default: '%d/%m/%Y') Set the format for the date string

    Returns
    -------
    parsed_date : date
        The date object that was parsed from date_str
    parsed_index : int
        The index where the datetime object is located along the path
    """

    if date_str == limit_str:
        parsed_index = path_prices.index[limit_idx]
        parsed_date = path_dates[parsed_index]
    else:
        parsed_date = datetime.datetime.strptime(date_str, frmt).date()
        parsed_index = np.where(path_dates == parsed_date)[0][0]

    return parsed_date, parsed_index


def _extract_historical_price_path(csv_df: pd.DataFrame, price_history_dates: np.ndarray,
                                   ticker: str, start_date_str: str, end_date_str: str,
                                   frmt='%d/%m/%Y'):
    """
    Takes a given training_set_dict supplied by the builder, along with the imported
    training data and parsed dates to extract the window of training data.

    Parameters
    ----------
    csv_df : pandas.DataFrame
        The DataFrame containing the price histories imported from the CSV file
    price_history_dates : numpy.ndarray
        The dates along the historical price path where we have price values
    ticker : str
        The name of the asset in the CSV
    start_date_str : str
        The start date of the training window as a string
    end_date_str : str
        The end date of the training window as a string
    frmt : str
        (Optional. Default: '%d/%m/%Y') Sets the format of the date strings

    Returns
    -------
    start_date : datetime
        The stating date as a datetime object
    end_date : datetime
        The ending date as a datetime object
    price_path : numpy.ndarray
        The price path selected as the training window data between start_date and end_date
    """
    # Get the full price history for the asset where a training set is being selected
    full_price_path = csv_df[ticker].dropna()

    # Get the datetime objects and index in the array for the start and end date
    start_date, starting_index = parse_date_from_str(start_date_str,
                                                     price_history_dates, full_price_path,
                                                     limit_str='min', limit_idx=0,
                                                     frmt=frmt)
    end_date, ending_index = parse_date_from_str(end_date_str,
                                                 price_history_dates, full_price_path,
                                                 limit_str='max', limit_idx=-1,
                                                 frmt=frmt)

    # Get the price history corresponding to the training window selected
    price_path = full_price_path.loc[starting_index:ending_index].copy()

    return start_date, end_date, price_path.to_numpy()


def _filter_convolution_group(csv_df: pd.DataFrame, row):
    """
    For all rows in the input CSV which have the same Asset, TrainingLabel, TrainingStart,
    and TrainingEnd, they will have the same results when the convolution is performed during
    curve calculation. Since this operation is computationally costly, it only needs to be
    performed once. This function filters the input DataFrame into one group based on the
    same convolution results.

    Parameters
    ----------
    csv_df : pandas.DataFrame
        The input DataFrame which a subset is being pulled from
    row : pandas.DataFrame
        The row in the input DataFrame currently being checked

    Returns
    -------
    filtered_df : pandas.DataFrame
        The DataFrame filtered containing a subset of the input
    """
    return csv_df[
        (csv_df['Asset'] == row.Asset) & (csv_df['TrainingLabel'] == row.TrainingLabel) & (
                csv_df['TrainingStart'] == row.TrainingStart) & (
                csv_df['TrainingEnd'] == row.TrainingEnd)].drop_duplicates().reset_index(
        drop=True)


def swap_params(dist_params: List[float]):
    """
    Swaps the order of the fit parameter list so that location and scale are always in front.
    These two parameters are always fit regardless of the distribution selected by the caller.

    Parameters
    ----------
    dist_params : List[float]
        The list of fit parameters which is a different length (at least 2) long depending on
        the distribution

    Returns
    -------
    dist_params : List[float]
        The list with the swapped order
    """
    # Swap location and scale to the front of the List
    if len(dist_params) == 3:
        dist_params[0], dist_params[1], dist_params[2] = (
            dist_params[1], dist_params[2], dist_params[0])
    if len(dist_params) > 3:
        dist_params[0], dist_params[-2] = dist_params[-2], dist_params[0]
        dist_params[1], dist_params[-1] = dist_params[-1], dist_params[1]

    return dist_params


def _fit_params_from_prices(price_path, *args, dist=skewed_t,
                            calc_returns=calc_log_returns):
    """
    Performs MLE for the specified distribution on the training data and returns the fit parameters.

    The format of the returned parameter List always contains the location and scale as the first
    two elements since these are the two parameters which will exist regardless of what
    probability distribution is passed to this function.

    The function also allows the caller to specify a helper function which will calculate the
    returns of the training data. By default this is log returns, but simple returns or another
    custom function can be passed.

    Parameters
    ----------
    price_path : numpy.ndarray
        The training data price history
    args : List[float]
        The parameter list to pass to the optimizer as an initial guess. See scipy.rv_continuous
        fit function for more details.
    dist : rv_continuous
        (Optional. Default: skewed_t) The probability distribution to use to generate the
        Kelly curve
    calc_returns : Callable
        The function to use to calculate the financial returns of the training data

    Returns
    -------
    dist_params : List[float]
        A List containing the fit parameters output from the MLE process. Format is
        [location, scale, param1, param2, ...] with the length of the List changing depending
        on how many parameters the passed distribution has
    """
    return_df = calc_returns(pd.DataFrame(price_path)).dropna()
    # vals = [x for x in return_df.values if ~np.isnan(x)]

    dist_params = list(dist.fit(return_df, *args))

    return swap_params(dist_params)


class Trainer:
    """
    This object is responsible for fitting probability distributions to the specified training
    data to use during the Kelly curve generation process
    """

    def __init__(self, config: TrainingConfig):
        """
        Constructs the object using the TrainingConfig created using the builder module

        Parameters
        ----------
        config : TrainingConfig
            The config object created using the builder module
        """
        self.config = config

    def configure(self, config: TrainingConfig):
        """
        Changes the config object to a different configuration

        Parameters
        ----------
        config : TrainingConfig
            The configuration object to set

        Returns
        -------
        None
        """
        self.config = config

    def _create_convolution_group(self, row, training_dates,
                                  *args, dist=skewed_t, calc_returns=calc_log_returns):
        """
        For all rows in the input CSV which have the same Asset, TrainingLabel, TrainingStart,
        and TrainingEnd, they will have the same results when the convolution is performed during
        curve calculation.

        Since this operation is computationally costly, it only needs to be
        performed once.

        This function filters the input DataFrame into one group based on the
        same convolution results, collects the training data for the filtered group,
        performs MLE to fit a probability distribution to the training data, and finally returns
        a DataFrame containing the resulting parameters and all of the info needed for the
        convolution module to perform its functions.

        Parameters
        ----------
        row : pandas.DataFrame
            The row of the input DataFrame whose convolution group will be created
        training_dates : numpy.ndarray
            The ndarray containing the dates of the training data when prices were collected
        args : List[float]
            The argument list containing float values as initial guesses for each of the parameters
            in the probability distribution being fit
        dist : scipy.stats.rv_continuous
            The probability distribution which is being fit to the training data returns
        calc_returns : Callable
            The function being used to calculate the financial returns of the training data

        Returns
        -------
        conv_df : pandas.DataFrame
            The DataFrame containing all of the information needed to run the convolution
            module during curve generation
        """
        # Filter the input into the subset we are interested in
        filtered_df = _filter_convolution_group(self.config.input_df, row)

        # Get the training data corresponding to this subset
        start_date, end_date, price_path = _extract_historical_price_path(
            self.config.training_df, training_dates, row.Asset, row.TrainingStart,
            row.TrainingEnd)

        # Perform MLE on the returns of this training data
        dist_params = _fit_params_from_prices(price_path, *args, dist=dist,
                                              calc_returns=calc_returns)

        # Create the output DataFrame and return it
        rows = [{
            'Asset': row.Asset,
            'TrainingLabel': row.TrainingLabel,
            'TrainingStart': start_date,
            'TrainingEnd': end_date,
            'StrikePct': f_row.StrikePct,
            'Expiration': f_row.Expiration,
            'DistParams': dist_params,
            'CurrentPrice': row.CurrentPrice,
            'TrainingPrices': price_path.tolist()
        } for f_i, f_row in filtered_df.iterrows()]

        conv_df = pd.DataFrame(rows)

        return conv_df

    def train(self, *args, dist=skewed_t, calc_returns=calc_log_returns):
        """
        Performs the training by fitting a probability distribution to the financial
        returns of the training data specified in the configuration.

        This function is supplied initial guesses for the parameters to feed into the
        optimizer performing the fitting.

        Using kwargs it is possible to change the probability distribution being fit to any
        other matching the rv_continuous interface. It is also possible to specify any function
        to use when calculating the financial returns of the training data.

        Parameters
        ----------
        args : List[float]
            The argument list containing float values as initial guesses for each of the parameters
            in the probability distribution being fit
        dist : scipy.stats.rv_continuous
            (Optional. Default: skewed_t) The probability distribution which is being fit to
            the training data returns
        calc_returns : Callable
            (Optional. Default: calc_log_returns) The function being used to calculate the
            financial returns of the training data

        Returns
        -------
        conv_dfs : List[pandas.DataFrame]
            A List containing the DataFrames to be used during each convolution run for
            each training set we are generating Kelly curves for
        """

        # Get the unique sets we will generate convolution groups for
        unique_sets = self.config.input_df.drop_duplicates(
            subset=['Asset', 'TrainingLabel', 'TrainingStart', 'TrainingEnd'])

        # Extract the training dates from the file so it isn't repeated in the loop
        training_dates = get_training_dates(self.config.training_df)

        conv_dfs = [self._create_convolution_group(row, training_dates, *args, dist=dist,
                                                   calc_returns=calc_returns)
                    for u_i, row in unique_sets.iterrows()]

        return conv_dfs


# Define a Global object with default values to be configured by the module user
_train = Trainer(TrainingConfigBuilder().build_config())

# Prebind the object's methods so the module can be used by object oriented and functional
# programmers alike
configure_training = _train.configure
train = _train.train

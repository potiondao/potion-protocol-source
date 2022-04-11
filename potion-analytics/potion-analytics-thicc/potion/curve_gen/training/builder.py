"""
This module supplies the TrainingConfig object and the TrainingConfigBuilder to allow
users of the library to configure the training process of fitting a probability distribution
to a set of price history and following a standard design pattern. This is the same pattern
used by the other modules of the curve generator.
"""
import pandas as pd
from typing import NamedTuple

from os.path import isfile


class TrainingConfig(NamedTuple):
    """
    Immutable configuration object produced by the builder containing the training data
    to use when the curve generator fits a distribution to the returns of an asset
    """
    training_df: pd.DataFrame
    """The DataFrame containing the price histories imported from the CSV file"""
    input_df: pd.DataFrame
    """The DataFrame containing the Kelly curves to be calculated by the curve generator"""

    def __eq__(self, other):
        """
        Checks if this config object is equal to other

        Parameters
        ----------
        other : TrainingConfig
            The other config object we are testing for equality

        Returns
        -------
        is_equal : bool
            True if the two objects are equal, False otherwise
        """
        return (self.training_df.equals(other.training_df)) and (
            self.input_df.equals(other.input_df))


def _error_file_not_found(filename: str):
    """
    Raises a FileNotFoundError when called. Default error handler used when importing CSV files.

    Parameters
    ----------
    filename : str
        The file name which was not found

    Raises
    -------
    err : FileNotFoundError
        Always raised when called
    """
    raise FileNotFoundError('Check configuration. Could not find File: {}'.format(filename))


def _error_bad_csv_format(filename: str):
    """
    Raises a ValueError when called. Default error handler used when importing CSV files.

    Parameters
    ----------
    filename : str
        The file name which had a bad format

    Raises
    -------
    err : ValueError
        Always raised when called
    """
    raise ValueError('Check configuration. CSV file bad format: {}'.format(filename))


def _check_input_format(csv_df: pd.DataFrame):
    """
    Default handler for checking the format of input CSV files to the kelly curve generator.
    Checks the column names of the input CSV and if all match return True. Otherwise, False.

    Parameters
    ----------
    csv_df : pandas.DataFrame
        The input CSV which is having the format checked

    Returns
    -------
    format : bool
        True if the column names of the input CSV all match. Otherwise False
    """
    return ('Asset' == csv_df.columns[0]) and ('TrainingLabel' == csv_df.columns[1]) and (
            'TrainingStart' == csv_df.columns[2]) and ('TrainingEnd' == csv_df.columns[3]) and (
                   'StrikePct' == csv_df.columns[4]) and ('Expiration' == csv_df.columns[5]) and (
                   'CurrentPrice' == csv_df.columns[6])


def _check_training_format(csv_df: pd.DataFrame):
    """
    Default handler for checking the format of training CSV files to the kelly curve generator.
    Checks the column names of the training CSV and if all match return True. Otherwise, False.

    Parameters
    ----------
    csv_df : pandas.DataFrame
        The training CSV which is having the format checked

    Returns
    -------
    format : bool
        True if the column names of the training CSV all match. Otherwise False
    """
    return 'Master calendar' == csv_df.columns[0]


def _verify_format(filename: str, csv_df: pd.DataFrame, check_format=_check_input_format,
                   on_format_error=_error_bad_csv_format):
    """
    Calls the logic to check the format of an input file. Using kwargs the caller can customize
    the behavior of the function by changing both the checking logic and the error handling
    logic if desired.

    Parameters
    ----------
    filename : str
        The filename which is having the input checked
    csv_df : pandas.DataFrame
        The DataFrame containing the loaded CSV
    check_format : Callable
        The function which is checking whether the format of the file is correct
    on_format_error : Callable
        The function which is called if the format of the file is incorrect

    Returns
    -------
    None
    """
    if not check_format(csv_df):
        on_format_error(filename)


def _load_csv_file(filename: str, sep=',', check_file_exists=isfile,
                   on_file_error=_error_file_not_found, on_format_error=_error_bad_csv_format):
    """
    Calls the logic to check whether the input file exists and loads it into a pandas DataFrame
    if it does. Using kwargs the caller can customize the behavior of the function by changing
    both the checking logic and the error handling logic if desired.

    Parameters
    ----------
    filename : str
        The filename which is being loaded
    sep : str
        (Optional. Default: ',') The separator character for the CSV file
    check_file_exists : Callable
        The function which checks if the file being loaded exists
    on_file_error : Callable
        The function which is called if the file does not exist
    on_format_error : Callable
        The function which is called if the format of the file is incorrect

    Returns
    -------
    csv_df : pandas.DataFrame or None
        The loaded DataFrame if the file exists, or None if it does not
    """
    if check_file_exists(filename):
        try:
            return pd.read_csv(filename, sep=sep)
        except pd.errors.ParserError:
            on_format_error(filename)
            return None
    else:
        on_file_error(filename)
        return None


class TrainingConfigBuilder:
    """
    Standard python builder class for creating immutable configuration objects to use
    with the training process.
    """

    def __init__(self):
        """
        Constructor initializes the builder with default values
        """
        self.training_history_filename = None
        self.input_csv_filename = None

    def set_training_history_filename(self, filename: str):
        """
        Sets the training history filename which is the name of the file containing price history
        data of different assets at different dates in time.

        Parameters
        ----------
        filename : filename
            The name of the file to use containing the training data

        Returns
        -------
        self : TrainingConfigBuilder
            This object following the builder pattern
        """
        self.training_history_filename = filename
        return self

    def set_input_csv_filename(self, filename: str):
        """
        Sets the input filename which is the name of the file containing the information
        about the curves the caller would like to generate. Strike, Asset, Expiration, etc.

        Parameters
        ----------
        filename : filename
            The name of the file to use containing the input data

        Returns
        -------
        self : TrainingConfigBuilder
            This object following the builder pattern
        """
        self.input_csv_filename = filename
        return self

    def build_config(self, check_file_exists=isfile, on_file_error=_error_file_not_found,
                     check_training_format=_check_training_format,
                     check_input_format=_check_input_format, on_format_error=_error_bad_csv_format):
        """
        Creates an immutable TrainingConfig object from the currently configured builder.

        This function allows the caller to customize the behavior of the builder functions using
        kwargs.

        Parameters
        ----------
        check_file_exists : Callable
            This function checks whether a given file exists
        on_file_error : Callable
            This function is called when the configured input file does not exist
        check_training_format : Callable
            This function checks whether the training data input file is the correct format
        check_input_format : Callable
            This function checks whether the input file is the correct format
        on_format_error : Callable
            This function is called when the configured input files are the wrong format.

        Raises
        -------
        FileNotFoundError
            By default, if an input file is not found
        ValueError
            By default, if an input file has a bad format

        Custom handlers may raise exceptions not listed here.

        Returns
        -------
        config : TrainingConfig
            The immutable configuration object
        """
        # Return an empty training config by default if called after object was just initialized
        if self.training_history_filename is None or self.input_csv_filename is None:
            return TrainingConfig(pd.DataFrame(), pd.DataFrame())

        # Load the CSV files, raise FileNotFoundError if the file can not be found
        training_csv_df = _load_csv_file(self.training_history_filename,
                                         check_file_exists=check_file_exists,
                                         on_file_error=on_file_error,
                                         on_format_error=on_format_error)
        input_csv_df = _load_csv_file(self.input_csv_filename,
                                      check_file_exists=check_file_exists,
                                      on_file_error=on_file_error, on_format_error=on_format_error)

        # Check the files match the right format, raise ValueError if the format is bad
        _verify_format(self.training_history_filename, training_csv_df,
                       check_format=check_training_format, on_format_error=on_format_error)
        _verify_format(self.input_csv_filename, input_csv_df,
                       check_format=check_input_format, on_format_error=on_format_error)

        input_asset_list = list(dict.fromkeys(input_csv_df.Asset.values))
        training_asset_list = list(dict.fromkeys(training_csv_df.columns[1:]))

        if not all(elem in training_asset_list for elem in input_asset_list):
            raise ValueError(
                'Historical Prices File must contain all assets from Input File. ' +
                'Assets in Historical: {} Assets in Input: {}'.format(
                    training_asset_list, input_asset_list))

        return TrainingConfig(training_csv_df, input_csv_df)

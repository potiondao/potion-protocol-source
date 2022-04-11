"""
This module provides helper function for the code which calculate returns on price data.
"""
import numpy as np
import pandas as pd


def calc_simple_returns(price_data: pd.DataFrame):
    """
    Calculates the simple returns for price history data and returns the result

    Parameters
    ----------
    price_data : pandas.DataFrame
        The price history as a single column with the date the price was recorded as the index

    Returns
    -------
    return_df : pandas.DataFrame
        The simple returns of the price history
    """
    ret = ((price_data / price_data.shift()) - 1.0).dropna()
    ret.columns = ['Return']
    return ret


def calc_log_returns(price_data: pd.DataFrame):
    """
    Calculates the log returns for price history data and returns the result

    Parameters
    ----------
    price_data : pandas.DataFrame
        The price history as a single column with the date the price was recorded as the index

    Returns
    -------
    return_df : pandas.DataFrame
        The log returns of the price history
    """
    return pd.DataFrame(np.copy(np.log(price_data / price_data.shift()).dropna()),
                        columns=['Return'])

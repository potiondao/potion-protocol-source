#!/usr/bin/env python3
"""Module with all convolution methods"""

import pandas as pd
import lib.distributions as dst
import lib.random_path_generation as rpg

def monte_carlo_convolution(
    returns_sequence, n_bins=100, number_of_paths=10, n_convolutions=5
):
    """Monte Carlo Convolution: Generate random paths => Calculate total return for each path =>
    get distribution of the returns
    Args:
        returns_sequence (list):
            Could be any convertable to pd.Series type.
            Could pass the returns_histogram_df as well
        n_bins (int):
            Number of bins. Could be also string (e.g. 'auto') or list of bin edges
            Whatever complies with np.histogram
        number_of_paths (int):
            Number of paths to generate
        n_convolutions (int):
            Number of returns in each path

    Returns:
        histogram_df (pd.DataFrame):
            Returns Histogram after the Convolution
    """

    if not isinstance(returns_sequence, pd.DataFrame):
        if n_convolutions == 1:
            return dst.get_returns_histogram_from_returns_sequence(
                returns_sequence, n_bins=n_bins
            )
        random_return_paths = rpg.generate_returns_paths_from_returns(
            returns_sequence,
            number_of_paths,
            path_length=n_convolutions + 1,
            output_as_df=True,
        )
    else:
        random_return_paths = rpg.generate_returns_paths_from_returns_histogram(
            returns_sequence,
            number_of_paths,
            path_length=n_convolutions + 1,
            output_as_df=True,
        )

    sum_returns = (random_return_paths + 1).prod().values - 1

    return dst.get_returns_histogram_from_returns_sequence(sum_returns, n_bins=n_bins)


def daily_returns_to_n_day_returns(returns_sequence, number_of_paths=10, n_days=5):
    """Monte Carlo way of aggregating returns: Generate random paths =>
    Calculate total return for each path with len=n_days => n_daily returns
    Args:
        returns_sequence (list):
            Could be any convertable to pd.Series type.
            Could pass the returns_histogram_df as well
        number_of_paths (int):
            Number of paths to generate
        n_days (int):
            Number of returns in each path

    Returns:
        histogram_df (pd.DataFrame):
            Returns Histogram after the Convolution
    """

    if n_days == 1:
        sum_returns = returns_sequence
    else:
        random_return_paths = rpg.generate_returns_paths_from_returns(
            returns_sequence,
            number_of_paths,
            path_length=n_days,
            output_as_df=True,
        )
        sum_returns = (random_return_paths + 1).prod().values - 1

    return sum_returns

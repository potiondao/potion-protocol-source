#!/usr/bin/env python3
"""Module with functions to generate/change distributions"""
import numpy as np
import pandas as pd

###################################################################################################
# Distribution Generation
###################################################################################################
def get_returns_histogram_from_returns_sequence(returns_sequence, n_bins="auto"):
    """Get returns_histogram as df
    Args:
        returns_sequence (list):
            Could be any convertable to pd.Series type.
        n_bins (float):
            Number of the histogram bins

    Returns:
        histogram_df (pd.DataFrame):
            Columns: returns, freq, cumulative_freq
            Basically a partial distribution function in a form of df
    """

    histogram_df = pd.DataFrame(np.histogram(returns_sequence, bins=n_bins))

    histogram_df = histogram_df.T
    histogram_df.rename(columns={0: "count", 1: "return"}, inplace=True)
    histogram_df["freq"] = histogram_df["count"] / len(returns_sequence)
    histogram_df.fillna(0, inplace=True)
    histogram_df["cumulative_freq"] = np.cumsum(histogram_df["freq"])

    return histogram_df


def get_returns_histogram_from_price_sequence(price_sequence, n_bins="auto"):
    """Get returns_histogram as df
    Args:
        price_sequence (list):
            Could be any convertable to pd.Series type.
        n_bins (float):
            Number of the histogram bins
    Returns:
        histogram_df (pd.DataFrame):
            Columns: returns, freq, cumulative_freq
            Basically a partial distribution function in a form of df
    """

    if isinstance(price_sequence, pd.Series):
        price_data = price_sequence
    else:
        price_data = pd.Series(price_sequence)

    returns_sequence = price_data.pct_change().values[1:]

    return get_returns_histogram_from_returns_sequence(returns_sequence, n_bins=n_bins)

###################################################################################################
# Distribution Manipulation
###################################################################################################


def move_distribution(histogram_df, distance, inplace=False):
    """Function to move distribution by distance_in_std
    Only works with constant bins!
    Args:
        histogram_df (pd.DataFrame):
            Necessary Columns: return, freq
        std (float):
            true standard deviation value
        distance_in_std (float):
            How far should we mode the distribution
        inplace (bool):
            change histogram_df or create a new one
    Returns:
        shifted_histogram_df (pd.DataFrame):
    """
    # std = get_returns_distribution_std(histogram_df)
    bin_size = histogram_df["return"].values[-1] - histogram_df["return"].values[-2]
    number_of_indexes_to_shift = int(distance / bin_size)
    if not inplace:
        shifted_histogram_df = histogram_df.copy()
        shifted_histogram_df["freq"] = histogram_df.shift(number_of_indexes_to_shift)[
            "freq"
        ]
        shifted_histogram_df.fillna(0, inplace=True)
        return shifted_histogram_df
    else:
        histogram_df["new_freq"] = histogram_df.shift(number_of_indexes_to_shift)[
            "freq"
        ]
        histogram_df["freq"] = histogram_df["new_freq"]
        histogram_df.drop(columns=["new_freq"], inplace=True)
        histogram_df.fillna(0, inplace=True)
        return histogram_df


###################################################################################################
# Distribution Stats
###################################################################################################


def calculate_mean(histogram_df):
    """Mean calculation at the histogram"""
    return histogram_df["return"].dot(histogram_df["freq"])


def calculate_std(histogram_df):
    """Standard deviation calculation at the histogram"""
    histogram_mean = calculate_mean(histogram_df)
    distance_mean_df = np.square(histogram_df["return"] - histogram_mean)
    variance = np.dot(histogram_df["freq"], distance_mean_df)
    return np.sqrt(variance)


def calculate_skew(histogram_df):
    """Skew calculation at the histogram"""
    histogram_mean = calculate_mean(histogram_df)
    histogram_std = calculate_std(histogram_df)
    third_moment_list = (histogram_df["return"] - histogram_mean) ** 3
    third_moment = np.dot(histogram_df["freq"], third_moment_list)
    return third_moment / (histogram_std) ** 3

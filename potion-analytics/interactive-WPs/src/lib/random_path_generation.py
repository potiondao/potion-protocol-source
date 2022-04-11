#!/usr/bin/env python3
"""Module with all random path generation methods"""

import numpy as np
import pandas as pd
import lib.helpers as hlp


def generate_utils_list(
    list_length, initial_util=0.5, duration=1, randomize=True, util_std=0.1
):
    """Function to utils list
    Utils Sequence imitate Brownian motion (not really) inside [0, 1] bounds
    or just creates list with constant util
    Args:
        list_length (int):
            Number of utilities
        initial_util (float):
            Utilization value for the first day
        duration (int):
            duration of the option
        randomize (bool):
            If we want

    Returns:
        utils (np.array):
            1d arr
    """
    if randomize:
        utils = []

        # use Uniform distribution if std < 0
        if util_std < 0:
            utils = np.random.uniform(0, 1, size=(list_length // duration,))
        else:
            for i in range(list_length // duration):
                del i
                new_util = np.random.normal(loc=initial_util, scale=util_std)
                if new_util > 1:
                    new_util = 1
                elif new_util < 0:
                    new_util = 0
                utils.append(new_util)

    else:
        utils = [initial_util] * int(list_length // duration)

    daily_utils = hlp.extend_list_to_be_daily(utils, duration, list_length)

    return np.array(daily_utils).astype("float16")


def generate_returns_paths_from_returns(
    returns_sequence, number_of_paths, path_length, output_as_df=False
):
    """Function to generate price paths based on given price_sequence

    Args:
        returns_sequence (list):
            list or other iterable of returns
        number_of_paths (int):
            Number of paths to generate
        path_length (int):
            number of returns in each path
        output_as_df (bool):
            each df the columns is returns path or each returns path is list inside list

    Returns:
        list_of_paths (list):
            2d array with returns paths
    """
    if isinstance(returns_sequence, pd.Series):
        returns_list = returns_sequence.values
    else:
        returns_list = returns_sequence
    returns_paths = np.random.choice(
        returns_list, size=(number_of_paths, path_length), replace=True
    )

    if not output_as_df:
        return returns_paths
    else:
        returns_paths_df = pd.DataFrame(returns_paths).T
        returns_paths_df = returns_paths_df.astype("float16")
        return returns_paths_df


def generate_price_paths_from_returns(
    returns_sequence,
    number_of_paths,
    path_length,
    current_price=1.0,
    output_as_df=False,
):
    """Function to generate price paths based on given price_sequence

    Args:
        returns_sequence (list):
            list or other iterable of returns
        number_of_paths (int):
            Number of paths to generate
        path_length (int):
            number of returns in each path
        current_price (float):
            Starting point of the calculations
        output_as_df (bool):
            each df the columns is price path or each price path is list inside list
    Returns:
        list_of_paths (list):
            2d array with price paths
    """
    returns_paths = np.random.choice(
        returns_sequence, size=(number_of_paths, path_length - 1), replace=True
    )
    cum_deltas = np.cumprod(1 + returns_paths, axis=1)
    path_list = np.insert(current_price * cum_deltas, 0, current_price, axis=1)

    if not output_as_df:
        return path_list
    else:
        return pd.DataFrame(path_list).T


def generate_returns_paths_from_returns_histogram(
    returns_histogram_df, number_of_paths, path_length, output_as_df=False
):
    """Function to generate price paths based on given price_sequence

    Args:
        returns_histogram_df (pd.DataFrame):
            Necessary Columns: return, freq
        number_of_paths (int):
            Number of paths to generate
        path_length (int):
            number of returns in each path
        current_price (float):
            Starting point of the calculations
    Returns:
        list_of_paths (list):
            2d array with price paths
    """
    returns_paths = np.random.choice(
        returns_histogram_df["return"],
        size=(number_of_paths, path_length),
        p=returns_histogram_df["freq"] / returns_histogram_df["freq"].sum(),
    )

    if not output_as_df:
        return returns_paths
    else:
        return pd.DataFrame(returns_paths).T


def simple_moving_average(arr, span):
    """actually not that simple:
    len(output) == len(input) and first value is gonna be the original one
    Mean of empty slice Warning
    """
    first_elem = arr[0]

    arr = [arr[0]] * (span) + arr

    smoothed_part = [
        np.average(arr[val - span : val + span + 1]) for val in range(len(arr))
    ]
    smoothed_part = [val for val in smoothed_part if str(val) != "nan"]
    smoothed_part[0] = first_elem

    return smoothed_part

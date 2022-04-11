#!/usr/bin/env python3
"""Module with small helpers"""
import datetime as dt
import os
import numpy as np
import pandas as pd

HELPERS_DIR = os.path.realpath(__file__)
LIB_DIR = os.path.dirname(HELPERS_DIR)
SRC_DIR = os.path.dirname(LIB_DIR)
PROJECT_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
INPUT_DATA_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DATA_DIR = os.path.join(DATA_DIR, "output")
MEDIA_DIR = os.path.join(PROJECT_DIR, "media")


def get_date(date_str, asset_name, historical_df):
    """get 22/5/14"""

    if date_str == "min":
        return historical_df[asset_name].first_valid_index()

    elif date_str == "max":
        return historical_df[asset_name].last_valid_index()
    elif "-" in date_str:
        return dt.datetime.strptime(date_str, "%Y-%m-%d")
    else:
        return dt.datetime.strptime(date_str, "%m/%d/%Y")


def convert_bankroll_to_cagr(final_bankroll, years, begin_bankroll=1):
    """get cagr"""
    return (final_bankroll / begin_bankroll) ** (1 / years) - 1

def get_historical_prices_df():
    """read/prepare historical_source csv file"""
    # using pd.DataFrame over here only to calm down linter
    historical_df = pd.DataFrame(pd.read_csv(
        os.path.join(INPUT_DATA_DIR, "historical_source.csv"), sep=","
    ))
    historical_df["date"] = historical_df["date"].apply(
        dt.datetime.strptime, args=("%Y-%m-%d",))
    historical_df.set_index("date", inplace=True)

    return historical_df


def extend_list_to_be_daily(cycles_list, duration, n_days):
    """Switch from options expiration cycles to days
    via zero fill"""
    daily_2d_list = [([0] * int(duration - 1)) + [cycle] for cycle in cycles_list]
    daily_list = [j for sub in daily_2d_list for j in sub]
    daily_list.extend([0] * int(n_days - len(daily_list)))

    return daily_list


def get_mood_segment_dates(
    price_series, segment_len_days=30, mood="bear", metric="sharpe"
):
    """Find most bullish/bearish segment in the price series
    Args:
        price_series (pd.Series):
            Prices of instrument, index should be datetime
        segment_len_days (int):
            Length of segment
        mood (str):
            'bear' or 'bull', anything else will return min, max dates
        metric (str):
            'sharpe' or 'return'

    Returns:
        segment_start_date (dt.datetime), segment_end_date(dt.datetime):
            Columns: returns, freq, cumulative_freq
            Basically a partial distribution function in a form of df
    """

    start_date = price_series.index.min()
    end_date = price_series.index.max()

    if mood == "bear":
        highest_metric = 999
    elif mood == "bull":
        highest_metric = -999
    else:
        return start_date, end_date

    segment_start_date = None
    segment_end_date = None
    current_date = start_date
    returns_series = price_series.pct_change().dropna()

    # loop over all history
    while current_date < end_date - dt.timedelta(days=segment_len_days):
        tmp_price_series = price_series[
            (price_series.index > current_date)
            & (price_series.index < current_date + dt.timedelta(segment_len_days))
        ]
        tmp_returns_series = returns_series[
            (returns_series.index > current_date)
            & (returns_series.index < current_date + dt.timedelta(segment_len_days))
        ]
        # calculate metric
        if metric == "sharpe":
            tmp_metric = tmp_returns_series.mean() / tmp_returns_series.std()

        elif metric == "return" and len(tmp_price_series.values) > 1:
            tmp_metric = (
                tmp_price_series.values[-1] - tmp_price_series.values[0]
            ) / tmp_price_series.values[0]

        # update highest metric value
        if tmp_metric > highest_metric and mood == "bull":
            highest_metric = tmp_metric
            segment_start_date = current_date
            segment_end_date = segment_start_date + dt.timedelta(segment_len_days)
        elif tmp_metric < highest_metric and mood == "bear":
            highest_metric = tmp_metric
            segment_start_date = current_date
            segment_end_date = segment_start_date + dt.timedelta(segment_len_days)
        current_date += dt.timedelta(days=1)

    return segment_start_date, segment_end_date


def get_price_for_mood_segment(
    price_series, segment_len_days=30, mood="bear", metric="sharpe", calc_log_price=True
):
    """Create df with cols: date, price, log_price"""

    date_start, date_end = get_mood_segment_dates(
        price_series, segment_len_days=segment_len_days, mood=mood, metric=metric
    )
    if date_start is None:
        return pd.DataFrame()
    else:
        filtered_price_sequence = price_series[
            (price_series.index > date_start) & (price_series.index < date_end)
        ]
        price_df = filtered_price_sequence.to_frame()
        price_df.rename(columns=lambda x: "price", inplace=True)
        if calc_log_price:
            price_df["log_price"] = np.log(price_df["price"])
        price_df["label"] = mood
    return price_df.sort_index()

def apply_sma(data, window_length=20):
    """Simple Moving Average applied to the list like data"""
    i = 1
    averaged_elements = []
    while i < len(data):
        if i < window_length:
            averaged_elements.append(np.mean(data[:i]))
        else:
            averaged_elements.append(np.mean(data[i-window_length:i]))
        i += 1

    return averaged_elements

"""
Provides file helper functions to the portfolio backtester GUI
"""
import numpy as np
import pandas as pd


def read_multi_asset_curves_from_csv(filename: str):
    """
    Imports a CSV of curve parameters as a DataFrame so that it can be used in python code

    Parameters
    ----------
    filename : str
        The filename to read

    Returns
    -------
    df : pandas.DataFrame
        The DataFrame containing the curve parameters
    """
    df = pd.read_csv(filename, sep=',')

    t_col = df.t_params
    bet_frac_col = df.bet_fractions
    prem_col = df.curve_points

    t_vals = []
    bf_vals = []
    prem_vals = []
    for t_params, bf, prem in zip(t_col.values, bet_frac_col.values, prem_col):

        t_vals.append(np.array(t_params[1:-1].split()).astype(float))
        bf_vals.append(np.array(bf[1:-1].split()).astype(float))
        prem_vals.append(np.array(prem[1:-1].split()).astype(float))

    df['t_params'] = t_vals
    df['bet_fractions'] = bf_vals
    df['curve_points'] = prem_vals

    return df

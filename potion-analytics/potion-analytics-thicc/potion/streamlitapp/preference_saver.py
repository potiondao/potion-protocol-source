"""
Module used to save UI preferences the user has entered. When the user clicks a button and one of
the tools begins calculation, the last input values are saved in a pandas DataFrame and saved in a
CSV. If the user closes the tool or the program suffers a random crash or something, all the user's
last inputs will have been saved and tedious repeated UI entry avoided.
"""
import pandas as pd
import streamlit as st

preference_df_file_name = 'preferences.csv'

CURVE_GEN_IF = 'Curve Generator Input File'
CURVE_GEN_PF = 'Curve Generator Price File'
CURVE_GEN_BN = 'Curve Generator Batch Number'
CURVE_GEN_IB = 'Curve Generator Initial Bankroll'
CURVE_BACK_BN = 'Curve Backtester Batch Number'
CURVE_BACK_IB = 'Curve Backtester Initial Bankroll'
CURVE_BACK_PG = 'Curve Backtester Path Generation'
CURVE_BACK_NP = 'Curve Backtester Number of Paths'
CURVE_BACK_PL = 'Curve Backtester Path Length'
CURVE_BACK_UT = 'Curve Backtester Utilization'
POOL_CREATE_BN = 'Pool Creator Batch Number'
POOL_CREATE_NG = 'Pool Creator Number of Performance Groups'
POOL_CREATE_NP = 'Pool Creator Number of Pools'
POOL_BACK_BN = 'Pool Backtester Batch Number'
POOL_BACK_PG = 'Pool Backtester Path Generation'
POOL_BACK_NP = 'Pool Backtester Number of Paths'
POOL_BACK_PL = 'Pool Backtester Path Length'
POOL_BACK_IB = 'Pool Backtester Initial Bankroll'
WIDGET_CF = 'Log Widget Conversion File'
WIDGET_BN = 'Log Widget Batch Number'
WIDGET_IC = 'Log Widget Include CSVs'
WIDGET_IS = 'Log Widget Include SVGs'
WIDGET_IH = 'Log Widget Include HDF5s'
WIDGET_DF = 'Log Widget Delete Files'


def initialize_preference_df():
    """
    Initializes a default preference dataframe containing the default values.

    Returns
    -------
    default_df : pandas.DataFrame
        A DataFrame containing the default preference values
    """
    default_values = [{
        CURVE_GEN_IF: '',
        CURVE_GEN_PF: '',
        CURVE_GEN_BN: 0,
        CURVE_GEN_IB: 1000.0,
        CURVE_BACK_BN: 0,
        CURVE_BACK_IB: 1000.0,
        CURVE_BACK_PG: 'SkewT',
        CURVE_BACK_NP: 300,
        CURVE_BACK_PL: 730,
        CURVE_BACK_UT: 0.3,
        POOL_CREATE_BN: 0,
        POOL_CREATE_NG: 1,
        POOL_CREATE_NP: 1,
        POOL_BACK_BN: 0,
        POOL_BACK_PG: 'Multivariate Student\'s T',
        POOL_BACK_NP: 300,
        POOL_BACK_PL: 730,
        POOL_BACK_IB: 1000.0,
        WIDGET_CF: '',
        WIDGET_BN: 0,
        WIDGET_IC: True,
        WIDGET_IS: True,
        WIDGET_IH: True,
        WIDGET_DF: False
    }]

    return pd.DataFrame(default_values)


def get_pref(name):
    """
    Gets one of the preference values

    Parameters
    ----------
    name : str
        The name of the preference to get

    Returns
    -------
    obj : Any
        The saved preference to use as UI input
    """
    return st.session_state.pref_df[name][0]


def save_curve_gen_preferences(input_file, price_file, batch_number, init_bankroll):
    """
    Saves the UI input values from the curve generator tool

    Parameters
    ----------
    input_file : str
        The name of the file containing input curve parameters
    price_file : str
        The name of the file containing the price history data
    batch_number : int
        The id number identifying the batch of log results
    init_bankroll : float
        The initial starting capital for the simulation

    Returns
    -------
    None
    """
    st.session_state.pref_df[CURVE_GEN_IF] = input_file
    st.session_state.pref_df[CURVE_GEN_PF] = price_file
    st.session_state.pref_df[CURVE_GEN_BN] = batch_number
    st.session_state.pref_df[CURVE_GEN_IB] = init_bankroll

    st.session_state.pref_df.to_csv(preference_df_file_name, index=False)


def save_curve_backtester_preferences(batch_number, init_bankroll, path_gen, num_paths,
                                      path_length, util):
    """
    Saves the UI input values from the backtesting tool

    Parameters
    ----------
    batch_number : int
        The id number identifying the batch of log results
    init_bankroll : float
        The initial starting capital for the simulation
    path_gen : PathGenMethod
        The method used to generate paths
    num_paths : int
        The number of paths in the backtesting simulation
    path_length : int
        The length of the path in the backtesting simulation
    util : float
        The util of the simulation

    Returns
    -------
    None
    """
    st.session_state.pref_df[CURVE_BACK_BN] = batch_number
    st.session_state.pref_df[CURVE_BACK_IB] = init_bankroll
    st.session_state.pref_df[CURVE_BACK_PG] = path_gen
    st.session_state.pref_df[CURVE_BACK_NP] = num_paths
    st.session_state.pref_df[CURVE_BACK_PL] = path_length
    st.session_state.pref_df[CURVE_BACK_UT] = util

    st.session_state.pref_df.to_csv(preference_df_file_name, index=False)


def save_pool_creator_preferences(batch_number, num_groups, num_pools):
    """
    Saves the UI input values from the portfolio creator tool

    Parameters
    ----------
    batch_number : int
        The id number identifying the batch of log results
    num_groups : int
        The number of groups to make from the generated curves
    num_pools : int
        The number of pools to make from the generated curves

    Returns
    -------
    None
    """
    st.session_state.pref_df[POOL_CREATE_BN] = batch_number
    st.session_state.pref_df[POOL_CREATE_NG] = num_groups
    st.session_state.pref_df[POOL_CREATE_NP] = num_pools

    st.session_state.pref_df.to_csv(preference_df_file_name, index=False)


def save_pool_backtester_preferences(batch_number, path_gen, num_paths, path_length,
                                     init_bankroll):
    """
    Saves the UI input values from the portfolio backtester tool

    Parameters
    ----------
    batch_number : int
        The id number identifying the batch of log results
    path_gen : PathGenMethod
        The method used to generate paths
    num_paths : int
        The number of paths in the backtesting simulation
    path_length : int
        The length of the path in the backtesting simulation
    init_bankroll : float
        The initial starting capital for the simulation

    Returns
    -------
    None
    """
    st.session_state.pref_df[POOL_BACK_BN] = batch_number
    st.session_state.pref_df[POOL_BACK_PG] = path_gen
    st.session_state.pref_df[POOL_BACK_NP] = num_paths
    st.session_state.pref_df[POOL_BACK_PL] = path_length
    st.session_state.pref_df[POOL_BACK_IB] = init_bankroll

    st.session_state.pref_df.to_csv(preference_df_file_name, index=False)


def save_widget_preferences(conversion_file_name, batch_number, include_csvs, include_svgs,
                            include_hdf5s, del_files):
    """
    Saves the UI input values from the log archive widget

    Parameters
    ----------
    conversion_file_name : str
        The name of the log file to convert from hdf5 to CSV
    batch_number : int
        The id number identifying the batch of log results
    include_csvs : bool
        Flag for whether to include CSV files in the zip archive
    include_svgs : bool
        Flag for whether to include svg files in the zip archive
    include_hdf5s : bool
        Flag for whether to include hdf5 files in the zip archive
    del_files : bool
        Flag for whether to delete log files after archiving them in a zip

    Returns
    -------
    None
    """
    st.session_state.pref_df[WIDGET_CF] = conversion_file_name
    st.session_state.pref_df[WIDGET_BN] = batch_number
    st.session_state.pref_df[WIDGET_IC] = include_csvs
    st.session_state.pref_df[WIDGET_IS] = include_svgs
    st.session_state.pref_df[WIDGET_IH] = include_hdf5s
    st.session_state.pref_df[WIDGET_DF] = del_files

    st.session_state.pref_df.to_csv(preference_df_file_name, index=False)


"""
Provides file helper functions to the curve generation GUI
"""
import os
from pathlib import Path
import csv
from datetime import datetime
import numpy as np
import pandas as pd

from plotly.graph_objects import Figure


def save_plotly_fig_to_file(dir_filepath: str, filename: str, fig: Figure):
    """
    This function takes a Plotly figure object and saves it to a file

    Parameters
    ----------
    dir_filepath : str
        The path to the directory where the file will be saved
    filename : str
        The desired name of the file to be saved
    fig : plotly.graph_objects.Figure
        The Plotly figure object

    Returns
    --------
    None
    """
    if not os.path.exists(dir_filepath):
        os.mkdir(dir_filepath)
    fig.write_image(dir_filepath + '/' + filename)


def write_curve_gen_outputs(batch_num: int, curve_df: pd.DataFrame, pdf_df: pd.DataFrame,
                            training_df: pd.DataFrame):
    """
    Writes the 3 output CSVs from the curve generation process

    Parameters
    ----------
    batch_num : int
        The user specified batch number identifying this set of results from others in the
        log directory
    curve_df : pandas.DataFrame
        The output DataFrame containing the generated curve information
    pdf_df : pandas.DataFrame
        The output DataFrame containing the generated PDFs from convolution
    training_df : pandas.DataFrame
        The output DataFrame containing the training data information

    Returns
    -------
    None
    """
    Path('./batch_results/batch_{}/curve_generation'.format(
        batch_num)).mkdir(parents=True, exist_ok=True)
    Path('./batch_results/batch_{}/curve_generation/plots'.format(
        batch_num)).mkdir(parents=True, exist_ok=True)

    curve_df.to_csv('./batch_results/batch_{}/curve_generation/curves.csv'.format(batch_num),
                    index=False, quoting=csv.QUOTE_ALL)
    pdf_df.to_csv('./batch_results/batch_{}/curve_generation/pdfs.csv'.format(batch_num),
                  index=False, quoting=csv.QUOTE_ALL)
    training_df.to_csv('./batch_results/batch_{}/curve_generation/training.csv'.format(batch_num),
                       index=False, quoting=csv.QUOTE_ALL)


def read_training_data_from_csv(filename: str):
    """
    Imports a CSV of training data as a DataFrame so that it can be used in python code

    Parameters
    ----------
    filename : str
        The filename to read

    Returns
    -------
    df : pandas.DataFrame
        The DataFrame containing the training data
    """
    df = pd.read_csv(filename, sep=',')

    start_col = df.StartDate
    end_col = df.EndDate
    train_col = df.TrainingPrices

    start_vals = []
    end_vals = []
    train_vals = []
    for start, end, price in zip(start_col.values, end_col.values, train_col.values):
        start_vals.append(np.array(start.replace('\n', '').replace(
            '[', '').replace(']', '').replace(',', '').split()).astype(datetime)[0])
        end_vals.append(np.array(end.replace('\n', '').replace(
            '[', '').replace(']', '').replace(',', '').split()).astype(datetime)[0])
        train_vals.append(np.array(price.replace('\n', '').replace(
            '[', '').replace(']', '').replace(',', '').split()).astype(np.float64))

    df['StartDate'] = start_vals
    df['EndDate'] = end_vals
    df['TrainingPrices'] = train_vals

    return df


def read_pdfs_from_csv(filename: str):
    """
    Imports a CSV of PDF data as a DataFrame so that it can be used in python code

    Parameters
    ----------
    filename : str
        The filename to read

    Returns
    -------
    df : pandas.DataFrame
        The DataFrame containing the PDF data
    """
    return pd.read_csv(filename, sep=',')


def read_curves_from_csv(filename: str):
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
        t_vals.append(np.array(t_params.replace('\n', '').replace(
            '[', '').replace(']', '').replace(',', '').split()).astype(np.float64))
        bf_vals.append(np.array(bf.replace('\n', '').replace(
            '[', '').replace(']', '').replace(',', '').split()).astype(np.float64))
        prem_vals.append(np.array(prem.replace('\n', '').replace(
            '[', '').replace(']', '').replace(',', '').split()).astype(np.float64))

    df['t_params'] = t_vals
    df['bet_fractions'] = bf_vals
    df['curve_points'] = prem_vals

    return df


def curve_output_to_json(curve_df: pd.DataFrame, training_df: pd.DataFrame, msg=''):
    """
    Converts the output DataFrames into json objects

    Parameters
    ----------
    curve_df : pandas.DataFrame
        The curve output DataFrame
    training_df : pandas.DataFrame
        The training output DataFrame
    msg : str
        (Optional. Default: '') The message to include in the json object

    Returns
    -------
    json_objs : List[str]
        The List of json objects output for each curve
    """
    json_objs = []
    for index, row in curve_df.iterrows():
        train_set = training_df[
            ((training_df['Ticker'] == row.Ticker) & (training_df['Label'] == row.Label))]

        if msg == '':
            message = row.Label
        else:
            message = msg

        json_objs.append({
            'duration': int(row.Expiration),
            'strike': int(row.StrikePercent * 100.0),
            'training': {
                'from': int(datetime.strptime(
                    train_set['StartDate'].values[0], '%d/%m/%Y').timestamp()),
                'to': int(datetime.strptime(
                    train_set['EndDate'].values[0], '%d/%m/%Y').timestamp()),
            },
            'curve': {
                'a': row.A,
                'b': row.B,
                'c': row.C,
                'd': row.D
                # 'max': 1.0
            },
            'asset': row.Ticker,
            'message': message
        })

    return json_objs

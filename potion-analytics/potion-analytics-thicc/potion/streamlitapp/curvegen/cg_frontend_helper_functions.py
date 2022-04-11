"""
This module provides the frontend helper code for the curve generation GUI
"""
import numpy as np
import pandas as pd

import streamlit as st

import os
from pathlib import Path
import sys
import glob

# Add the root to the path so we can import our potion files
module_path = os.path.abspath(os.path.join('.'))

if module_path not in sys.path:
    sys.path.append(module_path)
# print('Current Module Path: {}'.format(module_path))

from potion.curve_gen.curve_conversion import (convert_fully_normalized_to_strike_normalized_curve,
                                               convert_strike_normalized_to_absolute_curve)
from potion.curve_gen.kelly import evaluate_premium_curve
from potion.curve_gen.utils import build_generator_config

from potion.streamlitapp.curvegen import (
    CG_INPUT_FILE_HELP_TEXT, CG_PRICES_FILE_HELP_TEXT, CG_BATCH_NUMBER_HELP_TEXT,
    CG_INIT_BANKROLL_HELP_TEXT)
from potion.streamlitapp.curvegen.curve_generation_helper_functions import (run_curve_generation)
from potion.streamlitapp.curvegen.cg_file_io import (
    read_pdfs_from_csv, read_training_data_from_csv, read_curves_from_csv, save_plotly_fig_to_file)
from potion.streamlitapp.curvegen.cg_plot import (
    plot_curves_from_csv, plot_pdf_and_option_payout, plot_training_data_sets)
from potion.streamlitapp.preference_saver import (
    preference_df_file_name, initialize_preference_df, save_curve_gen_preferences,
    get_pref, CURVE_GEN_IF, CURVE_GEN_BN, CURVE_GEN_IB)


def get_input_files(directory='inputs/*.csv'):
    """
    Gets all of the CSV files in the inputs directory and displays them to the user to select.

    Parameters
    ----------
    directory : str
        (Optional. Default: 'inputs/*.csv') The directory to check for input files

    Returns
    -------
    file_list : List[str]
        The List of file names in the directory which are CSV files
    input_index : int
        The default index value of the item to display to the user
    """
    # Detect CSV files in the current directory which may be input files
    file_list = glob.glob(directory)
    if preference_df_file_name in file_list:
        file_list.remove(preference_df_file_name)
    file_list.sort()

    # Remove the directory name from the display
    file_list = [filename.split(os.sep)[-1] for filename in file_list]

    # Select the default value for the selectbox
    if get_pref(CURVE_GEN_IF) in file_list:
        input_index = file_list.index(get_pref(CURVE_GEN_IF))
    else:
        input_index = 0

    return file_list, input_index


def get_price_files(directory='resources/*.csv'):
    """
    Gets all of the CSV files in the resources directory and displays them to the user to select.

    Parameters
    ----------
    directory : str
        (Optional. Default: 'resources/*.csv') The directory to check for price history files

    Returns
    -------
    file_list : List[str]
        The List of file names in the directory which are CSV files
    input_index : int
        The default index value of the item to display to the user
    """
    # Detect CSV files in the current directory which may be input files
    file_list = glob.glob(directory)
    file_list.sort()

    # Remove the directory name from the display
    file_list = [filename.split(os.sep)[-1] for filename in file_list]

    return file_list, 0


def initialize_curve_gen_session_state():
    """
    Initializes the session_state streamlit object so that the tool can use dynamic UI
    components in streamlit

    Returns
    -------
    None
    """
    if 'curves_df' not in st.session_state:
        st.session_state.curves_df = None

    if 'pdf_df' not in st.session_state:
        st.session_state.pdf_df = None

    if 'curve_plots' not in st.session_state:
        st.session_state.curve_plots = None

    if 'training_plots' not in st.session_state:
        st.session_state.training_plots = None

    if 'pdf_plots' not in st.session_state:
        st.session_state.pdf_plots = None

    if 'curve_unit_radios' not in st.session_state:
        st.session_state.curve_unit_radios = None

    if 'curve_grid_radios' not in st.session_state:
        st.session_state.curve_grid_radios = None

    if 'training_log_radios' not in st.session_state:
        st.session_state.training_log_radios = None

    if 'training_df' not in st.session_state:
        st.session_state.training_df = None

    if 'pref_df' not in st.session_state:
        st.session_state.pref_df = None

    if os.path.isfile(preference_df_file_name):
        st.session_state.pref_df = pd.read_csv(preference_df_file_name, sep=',')
    else:
        st.session_state.pref_df = initialize_preference_df()


def load_curve_gen_settings_panel():
    """
    Displays the curve generation settings UI panel to the user. When the user clicks
    the Generate Curves button, this function also kicks off the business logic of
    actually calculating the curves using the library and stores the results in the session_state
    for use in other areas of the streamlit app.

    Returns
    --------
    historical_file : str
        The user specified name of the price history file containing the training data
    input_file : str
        The user specified name of the input file containing the curves to be generated
    batch_number : int
        The user specified batch number identifying this set of results from others in the
        log directory
    initial_bankroll : float
        The user specified starting bankroll
    """
    batch_curve_form = st.form(key='curves')

    batch_curve_form.subheader('Curve Generation Settings')

    link = '[Open User Guide](' + \
           'http://localhost:8080/potion/user_guides/curve_generator_user_guide.html)'
    batch_curve_form.markdown(link, unsafe_allow_html=True)

    # Define the UI inputs
    file_list, input_index = get_input_files()
    input_file = batch_curve_form.selectbox('Select the Input File (directory ./inputs/*.csv)',
                                            file_list, index=input_index)

    help_panel = batch_curve_form.expander('Need Help? Click to Expand', expanded=False)
    help_panel.markdown(CG_INPUT_FILE_HELP_TEXT)

    price_file_list, price_input_index = get_price_files()
    historical_file = batch_curve_form.selectbox(
        'Select the Historical Prices File (directory ./resources/*.csv)',
        price_file_list, index=price_input_index)

    help_panel = batch_curve_form.expander('Need Help? Click to Expand', expanded=False)
    help_panel.markdown(CG_PRICES_FILE_HELP_TEXT)

    batch_number = batch_curve_form.number_input('Select the batch number', min_value=0,
                                                 max_value=1000000, value=get_pref(CURVE_GEN_BN),
                                                 step=1)

    help_panel = batch_curve_form.expander('Need Help? Click to Expand', expanded=False)
    help_panel.markdown(CG_BATCH_NUMBER_HELP_TEXT)

    initial_bankroll = batch_curve_form.number_input('Initial Bankroll:', min_value=1.0,
                                                     max_value=1000000.0,
                                                     value=float(get_pref(CURVE_GEN_IB)),
                                                     step=0.01, format='%.2f')

    help_panel = batch_curve_form.expander('Need Help? Click to Expand', expanded=False)
    help_panel.markdown(CG_INIT_BANKROLL_HELP_TEXT)

    batch_curve_button = batch_curve_form.form_submit_button('Generate Curves')

    # If the button is pressed, run the curve generation, and save the results
    # and plots in the session_state for use later
    if batch_curve_button:

        full_input_path = 'inputs' + os.sep + str(input_file)
        full_historical_path = 'resources' + os.sep + str(historical_file)

        try:
            cfg = build_generator_config(full_input_path, full_historical_path)

            # Run the curve generation
            run_curve_generation(cfg, batch_number)

            price_history_csv = pd.read_csv('resources' + os.sep + str(historical_file))

            res_dir = './batch_results/batch_{}/curve_generation/'.format(batch_number)

            # Read the results from CSVs
            training_df = read_training_data_from_csv(res_dir + 'training.csv')
            pdf_df = read_pdfs_from_csv(res_dir + 'pdfs.csv')
            curve_df = read_curves_from_csv(res_dir + 'curves.csv')

            # Generate our results plots
            curve_figures = plot_curves_from_csv(curve_df)
            pdf_figures = plot_pdf_and_option_payout(pdf_df, curve_df)

            # Get the plots of the training data sets
            training_data_plots = plot_training_data_sets(price_history_csv, training_df,
                                                          log_plot=False)

            st.session_state.training_plots = [
                training_data_plots[train_row.Ticker + '-' + train_row.Label]
                for i, train_row in curve_df.iterrows()]

            # Save in the session state for later
            st.session_state.curve_plots = curve_figures
            st.session_state.curves_df = curve_df
            st.session_state.training_df = training_df
            st.session_state.pdf_df = pdf_df
            st.session_state.pdf_plots = pdf_figures
            st.session_state.curve_unit_radios = ['Relative'] * len(curve_figures)
            st.session_state.curve_grid_radios = [True] * len(curve_figures)
            st.session_state.training_log_radios = [False] * len(curve_figures)

            save_curve_gen_preferences(str(input_file), str(historical_file), int(batch_number),
                                       float(initial_bankroll))
        except ValueError as e:
            st.error(e)
        except FileNotFoundError as e:
            st.error(e)

    # Return the UI values to the caller of the function
    return historical_file, input_file, batch_number, initial_bankroll


def load_curve_plot_panel(i: int, directory='./batch_results'):
    """
    Displays the generated curve plot to the user

    Parameters
    ----------
    i : int
        Index identifying the curve in the loop
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results

    Returns
    --------
    None
    """
    if st.session_state.curve_plots[i] is not None:
        st.plotly_chart(st.session_state.curve_plots[i], use_container_width=True)
        save_plotly_fig_to_file(
            directory, 'curve_plot.svg', st.session_state.curve_plots[i])


def load_curve_parameters_panel(i: int):
    """
    Displays the expandable panel to the user which contains the table containing
    the curve parameters

    Parameters
    ----------
    i : int
        Index identifying the curve in the loop

    Returns
    --------
    None
    """
    # The funny transposes and df copying here are solely to make streamlit
    # properly display the info as a row and not a column
    with st.expander('Show Curve Parameters', expanded=True):
        st.dataframe(pd.DataFrame(st.session_state.curves_df.iloc[i, 0:8].T).T)


def load_pdf_and_payout_panel(i: int, directory='./batch_results'):
    """
    Displays the expandable panel to the user which contains the graph of the
    probability PDF and option payout function which were used in the generation of the curve

    Parameters
    ----------
    i : int
        Index identifying the curve in the loop
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results

    Returns
    --------
    None
    """
    with st.expander('Show PDF and Option Payout', expanded=False):
        pdf_plot = st.session_state.pdf_plots[i]

        st.plotly_chart(pdf_plot, use_container_width=True)
        save_plotly_fig_to_file(directory, 'pdf_and_payout.svg', pdf_plot)


def load_training_price_path_panel(i: int, directory='./batch_results'):
    """
    Displays the expandable panel to the user which contains the price history
    and training data set

    Parameters
    ----------
    i : int
        Index identifying the curve in the loop
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results

    Returns
    --------
    None
    """
    if st.session_state.training_plots is not None:
        with st.expander('Show Training Data Price Path', expanded=False):

            training_plot = st.session_state.training_plots[i]

            if (training_plot.data[0].customdata[0] and
                    st.session_state.training_log_radios[i] == 'Prices'):
                training_plot.data[0].y = np.exp(training_plot.data[0].y)
                training_plot.data[1].y = np.exp(training_plot.data[1].y)
                training_plot.data[0].customdata = (False, False)
            elif (not training_plot.data[0].customdata[0] and
                  st.session_state.training_log_radios[i] == 'Log Prices'):
                training_plot.data[0].y = np.log(training_plot.data[0].y)
                training_plot.data[1].y = np.log(training_plot.data[1].y)
                training_plot.data[0].customdata = (True, True)

            st.plotly_chart(training_plot, use_container_width=True)
            save_plotly_fig_to_file(directory, 'training_data.svg', training_plot)


def load_plot_config_panel(i: int, train_row: pd.Series, initial_bankroll_slider: float):
    """
    Displays the configuration expandable panel to the user which contains some
    controls which let the user control the plot properties

    Parameters
    ----------
    i : int
        Index identifying the curve in the loop
    train_row : pandas.Series
        The row of the dataframe containing info about this curve
    initial_bankroll_slider : float
        The starting bankroll of the user

    Returns
    --------
    None
    """
    with st.expander('Configure Plots', expanded=False):

        curve_units = ['Relative', 'Absolute']

        st.session_state.curve_unit_radios[i] = st.radio('Select Curve Units', curve_units,
                                                         key='cu_radio_{}'.format(i))

        enable_grid_labels = ['Enabled', 'Disabled']

        st.session_state.curve_grid_radios[i] = st.radio('Enable Curve Plot Grid',
                                                         enable_grid_labels,
                                                         key='ceg_radio_{}'.format(i))

        training_log_labels = ['Prices', 'Log Prices']

        st.session_state.training_log_radios[i] = st.radio('Training Data Log Prices',
                                                           training_log_labels,
                                                           key='tlp_radio_{}'.format(i))

        if st.session_state.curve_grid_radios[i] == 'Enabled':
            grid_enable = True
        else:
            grid_enable = False

        fit_params = [train_row.A, train_row.B, train_row.C, train_row.D]
        if st.session_state.curve_unit_radios[i] == 'Absolute':

            current_price = st.session_state.training_df.CurrentPrice.values[0]
            strike = train_row.StrikePercent * current_price

            user_strike_normalized_premium = convert_fully_normalized_to_strike_normalized_curve(
                strike,
                initial_bankroll_slider,
                train_row.bet_fractions,
                evaluate_premium_curve(fit_params, train_row.bet_fractions)
            )
            opt_strike_normalized_premium = convert_fully_normalized_to_strike_normalized_curve(
                strike,
                initial_bankroll_slider,
                train_row.bet_fractions,
                train_row.curve_points)

            # print(strike_normalized_premium)

            (user_locked_collateral, user_absolute_premium) = \
                convert_strike_normalized_to_absolute_curve(strike, initial_bankroll_slider,
                                                            train_row.bet_fractions,
                                                            user_strike_normalized_premium)
            (opt_locked_collateral, opt_absolute_premium) = \
                convert_strike_normalized_to_absolute_curve(strike, initial_bankroll_slider,
                                                            train_row.bet_fractions,
                                                            opt_strike_normalized_premium)
            st.session_state.curve_plots[i].update_layout(
                plot_bgcolor='rgb(230,230,230)',
                title="Absolute USDC Curve",
                xaxis_title='Locked USDC',
                yaxis_title='USDC Premium'
            ).update_xaxes(showgrid=grid_enable).update_yaxes(showgrid=grid_enable)

            st.session_state.curve_plots[i].update_layout(legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ))

            st.session_state.curve_plots[i].data[0].x = opt_locked_collateral
            st.session_state.curve_plots[i].data[0].y = opt_absolute_premium
            st.session_state.curve_plots[i].data[1].x = user_locked_collateral
            st.session_state.curve_plots[i].data[1].y = user_absolute_premium

        else:

            st.session_state.curve_plots[i].update_layout(
                plot_bgcolor='rgb(230,230,230)',
                title="On-Chain Curve",
                xaxis_title='Utilisation',
                yaxis_title='Premium (%)'
            ).update_xaxes(showgrid=grid_enable).update_yaxes(showgrid=grid_enable)

            st.session_state.curve_plots[i].update_layout(legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ))

            st.session_state.curve_plots[i].data[0].x = train_row.bet_fractions
            st.session_state.curve_plots[i].data[0].y = train_row.curve_points
            st.session_state.curve_plots[i].data[1].x = train_row.bet_fractions
            st.session_state.curve_plots[i].data[1].y = evaluate_premium_curve(
                fit_params, train_row.bet_fractions)


def load_edit_curve_panel(i: int, train_row: pd.Series, batch_number: int):
    """
    This function displays the expandable panel which allows the user to edit the curve

    Parameters
    ----------
    i : int
        Index identifying the curve in the loop
    train_row : pandas.Series
        The row of the dataframe containing info about this curve
    batch_number : int
        ID number indicating the batch of simulation results

    Returns
    --------
    None
    """
    with st.expander('Edit Curve', expanded=False):
        num_a = st.number_input('A', min_value=0.0, max_value=100.0, value=train_row.A,
                                step=0.00000001, format='%.8f', key='A_num_{}'.format(i))
        num_b = st.number_input('B', min_value=0.0, max_value=100.0, value=train_row.B,
                                step=0.00000001, format='%.8f', key='B_num_{}'.format(i))
        num_c = st.number_input('C', min_value=0.0, max_value=100.0, value=train_row.C,
                                step=0.00000001, format='%.8f', key='C_num_{}'.format(i))
        num_d = st.number_input('D', min_value=0.0, max_value=100.0, value=train_row.D,
                                step=0.00000001, format='%.8f', key='D_num_{}'.format(i))

        update_curve_button = st.button('Update Curve', key='uc_{}'.format(i))

        # Run when the button is pressed
        if update_curve_button:
            # print('Updating curve')
            st.session_state.curves_df.iloc[i, 4] = num_a
            st.session_state.curves_df.iloc[i, 5] = num_b
            st.session_state.curves_df.iloc[i, 6] = num_c
            st.session_state.curves_df.iloc[i, 7] = num_d

            fit_params = [num_a, num_b, num_c, num_d]

            st.session_state.curve_plots[i].data[1].x = train_row.bet_fractions
            st.session_state.curve_plots[i].data[1].y = \
                evaluate_premium_curve(fit_params, train_row.bet_fractions)

            res_dir = './batch_results/batch_{}/curve_generation/'.format(batch_number)

            st.session_state.curves_df.to_csv(res_dir + 'curves.csv',
                                              index=False)


def load_curve_gen_results_panel(batch_number: int, initial_bankroll_slider: float,
                                 directory='./batch_results'):
    """
    This function displays the streamlit panels containing the results of the curve
    generation process to the user

    Parameters
    ----------
    batch_number : int
        ID number indicating the batch of simulation results
    initial_bankroll_slider : float
        The starting bankroll of the user
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results

    Returns
    --------
    None
    """
    # Will not be none once the user clicks the button to generate the curves
    if st.session_state.curves_df is not None:

        with st.container():

            # Loop over each curve generated and display the panels to the user
            for i, train_row in st.session_state.curves_df.iterrows():
                # print(train_row)

                with st.container():
                    st.subheader('Curve {}: {}, {}, Strike {}, Expiration {}'.format(
                        i, train_row.Ticker, train_row.Label, train_row.StrikePercent,
                        train_row.Expiration))

                    plot_dir = directory + \
                        '/batch_{}/curve_generation/plots/'.format(batch_number) + \
                        'curve_{}_{}_{}_s{}_e{}'.format(
                            i, train_row.Ticker, train_row.Label, train_row.StrikePercent,
                            train_row.Expiration)
                    Path(plot_dir).mkdir(parents=True, exist_ok=True)

                    col1, col2 = st.columns(2)

                    # Display the curve plot in the left column
                    with col1.container():
                        load_curve_plot_panel(i, directory=plot_dir)

                    # Display the controls panels in the right column
                    with col2.container():
                        load_curve_parameters_panel(i)
                        load_pdf_and_payout_panel(i, directory=plot_dir)
                        load_training_price_path_panel(i, directory=plot_dir)
                        load_plot_config_panel(i, train_row, initial_bankroll_slider)
                        load_edit_curve_panel(i, train_row, batch_number)

            with st.expander('Output CSVs', expanded=False):
                st.subheader('Curve CSV')
                st.dataframe(st.session_state.curves_df)

                st.subheader('Training CSV')
                st.dataframe(st.session_state.training_df)

                st.subheader('PDF CSV')
                st.dataframe(st.session_state.pdf_df)

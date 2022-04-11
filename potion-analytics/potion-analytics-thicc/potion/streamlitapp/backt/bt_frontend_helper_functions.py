"""
This module provides the frontend helper code for the backtesting GUI
"""
import pandas as pd
import streamlit as st
import os
from pathlib import Path
import glob

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

from potion.backtest.batch_backtester import PathGenMethod
from potion.streamlitapp.backt import (
    BT_BATCH_NUMBER_HELP_TEXT, BT_INIT_BANKROLL_HELP_TEXT, BT_PATH_GEN_METHOD_HELP_TEXT,
    BT_NUM_PATHS_HELP_TEXT, BT_PATH_LEN_HELP_TEXT, BT_UTIL_HElP_TEXT)
from potion.streamlitapp.backt.backtest_helper_functions import run_backtesting_script
from potion.streamlitapp.backt.bt_plot import plot_backtesting_paths, plot_performance_scatter_plot
from potion.streamlitapp.curvegen.cg_file_io import save_plotly_fig_to_file, read_curves_from_csv
from potion.streamlitapp.preference_saver import (
    preference_df_file_name, initialize_preference_df, save_curve_backtester_preferences,
    get_pref, CURVE_BACK_IB, CURVE_BACK_PG, CURVE_BACK_NP,
    CURVE_BACK_PL, CURVE_BACK_UT)


def _check_curve_rows_eq(row_1, row_2):
    """
    Checks whether two curve rows are equal

    Parameters
    ----------
    row_1 : pandas.Series
        The first row to compare
    row_2 : pandas.Series
        The second row to compare

    Returns
    -------
    equal : bool
        True if the rows are equal, False otherwise
    """
    return (row_1['Ticker'] == row_2['Ticker']) & (
            row_1['Label'] == row_2['Label']) & (
                   row_1['Expiration'] == row_2['Expiration']) & (
                   row_1['StrikePercent'] == row_2['StrikePercent']) & (
                   row_1['A'] == row_2['A']) & (
                   row_1['B'] == row_2['B']) & (
                   row_1['C'] == row_2['C']) & (
                   row_1['D'] == row_2['D'])


def _check_matching_curve_row(perf_row, curve_row):
    """
    Checks whether a performance_df row corresponds to the curve_df row

    Parameters
    ----------
    perf_row : pandas.Series
        The first row to compare
    curve_row : pandas.Series
        The second row to compare

    Returns
    -------
    equal : bool
        True if the rows are equal, False otherwise
    """
    key = perf_row['key']
    ticker = key.split('-')[0]
    label = key.split('-')[1]
    return (ticker == curve_row['Ticker']) & (
            label == curve_row['Label']) & (
                   perf_row['duration'] == curve_row['Expiration']) & (
                   perf_row['strike'] == curve_row['StrikePercent'])


def _get_matching_curve(perf_row, curve_df):
    """
    Takes a row of backtest performance results and gets the matching curve row from the curve
    DataFrame.

    Parameters
    ----------
    perf_row : pandas.Series
        The row of the performance DataFrame
    curve_df : pandas.DataFrame
        The DataFrame containing the curves being searched

    Returns
    -------
    curve_id : int
        The row number in the curve DataFrame corresponding to this row of performance data
    curve_row : pandas.Series
        The row containing the curve information
    """
    curve_id = -1
    curve_row = None
    for idx, row in curve_df.iterrows():
        if _check_matching_curve_row(perf_row, row):
            curve_id = idx
            curve_row = row
            break

    return curve_id, curve_row


def get_batch_numbers(directory='./batch_results'):
    """
    Searches the batch_results directory for existing results from curve generation to
    allow the user to select an existing batch number.

    Parameters
    ----------
    directory : str
        (Optional. Default: './batch_results') The directory containing curve generation results

    Returns
    -------
    batch_numbers : List[int]
        The List of batch numbers from existing curve generation results
    """

    # Grab all of the batch_ folders
    dirs = glob.glob(os.path.join(directory, "*", ""))

    batch_numbers = []
    for d in dirs:
        # Find the directory name for the batch
        dir_names = d.split(os.sep)
        dir_names = list(filter(lambda a: a != '', dir_names))

        # Split the number and save it
        batch_dir = dir_names[-1]
        if 'batch_' in batch_dir:
            split_name = batch_dir.split('_')
            batch_numbers.append(int(split_name[-1]))

    return batch_numbers


def _load_curve_batch(batch_num: int):
    """
    Loads a preview DataFrame so the user can see the curves generated for the batch

    Parameters
    ----------
    batch_num : int
        The batch number containing the curves to load

    Returns
    -------
    None
    """
    res_dir = './batch_results/batch_{}/curve_generation/'.format(batch_num)
    curve_filename = res_dir + 'curves.csv'

    if os.path.exists(curve_filename):
        st.session_state.preview_df = read_curves_from_csv(curve_filename)


def initialize_backtester_session_state():
    """
    Initializes the session_state streamlit object so that we can have dynamic UI
    components in streamlit

    Returns
    -------
    None
    """
    if 'backtesters' not in st.session_state:
        st.session_state.backtesters = None

    if 'log_file_names' not in st.session_state:
        st.session_state.log_file_names = None

    if 'full_performance_df' not in st.session_state:
        st.session_state.full_performance_df = None

    if 'plot_dicts' not in st.session_state:
        st.session_state.plot_dicts = None

    if 'path_figs' not in st.session_state:
        st.session_state.path_figs = None

    if 'performance_plot' not in st.session_state:
        st.session_state.performance_plot = None

    if 'pref_df' not in st.session_state:
        st.session_state.pref_df = None

    if 'preview_df' not in st.session_state:
        st.session_state.preview_df = None

    if 'selected_indices' not in st.session_state:
        st.session_state.selected_indices = None

    if 'write_plots_to_file' not in st.session_state:
        st.session_state.write_plots_to_file = None

    if os.path.isfile(preference_df_file_name):
        st.session_state.pref_df = pd.read_csv(preference_df_file_name, sep=',')
    else:
        st.session_state.pref_df = initialize_preference_df()


def load_backtester_settings_panel():
    """
    Displays the backtester settings panel to the user. When the user clicks the start
    button this function also kicks off the business logic of actually running the backtesting
    simulation and stores the results in the session_state for use in other areas of the
    streamlit app.

    Returns
    -------
    batch_number : int
        The user provided results id number from the UI input
    path_gen_method : PathGenMethod
        The method to use to generate backtesting paths from the UI input
    num_paths : int
        The number of paths in the simulation from the UI input
    path_length :int
        The length of the paths in days from the UI input
    util : float
        The util to use in the backtesting simulation from the UI input
    """
    batch_number_form = st.form(key='batch_num_form')

    batch_number_form.subheader('Backtesting Settings')

    link = '[Open User Guide](http://localhost:8080/potion/user_guides/backtester_user_guide.html)'
    batch_number_form.markdown(link, unsafe_allow_html=True)

    batch_numbers = get_batch_numbers()

    if not batch_numbers:
        batch_number_form.markdown(
            'No Generated Curve results detected in results directory (./batch_results). ' +
            'Please Run the Curve Generator to get started.  \n' +
            '[Open Curve Generator](http://localhost:8502/)')

        batch_number_form.form_submit_button('Select')

        return 0, PathGenMethod.SKEWED_T, 0, 0, 0

    batch_number = batch_number_form.selectbox(
        'Select the results batch number to choose ' +
        'generated curves (directory ./batch_results)',
        batch_numbers, index=0)

    help_panel = batch_number_form.expander('Need Help? Click to Expand', expanded=False)
    help_panel.markdown(BT_BATCH_NUMBER_HELP_TEXT)

    select_button = batch_number_form.form_submit_button('Select')

    if select_button:
        _load_curve_batch(batch_number)

    if st.session_state.preview_df is not None:

        gb = GridOptionsBuilder.from_dataframe(st.session_state.preview_df)
        gb.configure_pagination()
        gb.configure_selection(selection_mode='multiple', use_checkbox=True)
        grid_options = gb.build()

        st.text('Loaded Curve Batch. Select Rows to generate output plots:')
        selected_rows = AgGrid(st.session_state.preview_df, gridOptions=grid_options,
                               update_mode=GridUpdateMode.SELECTION_CHANGED)

        (col_a, col_b, _, _, _, _, _, _, _, _) = st.columns(10)
        plot_all = col_a.checkbox('Plot All Curves', value=True)
        st.session_state.write_plots_to_file = col_b.checkbox('Write Plots to File', value=True)

        if selected_rows is not None:
            # print(selected_rows)
            selected_rows = selected_rows['selected_rows']
            selected_rows = pd.DataFrame(selected_rows)

            if plot_all:
                selected_rows = st.session_state.preview_df

            # No ability to get the row numbers from the AgGrid component unfortunately
            selected_indices = []
            for idx, row in selected_rows.iterrows():
                row['StrikePercent'] = float(row['StrikePercent'])
                row_pd = pd.Series(row)

                for r_index, p_row in st.session_state.preview_df.iterrows():

                    row_pd.name = p_row.name
                    if _check_curve_rows_eq(row_pd, p_row):
                        selected_indices.append(r_index)
                        break

            st.text('Rows Selected for Plotting:')
            st.dataframe(selected_rows)

            st.session_state.selected_indices = selected_indices

        batch_backtest_form = st.form(key='backtests')

        initial_bankroll = batch_backtest_form.number_input('Initial Bankroll:', min_value=1.0,
                                                            max_value=1000000.0,
                                                            value=float(get_pref(CURVE_BACK_IB)),
                                                            step=0.01, format='%.2f')

        help_panel = batch_backtest_form.expander('Need Help? Click to Expand', expanded=False)
        help_panel.markdown(BT_INIT_BANKROLL_HELP_TEXT)

        path_gen_methods = ['Histogram', 'Student\'s T with Skew']
        if get_pref(CURVE_BACK_PG) in path_gen_methods:
            selected_index = path_gen_methods.index(get_pref(CURVE_BACK_PG))
        else:
            selected_index = 1

        path_gen_method_text = batch_backtest_form.selectbox('Select path generation method',
                                                             path_gen_methods,
                                                             index=selected_index)

        help_panel = batch_backtest_form.expander('Need Help? Click to Expand', expanded=False)
        help_panel.markdown(BT_PATH_GEN_METHOD_HELP_TEXT)

        num_paths = batch_backtest_form.number_input('Number of paths', min_value=1, max_value=3000,
                                                     step=1,
                                                     value=get_pref(CURVE_BACK_NP))

        help_panel = batch_backtest_form.expander('Need Help? Click to Expand', expanded=False)
        help_panel.markdown(BT_NUM_PATHS_HELP_TEXT)

        path_length = batch_backtest_form.number_input('Path length in number of days', min_value=1,
                                                       max_value=1000, step=1,
                                                       value=get_pref(CURVE_BACK_PL))

        help_panel = batch_backtest_form.expander('Need Help? Click to Expand', expanded=False)
        help_panel.markdown(BT_PATH_LEN_HELP_TEXT)

        util = batch_backtest_form.number_input(
            'Utilization (between 0.0 and 1.0)', min_value=0.0, max_value=1.0, step=0.01,
            value=get_pref(CURVE_BACK_UT))

        help_panel = batch_backtest_form.expander('Need Help? Click to Expand', expanded=False)
        help_panel.markdown(BT_UTIL_HElP_TEXT)

        batch_backtest_form.text('Backtesting Progress:')
        backtest_progress_bar = batch_backtest_form.progress(0.0)
        batch_backtest_form.text('Plot Generation Progress')
        plot_progress_bar = batch_backtest_form.progress(0.0)

        batch_backtest_button = batch_backtest_form.form_submit_button('Run Backtesting')

        # Convert the string into the enum object for convenience
        if path_gen_method_text == 'Histogram':
            path_gen_method = PathGenMethod.HISTOGRAM
        elif path_gen_method_text == 'Student\'s T with Skew':
            path_gen_method = PathGenMethod.SKEWED_T
        else:
            path_gen_method = PathGenMethod.SKEWED_T

        # If the button is pressed, run the backtesting, and save the results and plots in
        # the session_state for use later
        if batch_backtest_button:

            res_dir = './batch_results/batch_{}/curve_generation/'.format(batch_number)

            if not os.path.exists(res_dir):
                st.error('Missing curve generation results.')
                st.markdown(
                    'Selected batch_{} folder exists, but does not contain '.format(batch_number) +
                    'curve generation results. (./batch_results/batch_{}). '.format(batch_number) +
                    'Please Run the Curve Generator to get started, or ' +
                    'select another results folder.  \n' +
                    '[Open Curve Generator](http://localhost:8502/)')
                return 0, PathGenMethod.SKEWED_T, 0, 0, 0

            train_filename = res_dir + 'training.csv'
            curve_filename = res_dir + 'curves.csv'
            pdf_filename = res_dir + 'pdfs.csv'

            # Run the backtesting and generate our results plots
            backtester_map, log_file_names, full_performance_df, plot_dicts = \
                run_backtesting_script(batch_number, curve_filename, train_filename, pdf_filename,
                                       [util], path_gen_method,
                                       num_paths, path_length, initial_bankroll,
                                       backtest_progress_bar=backtest_progress_bar,
                                       plot_progress_bar=plot_progress_bar)

            # Map each path history to performance_df row
            price_path_figs = []
            for i, perf_row in full_performance_df.iterrows():

                backtester = backtester_map[perf_row.util]

                path_figs = plot_backtesting_paths(backtester, path_length)

                for j, key in enumerate(backtester.keys):
                    if key == perf_row.key:
                        price_path_figs.append(path_figs[j])

            # Save in the session state for later
            st.session_state.backtesters = backtester_map
            st.session_state.log_file_names = log_file_names
            st.session_state.full_performance_df = full_performance_df
            st.session_state.plot_dicts = plot_dicts
            st.session_state.path_figs = price_path_figs

            save_curve_backtester_preferences(
                batch_number, initial_bankroll, str(path_gen_method_text), num_paths,
                path_length, util)

        # Return the UI values to the caller of the function
        return batch_number, path_gen_method, num_paths, path_length, util
    else:
        return 0, PathGenMethod.SKEWED_T, 0, 0, 0


def load_performance_statistics_panel(perf_row):
    """
    Displays the expandable panel to the user which contains the table containing the
    backtesting performance statistics to user

    Parameters
    ----------
    perf_row : pandas.Series
        The row from the performance DataFrame to display

    Returns
    -------
    None
    """
    # The funny transposes and df copying here are solely to make streamlit properly display the
    # info as a row and not a column
    with st.expander('Show Percentile Statistics', expanded=True):
        st.dataframe(pd.DataFrame(perf_row.T).T)


def load_backtesting_paths_panel(i, directory='./batch_results', save_file=True):
    """
    Displays the expandable panel to the user which contains the set of backtesting price
    paths to the user

    Parameters
    ----------
    i : int
        Index identifying the curve in the loop
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results
    save_file : bool
        (Optional. Default: True) Whether to save the plot to a file

    Returns
    -------
    None
    """
    with st.expander('Show Generated Backtesting Paths', expanded=False):
        st.plotly_chart(st.session_state.path_figs[i], use_container_width=True)
        if save_file:
            save_plotly_fig_to_file(directory, 'backtest_paths.svg', st.session_state.path_figs[i])


def load_pdf_payout_and_histogram_panel(fig_pdf_pay, directory='./batch_results', save_file=True):
    """
    Displays the expandable panel to the user which contains the graph of the probability PDF
    and option payout function which were used in the generation of the curve compared to the
    histogram of price paths from the backtesting scenario

    Parameters
    ----------
    fig_pdf_pay : plotly.graph_object.Figure
        The plot to display to the user
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results
    save_file : bool
        (Optional. Default: True) Whether to save the plot to a file

    Returns
    -------
    None
    """
    with st.expander('Show Paths vs. PDF and Option Payout', expanded=False):
        st.plotly_chart(fig_pdf_pay, use_container_width=True)
        if save_file:
            save_plotly_fig_to_file(directory, 'pdf_payout_and_histogram.svg', fig_pdf_pay)


def load_performance_scatter_panel(performance_df, batch_number, directory='./batch_results',
                                   save_file=True):
    """
    Displays the expandable panel to the user which contains a scatterplot of the median
    CAGR vs. median max drawdown. One point is graphed for each row (curve) in the dataframe.

    Parameters
    ----------
    performance_df : pandas.DataFrame
        The performance statistics to be plotted
    batch_number : int
        ID number indicating the batch of simulation results
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results
    save_file : bool
        (Optional. Default: True) Whether to save the plot to a file

    Returns
    -------
    None
    """
    performance_plot = plot_performance_scatter_plot(performance_df)

    st.session_state.performance_plot = performance_plot

    with st.expander('Show Performance vs. Drawdown', expanded=True):
        st.plotly_chart(performance_plot, use_container_width=True)
        if save_file:
            save_plotly_fig_to_file(directory,
                                    'batch_{}_backtest_performance_scatter.svg'.format(
                                        batch_number), performance_plot)


def load_user_curve_plot_panel(col, fig_user_br, fig_user_cagr, fig_user_util, fig_user_amt,
                               directory='./batch_results', save_file=True):
    """
    Displays the four expandable panels to the user which contain the backtesting results for the
    user's ABCD curve. The panels are bankrolls, CAGRs, Util, and Amounts of contracts
    traded in the simulation.

    Parameters
    ----------
    col: streamlit.column
        The column container which will contain the four plots
    fig_user_br : plotly.graph_object.Figure
        The user bankroll plot
    fig_user_cagr : plotly.graph_object.Figure
        The user cagr plot
    fig_user_util : plotly.graph_object.Figure
        The user util plot
    fig_user_amt : plotly.graph_object.Figure
        The amount of contracts traded plot
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results
    save_file : bool
        (Optional. Default: True) Whether to save the plot to a file

    Returns
    -------
    None
    """
    # Display the user curve plots in the left column
    with col.container():
        with st.expander('Show Bankroll Plot for User ABCD Curve', expanded=False):
            st.plotly_chart(fig_user_br, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(directory, 'user_curve_bankroll.svg', fig_user_br)

        with st.expander('Show CAGR Plot for User ABCD Curve', expanded=False):
            st.plotly_chart(fig_user_cagr, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(directory, 'user_curve_cagr.svg', fig_user_cagr)

        with st.expander('Show Util Plot for User ABCD Curve', expanded=False):
            st.plotly_chart(fig_user_util, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(directory, 'user_curve_util.svg', fig_user_util)

        with st.expander('Show Amount Plot for User ABCD Curve', expanded=False):
            st.plotly_chart(fig_user_amt, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(directory, 'user_curve_amounts.svg', fig_user_amt)


def load_opt_curve_plot_panel(col, fig_opt_br, fig_opt_cagr, fig_opt_util, fig_opt_amt,
                              directory='./batch_results', save_file=True):
    """
    Displays the four expandable panels to the user which contain the backtesting results for the
    calculated optimum curve. The panels are bankrolls, CAGRs, Util, and Amounts of contracts
    traded in the simulation.

    Parameters
    ----------
    col : streamlit.column
        The column container which will contain the four plots
    fig_opt_br : plotly.graph_object.Figure
        The optimal curve bankroll plot
    fig_opt_cagr : plotly.graph_object.Figure
        The optimal curve cagr plot
    fig_opt_util : plotly.graph_object.Figure
        The  optimal curve util plot
    fig_opt_amt : plotly.graph_object.Figure
        The amount of contracts traded plot
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results
    save_file : bool
        (Optional. Default: True) Whether to save the plot to a file

    Returns
    -------
    None
    """
    # Display the optimal curve plots in the right column
    with col.container():
        with st.expander('Show Bankroll Plot for Minimum Optimal Curve', expanded=False):
            st.plotly_chart(fig_opt_br, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(directory, 'minimum_curve_bankroll.svg', fig_opt_br)

        with st.expander('Show CAGR Plot for Minimum Optimal Curve', expanded=False):
            st.plotly_chart(fig_opt_cagr, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(directory, 'minimum_curve_cagr.svg', fig_opt_cagr)

        with st.expander('Show Util Plot for Minimum Optimal Curve', expanded=False):
            st.plotly_chart(fig_opt_util, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(directory, 'minimum_curve_util.svg', fig_opt_util)

        with st.expander('Show Amount Plot for Minimum Optimal Curve', expanded=False):
            st.plotly_chart(fig_opt_amt, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(directory, 'minimum_curve_amounts.svg', fig_opt_amt)


def load_backtester_results_panel(batch_number):
    """
    This function displays the streamlit panels containing the results of the backtesting process
    to the user

    Parameters
    ----------
    batch_number : int
        ID number indicating the batch of simulation results

    Returns
    -------
    None
    """
    if st.session_state.plot_dicts is not None:

        with st.container():

            performance_df = st.session_state.full_performance_df
            load_performance_scatter_panel(
                performance_df, batch_number,
                directory='./batch_results/batch_{}/backtesting/plots/'.format(batch_number))

            for perf_id, perf_row in performance_df.iterrows():

                curve_id, curve_row = _get_matching_curve(perf_row, st.session_state.preview_df)

                if st.session_state.selected_indices is not None:
                    if curve_id in st.session_state.selected_indices:

                        plot_dict = st.session_state.plot_dicts[perf_id]
                        fig_user_br = plot_dict['user_br']
                        fig_opt_br = plot_dict['opt_br']
                        fig_user_cagr = plot_dict['user_cagr']
                        fig_opt_cagr = plot_dict['opt_cagr']
                        fig_user_util = plot_dict['user_util']
                        fig_opt_util = plot_dict['opt_util']
                        fig_user_amt = plot_dict['user_amt']
                        fig_opt_amt = plot_dict['opt_amt']
                        fig_pdf_pay = plot_dict['pdf_and_pay']

                        with st.container():
                            st.subheader(
                                'Curve {}: {}, {}, Strike {}, Expiration {}'.format(
                                    curve_id, curve_row.Ticker, curve_row.Label,
                                    curve_row.StrikePercent, curve_row.Expiration))

                            res_dir = './batch_results/batch_{}/backtesting/plots/'.format(
                                batch_number) + 'curve_{}_{}_{}_s{}_e{}'.format(
                                curve_id, curve_row.Ticker, curve_row.Label,
                                curve_row.StrikePercent, curve_row.Expiration)

                            if st.session_state.write_plots_to_file:
                                Path(res_dir).mkdir(parents=True, exist_ok=True)

                            load_performance_statistics_panel(perf_row)
                            load_backtesting_paths_panel(
                                curve_id, directory=res_dir,
                                save_file=st.session_state.write_plots_to_file)
                            load_pdf_payout_and_histogram_panel(
                                fig_pdf_pay, directory=res_dir,
                                save_file=st.session_state.write_plots_to_file)

                            col1, col2 = st.columns(2)
                            load_user_curve_plot_panel(
                                col1, fig_user_br, fig_user_cagr, fig_user_util, fig_user_amt,
                                directory=res_dir, save_file=st.session_state.write_plots_to_file)
                            load_opt_curve_plot_panel(
                                col2, fig_opt_br, fig_opt_cagr, fig_opt_util, fig_opt_amt,
                                directory=res_dir, save_file=st.session_state.write_plots_to_file)

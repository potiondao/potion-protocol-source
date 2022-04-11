"""
This module provides the frontend helper code for the portfolio backtesting GUI
"""
import pandas as pd
import streamlit as st
import os
from pathlib import Path
import glob

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

from potion.backtest.multi_asset_backtester import PathGenMethod
from potion.streamlitapp.multibackt import (
    PB_BATCH_NUMBER_HELP_TEXT, PB_PATH_GEN_HELP_TEXT, PB_NUM_PATHS_HELP_TEXT,
    PB_PATH_LENGTH_HELP_TEXT, PB_INIT_BANKROLL_HELP_TEXT)
from potion.streamlitapp.multibackt.ma_backtest_helper_functions import run_backtesting_script
from potion.streamlitapp.multibackt.ma_plot import (
    plot_multi_asset_paths, create_backtesting_plots, calc_total_num_plot_tasks)
from potion.streamlitapp.curvegen.cg_file_io import save_plotly_fig_to_file
from potion.streamlitapp.curvegen.cg_file_io import read_pdfs_from_csv, read_training_data_from_csv
from potion.streamlitapp.multibackt.ma_file_io import read_multi_asset_curves_from_csv
from potion.streamlitapp.preference_saver import (
    preference_df_file_name, initialize_preference_df, save_pool_backtester_preferences,
    get_pref, POOL_BACK_PG, POOL_BACK_NP, POOL_BACK_PL, POOL_BACK_IB)


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
    return (row_1['Label'] == row_2['Label']) & (
            row_1['Backtest_ID'] == row_2['Backtest_ID']) & (
                   row_1['Curve_ID'] == row_2['Curve_ID']) & (
                   row_1['Asset'] == row_2['Asset']) & (
                   row_1['Expiration'] == row_2['Expiration']) & (
                   row_1['StrikePercent'] == row_2['StrikePercent']) & (
                   row_1['A'] == row_2['A']) & (
                   row_1['B'] == row_2['B']) & (
                   row_1['C'] == row_2['C']) & (
                   row_1['D'] == row_2['D'])


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


def initialize_multi_asset_backtester_session_state():
    """
    Initializes the session_state streamlit object so that we can have dynamic UI
    components in streamlit

    Returns
    -------
    None
    """
    if 'multi_asset_return_dists' not in st.session_state:
        st.session_state.multi_asset_return_dists = None

    if 'marginal_dists' not in st.session_state:
        st.session_state.marginal_dists = None

    if 'ma_path_plot_map' not in st.session_state:
        st.session_state.ma_path_plot_map = None

    if 'ma_backtester_map' not in st.session_state:
        st.session_state.ma_backtester_map = None

    if 'ma_pdf_and_payout_fig_map' not in st.session_state:
        st.session_state.ma_pdf_and_payout_fig_map = None

    if 'ma_performance_df' not in st.session_state:
        st.session_state.ma_performance_df = None

    if 'ma_performance_plot_list' not in st.session_state:
        st.session_state.ma_performance_plot_list = None

    if 'batch_number' not in st.session_state:
        st.session_state.batch_number = None

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


def load_multi_asset_settings_panel():
    """
    Displays the multi asset backtester settings panel to the user. When the user clicks the
    start button this function also kicks off the business logic of actually running the
    backtesting simulation and stores the results in the session_state for use in other
    areas of the streamlit app.

    Returns
    -------
    batch_number : int
        A number to identify the results of this batch from others in the log files
    """
    batch_input_form = st.form(key='batch-input-form')

    batch_input_form.subheader('Results Selection')

    link = '[Open User Guide](http://localhost:8080/potion/' + \
           'user_guides/pool_backtester_user_guide.html)'
    batch_input_form.markdown(link, unsafe_allow_html=True)

    batch_numbers = get_batch_numbers()

    if not batch_numbers:
        batch_input_form.markdown(
            'No Generated Curve results detected in results directory (./batch_results). ' +
            'Please Run the Curve Generator to get started.  \n' +
            '[Open Curve Generator](http://localhost:8502/)')

        batch_input_form.form_submit_button('Submit')

        return -1
    else:

        batch_number = batch_input_form.selectbox(
            'Select the results batch number to choose ' +
            'generated curves (directory ./batch_results)',
            batch_numbers, index=0)

        help_panel = batch_input_form.expander('Need Help? Click to Expand', expanded=False)
        help_panel.markdown(PB_BATCH_NUMBER_HELP_TEXT)

        batch_number_button = batch_input_form.form_submit_button('Select')

        if batch_number_button:

            st.session_state.batch_number = batch_number

        if st.session_state.batch_number is None:
            return -1

        # Read the CSV output from the curve generator and initialize the batch backtesting object
        res_dir = './batch_results/batch_{}/pool_creation/'.format(
            batch_number)
        ma_input_file = res_dir + 'multi_asset_input.csv'
        train_filename = './batch_results/batch_{}/curve_generation/training.csv'.format(
            st.session_state.batch_number)
        pdf_filename = './batch_results/batch_{}/curve_generation/pdfs.csv'.format(
            st.session_state.batch_number)

        if not os.path.isfile(train_filename):
            st.error('Missing curve generation results.')
            st.markdown(
                'Selected batch_{} folder exists, but does not contain '.format(
                    st.session_state.batch_number) +
                'curve generation results. (./batch_results/batch_{}). '.format(
                    st.session_state.batch_number) +
                'Please Run the Curve Generator to get started, or ' +
                'select another results folder.  \n' +
                '[Open Curve Generator](http://localhost:8502/)')
            return -1

        if not os.path.isfile(pdf_filename):
            st.error('Missing curve generation results.')
            st.markdown(
                'Selected batch_{} folder exists, but does not contain '.format(
                    st.session_state.batch_number) +
                'curve generation results. (./batch_results/batch_{}). '.format(
                    st.session_state.batch_number) +
                'Please Run the Curve Generator to get started, or ' +
                'select another results folder.  \n' +
                '[Open Curve Generator](http://localhost:8502/)')
            return -1

        if not os.path.isfile(ma_input_file):
            st.error('Missing Pool Creation results.')
            st.markdown(
                'Selected batch_{} folder exists, but does not contain '.format(
                    st.session_state.batch_number) +
                'Pool Creation results. (./batch_results/batch_{}). '.format(
                    st.session_state.batch_number) +
                'Please Run the Pool Creator to get started, or ' +
                'select another results folder.  \n' +
                '[Open Pool Creator](http://localhost:8504/)')
            return -1

        ma_curve_df = read_multi_asset_curves_from_csv(ma_input_file)
        training_df = read_training_data_from_csv(train_filename)
        pdf_df = read_pdfs_from_csv(pdf_filename)
        st.session_state.preview_df = ma_curve_df

        gb = GridOptionsBuilder.from_dataframe(st.session_state.preview_df)
        gb.configure_pagination()
        gb.configure_selection(selection_mode='multiple', use_checkbox=True)
        grid_options = gb.build()

        st.text('Loaded Portfolio Batch. Select Rows to generate output plots:')
        selected_rows = AgGrid(st.session_state.preview_df, gridOptions=grid_options,
                               update_mode=GridUpdateMode.SELECTION_CHANGED)

        (col_a, col_b, _, _, _, _, _, _, _, _) = st.columns(10)
        plot_all = col_a.checkbox('Plot All Portfolios', value=True)
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

            # Get all of the backtest IDs of the rows selected so we can grab rows with
            # the same backtest ID too
            selected_backtest_ids = []
            for index in selected_indices:
                bt_id = int(st.session_state.preview_df.iloc[index]['Backtest_ID'])
                if bt_id not in selected_backtest_ids:
                    selected_backtest_ids.append(bt_id)

            included_indices = [idx for idx, row in st.session_state.preview_df.iterrows()
                                if int(row['Backtest_ID']) in selected_backtest_ids]

            included_rows = st.session_state.preview_df[st.session_state.preview_df.index.isin(
                included_indices)]

            st.text('Rows Selected for Plotting:')
            st.dataframe(included_rows)

            st.session_state.selected_indices = included_indices

        ma_backtest_form = st.form(key='ma-backtest')
        ma_backtest_form.subheader('Pool Backtest Settings')

        # Get from the preferences
        path_gen_methods = ['Multivariate Normal', 'Multivariate Student\'s T']
        if get_pref(POOL_BACK_PG) in path_gen_methods:
            selected_index = path_gen_methods.index(get_pref(POOL_BACK_PG))
        else:
            selected_index = 1

        gen_method = ma_backtest_form.selectbox('Select path generation method', path_gen_methods,
                                                index=selected_index)

        help_panel = ma_backtest_form.expander('Need Help? Click to Expand', expanded=False)
        help_panel.markdown(PB_PATH_GEN_HELP_TEXT)

        # Convert to enum
        if gen_method == 'Multivariate Normal':
            gen_method = PathGenMethod.MV_NORMAL
        elif gen_method == 'Multivariate Student\'s T':
            gen_method = PathGenMethod.MV_STUDENT_T
        else:
            ma_backtest_form.write('Unknown Selection: {}'.format(gen_method))

        num_paths_slider = ma_backtest_form.number_input(
            'Number of Paths', min_value=1, max_value=20000, value=get_pref(POOL_BACK_NP), step=5)

        help_panel = ma_backtest_form.expander('Need Help? Click to Expand', expanded=False)
        help_panel.markdown(PB_NUM_PATHS_HELP_TEXT)

        path_length_slider = ma_backtest_form.number_input(
            'Path Length', min_value=1, max_value=3650, value=get_pref(POOL_BACK_PL), step=1)

        help_panel = ma_backtest_form.expander('Need Help? Click to Expand', expanded=False)
        help_panel.markdown(PB_PATH_LENGTH_HELP_TEXT)

        initial_bankroll = ma_backtest_form.number_input(
            'Initial Bankroll:', min_value=1.0, max_value=1000000.0,
            value=float(get_pref(POOL_BACK_IB)), step=0.01, format='%.2f')

        help_panel = ma_backtest_form.expander('Need Help? Click to Expand', expanded=False)
        help_panel.markdown(PB_INIT_BANKROLL_HELP_TEXT)

        backtest_util_list = []
        _cov_matrix_list = []
        tail_alpha_list = []

        backtest_ids = ma_curve_df.Backtest_ID.unique()

        cov_checks = []
        cov_files = []
        for b_id in backtest_ids:
            query_res = ma_curve_df.query('Backtest_ID == {}'.format(b_id))

            backtest_panel_i = ma_backtest_form.expander(
                'Backtest {} Configuration'.format(b_id), expanded=True)

            left_col, right_col = backtest_panel_i.columns(2)

            cov_input_file_i = right_col.text_input(
                'Specify custom covariance matrix input file', 'covariance.csv',
                key='Backtest_{}_cov_input'.format(b_id))
            user_alpha = right_col.number_input(
                'Tail Alpha', min_value=1.0, max_value=100.0, value=2.5, step=0.1,
                key='tail_alpha_{}'.format(b_id))
            cov_check_i = right_col.checkbox(
                'Use custom covariance input file', value=False,
                key='Backtest_{}_cov_check'.format(b_id))

            cov_checks.append(cov_check_i)
            cov_files.append(cov_input_file_i)

            util_map = {}
            for i, row in query_res.iterrows():
                util_input = left_col.number_input(
                    'Curve {} Util (Must be between 0.0-1.0)'.format(
                        row.Curve_ID), min_value=0.0, max_value=1.0,
                    value=0.1, step=0.001, format='%.8f',
                    key='Backtest_{}_label_{}_curve_{}_util'.format(
                        b_id, row.Label, row.Curve_ID))
                util_map[row.Curve_ID] = util_input

            backtest_util_list.append(util_map)
            tail_alpha_list.append(user_alpha)

        ma_backtest_form.text('Backtesting Progress:')
        backtest_progress_bar = ma_backtest_form.progress(0.0)

        ma_backtest_form.text('Plot Generation Progress')
        plot_progress_bar = ma_backtest_form.progress(0.0)

        ma_backtest_button = ma_backtest_form.form_submit_button('Run Backtesting')

        # If the button is pressed, run the backtesting, and save the results and
        # plots in the session_state for use later
        if ma_backtest_button:

            if backtest_util_list:

                # Check if we are configured correctly
                for i, util_map in enumerate(backtest_util_list):

                    util_sum = 0.0
                    for key, util in util_map.items():
                        util_sum += util

                    if util_sum > 1.0:
                        ma_backtest_form.error('Error: Util totals for each asset in '
                                               'backtest {} must be less than 1.0'.format(i))
                        return -1

                log_dir = './batch_results/batch_{}/pool_backtesting/'.format(
                    st.session_state.batch_number)
                Path(log_dir).mkdir(parents=True, exist_ok=True)

                backtester_map = run_backtesting_script(
                    log_dir, ma_curve_df, training_df, gen_method, num_paths_slider,
                    path_length_slider, initial_bankroll, backtest_util_list,
                    tail_alpha_list, progress_bar=backtest_progress_bar)

                return_dist_map = {}
                marginal_dist_map = {}
                path_plot_map = {}
                pdf_and_pay_map = {}
                performance_dict_list = []
                performance_plot_list = []

                progress_bar_count = 0
                total_num_plot_tasks = calc_total_num_plot_tasks(backtester_map)
                for backtest_id, backtester in backtester_map.items():

                    (marginal_dist_dict, two_d_fig_map, path_figure_map,
                     progress_bar_count) = plot_multi_asset_paths(
                        backtester, path_length_slider, progress_bar_count)

                    log_file_name = log_dir + 'ma_backtest_pool_{}'.format(backtest_id)
                    (performance_dict, plot_dicts, pdf_payout_figs,
                     progress_bar_count) = create_backtesting_plots(
                        backtest_id, backtester, log_file_name, pdf_df, marginal_dist_dict,
                        num_paths_slider, progress_bar_count, total_num_plot_tasks,
                        plot_progress_bar=plot_progress_bar)

                    return_dist_map[backtest_id] = two_d_fig_map
                    marginal_dist_map[backtest_id] = marginal_dist_dict
                    path_plot_map[backtest_id] = path_figure_map
                    pdf_and_pay_map[backtest_id] = pdf_payout_figs
                    performance_dict_list.append(performance_dict)
                    performance_plot_list.append(plot_dicts)

                plot_progress_bar.progress(1.0)

                performace_df = pd.DataFrame(performance_dict_list)
                performace_df.to_csv(log_dir + 'ma_backtest_performance.csv', index=False)

                st.session_state.multi_asset_return_dists = return_dist_map
                st.session_state.ma_backtester_map = backtester_map
                st.session_state.marginal_dists = marginal_dist_map
                st.session_state.ma_path_plot_map = path_plot_map
                st.session_state.ma_pdf_and_payout_fig_map = pdf_and_pay_map
                st.session_state.ma_performance_df = performace_df
                st.session_state.ma_performance_plot_list = performance_plot_list

                save_pool_backtester_preferences(
                    int(batch_number), str(gen_method), int(num_paths_slider),
                    int(path_length_slider), float(initial_bankroll))

        return batch_number


def load_performance_statistics_panel(backtest_id):
    """
    Displays the expandable panel to the user which contains the table containing
    the backtesting performance statistics to user

    Parameters
    ----------
    backtest_id : int
        Index identifying the backtest

    Returns
    -------
    None
    """
    # The funny transposes and df copying here are to make streamlit properly display the
    # info as a row and not a column
    with st.expander('Show Percentile Statistics', expanded=True):
        st.dataframe(pd.DataFrame(st.session_state.ma_performance_df.iloc[backtest_id, :].T).T)


def load_multi_asset_return_pdf_panel(backtest_id, directory='./batch_results', save_file=True):
    """
    Displays the expandable panel to the user which contains 3-D plots (2-D random variable)
    of asset returns used to generate simulated paths in the backtesting simulation. Also
    displays the set of backtesting price paths to the user

    Parameters
    ----------
    backtest_id : int
        Index identifying the backtest
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results
    save_file : bool
        (Optional. Default: True) Whether to save the plot to a file

    Returns
    -------
    None
    """
    two_d_fig_map = st.session_state.multi_asset_return_dists[backtest_id]

    # Plot the 2-D Return PDFs for each combination in the N-dimensional PDF
    for i, (combo, fig) in enumerate(two_d_fig_map.items()):
        asset_0 = combo[0]
        asset_1 = combo[1]

        with st.expander(
                'Show Multi Asset Return PDF {} vs. {}'.format(asset_0, asset_1), expanded=False):
            st.plotly_chart(fig, width=800, height=800, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(
                    directory, 'ma_return_{}_{}_pdf.svg'.format(asset_0, asset_1), fig)

    # Plot the paths for each asset
    path_figure_map = st.session_state.ma_path_plot_map[backtest_id]
    for i, (asset, path_fig) in enumerate(path_figure_map.items()):
        with st.expander('Show {} Simulated Backtesting Paths'.format(asset), expanded=False):
            st.plotly_chart(path_fig, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(directory, '{}_backtesting_paths.svg'.format(asset),
                                        path_fig)


def load_pdf_payout_and_histogram_panel(backtest_id, curve_df, directory='./batch_results',
                                        save_file=True):
    """
    Displays the expandable panel to the user which contains the graph of the probability
    PDFs and option payout functions which were used in the generation of the curve
    compared to the histogram of price paths from the backtesting scenario

    Parameters
    ----------
    backtest_id : int
        Index identifying the backtest
    curve_df : pandas.DataFrame
        The DataFrame containing the backtesting curves
    directory : str
        (Optional. Default: './batch_results') The directory in which to save plot results
    save_file : bool
        (Optional. Default: True) Whether to save the plot to a file

    Returns
    -------
    None
    """
    for i, row in curve_df.iterrows():

        fig_pdf_pay = st.session_state.ma_pdf_and_payout_fig_map[backtest_id][row.Curve_ID]

        fig_pdf_pay.update_layout(
            title_text='Asset: {} Strike: {} Days to Expiration: {}'.format(
                row.Asset, row.StrikePercent, row.Expiration)
        )

        with st.expander(
                'Show Paths vs. PDF and Option Payout for Curve {}'.format(row.Curve_ID),
                expanded=False):
            st.plotly_chart(fig_pdf_pay, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(
                    directory, 'curve_{}_pdf_payout_and_histogram.svg'.format(row.Curve_ID),
                    fig_pdf_pay)


def load_user_curve_plot_panel(col, fig_user_br, fig_user_cagr, fig_user_utils, fig_user_amts,
                               curve_df, directory='./batch_results', save_file=True):
    """
    Displays the expandable panels to the user which contain the backtesting results
    for the user's ABCD curve. The panels are bankrolls, CAGRs, Util, and Amounts of contracts
    traded in the simulation.

    Parameters
    ----------
    col : streamlit.column
        The column beta container which will contain the four plots
    fig_user_br : plotly.graph_object.Figure
        The user bankroll plot
    fig_user_cagr : plotly.graph_object.Figure
        The user cagr plot
    fig_user_utils : List[plotly.graph_object.Figure]
        The user util plots
    fig_user_amts: List[plotly.graph_object.Figure]
        The amount of contracts traded plots
    curve_df : pandas.DataFrame
        The DataFrame containing the backtesting curves
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
                save_plotly_fig_to_file(directory, 'user_bankroll.svg', fig_user_br)

        with st.expander('Show CAGR Plot for User ABCD Curve', expanded=False):
            st.plotly_chart(fig_user_cagr, use_container_width=True)
            if save_file:
                save_plotly_fig_to_file(directory, 'user_cagr.svg', fig_user_cagr)

        for index, row in curve_df.iterrows():
            fig_user_utils[row.Curve_ID].update_layout(
                title_text='Util Used for Curve {}'.format(row.Curve_ID)
            )
            fig_user_amts[row.Curve_ID]['f'].update_layout(
                title_text='Amount of Potion Contracts Traded for Curve {}'.format(row.Curve_ID)
            )

            curve_dir = directory + 'curve_{}_{}_s{}_e{}/'.format(
                row.Curve_ID, row.Label, row.StrikePercent, row.Expiration)
            Path(curve_dir).mkdir(parents=True, exist_ok=True)

            with st.expander(
                    'Show Curve {} Util Plot for User ABCD Curve'.format(row.Curve_ID),
                    expanded=False):
                st.plotly_chart(fig_user_utils[row.Curve_ID], use_container_width=True)
                if save_file:
                    save_plotly_fig_to_file(
                        curve_dir, 'user_util.svg', fig_user_utils[row.Curve_ID])

            with st.expander(
                    'Show Curve {} Amount Plot for User ABCD Curve'.format(row.Curve_ID),
                    expanded=False):
                st.plotly_chart(fig_user_amts[row.Curve_ID]['f'], use_container_width=True)
                if save_file:
                    save_plotly_fig_to_file(curve_dir, 'user_amounts.svg',
                                            fig_user_amts[row.Curve_ID]['f'])


def load_opt_curve_plot_panel(col, fig_opt_br, fig_opt_cagr, fig_opt_utils, fig_opt_amts,
                              curve_df, directory='./batch_results', save_file=True):
    """
    Displays the four expandable panels to the user which contain the backtesting results
    for the calculated optimum curve. The panels are bankrolls, CAGRs, Util, and Amounts
    of contracts traded in the simulation.

    Parameters
    ----------
    col : streamlit.column
        The column beta container which will contain the four plots
    fig_opt_br : plotly.graph_object.Figure
        The optimal curve bankroll plot
    fig_opt_cagr : plotly.graph_object.Figure
        The optimal curve cagr plot
    fig_opt_utils : List[plotly.graph_object.Figure]
        The optimal curve util plots
    fig_opt_amts : List[plotly.graph_object.Figure]
        The amount of contracts traded plots
    curve_df : pandas.DataFrame
        The DataFrame containing the backtesting curves
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

        for index, row in curve_df.iterrows():
            fig_opt_utils[row.Curve_ID].update_layout(
                title_text='Util Used for Curve {}'.format(row.Curve_ID)
            )
            fig_opt_amts[row.Curve_ID]['f'].update_layout(
                title_text='Amount of Potion Contracts Traded for Curve {}'.format(row.Curve_ID)
            )

            curve_dir = directory + 'curve_{}_{}_s{}_e{}/'.format(
                row.Curve_ID, row.Label, row.StrikePercent, row.Expiration)
            Path(curve_dir).mkdir(parents=True, exist_ok=True)

            with st.expander(
                    'Show Curve {} Util Plot for Minimum Optimal Curve'.format(row.Curve_ID),
                    expanded=False):
                st.plotly_chart(fig_opt_utils[row.Curve_ID], use_container_width=True)
                if save_file:
                    save_plotly_fig_to_file(curve_dir, 'minimum_curve_util.svg',
                                            fig_opt_utils[row.Curve_ID])

            with st.expander(
                    'Show Curve {} Amount Plot for Minimum Optimal Curve'.format(row.Curve_ID),
                    expanded=False):
                st.plotly_chart(fig_opt_amts[row.Curve_ID]['f'], use_container_width=True)
                if save_file:
                    save_plotly_fig_to_file(curve_dir, 'minimum_curve_amounts.svg',
                                            fig_opt_amts[row.Curve_ID]['f'])


def load_multi_asset_results_panel(batch_number):
    """
    Main function to load all of the streamlit panels containing the results plots for the user

    Parameters
    ----------
    batch_number : int
        ID number indicating the batch of simulation results

    Returns
    -------
    None
    """
    if st.session_state.multi_asset_return_dists is not None:

        with st.container():

            st.subheader('Backtester Results')

            for backtest_id, backtester in st.session_state.ma_backtester_map.items():

                if st.session_state.selected_indices is not None:
                    if backtest_id in st.session_state.selected_indices:

                        with st.container():
                            st.subheader('Backtest ID: {}'.format(backtest_id))

                            res_dir = './batch_results/batch_{}/pool_backtesting/plots/'.format(
                                batch_number) + 'backtest_{}/'.format(backtest_id)

                            if st.session_state.write_plots_to_file:
                                Path(res_dir).mkdir(parents=True, exist_ok=True)

                            load_performance_statistics_panel(backtest_id)
                            load_multi_asset_return_pdf_panel(
                                backtest_id, res_dir, st.session_state.write_plots_to_file)
                            load_pdf_payout_and_histogram_panel(
                                backtest_id, backtester.curve_df, res_dir,
                                st.session_state.write_plots_to_file)

                            plot_list = st.session_state.ma_performance_plot_list[backtest_id]

                            user_bankroll_fig = plot_list[0]
                            opt_bankroll_fig = plot_list[1]
                            user_cagr_fig = plot_list[2]
                            opt_cagr_fig = plot_list[3]
                            user_util_figs = plot_list[4]
                            opt_util_figs = plot_list[5]
                            user_amt_figs = plot_list[6]
                            opt_amt_figs = plot_list[7]

                            col1, col2 = st.columns(2)
                            load_user_curve_plot_panel(
                                col1, user_bankroll_fig, user_cagr_fig, user_util_figs,
                                user_amt_figs, backtester.curve_df, res_dir,
                                st.session_state.write_plots_to_file)
                            load_opt_curve_plot_panel(
                                col2, opt_bankroll_fig, opt_cagr_fig, opt_util_figs, opt_amt_figs,
                                backtester.curve_df, res_dir, st.session_state.write_plots_to_file)

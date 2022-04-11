"""
This module provides the frontend helper code for the portfolio creator GUI
"""
import os
from pathlib import Path
import glob
import numpy as np
import pandas as pd
import streamlit as st
from types import SimpleNamespace

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

from potion.streamlitapp.curvegen.cg_file_io import read_curves_from_csv
from potion.streamlitapp.backt.bt_plot import plot_performance_scatter_plot
from potion.streamlitapp.category import (PC_BATCH_NUMBER_HELP_TEXT, PC_NUM_PER_GRPS_HELP_TEXT,
                                          PC_NUM_POOLS_HELP_TEXT)
from potion.streamlitapp.category.categorizer import Categorizer
from potion.streamlitapp.category.cat_plot import plot_curves_in_pool
from potion.streamlitapp.preference_saver import (preference_df_file_name, initialize_preference_df,
                                                  save_pool_creator_preferences, get_pref,
                                                  POOL_CREATE_NG, POOL_CREATE_NP)


def get_batch_numbers(directory='./batch_results'):
    """
    Searches the batch_results directory for existing results from backtesting to
    allow the user to select an existing batch number.

    Parameters
    ----------
    directory : str
        (Optional. Default: './batch_results') The directory containing backtesting results

    Returns
    -------
    batch_numbers : List[int]
        The List of batch numbers from existing backtesting results
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


def _check_curve_rows_eq(perf_row, curve_row):
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


def initialize_categorization_session_state():
    """
    Initializes the session_state streamlit object so that we can have dynamic UI
    components in streamlit

    Returns
    --------
    None
    """
    if 'historical_scores' not in st.session_state:
        st.session_state.historical_scores = None

    if 'rating_mapping' not in st.session_state:
        st.session_state.rating_mapping = None

    if 'category_map' not in st.session_state:
        st.session_state.category_map = None

    if 'multi_asset_input_map' not in st.session_state:
        st.session_state.multi_asset_input_map = None

    if 'manual_pool_ids' not in st.session_state:
        st.session_state.manual_pool_ids = None

    if 'batch_number' not in st.session_state:
        st.session_state.batch_number = None

    if 'pref_df' not in st.session_state:
        st.session_state.pref_df = None

    if 'preview_df' not in st.session_state:
        st.session_state.preview_df = None

    if os.path.isfile(preference_df_file_name):
        st.session_state.pref_df = pd.read_csv(preference_df_file_name, sep=',')
    else:
        st.session_state.pref_df = initialize_preference_df()


def load_categorization_settings_panel():
    """
    Displays the pool categorization settings panel to the user. When the user clicks
    the start button this function also kicks off the business logic of actually running
    the backtesting simulation and stores the results in the session_state for use in
    other areas of the streamlit app.

    Returns
    --------
    num_clusters : int
        The number of curve groups the user picked
    batch_number : int
        The batch id number the user picked
    curves_df : pandas.DataFrame
        The DataFrame containing the curve info
    """
    batch_input_form = st.form(key='batch-input-form')

    batch_input_form.subheader('Pool Creation Settings')

    link = '[Open User Guide](http://localhost:8080/' + \
           'potion/user_guides/pool_creator_user_guide.html)'
    batch_input_form.markdown(link, unsafe_allow_html=True)

    batch_numbers = get_batch_numbers()

    help_panel = batch_input_form.expander('Need Help? Click to Expand', expanded=False)
    help_panel.markdown(PC_BATCH_NUMBER_HELP_TEXT)

    if not batch_numbers:
        batch_input_form.markdown(
            'No Backtesting results detected in results directory (./batch_results). ' +
            'Please Run the Backtester to get started.  \n' +
            '[Open Curve Generator](http://localhost:8503/)')

        batch_input_form.form_submit_button('Submit')

        return 0, -1, pd.DataFrame()
    else:

        batch_number = batch_input_form.selectbox(
            'Select the results batch number to choose ' +
            'generated curves (directory ./batch_results)',
            batch_numbers, index=0)

        batch_number_button = batch_input_form.form_submit_button('Submit')

        if batch_number_button:
            st.session_state.batch_number = batch_number

        if st.session_state.batch_number is None:
            return 0, -1, pd.DataFrame()

        res_file = 'batch_results/batch_{}/backtesting/backtest_performance.csv'.format(
            st.session_state.batch_number)
        curves_file = 'batch_results/batch_{}/curve_generation/curves.csv'.format(
            st.session_state.batch_number)

        if not os.path.isfile(curves_file):
            st.error('Missing curve generation results.')
            st.markdown(
                'Selected batch_{} folder exists, but does not contain '.format(
                    st.session_state.batch_number) +
                'curve generation results. (./batch_results/batch_{}). '.format(
                    st.session_state.batch_number) +
                'Please Run the Curve Generator to get started, or ' +
                'select another results folder.  \n' +
                '[Open Curve Generator](http://localhost:8502/)')
            return 0, -1, pd.DataFrame()

        if not os.path.isfile(res_file):
            st.error('Missing backtesting results.')
            st.markdown(
                'Selected batch_{} folder exists, but does not contain '.format(
                    st.session_state.batch_number) +
                'backtesting results. (./batch_results/batch_{}). '.format(
                    st.session_state.batch_number) +
                'Please Run the Curve Backtester to get started, or ' +
                'select another results folder.  \n' +
                '[Open Curve Backtester](http://localhost:8503/)')
            return 0, -1, pd.DataFrame()

        performance_df = pd.read_csv(res_file, sep=',')
        curves_df = read_curves_from_csv(curves_file)

        with st.container():

            performance_plot = plot_performance_scatter_plot(performance_df)
            st.plotly_chart(performance_plot, use_container_width=True)
            # selected_points_json = plotly_events(performance_plot, click_event=False,
            #                                      select_event=True, hover_event=False)

            gb = GridOptionsBuilder.from_dataframe(performance_df)
            gb.configure_pagination()
            gb.configure_selection(selection_mode='multiple', use_checkbox=True)
            grid_options = gb.build()

            st.text('Loaded Curve Batch. Select Rows to Add to Portfolio:')
            selected_rows = AgGrid(performance_df, gridOptions=grid_options,
                                   update_mode=GridUpdateMode.SELECTION_CHANGED)

            selected_curve_ids = []
            if selected_rows is not None:

                selected_rows = selected_rows['selected_rows']
                selected_rows = pd.DataFrame(selected_rows)

                # No ability to get the row numbers from the AgGrid component unfortunately
                for idx, row in selected_rows.iterrows():
                    row['strike'] = float(row['strike'])
                    row_pd = pd.Series(row)

                    for c_index, c_row in curves_df.iterrows():

                        row_pd.name = c_row.name
                        if _check_curve_rows_eq(row_pd, c_row):
                            selected_curve_ids.append(c_index)
                            break

                st.text('Current Selection for Portfolio:')
                st.dataframe(selected_rows)

            manual_categorization_form = st.form(key='manual-category-form')

            with manual_categorization_form:

                st.subheader('Manual Pool Creation')
                st.text('Manually create a pool by selecting rows from the table above. '
                        'After rows have been selected, click the Create Pools button')
                manual_button = manual_categorization_form.form_submit_button('Create Pools')

                if manual_button:

                    # Set the automatic ones to none to clear any
                    # cached results from previous runs
                    st.session_state.historical_scores = None
                    st.session_state.rating_mapping = None
                    st.session_state.category_map = None

                    st.session_state.manual_pool_ids = selected_curve_ids
                    st.session_state.multi_asset_input_map = []

            automatic_categorization_form = st.form(key='automatic-category-form')

            with automatic_categorization_form:

                st.subheader('Automatic Pool Creation')
                st.text(
                    'Automatically create pools by selecting the two parameters: '
                    'Number of Groups and Number of Clusters. May also use both parameters.')

                num_groups = automatic_categorization_form.number_input(
                    'Number of Performance Groups:', min_value=1, max_value=10,
                    value=get_pref(POOL_CREATE_NG), step=1)

                help_panel = automatic_categorization_form.expander(
                    'Need Help? Click to Expand', expanded=False)
                help_panel.markdown(PC_NUM_PER_GRPS_HELP_TEXT)

                num_clusters = automatic_categorization_form.number_input(
                    'Number of Clusters:', min_value=1, max_value=10,
                    value=get_pref(POOL_CREATE_NP), step=1)

                help_panel = automatic_categorization_form.expander(
                    'Need Help? Click to Expand', expanded=False)
                help_panel.markdown(PC_NUM_POOLS_HELP_TEXT)

                auto_button = automatic_categorization_form.form_submit_button('Create Pools')

                if auto_button:

                    if num_groups * num_clusters > len(curves_df):
                        st.error(
                            'Total number of pools selected (number of pools * '
                            'number of performance groups) is '
                            'larger than the number of curves. Please select a valid number')
                        return 0, -1, pd.DataFrame()

                    st.session_state.multi_asset_input_map = []

                    if len(curves_df) == 1:
                        # If the user only put in one curve,
                        # mock the output from the category class because we only have
                        # one curve and don't need to run the algrithm
                        obj = SimpleNamespace()
                        setattr(obj, 'clustering', [0])
                        st.session_state.category_map = {'key': {
                            'ids': [0],
                            'cluster': obj
                        }}
                        save_pool_creator_preferences(
                            st.session_state.batch_number, num_groups, num_clusters)
                        return num_clusters, st.session_state.batch_number, curves_df
                    else:
                        # Run the pool clustering algorithm to automatically
                        # generate some pools for the user
                        categorizer = Categorizer(
                            performance_df=performance_df, curves_df=curves_df)

                        (performance_group_mapping,
                         user_historical_scores) = categorizer.create_historical_score_mapping(
                            num_groups)

                        category_map = categorizer.cluster_based_on_category(
                            num_groups, num_clusters, performance_group_mapping)

                        # Save the results in the session state for plotting later
                        st.session_state.historical_scores = user_historical_scores
                        st.session_state.rating_mapping = performance_group_mapping
                        st.session_state.category_map = category_map
                        st.session_state.manual_pool_ids = None

        save_pool_creator_preferences(st.session_state.batch_number, num_groups, num_clusters)
        return num_clusters, st.session_state.batch_number, curves_df


def load_pool_panels(num_pools, curves_df, clusters, pool_curve_ids, form_label_str):
    """
    Loads the panels which display the pool curves and allow the user to
    select which curve to use for which pool.

    Parameters
    ----------
    num_pools : int
        The number of pools to split curves into
    curves_df : pandas.DataFrame
        The DF of curves being tested
    clusters : List[int]
        The clusters of curves which will be split into pools
    pool_curve_ids : List[int]
        The ID numbers indicating which curve is in the pool
    form_label_str : str
        The unique string to use as a key for the form

    Returns
    --------
    None
    """
    for pool in range(num_pools):

        with st.form(form_label_str + '_{}'.format(pool)):

            st.text('Pool {}'.format(pool))

            curve_indices_in_pool = np.where(np.asarray(clusters) == pool)[0]

            # Create a list of the bet fraction arrays for plotting and
            # info for a dataframe of the pool info
            bf_list = [curves_df.bet_fractions[pool_curve_ids[curve_index]]
                       for curve_index in curve_indices_in_pool]
            pool_rows = [{
                'ID': pool_curve_ids[curve_index],
                'Ticker': curves_df.Ticker[pool_curve_ids[curve_index]],
                'Label': curves_df.Label[pool_curve_ids[curve_index]],
                'Expiration': curves_df.Expiration[pool_curve_ids[curve_index]],
                'StrikePct': curves_df.StrikePercent[pool_curve_ids[curve_index]],
                'A': curves_df.A[pool_curve_ids[curve_index]],
                'B': curves_df.B[pool_curve_ids[curve_index]],
                'C': curves_df.C[pool_curve_ids[curve_index]],
                'D': curves_df.D[pool_curve_ids[curve_index]]
            } for curve_index in curve_indices_in_pool]

            left_col, right_col = st.columns(2)

            pool_df = pd.DataFrame(pool_rows)
            left_col.dataframe(pool_df)

            overestimate = left_col.checkbox('Use Single Curve for Entire Pool', value=True)
            selected_index = left_col.selectbox('Select Curve:', pool_df.ID)

            right_col.plotly_chart(plot_curves_in_pool(pool_df, bf_list), use_container_width=True)

            add_pool = st.form_submit_button('Add Pool to Input Dataframe')

            if add_pool:

                try:
                    tmp_df = pd.DataFrame(st.session_state.multi_asset_input_map)
                    bid_col = tmp_df['Backtest_ID']
                    backtest_id = bid_col.max() + 1
                except KeyError:
                    backtest_id = 0

                rows = [
                    {
                        'Label': pool_row.Ticker + '-' + pool_row.Label,
                        'Backtest_ID': backtest_id,
                        'Curve_ID': pool_row.ID,
                        'Asset': pool_row.Ticker,
                        'Expiration': pool_row.Expiration,
                        'StrikePercent': pool_row.StrikePct,
                        'A': curves_df.A[selected_index if overestimate else pool_row.ID],
                        'B': curves_df.B[selected_index if overestimate else pool_row.ID],
                        'C': curves_df.C[selected_index if overestimate else pool_row.ID],
                        'D': curves_df.D[selected_index if overestimate else pool_row.ID],
                        't_params': curves_df.t_params[
                            selected_index if overestimate else pool_row.ID],
                        'bet_fractions': curves_df.bet_fractions[
                            selected_index if overestimate else pool_row.ID],
                        'curve_points': curves_df.curve_points[
                            selected_index if overestimate else pool_row.ID]
                    } for i, pool_row in pool_df.iterrows()]

                st.session_state.multi_asset_input_map.extend(rows)


def load_categorization_results_panel(num_pools, curves_df):
    """
    This function displays the streamlit panels containing the results of the pool
    selection process to the user

    Parameters
    ----------
    num_pools : int
        The number of pools
    curves_df : pandas.DataFrame
        The DF of curves being tested

    Returns
    --------
    None
    """
    if st.session_state.category_map is not None:
        # Auto button pressed

        with st.container():

            for category_num, (key, category) in enumerate(st.session_state.category_map.items()):
                with st.expander('Performance Group {}'.format(category_num), expanded=False):

                    pool_curve_ids = category['ids']
                    clusters = category['cluster'].clustering

                    load_pool_panels(num_pools, curves_df, clusters, pool_curve_ids,
                                     'performance_group_{}'.format(category_num))
    else:

        if st.session_state.manual_pool_ids is not None:
            # Manual button pressed

            with st.expander('Manually Created Pool', expanded=True):
                load_pool_panels(1, curves_df, np.zeros(len(st.session_state.manual_pool_ids)),
                                 st.session_state.manual_pool_ids, 'manual_pool')

    if st.session_state.multi_asset_input_map is not None and \
            st.session_state.multi_asset_input_map:
        with st.container():
            st.subheader('Pool Backtester Input Dataframe')

            ma_df = pd.DataFrame(st.session_state.multi_asset_input_map)

            res_dir = './batch_results/batch_{}/pool_creation/'.format(
                st.session_state.batch_number)
            Path(res_dir).mkdir(parents=True, exist_ok=True)

            ma_df.to_csv(res_dir + 'multi_asset_input.csv', index=False)

            st.dataframe(ma_df)

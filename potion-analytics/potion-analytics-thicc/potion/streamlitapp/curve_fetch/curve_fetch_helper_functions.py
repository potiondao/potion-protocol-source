"""
This module provides the backend code for the curve fetching tool and implements the calls from
the GUI
"""
import os

import pandas as pd
import streamlit as st

import plotly.graph_objects as go

import json
from pycoingecko import CoinGeckoAPI

from potion.streamlitapp.curvegen.cg_frontend_helper_functions import get_price_files
from potion.streamlitapp.curve_fetch.gql_query import (create_gql_client, get_all_potions_query,
                                                       parse_query_results_to_df)

from potion.streamlitapp.preference_saver import (preference_df_file_name, initialize_preference_df)


def _plot_training_data(asset: str, x_values, y_values, x_label, y_label):
    """
    Plots the price history of an asset on a plotly figure for display to the user as part of the
    training data selection process

    Parameters
    ----------
    asset : str
        The name of the asset whose training data is being plotted
    x_values : List
        The x values of the training data (Dates)
    y_values : List[float]
        The y values of the training data (Prices)
    x_label : str
        The string label to display on the X axis of the plot
    y_label
        The string label to display on the Y axis of the plot

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The plotly figure to display on the streamlit UI
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_values, y=y_values,
                             mode='lines',
                             name='{} Full History'.format(asset)))

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)', xaxis_title=x_label,
        yaxis_title=y_label).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    return fig


def initialize_curve_fetch_session_state():
    """
    Initializes the session_state streamlit object so that we can have dynamic UI components
    in streamlit

    Returns
    -----------
    None
    """
    if 'pref_df' not in st.session_state:
        st.session_state.pref_df = None

    if 'cg' not in st.session_state:
        st.session_state.cg = None

    if 'coins' not in st.session_state:
        st.session_state.coins = None

    if 'gql' not in st.session_state:
        st.session_state.gql = None

    if 'potion_df' not in st.session_state:
        st.session_state.potion_df = None

    if 'input_rows' not in st.session_state:
        st.session_state.input_rows = []

    if 'man_input_rows' not in st.session_state:
        st.session_state.man_input_rows = []

    if 'hist_df' not in st.session_state:
        st.session_state.hist_df = None

    if 'hist_file' not in st.session_state:
        st.session_state.hist_file = None

    if 'training_figs' not in st.session_state:
        st.session_state.training_figs = {}

    if 'output_rows' not in st.session_state:
        st.session_state.output_rows = []

    if os.path.isfile(preference_df_file_name):
        st.session_state.pref_df = pd.read_csv(preference_df_file_name, sep=',')
    else:
        st.session_state.pref_df = initialize_preference_df()

    with open('./urls.json') as f:
        url_dict = json.load(f)
        st.session_state.subgraph_url = url_dict['subgraph']


def load_curve_fetch_settings_panel():
    """
    Displays the price fetch settings panel to the user. When the user clicks the start button
    this function also kicks off the business logic of the widget and stores the results in
    the session_state for use in other areas of the streamlit app.

    Returns
    -----------
    None
    """
    if st.session_state.cg is None:
        st.session_state.cg = CoinGeckoAPI()
        st.session_state.coins = st.session_state.cg.get_coins_list()
    coin_symbol_list = [c['symbol'] for c in st.session_state.coins]
    coin_id_list = [c['id'] for c in st.session_state.coins]



    historical_file_form = st.expander(label='', expanded=True)

    historical_file_form.subheader('Historical File Selection')

    link = '[Open User Guide](http://localhost:8080/potion/user_guides/' \
           'subgraph_downloader_user_guide.html)'
    historical_file_form.markdown(link, unsafe_allow_html=True)

    price_file_list, price_input_index = get_price_files()
    historical_file = historical_file_form.selectbox(
        'Select the Historical Prices File (directory ./resources/*.csv)',
        price_file_list, index=price_input_index)

    potion_download_form = st.form(key='potion_download_form')

    potion_download_form.subheader('Subgraph Downloader')

    gql_button = potion_download_form.form_submit_button('Click to Query the Subgraph')

    if gql_button:

        if st.session_state.subgraph_url == '':
            st.error('Please update the subgraph URL in the urls.json '
                     'file and restart in order to use this feature.')
        else:
            if st.session_state.gql is None:
                st.session_state.gql = create_gql_client(gql_url=st.session_state.subgraph_url)

            potion_list = get_all_potions_query(st.session_state.gql, 1000)

            potion_df = parse_query_results_to_df(potion_list)

            st.session_state.potion_df = potion_df
            st.session_state.input_rows = []

    if st.session_state.potion_df is not None:

        select_row_form = st.form(key='select_row_form')

        select_row_form.dataframe(st.session_state.potion_df)

        selected_row = select_row_form.selectbox('Select Row to Add to Input File',
                                                 st.session_state.potion_df.index,
                                                 index=0)

        # Space the form buttons together
        (col1, col2, _, _, _, _, _, _, _, _) = select_row_form.columns(10)
        add_row_button = col1.form_submit_button('Add Row to Input')
        clear_rows_button = col2.form_submit_button('Clear Rows')

        if add_row_button:
            st.session_state.input_rows.append(selected_row)

            hist_df = pd.read_csv('resources/' + historical_file, sep=',')
            hist_df['Master calendar'] = pd.to_datetime(hist_df['Master calendar'],
                                                        format='%d/%m/%Y').dt.date
            st.session_state.hist_df = hist_df

        if clear_rows_button:
            st.session_state.input_rows = []
            st.session_state.man_input_rows = []
            st.session_state.output_rows = []
            st.session_state.training_figs = {}

    manual_input_form = st.form(key='manual_input_form')

    manual_input_form.subheader('Add CoinGecko Asset')

    manual_input_form.text('Note: \'CoinGecko\' is a registered trademark of Gecko Labs PTE LTD')

    col1, col2, col3 = manual_input_form.columns(3)

    selected_coin = col1.selectbox('Select Asset', coin_symbol_list,
                                   index=coin_symbol_list.index('btc'))

    strike = col2.number_input('Strike Price', min_value=0.0,
                               value=100.0, format='%.2f')

    expiration = col3.number_input('Expiration (Days)', min_value=1, value=30)

    # Space the form buttons together
    (cola, colb, _, _, _, _, _, _, _, _) = manual_input_form.columns(10)
    manual_add_row = cola.form_submit_button('Add Row to Input')
    clear_rows_button = colb.form_submit_button('Clear Rows')

    if manual_add_row:
        coin_id = coin_id_list[coin_symbol_list.index(str(selected_coin))]

        st.session_state.man_input_rows.append({
            'Asset': coin_id,
            'Strike': strike,
            'Expiration': expiration
        })

        hist_df = pd.read_csv('resources/' + historical_file, sep=',')
        hist_df['Master calendar'] = pd.to_datetime(hist_df['Master calendar'],
                                                    format='%d/%m/%Y').dt.date
        st.session_state.hist_df = hist_df
        st.session_state.hist_file = historical_file

    if clear_rows_button:
        st.session_state.input_rows = []
        st.session_state.man_input_rows = []
        st.session_state.output_rows = []
        st.session_state.training_figs = {}


def load_curve_fetch_results_panel():
    """
    This function displays the streamlit panels containing the results of the backtesting
    process to the user

    Returns
    -----------
    None
    """
    if len(st.session_state.input_rows) > 0 or len(st.session_state.man_input_rows) > 0:

        if st.session_state.potion_df is not None:
            input_df = st.session_state.potion_df.iloc[st.session_state.input_rows]
            input_df = input_df.append(st.session_state.man_input_rows)
            input_df.reset_index(drop=True, inplace=True)
        else:
            input_df = pd.DataFrame(st.session_state.man_input_rows,
                                    columns=['Asset', 'Strike', 'Expiration'])

        # st.dataframe(input_df)

        # Loop over each curve generated and display the panels to the user
        for i, input_row in input_df.iterrows():
            with st.expander('Potion {}: {}, Strike {}, Expiration {}'.format(i, input_row.Asset,
                                                                              input_row.Strike,
                                                                              input_row.Expiration),
                             expanded=True):
                # st.subheader()

                try:
                    full_history_index = st.session_state.hist_df['Master calendar'].values
                    full_price_history = st.session_state.hist_df[input_row.Asset].values
                except KeyError:
                    st.error('Asset must exist in Historical Price Data CSV: {}, Asset: {}'.format(
                        st.session_state.hist_file, input_row.Asset))
                    continue

                col1, col2 = st.columns(2)

                if st.session_state.training_figs.get(i) is None:
                    st.session_state.training_figs[i] = _plot_training_data(input_row.Asset,
                                                                            full_history_index,
                                                                            full_price_history,
                                                                            'Dates',
                                                                            'Price')

                # Display the curve plot in the left column
                with col1.container():
                    col1.plotly_chart(st.session_state.training_figs[i], use_container_width=True)

                # Display the controls panels in the right column
                with col2.container():
                    training_start = col2.selectbox('Select a Start Date for the Training Data',
                                                    full_history_index,
                                                    index=0, key='training_start_{}'.format(i))
                    training_end = col2.selectbox('Select an End Date for the Training Data',
                                                  full_history_index,
                                                  index=len(full_history_index) - 1,
                                                  key='training_end_{}'.format(i))

                    training_label = col2.text_input('Specify a Custom Label for the Training Data',
                                                     value='Potion_{}'.format(i),
                                                     key='training_label_{}'.format(i))

                    use_custom = col2.checkbox(
                        'Use Custom Current Price (only affects where ' +
                        'price paths start in backtester)', value=False,
                        key='training_ccp_check_{}'.format(i))

                    custom_price = col2.number_input('Custom Current Price', min_value=0.0,
                                                     value=full_price_history[-1], format='%.2f',
                                                     key='training_ccp_{}'.format(i))

                    choose_window_button = col2.button('Select Training Window',
                                                       key='training_button_{}'.format(i))

                    if choose_window_button:

                        start_cond = (st.session_state.hist_df['Master calendar'] >= training_start)
                        end_cond = (st.session_state.hist_df['Master calendar'] <= training_end)

                        training_df = st.session_state.hist_df.loc[start_cond & end_cond]

                        training_history_index = training_df['Master calendar'].values
                        training_price_history = training_df[input_row.Asset].values

                        st.session_state.training_figs[i].add_trace(
                            go.Scatter(x=training_history_index, y=training_price_history,
                                       mode='lines',
                                       name='{}'.format(training_label)))

                        if use_custom:
                            current_price = custom_price
                        else:
                            current_price = full_price_history[-1]

                        st.session_state.output_rows.append({
                            'Asset': input_row.Asset,
                            'TrainingLabel': training_label,
                            'TrainingStart': training_start.strftime('%d/%m/%Y'),
                            'TrainingEnd': training_end.strftime('%d/%m/%Y'),
                            'StrikePct': input_row.Strike / current_price,
                            'Expiration': int(input_row.Expiration),
                            'CurrentPrice': current_price
                        })

                        st.experimental_rerun()

    if len(st.session_state.output_rows) > 0:
        output_df = pd.DataFrame(st.session_state.output_rows,
                                 columns=['Asset', 'TrainingLabel', 'TrainingStart', 'TrainingEnd',
                                          'StrikePct', 'Expiration', 'CurrentPrice'])

        with st.expander('Output CSV', expanded=True):

            output_form = st.form('Output CSV')
            output_form.dataframe(output_df)

            csv_filename = output_form.text_input('Save As CSV File: ', '')

            # Space the form buttons together
            (col1, col2, _, _, _, _, _, _, _, _) = output_form.columns(10)
            write_output = col1.form_submit_button('Write Output CSV')
            clear_rows_button = col2.form_submit_button('Clear Rows')

            if write_output:
                st.write('Saving File... inputs/{}'.format(csv_filename))

                output_df.to_csv('inputs/{}'.format(csv_filename),
                                 index=False)

            if clear_rows_button:
                st.session_state.output_rows = []
                st.session_state.training_figs = {}

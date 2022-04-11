"""
This module provides the backend code for the historical data downloading tool
"""
import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

import json
from pycoingecko import CoinGeckoAPI

from potion.streamlitapp.preference_saver import (preference_df_file_name, initialize_preference_df)


def initialize_price_fetch_session_state():
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

    if 'history_dict' not in st.session_state:
        st.session_state.history_dict = {}

    if 'merged_df' not in st.session_state:
        st.session_state.merged_df = None

    if os.path.isfile(preference_df_file_name):
        st.session_state.pref_df = pd.read_csv(preference_df_file_name, sep=',')
    else:
        st.session_state.pref_df = initialize_preference_df()

    with open('./urls.json') as f:
        url_dict = json.load(f)
        st.session_state.coingecko_url = url_dict['coingecko']


def load_price_fetch_settings_panel():
    """
    Displays the price fetch settings panel to the user. When the user clicks the start button
    this function also kicks off the business logic of the widget and stores the results in
    the session_state for use in other areas of the streamlit app.

    Returns
    -----------
    csv_filename : str
        The user provided input CSV filename
    """

    if st.session_state.cg is None:
        st.session_state.cg = CoinGeckoAPI(api_base_url=st.session_state.coingecko_url)
        st.session_state.coins = st.session_state.cg.get_coins_list()
    coin_symbol_list = [c['symbol'] for c in st.session_state.coins]
    coin_id_list = [c['id'] for c in st.session_state.coins]
    coin_full = ['Symbol: ' + symbol + ' Name: ' + coin_id for symbol, coin_id in zip(
        coin_symbol_list, coin_id_list)]

    price_data_download_form = st.form(key='price_data_download_form')

    price_data_download_form.subheader('Price Data Download')

    price_data_download_form.text(
        'Note: \'CoinGecko\' is a registered trademark of Gecko Labs PTE LTD')

    link = '[Open User Guide](http://localhost:8080/potion/user_guides/' \
           'historical_data_downloader_user_guide.html)'
    price_data_download_form.markdown(link, unsafe_allow_html=True)

    selected_coin = price_data_download_form.selectbox(
        'Select Ticker to Download. Begin typing to search ' +
        'CoinGecko for the asset of your choosing.', coin_full, index=coin_symbol_list.index('btc'))

    add_ticker_button = price_data_download_form.form_submit_button('Add Ticker to Download')

    if add_ticker_button:

        coin_id = str(selected_coin).split(' Name: ')[1]

        history = st.session_state.cg.get_coin_market_chart_by_id(
            id=coin_id, vs_currency='usd', days='max')

        history_dates, history_prices = list(map(list,
                                                 zip(*[[datetime.fromtimestamp(
                                                     float(entry[0] / 1000.0),
                                                     tz=timezone.utc), entry[1]]
                                                     for entry in history['prices']])))

        # For all dates, some will not be price sampled at midnight UTC. Convert datetimes into
        # datetimes at midnight so that they can be merged by pandas.merge
        history_dates = [datetime.combine(h_date.date(), datetime.min.time(),
                                          tzinfo=timezone.utc)
                         for h_date in history_dates]

        st.session_state.history_dict[coin_id] = pd.DataFrame(
            history_prices, index=history_dates, columns=[coin_id])

    if len(st.session_state.history_dict.items()) > 0:

        price_data_merge_form = st.form(key='price_data_merge_form')

        table_rows = [{
            'Symbol': key,
            'StartDate': value.index[0],
            'EndDate': value.index[-1]
        } for key, value in st.session_state.history_dict.items()]

        price_data_merge_form.dataframe(pd.DataFrame(table_rows))

        csv_filename = price_data_merge_form.text_input(
            'Save As CSV File: (output directory ./resources/*.csv)', 'webapp-coins.csv')

        (col1, col2, _, _, _, _, _, _, _, _) = price_data_merge_form.columns(10)
        merge_button = col1.form_submit_button('Merge Into CSV')
        clear_button = col2.form_submit_button('Clear Ticker Table')

        if merge_button:

            merged_df = None
            cols = ['Date']
            for key, value in st.session_state.history_dict.items():

                cols.append(key)
                if merged_df is None:
                    merged_df = value.copy()
                else:
                    merged_df = pd.merge_ordered(merged_df, value, left_on=merged_df.index,
                                                 right_on=value.index)
                    merged_df.columns = cols
                    merged_df.set_index('Date', drop=True, inplace=True)

            index_as_strs = [day.strftime('%d/%m/%Y') for day in merged_df.index]
            merged_df.index = index_as_strs

            merged_df.to_csv('resources/{}'.format(csv_filename),
                             index=True, index_label='Master calendar')

            st.session_state.merged_df = merged_df

        if clear_button:
            st.session_state.history_dict = {}
            st.session_state.merged_df = None

        return csv_filename
    else:
        return ''


def load_price_fetch_results_panel(csv_filename):
    """
    This function displays the streamlit panels containing the results of the backtesting
    process to the user

    Parameters
    -----------
    csv_filename : str
        The filename to save the historical data

    Returns
    -----------
    None
    """
    if st.session_state.merged_df is not None:
        st.write('Saving File... resources/{}'.format(csv_filename))

        with st.expander('Output CSV', expanded=True):
            st.session_state.merged_df.fillna(0.0, inplace=True)
            st.dataframe(st.session_state.merged_df)

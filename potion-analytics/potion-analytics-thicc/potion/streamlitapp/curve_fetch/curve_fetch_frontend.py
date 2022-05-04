"""
This file creates a Streamlit GUI to help the user create curves for the application
without having to create any CSV files by hand
"""
from PIL import Image
import streamlit as st
import subprocess
import os
import sys

import argparse

# Add the root to the path so we can import our potion files
module_path = os.path.abspath(os.path.join('.'))

if module_path not in sys.path:
    sys.path.append(module_path)
# print('Current Module Path: {}'.format(module_path))

from potion.streamlitapp.curve_fetch.curve_fetch_helper_functions import (
    initialize_curve_fetch_session_state, load_curve_fetch_settings_panel,
    load_curve_fetch_results_panel)

# Set the page configuration
im = Image.open("resources/potion_logo.jpg")
st.set_page_config(
    page_title='Potion Analytics: THICC',
    layout="wide",
    page_icon=im,
    initial_sidebar_state="collapsed",
)


def initialize_session_state():
    """
    Initializes the streamlit session state object to use dynamic UI elements

    Returns
    -------
    None
    """
    if 'docs_engine' not in st.session_state:
        st.session_state.docs_engine = None

    if 'files_engine' not in st.session_state:
        st.session_state.files_engine = None


def start_pdocs(multi=False):
    """
    When started in single tab mode, the documentation and file servers
    need to be started so that the user guides work.

    Parameters
    ----------
    multi : bool
        Flag indicating if running in multi tab mode

    Returns
    -------
    None
    """
    if not multi:

        st.session_state.files_engine = subprocess.Popen(['python', '-m', 'http.server'])
        st.session_state.docs_engine = subprocess.Popen([
            'pdoc', '--html', 'potion', '--force', '--http', ':'])


def load_sidebar():
    """
    This function is where any sidebar UI elements go

    Returns
    --------
    None
    """
    st.sidebar.text("")


def do_main():
    """
    Main application function

    Returns
    --------
    None
    """
    load_sidebar()
    body()


def body():
    """
    This function loads the UI elements of the web app page body

    Returns
    --------
    None
    """
    initialize_curve_fetch_session_state()

    st.title('Subgraph Downloader and Input CSV Creator')
    st.image(im)
    with st.container():
        # Get the inputs from the user
        load_curve_fetch_settings_panel()

        # Display the results after the user pressed the start button
        load_curve_fetch_results_panel()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='curve_fetch_frontend', usage='%(prog)s [options]')
    parser.add_argument('--multi', action='store_true',
                        help='Launches the Subgraph Downloader tab in multi '
                             'page mode (does not start docs server)')

    args = parser.parse_args()

    start_pdocs(args.multi)

    do_main()

"""
This module provides the main GUI for the Streamlit application
"""
from PIL import Image
import streamlit as st
import subprocess

import json
import socket


# Set the page configuration
im = Image.open("resources/potion_logo.jpg")
st.set_page_config(
    page_title='Potion Analytics: THICC',
    layout="wide",
    page_icon=im,
    initial_sidebar_state="collapsed",
)

welcome_text = """
    # Welcome to Potion Analytics: THICC
    
    ![logo](http://localhost:8000/resources/potion_logo.jpg)

    Welcome to Potion Analytics: T.H.I.C.C (Trustworthy Helper for the Implementation and 
    Calculation of Curves). \n
    
    This application is a collection of tools that allow the user to create Kelly 
    curves including curves for assets exhibiting fat (thicc) tailed behavior. 
    The tools create curves for a Put contract (UI-only),  or any possible option 
    payoff (with the library) and tools to backtest that curve in a backtesting simulator. \n
     
    The library is also capable of using any probability 
    distribution, the UI-default is the Student's T distribution (a fat tailed one). In addition, 
    the library calls can be configured to generate Kelly curves free of arbitrage. Please see 
    the usage examples and companion papers. \n
    
    Tools also exist for downloading price history training data 
    from CoinGecko, querying the subgraph for existing Kelly curves 
    and simulating them, as well as creating and backtesting portfolios (pools) of curves. \n
    
    There is also a tool for managing log files output by the tool. \n
    
    User Guides exist with pictures and screenshots for all of the tools, and can be accessed 
    easily from within this tool in the web browser. Links are below. \n
    
    If you are interested in using the libraries directly in your own Python programs, there 
    is also extensive API documentation for the library and Usage Examples all linked below. \n
    
    Note: 'CoinGecko' is a registered trademark of Gecko Labs PTE LTD
    
    Follow the guides in this order:  \n
    | | Tool Link     | User Guide    | Description |
    |-| ------------- | ------------- | ----------- |
    |1| [Open Historical Price Data Downloader](http://localhost:8507/) | [Historical Price Data Downloader Guide](http://localhost:8080/potion/user_guides/historical_data_downloader_user_guide.html) | Downloads price data from CoinGecko which is used as training data input for generating Kelly Curves. |
    |2| [Open Subgraph Curve Downloader](http://localhost:8508/)  | [Subgraph Curve Downloader Guide](http://localhost:8080/potion/user_guides/subgraph_downloader_user_guide.html) | Downloads existing Kelly Curve configurations from the subgraph and lets the user choose training windows for the input data. |
    |3| [Open Curve Generator](http://localhost:8502/)  | [Curve Generator Guide](http://localhost:8080/potion/user_guides/curve_generator_user_guide.html) | Generates Kelly Curves using the downloaded training data and selected training windows. |
    |4| [Open Curve Backtester](http://localhost:8503/)  | [Kelly Curve Backtester Guide](http://localhost:8080/potion/user_guides/backtester_user_guide.html) | Backtest the generated Kelly Curves. |
    |5| [Open Pool Creator](http://localhost:8504/)  | [Pool Creator Guide](http://localhost:8080/potion/user_guides/pool_creator_user_guide.html) | Groups Kelly Curves which have been backtested into a portfolio or pool of curves. |
    |6| [Open Pool Backtester](http://localhost:8505/)  | [Pool Backtester Guide](http://localhost:8080/potion/user_guides/pool_backtester_user_guide.html) | Backtests pools of Kelly Curves. |
    |7| [Open Log Management](http://localhost:8506/)  | [Log Manager Guide](http://localhost:8080/potion/user_guides/log_archive_user_guide.html) | Manages logs and results files from the other tools. |

    ## What Are the Controls Below?
    
    These tools use [Streamlit](https://streamlit.io/) to provide a great and simple UI to the 
    backend library. At the moment, multiple tabs are not natively supported. As a workaround, 
    each separate tool is served as a Streamlit app on a separate port. Similarly, the User Guides 
    are served on a separate port.
    
    Note: 'Streamlit' is a registered trademark of Streamlit Inc.
    
    #### Why Does it Matter to Me?
    
    If you are running these tools on a computer with constrained resources, it may be helpful to 
    only run one tool at a time. Using the controls below, you can start and stop each application 
    at your choosing.
    
    #### Other Features
    
    The tools will save the last values entered in the UI input forms. That way, if the tabs are 
    closed or the tools are stopped the previous input is preserved. These are stored in the file 
    preferences.csv in the root of the project folder.
    
    ## Backend API Documentation
    
    | API Links     |
    | ------------- |
    | [Reference Documentation](http://localhost:8080/potion/) |
    | [Usage Example Walkthrough](http://localhost:8080/potion/examples/walkthrough.html) |
    | [Usage Example Code](http://localhost:8080/potion/examples/) |
"""

curve_gen_off_md = """
        <style>
        
            .curve-gen-status
            {
               background-color: red;
            }
        
        </style>
        <div class="curve-gen-status"></br></div>
        """

curve_gen_on_md = """
        <style>
        
            .curve-gen-status
            {
               background-color: green;
            }
        
        </style>
        <div class="curve-gen-status"></br></div>
        """

backtester_off_md = """
        <style>

            .backtester-status
            {
               background-color: red;
            }

        </style>
        <div class="backtester-status"></br></div>
        """

backtester_on_md = """
        <style>

            .backtester-status
            {
               background-color: green;
            }

        </style>
        <div class="backtester-status"></br></div>
        """

pool_creator_off_md = """
        <style>

            .pool-creator-status
            {
               background-color: red;
            }

        </style>
        <div class="pool-creator-status"></br></div>
        """

pool_creator_on_md = """
        <style>

            .pool-creator-status
            {
               background-color: green;
            }

        </style>
        <div class="pool-creator-status"></br></div>
        """

pool_backtester_off_md = """
        <style>

            .pool-backtester-status
            {
               background-color: red;
            }

        </style>
        <div class="pool-backtester-status"></br></div>
        """

pool_backtester_on_md = """
        <style>

            .pool-backtester-status
            {
               background-color: green;
            }

        </style>
        <div class="pool-backtester-status"></br></div>
        """

log_management_off_md = """
        <style>

            .log-management-status
            {
               background-color: red;
            }

        </style>
        <div class="log-management-status"></br></div>
        """

log_management_on_md = """
        <style>

            .log-management-status
            {
               background-color: green;
            }

        </style>
        <div class="log-management-status"></br></div>
        """

docs_off_md = """
        <style>

            .docs-status
            {
               background-color: red;
            }

        </style>
        <div class="docs-status"></br></div>
        """

docs_on_md = """
        <style>

            .docs-status
            {
               background-color: green;
            }

        </style>
        <div class="docs-status"></br></div>
        """

price_fetch_off_md = """
        <style>

            .price-fetch-status
            {
               background-color: red;
            }

        </style>
        <div class="price-fetch-status"></br></div>
        """

price_fetch_on_md = """
        <style>

            .price-fetch-status
            {
               background-color: green;
            }

        </style>
        <div class="price-fetch-status"></br></div>
        """

curve_fetch_off_md = """
        <style>

            .curve-fetch-status
            {
               background-color: red;
            }

        </style>
        <div class="curve-fetch-status"></br></div>
        """

curve_fetch_on_md = """
        <style>

            .curve-fetch-status
            {
               background-color: green;
            }

        </style>
        <div class="curve-fetch-status"></br></div>
        """


def is_port_in_use(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def initialize_session_state():
    """
    Initializes the streamlit session state object to use dynamic UI elements

    Returns
    -------
    None
    """
    if 'curve_gen_engine' not in st.session_state:
        st.session_state.curve_gen_engine = None

    if 'curve_gen_engine_status' not in st.session_state:
        st.session_state.curve_gen_engine_status = curve_gen_off_md

    if 'backtester_engine' not in st.session_state:
        st.session_state.backtester_engine = None

    if 'backtester_engine_status' not in st.session_state:
        st.session_state.backtester_engine_status = backtester_off_md

    if 'pool_creator_engine' not in st.session_state:
        st.session_state.pool_creator_engine = None

    if 'pool_creator_engine_status' not in st.session_state:
        st.session_state.pool_creator_engine_status = pool_creator_off_md

    if 'pool_backtester_engine' not in st.session_state:
        st.session_state.pool_backtester_engine = None

    if 'pool_backtester_engine_status' not in st.session_state:
        st.session_state.pool_backtester_engine_status = pool_backtester_off_md

    if 'log_management_engine' not in st.session_state:
        st.session_state.log_management_engine = None

    if 'log_management_engine_status' not in st.session_state:
        st.session_state.log_management_engine_status = log_management_off_md

    if 'docs_engine' not in st.session_state:
        st.session_state.docs_engine = None

    if 'files_engine' not in st.session_state:
        st.session_state.files_engine = None

    if 'docs_engine_status' not in st.session_state:
        st.session_state.docs_engine_status = docs_off_md

    if 'price_fetch_engine' not in st.session_state:
        st.session_state.price_fetch_engine = None

    if 'price_fetch_engine_status' not in st.session_state:
        st.session_state.price_fetch_engine_status = price_fetch_off_md

    if 'curve_fetch_engine' not in st.session_state:
        st.session_state.curve_fetch_engine = None

    if 'curve_fetch_engine_status' not in st.session_state:
        st.session_state.curve_fetch_engine_status = curve_fetch_off_md


def load_sidebar():
    """
    This function is where any sidebar UI elements go

    Returns
    -------
    None
    """
    st.sidebar.text("")


def do_main():
    """
    Main application function

    Returns
    -------
    None
    """
    load_sidebar()
    body()


def start_curve_gen_button_callback():
    """
    Callback function called when the user clicks the start button for the curve generator tab

    Returns
    -------
    None
    """
    if not is_port_in_use(8502):
        st.session_state.curve_gen_engine = subprocess.Popen([
            'streamlit', 'run', './potion/streamlitapp/curvegen/curve_gen_frontend.py',
            '--server.port', '8502', '--server.headless', 'true', '--', '--multi'])
        st.session_state.curve_gen_engine_status = curve_gen_on_md


def start_backtester_button_callback():
    """
    Callback function called when the user clicks the start button for the backtester tab

    Returns
    -------
    None
    """
    if not is_port_in_use(8503):
        st.session_state.backtester_engine = subprocess.Popen([
            'streamlit', 'run', './potion/streamlitapp/backt/backtest_frontend.py', '--server.port',
            '8503', '--server.headless', 'true', '--', '--multi'])
        st.session_state.backtester_engine_status = backtester_on_md


def start_pool_creator_button_callback():
    """
    Callback function called when the user clicks the start button for the portfolio creator tab

    Returns
    -------
    None
    """
    if not is_port_in_use(8504):
        st.session_state.pool_creator_engine = subprocess.Popen([
            'streamlit', 'run', './potion/streamlitapp/category/cat_frontend.py', '--server.port',
            '8504', '--server.headless', 'true', '--', '--multi'])
        st.session_state.pool_creator_engine_status = pool_creator_on_md


def start_pool_backtester_button_callback():
    """
    Callback function called when the user clicks the start button for the portfolio backtester tab

    Returns
    -------
    None
    """
    if not is_port_in_use(8505):
        st.session_state.pool_backtester_engine = subprocess.Popen([
            'streamlit', 'run', './potion/streamlitapp/multibackt/ma_frontend.py', '--server.port',
            '8505', '--server.headless', 'true', '--', '--multi'])
        st.session_state.pool_backtester_engine_status = pool_backtester_on_md


def start_log_management_button_callback():
    """
    Callback function called when the user clicks the start button for the log management tab

    Returns
    -------
    None
    """
    if not is_port_in_use(8506):
        st.session_state.log_management_engine = subprocess.Popen([
            'streamlit', 'run', './potion/streamlitapp/log_management/log_management_frontend.py',
            '--server.port', '8506', '--server.headless', 'true', '--', '--multi'])
        st.session_state.log_management_engine_status = log_management_on_md


def start_docs_button_callback():
    """
    Callback function called when the user clicks the start documentation button

    Returns
    -------
    None
    """
    # if not is_port_in_use(8080):
    # st.session_state.docs_engine = subprocess.Popen([
    #     'pdoc', '--html', '--output-dir', 'html', 'potion', '--force', '--http', ':'])
    st.session_state.files_engine = subprocess.Popen(['python', '-m', 'http.server'])
    st.session_state.docs_engine = subprocess.Popen([
        'pdoc', '--html', 'potion', '--force', '--http', ':'])
    st.session_state.docs_engine_status = docs_on_md


def start_price_fetch_button_callback():
    """
    Callback function called when the user clicks the start button for the price history fetch tab

    Returns
    -------
    None
    """
    if not is_port_in_use(8507):
        st.session_state.price_fetch_engine = subprocess.Popen([
            'streamlit', 'run', './potion/streamlitapp/price_fetch/price_fetch_frontend.py',
            '--server.port', '8507', '--server.headless', 'true', '--', '--multi'])
        st.session_state.price_fetch_engine_status = price_fetch_on_md


def start_curve_fetch_button_callback():
    """
    Callback function called when the user clicks the start button for the curve fetch tab

    Returns
    -------
    None
    """
    if not is_port_in_use(8508):
        st.session_state.curve_fetch_engine = subprocess.Popen([
            'streamlit', 'run', './potion/streamlitapp/curve_fetch/curve_fetch_frontend.py',
            '--server.port', '8508', '--server.headless', 'true', '--', '--multi'])
        st.session_state.curve_fetch_engine_status = curve_fetch_on_md


def stop_curve_gen_button_callback():
    """
    Callback function called when the user clicks the stop button for the curve generator tab

    Returns
    -------
    None
    """
    st.session_state.curve_gen_engine.kill()

    code = st.session_state.curve_gen_engine.wait()
    if code != 0 and code != 1:
        st.error('Error Stopping Curve Generator Engine: {}'.format(
            st.session_state.curve_gen_engine.returncode))
    else:
        st.session_state.curve_gen_engine = None
        st.session_state.curve_gen_engine_status = curve_gen_off_md

    # print('Stop Callback Complete')


def stop_backtester_button_callback():
    """
    Callback function called when the user clicks the stop button for the backtester tab

    Returns
    -------
    None
    """
    st.session_state.backtester_engine.kill()

    code = st.session_state.backtester_engine.wait()
    if code != 0 and code != 1:
        st.error('Error Stopping Backtester Engine: {}'.format(
            st.session_state.backtester_engine.returncode))
    else:
        st.session_state.backtester_engine = None
        st.session_state.backtester_engine_status = backtester_off_md

    # print('Stop Callback Complete')


def stop_pool_creator_button_callback():
    """
    Callback function called when the user clicks the stop button for the portfolio creator tab

    Returns
    -------
    None
    """
    st.session_state.pool_creator_engine.kill()

    code = st.session_state.pool_creator_engine.wait()
    if code != 0 and code != 1:
        st.error('Error Stopping Pool Creator Engine: {}'.format(
            st.session_state.pool_creator_engine.returncode))
    else:
        st.session_state.pool_creator_engine = None
        st.session_state.pool_creator_engine_status = pool_creator_off_md

    # print('Stop Callback Complete')


def stop_pool_backtester_button_callback():
    """
    Callback function called when the user clicks the stop button for the portfolio backtester tab

    Returns
    -------
    None
    """
    st.session_state.pool_backtester_engine.kill()

    code = st.session_state.pool_backtester_engine.wait()
    if code != 0 and code != 1:
        st.error('Error Stopping Pool Backtester Engine: {}'.format(
            st.session_state.pool_backtester_engine.returncode))
    else:
        st.session_state.pool_backtester_engine = None
        st.session_state.pool_backtester_engine_status = pool_backtester_off_md

    # print('Stop Callback Complete')


def stop_log_management_button_callback():
    """
    Callback function called when the user clicks the stop button for the log management tab

    Returns
    -------
    None
    """
    st.session_state.log_management_engine.kill()

    code = st.session_state.log_management_engine.wait()
    if code != 0 and code != 1:
        st.error(
            'Error Stopping Log Management Engine: {}'.format(
                st.session_state.log_management_engine.returncode))
    else:
        st.session_state.log_management_engine = None
        st.session_state.log_management_engine_status = log_management_off_md

    # print('Stop Callback Complete')


def stop_docs_button_callback():
    """
    Callback function called when the user clicks the stop button for the documentation tab

    Returns
    -------
    None
    """
    st.session_state.docs_engine.kill()
    st.session_state.files_engine.kill()

    code = st.session_state.docs_engine.wait()
    if code != 0 and code != 1:
        st.error('Error Stopping Docs Engine: {}'.format(st.session_state.docs_engine.returncode))
    else:
        st.session_state.docs_engine = None
        st.session_state.docs_engine_status = docs_off_md

    code = st.session_state.files_engine.wait()

    if code != 0 and code != 1:
        st.error('Error Stopping Files Engine: {}'.format(st.session_state.files_engine.returncode))

    # print('Stop Callback Complete')


def stop_price_fetch_button_callback():
    """
    Callback function called when the user clicks the stop button for the price fetch tool tab

    Returns
    -------
    None
    """
    st.session_state.price_fetch_engine.kill()

    code = st.session_state.price_fetch_engine.wait()
    if code != 0 and code != 1:
        st.error(
            'Error Stopping Historical Data Download Engine: {}'.format(
                st.session_state.price_fetch_engine.returncode))
    else:
        st.session_state.price_fetch_engine = None
        st.session_state.price_fetch_engine_status = price_fetch_off_md

    # print('Stop Callback Complete')


def stop_curve_fetch_button_callback():
    """
    Callback function called when the user clicks the stop button for the curve fetch tab

    Returns
    -------
    None
    """
    st.session_state.curve_fetch_engine.kill()

    code = st.session_state.curve_fetch_engine.wait()
    if code != 0 and code != 1:
        st.error(
            'Error Stopping Curve Download Engine: {}'.format(
                st.session_state.curve_fetch_engine.returncode))
    else:
        st.session_state.curve_fetch_engine = None
        st.session_state.curve_fetch_engine_status = curve_fetch_off_md

    # print('Stop Callback Complete')


def load_curve_gen_panel():
    """
    Loads the UI elements for the curve generator tab panel

    Returns
    -------
    None
    """
    with st.expander('3. Curve Generator Control', expanded=True):
        # st.subheader('Curve Generator')
        col1, col2 = st.columns(2)
        col1.button('Start Curve Generator App', on_click=start_curve_gen_button_callback)
        col1.button('Stop Curve Generator App', on_click=stop_curve_gen_button_callback)
        col2.text('App Status: ')
        col2.markdown(st.session_state.curve_gen_engine_status, unsafe_allow_html=True)
        link = '[Open Curve Generator in new tab](http://localhost:8502/)'
        col2.markdown(link, unsafe_allow_html=True)


def load_backtester_panel():
    """
    Loads the UI elements for the backtester tab panel

    Returns
    -------
    None
    """
    with st.expander('4. Curve Backtester Control', expanded=True):
        col1, col2 = st.columns(2)
        col1.button('Start Curve Backtester App', on_click=start_backtester_button_callback)
        col1.button('Stop Curve Backtester App', on_click=stop_backtester_button_callback)
        col2.text('App Status: ')
        col2.markdown(st.session_state.backtester_engine_status, unsafe_allow_html=True)
        link = '[Open Curve Backtester in new tab](http://localhost:8503/)'
        col2.markdown(link, unsafe_allow_html=True)


def load_pool_creator_panel():
    """
    Loads the UI elements for the portfolio creator tab panel

    Returns
    -------
    None
    """
    with st.expander('5. Pool Creator Control', expanded=True):
        col1, col2 = st.columns(2)
        col1.button('Start Pool Creator App', on_click=start_pool_creator_button_callback)
        col1.button('Stop Pool Creator App', on_click=stop_pool_creator_button_callback)
        col2.text('App Status: ')
        col2.markdown(st.session_state.pool_creator_engine_status, unsafe_allow_html=True)
        link = '[Open Pool Creator in new tab](http://localhost:8504/)'
        col2.markdown(link, unsafe_allow_html=True)


def load_pool_backtester_panel():
    """
    Loads the UI elements for the portfolio backtester tab panel

    Returns
    -------
    None
    """
    with st.expander('6. Pool Backtester Control', expanded=True):
        col1, col2 = st.columns(2)
        col1.button('Start Pool Backtester App', on_click=start_pool_backtester_button_callback)
        col1.button('Stop Pool Backtester App', on_click=stop_pool_backtester_button_callback)
        col2.text('App Status: ')
        col2.markdown(st.session_state.pool_backtester_engine_status, unsafe_allow_html=True)
        link = '[Open Pool Backtester in new tab](http://localhost:8505/)'
        col2.markdown(link, unsafe_allow_html=True)


def load_log_management_panel():
    """
    Loads the UI elements for the log management tab panel

    Returns
    -------
    None
    """
    with st.expander('7. Log Management Control', expanded=True):
        col1, col2 = st.columns(2)
        col1.button('Start Log Management App', on_click=start_log_management_button_callback)
        col1.button('Stop Log Management App', on_click=stop_log_management_button_callback)
        col2.text('App Status: ')
        col2.markdown(st.session_state.log_management_engine_status, unsafe_allow_html=True)
        link = '[Open Log Management in new tab](http://localhost:8506/)'
        col2.markdown(link, unsafe_allow_html=True)


def load_docs_panel():
    """
    Loads the UI elements for the documentation tab panel

    Returns
    -------
    None
    """
    with st.expander('Documentation Control', expanded=True):
        col1, col2 = st.columns(2)
        col1.button('Start Docs App', on_click=start_docs_button_callback)
        col1.button('Stop Docs App', on_click=stop_docs_button_callback)
        col2.text('App Status: ')
        col2.markdown(st.session_state.docs_engine_status, unsafe_allow_html=True)
        link = '[Open Documentation in new tab](http://localhost:8080/potion/user_guides/)'
        col2.markdown(link, unsafe_allow_html=True)


def load_price_fetch_panel():
    """
    Loads the UI elements for the price fetch tab panel

    Returns
    -------
    None
    """
    with st.expander('1. Historical Data Download Control', expanded=True):
        col1, col2 = st.columns(2)
        col1.button('Start Historical Data Download App',
                    on_click=start_price_fetch_button_callback)
        col1.button('Stop Historical Data Download App', on_click=stop_price_fetch_button_callback)
        col2.text('App Status: ')
        col2.markdown(st.session_state.price_fetch_engine_status, unsafe_allow_html=True)
        link = '[Open Historical Data Download in new tab](http://localhost:8507/)'
        col2.markdown(link, unsafe_allow_html=True)


def load_curve_fetch_panel():
    """
    Loads the UI elements for the curve download tab panel

    Returns
    -------
    None
    """
    with st.expander('2. Curve Subgraph Download Control', expanded=True):
        col1, col2 = st.columns(2)
        col1.button('Start Curve Download App',
                    on_click=start_curve_fetch_button_callback)
        col1.button('Stop Curve Download App', on_click=stop_curve_fetch_button_callback)
        col2.text('App Status: ')
        col2.markdown(st.session_state.curve_fetch_engine_status, unsafe_allow_html=True)
        link = '[Open Curve Download in new tab](http://localhost:8508/)'
        col2.markdown(link, unsafe_allow_html=True)


def body(json_name='./urls.json'):
    """
    This function loads the UI elements of the web app page body

    Returns
    -------
    None
    """
    initialize_session_state()

    # Start all the apps on startup
    start_curve_gen_button_callback()
    start_backtester_button_callback()
    start_pool_creator_button_callback()
    start_pool_backtester_button_callback()
    start_log_management_button_callback()
    start_docs_button_callback()
    start_price_fetch_button_callback()
    start_curve_fetch_button_callback()

    with st.expander('', expanded=True):
        with open(json_name, 'r') as rf:
            url_dict = json.load(rf)

            st.markdown(welcome_text)

            display_text = "    ## Potion Whitepapers and Notion Docs  \n" + \
                           "    | Paper Link    | Description |  \n" + \
                           "    | ------------- | ----------- |  \n" + \
                           "    | [Notion Docs]({})   | ".format(
                               url_dict['notion']) + \
                           "The Notion pages containing all of the Potion documentation |  \n" + \
                           "    | [Fat Tailed Curve Generation Paper]" + \
                           "(http://localhost:8000/paper/Bonding-Curve-Generation-for-Fat-Tailed-Models.pdf) | " + \
                           "A Paper describing the process by which the Kelly Curves " + \
                           "are generated within these tools. |  \n" + \
                           "    | [Arbitrage Curve Generation Paper]" + \
                           "(http://localhost:8000/paper/Arbitrage-Free-Generation-of-Bonding-Curves-Using-the-Kelly-Criterion.pdf) | " + \
                           "A Paper describing the process this tool can use to generate Kelly " \
                           "Curves with no arbitrage. | \n" + \
                           "    | [Protocol Papers]" \
                           "(https://www.notion.so/Potion-Protocol-d5a6682ed0d74dbfb2fe43a0600f5792) | " + \
                           "A Paper describing the webapp routing algorithm. |  \n" + \
                           "    | [Kelly Finance]({}) | ".format(
                               url_dict['kelly_finance']) + "An interactive webapp for " + \
                           "learning about the Kelly Criterion and generating curves. |  \n"
            st.markdown(display_text)

    load_price_fetch_panel()
    load_curve_fetch_panel()
    load_curve_gen_panel()
    load_backtester_panel()
    load_pool_creator_panel()
    load_pool_backtester_panel()
    load_log_management_panel()
    load_docs_panel()


if __name__ == '__main__':
    do_main()

#!/usr/bin/env python3
"""Module with streamlit components"""
import matplotlib.pyplot as plt
from bokeh.models.widgets import Div
import streamlit as st
import lib.helpers as hlp
import lib.plotting as plotting

LAYOUT = "centered"
SIDEBAR_STATE = "expanded"
CACHE_KWARGS = {"show_spinner": False, "suppress_st_warning": True, "ttl": 3600, "max_entries": 30}
CACHE_SINGLETON_KWARGS = {"show_spinner": False, "suppress_st_warning": True}

HIDE_ST_STYLE = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """

TERMS_AND_CONDITIONS_LINK = \
    '''https://www.notion.so/Kelly-finance-Terms-Conditions-5c0851151fcd4ec8b6ed98081f69e689'''


# slider defaults
###################################################################################################
SLIDER_MIN_STRIKE = 70
SLIDER_MAX_STRIKE = 130
SLIDER_DEFAULT_STRIKE = 100

SLIDER_MIN_DURATION = 1
SLIDER_MAX_DURATION = 28
SLIDER_MAX2_DURATION = 365
SLIDER_DEFAULT_DURATION = 1

SLIDER_MIN_DAYS = 28
SLIDER_MAX_DAYS = 365
SLIDER_MAX2_DAYS = 1000
SLIDER_DEFAULT_DAYS = 28

SLIDER_MIN_PATHS = 10
SLIDER_MAX_PATHS = 250
SLIDER_MAX2_PATHS = 1000
SLIDER_DEFAULT_PATHS = 10

SLIDER_MIN_UTIL = 0
SLIDER_MAX_UTIL = 100
SLIDER_DEFAULT_UTIL = 50

SLIDER_MIN_PREMIUM_OFFSET = -100
SLIDER_MAX_PREMIUM_OFFSET = 100
SLIDER_DEFAULT_PREMIUM_OFFSET = 0

CONVOLUTION_N_PATHS = 1000
###################################################################################################

def button_with_link(link, button_name, button_holder, new_tab=False):
    """button with embedded link"""
    if button_holder.button(button_name):
        if new_tab:
            js_code = f"window.open({link})"  # New tab or window
        else:
            js_code = f"window.location.href = {link}"  # Current tab
        html = f'<img src onerror="{js_code}">'
        div = Div(text=html)
        button_holder.bokeh_chart(div)


def add_cross_app_links_to_sidebar(sidebar):
    """Way to add Navigation to the sidebar"""
    st.markdown(
        """
                <style>
                    .stButton>button {
                        width: 15em;
                    }
                </style>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 270px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 270px;
            margin-left: -500px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    sidebar.title("Navigation")
    button_with_link(
        "'https://academy.kelly.finance/'", "Kelly Academy", sidebar
    )
    button_with_link(
        "'https://optimal.kelly.finance'", "Kelly Optimal Premiums", sidebar
    )
    button_with_link(
        "'https://bsm-bench.kelly.finance/'", "Kelly vs Black Scholes", sidebar
    )
    # button_with_link(
    #     "'https://kelly-input-generation.herokuapp.com/'", "input-generation", sidebar
    # )
    button_with_link(
        "'https://custom.kelly.finance/'",
        "Curve designer ",
        sidebar,
    )
    button_with_link(
        "'https://portfolio.kelly.finance/'",
        "Multi-asset Kelly",
        sidebar,
    )


def set_max_container_width(n_pixels=1100):
    """Utilizing raw css to adjust streamlit containers"""
    max_width_str = f"max-width: {n_pixels}px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def setup_page_config(page_name):
    """Just a wrapper for the page config"""
    st.set_page_config(
        page_title=page_name,
        layout=LAYOUT,
        initial_sidebar_state=SIDEBAR_STATE,
        page_icon=f"{hlp.MEDIA_DIR}/potion_favicon.png",
    )
    # st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)
    set_max_container_width()


def add_style_settings_to_sidebar(sidebar):
    "Allows to change graphs"
    sidebar.title("Style")
    graph_background = sidebar.radio("Graph Background", ["black", "white"])
    sidebar.write("Make sure to change Theme in Settings in the Hamburger Menu as well")
    if graph_background == "black":
        graph_settings = plotting.GraphSettings(
            background_color="#0E1117",
            template_pick="plotly_dark",
            linewidth=1,
            linecolor="#1b003d",
            gridcolor="black",
            zerolinecolor="#ffffff",  # "#813eed",
            showline=False,
            text_color="#ffffff",  # duplicate of the setting from "config.toml"
            accent_color="#f3ff0f",
            second_accent="#e7e311",
        )

    else:
        graph_settings = plotting.GraphSettings(
            background_color="white",
            template_pick="plotly_white",
            linewidth=1,
            linecolor="#1b003d",
            gridcolor="#d4d4d4",
            zerolinecolor="#000000",  # "#813eed",
            showline=False,
            text_color="#000000",  # duplicate of the setting from "config.toml"
            accent_color="#12dad9",
            second_accent="#e7e311",
        )

    plt.rcParams.update(
        {
            "hatch.color": graph_settings.background_color,
            "lines.color": graph_settings.text_color,
            "patch.edgecolor": graph_settings.text_color,
            "patch.facecolor": ([0, 1, 1]),
            "grid.alpha": 0.4,
            "text.color": graph_settings.text_color,
            "axes.facecolor": graph_settings.background_color,
            "axes.edgecolor": graph_settings.gridcolor,
            "axes.labelcolor": graph_settings.text_color,
            "xtick.color": graph_settings.text_color,
            "ytick.color": graph_settings.text_color,
            "grid.color": graph_settings.gridcolor,
            "figure.facecolor": graph_settings.background_color,
            "figure.edgecolor": graph_settings.background_color,
            "savefig.facecolor": graph_settings.background_color,
            "savefig.edgecolor": graph_settings.background_color,
        }
    )

    return graph_settings

def get_footer(text_color, background_color):
    '''Footer'''
    footer=f"""<style>
a:link , a:visited{{
color: {text_color};
background-color: transparent;
text-decoration: underline;
}}

a:hover,  a:active {{
color: red;
background-color: transparent;
text-decoration: underline;
}}

.footer {{
position: fixed;
display: block;
left: 0;
bottom: 0;
right:0;
width: 100%;
background-color: {background_color};
color: black;
text-align: center;
}}
</style>
<div class="footer">
<p><a href='{TERMS_AND_CONDITIONS_LINK}' target="_blank">Terms and Conditions</a></p>
</div>
"""

    return footer

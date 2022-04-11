#!/usr/bin/env python3
"""Script which creates flow2 input files in the form of streamlit app"""

import itertools
import numpy as np
import pandas as pd
import streamlit as st
import lib.helpers as hlp
import lib.steamlit_components as sc

##########################################################################################
# SETTINGS
##########################################################################################
# DEFAULT SETTINGS

# duration
DEFAULT_MIN_DURATION = 0
DEFAULT_MAX_DURATION = 10
DEFAULT_STEP_DURATION = 1
DURATION_DICT = {
    "default_min": DEFAULT_MIN_DURATION,
    "min_min": 0,
    "max_min": 30,
    "default_max": DEFAULT_MAX_DURATION,
    "min_max": 1,
    "max_max": 31,
    "default_step": DEFAULT_STEP_DURATION,
    "min_step": 2,
    "max_step": 30,
}

# utils
DEFAULT_MIN_UTIL = 1
DEFAULT_MAX_UTIL = 100
DEFAULT_STEP_UTIL = 10
UTIL_DICT = {
    "default_min": DEFAULT_MIN_UTIL,
    "min_min": 0,
    "max_min": 100,
    "default_max": DEFAULT_MAX_UTIL,
    "min_max": 0,
    "max_max": 100,
    "default_step": DEFAULT_STEP_UTIL,
    "min_step": 2,
    "max_step": 99,
}

# strikes
DEFAULT_MIN_STRIKE = -20
DEFAULT_MAX_STRIKE = 20
DEFAULT_STEP_STRIKE = 2

STRIKE_DICT = {
    "default_min": DEFAULT_MIN_STRIKE,
    "min_min": -50,
    "max_min": 50,
    "default_max": DEFAULT_MAX_STRIKE,
    "min_max": -50,
    "max_max": 50,
    "default_step": DEFAULT_STEP_STRIKE,
    "min_step": 2,
    "max_step": 99,
}

##########################################################################################
# FUNCTIONS
##########################################################################################
@st.cache(**sc.CACHE_KWARGS)
def get_historical_prices_df():
    '''Caching wrapper'''
    return hlp.get_historical_prices_df()

def create_intro():
    """Create some text with explanations"""
    st.title("Create Instruments Batch")
    intro_expander = st.expander("Introdution", expanded=True)
    with intro_expander:
        st.write(
            "Instrument is defined by the few params: asset_name, duration, strike, etc."
        )
        st.write("Goal is to have a set of different instruments.")
        st.write("First please choose a set of values for each param.")
        st.write(
            "Then generate all the combinations of params list values with the Button push."
        )
        st.write("Results are available as a downloadable instruments.csv.")


def create_three_sliders(name, val_dict):
    """Create three sliders, return values from sliders"""
    st.write(name)
    col1, col2, col3 = st.columns(3)

    val1 = col1.slider(
        "Min",
        val_dict["min_min"],
        val_dict["max_min"],
        val_dict["default_min"],
    )

    val2 = col2.slider(
        "Max",
        val_dict["min_max"],
        val_dict["max_max"],
        val_dict["default_max"],
    )

    val3 = col3.slider(
        "Steps between min and max",
        val_dict["min_step"],
        val_dict["max_step"],
        val_dict["default_step"],
    )

    return val1, val2, val3


@st.cache(**sc.CACHE_KWARGS)
def convert_df_to_csv(some_df):
    """Convert pd.DataFrame to csv string"""
    return some_df.to_csv().encode("utf-8")


@st.cache(**sc.CACHE_KWARGS)
def create_values_list(min_value, max_value, steps):
    """variation of the range()"""
    if min_value == max_value:
        generated_list = [max_value]
    elif min_value > max_value:
        generated_list = []
    else:
        generated_list = np.linspace(min_value, max_value, steps)

    return generated_list


def create_sidebar():
    """Initialize some Settings"""
    # Title
    st.sidebar.title("Settings menu")
    st.sidebar.write(
        "The parameters chosen here affect the instruments batch you generate"
    )
    st.sidebar.text("")

    historical_df_inner = get_historical_prices_df()

    st.session_state["start_date"] = historical_df_inner.index.min()
    st.session_state["end_date"] = historical_df_inner.index.max()

    assets = [
        asset
        for asset in historical_df_inner.columns
        if (not "Unnam" in asset and not "Master" in asset)
    ]

    assets = st.multiselect("Assets Choice", assets)

    st.sidebar.text("")
    st.sidebar.text("Moods")

    col1, col2, col3 = st.sidebar.columns(3)
    col1.header("Full")
    col2.header("Bear")
    col3.header("Bull")

    st.session_state["mood_full"] = col1.checkbox("Full", value=True)
    st.session_state["mood_bear"] = col2.checkbox("Bear")
    st.session_state["mood_bull"] = col3.checkbox("Bull")

    if not any(
        [
            st.session_state["mood_full"],
            st.session_state["mood_bear"],
            st.session_state["mood_bull"],
        ]
    ):
        st.sidebar.warning("Please pick at least one mood")

    st.session_state["mood_segment_len"] = st.sidebar.slider(
        "Mood Segment Length", 1, 365, 365
    )

    return historical_df_inner, assets


def input_generation():
    """main function to run"""
    sc.add_cross_app_links_to_sidebar(st.sidebar)

    ##########################################################################################
    # APP LOGIC
    ##########################################################################################
    create_intro()

    historical_df, assets_list = create_sidebar()

    if not assets_list:
        st.warning("Please choose at least one asset")
    st.markdown("""---""")

    st.session_state["util_vals"] = create_three_sliders("Util", UTIL_DICT)

    st.markdown("""---""")

    st.session_state["strike_vals"] = create_three_sliders("Strike", STRIKE_DICT)

    st.markdown("""---""")

    st.write("Duration")

    durations_dict = {}
    cols_duration = st.columns(4)
    durations_dict[1] = cols_duration[0].checkbox("Daily", value=True)
    durations_dict[7] = cols_duration[1].checkbox("Weekly", value=False)
    durations_dict[14] = cols_duration[2].checkbox("2Weekly", value=False)
    durations_dict[30] = cols_duration[3].checkbox("Monthly", value=False)

    if not any(durations_dict.values()):
        st.warning("Please pick at least one duration")

    st.markdown("""---""")

    st.write("Option Type")

    option_types_list = []
    cols_option_types = st.columns(2)

    put = cols_option_types[0].checkbox("Put", value=True)
    call = cols_option_types[1].checkbox("Call", value=False)

    if put:
        option_types_list.append("put")
    if call:
        option_types_list.append("call")

    if len(option_types_list) == 0:
        st.warning("Please pick at least one Option Type")

    st.markdown("""---""")

    ##########################################################################################
    st.session_state["generate_button"] = st.button("Generate Instruments Batch")

    if st.session_state["generate_button"]:
        # create lists for the combinations
        ######################################################################################
        columns = [
            "asset",
            "strike_pct",
            "duration",
            "util",
            "mood",
            "option_type",
        ]
        strike_pcts = create_values_list(
            st.session_state["strike_vals"][0],
            st.session_state["strike_vals"][1],
            st.session_state["strike_vals"][2],
        )

        durations = [key for key, value in durations_dict.items() if value]

        utilizations = create_values_list(
            st.session_state["util_vals"][0],
            st.session_state["util_vals"][1],
            st.session_state["util_vals"][2],
        )

        moods = []
        if st.session_state["mood_full"]:
            moods.append("Full History")
        if st.session_state["mood_bear"]:
            moods.append("bear")
        if st.session_state["mood_bull"]:
            moods.append("bull")
        ######################################################################################
        # generate combinations
        ######################################################################################
        all_combinations = list(
            itertools.product(
                assets_list,
                strike_pcts,
                durations,
                utilizations,
                moods,
                option_types_list,
            )
        )
        instruments_df = pd.DataFrame(all_combinations, columns=columns)
        cache_asset_dict = {}
        instruments_df["train_start_date"] = None
        instruments_df["train_end_date"] = None

        # change mood dates
        for index, row in instruments_df.iterrows():

            # if row["mood"] != "Full History":
            if row["asset"] + row["mood"] in cache_asset_dict:
                (
                    instruments_df.at[index, "train_start_date"],
                    instruments_df.at[index, "train_end_date"],
                ) = cache_asset_dict[row["asset"] + row["mood"]]
            else:

                tmp_price_series = historical_df[row["asset"]].dropna()
                (
                    instruments_df.at[index, "train_start_date"],
                    instruments_df.at[index, "train_end_date"],
                ) = hlp.get_mood_segment_dates(
                    tmp_price_series,
                    segment_len_days=st.session_state["mood_segment_len"],
                    mood=row["mood"],
                    metric="sharpe",
                )
                cache_asset_dict[row["asset"] + row["mood"]] = (
                    instruments_df.at[index, "train_start_date"],
                    instruments_df.at[index, "train_end_date"],
                )
        instruments_df["train_start_date"] = pd.to_datetime(
            instruments_df["train_start_date"]
        ).dt.date
        instruments_df["train_end_date"] = pd.to_datetime(
            instruments_df["train_end_date"]
        ).dt.date
        filtered_instruments_df = instruments_df[
            (instruments_df["mood"] == "bear") | (instruments_df["mood"] == "bull")
        ]
        filtered_instruments_df = filtered_instruments_df[
            filtered_instruments_df["train_end_date"].isnull()
        ]
        if len(filtered_instruments_df):
            st.warning(
                (
                    f"Warning: There is not enough historical data "
                    f"to generate mood segments of length "
                    f'{st.session_state["mood_segment_len"]} for: '
                    f' {filtered_instruments_df["asset"].unique()}. \n'
                )
            )
            st.warning(
                f"Therefore, these moods were skipped in the generated file. \n"
                f"Please shorten the mood segment length in the settings "
                f"menu if you want to include mood segments for "
                f'{filtered_instruments_df["asset"].unique()}.'
            )

        instruments_df["util"] /= 100
        st.write(f"Generated {len(instruments_df)} Instruments")

        st.download_button(
            "Download Generated Instruments",
            convert_df_to_csv(instruments_df),
            mime="text/csv",
            file_name="instruments.csv",
        )


if __name__ == "__main__":
    sc.setup_page_config("MultiAsset potrfolio creation/backtest")
    input_generation()

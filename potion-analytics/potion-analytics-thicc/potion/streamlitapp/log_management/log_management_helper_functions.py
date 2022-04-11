"""
This module provides the backend code for the log management tool
"""
import os
import glob
from zipfile import ZipFile
from pathlib import Path
import streamlit as st
import vaex
import pandas as pd
from potion.streamlitapp.preference_saver import (preference_df_file_name, initialize_preference_df,
                                                  save_widget_preferences, get_pref, WIDGET_CF,
                                                  WIDGET_IC, WIDGET_IS, WIDGET_IH, WIDGET_DF)


def zip_files_in_directory(directory, zip_archive_name, filter_lambda):
    """
    This function zips a set of results into a single archive file for convenience

    Parameters
    ----------
    directory : str
        The directory containing the files
    zip_archive_name : str
        The desired name of the output zip file
    filter_lambda : Callable
        Used to filter files with expressions
    """
    dir_cwd = Path(directory).cwd()
    with ZipFile(zip_archive_name, 'w') as zip_file:

        file_list = []
        file_list.extend([path.resolve() for path in Path(directory).rglob('*.csv')])
        file_list.extend([path.resolve() for path in Path(directory).rglob('*.svg')])
        file_list.extend([path.resolve() for path in Path(directory).rglob('*.hdf5')])

        for path in file_list:

            if filter_lambda(str(path)):

                archive_path = str(path).replace(str(dir_cwd), '.').replace(
                    'batch_results' + os.sep, '').replace(
                    'batch_{}'.format(st.session_state.batch_number) + os.sep, '')

                zip_file.write(str(path), archive_path)


def delete_files_in_directory(directory, filter_lambda):
    """
    This function deletes a set of files from a single directory

    Parameters
    ----------
    directory : str
        The directory containing the files
    filter_lambda : Callable
        Used to filter files with expressions
    """
    file_list = []
    file_list.extend([path.resolve() for path in Path(directory).rglob('*.csv')])
    file_list.extend([path.resolve() for path in Path(directory).rglob('*.svg')])
    file_list.extend([path.resolve() for path in Path(directory).rglob('*.hdf5')])

    for path in file_list:

        if filter_lambda(str(path)):
            os.remove(str(path))


def _get_batch_numbers(directory='./batch_results'):
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


def _get_files(log_dir, include_csv, include_svg, include_hdf5, include_zip):
    """
    Gets all of the files in the directory the caller cares about

    Parameters
    ----------
    log_dir : str
        The directory to get files from
    include_csv : bool
        True or False whether to include CSV files
    include_svg : bool
        True or False whether to include SVG files
    include_hdf5 : bool
        True or False whether to include HDF5 files
    include_zip : bool
        True or False whether to include ZIP files

    Returns
    -------
    file_list : List[str]
        The list of files in the directory filtered by the extensions the caller cares about
    """
    file_list = []

    if include_csv:
        csv_files = [path.resolve() for path in Path(log_dir).rglob('*.csv')]
        file_list.extend(csv_files)

    if include_svg:
        svg_files = [path.resolve() for path in Path(log_dir).rglob('*.svg')]
        file_list.extend(svg_files)

    if include_hdf5:
        hdf5_files = [path.resolve() for path in Path(log_dir).rglob('*.hdf5')]
        file_list.extend(hdf5_files)

    if include_zip:
        zip_files = [path.resolve() for path in Path(log_dir).rglob('*.zip')]
        file_list.extend(zip_files)

    return file_list


def _get_filter_condition(file_name):
    """
    Gets a True or False condition of whether to filter a file from a list based on the name

    Parameters
    ----------
    file_name : str
        The name of the file we may filter

    Returns
    -------
    condition : bool
        True or False whether to filter the file
    """
    file_extension = file_name.split('.')[-1].lower()

    csv_type_condition = (file_extension == 'csv' and st.session_state.include_csv)
    svg_type_condition = (file_extension == 'svg' and st.session_state.include_svg)
    hdf5_type_condition = (file_extension == 'hdf5' and st.session_state.include_hdf5)

    type_condition = csv_type_condition or svg_type_condition or hdf5_type_condition

    batch_condition = 'batch_{}'.format(st.session_state.batch_number) in file_name
    condition = batch_condition and type_condition

    return condition


def initialize_log_session_state():
    """
    Initializes the session_state streamlit object so that we can have
    dynamic UI components in streamlit

    Returns
    -----------
    None
    """
    if 'log_dir' not in st.session_state:
        st.session_state.log_dir = None

    if 'include_csv' not in st.session_state:
        st.session_state.include_csv = None

    if 'include_svg' not in st.session_state:
        st.session_state.include_svg = None

    if 'include_hdf5' not in st.session_state:
        st.session_state.include_hdf5 = None

    if 'delete_files' not in st.session_state:
        st.session_state.delete_files = None

    if 'batch_number' not in st.session_state:
        st.session_state.batch_number = None

    if 'pref_df' not in st.session_state:
        st.session_state.pref_df = None

    if os.path.isfile(preference_df_file_name):
        st.session_state.pref_df = pd.read_csv(preference_df_file_name, sep=',')
    else:
        st.session_state.pref_df = initialize_preference_df()


def load_log_settings_panel():
    """
    Displays the UI panels to the user.

    Returns
    -----------
    None
    """
    st.session_state.log_dir = '.{}batch_results{}'.format(os.sep, os.sep)

    log_converter_form = st.form(key='log_conversion_widget')

    log_converter_form.subheader('Log Conversion Widget')

    link = '[Open User Guide](http://localhost:8080/potion/user_guides/log_archive_user_guide.html)'
    log_converter_form.markdown(link, unsafe_allow_html=True)

    # Get all of the HDF5 binary log files
    log_file_list = _get_files(st.session_state.log_dir, False, False, True, False)
    log_file_list.sort()

    # Select the default value for the selectbox
    if get_pref(WIDGET_CF) in log_file_list:
        input_index = log_file_list.index(get_pref(WIDGET_CF))
    else:
        input_index = 0

    log_converter_form.text(
        'Use this widget to convert the binary .hdf5 log file output by this program into a CSV.')

    # Define the UI inputs
    selected_log_to_convert = log_converter_form.selectbox('Select the log file to convert:',
                                                           log_file_list,
                                                           index=input_index)

    log_converter_form.text('Current Log File Name: {}'.format(selected_log_to_convert))

    convert_log_button = log_converter_form.form_submit_button('Convert to CSV')

    # If the button is pressed, run the log conversion
    if convert_log_button:
        log_as_str = str(selected_log_to_convert)
        output_csv = log_as_str[0:log_as_str.index(log_as_str.split('.')[-1])] + 'csv'
        log_df = vaex.open(selected_log_to_convert)
        log_df.export_csv(output_csv, progress='widget')

        save_widget_preferences(selected_log_to_convert, st.session_state.batch_number,
                                st.session_state.include_csv,
                                st.session_state.include_svg, st.session_state.include_hdf5,
                                st.session_state.delete_files)

        log_converter_form.text('Conversion complete')

    results_archive_form = st.form(key='results_archive_form')

    results_archive_form.subheader('Results Archive Widget')

    results_archive_form.text('Use this widget to archive results output from the apps')

    batch_numbers = _get_batch_numbers()

    st.session_state.batch_number = results_archive_form.selectbox(
        'Select the batch number to archive (directory ./batch_results)',
        batch_numbers, index=0)

    st.session_state.include_csv = results_archive_form.checkbox('Include CSV Files in zip archive',
                                                                 value=get_pref(WIDGET_IC))
    st.session_state.include_svg = results_archive_form.checkbox('Include SVG Files in zip archive',
                                                                 value=get_pref(WIDGET_IS))
    st.session_state.include_hdf5 = results_archive_form.checkbox(
        'Include HDF5 Files in zip archive',
        value=get_pref(WIDGET_IH))
    st.session_state.delete_files = results_archive_form.checkbox(
        'Delete Files after including in zip archive',
        value=get_pref(WIDGET_DF))

    archive_button = results_archive_form.form_submit_button('Archive Results')

    if archive_button:

        zip_files_in_directory(st.session_state.log_dir,
                               st.session_state.log_dir + os.sep + 'batch_{}.zip'.format(
                                   st.session_state.batch_number),
                               _get_filter_condition)

        if st.session_state.delete_files:
            delete_files_in_directory(st.session_state.log_dir, _get_filter_condition)

        save_widget_preferences(selected_log_to_convert, st.session_state.batch_number,
                                st.session_state.include_csv,
                                st.session_state.include_svg, st.session_state.include_hdf5,
                                st.session_state.delete_files)


def load_log_results_panel():
    """
    This function displays the streamlit panels containing the results directory to the user

    Returns
    -----------
    None
    """
    with st.expander('Show Current Results Directory', expanded=True):
        st.text('Current Results Directory: {} (*.csv, *.svg, *.hdf5, *.zip)'.format(
            st.session_state.log_dir))

        # Display all of the relevant files in the directory
        file_list = _get_files(st.session_state.log_dir, True, True, True, True)

        # Repackage as DF
        keys = ['FileExtension', 'FileName']
        files_enum = [[file_name.name.split('.')[-1].upper(), str(file_name)]
                      for file_name in file_list]
        file_map = [{key: value for (key, value) in zip(keys, vals)} for vals in files_enum]
        file_df = pd.DataFrame(file_map)

        st.table(file_df)

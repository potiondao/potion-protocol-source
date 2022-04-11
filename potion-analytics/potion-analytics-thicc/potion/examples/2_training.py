"""
Usage Example code for the training module
"""
import pandas as pd
from scipy.stats import skewnorm
from potion.curve_gen.training.builder import TrainingConfigBuilder
from potion.curve_gen.training.train import configure_training, train


def _error_file_not_found(filename: str):
    raise FileNotFoundError('Check configuration. Could not find File: {}'.format(filename))


def _error_bad_csv_format(filename: str):
    raise ValueError('Check configuration. CSV file bad format: {}'.format(filename))


def _check_input_format(csv_df: pd.DataFrame):
    return 'Asset' == csv_df.columns[0]


def _check_training_format(csv_df: pd.DataFrame):
    return 'Master calendar' == csv_df.columns[0]


def training_builder():
    """
    Example Hello World for using the training configuration builder

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    builder = TrainingConfigBuilder().set_input_csv_filename(
        input_file).set_training_history_filename(price_history_file)

    config = builder.build_config()

    print(config)


def training_builder_custom_logic():
    """
    Example Hello World for using the training configuration builder with custom logic

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    builder = TrainingConfigBuilder().set_input_csv_filename(
        input_file).set_training_history_filename(price_history_file)

    config = builder.build_config(
        on_file_error=_error_file_not_found, check_training_format=_check_training_format,
        check_input_format=_check_input_format, on_format_error=_error_bad_csv_format)

    print(config)


def training_usage():
    """
    Example Hello World for using the training module

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    config = TrainingConfigBuilder().set_input_csv_filename(
        input_file).set_training_history_filename(price_history_file).build_config()

    configure_training(config)
    conv_dfs = train(1.0, 3.5)

    print(conv_dfs)


def training_custom_distribution():
    """
    Example Hello World for using the training module with a custom distribution

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    config = TrainingConfigBuilder().set_input_csv_filename(
        input_file).set_training_history_filename(price_history_file).build_config()

    configure_training(config)
    conv_dfs = train(1.0, dist=skewnorm)

    for df in conv_dfs:
        print(df.to_string())


if __name__ == '__main__':
    training_builder()
    training_builder_custom_logic()
    training_usage()
    training_custom_distribution()

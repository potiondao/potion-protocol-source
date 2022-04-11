"""
Usage Example code for the multi asset backtester module
"""
from potion.streamlitapp.curvegen.cg_file_io import read_training_data_from_csv
from potion.streamlitapp.multibackt.ma_file_io import read_multi_asset_curves_from_csv
from potion.backtest.multi_asset_backtester import (
    create_ma_backtester_config, MultiAssetBacktester, PathGenMethod)


def ma_backtester_hello_world():
    """
    Example Hello World for running the multi asset backtester

    Returns
    -------
    None
    """
    # Read in the input dataframes from the example files
    input_df = read_multi_asset_curves_from_csv('../../inputs/ExampleMultiAssetBacktesterInput.csv')
    training_df = read_training_data_from_csv('../../resources/examples/training.csv')

    # Same as parameters in single asset backtester
    num_paths = 300
    path_length = 730
    initial_bankroll = 1000.0

    # Specifies 10% util for each asset. In this case, input CSV has ethereum as ID 0 and
    # bitcoin as ID 1
    util_map = {
        0: 0.1,
        1: 0.1
    }

    # Configure the backtester
    config = create_ma_backtester_config(PathGenMethod.MV_STUDENT_T, num_paths, path_length,
                                         util_map, initial_bankroll)

    # Run the backtesting
    backtester = MultiAssetBacktester(config=config, curve_df=input_df,
                                      training_df=training_df)
    backtester.generate_backtesting_paths()
    backtester.evaluate_backtest_sequentially('out_log_name', backtest_id=0, num_ma_backtests=1)


if __name__ == '__main__':
    ma_backtester_hello_world()

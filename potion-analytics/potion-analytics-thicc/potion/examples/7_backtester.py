"""
Usage Example code for the single asset backtester module
"""
from potion.curve_gen.utils import build_generator_config
from potion.curve_gen.gen import configure_curve_gen, generate_curves

from potion.backtest.batch_backtester import create_backtester_config, BatchBacktester


def backtester_hello_world():
    """
    Example Hello World for running the backtester

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    # Generate the curves to backtest
    configure_curve_gen(build_generator_config(input_file, price_history_file))
    curve_df, pdf_df, training_df = generate_curves()

    # Configure the backtester
    num_paths = 30
    path_length = 50
    util = 0.3
    initial_bankroll = 1000.0

    config = create_backtester_config(num_paths, path_length, util, initial_bankroll)

    # Run the backtesting simulation
    backtester = BatchBacktester(config=config, curve_df=curve_df, training_df=training_df)
    backtester.generate_backtesting_paths()
    backtester.evaluate_backtest_sequentially('output_log_name')


if __name__ == '__main__':
    backtester_hello_world()

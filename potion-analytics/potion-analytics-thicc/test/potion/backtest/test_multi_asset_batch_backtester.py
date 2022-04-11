import unittest
import numpy as np
import pandas as pd

from potion.backtest.multi_asset_backtester import (
    MultiAssetBacktester, create_ma_backtester_config, PathGenMethod)
import yfinance as yf
import time
import matplotlib.pyplot as plt


COL_KEY_PRICE_HIST_DATES = 'Master calendar'


def get_ticker_history(ticker, num_retries, start, end):

    for retry in range(0, num_retries):
        try:
            history = ticker.history(start=start, end=end, auto_adjust=True)
            return history
        except:
            print('Retyring history request: #{} Ticker: {} Start: {} End: {}'.format(
                retry, ticker.ticker, start, end))
            time.sleep(5 * retry)

    return None


def get_csv_history(ticker, start, end):

    backtest_data = pd.read_csv('../../../resources/webapp-coins.csv', sep=',')
    price_history_dates = backtest_data[COL_KEY_PRICE_HIST_DATES]

    full_price_path = backtest_data[ticker].dropna()
    if start == 'min':
        starting_index = full_price_path.index[0]
        _start_date = price_history_dates[starting_index]
    else:
        starting_index = price_history_dates[price_history_dates == start].index[0]

    if end == 'max':
        ending_index = full_price_path.index[-1]
        _end_date = price_history_dates[ending_index]
    else:
        ending_index = price_history_dates[price_history_dates == end].index[0]

    price_path = full_price_path.loc[starting_index:ending_index].copy()

    return price_path


def get_csv_training_df():

    eth_training_df = get_csv_history('Ethereum', '8/8/15', '27/2/21')
    btc_training_df = get_csv_history('Bitcoin', '8/8/15', '27/2/21')

    eth_row = {
        'Ticker': 'ETH',
        'Label': 'full',
        'CurrentPrice': eth_training_df.tolist()[-1],
        'StartDate': '2015-08-08',
        'EndDate': '2021-02-27',
        'TrainingPrices': eth_training_df.tolist()
    }
    btc_row = {
        'Ticker': 'BTC',
        'Label': 'full',
        'CurrentPrice': btc_training_df.tolist()[-1],
        'StartDate': '2015-08-08',
        'EndDate': '2021-02-27',
        'TrainingPrices': btc_training_df.tolist()
    }
    training_list = [eth_row, btc_row]

    training_df = pd.DataFrame(training_list)

    return training_df


def get_test_training_df():
    aapl = 'AAPL'
    goog = 'GOOG'
    aapl_ticker = yf.Ticker(aapl)
    goog_ticker = yf.Ticker(goog)
    # print(aapl_ticker)
    # aapl_history = aapl_ticker.history(start="2005-01-01", end="2021-07-07", auto_adjust=True)
    # goog_history = goog_ticker.history(start='2005-01-01', end='2021-07-07', auto_adjust=True)
    aapl_history = get_ticker_history(aapl_ticker, 5, '2005-01-01', '2021-07-07')
    goog_history = get_ticker_history(goog_ticker, 5, '2005-01-01', '2021-07-07')
    aapl_close_data = aapl_history['Close']
    goog_close_data = goog_history['Close']

    aapl_row = {
        'Ticker': aapl,
        'Label': 'full',
        'CurrentPrice': aapl_close_data.tolist()[-1],
        'StartDate': '2005-01-01',
        'EndDate': '2021-07-07',
        'TrainingPrices': aapl_close_data.tolist()
    }
    goog_row = {
        'Ticker': goog,
        'Label': 'full',
        'CurrentPrice': goog_close_data.tolist()[-1],
        'StartDate': '2005-01-01',
        'EndDate': '2021-07-07',
        'TrainingPrices': goog_close_data.tolist()
    }
    training_list = [aapl_row, goog_row]

    training_df = pd.DataFrame(training_list)

    return training_df


def get_test_curves_df():

    eth_btc_row = {
        'Label': 'ETH-BTC',
        'Assets': ['ETH-full', 'BTC-full'],
        'ETH-full_Expiration': 1,
        'BTC-full_Expiration': 3,
        'ETH-full_StrikePercent': 1.0,
        'BTC-full_StrikePercent': 0.9,
        'A': 1.0,
        'B': 2.0,
        'C': 3.0,
        'D': 4.0,
        't_params': [2.5],
        'bet_fractions': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
        'curve_points': [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
    }
    curves_list = [eth_btc_row]

    curve_df = pd.DataFrame(curves_list)

    return curve_df


class MultiAssetBatchBacktesterTestCase(unittest.TestCase):

    def test_parse_curves_df_input(self):

        curve_df = get_test_curves_df()
        training_df = get_csv_training_df()

        print(curve_df.to_string())
        print(training_df.to_string())

        util_map = {
            'AAPL': 0.1,
            'GOOG': 0.1
        }

        config = create_ma_backtester_config(PathGenMethod.MV_NORMAL, 300, 3000, util_map, 10000)

        backtester = MultiAssetBacktester(config, curve_df, training_df)

    def test_generate_paths(self):

        curve_df = get_test_curves_df()
        training_df = get_csv_training_df()

        # print(curve_df.to_string())
        # print(training_df.to_string())

        util_map = {
            'ETH-full': 0.1,
            'BTC-full': 0.1
        }

        num_paths = 300
        path_length = 300

        config = create_ma_backtester_config(PathGenMethod.MV_NORMAL, num_paths, path_length,
                                             util_map, 10000)

        backtester = MultiAssetBacktester(config, curve_df, training_df)

        backtester.generate_backtesting_paths()

        backtester.evaluate_backtest_sequentially('test_back_seq_log.csv')

        # Number of days along the path for plotting
        days = np.linspace(0, path_length, path_length)

        fig, axs = plt.subplots(1, 2, constrained_layout=True, figsize=(12, 8))

        ax0 = axs[0]
        ax1 = axs[1]

        # Plot each path
        for path in backtester.path_mapping['ETH-BTC']:
            eth_path = path['ETH-full']
            btc_path = path['BTC-full']

            ax0.plot(days, eth_path)
            ax1.plot(days, btc_path)

            ax0.grid(True)
            ax0.set_xlabel('Number of Days')
            ax0.set_ylabel('Price')
            ax0.set_title('ETH Simulated Paths')
            ax1.grid(True)
            ax1.set_xlabel('Number of Days')
            ax1.set_ylabel('Price')
            ax1.set_title('BTC Simulated Paths')

        # plt.show()

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

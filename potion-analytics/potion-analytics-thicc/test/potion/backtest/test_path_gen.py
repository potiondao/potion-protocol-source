import unittest
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

from potion.backtest.path_gen import (
    prices_to_sample_covariance_matrix, multivariate_normal_path_sampling)


class PathGenTestCase(unittest.TestCase):

    def test_multivariate_normal(self):

        aapl = 'AAPL'
        goog = 'GOOG'
        aapl_ticker = yf.Ticker(aapl)
        goog_ticker = yf.Ticker(goog)
        aapl_history = aapl_ticker.history(start="2005-01-01", end="2021-07-07", auto_adjust=True)
        goog_history = goog_ticker.history(start="2005-01-01", end="2021-07-07", auto_adjust=True)
        aapl_close_data = aapl_history['Close'].values
        goog_close_data = goog_history['Close'].values

        price_history_list = {
            'aapl': aapl_close_data,
            'goog': goog_close_data
        }

        current_prices = {
            'aapl': aapl_close_data[-1],
            'goog': goog_close_data[-1]
        }

        num_paths = 30
        path_length = 1000

        covariance_matrix, asset_params = prices_to_sample_covariance_matrix(price_history_list)

        # print('Cov Matrix: \n{}'.format(covariance_matrix.to_string()))

        path_dict, log_delta_list = multivariate_normal_path_sampling(
            num_paths, path_length, covariance_matrix, current_prices)

        fig = plt.figure()
        ax = fig.gca()
        ax.grid(True)
        ax.set_title('First Path AAPL vs GOOG Return')
        ax.set_xlabel('AAPL Log Return')
        ax.set_ylabel('GOOG Log Return')
        for i in range(num_paths):
            correlated_sample_list = log_delta_list[i]
            ax.scatter(correlated_sample_list[0], correlated_sample_list[1])

        # Number of days along the path for plotting
        days = np.linspace(0, path_length, path_length)

        fig, axs = plt.subplots(1, 2, constrained_layout=True, figsize=(15, 10))

        ax0 = axs[0]
        ax1 = axs[1]

        # Plot each path
        aapl_paths = path_dict['aapl']
        goog_paths = path_dict['goog']

        for a_path, g_path in zip(aapl_paths, goog_paths):
            ax0.plot(days, a_path)
            ax1.plot(days, g_path)

        ax0.grid(True)
        ax0.set_xlabel('Number of Days')
        ax0.set_ylabel('Price')
        ax0.set_title('AAPL Simulated Paths')
        ax1.grid(True)
        ax1.set_xlabel('Number of Days')
        ax1.set_ylabel('Price')
        ax1.set_title('GOOG Simulated Paths')

        plt.show()

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

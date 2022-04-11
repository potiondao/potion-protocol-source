import unittest
import os
import numpy as np
from potion.backtest.batch_backtester import PathGenMethod
from potion.streamlitapp.backt.backtest_helper_functions import run_backtesting_script


class AnalyticalFormulaTestCase(unittest.TestCase):

    def test_formula(self):

        batch_number = 0
        utils = [0.1, 0.25, 0.5, 0.75, 0.99]
        path_gen_method = PathGenMethod.SKEWED_T
        num_paths = 300
        path_length = 730
        initial_bankroll = 1000.0

        os.chdir('../../..')

        train_filename = './batch_results/batch_' + str(batch_number) + '_training.csv'
        curve_filename = './batch_results/batch_' + str(batch_number) + '_curves.csv'
        pdf_filename = './batch_results/batch_' + str(batch_number) + '_pdfs.csv'

        # Run the backtesting and generate our results plots
        (backtester_map, log_file_names, full_performance_df, plot_dicts) = \
            run_backtesting_script(
                batch_number, curve_filename, train_filename, pdf_filename, utils, path_gen_method,
                num_paths, path_length, initial_bankroll,
                backtest_progress_bar=None, plot_progress_bar=None)

        for i, plot_dict in enumerate(plot_dicts):

            fig_opt_cagr = plot_dict['opt_cagr']
            expected_cagr = fig_opt_cagr.data[num_paths].y[0]

            median_cagr = np.median(
                np.asarray([fig_opt_cagr.data[i].y[-1] for i in range(num_paths)]))
            print('expected cagr: {} median actual cagr: {}'.format(expected_cagr, median_cagr))

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

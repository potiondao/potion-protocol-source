import unittest

import numpy as np
from numpy.testing import assert_array_almost_equal
import pandas as pd

from scipy.stats import norm

from potion.curve_gen.training.builder import TrainingConfigBuilder
from potion.curve_gen.training.fit.helpers import calc_log_returns
from potion.curve_gen.training.fit.tail_fit import (
    _sort_tail_returns, _convert_samples_to_log_deltas, _adjust_deltas_to_same_size,
    fit_samples, perform_linear_replication, calculate_expected_next_extreme,
    fit_samples_mle)
from test.potion.curve_gen.plot_help import plot_tail_fits
# import matplotlib.pyplot as plt


class TailFitterTestCase(unittest.TestCase):

    def test_sort_tail_returns(self):

        data = {'Return': [2.0, 1.0, 5.0, -1.0, -7.0, -2.0]}
        samples = pd.DataFrame(data)

        sorted_left_tail = _sort_tail_returns(samples, left_tail=True)
        sorted_right_tail = _sort_tail_returns(samples, left_tail=False)

        self.assertEqual(-7.0, sorted_left_tail.Return.values[0])
        self.assertEqual(-2.0, sorted_left_tail.Return.values[1])
        self.assertEqual(-1.0, sorted_left_tail.Return.values[2])
        self.assertEqual(5.0, sorted_right_tail.Return.values[0])
        self.assertEqual(2.0, sorted_right_tail.Return.values[1])
        self.assertEqual(1.0, sorted_right_tail.Return.values[2])

    def test_convert_samples_to_log_deltas(self):

        data = {'Return': [3.0, 2.0, 1.0, -1.0, -2.0, -3.0]}
        samples = pd.DataFrame(data)

        sorted_left_tail = _sort_tail_returns(samples, left_tail=True)
        sorted_right_tail = _sort_tail_returns(samples, left_tail=False)

        left_log_deltas = _convert_samples_to_log_deltas(
            sorted_left_tail, 0.0, 2.5, left_tail=True)
        right_log_deltas = _convert_samples_to_log_deltas(
            sorted_right_tail, 0.0, 2.5, left_tail=False)

        self.assertAlmostEqual(1.09861229, left_log_deltas[0], 6)
        self.assertAlmostEqual(1.09861229, right_log_deltas[0], 6)

        left_log_deltas = _convert_samples_to_log_deltas(
            sorted_left_tail, 1.0, 3.5, left_tail=True)
        right_log_deltas = _convert_samples_to_log_deltas(
            sorted_right_tail, 1.0, 1.5, left_tail=False)

        self.assertAlmostEqual(1.38629436, left_log_deltas[0], 6)
        self.assertAlmostEqual(0.69314718, right_log_deltas[0], 6)

        left_log_deltas = _convert_samples_to_log_deltas(
            sorted_left_tail, -1.0, 1.5, left_tail=True)
        right_log_deltas = _convert_samples_to_log_deltas(
            sorted_right_tail, -1.0, 3.5, left_tail=False)

        self.assertAlmostEqual(0.69314718, left_log_deltas[0], 6)
        self.assertAlmostEqual(1.38629436, right_log_deltas[0], 6)

    def test_adjust_deltas_to_same_size(self):

        data = {'Return': [3.0, 2.0, 1.0, -1.0, -2.0, -3.0]}
        samples = pd.DataFrame(data)

        sorted_left_tail = _sort_tail_returns(samples, left_tail=True)
        sorted_right_tail = _sort_tail_returns(samples, left_tail=False)

        left_log_deltas = _convert_samples_to_log_deltas(
            sorted_left_tail, 1.0, 1.5, left_tail=True)
        right_log_deltas = _convert_samples_to_log_deltas(
            sorted_right_tail, 1.0, 1.5, left_tail=False)

        left_log_deltas, right_log_deltas = _adjust_deltas_to_same_size(
            left_log_deltas, right_log_deltas)

        self.assertEqual(len(left_log_deltas), len(right_log_deltas))

    def test_perform_linear_replication(self):

        b = -0.1
        m = 3.0

        log_rank = np.log(np.linspace(1, 10, 10))

        self.assertEqual(len(log_rank), len(perform_linear_replication(log_rank, b, m)))
        assert_array_almost_equal((log_rank - b) / m, perform_linear_replication(log_rank, b, m))

        b = 0.1
        m = 3.0

        self.assertEqual(len(log_rank), len(perform_linear_replication(log_rank, b, m)))
        assert_array_almost_equal((log_rank - b) / m, perform_linear_replication(log_rank, b, m))

        b = -0.1
        m = -3.0

        self.assertEqual(len(log_rank), len(perform_linear_replication(log_rank, b, m)))
        assert_array_almost_equal((log_rank - b) / m, perform_linear_replication(log_rank, b, m))

        b = 0.1
        m = -3.0

        self.assertEqual(len(log_rank), len(perform_linear_replication(log_rank, b, m)))
        assert_array_almost_equal((log_rank - b) / m, perform_linear_replication(log_rank, b, m))

        b = 0.0
        m = 0.0

        self.assertEqual(len(log_rank), len(perform_linear_replication(log_rank, b, m)))
        assert_array_almost_equal(np.full_like(log_rank, np.inf),
                                  perform_linear_replication(log_rank, b, m))

    def test_calculate_expected_next_extreme(self):

        current_worst = -2.0
        current_best = 2.0
        left_m = -2.0
        right_m = -2.0

        next_worst = calculate_expected_next_extreme(current_worst, left_m)
        next_best = calculate_expected_next_extreme(current_best, right_m)

        self.assertEqual(4.0, next_best)
        self.assertEqual(-4.0, next_worst)

    def test_fit_samples(self):

        builder = TrainingConfigBuilder()
        builder.set_training_history_filename('../../../../../resources/webapp-coins.csv')
        builder.set_input_csv_filename('../../../../../inputs/ExampleCurveGenInputSingle.csv')
        cfg = builder.build_config()

        return_df = calc_log_returns(cfg.training_df['bitcoin'])

        dist_params, fit_dict = fit_samples(
            return_df, 1.0, 2.5, left_threshold=0.1, right_threshold=0.1)

        log_rank = fit_dict['log_rank']
        extreme_values = fit_dict['evs']
        left_fit_stats = fit_dict['left_stats']
        right_fit_stats = fit_dict['right_stats']

        self.assertEqual(6, len(dist_params))
        assert_array_almost_equal(np.linspace(1, len(log_rank), len(log_rank)), np.exp(log_rank), 0)
        self.assertEqual(return_df.Return.min(), extreme_values[0])
        self.assertEqual(return_df.Return.max(), extreme_values[1])
        self.assertAlmostEqual(1.0, left_fit_stats['r'] ** 2.0, 1)
        self.assertAlmostEqual(1.0, right_fit_stats['r'] ** 2.0, 1)
        self.assertAlmostEqual(0.0, left_fit_stats['p'])
        self.assertAlmostEqual(0.0, right_fit_stats['p'])
        self.assertAlmostEqual(0.0, left_fit_stats['std_err'], 0)
        self.assertAlmostEqual(0.0, right_fit_stats['std_err'], 0)

        dist_params, fit_dict = fit_samples(return_df, dist=norm)

        self.assertEqual(4, len(dist_params))

        plot_tail_fits('ETH', dist_params, fit_dict)
        # plt.show()

    def test_fit_samples_mle(self):

        builder = TrainingConfigBuilder()
        builder.set_training_history_filename('../../../../../resources/webapp-coins.csv')
        builder.set_input_csv_filename('../../../../../inputs/ExampleCurveGenInputSingle.csv')
        cfg = builder.build_config()

        return_df = calc_log_returns(cfg.training_df['bitcoin'])

        dist_params, fit_dict = fit_samples_mle(
            return_df, 1.0, 2.5, left_threshold=0.1, right_threshold=0.1)

        self.assertEqual(6, len(dist_params))

        dist_params, fit_dict = fit_samples_mle(return_df, dist=norm)

        self.assertEqual(4, len(dist_params))

    def test_compare(self):

        builder = TrainingConfigBuilder()
        builder.set_training_history_filename('../../../../../resources/webapp-coins.csv')
        builder.set_input_csv_filename('../../../../../inputs/ExampleCurveGenInputSingle.csv')
        cfg = builder.build_config()

        return_df = calc_log_returns(cfg.training_df['bitcoin'])

        dist_params_lin, fit_dict_lin = fit_samples(
            return_df, 1.0, 2.5, left_threshold=0.1, right_threshold=0.1)

        self.assertEqual(6, len(dist_params_lin))

        lin_log_rank = fit_dict_lin['log_rank']
        left_b = fit_dict_lin['left_b']
        left_m = -dist_params_lin[-2]
        right_b = fit_dict_lin['right_b']
        right_m = -dist_params_lin[-1]

        dist_params_lin[-2] = left_m
        dist_params_lin[-1] = right_m

        left_rep = perform_linear_replication(
            lin_log_rank, left_b, left_m)
        right_rep = perform_linear_replication(
            lin_log_rank, right_b, right_m)

        fig, ax = plot_tail_fits('ETH', dist_params_lin, fit_dict_lin)
        dist_params_lin[-2] = -left_m
        dist_params_lin[-1] = -right_m

        dist_params_mle, fit_dict_mle = fit_samples_mle(
            return_df, 1.0, 2.5, left_threshold=0.1, right_threshold=0.1)

        ax.plot(left_rep[-1], lin_log_rank[-1], 'ko')
        ax.plot(right_rep[-1], lin_log_rank[-1], 'ko')

        left_m_mle = -dist_params_mle[-2]
        right_m_mle = -dist_params_mle[-1]

        left_rep = perform_linear_replication(
            lin_log_rank, lin_log_rank[-1] - left_m_mle * left_rep[-1], left_m_mle)
        right_rep = perform_linear_replication(
            lin_log_rank, lin_log_rank[-1] - right_m_mle * right_rep[-1], right_m_mle)

        ax.plot(left_rep, fit_dict_lin['log_rank'], 'b-.')
        ax.plot(right_rep, fit_dict_lin['log_rank'], 'g-.')

        print('linear estimation: ', dist_params_lin)
        print('mle: ', dist_params_mle)

        self.assertAlmostEqual(dist_params_lin[0], dist_params_mle[0], 5)
        self.assertAlmostEqual(dist_params_lin[1], dist_params_mle[1], 5)
        self.assertAlmostEqual(dist_params_lin[2], dist_params_mle[2], 5)
        self.assertAlmostEqual(dist_params_lin[3], dist_params_mle[3], 5)

        # plt.show()


if __name__ == '__main__':
    unittest.main()

import unittest
import numpy as np
import matplotlib.pyplot as plt
from test.potion.curve_gen.plot_help import histogram_plot
from potion.curve_gen.training.fit.tail_fit import fit_samples, fit_samples_mle
from potion.curve_gen.training.distributions.skewed_students_t import skewed_t

from potion.curve_gen.training.distributions.piecewise import piecewise


class PiecewiseDistributionTestCase(unittest.TestCase):

    def test_fit(self):

        skew = 1.0
        alpha = 2.5
        sample_data = skewed_t.rvs(skew, alpha, loc=0.0, scale=0.03, size=20000)

        dist_params = piecewise.fit(sample_data, 1.0, 2.5, dist=skewed_t, fit_function=fit_samples,
                                    left_threshold=0.01, right_threshold=0.01)

        self.assertAlmostEqual(skew, dist_params[0], 1)
        self.assertAlmostEqual(alpha, dist_params[1], 0)
        self.assertAlmostEqual(0.0, dist_params[4], 1)
        self.assertAlmostEqual(0.03, dist_params[5], 1)

    def test_pdf(self):

        loc = 0.0
        scale = 0.02
        skew = 1.0
        alpha = 2.5
        left_thr = 0.1
        right_thr = 0.1
        x_min = -0.5
        x_max = 0.5
        num_pdf_points = 10000
        num_samples = 20000
        x_vals = np.linspace(x_min, x_max, num_pdf_points)
        sample_data = skewed_t.rvs(skew, alpha, loc=loc, scale=scale, size=num_samples)

        dist_params = piecewise.fit(
            sample_data, skew, alpha, dist=skewed_t, fit_function=fit_samples,
            left_threshold=left_thr, right_threshold=right_thr)
        dist_params_mle = piecewise.fit(
            sample_data, skew, alpha, dist=skewed_t,
            fit_function=fit_samples_mle, left_threshold=left_thr, right_threshold=right_thr)

        param_dict = {
            'center_dist': skewed_t,
            'center_dist_params': dist_params[:-4],
            'left_threshold': left_thr,
            'right_threshold': right_thr,
            'left_alpha': dist_params[-4],
            'right_alpha': dist_params[-3],
            'loc': dist_params[-2],
            'scale': dist_params[-1]
        }

        param_dict_mle = {
            'center_dist': skewed_t,
            'center_dist_params': dist_params_mle[:-4],
            'left_threshold': left_thr,
            'right_threshold': right_thr,
            'left_alpha': dist_params_mle[-4],
            'right_alpha': dist_params_mle[-3],
            'loc': dist_params_mle[-2],
            'scale': dist_params_mle[-1]
        }

        output = piecewise.pdf(x_vals, param_dict)
        output_mle = piecewise.pdf(x_vals, param_dict_mle)

        # print('probability: ', np.sum(np.multiply(np.diff(x_vals), output[:-1])))

        t_params = skewed_t.fit(
            sample_data, skew, alpha, loc=dist_params[-2], scale=dist_params[-1])

        fig, ax, bin_counts, bin_edges = histogram_plot(
            sample_data, 't', 'return', 'counts', num_pdf_points, x_min, x_max)

        # print(bin_edges)
        # log_dens = semi.kde.score_samples(bin_edges[:, np.newaxis])
        # ax.plot(bin_edges, np.exp(log_dens), color='orange')

        ax.plot(x_vals, output, color='red')
        ax.plot(x_vals, output_mle, color='green')
        ax.plot(x_vals, skewed_t.pdf(x_vals, t_params[0], t_params[1],
                                     loc=t_params[-2], scale=t_params[-1]))
        ax.grid(True)

        # plt.show()
        self.assertEqual(len(x_vals), len(output))
        self.assertAlmostEqual(1.0, np.sum(np.multiply(np.diff(x_vals), output[:-1])), 0)

    def test_cdf(self):

        loc = 0.0
        scale = 0.02
        skew = 1.0
        alpha = 2.5
        left_thr = 0.1
        right_thr = 0.1
        x_min = -0.5
        x_max = 0.5
        num_pdf_points = 10000
        num_samples = 20000
        x_vals = np.linspace(x_min, x_max, num_pdf_points)
        sample_data = skewed_t.rvs(skew, alpha, loc=loc, scale=scale, size=num_samples)

        dist_params = piecewise.fit(
            sample_data, skew, alpha, dist=skewed_t, fit_function=fit_samples,
            left_threshold=left_thr, right_threshold=right_thr)

        param_dict = {
            'center_dist': skewed_t,
            'center_dist_params': dist_params[:-4],
            'left_threshold': left_thr,
            'right_threshold': right_thr,
            'left_alpha': dist_params[-4],
            'right_alpha': dist_params[-3],
            'loc': dist_params[-2],
            'scale': dist_params[-1]
        }

        cdf_y = piecewise.cdf(x_vals, param_dict)

        fig = plt.figure()
        ax = fig.gca()
        ax.plot(x_vals, cdf_y)
        ax.grid(True)

        # plt.show()
        self.assertEqual(len(x_vals), len(cdf_y))

    def test_calculate_inverse_cdf(self):

        loc = 0.0
        scale = 0.02
        skew = 1.0
        alpha = 2.5
        left_thr = 0.1
        right_thr = 0.1
        x_min = -0.5
        x_max = 0.5
        num_pdf_points = 10000
        num_samples = 20000
        x_vals = np.linspace(x_min, x_max, num_pdf_points)
        sample_data = skewed_t.rvs(skew, alpha, loc=loc, scale=scale, size=num_samples)

        dist_params = piecewise.fit(
            sample_data, skew, alpha, dist=skewed_t, fit_function=fit_samples,
            left_threshold=left_thr, right_threshold=right_thr)

        param_dict = {
            'center_dist': skewed_t,
            'center_dist_params': dist_params[:-4],
            'left_threshold': left_thr,
            'right_threshold': right_thr,
            'left_alpha': dist_params[-4],
            'right_alpha': dist_params[-3],
            'loc': dist_params[-2],
            'scale': dist_params[-1]
        }

        fig = plt.figure()
        ax = fig.gca()
        inv_x_values, inv_y_values = piecewise._calculate_inverse_cdf(x_vals, param_dict)
        ax.grid(True)
        ax.plot(inv_x_values, inv_y_values)

        # plt.show()
        self.assertEqual(len(inv_x_values), len(inv_y_values))

    def test_rvs(self):

        loc = 0.0
        scale = 0.02
        skew = 1.0
        alpha = 2.5
        left_thr = 0.1
        right_thr = 0.1
        x_min = -0.5
        x_max = 0.5
        num_pdf_points = 10000
        num_samples = 20000
        x_vals = np.linspace(x_min, x_max, num_pdf_points)
        sample_data = skewed_t.rvs(skew, alpha, loc=loc, scale=scale, size=num_samples)

        dist_params = piecewise.fit(
            sample_data, skew, alpha, dist=skewed_t, fit_function=fit_samples,
            left_threshold=left_thr, right_threshold=right_thr)

        param_dict = {
            'center_dist': skewed_t,
            'center_dist_params': dist_params[:-4],
            'left_threshold': left_thr,
            'right_threshold': right_thr,
            'left_alpha': dist_params[-4],
            'right_alpha': dist_params[-3],
            'loc': dist_params[-2],
            'scale': dist_params[-1]
        }

        num_random_samples = 20000
        pdf_y = piecewise.pdf(x_vals, param_dict)
        random_returns = piecewise.rvs(param_dict, size=num_random_samples)

        fig, ax, bin_counts, bin_edges = histogram_plot(random_returns, 'gen_samples',
                                                        'return', 'counts', 2000, x_min, x_max)
        ax.plot(x_vals, pdf_y, color='red')

        # plt.show()
        self.assertEqual(num_random_samples, len(random_returns))


if __name__ == '__main__':
    unittest.main()

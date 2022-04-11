
import unittest
import numpy as np
import time
import matplotlib.pyplot as plt
from potion.curve_gen.training.distributions.skewed_students_t import SkewedT
from potion.curve_gen.kelly import trapezoidal_rule
from potion.curve_gen.convolution.helpers import convolve_self_n, bind_pdf_params
from potion.curve_gen.domain_transformation import (transform_pdf_using_optimize,
                                                    log_to_price_sample_points)


class SkewedTTestCase(unittest.TestCase):

    def test_skewed_t(self):

        print('Testing skewed_t pdf')

        min_x = -0.7754946
        max_x = 17.41241
        delta = 0.1
        num_pts = int((max_x - min_x) / delta) + 1
        x = np.linspace(min_x, max_x, num_pts)

        shape = 3.054333
        nu = 3.218173
        location = 1.025116
        scale = 0.9967822
        # scale = 1.0

        skewed_t = SkewedT()

        t0 = time.time()
        y_pdf = skewed_t.pdf(x, shape, nu, loc=location, scale=scale)
        # y_pdf = skewed_t.pdf(x, shape, nu)
        t1 = time.time()

        print('Calculation time (s): {}'.format(t1 - t0))

        prob_bins = np.full_like(x, 0.0)
        for i in range(x.size - 1):
            point = x[i]
            next_point = x[i + 1]
            prob = y_pdf[i]
            next_prob = y_pdf[i + 1]
            prob_bins[i + 1] = trapezoidal_rule(point, prob, next_point, next_prob)
        print('Sum: {}'.format(np.sum(prob_bins)))

        # Check the skewed T matches skewed normal and student's T for special cases
        plt.figure()
        plt.plot(x, y_pdf)
        # plt.plot(x, t.pdf(x, nu, loc=location, scale=scale))
        # plt.plot(x, skewnorm.pdf(x, 1.2, loc=location, scale=scale))
        plt.grid(True)
        # plt.show()

        self.assertEqual(True, True)

    def test_rvs(self):

        skew = 1.2
        nu = 2.5
        location = 0.0
        scale = 0.01
        num_points = 20000

        # skew_inv = 1.0 / skew
        # weighting = skew / (skew + skew_inv)
        #
        # print(weighting + (1 - weighting))
        # print('weight: {}'.format(weighting))
        # print('min: {} max: {} max2: {}'.format(-weighting, 2*weighting, 1-weighting))
        # z = uniform.rvs(loc=-weighting, scale=1.0, size=20000)
        #
        # bins = np.linspace(-1.0, 1.5, 200)
        # fig = plt.figure()
        # ax = fig.gca()
        # ax.hist(z, bins=bins, density=True, alpha=0.9)
        # plt.show()

        x = np.linspace(-5, 5, num_points)

        skewed_t = SkewedT()
        log_deltas = skewed_t.rvs(skew, nu, loc=location, scale=scale, size=num_points)
        log_deltas2 = skewed_t.rvs(skew - 0.4, nu, loc=location, scale=scale, size=num_points)
        y_pdf = skewed_t.pdf(x, skew, nu, loc=location, scale=scale)
        y_pdf2 = skewed_t.pdf(x, skew - 0.4, nu, loc=location, scale=scale)

        bins = np.linspace(-5.0, 5.0, num_points)

        fig = plt.figure()
        ax = fig.gca()
        ax.plot(x, y_pdf, color='blue')
        ax.plot(x, y_pdf2, color='red')
        ax.set_xlim([-0.5, 0.5])
        ax.grid(True)
        ax.hist(log_deltas, bins=bins, density=True, alpha=0.5, color='blue')
        ax.hist(log_deltas2, bins=bins, density=True, alpha=0.5, color='red')

        current_price = 200
        possible_prices = log_to_price_sample_points(x, current_price)
        y_price = transform_pdf_using_optimize(x, y_pdf, possible_prices)

        n_paths = 200_000
        path_length = 10
        path_list = []
        price_over_paths = np.zeros(n_paths)
        # print(price_over_paths)
        for i in range(n_paths):

            log_deltas = skewed_t.rvs(skew, nu, loc=location, scale=scale, size=path_length-1)

            path = [current_price]
            last_price = current_price
            price = 0
            for log_delta in log_deltas:

                price = log_to_price_sample_points(log_delta, last_price)
                path.append(price)
                last_price = price

            price_over_paths[i] = price
            path_list.append(path)

        # print(path_list)
        # print(price_over_paths)

        dist_x = bind_pdf_params(skewed_t, location, scale, skew, nu)
        log_pdf_list = convolve_self_n(dist_x, x, path_length-2)

        price_pdf_list = []
        for log_pdf in log_pdf_list:
            price_pdf = transform_pdf_using_optimize(x, log_pdf, possible_prices)
            # price_pdf = log_pdf[pos_index]
            price_pdf_list.append(price_pdf)

        bins = np.linspace(100, 300, 2000)
        fig = plt.figure()
        ax = fig.gca()
        ax.plot(possible_prices, price_pdf_list[-1])
        ax.set_xlim([100.0, 300.0])
        ax.grid(True)
        ax.hist(price_over_paths, bins=bins, density=True, alpha=0.9)

        plt.show()

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()

import unittest
import numpy as np

from scipy.stats import norm, expon

from potion.curve_gen.domain_transformation import log_to_price_sample_points
from potion.curve_gen.convolution.builder import ConvolutionConfigBuilder


class ConvolutionBuilderTestCase(unittest.TestCase):

    def test_init(self):
        builder = ConvolutionConfigBuilder()

        self.assertEqual(1, builder.num_times_to_conv)
        self.assertEqual(norm, builder.dist)
        self.assertEqual([], builder.dist_params)
        self.assertEqual(-5, builder.min_x)
        self.assertEqual(5, builder.max_x)
        self.assertEqual(20001, builder.points_in_pdf)
        self.assertEqual(False, builder.log_only)

    def test_set_num_times_to_convolve(self):
        builder = ConvolutionConfigBuilder()

        builder.set_num_times_to_convolve(5)

        self.assertEqual(5, builder.num_times_to_conv)

    def test_set_distribution(self):
        builder = ConvolutionConfigBuilder()

        builder.set_distribution(expon)

        self.assertEqual(expon, builder.dist)

    def test_set_distribution_params(self):
        builder = ConvolutionConfigBuilder()

        builder.set_distribution_params([0.0, 1.0])

        self.assertEqual([0.0, 1.0], builder.dist_params)

    def test_set_min_x(self):
        builder = ConvolutionConfigBuilder()

        builder.set_min_x(-6.0)

        self.assertEqual(-6.0, builder.min_x)

    def test_set_max_x(self):
        builder = ConvolutionConfigBuilder()

        builder.set_max_x(6.0)

        self.assertEqual(6.0, builder.max_x)

    def test_set_points_in_pdf(self):
        builder = ConvolutionConfigBuilder()

        builder.set_points_in_pdf(30001)

        self.assertEqual(30001, builder.points_in_pdf)

    def test_set_log_only(self):
        builder = ConvolutionConfigBuilder()

        builder.set_log_only(True)

        self.assertEqual(True, builder.log_only)

    def test_build_config(self):
        builder = ConvolutionConfigBuilder()

        config = builder.set_min_x(-5.0).set_max_x(
            5.0).set_points_in_pdf(20001).set_log_only(
            False).set_num_times_to_convolve(3).build_config()

        self.assertEqual(3, config.num_times_to_conv)
        self.assertEqual(20001, config.points_in_pdf)
        self.assertEqual(False, config.log_only)
        self.assertEqual([], config.dist_params)
        self.assertEqual(norm, config.dist)
        np.testing.assert_almost_equal(np.linspace(-5.0, 5.0, 20001),
                                       config.log_x, 5)
        np.testing.assert_almost_equal(log_to_price_sample_points(
            np.linspace(-5.0, 5.0, 20001), 1.0),
            config.x, 5)


if __name__ == '__main__':
    unittest.main()

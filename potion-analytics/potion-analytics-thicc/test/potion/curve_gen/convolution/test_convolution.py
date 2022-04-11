import unittest

import numpy as np
from scipy.stats import norm

from potion.curve_gen.domain_transformation import transform_pdf_using_optimize, transform_pdf_rough
from potion.curve_gen.convolution.builder import ConvolutionConfigBuilder
from potion.curve_gen.convolution.convolution import (LogDomainConvolver, configure_convolution,
                                                      run_convolution, get_pdf_arrays)


class ConvolutionTestCase(unittest.TestCase):

    def test_init_log_domain_convolver(self):

        builder = ConvolutionConfigBuilder()

        builder.set_num_times_to_convolve(6).set_min_x(-6.0).set_max_x(6.0).set_distribution_params(
            [0, 1]).set_distribution(norm).set_points_in_pdf(30001)

        conv = LogDomainConvolver(builder.build_config())

        self.assertEqual(6, conv.config.num_times_to_conv)
        self.assertEqual(-6.0, np.min(conv.config.log_x))
        self.assertEqual(6.0, np.max(conv.config.log_x))
        self.assertEqual([0, 1], conv.config.dist_params)
        self.assertEqual(norm, conv.config.dist)
        self.assertEqual(30001, conv.config.points_in_pdf)
        self.assertEqual(transform_pdf_using_optimize, conv.transform_pdf_func)
        self.assertIsNone(conv.log_pdf_list)
        self.assertIsNone(conv.price_pdf_list)

    def test_configure_log_domain_convolver(self):

        builder = ConvolutionConfigBuilder()

        builder.set_num_times_to_convolve(6).set_min_x(-6.0).set_max_x(6.0).set_distribution_params(
            [0, 1]).set_distribution(norm).set_points_in_pdf(30001)

        conv = LogDomainConvolver(ConvolutionConfigBuilder().build_config())

        conv.configure(builder.build_config())

        self.assertEqual(6, conv.config.num_times_to_conv)
        self.assertEqual(-6.0, np.min(conv.config.log_x))
        self.assertEqual(6.0, np.max(conv.config.log_x))
        self.assertEqual([0, 1], conv.config.dist_params)
        self.assertEqual(norm, conv.config.dist)
        self.assertEqual(30001, conv.config.points_in_pdf)

    def test_set_pdf_transform_func_log_domain_convolver(self):

        conv = LogDomainConvolver(ConvolutionConfigBuilder().build_config())

        conv._set_pdf_transform_func(transform_pdf_rough)

        self.assertEqual(transform_pdf_rough, conv.transform_pdf_func)

    def test_create_log_pdfs_log_domain_convolver(self):

        builder = ConvolutionConfigBuilder()

        builder.set_num_times_to_convolve(2).set_min_x(-5.0).set_max_x(5.0).set_distribution_params(
            [0, 1]).set_distribution(norm.pdf).set_points_in_pdf(20001)

        conv = LogDomainConvolver(builder.build_config())

        conv._create_log_pdfs()

        self.assertEqual(3, len(conv.log_pdf_list))
        self.assertEqual(20001, len(conv.log_pdf_list[0]))
        self.assertEqual(20001, len(conv.log_pdf_list[1]))
        self.assertEqual(20001, len(conv.log_pdf_list[2]))

    def test_create_price_pdfs_log_domain_convolver(self):

        builder = ConvolutionConfigBuilder()

        builder.set_num_times_to_convolve(2).set_min_x(-5.0).set_max_x(5.0).set_distribution_params(
            [0, 1]).set_distribution(norm.pdf).set_points_in_pdf(20001).set_log_only(True)

        conv = LogDomainConvolver(builder.build_config())

        conv._set_pdf_transform_func(transform_pdf_rough)
        conv._create_log_pdfs()
        conv._create_price_pdfs()

        self.assertIsNone(conv.price_pdf_list)

        builder.set_log_only(False)

        conv.configure(builder.build_config())

        conv._create_log_pdfs()
        conv._create_price_pdfs()

        self.assertEqual(3, len(conv.price_pdf_list))
        self.assertEqual(20001, len(conv.price_pdf_list[0]))
        self.assertEqual(20001, len(conv.price_pdf_list[1]))
        self.assertEqual(20001, len(conv.price_pdf_list[2]))

    def test_run_convolution_log_domain_convolver(self):

        builder = ConvolutionConfigBuilder()

        builder.set_num_times_to_convolve(2).set_min_x(-5.0).set_max_x(5.0).set_distribution_params(
            [0, 1]).set_distribution(norm.pdf).set_points_in_pdf(20001).set_log_only(True)

        conv = LogDomainConvolver(builder.build_config())

        conv.run_convolution(transform=transform_pdf_rough)

        self.assertIsNone(conv.price_pdf_list)

        builder.set_log_only(False)

        conv.configure(builder.build_config())

        conv.run_convolution(transform=transform_pdf_rough)

        self.assertEqual(3, len(conv.price_pdf_list))
        self.assertEqual(20001, len(conv.price_pdf_list[0]))
        self.assertEqual(20001, len(conv.price_pdf_list[1]))
        self.assertEqual(20001, len(conv.price_pdf_list[2]))

    def test_get_pdf_arrays_log_domain_convolver(self):

        builder = ConvolutionConfigBuilder()

        builder.set_num_times_to_convolve(2).set_min_x(-5.0).set_max_x(5.0).set_distribution_params(
            [0, 1]).set_distribution(norm.pdf).set_points_in_pdf(20001).set_log_only(True)

        conv = LogDomainConvolver(builder.build_config())

        conv.run_convolution(transform=transform_pdf_rough)

        x_values, y_values = conv.get_pdf_arrays()

        self.assertEqual(20001, len(x_values))
        self.assertEqual(20001, len(y_values))
        self.assertEqual(-5.0, np.min(x_values))
        self.assertEqual(5.0, np.max(x_values))

        builder.set_log_only(False)

        conv.configure(builder.build_config())

        conv.run_convolution(transform=transform_pdf_rough)

        x_values, y_values = conv.get_pdf_arrays()

        self.assertEqual(20001, len(x_values))
        self.assertEqual(20001, len(y_values))

    def test_prebind_methods_log_domain_convolver(self):

        builder = ConvolutionConfigBuilder()

        builder.set_num_times_to_convolve(2).set_min_x(-5.0).set_max_x(5.0).set_distribution_params(
            [0, 1]).set_distribution(norm.pdf).set_points_in_pdf(20001).set_log_only(True)

        configure_convolution(builder.build_config())

        run_convolution(transform=transform_pdf_rough)

        x_values, y_values = get_pdf_arrays(0)

        self.assertEqual(20001, len(x_values))
        self.assertEqual(20001, len(y_values))
        self.assertEqual(-5.0, np.min(x_values))
        self.assertEqual(5.0, np.max(x_values))

        builder.set_log_only(False)

        configure_convolution(builder.build_config())

        run_convolution(transform=transform_pdf_rough)

        x_values, y_values = get_pdf_arrays(0)

        self.assertEqual(20001, len(x_values))
        self.assertEqual(20001, len(y_values))


if __name__ == '__main__':
    unittest.main()

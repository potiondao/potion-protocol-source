"""
Usage Example code for the convolution module
"""
from scipy.stats import norm
from potion.curve_gen.convolution.builder import ConvolutionConfigBuilder
from potion.curve_gen.convolution.convolution import (
    configure_convolution, run_convolution, get_pdf_arrays)


def conv_builder():
    """
    Example Hello World for using the convolution configuration builder

    Returns
    -------
    None
    """
    builder = ConvolutionConfigBuilder()

    config = builder.build_config()

    print(config)


def conv_builder_custom():
    """
    Example Hello World for using the convolution configuration builder with custom logic

    Returns
    -------
    None
    """
    config = ConvolutionConfigBuilder().set_num_times_to_convolve(30).set_log_only(
            False).set_points_in_pdf(30001).set_distribution(
            norm(loc=0.0, scale=1.0).pdf).build_config()

    print(config)


def conv_usage():
    """
    Example Hello World for using the convolution module

    Returns
    -------
    None
    """
    config = ConvolutionConfigBuilder().build_config()

    configure_convolution(config)
    run_convolution()

    pdf_x, pdf_y_list = get_pdf_arrays()

    for pdf_y in pdf_y_list:
        print('x: ', pdf_x, '\ny: ', pdf_y)


if __name__ == '__main__':
    conv_builder()
    conv_builder_custom()
    conv_usage()

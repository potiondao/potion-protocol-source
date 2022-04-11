"""
Usage Example code for the curve fitting module
"""
import numpy as np
from potion.curve_gen.kelly_fit.builder import FitConfigBuilder
from potion.curve_gen.kelly_fit.kelly_fit import configure_fit, fit_kelly_curve, fit_function_table


def fit_builder():
    """
    Example Hello World for using the fit configuration builder

    Returns
    -------
    None
    """
    config = FitConfigBuilder().set_fit_type('COSH').build_config()

    print(config)


def fit_usage():
    """
    Example Hello World for using the fit module

    Returns
    -------
    None
    """
    config = FitConfigBuilder().set_fit_type('COSH').build_config()

    configure_fit(config)
    [a, b, c, d] = fit_kelly_curve(np.linspace(0.0, 0.9999, 50), np.linspace(0.0, 0.9999, 50))

    print(a, b, c, d)


def fit_usage_custom():
    """
    Example Hello World for using the fit module with a custom fit function

    Returns
    -------
    None
    """
    config = FitConfigBuilder().set_fit_type('my_custom_function').build_config()

    fit_function_table['my_custom_function'] = lambda x, y, **kwargs: [1.0, 2.0, 3.0, 4.0]

    configure_fit(config)
    [a, b, c, d] = fit_kelly_curve(np.linspace(0.0, 0.9999, 50), np.linspace(0.0, 0.9999, 50))

    print(a, b, c, d)


if __name__ == '__main__':
    fit_builder()
    fit_usage()
    fit_usage_custom()


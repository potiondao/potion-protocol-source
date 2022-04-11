"""
Usage Example code for the Curve Generator module
"""
import numpy as np
from scipy.stats import norm, skewnorm

from potion.curve_gen.utils import build_generator_config
from potion.curve_gen.builder import GeneratorConfigBuilder
from potion.curve_gen.training.builder import TrainingConfigBuilder
from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder
from potion.curve_gen.kelly_fit.builder import FitConfigBuilder
from potion.curve_gen.gen import configure_curve_gen, generate_curves, Generator
from potion.curve_gen.utils import make_payoff_dict, add_leg_to_dict
from potion.curve_gen.convolution.convolution import get_pdf_arrays
from potion.curve_gen.analysis.plot import (pdf_and_payout_sweep, kelly_growth_sweep,
                                            kelly_derivative_sweep, plot_curve, show)


def generator_hello_world_func():
    """
    Example Hello World for generating curves. Functional Style

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    configure_curve_gen(build_generator_config(input_file, price_history_file))
    curve_df, pdf_df, training_df = generate_curves()

    print(curve_df.to_string())
    print(training_df.to_string())
    print(pdf_df.to_string())


def generator_hello_world_oo():
    """
    Example Hello World for generating curves. Object Oriented Style

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    gen = Generator()
    gen.configure_curve_gen(build_generator_config(input_file, price_history_file))
    curve_df, pdf_df, training_df = gen.generate_curves()

    print(curve_df.to_string())
    print(training_df.to_string())
    print(pdf_df.to_string())


def generator_normal_dist():
    """
    Example Hello World for generating curves with a normal distribution

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    configure_curve_gen(build_generator_config(input_file, price_history_file))
    curve_df, pdf_df, training_df = generate_curves(initial_guess=(), dist=norm)

    print(curve_df.to_string())
    print(training_df.to_string())
    print(pdf_df.to_string())


def generator_skewed_normal_dist():
    """
    Example Hello World for generating curves with a skewed normal distribution

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    configure_curve_gen(build_generator_config(input_file, price_history_file))
    curve_df, pdf_df, training_df = generate_curves(initial_guess=(1.0,), dist=skewnorm)

    print(curve_df.to_string())
    print(training_df.to_string())
    print(pdf_df.to_string())


def generator_long_call():
    """
    Example Hello World for generating curves for a long call

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    payoff_dict = make_payoff_dict(call_or_put='call', direction='long')

    configure_curve_gen(build_generator_config(
        input_file, price_history_file, payoff_dict=payoff_dict))
    curve_df, pdf_df, training_df = generate_curves(payoff_dict=payoff_dict)

    pdf_x, pdfs_y = get_pdf_arrays()

    min_prem = -0.01
    max_prem = -0.1
    fig1 = pdf_and_payout_sweep(pdf_x, pdfs_y[0],
                                np.linspace(min_prem, max_prem, 10), 'ETH', legend=False)
    fig2 = kelly_growth_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                              np.linspace(0.0, 0.9999, 50))
    fig3 = kelly_derivative_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                                  np.linspace(0.0, 0.9999, 50))
    fig4 = plot_curve([curve_df.A.values[0], curve_df.B.values[0],
                      curve_df.C.values[0], curve_df.D.values[0]],
                      curve_df.bet_fractions.values[0], curve_df.curve_points.values[0])

    # Change when running the example
    show_figs = False
    if show_figs:
        show(fig1)
        show(fig2)
        show(fig3)
        show(fig4)

    print(pdf_df.to_string())
    print(curve_df.to_string())
    print(training_df.to_string())


def generator_bull_put():
    """
    Example Hello World for generating curves for a bull put spread

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    payoff_dict = make_payoff_dict(call_or_put='put', direction='short')
    payoff_dict = add_leg_to_dict(payoff_dict, strike=0.8, call_or_put='put', direction='long')

    configure_curve_gen(build_generator_config(input_file, price_history_file,
                                               payoff_dict=payoff_dict))
    curve_df, pdf_df, training_df = generate_curves(payoff_dict=payoff_dict)

    pdf_x, pdfs_y = get_pdf_arrays()

    min_prem = 0.001
    max_prem = 0.03
    fig1 = pdf_and_payout_sweep(pdf_x, pdfs_y[0],
                                np.linspace(min_prem, max_prem, 10), 'ETH', legend=False)
    fig2 = kelly_growth_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                              np.linspace(0.0, 0.9999, 50))
    fig3 = kelly_derivative_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                                  np.linspace(0.0, 0.9999, 50))
    fig4 = plot_curve([curve_df.A.values[0], curve_df.B.values[0],
                      curve_df.C.values[0], curve_df.D.values[0]],
                      curve_df.bet_fractions.values[0], curve_df.curve_points.values[0])

    # Change when running the example
    show_figs = False
    if show_figs:
        show(fig1)
        show(fig2)
        show(fig3)
        show(fig4)

    print(pdf_df.to_string())
    print(curve_df.to_string())
    print(training_df.to_string())


def generator_builder():
    """
    Example Hello World for generating curves using the builder configuration objects

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    training_config = TrainingConfigBuilder().set_input_csv_filename(
        input_file).set_training_history_filename(price_history_file)

    bounds_config = ConstraintsConfigBuilder().add_upper_bound(lambda a: 1.0).add_lower_bound(
        lambda a: 0.0)

    config = GeneratorConfigBuilder().set_training_builder(training_config).set_bounds_builder(
        bounds_config).set_fit_builder(FitConfigBuilder()).build_config()

    configure_curve_gen(config)
    curve_df, pdf_df, training_df = generate_curves()

    print(curve_df.to_string())
    print(training_df.to_string())
    print(pdf_df.to_string())


if __name__ == '__main__':
    generator_hello_world_func()
    generator_hello_world_oo()
    generator_normal_dist()
    generator_skewed_normal_dist()
    generator_long_call()
    generator_bull_put()
    generator_builder()

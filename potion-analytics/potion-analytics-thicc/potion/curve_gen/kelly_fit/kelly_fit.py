"""
This module is used by the Generator to fit best-fit curves to the generated Kelly curve points.

This is done using a class which follows the duck typed interface of the Generator
and is used by it to fit Kelly curves.

Callers who wish to replace or customize the behavior of this module need only implement
three duck typed functions:

    configure_convolution(FitConfig)
        'Configures the settings of this module. See builders module for more info
        on FitConfig'
    fit_kelly_curve(ndarray, ndarray)
        'Fits a function to the X and Y points of the Kelly curve'

Like many python libraries, this module uses a global object with the methods prebound so that
the same library can be used by object-oriented and functional programmers alike. Object-oriented
users can use the KellyFit class, and functional programmers can use the functions
described above.
"""
import numpy as np
from scipy.optimize import curve_fit

from potion.curve_gen.kelly_fit.builder import FitConfig, FitConfigBuilder


def _fit_exp(bet_fractions: np.ndarray, premiums: np.ndarray, maxfev=100000,
             lower_bounds=(0.0, 0.0, 0.0), upper_bounds=(np.inf, np.inf, np.inf)):
    """
    Fits an exponential function to the data points of the Kelly curve

    Parameters
    ----------
    bet_fractions : numpy.ndarray
        The bet fractions which are the X points on the Kelly curve
    premiums : numpy.ndarray
        The premiums which are the Y points on the Kelly curve
    maxfev : int
        (Optional. Default: 100000) The max function evaluations of the optimizer
    lower_bounds : Tuple[float]
        (Optional. Default: (0.0, 0.0, 0.0)) The lower bounds on each of the parameters
        in the optimizer
    upper_bounds : Tuple[float]
        (Optional. Default: (inf, inf, inf)) The upper bounds on each of the parameters
        in the optimizer

    Returns
    -------
    params : List[float]
        The list of parameters of the function fit to the Kelly curve
    """
    fit_params, fit_cov = curve_fit(lambda t, a, b, c:
                                    a * np.exp(b * t) + c, bet_fractions, premiums,
                                    maxfev=maxfev, bounds=(lower_bounds, upper_bounds))
    return fit_params


def _fit_poly(bet_fractions: np.ndarray, premiums: np.ndarray, maxfev=100000,
              lower_bounds=(0.0, 0.0, 0.0, 0.0), upper_bounds=(np.inf, np.inf, np.inf, np.inf)):
    """
    Fits an polynomial function to the data points of the Kelly curve

    Parameters
    ----------
    bet_fractions : numpy.ndarray
        The bet fractions which are the X points on the Kelly curve
    premiums : numpy.ndarray
        The premiums which are the Y points on the Kelly curve
    maxfev : int
        (Optional. Default: 100000) The max function evaluations of the optimizer
    lower_bounds : Tuple[float]
        (Optional. Default: (0.0, 0.0, 0.0, 0.0)) The lower bounds on each of the parameters
        in the optimizer
    upper_bounds : Tuple[float]
        (Optional. Default: (inf, inf, inf, inf)) The upper bounds on each of the parameters
        in the optimizer

    Returns
    -------
    params : List[float]
        The list of parameters of the function fit to the Kelly curve
    """
    fit_params, fit_cov = curve_fit(lambda t, a, b, c, d:
                                    a * t ** 3 + b * t ** 2 + c * t + d,
                                    bet_fractions, premiums, maxfev=maxfev,
                                    bounds=(lower_bounds, upper_bounds))
    return fit_params


def _fit_cosh(bet_fractions: np.ndarray, premiums: np.ndarray, maxfev=100000,
              lower_bounds=(0.0, 0.0, 0.0, 0.0), upper_bounds=(100.0, 100.0, 100.0, 100.0)):
    """
    Fits a cosh function to the data points of the Kelly curve

    Parameters
    ----------
    bet_fractions : numpy.ndarray
        The bet fractions which are the X points on the Kelly curve
    premiums : numpy.ndarray
        The premiums which are the Y points on the Kelly curve
    maxfev : int
        (Optional. Default: 100000) The max function evaluations of the optimizer
    lower_bounds : Tuple[float]
        (Optional. Default: (0.0, 0.0, 0.0, 0.0)) The lower bounds on each of the parameters
        in the optimizer
    upper_bounds : Tuple[float]
        (Optional. Default: (100.0, 100.0, 100.0, 100.0)) The upper bounds on each of the parameters
        in the optimizer

    Returns
    -------
    params : List[float]
        The list of parameters of the function fit to the Kelly curve
    """
    min_d = premiums[0]
    lower_bounds = (lower_bounds[0], lower_bounds[1], lower_bounds[2], min_d)
    fit_params, fit_cov = curve_fit(lambda t, a, b, c, d:
                                    a * t * np.cosh(b * (t ** c)) + d,
                                    bet_fractions, premiums, maxfev=maxfev,
                                    bounds=(lower_bounds, upper_bounds))

    return fit_params


# Define a lookup table so we can switch functions based on the config
fit_function_table = {
    'EXP': _fit_exp,
    'POLY': _fit_poly,
    'COSH': _fit_cosh
}


class KellyFit:
    """
    This class fits a best-fit curve to the generated points of the Kelly curve. This class is
    used by the Generator following a duck typed interface to create curves.
    """

    def __init__(self, config: FitConfig):
        """
        Constructs the object using the FitConfig created using the builder module

        Parameters
        ----------
        config : FitConfig
            The config object created using the builder module
        """
        self.config = config
        self.fit_func = fit_function_table[self.config.fit_type]

    def configure(self, config: FitConfig):
        """
        Changes the config object to a different configuration

        Parameters
        ----------
        config : FitConfig
            The configuration object to set

        Returns
        -------
        None
        """
        self.config = config
        self.fit_func = fit_function_table[self.config.fit_type]

    def fit_kelly_curve(self, bet_fractions: np.ndarray, premiums: np.ndarray, maxfev=100000,
                        lower_bounds=(0.0, 0.0, 0.0, 0.0),
                        upper_bounds=(100.0, 100.0, 100.0, 100.0)):
        """
        Fits the currently configured function to the data points of the Kelly curve

        Parameters
        ----------
        bet_fractions : numpy.ndarray
            The bet fractions which are the X points on the Kelly curve
        premiums : numpy.ndarray
            The premiums which are the Y points on the Kelly curve
        maxfev : int
            (Optional. Default: 100000) The max function evaluations of the optimizer
        lower_bounds : Tuple[float]
            (Optional. Default: (0.0, 0.0, 0.0, 0.0)) The lower bounds on each of the parameters
            in the optimizer
        upper_bounds : Tuple[float]
            (Optional. Default: (100.0, 100.0, 100.0, 100.0)) The upper bounds on each of the
            parameters in the optimizer

        Returns
        -------
        params : List[float]
            The list of parameters of the function fit to the Kelly curve
        """
        range_to_use = np.where((np.asarray(
            premiums) > 1e-10) | (np.asarray(premiums) < -1e-10))[0][-1]

        return self.fit_func(bet_fractions[:range_to_use+1], premiums[:range_to_use+1],
                             maxfev=maxfev, lower_bounds=lower_bounds, upper_bounds=upper_bounds)


# Define a Global object with default values to be configured by the module user
_fit = KellyFit(FitConfigBuilder().build_config())

# Prebind the object's methods so the module can be used by object oriented and functional
# programmers alike
configure_fit = _fit.configure
fit_kelly_curve = _fit.fit_kelly_curve

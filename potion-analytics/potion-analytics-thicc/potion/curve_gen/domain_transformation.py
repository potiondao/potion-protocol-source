"""
This module provides functions which transform a probability distribution from one domain to
another. Generally, this is used when converting probabilities over log returns into probability
values over prices.

When the tool models the probability distribution of some financial returns and performs
convolution to propagate the distribution forward in time, it does this in the
log domain for a collection of different reasons. The payout function from an option however, is
calculated over the price domain (i.e. the payout depends on the strike, not a log return). To
perform the Kelly calculation, the probability values need to be transformed into a function over
the price.

In this module, the trapezoidal rule of integration is used to model the probability bins.

The function transform_pdf_optimize is the main function which should be used.  It uses
optimization to perform the transformation. The older version of the function is called
transform_pdf_rough which only calculates a rough approximation of the transformed PDF
and in general should not be used. It is used as an initial guess for the optimizer.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.ndimage import gaussian_filter1d


def log_to_price_sample_points(x, current_price: float):
    """
    Transforms sample points in the log-return domain to the price domain using the current price.
    This allows an apples-to-apples comparison between the probability PDF and the payout function

    Parameters
    ----------
    x : List[float]
        The sample points in the log-return domain
    current_price : float
        The current price in the price domain to use as reference

    Returns
    -------
    sample_points : List[float]
        List of sample points in the price domain corresponding to the x points in the log return
        domain

    """
    return np.exp(x) * current_price


def price_to_log_sample_points(x: np.ndarray, current_price: float):
    """
    Transforms sample points in the price domain to the log-return domain using the current price.
    This allows an apples-to-apples comparison between the probability PDF and the payout function

    Parameters
    ----------
    x : numpy.ndarray
        The sample points in the price domain
    current_price : float
        The current price in the price domain to use as reference

    Returns
    -------
    sample_points
        List of sample points in the log-return domain corresponding to the x points in the
        price domain
    """
    return np.log(x / current_price)


def transform_probability_bin(x1: float, y1: float, x2: float, y2: float, x1_t: float, y1_t: float,
                              x2_t: float):
    """
    This function uses the Trapezoidal Rule to transform a probability bin from one domain to
    another by assuming the areas of the two bins to be equal in both domains

    Parameters
    ----------
    x1 : float
        The x value of the first point in the starting domain
    y1 : float
        The y value of the first point in the starting domain
    x2 : float
        The x value of the second point in the starting domain
    y2 : float
        The y value of the second point in the starting domain
    x1_t : float
        The x value of the first point in the transformed domain
    y1_t : float
        The y value of the first point in the transformed domain
    x2_t : float
        The x value of the second point in the transformed domain

    Returns
    -------
    y2_t : float
        The y value of the second point in the transformed domain

    """
    return ((x2 - x1) * (y1 + y2) / (x2_t - x1_t)) - y1_t


def transform_pdf_rough(starting_domain_pts: np.ndarray, starting_domain_pdf: np.ndarray,
                        transformed_domain_pts: np.ndarray):
    """
    This function takes the samples points of a probability PDF and approximately transforms
    them into some other domain. For example, transforming from log-return domain to price domain.

    Parameters
    ----------
    starting_domain_pts : numpy.ndarray
        The sample points along the x axis of the probability PDF in the starting domain
    starting_domain_pdf : numpy.ndarray
        The PDF function values f(x) at the sample points x in the starting domain
    transformed_domain_pts : numpy.ndarray
        The sample points along the x axis of the probability PDF in the transformed domain

    Raises
    -------
    ValueError
        If the length of the input arrays is not the same

    Returns
    -------
    transformed_domain_pdf : numpy.ndarray
        The PDF function values f(x) at the sample points x in the transformed domain
    """
    if len(starting_domain_pts) != len(starting_domain_pdf) or len(starting_domain_pts) != len(
            transformed_domain_pts):
        raise ValueError(
            'Length of domain arrays must be equal to each other as '
            'well as pdf values array length')

    # Calculate a reasonable non-zero initial pdf value to reduce the amplitude of the
    # sawtooth behavior
    dx = float(starting_domain_pts[1] - starting_domain_pts[0])
    sy = float(starting_domain_pdf[1] + starting_domain_pdf[0])
    first_bin_area = dx * sy / 2.0
    y1_t = first_bin_area / 2.0

    # Roughly transform the PDF function assuming equal areas of the probability bins
    transformed_domain_pdf = np.zeros(len(transformed_domain_pts))
    for i in range(len(starting_domain_pts) - 1):
        x1 = starting_domain_pts[i]
        y1 = starting_domain_pdf[i]
        x2 = starting_domain_pts[i + 1]
        y2 = starting_domain_pdf[i + 1]
        x1_t = transformed_domain_pts[i]
        x2_t = transformed_domain_pts[i + 1]

        y2_t = transform_probability_bin(x1, y1, x2, y2, x1_t, y1_t, x2_t)

        # Index is i+1 because our initial value was y1_t
        transformed_domain_pdf[i + 1] = y2_t

        # save y for next loop
        y1_t = y2_t

    return transformed_domain_pdf


def sum_squared_error_bin_areas(transformed_pdf: np.ndarray, starting_domain_pts: np.ndarray,
                                starting_domain_pdf: np.ndarray,
                                transformed_domain_pts: np.ndarray):
    """
    This function is used as the objective function for scipy minimize to take a probability
    distribution and transform it into a different domain. This process assumes that the two
    domains will have probability bins which have equal area. This function calculates the sum
    of the squared errors so that we can minimize the difference between the bins of one domain
    and the other, which will give us the points of the transformed distribution.

    Parameters
    ----------
    transformed_pdf : numpy.ndarray
        The input (Y values) points where we are calculating our score that is being minimized
    starting_domain_pts : numpy.ndarray
        The X values of the points in the starting domain
    starting_domain_pdf : numpy.ndarray
        The Y values of the points in the starting domain
    transformed_domain_pts : numpy.ndarray
        The X values of the points in the output domain

    Returns
    -------
    sum_sq_errors : numpy.ndarray
        The sum of the errors squared
    """
    # Calculate the inputs to the trapezoidal rule
    dx = np.diff(np.asarray(starting_domain_pts))
    sy = np.asarray(starting_domain_pdf[:-1]) + np.asarray(starting_domain_pdf[1:])
    dxt = np.diff(transformed_domain_pts)
    syt = transformed_pdf[:-1] + transformed_pdf[1:]

    # Trapezoidal rule to assume equal areas
    dx = np.asarray(dx, dtype=float)
    starting_bin_area = (dx * sy) / 2.0
    transformed_bin_area = (dxt * syt) / 2.0

    # print('As: {} At: {}'.format(starting_bin_area, transformed_bin_area))

    # Calculate the sum squared error
    error = starting_bin_area - transformed_bin_area
    sq_error = np.square(error)
    sum_sq_errors = np.sum(sq_error)

    # print('e: {} sq: {} sse: {}'.format(error, sq_error, out))

    return sum_sq_errors


def transform_pdf_using_optimize(starting_domain_pts: np.ndarray, starting_domain_pdf: np.ndarray,
                                 transformed_domain_pts: np.ndarray, bounds='default',
                                 tol=1e-6):
    """
    Finds the Y values of the transformed PDF by minimizing the differences between the areas
    of the input domain and output domain PDFs.
    
    For example, if we wanted to convert from a PDF over log returns to one over prices, we
    could take the X and Y values of the PDF in log returns, and the X values of possible
    prices in the price domain, and calculate the Y values of the PDF over the prices.

    Parameters
    ----------
    starting_domain_pts : numpy.ndarray
        The X values in the domain of the input PDF
    starting_domain_pdf : numpy.ndarray
        The Y values of probability density in the input PDF
    transformed_domain_pts : numpy.ndarray
        The X values in the domain of the output PDF
    bounds : List[tuple] or str
        The List of tuples defining the upper and lower bound of each input
        variable e.g. (0, 2) (Default value = 'default')
    tol : float
        (Default: 1e-6) The tolerance on the optimizer error
        

    Returns
    -------
    transformed_pdf : numpy.ndarray
        The Y values of probability density in the output PDF
    """

    # Calculates an approximate initial value of what the transformed pdf will be
    transformed_guess = transform_pdf_rough(starting_domain_pts, starting_domain_pdf,
                                            transformed_domain_pts)

    # Smooth any sawtooth pattern modulated into the initial guess PDF
    transformed_guess = gaussian_filter1d(transformed_guess, 2)

    if bounds == 'default':
        # Define the optimization boundaries on each input variable
        bounds = []
        for x in transformed_guess:
            bounds.append((0, None))

    # This option chooses to not constrain the inputs at all. Used if it is a
    # function that's not a PDF being transformed
    if bounds is None:
        transformed_pdf = minimize(sum_squared_error_bin_areas, transformed_guess,
                                   args=(starting_domain_pts, starting_domain_pdf,
                                         transformed_domain_pts),
                                   tol=tol)
    else:
        # Minimize the differences between the input and output areas
        transformed_pdf = minimize(sum_squared_error_bin_areas, transformed_guess,
                                   args=(starting_domain_pts, starting_domain_pdf,
                                         transformed_domain_pts),
                                   tol=tol, bounds=bounds)

    # print('out: {}'.format(transformed_pdf))

    # Returns the output value
    return transformed_pdf.x

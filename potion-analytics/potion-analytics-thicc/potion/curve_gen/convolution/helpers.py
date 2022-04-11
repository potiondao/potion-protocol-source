"""
This module provides helper functions for performing convolution of a probability PDF in order to
propagate that distribution forward in time.

For example, suppose the caller has a PDF function for what values a random variable are
probable to have 1 day in the future. If it is assumed this PDF does not change each day,
the PDF for the random variable 2 days in the future can be calculated by performing the
convolution of the PDF function with itself. To get the PDF N days in the future requires N
convolutions of the PDF with itself.

This module provides basic functions to perform convolutions on PDFs.

There is also a helper function for binding distribution parameters (location, scale, skew, nu)
to the PDF function call itself. With this, the caller can pass just the function in their
code, rather than passing the PDF parameters around all of the time for convenience.

Example:
    dist = bind_pdf_params(skewed_t.pdf, loc, scale, skew, nu)  \n
    Now, dist(x) is the same as calling skewed_t.pdf(x, skew, nu, loc=loc, scale=scale) and is
    a lot nicer to write
"""
from functools import partial
import numpy as np
from scipy.stats import rv_continuous
import scipy.signal


def bind_pdf_params(dist: rv_continuous, loc: float, scale: float, skew: float, nu: float):
    """
    This is a helper function which uses the python partial functions library to bind the
    parameters of the distribution to the .pdf function call so that we can calculate the PDF
    by simply calling dist.pdf(x) without having to pass around location, scale, skew, nu
    parameters all the time. This partial function binds those parameters so that they are
    passed with the distribution arguments.

    Parameters
    ----------
    dist : rv_continuous
        The rv_continuous object for which we are binding the parameters to
    loc : float
        The location parameter of the distribution
    scale : float
        The scale parameter of the distribution
    skew : float
        The skew parameter of the distribution
    nu : float
        The nu parameter of the distribution

    Returns
    -------
    functools.partial
        The partial function we can call func(x) to get the PDF
    """
    # Partial function always binds the left-most input parameter so we have to use this lambda
    # to be tricky and move x to be the last input of the function
    return partial(lambda l, sc, sk, n, x: dist.pdf(x, sk, n, loc=l, scale=sc), loc, scale, skew,
                   nu)


def convolve(dist_x: partial, dist_y: partial, x: np.ndarray):
    """
    Performs a convolution of the x and y distributions provided. These partial functions should
    implement the PDF function of the distribution using bind_pdf_params. The convolution is
    performed at the points specified by the x-array

    Parameters
    ----------
    dist_x : partial
        The PDF function of the distribution for the first random variable
    dist_y : partial
        The PDF function of the distribution for the second random variable
    x : numpy.ndarray
        The points at which to calculate the convolved PDF

    Returns
    -------
    pdf_x : List[float]
        The X PDF evaluated at each X point
    pdf_y : List[float]
        The Y PDF evaluated at each X point
    out : List[float]
        The convolved PDF values at each X point
    delta : float
        The delta (spacing) between the X points
    """
    # Get the PDF values for each distribution
    pdf_x = dist_x(x)
    pdf_y = dist_y(x)

    # Get the delta between x points to scale the convolution input and output values
    delta = x[1] - x[0]

    # out = scipy.signal.convolve(pdf_x * delta, pdf_y * delta, 'same') / delta
    out = scipy.signal.convolve(pdf_x * delta, pdf_y * delta, 'same') / delta

    return pdf_x, pdf_y, out, delta


def convolve_self(dist: partial, x: np.ndarray):
    """
    Performs a convolution of the x distribution provided with itself. This partial function
    should implement the PDF function of the distribution using bind_pdf_params. The convolution
    is performed at the points specified by the x-array

    Parameters
    ----------
    dist : functools.partial
        The PDF function of the distribution for the random variable
    x : numpy.ndarray
        The points at which to calculate the convolved PDF

    Returns
    -------
    pdf_x : List[float]
        The X PDF evaluated at each X point
    out : List[float]
        The convolved PDF values at each X point
    delta : float
        The delta (spacing) between the X points
    """
    pdf_x = dist(x)

    # Get the delta between x points to scale the convolution input and output values
    delta = x[1] - x[0]

    out = scipy.signal.convolve(pdf_x * delta, pdf_x * delta, 'same') / delta

    return pdf_x, out, delta


def convolve_self_n(dist: partial, x, n: int):
    """
    Performs a self convolution n number of times. The partial function should implement the
    PDF function of the distribution using bind_pdf_params. The convolution is performed at
    the points specified by the x-array n number of times.

    Parameters
    ----------
    dist : functools.partial
        The PDF function of the distribution for the random variable
    x : numpy.ndarray
        The points at which to calculate the convolved PDF
    n : int
        The number of times to perform the convolution of the distribution with itself

    Returns
    -------
    pdf_list : List[List[float]]
        A nested List containing the convolved PDF values n elements long. One element for
        each convolution PDF
    """

    # Check the input is valid. For 0 and negative it just calculates the PDF
    if n < 1:
        return [dist(x)]

    # Perform the convolution for the first time
    pdf_x, con_pdf, delta = convolve_self(dist, x)

    # Perform the subsequent convolutions
    pdf_list = [pdf_x, con_pdf]
    out = con_pdf
    for i in range(n - 1):
        out = scipy.signal.convolve(out * delta, pdf_x * delta, 'same') / delta
        pdf_list.append(out)

    return pdf_list

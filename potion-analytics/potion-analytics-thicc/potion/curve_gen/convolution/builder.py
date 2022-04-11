"""
This module supplies the ConvolutionConfig object and the ConvolutionConfigBuilder to allow
users of the library to configure the convolution of return PDFs following a standard
design pattern. This is the same pattern used by the other modules of the curve generator.
"""
import numpy as np
from typing import NamedTuple, List
from scipy.stats import rv_continuous, norm

from potion.curve_gen.domain_transformation import log_to_price_sample_points


class ConvolutionConfig(NamedTuple):
    """
    Immutable configuration object produced by the builder containing the values to use
    during convolution
    """
    num_times_to_conv: int
    """The number of days into the future to project the distribution using convolution"""
    points_in_pdf: int
    """The number of sample points in the PDF function"""
    log_only: bool
    """Whether the caller only cares about calculating the log pdf functions"""
    dist_params: List[float]
    """The list of parameters fit for the rv_continuous distribution"""
    dist: rv_continuous
    """The probability distribution fit to the return data"""
    x: np.ndarray
    """The domain points of the PDF using possible prices"""
    log_x: np.ndarray
    """The domain points of the PDF using possible log return values"""

    def __eq__(self, other):
        """
        Checks if this config object is equal to other

        Parameters
        ----------
        other : ConvolutionConfig
            The other config object we are testing for equality

        Returns
        -------
        is_equal : bool
            True if the two objects are equal, False otherwise
        """
        return (self.num_times_to_conv == other.num_times_to_conv) and (
                self.points_in_pdf == other.points_in_pdf) and (
                       self.log_only == other.log_only) and (
                       self.dist_params == other.dist_params) and (
                       self.dist == other.dist) and np.array_equal(
            self.x, other.x) and np.array_equal(self.log_x, other.log_x)


class ConvolutionConfigBuilder:
    """
    Standard python builder class for creating immutable configuration objects to use
    during the convolution process
    """

    def __init__(self):
        """
        Constructor initializes the builder with default values
        """
        self.num_times_to_conv = 1
        self.dist = norm.pdf
        self.dist_params = []
        self.min_x = -5
        self.max_x = 5
        self.points_in_pdf = 20001
        self.log_only = False

    def set_num_times_to_convolve(self, num: int):
        """
        Sets the number of times (days) to perform the convolution into the future

        Parameters
        ----------
        num : int
            The number of days into the future to project the distribution

        Returns
        -------
        self : ConvolutionConfigBuilder
            This object following the builder pattern
        """
        self.num_times_to_conv = num
        return self

    def set_distribution(self, dist: rv_continuous):
        """
        Sets the probability distribution to use during convolution

        Parameters
        ----------
        dist : rv_continuous
            The probability distribution fit to the return data

        Returns
        -------
        self : ConvolutionConfigBuilder
            This object following the builder pattern
        """
        self.dist = dist
        return self

    def set_distribution_params(self, params: List[float]):
        """
        Sets the parameters fit for the probability distribution

        Parameters
        ----------
        params : List[float]
            The list of parameters fit for the rv_continuous distribution

        Returns
        -------
        self : ConvolutionConfigBuilder
            This object following the builder pattern
        """
        self.dist_params = params
        return self

    def set_min_x(self, min_x: float):
        """
        Sets the lowest x value in the log PDF function

        Parameters
        ----------
        min_x : float
            The min x value

        Returns
        -------
        self : ConvolutionConfigBuilder
            This object following the builder pattern
        """
        self.min_x = min_x
        return self

    def set_max_x(self, max_x: float):
        """
        Sets the highest x value in the log PDF function

        Parameters
        ----------
        max_x : float
            The max x value

        Returns
        -------
        self : ConvolutionConfigBuilder
            This object following the builder pattern
        """
        self.max_x = max_x
        return self

    def set_points_in_pdf(self, num_points: int):
        """
        Sets the number of sample points in the PDF function

        Parameters
        ----------
        num_points : int
            The number of sample points in the PDF function

        Returns
        -------
        self : ConvolutionConfigBuilder
            This object following the builder pattern
        """
        self.points_in_pdf = num_points
        return self

    def set_log_only(self, log_only: bool):
        """
        Sets the flag for whether the caller only cares about calculating the log pdf functions

        Parameters
        ----------
        log_only : bool
            Whether the caller only cares about calculating the log pdf functions

        Returns
        -------
        self : ConvolutionConfigBuilder
            This object following the builder pattern
        """
        self.log_only = log_only
        return self

    def build_config(self):
        """
        Creates an immutable ConvolutionConfig object from the currently configured builder

        Returns
        -------
        config : ConvolutionConfig
            The immutable configuration object
        """
        log_x = np.linspace(self.min_x, self.max_x, self.points_in_pdf)
        x = log_to_price_sample_points(log_x, 1.0)
        return ConvolutionConfig(self.num_times_to_conv, self.points_in_pdf, self.log_only,
                                 self.dist_params, self.dist, x, log_x)

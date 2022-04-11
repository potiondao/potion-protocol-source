"""
This module implemets a class that wraps the external library (for estimation) and scipy's
implementation of the multivariate t distribution in a format that aims to be consistent
with the scipy stats rv_continuous interface.

rv_continuous seems to only support single variable random variables, so it cannot be directly
subclassed like the others. The function calls however mimic the same interface so that it is
consistent throughout the tool.
"""
from scipy.stats import multivariate_t
import pandas as pd
import numpy as np

from lib.t import t


def mle_multi_var_t(samples, nu):
    """
    Calls the MLE library to calibrate the distributions based on the sample data and
    unpacks the results

    Parameters
    ----------
    samples : pandas.DataFrame
        The return samples which are used to estimate the multivariate t distribution
    nu : float
        The tail parameter of the Student's T, estimated previously using a tail fitting algorithm

    Returns
    -------
    mu_est : numpy.ndarray
        Estimated means of each variable
    cov_est : pandas.DataFrame
        Estimated covariance matrix
    fitness_scores : numpy.ndarray
        The fitness scores at each iteration of the optimization
    """
    estimates = t(samples.to_numpy(), dof=nu)

    mu_est = estimates[1]
    cov_est = estimates[0]
    fitness_scores = estimates[2]

    return mu_est, cov_est, fitness_scores


class MultiVarStudentT:
    """
    A class to implement the multivariate t distribution in a format that aims to be consistent
    with the scipy stats rv_continuous interface
    """

    def __init__(self, mu, cov, nu):
        """
        Constructor for the class

        Parameters
        ----------
        mu : List[float]
            The List of means for the distribution. One mean value for each random variable
        cov : pandas.DataFrame
            The covariance matrix for the distribution, an NxN matrix for each N variables
        nu : float
            The degrees of freedom parameter determining the tail behavior of the distribution
        """
        self.t = multivariate_t(mu, cov, df=nu)
        self.mu = mu
        self.cov = pd.DataFrame(cov)
        self.nu = nu

    def get_positions_for_pdf(self, axis_minimums, axis_maximums, axis_deltas):
        """
        Gets an N-dimensional grid which are the domain values of the PDF

        Parameters
        ----------
        axis_minimums : List[float]
            The minimum values along each axis of the distribution
        axis_maximums : List[float]
            The maximum values along each axis of the distribution
        axis_deltas : List[float]
            The deltas controlling the distance between each point along the axis

        Returns
        -------
        positions : numpy.ndarray
            The ndarray containing the grid positions output from dstack
        grid : numpy.ndarray
            The mesh-grid input for the positions
        """
        num_dimensions = len(self.mu)

        # Build a tuple of slices for input to mgrid
        slice_list = []
        for i in range(num_dimensions):
            slice_list.append(slice(axis_minimums[i], axis_maximums[i], axis_deltas[i]))

        mgrid_index = tuple(s for s in slice_list)

        # Create the grid and return the stacked positions
        grid = np.mgrid[mgrid_index]
        return np.dstack(grid), grid

    def pdf(self, positions):
        """
        This function mimics rv_continuous's pdf and calculates the PDF at each position,
        then the PDF values are returned in a corresponding array.

        Parameters
        ----------
        positions : numpy.ndarray
            The positions in the grid where we are calculating a PDF value from a mesh-grid
            of ndarrays all of the same dimensions

        Returns
        -------
        pdf_values : numpy.ndarray
            The PDF value at each position in the mesh-grid
        """
        return self.t.pdf(positions)

    def rvs(self, num_samples):
        """
        This function mimics rv_continuous's rvs and generates num_samples random samples
        from the distribution

        Parameters
        ----------
        num_samples : int
            The number of samples to generate

        Returns
        -------
        rand_vars : pandas.DataFrame
            A DataFrame num_samples rows by N columns
        """
        return pd.DataFrame(self.t.rvs(num_samples), columns=self.cov.columns)


# **************************************************************
# This file implements Diethelm Wuertz's Skewed Student T of the
# fGarch library for use with Python scipy which can be found
# here: https://rdrr.io/cran/fGarch/src/R/dist-sstd.R
# The library uses the LGPLv2 which can be found here:
# https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html
# which makes this file also LGPLv2.
# Last modifications by Mike Johnson on 5/5/2021
# **************************************************************

# This file is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General
# Public License along with this file; if not, write to the
# Free Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA  02111-1307  USA
"""
This module implements a Student's T distribution with skew in a manner that allows it to
be used with scipy.stats as a custom distribution. It does this primarily by subclassing
rv_continuous and overriding the specified internal functions.
"""
from scipy.stats import rv_continuous, t, uniform
from scipy.special import beta
import numpy as np


class SkewedT(rv_continuous):
    """
    This class is a subclass of rv_continuous and implements a custom probability distribution.
    This class implements Student's T with Skew so that it can be used with scipy.stats
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor sets the scipy name of the distribution to skewed_t and tells scipy there
        are two parameters named shape and nu
        """
        kwargs['name'] = 'skewed_t'
        kwargs['shapes'] = 'shape, nu'
        super(SkewedT, self).__init__(*args, **kwargs)

    def _argcheck(self, *args):
        """
        Overrides the default _argcheck function so we can check our parameters allow the
        correct input range

        Parameters
        ----------
        args : List[float]
            The array of input parameters

        Raises
        -------
        ValueError
            If the number of parameters is not 2

        Returns
        -------
        condition : bool
            True if the args are correct, False otherwise
        """
        if len(args) != 2:
            raise ValueError('Skewed T Distribution requires 2 parameters shape and nu')

        cond = 1

        skew = args[0]
        nu = args[1]

        # For some reason scipy.stats sometimes passes this in as an array of the parameter
        if type(skew) is np.ndarray:
            if skew.ndim > 0:
                skew = skew[0]
        if type(nu) is np.ndarray:
            if nu.ndim > 0:
                nu = nu[0]

        # check the skew param is between -inf and inf
        cond = np.logical_and(cond, (skew > 0.0))
        # cond = np.logical_and(cond, (skew > -np.inf))
        cond = np.logical_and(cond, (skew < np.inf))
        # check degrees of freedom is greater than 1 (cauchy dist)
        cond = np.logical_and(cond, (nu > 2.0))

        # print('arg_check: {}'.format(cond))
        return cond

    def _pdf(self, x, *args, loc=0.0, scale=1.0):
        """
        Overrides the _pdf function so we can calculate our custom density function for an
        rv_continuous variable

        Parameters
        ----------
        x : numpy.ndarray
            The points in the domain to calculate the density at
        args : List[float]
            The array of input parameters - in this case args[0] is skew and args[1] is nu
        loc : float
            The location parameter to move the distribution (Default value = 0.0)
        scale : float
            The scale parameter to scale the distribution size up and down with the same skew and
            tail properties (Default value = 1.0)

        Returns
        -------
        pdf : numpy.ndarray
            The density function y values at the points x for y=f(x)
        """
        skew = args[0]
        nu = args[1]

        # print(type(skew))

        # For some reason scipy.stats sometimes passes this in as an array of the parameter
        if type(skew) is np.ndarray:
            if skew.ndim > 0:
                skew = skew[0]
        if type(nu) is np.ndarray:
            if nu.ndim > 0:
                nu = nu[0]

        # Calculate mu
        skew_inv = 1.0 / skew
        m1 = 2.0 * np.sqrt(nu - 2.0) / (nu - 1.0) / beta(0.5, nu / 2.0)
        mu = m1 * (skew - skew_inv)

        # Calculate sigma for scaling inputs and outputs
        skew_sq = skew ** 2.0
        m1_sq = m1 ** 2.0
        arg = (1.0 - m1_sq) * (skew_sq + (1.0 / skew_sq)) + (2 * m1_sq) - 1.0
        sig = np.sqrt(arg)

        # Scale the inputs
        z = x * sig + mu

        # print('z: {}'.format(z))

        # Calculate skewed density
        skew_values = skew ** np.sign(z)

        # print('skvs: {}'.format(skew_values))

        k = 2.0 / (skew + skew_inv)

        # print('k: {}'.format(k))

        z_skew = z / skew_values
        density_values = k * t.pdf(z_skew, nu)

        # Scale the output
        return sig * density_values

    def _cdf(self, x, *args, loc=0.0, scale=1.0):
        """
        Overrides the _cdf function so we can calculate our custom cumulative density function
        for an rv_continuous variable

        Parameters
        ----------
        x : numpy.ndarray
            The points in the domain to calculate the density at
        args : List[float]
            The array of input parameters - in this case args[0] is skew and args[1] is nu
        loc : float
            The location parameter to move the distribution (Default value = 0.0)
        scale : float
            The scale parameter to scale the distribution size up and down with the same skew and
            tail properties (Default value = 1.0)

        Returns
        -------
        cdf : numpy.ndarray
            The cumulative density function y values at the points x for y=f(x)
        """
        skew = args[0]
        nu = args[1]

        # For some reason scipy.stats sometimes passes this in as an array of the parameter
        if type(skew) is np.ndarray:
            if skew.ndim > 0:
                skew = skew[0]
        if type(nu) is np.ndarray:
            if nu.ndim > 0:
                nu = nu[0]

        # Calculate mu
        skew_inv = 1.0 / skew
        m1 = 2.0 * np.sqrt(nu - 2.0) / (nu - 1.0) / beta(0.5, nu / 2.0)
        mu = m1 * (skew - skew_inv)

        # Calculate sigma for scaling inputs and outputs
        skew_sq = skew ** 2.0
        m1_sq = m1 ** 2.0
        arg = (1.0 - m1_sq) * (skew_sq + (1.0 / skew_sq)) + (2 * m1_sq) - 1.0
        sig = np.sqrt(arg)

        # Scale the inputs
        # print('x: {}'.format(x))
        z = x * sig + mu

        # Calculate skewed density
        skew_values = skew ** np.sign(z)
        k = 2.0 / (skew + skew_inv)
        cdf_values = np.heaviside(z, 0.5) - np.sign(z) * k * skew_values * t.cdf(
            (-np.abs(z) / skew_values), nu)

        return cdf_values

    def _rvs(self, *args, size=None, random_state=None):
        """
        Overrides the _rvs function so we can generate random variable samples for an
        rv_continuous variable

        Parameters
        ----------
        args : List[float]
            The array of input parameters - in this case args[0] is skew and args[1] is nu
        size : int or tuple of ints, optional
            Defining number of random variates (default is 1).
        random_state : {None, int, numpy.random.Generator, numpy.random.RandomState}
            See scipy doc: If seed is None (or np.random), the numpy.random.RandomState
            singleton is used. If seed is an int, a new RandomState instance is used, seeded
            with seed. If seed is already a Generator or RandomState instance then that
            instance is used.

        Returns
        -------
        rvs : numpy.ndarray
            Random variates of given size
        """
        skew = args[0]
        nu = args[1]

        # For some reason scipy.stats sometimes passes this in as an array of the parameter
        if type(skew) is np.ndarray:
            if skew.ndim > 0:
                skew = skew[0]
        if type(nu) is np.ndarray:
            if nu.ndim > 0:
                nu = nu[0]

        # Generate the random samples
        skew_inv = 1.0 / skew
        weighting = skew / (skew + skew_inv)
        z = uniform.rvs(loc=-weighting, scale=1.0, size=size)
        skew_values = skew ** np.sign(z)
        random_samples = -np.abs(t.rvs(nu, size=size)) / skew_values * np.sign(z)

        # Calculate the location parameter
        m1 = 2.0 * np.sqrt(nu - 2.0) / (nu - 1.0) / beta(0.5, nu / 2.0)
        mu = m1 * (skew - skew_inv)

        # Calculate sigma for scaling inputs and outputs
        skew_sq = skew ** 2.0
        m1_sq = m1 ** 2.0
        arg = (1.0 - m1_sq) * (skew_sq + (1.0 / skew_sq)) + (2 * m1_sq) - 1.0
        sig = np.sqrt(arg)

        # Transform the output by location/scale
        random_samples = (random_samples - mu) / sig

        return random_samples


# Defines this variable as an instance of the class so that it can be used
# like the other scipy.stats distributions
skewed_t = SkewedT()

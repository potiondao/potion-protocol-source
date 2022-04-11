"""
This module implements a Piecewise distribution which has the 'head' as any scipy distribution,
and two pareto tails which replace the original tails of the center distribution. This allows
the center distribution to have tails which are both fat and not symmetric and allows the
modeling of left tail (market crashes) and right tail (squeezes) with separate properties.
"""
import numpy as np
from scipy.stats import genpareto, rv_continuous
from scipy.optimize import brentq

from potion.curve_gen.training.distributions.skewed_students_t import skewed_t
from potion.curve_gen.training.fit.tail_fit import fit_samples


def find_nearest(array, value):
    """
    Helper function which finds the nearest value in the numpy array to the specified value

    Parameters
    ----------
    array : numpy.ndarray
        The array we are searching
    value : float
        The value we are testing with

    Returns
    -------
    close_value : float
        The closest element of the array
    """
    index = np.searchsorted(array, value, side="left")

    if index > 0 and (index == len(array) or np.fabs(value - array[index - 1]) < np.fabs(
            value - array[index])):
        return array[index - 1]
    else:
        return array[index]


def left_tail_helper(x, start_x, pdf, normalization_factor):
    """
    Helper function to use with the root finder to select where the left tail begins

    Parameters
    ----------
    x : float
        The x point to try
    start_x : float
        The point where the center of the distribution ends
    pdf : numpy.ndarray
        The probability density function of the pareto tail
    normalization_factor : float
        The factor to normalize with which is the sum of the densities

    Returns
    -------
    start_error : float
        The error between the calculated spot and the start of the tail which we are minimizing
    """
    ret = ((pdf / np.sum(pdf)) * x)[0] - (start_x / normalization_factor)
    return ret


def right_tail_helper(x, start_x, pdf, normalization_factor):
    """
    Helper function to use with the root finder to select where the right tail begins

    Parameters
    ----------
    x : float
        The x point to try
    start_x : float
        The point where the center of the distribution ends
    pdf : numpy.ndarray
        The probability density function of the pareto tail
    normalization_factor : float
        The factor to normalize with which is the sum of the densities

    Returns
    -------
    start_error : float
        The error between the calculated spot and the start of the tail which we are minimizing
    """
    ret = ((pdf / np.sum(pdf)) * (1.0 - x) * normalization_factor)[0] - start_x
    return ret


class PiecewiseDistribution(rv_continuous):
    """
    This class fits and calculates a two tailed piecewise distribution with pareto tails
    replacing each tail
    """

    def __init__(self, *args, **kwargs):
        """
        Fits a two tailed PiecewiseDistribution to the specified sample data.

        Parameters
        ------------
        lower_threshold : float
            The threshold in CDF probability below which the left tail begins
        upper_threshold : float
            The threshold in CDF probability above which the right tail begins

        Raises
        ------------
        ValueError
            If the lower threshold or upper threshold are not between 0 and 1.0, or if the
            upper threshold is not greater than the lower threshold
        """
        kwargs['name'] = 'piecewise'
        kwargs['shapes'] = 'dist_args'
        super(PiecewiseDistribution, self).__init__(*args, **kwargs)

    def _argcheck(self, *args):
        """
        Overrides the default _argcheck function so we can check our parameters allow the
        correct input range

        Parameters
        ----------
        args : List[float]
            The array of input parameters

        Returns
        -------
        is_valid : bool
            Returns True if the args are valid to calculate outputs
        """

        in_dict = args[0]

        # For some reason scipy.stats sometimes passes this in as an array of the parameter
        if type(in_dict) is np.ndarray:
            in_dict = in_dict.flatten()[0]

        dist = in_dict['center_dist']
        dist_args = in_dict['center_dist_params']
        left_threshold = in_dict['left_threshold']
        right_threshold = in_dict['right_threshold']
        left_alpha = in_dict['left_alpha']
        right_alpha = in_dict['right_alpha']
        loc = in_dict['loc']
        scale = in_dict['scale']

        cond = 1
        cond = np.logical_and(cond, isinstance(dist, rv_continuous))

        for param in dist_args:
            cond = np.logical_and(cond, isinstance(param, float))
        cond = np.logical_and(cond, (left_threshold > 0.0))
        cond = np.logical_and(cond, (right_threshold > 0.0))
        cond = np.logical_and(cond, (left_alpha > 0.0))
        cond = np.logical_and(cond, (right_alpha > 0.0))
        cond = np.logical_and(cond, isinstance(loc, float))
        cond = np.logical_and(cond, isinstance(scale, float))

        return cond

    def fit(self, data, *args, dist=skewed_t, fit_function=fit_samples,
            left_threshold=0.1, right_threshold=0.1, **kwargs):
        """
        Overrides the default MLE function to call special tail fitting routines

        Parameters
        ----------
        data : numpy.ndarray
            The data samples being fit
        args : List[float]
            The parameter list to pass to the optimizer as an initial guess. See
            scipy.rv_continuous fit function for more details.
        dist : rv_continuous
            (Optional. Default: skewed_t) The probability distribution to use to generate the
            Kelly curve
        fit_function : Callable
            The function to use when fitting the tail parameters. See tail_fit.py
        left_threshold : float
            (Optional. Default: 0.1) The probability threshold where the sample is considered
            on the left tail. For example, 0.1 is 10% return.
        right_threshold : float
            (Optional. Default: 0.1) The probability threshold where the sample is considered
            on the right tail. For example, 0.1 is 10% return.
        kwargs : dict
            The kwargs if any additional keywords are passed to this function

        Returns
        -------
        dist_params : List[float]
            The distribution parameters fit from the data
        """
        dist_params, fit_dict = fit_function(
            data, *args, dist=dist, left_threshold=left_threshold,
            right_threshold=right_threshold)

        # Swap the parameters back to what scipy interface is
        dist_swapped = list(dist_params[2:])
        dist_swapped.append(dist_params[0])
        dist_swapped.append(dist_params[1])

        return tuple(dist_swapped)

    def _pdf(self, x, *args, loc=0.0, scale=1.0):
        """
        Calculates the PDF function of the distribution which was fit at the
        specified sample_points

        Parameters
        ----------
        sample_points : numpy.ndarray
            The points at which we are calculating the PDF

        Returns
        -------
        output_values : numpy.ndarray
            The Y values of the PDF function
        """
        in_dict = args[0]

        if type(in_dict) == np.ndarray:
            in_dict = in_dict.flatten()[0]

        dist = in_dict['center_dist']
        dist_args = in_dict['center_dist_params']
        left_threshold = in_dict['left_threshold']
        right_threshold = in_dict['right_threshold']
        left_alpha = in_dict['left_alpha']
        right_alpha = in_dict['right_alpha']
        loc = in_dict['loc']
        scale = in_dict['scale']

        x_points = np.sort(x)

        left_tail_x_points = x_points[x_points <= -left_threshold]
        right_tail_x_points = x_points[x_points >= right_threshold]

        left_tail_start_sample = left_tail_x_points[-1]
        right_tail_start_sample = right_tail_x_points[0]

        # Add the transition points if they do not exist
        if left_tail_start_sample not in x_points:
            x_points = np.insert(x_points, 0, left_tail_start_sample)
        if right_tail_start_sample not in x_points:
            x_points = np.insert(x_points, 0, right_tail_start_sample)

        x_points = np.sort(x_points)

        n = len(x_points)
        output_values = np.zeros(n)

        densities = dist.pdf(x_points, *dist_args, loc=loc, scale=scale)
        normalization_factor = np.sum(densities)

        # Get the X-values corresponding to the region of the distribution not on the tail
        center_x_values = x_points[x_points >= left_tail_start_sample]
        center_x_values = center_x_values[center_x_values <= right_tail_start_sample]

        # Get the indices in the x_points which correspond to the center values
        center_x_index = np.flatnonzero(np.isin(x_points, center_x_values))

        output_values[center_x_index] = densities[center_x_index]

        left_tail_x_points = x_points[x_points <= left_tail_start_sample]
        right_tail_x_points = x_points[x_points >= right_tail_start_sample]

        left_tail_x_index = np.flatnonzero(np.isin(x_points, left_tail_x_points))
        right_tail_x_index = np.flatnonzero(np.isin(x_points, right_tail_x_points))

        if len(left_tail_x_points) > 0:
            left_tail_pdf = genpareto.pdf(np.flip(left_tail_start_sample - left_tail_x_points),
                                          1.0 / left_alpha, scale=scale)

            root = brentq(left_tail_helper, 0.0, 0.5,
                          args=(output_values[center_x_index[0]], left_tail_pdf,
                                normalization_factor))

            # print('root: {}'.format(root))

            output_values[left_tail_x_index] = (np.flip(left_tail_pdf) / np.sum(
                left_tail_pdf)) * root * normalization_factor

        if len(right_tail_x_points) > 0:
            right_tail_pdf = genpareto.pdf((right_tail_x_points - right_tail_start_sample),
                                           1.0 / right_alpha, scale=scale)

            root = brentq(right_tail_helper, 0.5, 1.0,
                          args=(
                              output_values[center_x_index[-1]], right_tail_pdf,
                              normalization_factor))

            # print('root: {}'.format(root))

            output_values[right_tail_x_index] = (right_tail_pdf / np.sum(right_tail_pdf)) * (
                    1.0 - float(root)) * normalization_factor

        return output_values

    def _cdf(self, x, *args, loc=0.0, scale=1.0):
        """
        Calculates the CDF function of the distribution which was fit at the specified
        sample_points

        Parameters
        ----------
        sample_points : numpy.ndarray
            The points at which we are calculating the CDF

        Returns
        -------
        cdf_values : numpy.ndarray
            The Y values of the CDF function
        """
        pdf_values = self._pdf(x, *args, loc=loc, scale=scale)
        return np.cumsum(pdf_values / np.sum(pdf_values))

    def _calculate_inverse_cdf(self, x, *args, loc=0.0, scale=1.0):
        """
        Calculates the inverse CDF function of the distribution which was fit at the
        specified sample_points

        Parameters
        ----------
        sample_points : numpy.ndarray
            The points at which we are calculating the inverse CDF

        Returns
        -------
        x_points : numpy.ndarray
            The (sorted) X locations at which the inverse CDF is evaluated
        output_values : numpy.ndarray
            The Y values of the inverse CDF function
        """
        cdf_values = self._cdf(x, *args, loc=loc, scale=scale)

        # Intentionally reversed because it is the inverse
        return cdf_values, x

    def _rvs(self, *args, size=None, random_state=None):
        """
        Generates a certain number of random samples according to the distribution which was fit.
        Method uses inverse transform sampling to generate random samples.

        Parameters
        ----------
        args : List[dict]
            The distribution parameters for which we are generating samples
        size : int
            The number of random samples to generate
        random_state : {None, int, numpy.random.Generator, numpy.random.RandomState}
            (Optional) See scipy.rv_continuous

        Returns
        -------
        output_samples : numpy.ndarray
            The random samples as an array of num_samples length
        """
        samples = np.random.uniform(low=0.0, high=1.0, size=size)

        uniform, random_samples = self._calculate_inverse_cdf(
            np.linspace(-10.0, 10.0, 30000), *args)

        count = 0
        output_samples = np.full_like(samples, 0.0)
        for sample in samples:

            nearest = find_nearest(uniform, sample)
            index_tuple = np.where(uniform == nearest)
            index = index_tuple[0][0]

            # If above, we need to linear intepolate with index-1
            if nearest > sample:

                index_1 = index - 1
                x_1 = uniform[index_1]
                x_2 = nearest
                y_1 = random_samples[index_1]
                y_2 = random_samples[index]
            else:
                index_1 = index + 1
                x_1 = nearest
                x_2 = uniform[index_1]
                y_1 = random_samples[index]
                y_2 = random_samples[index_1]

            slope = (y_2 - y_1) / (x_2 - x_1)
            b = (y_1 * x_2 - y_2 * x_1) / (x_2 - x_1)

            output_samples[count] = slope * sample + b

            count = count + 1

        return output_samples


# Defines this variable as an instance of the class so that it can be used
# like the other scipy.stats distributions
piecewise = PiecewiseDistribution()

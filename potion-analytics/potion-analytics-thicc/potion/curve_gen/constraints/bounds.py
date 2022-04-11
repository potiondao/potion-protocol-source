"""
This module is used by the Generator to constrain the premium points in generated Kelly curves
to lie between an upper and lower bound during optimization.

This is done using a class which follows the duck typed interface of the Generator
and is used by it to apply the constraints.

Callers who wish to replace or customize the behavior of this module need only implement
three duck typed functions:

    configure_convolution(ConstraintsConfig)
        'Configures the settings of this module. See builder module for more info
        on ConstraintsConfig'
    get_lower_bound(dict)
        'Gets a lower bound for the points of the Kelly curve'
    get_upper_bound(dict)
        'Gets an upper bound for the points of the Kelly curve'

Like many python libraries, this module uses a global object with the methods prebound so that
the same library can be used by object-oriented and functional programmers alike. Object-oriented
users can use the BoundaryConstraints class, and functional programmers can use the functions
described above.
"""
import numpy as np

from potion.curve_gen.constraints.builder import ConstraintsConfig, ConstraintsConfigBuilder


class BoundaryConstraints:
    """
    This class constrains the generated premium points of the Kelly curve. This class is
    used by the Generator following a duck typed interface to create curves.
    """

    def __init__(self, config: ConstraintsConfig):
        """
        Constructs the object using the ConstraintsConfig created using the builder module

        Parameters
        ----------
        config : ConstraintsConfig
            The config object created using the builder module
        """
        self.config = config

    def configure(self, config: ConstraintsConfig):
        """
        Changes the config object to a different configuration

        Parameters
        ----------
        config : ConstraintsConfig
            The configuration object to set

        Returns
        -------
        None
        """
        self.config = config

    def get_lower_bound(self, boundary_dict: dict, util: float):
        """
        For the Kelly curve being generated, apply a lower bound to the premium value being
        calculated, according to the current configuration

        Parameters
        ----------
        boundary_dict : dict
            A dict supplying the parameters to the boundary functions needed to calculate the
            lower bound
        util : float
            The util value at which the bounds will be calculated

        Returns
        -------
        lb : float
            The lower bound value
        """
        bounds_dict_util = boundary_dict.copy()
        bounds_dict_util['p_ii'] = bounds_dict_util['p_ii'][util]
        bounds_dict_util['p_iii'] = bounds_dict_util['p_iii'][util]
        if 'p_mm' in bounds_dict_util:
            bounds_dict_util['p_mm'] = bounds_dict_util['p_mm'][util]

        lower_bounds = np.asarray(
            [lb_fcn(bounds_dict_util) for lb_fcn in self.config.lower_premium_bounds])

        # Get the highest lower bound by taking the max
        lower_bounds = lower_bounds[~np.isnan(lower_bounds)]
        return np.amax(lower_bounds)

    def get_upper_bound(self, boundary_dict: dict, util: float):
        """
        For the Kelly curve being generated, apply an upper bound to the premium value being
        calculated, according to the current configuration

        Parameters
        ----------
        boundary_dict : dict
            A dict supplying the parameters to the boundary functions needed to calculate the
            upper bound
        util : float
            The util value at which the bounds will be calculated

        Returns
        -------
        ub : float
            The upper bound value
        """
        bounds_dict_util = boundary_dict.copy()
        bounds_dict_util['p_ii'] = bounds_dict_util['p_ii'][util]
        bounds_dict_util['p_iii'] = bounds_dict_util['p_iii'][util]
        if 'p_mm' in bounds_dict_util:
            bounds_dict_util['p_mm'] = bounds_dict_util['p_mm'][util]

        upper_bounds = np.asarray(
            [ub_fcn(bounds_dict_util) for ub_fcn in self.config.upper_premium_bounds])

        # Get the lowest upper bound by taking the min
        upper_bounds = upper_bounds[~np.isnan(upper_bounds)]
        return np.amin(upper_bounds)


# Define a Global object with default values to be configured by the module user
_bounds = BoundaryConstraints(ConstraintsConfigBuilder().build_config())

# Prebind the object's methods so the module can be used by object oriented and functional
# programmers alike
configure_bounds = _bounds.configure
get_lower_bound = _bounds.get_lower_bound
get_upper_bound = _bounds.get_upper_bound

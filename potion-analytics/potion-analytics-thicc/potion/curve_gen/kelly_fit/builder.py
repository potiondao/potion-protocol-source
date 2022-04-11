"""
This module supplies the FitConfig object and the FitConfigBuilder to allow
users of the library to configure_convolution the best-fit line fit to the Kelly curve. This is
following a standard design pattern. This is the same pattern used by the other
modules of the curve generator and is mirrored here.
"""
from typing import NamedTuple


class FitConfig(NamedTuple):
    """
    Immutable configuration object produced by the builder containing the values to use
    during Kelly curve fitting
    """

    fit_type: str
    """The string identifying which function will be fit to the points of the Kelly curve"""

    def __eq__(self, other):
        """
        Checks if this config object is equal to other

        Parameters
        ----------
        other : FitConfig
            The other config object we are testing for equality

        Returns
        -------
        is_equal : bool
            True if the two objects are equal, False otherwise
        """
        return self.fit_type == other.fit_type


class FitConfigBuilder:
    """
    Standard python builder class for creating immutable configuration objects to use
    with fitting functions to the Kelly curve
    """

    def __init__(self):
        """
        Constructor initializes the builder with default values
        """
        self.fit_type = 'COSH'

    def set_fit_type(self, fit_type: str):
        """
        Sets the function to use when fitting a best-fit curve to the Kelly curve. Currently
        supported options include 'EXP', 'POLY', and 'COSH' for exponential, polynomial, and
        hyperbolic cosine.

        Parameters
        ----------
        fit_type : str
            The function to use when fitting a best-fit curve to the Kelly curve

        Returns
        -------
        self : FitConfigBuilder
            This object following the builder pattern
        """
        self.fit_type = fit_type
        return self

    def build_config(self):
        """
        Creates an immutable FitConfig object from the currently configured builder

        Returns
        -------
        config : FitConfig
            The immutable configuration object
        """
        return FitConfig(self.fit_type)

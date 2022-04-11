"""
This module supplies the PayoffConfig object and the PayoffConfigBuilder to allow
users of the library to configure the payoff of an option or spread of options
following a standard design pattern. This is the same pattern used by the other
modules of the curve generator.
"""
import numpy as np
from typing import NamedTuple, List, Callable

from potion.curve_gen.payoff.helpers import black_scholes_payoff


class PayoffConfig(NamedTuple):
    """
    Immutable configuration object produced by the builder containing the values to use to
    calculate the payoff from the position of options and underlying specified by the caller
    """
    x_points: np.ndarray
    """The X points (prices) of the payoff function where the option payoff will be evaluated"""
    total_payoff: np.ndarray
    """The payoff function calculated from the sum of the option legs payoffs and the 
    underlying payoff"""
    underlying_payoff: np.ndarray
    """The payoff function from holding units of the underlying"""
    option_leg_payoff: List[np.ndarray]
    """The payoff function from each option leg in the spread"""
    option_legs: List[dict]
    """The List containing dicts specifying the info about each leg of the option spread"""

    def __key(self):
        """
        Implements a key function that is unique which can be provided to the __hash__ function

        Returns
        -------
        key : tuple
            The unique key to hash
        """
        return (tuple(self.x_points), tuple(self.total_payoff), tuple(self.underlying_payoff),
                (tuple(pay) for pay in self.option_leg_payoff),
                (tuple(leg) for leg in self.option_legs))

    def __eq__(self, other):
        """
        Checks if this config object is equal to other

        Parameters
        ----------
        other : PayoffConfig
            The other config object we are testing for equality

        Returns
        -------
        is_equal : bool
            True if the two objects are equal, False otherwise
        """
        return np.array_equal(self.x_points, other.x_points) and np.array_equal(
                self.total_payoff, other.total_payoff) and np.array_equal(
            self.underlying_payoff, other.underlying_payoff) and np.array_equal(
            self.option_leg_payoff, other.option_leg_payoff) and (
                self.option_legs == other.option_legs)

    def __hash__(self):
        """
        Implements a hash function for the config object so it can be used with some builtin
        python data structures

        Returns
        -------
        h : int
            The hash of the key
        """
        return hash(self.__key())


class PayoffConfigBuilder:
    """
    Standard python builder class for creating immutable configuration objects to use
    with the option payoff calculations
    """

    def __init__(self):
        """
        Constructor initializes the builder with default values
        """
        self.x_points = np.linspace(0.0, 2.0, 50)
        self.underlying_leg = {
            'price': 0.0,
            'amt': 0.0
        }
        self.option_legs = []
        self.payoff_function = black_scholes_payoff

    def set_payoff_function(self, func: Callable):
        """
        Sets the payoff function which is used to calculate the option's payoff when supplied the
        parameters. Current possibilities include black_scholes_payoff and expiration_only, or
        a custom function supplied by the caller.

        Parameters
        ----------
        func : Callable
            The python function to use to calculate the payoff of the option.

        Returns
        -------
        self : PayoffConfigBuilder
            This object following the builder pattern
        """
        self.payoff_function = func
        return self

    def set_x_points(self, x_points: np.ndarray):
        """
        Sets the X points of the payoff function which are the prices where the payoff
        function will be evaluated

        Parameters
        ----------
        x_points : numpy.ndarray
            The X points of the payoff function where the option payoff will be evaluated

        Returns
        -------
        self : PayoffConfigBuilder
            This object following the builder pattern
        """
        self.x_points = x_points
        return self

    def set_underlying_payoff_leg(self, underlying_price: float, underlying_amount: float):
        """
        Sets the payoff contribution from owning any amount of the underlying asset in the spread.
        This function specifies both the price the underlying was obtained, and the amount of the
        underlying purchased or sold short. If underlying_amount is negative, the position is short.

        Parameters
        ----------
        underlying_price : float
            The price at which the long or short position in the underlying asset was entered
        underlying_amount : float
            The number of units of the underlying long or short. If negative, the position is short

        Returns
        -------
        self : PayoffConfigBuilder
            This object following the builder pattern
        """
        self.underlying_leg = {
            'price': underlying_price,
            'amt': underlying_amount
        }
        return self

    def add_option_leg(self, call_or_put='call', direction='long', amount=1.0, strike=1.0,
                       time_to_exp=0.0, sigma=0.0, r=0.0, q=0.0):
        """
        Adds the parameters of an option leg to a List of dicts which contains the current
        spread legs.

        Parameters
        ----------
        call_or_put : str
            Whether the option leg is a call or a put. Accepted values are 'call' or 'put.
            (Default: 'call')
        direction : str
            Whether the option leg is long or short. Accepted values are 'long' or 'short'
            (Default: 'long')
        amount : float
            The number of option contracts in this leg. (Default: 1.0)
        strike : float
            The strike for the option leg. (Default: 1.0)
        time_to_exp : float
            The time to expiration of the option leg in years. (Default: 0.0 i.e. at expiration)
        sigma : float
            The volatility of the option leg. (Default: 0.0 i.e. at expiration)
        r : float
            The interest rate in years. (Default: 0.0 i.e. 0.02 is 2 percent annually)
        q : float
            The interest rate from cash flows from the underlying in
            years. (Default: 0.0 i.e. 0.02 is 2 percent annually)

        Returns
        -------
        self : PayoffConfigBuilder
            This object following the builder pattern
        """
        self.option_legs.append({
            'type': call_or_put,
            'dir': direction,
            'amt': amount,
            'strike': strike,
            't': time_to_exp,
            'sigma': sigma,
            'r': r,
            'q': q
        })
        return self

    def build_config(self):
        """
        Creates an immutable PayoffConfig object from the currently configured builder

        Returns
        -------
        config : PayoffConfig
            The immutable configuration object
        """
        # Calculates the numpy.ndarray for each option leg payoff
        leg_payoffs = [self.payoff_function(self.x_points, leg_payoff)
                       for leg_payoff in self.option_legs]

        # Calculates the numpy.ndarray for the underlying
        underlying_payoff = (self.x_points -
                             self.underlying_leg['price']) * self.underlying_leg['amt']

        # Sum each payoff and the payoff for the underlying
        total_payoff = underlying_payoff
        for leg_payoff in leg_payoffs:
            total_payoff = total_payoff + leg_payoff

        return PayoffConfig(self.x_points, total_payoff, underlying_payoff, leg_payoffs,
                            self.option_legs)

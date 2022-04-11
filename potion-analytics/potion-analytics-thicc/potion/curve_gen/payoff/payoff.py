"""
This module is used by the Generator to calculate the payoff from an option or spread
of options (or units of the underlying asset).

This is done using a class which follows the duck typed interface of the Generator
and is used by it to create Kelly curves.

Callers who wish to replace or customize the behavior of this module need only implement
three duck typed functions:

    configure_convolution(PayoffConfig)
        'Configures the settings of this module. See builder for more info
        on PayoffConfig'
    get_payoff_odds(float)
        'Which calculates the betting Odds function for the configured position'
    get_position_max_loss(float)
        'Which calculates the max loss of the configured position'

The betting odds payoff is used by the Kelly formula and take the form N-to-1 (i.e. 2-to-1 odds
or 1-to-3 odds).

Like many python libraries, this module uses a global object with the methods prebound so that
the same library can be used by object-oriented and functional programmers alike. Object-oriented
users can use the Payoff class, and functional programmers can use the functions described above.
"""
import numpy as np

from potion.curve_gen.payoff.builder import PayoffConfig, PayoffConfigBuilder
from potion.curve_gen.payoff.black_scholes import check_div_zero


class Payoff:
    """
    This class performs the payoff calculation for the option or spread of options. This class is
    used by the Generator following a duck typed interface to create Kelly curves.
    """

    def __init__(self, config: PayoffConfig):
        """
        Constructs the object using the PayoffConfig created using the builder module

        Parameters
        ----------
        config : PayoffConfig
            The config object created using the builder module
        """
        self.config = config

    def configure(self, config: PayoffConfig):
        """
        Changes the config object to a different configuration

        Parameters
        ----------
        config : PayoffConfig
            The configuration object to set

        Returns
        -------
        None
        """
        self.config = config

    def get_position_max_loss(self, premium=0.0):
        """
        Calculates the worst case loss of the position

        Parameters
        ----------
        premium : float
            The premium collected for the position

        Returns
        -------
        max_loss : float
            The worst case loss of the position
        """
        return check_div_zero(np.abs(np.amin(self.config.total_payoff + premium)))

    def get_payoff_odds(self, premium=0.0):
        """
        Gets the betting Odds function for the position

        Parameters
        ----------
        premium : float
            The premium collected for the position

        Returns
        -------
        odds : numpy.ndarray
            The betting odds function calculated from the option legs and the underlying payout
        """
        ml = np.abs(np.amin(self.config.total_payoff + premium))
        if ml == 0.0:
            raise ValueError('Max Loss cannot be 0.0 in Payoff Odds calculation')

        return (self.config.total_payoff + premium) / self.get_position_max_loss(premium)


# Define a Global object with default values to be configured by the module user
_payoff = Payoff(PayoffConfigBuilder().build_config())

# Prebind the object's methods so the module can be used by object oriented and functional
# programmers alike
configure_payoff = _payoff.configure
get_payoff_odds = _payoff.get_payoff_odds
get_position_max_loss = _payoff.get_position_max_loss

import numpy as np
import unittest

from potion.curve_gen.payoff.helpers import black_scholes_payoff
from potion.curve_gen.payoff.payoff import (Payoff, configure_payoff, get_position_max_loss,
                                            get_payoff_odds)
from potion.curve_gen.payoff.builder import PayoffConfigBuilder


class PayoffTestCase(unittest.TestCase):

    def test_get_position_max_loss(self):

        builder = PayoffConfigBuilder()

        config = builder.set_x_points(np.linspace(0.0, 200.0, 20001)).add_option_leg(
            'call', 'long', 1.0, 100.0, 1.0, 0.1, 0.01, 0.01
        ).build_config()

        # payoff = config.total_payoff - 5.0
        configure_payoff(config)

        self.assertAlmostEqual(5.0, get_position_max_loss(-5.0))

    def test_get_payoff_odds(self):

        builder = PayoffConfigBuilder()

        config = builder.set_x_points(np.linspace(0.0, 200.0, 20001)).add_option_leg(
            'call', 'long', 1.0, 100.0, 1.0, 0.1, 0.01, 0.01
        ).build_config()

        expected_odds = black_scholes_payoff(np.linspace(0.0, 200.0, 20001),
                                             builder.option_legs[0])
        expected_odds = (expected_odds - 5.0) / 5.0

        configure_payoff(config)
        odds = get_payoff_odds(-5.0)

        np.testing.assert_almost_equal(expected_odds, odds, 5)
        self.assertTrue(True)

    def test_payoff_class(self):

        builder = PayoffConfigBuilder()

        config = builder.set_x_points(np.linspace(0.0, 200.0, 20001)).add_option_leg(
            'call', 'long', 1.0, 100.0, 1.0, 0.1, 0.01, 0.01
        ).build_config()

        config2 = builder.set_x_points(np.linspace(0.0, 200.0, 20001)).add_option_leg(
            'put', 'long', 1.0, 100.0, 1.0, 0.1, 0.01, 0.01
        ).build_config()

        payoff = Payoff(config)

        self.assertEqual(config, payoff.config)

        payoff.configure(config2)

        self.assertEqual(config2, payoff.config)

        payoff.configure(config)

        expected_odds = black_scholes_payoff(np.linspace(0.0, 200.0, 20001),
                                             builder.option_legs[0])
        expected_odds = (expected_odds - 5.0) / 5.0

        odds = payoff.get_payoff_odds(-5.0)

        self.assertAlmostEqual(5.0, get_position_max_loss(-5.0))
        np.testing.assert_almost_equal(expected_odds, odds, 5)


if __name__ == '__main__':
    unittest.main()

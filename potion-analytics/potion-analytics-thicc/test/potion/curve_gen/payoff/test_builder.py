import unittest
import numpy as np

from potion.curve_gen.payoff.helpers import black_scholes_payoff, expiration_only
from potion.curve_gen.payoff.builder import PayoffConfigBuilder


class PayoffBuilderTestCase(unittest.TestCase):

    def test_init(self):
        builder = PayoffConfigBuilder()

        np.testing.assert_almost_equal(builder.x_points, np.linspace(0.0, 2.0, 50), 5)
        self.assertAlmostEqual(builder.underlying_leg['price'], 0.0, 5)
        self.assertAlmostEqual(builder.underlying_leg['amt'], 0.0, 5)
        self.assertListEqual([], builder.option_legs)
        self.assertEqual(builder.payoff_function, black_scholes_payoff)

    def test_set_payoff_function(self):
        builder = PayoffConfigBuilder()

        builder.set_payoff_function(expiration_only)

        self.assertEqual(builder.payoff_function, expiration_only)

    def test_set_underlying_payoff_leg(self):
        builder = PayoffConfigBuilder()

        builder.set_underlying_payoff_leg(100.0, 10.0)

        self.assertAlmostEqual(builder.underlying_leg['price'], 100.0, 5)
        self.assertAlmostEqual(builder.underlying_leg['amt'], 10.0, 5)

    def test_add_option_leg(self):
        builder = PayoffConfigBuilder()

        builder.set_x_points(np.linspace(0.0, 200.0, 20001)).add_option_leg(
            'call', 'short', 1.0, 98.0, 1.0, 0.1, 0.01, 0.01).add_option_leg(
            'call', 'long', 1.0, 99.0, 1.0, 0.1, 0.01, 0.01).add_option_leg(
            'put', 'long', 1.0, 101.0, 1.0, 0.1, 0.01, 0.01).add_option_leg(
            'put', 'short', 1.0, 102.0, 1.0, 0.1, 0.01, 0.01)

        self.assertEqual('call', builder.option_legs[0]['type'])
        self.assertEqual('short', builder.option_legs[0]['dir'])
        self.assertAlmostEqual(1.0, builder.option_legs[0]['amt'], 5)
        self.assertAlmostEqual(98.0, builder.option_legs[0]['strike'], 5)
        self.assertAlmostEqual(1.0, builder.option_legs[0]['t'], 5)
        self.assertAlmostEqual(0.1, builder.option_legs[0]['sigma'], 5)
        self.assertAlmostEqual(0.01, builder.option_legs[0]['r'], 5)
        self.assertAlmostEqual(0.01, builder.option_legs[0]['q'], 5)

        self.assertEqual('call', builder.option_legs[1]['type'])
        self.assertEqual('long', builder.option_legs[1]['dir'])
        self.assertAlmostEqual(1.0, builder.option_legs[1]['amt'], 5)
        self.assertAlmostEqual(99.0, builder.option_legs[1]['strike'], 5)
        self.assertAlmostEqual(1.0, builder.option_legs[1]['t'], 5)
        self.assertAlmostEqual(0.1, builder.option_legs[1]['sigma'], 5)
        self.assertAlmostEqual(0.01, builder.option_legs[1]['r'], 5)
        self.assertAlmostEqual(0.01, builder.option_legs[1]['q'], 5)

        self.assertEqual('put', builder.option_legs[2]['type'])
        self.assertEqual('long', builder.option_legs[2]['dir'])
        self.assertAlmostEqual(1.0, builder.option_legs[2]['amt'], 5)
        self.assertAlmostEqual(101.0, builder.option_legs[2]['strike'], 5)
        self.assertAlmostEqual(1.0, builder.option_legs[2]['t'], 5)
        self.assertAlmostEqual(0.1, builder.option_legs[2]['sigma'], 5)
        self.assertAlmostEqual(0.01, builder.option_legs[2]['r'], 5)
        self.assertAlmostEqual(0.01, builder.option_legs[2]['q'], 5)

    def test_build_config(self):

        builder = PayoffConfigBuilder()

        config = builder.set_x_points(np.linspace(0.0, 200.0, 20001)).add_option_leg(
            'call', 'short', 10.0, 98.0, 1.0, 0.1, 0.01, 0.01
        ).set_underlying_payoff_leg(100.0, 1.0).build_config()

        np.testing.assert_almost_equal(config.x_points, np.linspace(0.0, 200.0, 20001), 5)
        np.testing.assert_almost_equal(config.underlying_payoff,
                                       np.linspace(-100.0, 100.0, 20001), 5)
        np.testing.assert_almost_equal(config.option_leg_payoff[0],
                                       black_scholes_payoff(config.x_points,
                                                            config.option_legs[0]), 5)
        np.testing.assert_almost_equal(config.total_payoff,
                                       black_scholes_payoff(config.x_points,
                                                            config.option_legs[0]) +
                                       config.underlying_payoff, 5)

        self.assertEqual('call', config.option_legs[0]['type'])
        self.assertEqual('short', config.option_legs[0]['dir'])
        self.assertAlmostEqual(10.0, config.option_legs[0]['amt'], 5)
        self.assertAlmostEqual(98.0, config.option_legs[0]['strike'], 5)
        self.assertAlmostEqual(1.0, config.option_legs[0]['t'], 5)
        self.assertAlmostEqual(0.1, config.option_legs[0]['sigma'], 5)
        self.assertAlmostEqual(0.01, config.option_legs[0]['r'], 5)
        self.assertAlmostEqual(0.01, config.option_legs[0]['q'], 5)


if __name__ == '__main__':
    unittest.main()

import unittest
import numpy as np

from potion.curve_gen.payoff.helpers import (_bs_long_call, _bs_short_call, _bs_long_put,
                                            _bs_short_put, black_scholes_payoff,
                                            expiration_only)


class HelpersCase(unittest.TestCase):

    def test_bs_long_call(self):

        x = np.linspace(0, 200.0, 2000)

        option_leg = {
            'type': 'call',
            'dir': 'long',
            'strike': 100.0,
            't': 0.0,
            'sigma': 10.0 / 100.0,
            'r': 1.0 / 100.0,
            'q': 1.0 / 100.0,
            'amt': 10.0
        }

        payoff = _bs_long_call(x, option_leg, 5.0)
        eo_payoff = expiration_only(x, option_leg, 5.0)

        np.testing.assert_almost_equal(payoff, eo_payoff, 5)
        self.assertTrue(True)

    def test_bs_short_call(self):

        x = np.linspace(0, 200.0, 2000)

        option_leg = {
            'type': 'call',
            'dir': 'short',
            'strike': 100.0,
            't': 0.0,
            'sigma': 10.0 / 100.0,
            'r': 1.0 / 100.0,
            'q': 1.0 / 100.0,
            'amt': 10.0
        }

        payoff = _bs_short_call(x, option_leg, 5.0)
        eo_payoff = expiration_only(x, option_leg, 5.0)

        np.testing.assert_almost_equal(payoff, eo_payoff, 5)
        self.assertTrue(True)

    def test_bs_long_put(self):

        x = np.linspace(0, 200.0, 2000)

        option_leg = {
            'type': 'put',
            'dir': 'long',
            'strike': 100.0,
            't': 0.0,
            'sigma': 10.0 / 100.0,
            'r': 1.0 / 100.0,
            'q': 1.0 / 100.0,
            'amt': 10.0
        }

        payoff = _bs_long_put(x, option_leg, 5.0)
        eo_payoff = expiration_only(x, option_leg, 5.0)

        np.testing.assert_almost_equal(payoff, eo_payoff, 5)
        self.assertTrue(True)

    def test_bs_short_put(self):

        x = np.linspace(0, 200.0, 2000)

        option_leg = {
            'type': 'put',
            'dir': 'short',
            'strike': 100.0,
            't': 0.0,
            'sigma': 10.0 / 100.0,
            'r': 1.0 / 100.0,
            'q': 1.0 / 100.0,
            'amt': 10.0
        }

        payoff = _bs_short_put(x, option_leg, 5.0)
        eo_payoff = expiration_only(x, option_leg, 5.0)

        np.testing.assert_almost_equal(payoff, eo_payoff, 5)
        self.assertTrue(True)

    def test_black_scholes_payoff(self):

        x = np.linspace(0, 200.0, 2000)

        option_leg = {
            'type': 'call',
            'dir': 'long',
            'strike': 100.0,
            't': 0.0,
            'sigma': 10.0 / 100.0,
            'r': 1.0 / 100.0,
            'q': 1.0 / 100.0,
            'amt': 10.0
        }

        payoff = black_scholes_payoff(x, option_leg, 5.0)
        eo_payoff = expiration_only(x, option_leg, 5.0)

        np.testing.assert_almost_equal(payoff, eo_payoff, 5)

        option_leg = {
            'type': 'call',
            'dir': 'short',
            'strike': 100.0,
            't': 0.0,
            'sigma': 10.0 / 100.0,
            'r': 1.0 / 100.0,
            'q': 1.0 / 100.0,
            'amt': 10.0
        }

        payoff = black_scholes_payoff(x, option_leg, 5.0)
        eo_payoff = expiration_only(x, option_leg, 5.0)

        np.testing.assert_almost_equal(payoff, eo_payoff, 5)

        option_leg = {
            'type': 'put',
            'dir': 'long',
            'strike': 100.0,
            't': 0.0,
            'sigma': 10.0 / 100.0,
            'r': 1.0 / 100.0,
            'q': 1.0 / 100.0,
            'amt': 10.0
        }

        payoff = black_scholes_payoff(x, option_leg, 5.0)
        eo_payoff = expiration_only(x, option_leg, 5.0)

        np.testing.assert_almost_equal(payoff, eo_payoff, 5)

        option_leg = {
            'type': 'put',
            'dir': 'short',
            'strike': 100.0,
            't': 0.0,
            'sigma': 10.0 / 100.0,
            'r': 1.0 / 100.0,
            'q': 1.0 / 100.0,
            'amt': 10.0
        }

        payoff = black_scholes_payoff(x, option_leg, 5.0)
        eo_payoff = expiration_only(x, option_leg, 5.0)

        np.testing.assert_almost_equal(payoff, eo_payoff, 5)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()

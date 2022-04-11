import unittest
import numpy as np
# import matplotlib.pyplot as plt
from potion.curve_gen.payoff.black_scholes import call, put


class BlackScholesTestCase(unittest.TestCase):

    def test_prices(self):

        min_x = 0
        max_x = 200
        num_points = 201

        x = np.linspace(min_x, max_x, num_points)

        strike = 100.0
        r = 1.0 / 100.0
        q = 1.0 / 100.0
        tau = 0.0 / 365.0
        sigma = 30 / 100.0

        # print('Strike: {} Sigma: {} Tau: {} r: {} q: {}'.format(strike, sigma, tau, r, q))

        call_prices = [call(x_i, strike, tau, sigma, r, q)[0] for x_i in x]
        put_prices = [put(x_i, strike, tau, sigma, r, q)[0] for x_i in x]

        # plt.figure()
        # plt.plot(x, call_prices)
        # plt.plot(x, list(reversed(put_prices)))
        # plt.grid(True)
        # plt.title('Option Prices')
        # plt.xlabel('Underlying Price')
        # plt.ylabel('Payout')
        # plt.legend(['Call Price', 'Put Price'])
        # plt.show()

        np.testing.assert_almost_equal(call_prices, list(reversed(put_prices)), 5)
        self.assertTrue(True)

    def test_delta(self):

        strike = 100.0
        r = 1.0 / 100.0
        q = 1.0 / 100.0
        tau = 365.0 / 365.0
        sigma = 50 / 100.0

        # print('Strike: {} Sigma: {} Tau: {} r: {} q: {}'.format(strike, sigma, tau, r, q))

        call_price, call_greeks = call(100.0, strike, tau, sigma, r, q, calculate_greeks=True)
        put_price, put_greeks = put(100.0, strike, tau, sigma, r, q, calculate_greeks=True)

        call_delta = call_greeks['delta']
        put_delta = put_greeks['delta']

        # print('Call Price: {} Call Delta: {} Put Price: {} Put Delta: {}'.format(
        #     call_price, call_delta, put_price, put_delta))

        call_price2 = call(101.0, strike, tau, sigma, r, q)[0]
        put_price2 = put(101.0, strike, tau, sigma, r, q)[0]

        # print('Actual Call Delta: {}'.format(call_price2 - call_price))
        # print('Actual Put Delta: {}'.format(put_price2 - put_price))

        self.assertAlmostEqual(call_delta, (call_price2 - call_price), 2)
        self.assertAlmostEqual(put_delta, (put_price2 - put_price), 2)

    def test_gamma(self):

        strike = 100.0
        r = 1.0 / 100.0
        q = 1.0 / 100.0
        tau = 365.0 / 365.0
        sigma = 50 / 100.0

        # print('Strike: {} Sigma: {} Tau: {} r: {} q: {}'.format(strike, sigma, tau, r, q))

        call_price, call_greeks = call(100.0, strike, tau, sigma, r, q, calculate_greeks=True)
        put_price, put_greeks = put(100.0, strike, tau, sigma, r, q, calculate_greeks=True)

        call_gamma = call_greeks['gamma']
        put_gamma = put_greeks['gamma']

        call_delta = call_greeks['delta']
        put_delta = put_greeks['delta']

        # print('Call Delta: {} Call Gamma: {} Put Delta: {} Put Gamma: {}'.format(
        #     call_delta, call_gamma, put_delta, put_gamma))

        call_price2, call_greeks2 = call(101.0, strike, tau, sigma, r, q, calculate_greeks=True)
        put_price2, put_greeks2 = put(101.0, strike, tau, sigma, r, q, calculate_greeks=True)

        # print('Actual Call Gamma: {}'.format(call_greeks2['delta'] - call_delta))
        # print('Actual Put Gamma: {}'.format(put_greeks2['delta'] - put_delta))

        self.assertAlmostEqual(call_gamma, (call_greeks2['delta'] - call_delta), 2)
        self.assertAlmostEqual(put_gamma, (put_greeks2['delta'] - put_delta), 2)

    def test_theta(self):

        strike = 100.0
        r = 1.0 / 100.0
        q = 1.0 / 100.0
        tau = 1.0
        sigma = 10.0 / 100.0

        # print('Strike: {} Sigma: {} Tau: {} r: {} q: {}'.format(strike, sigma, tau, r, q))

        call_price, call_greeks = call(100.0, strike, tau, sigma, r, q, calculate_greeks=True)
        put_price, put_greeks = put(100.0, strike, tau, sigma, r, q, calculate_greeks=True)

        call_theta = call_greeks['theta']
        put_theta = put_greeks['theta']

        self.assertAlmostEqual(3.9480, call_price, 3)
        self.assertAlmostEqual(3.9480, put_price, 3)
        self.assertAlmostEqual(-1.932916, call_theta, 3)
        self.assertAlmostEqual(-1.932916, put_theta, 3)

        # print('Call Price: {} Call Theta: {} Put Price: {} Put Theta: {}'.format(
        #     call_price, call_theta, put_price, put_theta))

        new_tau = 0.5
        call_price2, call_greeks2 = call(100.0, strike, new_tau, sigma, r, q, calculate_greeks=True)
        put_price2, put_greeks2 = put(100.0, strike, new_tau, sigma, r, q, calculate_greeks=True)

        call_theta2 = call_greeks2['theta']
        put_theta2 = put_greeks2['theta']

        self.assertAlmostEqual(2.8063, call_price2, 3)
        self.assertAlmostEqual(2.8063, put_price2, 3)
        self.assertAlmostEqual(-2.777, call_theta2, 3)
        self.assertAlmostEqual(-2.777, put_theta2, 3)

    def test_vega(self):

        strike = 100.0
        r = 1.0 / 100.0
        q = 1.0 / 100.0
        tau = 1.0
        sigma = 10.0 / 100.0

        # print('Strike: {} Sigma: {} Tau: {} r: {} q: {}'.format(strike, sigma, tau, r, q))

        call_price, call_greeks = call(100.0, strike, tau, sigma, r, q, calculate_greeks=True)
        put_price, put_greeks = put(100.0, strike, tau, sigma, r, q, calculate_greeks=True)

        call_vega = call_greeks['vega']
        put_vega = put_greeks['vega']

        self.assertAlmostEqual(3.9480, call_price, 3)
        self.assertAlmostEqual(3.9480, put_price, 3)
        self.assertAlmostEqual(39.44793, call_vega, 3)
        self.assertAlmostEqual(39.44793, put_vega, 3)

        new_tau = 0.5
        call_price2, call_greeks2 = call(100.0, strike, new_tau, sigma, r, q, calculate_greeks=True)
        put_price2, put_greeks2 = put(100.0, strike, new_tau, sigma, r, q, calculate_greeks=True)

        call_vega2 = call_greeks2['vega']
        put_vega2 = put_greeks2['vega']

        self.assertAlmostEqual(2.8063, call_price2, 3)
        self.assertAlmostEqual(2.8063, put_price2, 3)
        self.assertAlmostEqual(28.05125, call_vega2, 3)
        self.assertAlmostEqual(28.05125, put_vega2, 3)

    def test_rho_r(self):

        strike = 100.0
        r = 1.0 / 100.0
        q = 1.0 / 100.0
        tau = 1.0
        sigma = 10.0 / 100.0

        # print('Strike: {} Sigma: {} Tau: {} r: {} q: {}'.format(strike, sigma, tau, r, q))

        call_price, call_greeks = call(100.0, strike, tau, sigma, r, q, calculate_greeks=True)
        put_price, put_greeks = put(100.0, strike, tau, sigma, r, q, calculate_greeks=True)

        call_rho_r = call_greeks['rho_r']
        put_rho_r = put_greeks['rho_r']

        self.assertAlmostEqual(3.9480, call_price, 3)
        self.assertAlmostEqual(3.9480, put_price, 3)
        self.assertAlmostEqual(47.52845, call_rho_r, 3)
        self.assertAlmostEqual(-51.47653, put_rho_r, 3)

        new_tau = 0.5
        call_price2, call_greeks2 = call(100.0, strike, new_tau, sigma, r, q, calculate_greeks=True)
        put_price2, put_greeks2 = put(100.0, strike, new_tau, sigma, r, q, calculate_greeks=True)

        call_rho_r2 = call_greeks2['rho_r']
        put_rho_r2 = put_greeks2['rho_r']

        self.assertAlmostEqual(2.8063, call_price2, 3)
        self.assertAlmostEqual(2.8063, put_price2, 3)
        self.assertAlmostEqual(24.17374, call_rho_r2, 3)
        self.assertAlmostEqual(-25.57689, put_rho_r2, 3)

    def test_rho_q(self):

        strike = 100.0
        r = 1.0 / 100.0
        q = 1.0 / 100.0
        tau = 1.0
        sigma = 10.0 / 100.0

        # print('Strike: {} Sigma: {} Tau: {} r: {} q: {}'.format(strike, sigma, tau, r, q))

        call_price, call_greeks = call(100.0, strike, tau, sigma, r, q, calculate_greeks=True)
        put_price, put_greeks = put(100.0, strike, tau, sigma, r, q, calculate_greeks=True)

        call_rho_q = call_greeks['rho_q']
        put_rho_q = put_greeks['rho_q']

        self.assertAlmostEqual(3.9480, call_price, 3)
        self.assertAlmostEqual(3.9480, put_price, 3)
        self.assertAlmostEqual(-51.47653, call_rho_q, 3)
        self.assertAlmostEqual(47.52845, put_rho_q, 3)

        new_tau = 0.5
        call_price2, call_greeks2 = call(100.0, strike, new_tau, sigma, r, q, calculate_greeks=True)
        put_price2, put_greeks2 = put(100.0, strike, new_tau, sigma, r, q, calculate_greeks=True)

        call_rho_q2 = call_greeks2['rho_q']
        put_rho_q2 = put_greeks2['rho_q']

        self.assertAlmostEqual(2.8063, call_price2, 3)
        self.assertAlmostEqual(2.8063, put_price2, 3)
        self.assertAlmostEqual(-25.57689, call_rho_q2, 3)
        self.assertAlmostEqual(24.17374, put_rho_q2, 3)


if __name__ == '__main__':
    unittest.main()

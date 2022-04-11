
import unittest
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import skewnorm
from potion.curve_gen.kelly import kelly_formula, probability_from_density


class KellyTestCase(unittest.TestCase):

    def test_kelly(self):

        x_min = -6.0
        x_max = 6.0
        num_points = 10000

        x = np.linspace(x_min, x_max, num_points)

        pdf = skewnorm.pdf(x, 1.5)

        payoff = np.full_like(x, 0.0)

        # Payoff for coin flip tails
        payoff[0:int((num_points - 1)/2.0)] = -1.0

        # Payoff for coin flip heads
        payoff[int((num_points - 1) / 2.0):] = 0.35

        bet_fractions = np.linspace(0.0001, 0.999, 1000)
        log_expected_growth = np.full_like(bet_fractions, 0.0)

        prob_bins = probability_from_density(x, pdf)

        for i in range(bet_fractions.size):
            bf = bet_fractions[i]
            log_expected_growth[i] = kelly_formula(prob_bins, payoff, bf)

        max_index = np.argmax(log_expected_growth)
        max_value = log_expected_growth[max_index]
        opt_frac = bet_fractions[max_index]

        print('Maximum Value Index: {}'.format(max_index))
        print('Maximum Value: {}'.format(max_value))
        print('Optimal Betting Fraction: {}'.format(opt_frac))

        growth_per_bet = np.exp(max_value)
        print('Growth Per Bet: {}'.format(growth_per_bet))

        num_bets_per_year = 5
        cagr = ((growth_per_bet ** num_bets_per_year) - 1.0) * 100.0

        print('Num Bets Per Year: {}'.format(num_bets_per_year))
        print('CAGR: {}'.format(cagr))

        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot(x, pdf)
        ax1.plot(x, payoff)
        legend_list = ['PDF', 'Odds Payout']
        ax1.legend(legend_list)
        ax1.set_xlabel('Outcome')
        ax1.set_ylabel('Probability and Odds Payout')
        ax1.grid(True)

        ax2.plot(bet_fractions, log_expected_growth)
        legend_list = ['Log Expected Growth Rate']
        ax2.legend(legend_list)
        ax2.set_xlabel('Betting Fraction (0-100%)')
        ax2.set_ylabel('Log Expected Growth Rate')
        ax2.grid(True)

        plt.show()

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

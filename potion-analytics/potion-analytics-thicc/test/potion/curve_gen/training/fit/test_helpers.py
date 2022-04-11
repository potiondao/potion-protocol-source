import unittest
import pandas as pd

from potion.curve_gen.training.fit.helpers import calc_log_returns, calc_simple_returns


class FitHelpersTestCase(unittest.TestCase):

    def test_calc_simple_returns(self):

        prices = [1.0, 2.0, 3.0, 4.0]

        returns = calc_simple_returns(pd.DataFrame(prices)).to_numpy().reshape(-1).tolist()

        self.assertEqual(1.0, returns[0])
        self.assertEqual(0.5, returns[1])
        self.assertAlmostEqual(0.3333, returns[2], 4)

    def test_calc_log_returns(self):

        prices = [1.0, 2.0, 3.0, 4.0]

        returns = calc_log_returns(pd.DataFrame(prices)).to_numpy().reshape(-1).tolist()

        self.assertAlmostEqual(0.6931471805599453, returns[0], 4)
        self.assertAlmostEqual(0.4054651081081644, returns[1], 4)
        self.assertAlmostEqual(0.28768207245178085, returns[2], 4)

        prices = [4.0, 3.0, 2.0, 1.0]

        returns = calc_log_returns(pd.DataFrame(prices)).to_numpy().reshape(-1).tolist()

        self.assertAlmostEqual(-0.6931471805599453, returns[2], 4)
        self.assertAlmostEqual(-0.4054651081081644, returns[1], 4)
        self.assertAlmostEqual(-0.28768207245178085, returns[0], 4)


if __name__ == '__main__':
    unittest.main()

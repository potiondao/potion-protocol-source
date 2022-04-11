import unittest
import numpy as np

from potion.curve_gen.kelly_fit.builder import FitConfigBuilder
from potion.curve_gen.kelly_fit.kelly_fit import (_fit_cosh, _fit_exp, KellyFit)


class KellyFitTestCase(unittest.TestCase):

    def test_init(self):

        builder = FitConfigBuilder()

        config = builder.build_config()

        fit = KellyFit(config)

        self.assertEqual('COSH', fit.config.fit_type)
        self.assertEqual(_fit_cosh, fit.fit_func)

    def test_configure(self):

        builder = FitConfigBuilder()

        config = builder.build_config()

        fit = KellyFit(config)

        config2 = builder.set_fit_type('EXP').build_config()
        fit.configure(config2)

        self.assertEqual('EXP', fit.config.fit_type)
        self.assertEqual(_fit_exp, fit.fit_func)

    def test_fit_kelly_curve(self):

        builder = FitConfigBuilder()

        config = builder.build_config()

        fit = KellyFit(config)

        params = fit.fit_kelly_curve(np.linspace(0.0, 1.0, 100), np.linspace(0.1, 0.7, 100))

        self.assertEqual(4, len(params))
        self.assertAlmostEqual(0.1, params[3], 5)


if __name__ == '__main__':
    unittest.main()

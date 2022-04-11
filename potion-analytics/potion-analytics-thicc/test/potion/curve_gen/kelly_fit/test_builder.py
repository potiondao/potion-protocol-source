import unittest

from potion.curve_gen.kelly_fit.builder import FitConfigBuilder


class KellyFitBuilderTestCase(unittest.TestCase):

    def test_init(self):

        builder = FitConfigBuilder()

        self.assertEqual('COSH', builder.fit_type)

    def test_set_fit_type(self):

        builder = FitConfigBuilder()

        builder.set_fit_type('EXP')

        self.assertEqual('EXP', builder.fit_type)

    def test_build_config(self):

        builder = FitConfigBuilder()

        config = builder.build_config()

        self.assertEqual('COSH', config.fit_type)


if __name__ == '__main__':
    unittest.main()

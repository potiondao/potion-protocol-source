import unittest

from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder


class ConstraintsBuilderTestCase(unittest.TestCase):

    def test_init(self):

        builder = ConstraintsConfigBuilder()

        self.assertEqual([], builder.lower_bounds)
        self.assertEqual([], builder.upper_bounds)

    def test_add_upper_bound(self):

        builder = ConstraintsConfigBuilder()

        builder.add_upper_bound(lambda a: 0.5)

        self.assertEqual(0.5, builder.upper_bounds[0](dict()))

    def test_add_lower_bound(self):

        builder = ConstraintsConfigBuilder()

        builder.add_lower_bound(lambda a: 0.3)

        self.assertEqual(0.3, builder.lower_bounds[0](dict()))

    def test_build_config(self):

        builder = ConstraintsConfigBuilder()

        builder.add_lower_bound(lambda a: 0.3)
        builder.add_upper_bound(lambda a: 0.5)

        config = builder.build_config()

        self.assertEqual(0.3, config.lower_premium_bounds[0](dict()))
        self.assertEqual(0.5, config.upper_premium_bounds[0](dict()))


if __name__ == '__main__':
    unittest.main()

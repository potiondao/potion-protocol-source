import unittest

from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder
from potion.curve_gen.constraints.bounds import BoundaryConstraints


class BoundaryConstraintsTestCase(unittest.TestCase):

    def test_init(self):
        config = ConstraintsConfigBuilder().build_config()

        bounds = BoundaryConstraints(config)

        self.assertEqual(config, bounds.config)

    def test_configure(self):
        config = ConstraintsConfigBuilder().build_config()

        bounds = BoundaryConstraints(config)

        self.assertEqual(config, bounds.config)

        config2 = ConstraintsConfigBuilder().add_lower_bound(
            lambda a: 0.3).add_upper_bound(lambda a: 0.5).build_config()

        bounds.configure(config2)

        self.assertEqual(config2, bounds.config)

    def test_get_lower_bound(self):

        config = ConstraintsConfigBuilder().add_lower_bound(
            lambda a: 0.30).add_lower_bound(
            lambda a: 0.25).add_lower_bound(
            lambda a: 0.20).add_lower_bound(
            lambda a: 0.15).add_lower_bound(
            lambda a: 0.10).add_upper_bound(
            lambda a: 0.50).add_upper_bound(
            lambda a: 0.55).add_upper_bound(
            lambda a: 0.60).add_upper_bound(
            lambda a: 0.65).add_upper_bound(
            lambda a: 0.70).build_config()

        bounds = BoundaryConstraints(config)

        self.assertEqual(config, bounds.config)
        self.assertEqual(0.3, bounds.get_lower_bound({}))

    def test_get_upper_bound(self):

        config = ConstraintsConfigBuilder().add_lower_bound(
            lambda a: 0.30).add_lower_bound(
            lambda a: 0.25).add_lower_bound(
            lambda a: 0.20).add_lower_bound(
            lambda a: 0.15).add_lower_bound(
            lambda a: 0.10).add_upper_bound(
            lambda a: 0.50).add_upper_bound(
            lambda a: 0.55).add_upper_bound(
            lambda a: 0.60).add_upper_bound(
            lambda a: 0.65).add_upper_bound(
            lambda a: 0.70).build_config()

        bounds = BoundaryConstraints(config)

        self.assertEqual(config, bounds.config)
        self.assertEqual(0.5, bounds.get_upper_bound({}))


if __name__ == '__main__':
    unittest.main()

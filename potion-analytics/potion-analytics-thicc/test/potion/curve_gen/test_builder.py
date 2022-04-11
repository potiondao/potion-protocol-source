import unittest

from potion.curve_gen.training.builder import TrainingConfigBuilder
from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder
from potion.curve_gen.kelly_fit.builder import FitConfigBuilder
from potion.curve_gen.builder import GeneratorConfigBuilder


class GeneratorConfigBuilderTestCase(unittest.TestCase):

    def test_init(self):

        bldr = GeneratorConfigBuilder()

        self.assertIsNotNone(bldr.train_builder)
        self.assertIsNotNone(bldr.bounds_builder)
        self.assertIsNotNone(bldr.fit_builder)

    def test_set_training_builder(self):

        trn_cfg = TrainingConfigBuilder()
        bnds_cfg = ConstraintsConfigBuilder()
        fit_cfg = FitConfigBuilder()

        bldr = GeneratorConfigBuilder()

        bldr.set_training_builder(trn_cfg)

        self.assertEqual(trn_cfg, bldr.train_builder)

    def test_set_fit_builder(self):

        fit_cfg = FitConfigBuilder()

        bldr = GeneratorConfigBuilder()

        bldr.set_fit_builder(fit_cfg)

        self.assertEqual(fit_cfg, bldr.fit_builder)

    def test_set_bounds_builder(self):

        bnds_cfg = ConstraintsConfigBuilder()

        bldr = GeneratorConfigBuilder()

        bldr.set_bounds_builder(bnds_cfg)

        self.assertEqual(bnds_cfg, bldr.bounds_builder)

    def test_build_config(self):

        trn_cfg = TrainingConfigBuilder()
        bnds_cfg = ConstraintsConfigBuilder()
        fit_cfg = FitConfigBuilder()

        bldr = GeneratorConfigBuilder()

        config = bldr.set_training_builder(trn_cfg).set_fit_builder(
            fit_cfg).set_bounds_builder(bnds_cfg).build_config()

        expected_trn = trn_cfg.build_config()
        expected_bnds = bnds_cfg.build_config()
        expected_fit = fit_cfg.build_config()

        self.assertEqual(expected_trn, config.train_config)
        self.assertEqual(expected_bnds, config.bounds_config)
        self.assertEqual(expected_fit, config.fit_config)


if __name__ == '__main__':
    unittest.main()

import unittest
import pandas as pd

from potion.curve_gen.training.builder import TrainingConfigBuilder, TrainingConfig


class TrainingConfigBuilderTestCase(unittest.TestCase):

    def test_init(self):

        builder = TrainingConfigBuilder()

        self.assertIsNone(builder.training_history_filename)
        self.assertIsNone(builder.input_csv_filename)

    def test_set_training_history_filename(self):

        builder = TrainingConfigBuilder()

        builder.set_training_history_filename('test.csv')

        self.assertEqual('test.csv', builder.training_history_filename)

    def test_set_input_csv_filename(self):

        builder = TrainingConfigBuilder()

        builder.set_input_csv_filename('test.csv')

        self.assertEqual('test.csv', builder.input_csv_filename)

    def test_build_config(self):

        builder = TrainingConfigBuilder()

        self.assertEqual(TrainingConfig(pd.DataFrame(), pd.DataFrame()), builder.build_config())

        builder.set_input_csv_filename('')
        builder.set_training_history_filename('')

        self.assertRaises(FileNotFoundError, builder.build_config)

        builder.set_training_history_filename('../../../../README.md')

        self.assertRaises(ValueError, builder.build_config)

        builder.set_input_csv_filename('../../../../README.md')

        self.assertRaises(ValueError, builder.build_config)

        builder.set_training_history_filename('../../../../resources/webapp-coins.csv')
        builder.set_input_csv_filename('../../../../inputs/ExampleCurveGenInputSingle.csv')

        config = builder.build_config()

        self.assertEqual(1, len(config.input_df))
        self.assertEqual(7, len(config.input_df.columns))


if __name__ == '__main__':
    unittest.main()

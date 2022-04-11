import unittest
import pandas as pd
import numpy as np
from datetime import date

from scipy.stats import norm, skewnorm

from potion.curve_gen.training.distributions.skewed_students_t import skewed_t
from potion.curve_gen.training.train import (Trainer, get_training_dates, parse_date_from_str,
                                             swap_params, _extract_historical_price_path,
                                             _fit_params_from_prices)
from potion.curve_gen.training.builder import TrainingConfigBuilder


class TrainerTestCase(unittest.TestCase):

    def test_get_training_dates(self):

        csv_df = pd.read_csv('../../../../resources/webapp-coins.csv')

        dates = get_training_dates(csv_df)

        [self.assertIsInstance(d, date) for d in dates]

    def test_parse_date_from_str(self):

        csv_df = pd.read_csv('../../../../resources/webapp-coins.csv')
        dates = get_training_dates(csv_df)

        prices = pd.DataFrame(np.full_like(dates, 5.0))

        parsed_date, parsed_index = parse_date_from_str('28/04/2013', dates, prices)

        self.assertEqual(date(2013, 4, 28), parsed_date)
        self.assertEqual(0, parsed_index)

        parsed_date, parsed_index = parse_date_from_str('min', dates, prices)

        self.assertEqual(date(2013, 4, 28), parsed_date)
        self.assertEqual(0, parsed_index)

    def test_extract_historical_price_path(self):

        csv_df = pd.read_csv('../../../../resources/webapp-coins.csv')
        dates = get_training_dates(csv_df)

        start, end, prices = _extract_historical_price_path(csv_df, dates, 'bitcoin', 'min', 'max')

        self.assertEqual(start, dates[0])
        self.assertEqual(end, dates[-1])
        self.assertEqual(len(dates), len(prices))

    def test_swap_params(self):

        dist_params = [1.0, 2.0]
        dist_params = swap_params(dist_params)

        self.assertEqual(1.0, dist_params[0])
        self.assertEqual(2.0, dist_params[1])

        dist_params = [1.0, 2.0, 3.0]
        dist_params = swap_params(dist_params)

        self.assertEqual(2.0, dist_params[0])
        self.assertEqual(3.0, dist_params[1])
        self.assertEqual(1.0, dist_params[2])

        dist_params = [1.0, 2.0, 3.0, 4.0]
        dist_params = swap_params(dist_params)

        self.assertEqual(3.0, dist_params[0])
        self.assertEqual(4.0, dist_params[1])
        self.assertEqual(1.0, dist_params[2])
        self.assertEqual(2.0, dist_params[3])

    def test_fit_params_from_prices(self):

        csv_df = pd.read_csv('../../../../resources/webapp-coins.csv')
        dates = get_training_dates(csv_df)
        prices = np.full_like(dates, 5.0)

        class FakeDist:

            def fit(self, a, *args):
                return [1.0, 2.0, 3.0, 4.0]

        dist_params = _fit_params_from_prices(prices, calc_returns=lambda a: pd.DataFrame(),
                                              dist=FakeDist())

        self.assertEqual(3.0, dist_params[0])
        self.assertEqual(4.0, dist_params[1])
        self.assertEqual(1.0, dist_params[2])
        self.assertEqual(2.0, dist_params[3])

    def test_init(self):

        builder = TrainingConfigBuilder()

        builder.set_training_history_filename('../../../../resources/webapp-coins.csv')
        builder.set_input_csv_filename('../../../../inputs/ExampleCurveGenInputMulti.csv')

        config = builder.build_config()

        trainer = Trainer(config)

        self.assertEqual(config, trainer.config)

    def test_configure(self):

        builder = TrainingConfigBuilder()

        trainer = Trainer(builder.build_config())

        builder.set_training_history_filename('../../../../resources/webapp-coins.csv')
        builder.set_input_csv_filename('../../../../inputs/ExampleCurveGenInputMulti.csv')

        config = builder.build_config()

        trainer.configure(config)

        self.assertEqual(config, trainer.config)

    def test_train(self):

        builder = TrainingConfigBuilder()

        builder.set_training_history_filename('../../../../resources/webapp-coins.csv')
        builder.set_input_csv_filename('../../../../inputs/ExampleCurveGenInputMulti.csv')

        trainer = Trainer(builder.build_config())

        conv_dfs = trainer.train(dist=norm)

        self.assertEqual(2, len(conv_dfs))
        [self.assertEqual(2, len(conv_df['DistParams'].values[0])) for conv_df in conv_dfs]

        conv_dfs = trainer.train(0.1, dist=skewnorm)

        self.assertEqual(2, len(conv_dfs))
        [self.assertEqual(3, len(conv_df['DistParams'].values[0])) for conv_df in conv_dfs]

        conv_dfs = trainer.train(1.0, 3.5, dist=skewed_t)

        self.assertEqual(2, len(conv_dfs))
        [self.assertEqual(4, len(conv_df['DistParams'].values[0])) for conv_df in conv_dfs]


if __name__ == '__main__':
    unittest.main()

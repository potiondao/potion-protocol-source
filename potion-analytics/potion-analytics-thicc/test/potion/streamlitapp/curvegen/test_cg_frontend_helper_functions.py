import unittest
import pandas as pd

from potion.streamlitapp.curvegen.cg_file_io import read_training_data_from_csv
from potion.streamlitapp.curvegen.cg_plot import plot_training_data_sets
from potion.curve_gen.analysis.plot import show


class CurveGenFrontendHelperFunctionsTestCase(unittest.TestCase):

    def test_plot_training_data_sets(self):

        price_history_csv = pd.read_csv('../../../../resources/webapp-coins.csv')
        training_df = read_training_data_from_csv('../../../../batch_results/batch_0_training.csv')

        fig_map = plot_training_data_sets(price_history_csv, training_df)

        for key, val in fig_map.items():
            print(key)
            show(val)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

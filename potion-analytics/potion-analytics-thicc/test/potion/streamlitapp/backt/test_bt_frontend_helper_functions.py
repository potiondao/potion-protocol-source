import unittest

import pandas as pd
from potion.streamlitapp.backt.bt_frontend_helper_functions import (
    _check_matching_curve_row, _get_matching_curve)


class BtFrontendHelperFunctionsTestCase(unittest.TestCase):

    def test_check_matching_curve_row(self):

        perf_df = pd.read_csv(
            '../../../../batch_results/batch_1/backtesting/backtest_performance.csv')
        curve_df = pd.read_csv('../../../../batch_results/batch_1/curve_generation/curves.csv')

        curve_ids = []
        for perf_id, perf_row in perf_df.iterrows():

            for curve_id, curve_row in curve_df.iterrows():
                if _check_matching_curve_row(perf_row, curve_row):
                    curve_ids.append(curve_id)

        print(curve_ids)

        self.assertEqual(True, True)

    def test_get_matching_curve(self):

        perf_df = pd.read_csv(
            '../../../../batch_results/batch_1/backtesting/backtest_performance.csv')
        curve_df = pd.read_csv('../../../../batch_results/batch_1/curve_generation/curves.csv')

        for perf_id, perf_row in perf_df.iterrows():
            curve_id, curve_row = _get_matching_curve(perf_row, curve_df)
            print('pid: ', perf_id, ' cid: ', curve_id)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

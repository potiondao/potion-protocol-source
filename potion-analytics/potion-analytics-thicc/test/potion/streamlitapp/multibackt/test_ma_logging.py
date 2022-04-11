
import unittest
import vaex
import pandas as pd
import numpy as np

from potion.backtest.multi_asset_backtester import initialize_logging_df, calculate_row_slices
from potion.backtest.multi_asset_expiration_evaluator import log_expiration_info


def export_df(log_file_name):

    log_df = vaex.open(log_file_name + '.hdf5')
    log_df.export_csv(log_file_name + '.csv')

    log_df.close()
    del log_df


class LoggingTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_initialize_log(self):

        log_file_name = 'unit_test_log'
        total_rows = 10
        curve_ids = [1, 2, 3]

        dfw = initialize_logging_df(log_file_name, total_rows, curve_ids)

        dfw.close()
        del dfw

        export_df(log_file_name)

        df = pd.read_csv(log_file_name + '.csv')

        cols = df.columns

        self.assertEqual('Timestamp', cols[0])
        self.assertEqual('Path_ID', cols[1])
        self.assertEqual('A', cols[2])
        self.assertEqual('B', cols[3])
        self.assertEqual('C', cols[4])
        self.assertEqual('D', cols[5])
        self.assertEqual('Opt_Bankroll', cols[6])
        self.assertEqual('Opt_CAGR', cols[7])
        self.assertEqual('Opt_Absolute_Return', cols[8])
        self.assertEqual('User_Bankroll', cols[9])
        self.assertEqual('User_CAGR', cols[10])
        self.assertEqual('User_Absolute_Return', cols[11])

        col_idx = 12
        for curve_id in curve_ids:

            self.assertEqual('{}_Training_Key'.format(curve_id), cols[col_idx])
            self.assertEqual('{}_Exp_Duration'.format(curve_id), cols[col_idx + 1])
            self.assertEqual('{}_Strike_Pct'.format(curve_id), cols[col_idx + 2])
            self.assertEqual('{}_Price'.format(curve_id), cols[col_idx + 3])
            self.assertEqual('{}_Is_Expired'.format(curve_id), cols[col_idx + 4])
            self.assertEqual('{}_Opt_Premium'.format(curve_id), cols[col_idx + 5])
            self.assertEqual('{}_Opt_Loss'.format(curve_id), cols[col_idx + 6])
            self.assertEqual('{}_Opt_Payout'.format(curve_id), cols[col_idx + 7])
            self.assertEqual('{}_Opt_Amount'.format(curve_id), cols[col_idx + 8])
            self.assertEqual('{}_Opt_Util'.format(curve_id), cols[col_idx + 9])
            self.assertEqual('{}_Opt_Locked'.format(curve_id), cols[col_idx + 10])
            self.assertEqual('{}_User_Premium'.format(curve_id), cols[col_idx + 11])
            self.assertEqual('{}_User_Loss'.format(curve_id), cols[col_idx + 12])
            self.assertEqual('{}_User_Payout'.format(curve_id), cols[col_idx + 13])
            self.assertEqual('{}_User_Amount'.format(curve_id), cols[col_idx + 14])
            self.assertEqual('{}_User_Util'.format(curve_id), cols[col_idx + 15])
            self.assertEqual('{}_User_Locked'.format(curve_id), cols[col_idx + 16])

            col_idx += 17

        self.assertEqual('Opt_Total_Util', cols[col_idx])
        self.assertEqual('Opt_Total_Amt', cols[col_idx + 1])
        self.assertEqual('User_Total_Util', cols[col_idx + 2])
        self.assertEqual('User_Total_Amt', cols[col_idx + 3])

    def test_log_exp_info(self):

        log_file_name = 'unit_test_log'
        total_rows = 10
        curve_ids = [1, 2, 3]

        dfw = initialize_logging_df(log_file_name, total_rows, curve_ids)

        price_dict = {1: 100.0, 2: 300.0, 3: 200.0}
        duration_dict = {1: 1, 2: 7, 3: 14}
        strike_dict = {1: 1.0, 2: 0.9, 3: 1.1}

        trade_dict = {
            'opt_br': 10000.0,
            'opt_premium': 5.0,
            'opt_amt': 3.0,
            'opt_util': 0.5,
            'opt_locked': 1000.0,
            'user_br': 10001.0,
            'user_premium': 7.0,
            'user_amt': 3.2,
            'user_util': 0.45,
            'user_locked': 1002.0
        }

        results_dict = {
            'opt_loss': 2.0,
            'user_loss': 2.1,
            'opt_cagr': 5.0,
            'opt_ar': 1.2,
            'user_cagr': 4.8,
            'user_ar': 1.19
        }

        for i in range(total_rows):
            log_expiration_info(
                dfw, curve_ids, 1, 7, {1: [1, 2, 3, 4]}, 102 + i, price_dict, duration_dict,
                strike_dict, trade_dict, results_dict, i)

        dfw.close()
        del dfw

        export_df(log_file_name)

        df = pd.read_csv(log_file_name + '.csv')
        # print(df.to_string())

        np.testing.assert_allclose([102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
                                   df.Timestamp, rtol=1e-10, atol=0)
        self.assertTrue(True)

    def test_row_slices(self):

        log_file_name = 'unit_test_log'
        num_paths = 3
        path_length = 4
        total_num_tasks = num_paths
        total_rows = total_num_tasks * path_length
        curve_ids = [1, 2, 3]

        dfw = initialize_logging_df(log_file_name, total_rows, curve_ids)

        log_length = len(dfw)

        # Calculate the row index slices for each task
        row_slices = calculate_row_slices(path_length, num_paths, log_length)

        print(row_slices)

        price_dict = {1: 100.0, 2: 300.0, 3: 200.0}
        duration_dict = {1: 1, 2: 7, 3: 14}
        strike_dict = {1: 1.0, 2: 0.9, 3: 1.1}

        trade_dict = {
            'opt_br': 10000.0,
            'opt_premium': 5.0,
            'opt_amt': 3.0,
            'opt_util': 0.5,
            'opt_locked': 1000.0,
            'user_br': 10001.0,
            'user_premium': 7.0,
            'user_amt': 3.2,
            'user_util': 0.45,
            'user_locked': 1002.0
        }

        results_dict = {
            'opt_loss': 2.0,
            'user_loss': 2.1,
            'opt_cagr': 5.0,
            'opt_ar': 1.2,
            'user_cagr': 4.8,
            'user_ar': 1.19
        }

        for i in range(num_paths):

            for j in range(path_length):

                log_expiration_info(dfw, curve_ids, 1, i, {1: [1, 2, 3, 4]}, j,
                                    price_dict, duration_dict, strike_dict, trade_dict,
                                    results_dict, row_slices[i][j])

        dfw.close()
        del dfw

        export_df(log_file_name)

        df = pd.read_csv(log_file_name + '.csv')
        print(df.to_string())


if __name__ == '__main__':
    unittest.main()

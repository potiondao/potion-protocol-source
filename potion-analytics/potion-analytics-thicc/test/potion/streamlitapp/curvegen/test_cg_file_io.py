import unittest

from potion.streamlitapp.curvegen.cg_file_io import (read_training_data_from_csv,
                                                     read_curves_from_csv,
                                                     read_pdfs_from_csv,
                                                     curve_output_to_json)


class CgFileIOTestCase(unittest.TestCase):

    def test_read_training_csv(self):

        file = '../../../../batch_results/batch_0_training.csv'
        # file = './batch_results/batch_0_training.csv'

        training_df = read_training_data_from_csv(file)

        # print(training_df.to_string())

        self.assertEqual(True, True)

    def test_read_curves_from_csv(self):

        file = '../../../../batch_results/batch_0_curves.csv'
        # file = './batch_results/batch_0_curves.csv'

        curve_df = read_curves_from_csv(file)

        # print(curve_df.to_string())

        self.assertEqual(True, True)

    def test_read_pdfs_from_csv(self):

        file = '../../../../batch_results/batch_0_pdfs.csv'
        # file = './batch_results/batch_0_pdfs.csv'

        pdf_df = read_pdfs_from_csv(file)

        # print(pdf_df.columns)

        # print(pdf_df.to_string())

        self.assertEqual(True, True)

    def test_curve_csv_to_json(self):

        curve_file = '../../../../batch_results/batch_0_curves.csv'
        training_file = '../../../../batch_results/batch_0_training.csv'

        curve_df = read_curves_from_csv(curve_file)
        training_df = read_training_data_from_csv(training_file)

        json_strs = curve_output_to_json(curve_df, training_df)

        for jstr in json_strs:
            print(jstr)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

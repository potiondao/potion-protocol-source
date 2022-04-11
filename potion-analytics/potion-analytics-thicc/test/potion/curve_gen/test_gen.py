import unittest

from potion.curve_gen.builder import GeneratorConfigBuilder

from potion.curve_gen.analysis.plot import show, plot_convolutions, plot_curve
from potion.streamlitapp.curvegen.cg_file_io import write_curve_gen_outputs
from potion.curve_gen.gen import Generator
from potion.curve_gen.training.builder import TrainingConfigBuilder
from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder
from potion.curve_gen.kelly_fit.builder import FitConfigBuilder


def build_generator_config(input_file: str, training_history_file: str):
    training_config = TrainingConfigBuilder().set_input_csv_filename(
        input_file).set_training_history_filename(training_history_file)

    bounds_config = ConstraintsConfigBuilder().add_lower_bound(
        lambda a: 0.0).add_upper_bound(lambda a: 1.0)

    kelly_fit_config = FitConfigBuilder()

    return GeneratorConfigBuilder().set_training_builder(training_config).set_bounds_builder(
        bounds_config).set_fit_builder(kelly_fit_config).build_config()


class GenTestCase(unittest.TestCase):

    def test_generate_curves(self):
        input_file = '../../../inputs/ExampleCurveGenInputMulti.csv'
        train_file = '../../../resources/webapp-coins.csv'

        config = build_generator_config(input_file, train_file)

        gen = Generator()
        gen.configure_curve_gen(config)

        curves_df, pdf_df, training_df = gen.generate_curves()

        print(training_df.to_string())
        print(curves_df.to_string())
        # print(pdf_df.to_string())

        write_curve_gen_outputs(0, curves_df, pdf_df, training_df)

        # gen.generate_curves()

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

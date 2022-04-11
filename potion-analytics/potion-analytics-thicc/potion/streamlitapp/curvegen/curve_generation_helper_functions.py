"""
This module provides the backend code for the curve generator tool
"""
from potion.streamlitapp.curvegen.cg_file_io import write_curve_gen_outputs

from potion.curve_gen.builder import GeneratorConfig
from potion.curve_gen.gen import configure_curve_gen, generate_curves


def run_curve_generation(config: GeneratorConfig, batch_num: int):
    """
    Runs the curve generation and writes the output CSV files to a file

    Parameters
    ----------
    config : GeneratorConfig
        The configuration for the curve generation process
    batch_num : int
        The user specified batch number identifying this set of results from others in the
        log directory

    Returns
    -------
    None
    """
    configure_curve_gen(config)
    curve_df, pdf_df, training_df = generate_curves()

    write_curve_gen_outputs(batch_num, curve_df, pdf_df, training_df)

"""
This module supplies the GeneratorConfig object and the GeneratorConfigBuilder to allow
users of the library to configure the curve generation module following a standard
design pattern. This is the same pattern used by the other modules of the curve generator.
"""
from typing import NamedTuple

from potion.curve_gen.training.builder import TrainingConfigBuilder, TrainingConfig
from potion.curve_gen.kelly_fit.builder import FitConfigBuilder, FitConfig
from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder, ConstraintsConfig


class GeneratorConfig(NamedTuple):
    """
    Immutable configuration object produced by the builder containing the config to use
    during curve generation
    """
    train_config: TrainingConfig
    """Immutable configuration object containing the training information"""
    fit_config: FitConfig
    """Immutable configuration object containing the curve fit information"""
    bounds_config: ConstraintsConfig
    """Immutable configuration object containing the constraint information"""

    def __eq__(self, other):
        """
        Checks if this config object is equal to other

        Parameters
        ----------
        other : GeneratorConfig
            The other config object we are testing for equality

        Returns
        -------
        is_equal : bool
            True if the two objects are equal, False otherwise
        """
        return (self.train_config == other.train_config) and (
                self.bounds_config == other.bounds_config) and (
                self.fit_config == other.fit_config)


class GeneratorConfigBuilder:
    """
    Standard python builder class for creating immutable configuration objects to use
    during the curve generation process
    """

    def __init__(self):
        """
        Constructor initializes the builder with default values
        """
        self.train_builder = TrainingConfigBuilder()
        self.fit_builder = FitConfigBuilder()
        self.bounds_builder = ConstraintsConfigBuilder()

    def set_training_builder(self, train_bldr: TrainingConfigBuilder):
        """
        Sets the configured builder object for training

        Parameters
        ----------
        train_bldr : TrainingConfigBuilder
            The builder object with the configured training info

        Returns
        -------
        self : GeneratorConfigBuilder
            This object following the builder pattern
        """
        self.train_builder = train_bldr
        return self

    def set_fit_builder(self, fit_bldr: FitConfigBuilder):
        """
        Sets the configured builder object for curve fitting

        Parameters
        ----------
        fit_bldr : FitConfigBuilder
            The builder object with the configured curve fit info

        Returns
        -------
        self : GeneratorConfigBuilder
            This object following the builder pattern
        """
        self.fit_builder = fit_bldr
        return self

    def set_bounds_builder(self, bounds_bldr: ConstraintsConfigBuilder):
        """
        Sets the configured builder object for constraining premium calculation

        Parameters
        ----------
        bounds_bldr : ConstraintsConfigBuilder
            The builder object with the configured constraints info

        Returns
        -------
        self : GeneratorConfigBuilder
            This object following the builder pattern
        """
        self.bounds_builder = bounds_bldr
        return self

    def build_config(self):
        """
        Creates an immutable GeneratorConfig object from the currently configured builder

        Returns
        -------
        config : GeneratorConfig
            Immutable configuration object to use during curve generation
        """
        return GeneratorConfig(self.train_builder.build_config(), self.fit_builder.build_config(),
                               self.bounds_builder.build_config())

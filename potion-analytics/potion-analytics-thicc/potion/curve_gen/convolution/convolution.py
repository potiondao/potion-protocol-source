"""
This module is used by the Generator to perform convolution of the return PDF to propagate it
forward in time, under the assumption that each day's return is independent of the next.

This is done using a class which follows the duck typed interface of the Generator
and is used by it to create Kelly curves.

Callers who wish to replace or customize the behavior of this module need only implement
three duck typed functions:

    configure_convolution(ConvolutionConfig)
        'Configures the settings of this module. See builders module for more info
        on ConvolutionConfig'
    run_convolution()
        'Which performs the convolutions of the PDF'
    get_pdf_arrays(int)
        'Which gets the X and Y arrays of the PDF functions on the specified day'

Like many python libraries, this module uses a global object with the methods prebound so that
the same library can be used by object-oriented and functional programmers alike. Object-oriented
users can use the LogDomainConvolver class, and functional programmers can use the functions
described above.
"""
from typing import Callable

from potion.curve_gen.domain_transformation import transform_pdf_using_optimize
from potion.curve_gen.convolution.builder import ConvolutionConfig, ConvolutionConfigBuilder
from potion.curve_gen.convolution.helpers import convolve_self_n


class LogDomainConvolver:
    """
    This class performs the convolution of the return PDF in the log return domain. This class is
    used by the Generator following a duck typed interface to create Kelly curves.
    """

    def __init__(self, config: ConvolutionConfig):
        """
        Constructs the object using the ConvolutionConfig created using the builder module

        Parameters
        ----------
        config : ConvolutionConfig
            The config object created using the builder module
        """
        self.config = config
        self.transform_pdf_func = transform_pdf_using_optimize

        self.log_pdf_list = None
        self.price_pdf_list = None

    def configure(self, config: ConvolutionConfig):
        """
        Changes the config object to a different configuration

        Parameters
        ----------
        config : ConvolutionConfig
            The configuration object to set

        Returns
        -------
        None
        """
        self.config = config

    def run_convolution(self, expiration_days=(), transform=transform_pdf_using_optimize):
        """
        Performs all of the tasks of convolution and stores the results in the class members.

        Parameters
        ----------
        expiration_days : List[int]
            Optional. Specify the List of expiration days on which to transform the PDF
        transform : Callable
            Optional. The function to use to transform the PDF from the log domain to
            the price domain

        Returns
        -------
        None
        """
        self._create_log_pdfs()
        self._set_pdf_transform_func(transform)
        self._create_price_pdfs(expiration_days)

    def get_pdf_arrays(self):
        """
        Gets the X and Y value ndarrays for the PDF function

        Parameters
        ----------

        Returns
        -------
        x : numpy.ndarray
            The X values of the PDF function
        y : numpy.ndarray
            The Y values of the PDF function
        """
        if self.config.log_only:
            return self.config.log_x, self.log_pdf_list
        else:
            return self.config.x, self.price_pdf_list

    def _set_pdf_transform_func(self, func: Callable):
        """
        Internal function which sets the python function used to transform the PDF from
        the log return domain to the price domain

        Parameters
        ----------
        func : Callable
            The function to use to do the transformation

        Returns
        -------
        None
        """
        self.transform_pdf_func = func

    def _create_log_pdfs(self):
        """
        Internal function which performs the convolutions of the PDFs the specified
        number of times to propagate the PDF forward in time a certain number of days.
        The results is stored as a List of List[float] containing the PDF in the log
        domain on each day.

        The result can be accessed by calling self.log_pdf_list

        Returns
        -------
        None
        """
        self.log_pdf_list = convolve_self_n(self.config.dist, self.config.log_x,
                                            self.config.num_times_to_conv)

    def _create_price_pdfs(self, expiration_days=()):
        """
        Internal function which uses the domain transformation library to convert the
        log return PDFs into PDFs in the price domain. The result is stored in self.price_pdf_list.

        Optionally, the expiration day List[int] can be specified to save some computation and
        only transform PDFs on the expiration days desired by the caller

        If the ConvolutionConfig is set to log_only=True, this function will do nothing and return.

        Parameters
        ----------
        expiration_days : List[int]
            List of expiration days on which to transform the PDF

        Returns
        -------
        None
        """
        if self.config.log_only:
            return

        self.price_pdf_list = [self.transform_pdf_func(self.config.log_x, log_pdf, self.config.x,
                                                       tol=1e-6)
                               for index, log_pdf in enumerate(self.log_pdf_list)
                               if len(expiration_days) == 0 or (index + 1) in expiration_days]


# Define a Global object with default values to be configured by the module user
_conv = LogDomainConvolver(ConvolutionConfigBuilder().build_config())

# Prebind the object's methods so the module can be used by object oriented and functional
# programmers alike
configure_convolution = _conv.configure
run_convolution = _conv.run_convolution
get_pdf_arrays = _conv.get_pdf_arrays

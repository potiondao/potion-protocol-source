"""

# Usage Examples Walkthrough

## Introduction

Provided in this module are a set of useage examples for the Potion Analytics: THICC curve
generation library and for running the backtesting tools called from the user's own python code.
These examples range from simple Hello World demos of the modules to intermediate an advanced
configurations and uses.

These examples are not meant to cover every possible configuration combination. Instead, they are
meant to teach the user the structure, layout, and general usage of the library's modules. That
way the user is prepared and can quickly get started using the library with their own python code,
and can make more effective use of the API documentation.

### Curve Generation

Example Code Location: [Curve Generation](http://localhost:8000/potion/examples/1_generator.py)  \n
In order to get started with using the curve generator, the simple 'hello world' example reuses
the helper functions which the Streamlit GUI takes advantage of:

##### Curve Generator: Hello World (functional)
```python
from potion.curve_gen.utils import build_generator_config
from potion.curve_gen.gen import configure_curve_gen, generate_curves

# Specify the input files for curve generation
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

# Configure the module and run curve generation
configure_curve_gen(build_generator_config(input_file, price_history_file))
curve_df, pdf_df, training_df = generate_curves()

print(curve_df.to_string())
print(training_df.to_string())
print(pdf_df.to_string())
```

In the simplest case, external programs can call the curve generator using only 2 lines of
code: one to configure the module, and one to run it. Most of the configuration information is
specified by the external files, which can easily be created using the tools of the Streamlit
GUI discussed [here](
http://localhost:8080/potion/user_guides/historical_data_downloader_user_guide.html) and
[here](http://localhost:8080/potion/user_guides/subgraph_downloader_user_guide.html).

The format of these input CSV files is specified [here](
http://localhost:8080/potion/user_guides/curve_generator_user_guide.html#input-csv-file-format)
if the user of the library is interested in creating their own CSV files.

The curve generation process outputs 3 pandas DataFrames which capture information recorded
about the curves. These output DataFrames are documented [here](
http://localhost:8080/potion/user_guides/backtester_user_guide.html#input-csv-file-formats).

Following the same design pattern as popular python libraries like scipy, the cuve generation
library allows the user to call it in a functional programming style or an object oriented
manner using a global module object. If the user would prefer to use multiple objects and
control the configuration of each separately, that can be accomplished using the object directly.

Subsequent examples in this guide will use the functional method only, for the object oriented
library calls please consult the API Reference documentation.

##### Curve Generator: Hello World (object oriented)
```python
from potion.curve_gen.utils import build_generator_config
from potion.curve_gen.gen import Generator

# Specify the input files for curve generation
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

# Configure the module and run curve generation
gen = Generator()
gen.configure_curve_gen(build_generator_config(input_file, price_history_file))
curve_df, pdf_df, training_df = gen.generate_curves()

print(curve_df.to_string())
print(training_df.to_string())
print(pdf_df.to_string())
```

#### Intermediate Configuration

By changing the default parameters to the functions, the user can make intermediate-level
configuration changes to the generated curves. For example, using other return distributions
for modeling the asset's financial returns, or specifying other payoffs or spreads.

For example, using a Normal Distribution for training the asset return distribution:

##### Curve Generator: Normal Distribution
```python
from potion.curve_gen.utils import build_generator_config
from potion.curve_gen.gen import configure_curve_gen, generate_curves
from scipy.stats import norm

# Specify the input files for curve generation
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

# Configure the module and run curve generation
configure_curve_gen(build_generator_config(input_file, price_history_file))
curve_df, pdf_df, training_df = generate_curves(initial_guess=(), dist=norm)

print(curve_df.to_string())
print(training_df.to_string())
print(pdf_df.to_string())
```

The Normal Distribution has no other parameters to train beyond location and scale, so the
initial_guess parameter of the function call is an empty tuple.

The same example using Skewed Normal:

##### Curve Generator: Skewed Normal Distribution
```python
from potion.curve_gen.utils import build_generator_config
from potion.curve_gen.gen import configure_curve_gen, generate_curves
from scipy.stats import skewnorm

# Specify the input files for curve generation
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

# Configure the module and run curve generation
configure_curve_gen(build_generator_config(input_file, price_history_file))
curve_df, pdf_df, training_df = generate_curves(initial_guess=(1.0,), dist=skewnorm)

print(curve_df.to_string())
print(training_df.to_string())
print(pdf_df.to_string())
```

Another configuration option includes changing the payoff from a short put to some other setting.
For example, a long call:

##### Curve Generator: Long Call
```python
from potion.curve_gen.utils import build_generator_config
from potion.curve_gen.gen import configure_curve_gen, generate_curves
from potion.curve_gen.utils import make_payoff_dict

# Specify the input files for curve generation
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

# Configure the module and run curve generation
payoff_dict = make_payoff_dict(call_or_put='call', direction='long')

configure_curve_gen(build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict))
curve_df, pdf_df, training_df = generate_curves(payoff_dict=payoff_dict)

print(curve_df.to_string())
print(training_df.to_string())
print(pdf_df.to_string())
```

This payoff dict can also be utilized to specify more complex inputs like an option spread. For
example, a bull put spread:

##### Curve Generator: Bull Put
```python
from potion.curve_gen.utils import build_generator_config
from potion.curve_gen.gen import configure_curve_gen, generate_curves
from potion.curve_gen.utils import make_payoff_dict, add_leg_to_dict

# Specify the input files for curve generation
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

# Configure the module and run curve generation
payoff_dict = make_payoff_dict(call_or_put='put', direction='short')
payoff_dict = add_leg_to_dict(payoff_dict, strike=0.8, call_or_put='put', direction='long')

configure_curve_gen(build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict))
curve_df, pdf_df, training_df = generate_curves(payoff_dict=payoff_dict)

print(curve_df.to_string())
print(training_df.to_string())
print(pdf_df.to_string())
```

#### Advanced Configuration

Not all configuration options of the library are exposed to the caller as function arguments. For
more advanced configuration needs, or fine grained control over the full set of parameters the
user must use the builder objects of the curve generator submodules.

Like popular libraries such as matplotlib, the configuration of the curve generator and the
curve generator submodules follows the builder design pattern. This pattern has an object which
can have parameters set using separate functions, or by chaining them together in a single call.

The curve generator module uses the [GeneratorConfigBuilder](
http://localhost:8080/potion/curve_gen/builder.html) object, which has its own variables
containing the configuration objects of the submodules. The submodule builders are:

* [TrainingConfigBuilder](http://localhost:8080/potion/curve_gen/training/builder.html)
* [ConvolutionConfigBuilder](http://localhost:8080/potion/curve_gen/convolution/builder.html)
* [PayoffConfigBuilder](http://localhost:8080/potion/curve_gen/payoff/builder.html)
* [ConstraintsConfigBuilder](http://localhost:8080/potion/curve_gen/constraints/builder.html)
* [FitConfigBuilder](http://localhost:8080/potion/curve_gen/kelly_fit/builder.html)

For example, without using the build_generator_config helper function, the Hello World
is as follows:

##### Curve Generator: Builders
```python
from potion.curve_gen.builder import GeneratorConfigBuilder
from potion.curve_gen.training.builder import TrainingConfigBuilder
from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder
from potion.curve_gen.kelly_fit.builder import FitConfigBuilder
from potion.curve_gen.gen import configure_curve_gen, generate_curves

# Specify the input files for curve generation
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

training_config = TrainingConfigBuilder().set_input_csv_filename(
    input_file).set_training_history_filename(price_history_file)

bounds_config = ConstraintsConfigBuilder().add_upper_bound(lambda a: 1.0).add_lower_bound(
    lambda a: 0.0)

config = GeneratorConfigBuilder().set_training_builder(training_config).set_bounds_builder(
    bounds_config).set_fit_builder(FitConfigBuilder()).build_config()

# Configure the module and run curve generation
configure_curve_gen(config)
curve_df, pdf_df, training_df = generate_curves()

print(curve_df.to_string())
print(training_df.to_string())
print(pdf_df.to_string())
```

The builders for the submodules will be described in detail in the following sections.

### Training Module

The training module performs the process of fitting a probability distribution to the historical
financial returns of an asset. Using the inputs specified in the files, the module will
extract the historical training data, calculate the financial returns of the data,
and fit those returns to a specified probability distribution which will be used as the
mathematical model during curve generation.

The builder is responsible for configuring this module and validating the input files for
correctness. The builder allows the user to override the validating and exception handling
logic of the file input process for use in their own programs.

The most basic usage of the training builder is as follows:

##### Training Module: Builder
```python
from potion.curve_gen.training.builder import TrainingConfigBuilder

# Specify the input files
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

builder = TrainingConfigBuilder().set_input_csv_filename(
    input_file).set_training_history_filename(price_history_file)

# Create the immutable config object
config = builder.build_config()

print(config)
```

The module allows the user to specify custom functions for handling different situations while
loading the CSV files. These are specified by overriding the default parameters in the build_config
function.

##### Training Module: Custom File Logic
```python
import pandas as pd
from potion.curve_gen.training.builder import TrainingConfigBuilder

def error_file_not_found(filename: str):
    raise FileNotFoundError('Check configuration. Could not find File: {}'.format(filename))

def error_bad_csv_format(filename: str):
    raise ValueError('Check configuration. CSV file bad format: {}'.format(filename))

def check_input_format(csv_df: pd.DataFrame):
    return 'Asset' == csv_df.columns[0]

def check_training_format(csv_df: pd.DataFrame):
    return 'Master calendar' == csv_df.columns[0]

# Specify the input files
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

builder = TrainingConfigBuilder().set_input_csv_filename(
    input_file).set_training_history_filename(price_history_file)

# Create the immutable config object
config = builder.build_config(
    on_file_error=error_file_not_found, check_training_format=check_training_format,
    check_input_format=check_input_format, on_format_error=error_bad_csv_format)

print(config)
```

To perform the training, the config object is used to set up the training module and then the
train function is called. The training function requires an initial guess as a tuple for the
optimizer at the distribution's parameters. By default, the skewed Student's T is used so these
parameters are the skew and nu parameter of the distribution (1.0 is no skew, 2.5 is nu guess).
The user can change them to desired guesses.

##### Training Module: Usage
```python
from potion.curve_gen.training.builder import TrainingConfigBuilder
from potion.curve_gen.training.train import configure_training, train

# Specify the input files
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

# Create the immutable config object
config = TrainingConfigBuilder().set_input_csv_filename(
    input_file).set_training_history_filename(price_history_file).build_config()

# Perform the training using the initial guess for PDF parameters.
configure_training(config)
conv_dfs = train(1.0, 2.5)

print(conv_dfs)
```

The DataFrames output by this function contain the information output for each training set that
will be used in the convolution process to propagate the return probability distribution forward
in time under the assumption of independence.

Other distributions can be trained from the data by specifying the appropriate number of initial
guesses for that distribution's parameters and overriding the default argument.

##### Training Module: Custom Distribution
```python
from scipy.stats import skewnorm
from potion.curve_gen.training.builder import TrainingConfigBuilder
from potion.curve_gen.training.train import configure_training, train

# Specify the input files
input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

# Create the immutable config object
config = TrainingConfigBuilder().set_input_csv_filename(
    input_file).set_training_history_filename(price_history_file).build_config()

# Perform the training using the initial guess for PDF parameters.
configure_training(config)
conv_dfs = train(1.0, dist=skewnorm)

for df in conv_dfs:
    print(df.to_string())
```

### Convolution Module

This module is used by the Generator to perform convolution of the return PDF to propagate it
forward in time, under the assumption that each day's return is independent of the next.

Unlike the other modules, the convolution module has 3 functions. A configuration function, a
run function, and a getter function. The existence of the getter function is for efficiency. For
the convolution process it only needs to be run once for each set of training data.

Calculating different strikes and expirations on the same training data incurs no additional
computation so long as the result is cached. By providing the getter function, the user does
not need to manage this caching in their own program. The run function is called once to
perform the calculations and the getter is called later when each result is needed again.

If the user does desire to manage their own cached values, the object oriented interface can be
used by consulting the API documentation for the module.

The builder is responsible for configuring this module and allows the user to override the
default values in their own programs.

##### Convolution Module: Builder
```python
from potion.curve_gen.convolution.builder import ConvolutionConfigBuilder

builder = ConvolutionConfigBuilder()
config = builder.build_config()

print(config)
```

Using custom parameters with the builder is possible by calling the builder functions:

##### Convolution Module: Custom Builder
```python
from potion.curve_gen.convolution.builder import ConvolutionConfigBuilder

config = ConvolutionConfigBuilder().set_num_times_to_convolve(30).set_log_only(
        False).set_points_in_pdf(30001).set_distribution(
        norm(loc=0.0, scale=1.0).pdf).build_config()

print(config)
```

Please see the API documentation for a full description of each possible parameter.

To use the module, the user must call the configure and run_convolution functions. Finally, when
the user is interested in using the output PDFs, call the getter function.

##### Convolution Module: Usage
```python
from potion.curve_gen.convolution.convolution import (
    configure_convolution, run_convolution, get_pdf_arrays)
from potion.curve_gen.convolution.builder import ConvolutionConfigBuilder

config = ConvolutionConfigBuilder().build_config()

# Configure and run the convolution
configure_convolution(config)
run_convolution()

# Later, get and use the output PDF arrays
pdf_x, pdf_y_list = get_pdf_arrays()

for pdf_y in pdf_y_list:
    print('x: ', pdf_x, '\\ny: ', pdf_y)
```

Please see the API documentation for a full list of configurable parameters of the convolution
module.

### Payoff Module

The payoff module provides the functions for calculating the simulated option payoff from an
option or spread of options (or units of the underlying asset).

Unlike the other modules, the payoff module has 3 functions. A configuration function, a
function to get the payoff odds, and a function to get the maximum loss of the position. By
default, these functions perform the calculation for 0.0 premium but can have it specified by
overriding the input argument with the premium value.

##### Payoff Module: Builder
```python
from potion.curve_gen.payoff.builder import PayoffConfigBuilder

builder = PayoffConfigBuilder()
config = builder.build_config()

print(config)
```

The user can also specify input arguments using the builder:

##### Payoff Module: Custom Builder
```python
from potion.curve_gen.payoff.builder import PayoffConfigBuilder

builder = PayoffConfigBuilder().add_option_leg(
    call_or_put='put', direction='short').set_underlying_payoff_leg(1.0, 1.0)

config = builder.build_config()

print(config)
```

To use the module, the user must call the configure function. When
the user is interested in calculating the payoff odds and the max loss, call the
matching functions. These can be called with default values (0.0 premium), or using specified
premium amounts.

##### Payoff Module: Usage
```python
from potion.curve_gen.payoff.builder import PayoffConfigBuilder
from potion.curve_gen.payoff.payoff import configure_payoff, get_payoff_odds, get_position_max_loss

config = PayoffConfigBuilder().add_option_leg(
    call_or_put='put', direction='short').build_config()

configure_payoff(config)
odds = get_payoff_odds()
max_loss = get_position_max_loss()

print('odds: ', odds)
print('max loss: ', max_loss)
```

##### Payoff Module: Usage With Premium
```python
from potion.curve_gen.payoff.builder import PayoffConfigBuilder
from potion.curve_gen.payoff.payoff import configure_payoff, get_payoff_odds, get_position_max_loss

config = PayoffConfigBuilder().add_option_leg(
    call_or_put='put', direction='short').build_config()

configure_payoff(config)
odds = get_payoff_odds(premium=0.1)
max_loss = get_position_max_loss(premium=0.1)

print('odds: ', odds)
print('max loss: ', max_loss)
```

### Constraints Module

This module is used by the Generator to constrain the premium points in generated Kelly curves
to lie between an upper and lower bound during optimization. By default, this module does not
apply any constraints and the lower bound is 0.0 premium with an upper bound of 1.0 (the full
amount required to collateralize the put in percentage terms).

##### Constraints Module: Builder
```python
from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder

builder = ConstraintsConfigBuilder().add_lower_bound(
    lambda a: 0.0).add_upper_bound(lambda a: 1.0)

config = builder.build_config()

print(config)
```

Suppose that a user wanted to generate a curve for a put at strike 0.9 and
expiration 35 days away. There is no existing curve on the subgraph for that strike and
expiration to study. There is however, a curve at strike 1.0 and 35 days away. The user knows that
if a curve were to be generated where the premium for strike 0.9 is larger than the premium for
strike 1.0, then arbitrage would be possible in the simulation. This would mean it would be
possible to buy the 1.0 strike put, and sell the 0.9 strike put for a risk free profit. This is
known as the monotonic constraint on the option prices.

Given the extra knowledge of nearby option prices, the simulation can be faster and more
accurate by constraining the optimizer to not search those arbitrage premium values. If the
optimizer produced a value where the user is required to make risk free profits in order for
the simulation to show positive return, the user would know that outside the simulation a real
order would never fill at that price - so it may not be interesting to simulate.

##### Constraints Module: Build Monotonic Constraints
```python
from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder

my_strike = 0.9
other_strike = 1.0
other_put_prem = 0.2

builder = ConstraintsConfigBuilder().add_lower_bound(
    lambda a: other_put_prem - (other_strike - my_strike)).add_upper_bound(
    lambda a: other_put_prem)

config = builder.build_config()

print(config)
```

The constraints module interface allows the user to pass a dict containing any number of
runtime parameter values to their custom boundary functions. This parameter is the 'a' value of
the lambda expressions in the above example. Since the constraints above do not have runtime
parameters, 'a' is ignored.

Finally, using the constraint module involves calling the same configuration function followed by
the get_lower_bound and get_upper_bound functions. These functions iterate over the lists of
user specified boundary functions and returns the float values representing the premiums of the
upper and lower bounds. For example, suppose there are many boundary functions specified by the
user:

##### Constraints Module: Usage
```python
from potion.curve_gen.constraints.builder import ConstraintsConfigBuilder
from potion.curve_gen.constraints.bounds import configure_bounds, get_lower_bound, get_upper_bound

config = ConstraintsConfigBuilder().add_lower_bound(
    lambda a: 0.0).add_upper_bound(lambda a: 0.9).add_lower_bound(
    lambda a: 0.1).add_upper_bound(lambda a: 1.0).build_config()

configure_bounds(config)

# optionally pass a dict with info to the boundary functions at calculation time
lower_bound = get_lower_bound({'example_custom_param': 3.0})
upper_bound = get_upper_bound({})

print('lb: ', lower_bound, ' ub: ', upper_bound)
```

### Fit Module

This module is used to create best-fit curves for the generated Kelly curve points. By default
this uses the cosh function. If the user is interested in studying others, the following examples
may prove useful.

##### Fit Module: Builder
```python
from potion.curve_gen.kelly_fit.builder import FitConfigBuilder

# 'EXP' and 'POLY' for exponential and polynomial are also implemented choices
config = FitConfigBuilder().set_fit_type('COSH').build_config()

print(config)
```

To use the module and fit a curve:

##### Fit Module: Usage
```python
import numpy as np
from potion.curve_gen.kelly_fit.builder import FitConfigBuilder
from potion.curve_gen.kelly_fit.kelly_fit import configure_fit, fit_kelly_curve, fit_function_table

config = FitConfigBuilder().set_fit_type('COSH').build_config()

configure_fit(config)
[a, b, c, d] = fit_kelly_curve(np.linspace(0.0, 0.9999, 50), np.linspace(0.0, 0.9999, 50))

print(a, b, c, d)
```

To implement a custom fitting function, the user must update the fit function table with their
custom function:

##### Fit Module: Custom Fit
```python
import numpy as np
from potion.curve_gen.kelly_fit.builder import FitConfigBuilder
from potion.curve_gen.kelly_fit.kelly_fit import configure_fit, fit_kelly_curve, fit_function_table

config = FitConfigBuilder().set_fit_type('my_custom_function').build_config()

fit_function_table['my_custom_function'] = lambda x, y, **kwargs: [1.0, 2.0, 3.0, 4.0]

configure_fit(config)
[a, b, c, d] = fit_kelly_curve(np.linspace(0.0, 0.9999, 50), np.linspace(0.0, 0.9999, 50))

print(a, b, c, d)
```

### Backtester

The batch_backtester module allows the user to run simulations of generated curves. Currently,
the backtesting module only supports simulating short put options.

Results are efficiently stored in a binary log file ending in *.hdf5 using the Vaex library.
Conversion utilities exist within the tool for the user's convenience that will convert these
output files into CSV.

##### Backtester: Hello World
```python
from potion.curve_gen.utils import build_generator_config
from potion.curve_gen.gen import configure_curve_gen, generate_curves
from potion.backtest.batch_backtester import create_backtester_config, BatchBacktester

input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
price_history_file = '../../resources/webapp-coins.csv'

# Generate the curves to backtest
configure_curve_gen(build_generator_config(input_file, price_history_file))
curve_df, pdf_df, training_df = generate_curves()

# Configure the backtester
num_paths = 300 # int number of simulated price paths
path_length = 730 # int number of days in simulation
util = 0.3 # from 0 to 1 as a percentage of the total capital available
initial_bankroll = 1000.0 # starting cash in the simulation

config = create_backtester_config(num_paths, path_length, util, initial_bankroll)

# Run the backtesting simulation
backtester = BatchBacktester(config=config, curve_df=curve_df, training_df=training_df)
backtester.generate_backtesting_paths()
backtester.evaluate_backtest_sequentially('output_log_name')
```

### Multi Asset Backtester

The batch_backtester module allows the user to run simulations of a portfolio of generated
curves. Currently, the multi asset backtesting module only supports simulating short put options.

Results are efficiently stored in a binary log file ending in *.hdf5 using the Vaex library,
exactly like the single asset version. Conversion utilities exist within the tool for the user's
convenience that will convert these output files into CSV.

##### Multi Asset Backtester: Hello World
```python
from potion.streamlitapp.curvegen.cg_file_io import read_training_data_from_csv
from potion.streamlitapp.multibackt.ma_file_io import read_multi_asset_curves_from_csv
from potion.backtest.multi_asset_backtester import (
    create_ma_backtester_config, MultiAssetBacktester, PathGenMethod)

# Read in the input dataframes from the example files
input_df = read_multi_asset_curves_from_csv('../../inputs/ExampleMultiAssetBacktesterInput.csv')
training_df = read_training_data_from_csv('../../resources/examples/training.csv')

# Same as parameters in single asset backtester
num_paths = 300
path_length = 730
initial_bankroll = 1000.0

# Specifies 10% util for each asset. In this case, input CSV has ethereum as ID 0 and
# bitcoin as ID 1
util_map = {
    0: 0.1,
    1: 0.1
}

# Configure the backtester
config = create_ma_backtester_config(PathGenMethod.MV_STUDENT_T, num_paths, path_length,
                                     util_map, initial_bankroll)

# Run the backtesting
backtester = MultiAssetBacktester(config=config, curve_df=input_df,
                                  training_df=training_df)
backtester.generate_backtesting_paths()
backtester.evaluate_backtest_sequentially('out_log_name', backtest_id=0, num_ma_backtests=1)
```

"""
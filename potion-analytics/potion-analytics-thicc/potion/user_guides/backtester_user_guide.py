"""
# Potion Analytics: THICC
# Backtester User Guide

## Introduction

The backtester is a tool that lets the user run what is called a monte carlo backtesting
simulation. This simulation starts with some probability distribution and generates random
walk-like paths of prices. Usually, the properties of this distribution are found or trained
based on the price history of some financial asset. That way, the simulated
paths are like alternate histories with the same properties of the real price history.

![paths](http://localhost:8000/resources/user_guides/backtester/paths.png)

The inputs to the backtester tool are 3 CSV files which are generated as outputs from the curve
generator. You can read about the curve generator and how to use it
[here](./curve_generator_user_guide.html). These CSV outputs allow the
user to easily import the results of the curve generation into other programs if desired.

If you want to skip reading about the tool generated CSV files for now, jump to the
[Walkthrough Guide](#walkthrough)

### Input CSV File Formats

The 3 CSV file formats are as follows:

** The Curve CSV File **

![curve_csv_format](http://localhost:8000/resources/user_guides/backtester/curve_csv_format.png)

This input file will tell the backtester app for each generated Kelly curve:  \n

Parameters
-----------
Ticker : str
    The name of the Asset the Kelly curve was generated for e.g. Bitcoin, Ethereum
Label : str
    The user specified label for the set of training data to differentiate it from other training
    sets on the same Asset. e.g. Bull, Bear, Full_History
Expiration : int
    The expiration date of the option in number of days. e.g. 7 is the option expires in 1 week
StrikePercent : float
    The strike price of the Put option as a multiple of the at-the-money (ATM) price. e.g. 1.0
    is ATM, 0.9 is 10% out-of-the-money (OTM), and 1.1 is 10% in-the-money (ITM), etc.
A : float
    The A parameter for the user specified Kelly Curve
B : float
    The B parameter for the user specified Kelly Curve
C : float
    The C parameter for the user specified Kelly Curve
D : float
    The D parameter for the user specified Kelly Curve
t_params : List[float]
    The four parameters of the Student's T distribution fit to the Asset training data: Location,
    Scale, Skew, Nu
bet_fractions : List[float]
    The points on the X-axis of the optimum boundary Kelly curve output from the calculator
curve_points : List[float]
    The points on the Y-axis of the optimum boundary Kelly curve output from the calculator

** The Training CSV File **

![training_csv_format](
http://localhost:8000/resources/user_guides/backtester/training_csv_format.png)

This input file will tell the backtester app for each underlying Asset's training data:  \n

Parameters
-----------
Ticker : str
    The name of the Asset the Kelly curve was generated for e.g. Bitcoin, Ethereum
Label : str
    The user specified label for the set of training data to differentiate it from other training
    sets on the same Asset. e.g. 'Bull', 'Bear', 'Full_History'
CurrentPrice : float
    The current price of the asset so the tool can begin price paths in the simulation at the
    current price of the Asset.
StartDate : str
    The start date of the training data window in the historical price data
EndDate : str
    The end date of the training data window in the historical price data
TrainingPrices : List[float]
    The selected range of training price data between StartDate and EndDate

** The PDF CSV File **

![pdf_csv_format](http://localhost:8000/resources/user_guides/backtester/pdf_csv_format.png)

This input file will tell the backtester app the PDF for each asset at the specified
expiration date:  \n

Parameters
-----------
Prices : float
    Column of price values on the X-axis of the PDF
PDF_Values : float
    Each column represents the PDF for an asset at a number of expiration days into the
    future. The format of the column name is Asset-Label|Expiration.
    For example: Bitcoin-Bull|7, Ethereum-Full|1

## Walkthrough

<span style="color:red">**NOTE: This part of the guide assumes the Curve Generator tool has
already been run. If not, see this part of the guide**</span> [here](
./curve_generator_user_guide.html#walkthrough)

1\. Select the Batch Number. This should match the Batch Number selected in the Curve
Generator for the results you are interested in backtesting. These results are automatically
detected by the tool looking for sub-directories named batch_# in the directory 'batch_results',
where the number is the number selected in the Curve Generator tool. For example:
./batch_results/batch_7

This Batch Number allows you to specify a number which will uniquely identify the log files
from different runs of this tool.

![1](http://localhost:8000/resources/user_guides/backtester/1_arrow.png)

2\. Click the Select button to select the Batch Number.

![1a](http://localhost:8000/resources/user_guides/backtester/1a_arrow.png)

3\. The Curves which were generated for the Batch using the Curve Generator will load and be
displayed in a table to the user.

![loaded_curves](http://localhost:8000/resources/user_guides/backtester/loaded_curves.png)

4\. Select the Curves the user would like to create output plots for. The checkboxes on the bottom
of the table allow the user to select all Curves, and allow the user to control whether these
output plots are saved as files in the ./batch_results/batch_# directory.

![loaded_curves](http://localhost:8000/resources/user_guides/backtester/selected_curves_arrow.png)

The Curves which are currently selected for plotting are displayed in a secondary table below the
checkbox controls.

5\. Choose a hypothetical starting amount of money (bankroll).

In the backtester, this number determines where the user's bankroll plot begins. This plot
graphs the amount of cash the user has over the duration of the simulation.

![2](http://localhost:8000/resources/user_guides/backtester/2_arrow.png)

6\. Select which probability distribution is used to generate the simulated price paths.

The options include:  \n
* Histogram - This distribution does not make any assumptions about what the asset's return
    distribution may be.

    As more price data is collected the Histogram will 'learn' and approach the asset's
    return distribution.  \n
* Student's T with Skew - The Student's T distribution is a common one studied in finance.

    It has 'fat tails' and can be used to model extreme events like market crashes. The
    skewed version is a version which does not require the distribution to be symmetric.

    If you are not sure which to pick, start simulating paths with Student's T since the simulation
    will be more conservative.

![3](http://localhost:8000/resources/user_guides/backtester/3_arrow.png)

7\. Choose the number of alternate history price paths which are simulated during the backtest.

![4](http://localhost:8000/resources/user_guides/backtester/4_arrow.png)

8\. Choose the length of price paths in the simulation specified in number of days.

![5](http://localhost:8000/resources/user_guides/backtester/5_arrow.png)

9\. Specify the util (% of the bankroll on the bet) to use in the simulation.

The backtesting will assume the utilization on the curve under test is held constant over the
life of the simulation to demonstrate the behavior from using the Kelly Criterion.

![6](http://localhost:8000/resources/user_guides/backtester/6_arrow.png)

10\. Click the Run Backtesting button to start the simulations.

Progress in running the simulation and generating the output plots will be tracked using the
Progress Bars.

![7](http://localhost:8000/resources/user_guides/backtester/7_arrow.png)

When the calculations complete, a plot comparing the CAGR to the Max Drawdown for each
backtesting simulation. One point in the plot corresponds to one input curve.

![perf_vs_dd](http://localhost:8000/resources/user_guides/backtester/performance_vs_drawdown.png)

Results for each backtested curve will be displayed. The curve ID number is shown along with
each of the parameters specified in the input CSV file.

Each of the curve results displays a table containing percentile statistics of the results
across all paths. Each column represents a percentile measurement in the following format:

* p### - percentile, for example p50 corresponds to the median
* user or opt - corresponds to the user curve (red) or the optimal boundary curve from the
Kelly calculation (blue)
* cagr or maxDD - corresponds to the CAGR or the Max Drawdown values  \n
See the full table format [here](./pool_creator_user_guide.html#input-csv-file-format)

For example, p25_user_cagr corresponds to the 25th percentile of CAGR results of the user curve.
p50_opt_maxDD corresponds to the 50th percentile (median) of Max Drawdown results for the
optimal (minimum) boundary curve.

![percentile_stats](http://localhost:8000/resources/user_guides/backtester/percentile_stats.png)

11\. Click to view the generated paths that were used in the simulation. The backtesting code
iterates over each of the price paths and evaluates the results of a simulated Put option trade.

![8](http://localhost:8000/resources/user_guides/backtester/8_arrow.png)

12\. Click to view the Payout and PDF from curve generation compared to the histogram of
backtesting prices.

This plot is useful for showing the assumptions made by the curve generation process compared
to the simulation results, and whether the simulation needs more paths to converge to the
distribution used in curve generation. The prices which are displayed in the histogram bins are
the prices at expiration for each of the backtesting paths.

![9](http://localhost:8000/resources/user_guides/backtester/9_arrow.png)

The next 4 plots display the performance results for the curve. These plots are split into
two columns, the left column contains the results from the user's A, B, C, D Kelly curve (red),
and the results in the right column display the results for the optimal (minimum) boundary Kelly
curve (blue).

![results_panel](http://localhost:8000/resources/user_guides/backtester/results_panel.png)

13\. Click to view the Bankroll plot for the curve. This plot displays the amount of capital
held over time along each of the paths.

![10](http://localhost:8000/resources/user_guides/backtester/10_arrow.png)

14\. Click to view the CAGR plot for the curve. The black line displays the analytical output
value from the Kelly formula which the paths will converge to over time.

![11](http://localhost:8000/resources/user_guides/backtester/11_arrow.png)

15\. Click to view the Util plot for the curve. In this case, the util is held constant at
the value specified by the user.

![12](http://localhost:8000/resources/user_guides/backtester/12_arrow.png)

16\. Click to view the Amounts plot for the curve. This plot displays the number of Put
contracts traded during the simulation.

![13](http://localhost:8000/resources/user_guides/backtester/13_arrow.png)

## Output Log File Format

The output log file is a binary log file stored as a .hdf5 using the Vaex library. This file
can be easily converted to a CSV file for convenient importing into other programs by using
the Log Widget [here](http://localhost:8080/potion/user_guides/log_archive_user_guide.html).

The format of the output log file is as follows:

![output](http://localhost:8000/resources/user_guides/backtester/output.png)

Parameters
-----------
Timestamp : int
    The number of days in the simulation at which the data row was recorded
Training_Key : int
    Indentifies the training data
Exp_Duration : int
    The expiration date of the option in number of days. e.g. 7 is the option expires in 1 week
Strike_Pct : float
    The strike price of the Put option as a multiple of the at-the-money (ATM) price. e.g. 1.0
    is ATM, 0.9 is 10% out-of-the-money (OTM), and 1.1 is 10% in-the-money (ITM), etc.
Path_ID : int
    The id number for the backtesting path
Expiration_Price : float
    The price along the path at the expiration
A : float
    The A parameter for the Kelly curve being backtested
B : float
    The B parameter for the Kelly curve being backtested
C : float
    The C parameter for the Kelly curve being backtested
D : float
    The D parameter for the Kelly curve being backtested
Opt_Premium : float
    The premium collected for the put according to the optimum boundary curve (blue curve in
    curve generator)
Opt_Loss : float
    The loss (if any) of the put for the optimum boundary curve (blue curve in curve generator)
Opt_Payout : float
    The payout of the put for the optimum boundary curve (blue curve in curve generator)
Opt_Amount : float
    The number of put contracts traded for the optimum boundary curve (blue curve in curve
    generator)
Opt_Util : float
    The util used in the simulation for the optimum boundary curve (blue curve in curve generator)
Opt_Locked : float
    The amount of collateral locked for the optimum boundary curve (blue curve in curve generator)
Opt_Bankroll : float
    The bankroll at this timestep for the optimum boundary curve (blue curve in curve generator)
Opt_CAGR : float
    The CAGR at this timestep for the optimum boundary curve (blue curve in curve generator)
Opt_Absolute_Return : float
    The absolute return at this timestep for the optimum boundary curve (blue curve in curve
    generator)
User_Premium : float
    The premium collected for the put according to the user A,B,C,D curve (red curve in curve
    generator)
User_Loss : float
    The loss (if any) of the put for the user A,B,C,D curve (red curve in curve generator)
User_Payout : float
    The payout of the put for the user A,B,C,D curve (red curve in curve generator)
User_Amount : float
    The number of put contracts traded for the user A,B,C,D curve (red curve in curve generator)
User_Util : float
    The util used in the simulation for the user A,B,C,D curve (red curve in curve generator)
User_Locked : float
    The amount of collateral locked for the user A,B,C,D curve (red curve in curve generator)
User_Bankroll : float
    The bankroll at this timestep for the user A,B,C,D curve (red curve in curve generator)
User_CAGR : float
    The CAGR at this timestep for the user A,B,C,D curve (red curve in curve generator)
User_Absolute_Return : float
    The absolute return at this timestep for the user A,B,C,D curve (red curve in curve generator)


[Click here to Open the Pool Creator](http://localhost:8504/)  \n
[Click here to continue to the Pool Creator User Guide](./pool_creator_user_guide.html)

"""
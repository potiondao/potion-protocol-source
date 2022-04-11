"""
# Potion Analytics: THICC
# Pool Backtester User Guide

## Introduction

The pool backtester is a tool that lets the user run a backtesting simulation for a pool of curves
grouped by the [Pool Creator](./pool_creator_user_guide.html). The Pool Creator can configure the
portfolio simulation to run the backtesting with a single curve for the entire pool or separate
curves for each Put.

The CSV inputs to the Pool Backtester are generated as output from the Pool Creator. You can
read about the Pool Creator and how to use it [here](./pool_creator_user_guide.html). This allows
the user to easily import the pools into other programs if desired.

If you want to skip reading about the tool generated CSV file for now, jump to the
[Walkthrough Guide](#walkthrough)

### Input CSV File Format

![input_csv_format](
http://localhost:8000/resources/user_guides/pool_backtester/input_csv_format.png)

Parameters
-----------
Label : str
    Indentifies the training data used for the curve
Backtest_ID : int
    The id number identifying one pool backtesting run from another
Curve_ID : int
    The id number identifying one of the curves in the pool
Asset : str
    The Asset underlying the curve
Expiration : int
    The number of days in the future the Put for the curve expires
StrikePercent : float
    The strike price of the Put option simulated as a multiple of the at-the-money (ATM) price.
    e.g. 1.0 is ATM, 0.9 is 10% out-of-the-money (OTM), and 1.1 is 10% in-the-money (ITM), etc.
A : float
    The A parameter for the Kelly curve being backtested
B : float
    The B parameter for the Kelly curve being backtested
C : float
    The C parameter for the Kelly curve being backtested
D : float
    The D parameter for the Kelly curve being backtested
t_params : List[float]
    The four parameters of the Student's T distribution fit to the Asset training data:
    Location, Scale, Skew, Nu
bet_fractions : List[float]
    The points on the X-axis of the optimum boundary Kelly curve output from the calculator
curve_points : List[float]
    The points on the Y-axis of the optimum boundary Kelly curve output from the calculator

## Walkthrough

<span style="color:red">**NOTE: This part of the guide assumes the Pool Creator tool has already
been run. If not, see this part of the guide**</span> [here](
./pool_creator_user_guide.html#walkthrough)

1\. Select the Batch Number. This should match the Batch Number selected in the Curve Generator
for the results you are interested in backtesting.

This Batch Number allows you to specify a number which will uniquely identify the log files
from different runs of this tool.

![1](http://localhost:8000/resources/user_guides/pool_backtester/1_arrow.png)

2\. Click the Submit button.

![2](http://localhost:8000/resources/user_guides/pool_backtester/2_arrow.png)

3\. The Portfolios which were created for the Batch using the Pool Creator will load and be
displayed in a table to the user. Each portfolio has a matching Backtest_ID to identify the curves.

![loaded_curves](http://localhost:8000/resources/user_guides/pool_backtester/loaded_curves.png)

4\. Select the Portfolio the user would like to create output plots for. The checkboxes on the
bottom of the table allow the user to select all Portfolios, and allow the user to control
whether these output plots are saved as files in the ./batch_results/batch_# directory.

![selected_curves](
http://localhost:8000/resources/user_guides/pool_backtester/selected_curves_arrow.png)

The Portfolios which are currently selected for plotting are displayed in a secondary table
below the checkbox controls. NOTE: If one of the curves in a portfolio is selected, all curves
with the same Backtest_ID (same portfolio) are displayed in the table.

When the portfolio info is loaded, the curve util configuration will be visible in the
Pool Backtest Settings panel.

![curve_util_config](
http://localhost:8000/resources/user_guides/pool_backtester/curve_util_config.png)

3\. Select which probability distribution is used to generate the simulated price paths.

The options include:  \n
* Multivariate Normal - This distribution is the multi asset version of the distribution used in
    Black Scholes to generate the price paths.  \n
* Multivariate Student's T - The Student's T distribution is a common one studied in finance.
    It has 'fat tails' and can be used to model extreme events like market crashes.

![3](http://localhost:8000/resources/user_guides/pool_backtester/3_arrow.png)

4\. Choose the number of alternate history price paths which are simulated during the backtest

![4](http://localhost:8000/resources/user_guides/pool_backtester/4_arrow.png)

5\. Choose the length of price paths in the simulation specified in number of days

![5](http://localhost:8000/resources/user_guides/pool_backtester/5_arrow.png)

6\. Choose a hypothetical starting amount of money (bankroll).

In the pool backtester, this number determines where the user's bankroll plot begins. This plot
graphs the amount of cash the user has over the duration of the simulation

![6](http://localhost:8000/resources/user_guides/pool_backtester/6_arrow.png)

7\. Select a util percentage for each curve. The sum of all curve utils must be greater than 0
and less than 1.

![7](http://localhost:8000/resources/user_guides/pool_backtester/7_arrow.png)

### Optional: Specify a custom covariance matrix

<hr />

If the user wants to specify a custom covariance matrix, they can follow these optional steps.
Otherwise, jump to [Step 11](#running-the-pool-backtester)

8\. Specify the input file. For the format, see the CSV file format [here](#input-csv-file-format)

![8](http://localhost:8000/resources/user_guides/pool_backtester/8_arrow.png)

9\. Select the alpha parameter for the tails of the distribution if Multivariate Student's
T is selected.

![9](http://localhost:8000/resources/user_guides/pool_backtester/9_arrow.png)

10\. Check the box to use the custom covariance matrix

![10](http://localhost:8000/resources/user_guides/pool_backtester/10_arrow.png)

<hr />

### Running the Pool Backtester
11\. Click the Run Backtesting button

![11](http://localhost:8000/resources/user_guides/pool_backtester/11_arrow.png)

When the calculations complete, the results will be displayed below to the user grouped
by Backtest ID.

![backtest_results](
http://localhost:8000/resources/user_guides/pool_backtester/backtest_results.png)

Each of the backtesting results displays a table containing percentile statistics of the
results across all paths.

![percentile_stats](
http://localhost:8000/resources/user_guides/pool_backtester/percentile_stats.png)

Each column represents a percentile measurement in the following format:

* p### - percentile, for example p50 corresponds to the median
* user or opt - corresponds to the user curve (red) or the optimal (minimum) boundary curve
from the Kelly calculation (blue)
* cagr or maxDD - corresponds to the CAGR or the Max Drawdown values  \n
See the full table format [here](./pool_creator_user_guide.html#input-csv-file-format)

For example, p25_user_cagr corresponds to the 25th percentile of CAGR results of the user curve.
p50_opt_maxDD corresponds to the 50th percentile (median) of Max Drawdown results for the
optimal (minimum) boundary curve.

12\. Click to display the Multi Asset Return distribution

![12](http://localhost:8000/resources/user_guides/pool_backtester/12_arrow.png)

Technically, the Multi Asset Return distribution is an N-dimensional probability distribution,
where N is the number of Assets. Since the screen only has 2-dimensions to display, the tool
will display the appropriate number of 2-D marginal distributions for the number of Assets
being simulated.

13\. Click to view the generated paths that were used in the simulation for each of the
Assets. The backtesting code iterates over each of the price paths and evaluates the results
of a simulated Put option trade.

![13](http://localhost:8000/resources/user_guides/pool_backtester/13_arrow.png)

14\. Click to view the Payout and PDF from curve generation compared to the histogram of
backtesting prices.

![14](http://localhost:8000/resources/user_guides/pool_backtester/14_arrow.png)

The next plots display the performance results for the curve. These plots are split into two
columns, the left column contains the results from the user's A, B, C, D Kelly curve (red), and
the results in the right column display the results for the optimal boundary Kelly curve (blue).

![results_panel](
http://localhost:8000/resources/user_guides/pool_backtester/results_panel_boxes.png)

15\. Click to view the Bankroll plot for the curve. This plot displays the amount of capital
held over time along each of the paths.

![15](http://localhost:8000/resources/user_guides/pool_backtester/15_arrow.png)

16\. Click to view the CAGR plot for the curve.

![16](http://localhost:8000/resources/user_guides/pool_backtester/16_arrow.png)

17\. Click to view the Util plot for the curve. In this case, the util is held constant at the
value specified by the user. One Util plot will exist for each Put in the pool.

![17](http://localhost:8000/resources/user_guides/pool_backtester/17_arrow.png)

18\. Click to view the Amounts plot for the curve. This plot displays the number of Put
contracts traded during the simulation. One Amounts plot will exist for each Put in the pool.

![18](http://localhost:8000/resources/user_guides/pool_backtester/18_arrow.png)

## Output Log File Format

The output log file is a binary log file stored as a .hdf5 using the Vaex library. This file
can be easily converted to a CSV file for convenient importing into other programs by using
the Log Widget [here](http://localhost:8506/).

The format of the output log file is as follows:

![output](http://localhost:8000/resources/user_guides/pool_backtester/output.png)

For each Curve with ID \'i\' in the Pool, there is a set of columns in the file.

Parameters
-----------
Timestamp : int
    The number of days in the simulation at which the data row was recorded
Path_ID : int
    The ID number identifying the path
A : float
    The A parameter for the Kelly curve being backtested
B : float
    The B parameter for the Kelly curve being backtested
C : float
    The C parameter for the Kelly curve being backtested
D : float
    The D parameter for the Kelly curve being backtested
Opt_Bankroll : float
    The bankroll at this timestep for the optimum boundary curve (blue curve in curve generator)
Opt_CAGR : float
    The CAGR at this timestep for the optimum boundary curve (blue curve in curve generator)
Opt_Absolute_Return : float
    The absolute return at this timestep for the optimum boundary curve (blue curve in
    curve generator)
User_Bankroll : float
    The bankroll at this timestep for the user A,B,C,D curve (red curve in curve generator)
User_CAGR : float
    The CAGR at this timestep for the user A,B,C,D curve (red curve in curve generator)
User_Absolute_Return : float
    The absolute return at this timestep for the user A,B,C,D curve (red curve in curve generator)
i_Training_Key : int
    Indentifies the training data for Curve i
i_Exp_Duration : int
    The expiration date of the option in number of days for Curve i. e.g. 7 is the option
    expires in 1 week
i_Strike_Pct : float
    The strike price of the Put option as a multiple of the at-the-money (ATM) price for
    Curve i. e.g. 1.0 is ATM, 0.9 is 10% out-of-the-money (OTM), and 1.1 is 10% in-the-money
    (ITM), etc.
i_Price : float
    The price along the path for Curve i.
i_Is_Expired : int
    Whether the Put for Curve i expired at this Timestep. For 0 it did not, other values it
    is expired.
i_Opt_Premium : float
    The premium collected for the put according to the optimum boundary curve for
    Curve i (blue curve in curve
    generator)
i_Opt_Loss : float
    The loss (if any) of the put for the optimum boundary curve for
    Curve i (blue curve in curve generator)
i_Opt_Payout : float
    The payout of the put for the optimum boundary curve for
    Curve i (blue curve in curve generator)
i_Opt_Amount : float
    The number of put contracts traded for the optimum boundary curve for
    Curve i (blue curve in curve generator)
i_Opt_Util : float
    The util used in the simulation for the optimum boundary curve for
    Curve i (blue curve in curve generator)
i_Opt_Locked : float
    The amount of collateral locked for the optimum boundary curve for
    Curve i (blue curve in curve generator)
i_User_Premium : float
    The premium collected for the put according to the user A,B,C,D curve for
    Curve i (red curve in curve generator)
i_User_Loss : float
    The loss (if any) of the put for the user A,B,C,D curve for
    Curve i (red curve in curve generator)
i_User_Payout : float
    The payout of the put for the user A,B,C,D curve for Curve i (red curve in curve generator)
i_User_Amount : float
    The number of put contracts traded for the user A,B,C,D curve for
    Curve i (red curve in curve generator)
i_User_Util : float
    The util used in the simulation for the user A,B,C,D curve for
    Curve i (red curve in curve generator)
i_User_Locked : float
    The amount of collateral locked for the user A,B,C,D curve for
    Curve i (red curve in curve generator)

"""
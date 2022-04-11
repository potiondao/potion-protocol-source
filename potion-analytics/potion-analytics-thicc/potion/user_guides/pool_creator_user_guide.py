"""
# Potion Analytics: THICC
# Pool Creator User Guide

## Introduction

The pool creator is a tool that lets the user group Kelly curve into a portfolio of curves to be
backtested by the [Pool Backtester](./pool_backtester_user_guide.html). This portfolio can be
configured to run the simulation with separate curves for each Put or with a single curve for
the entire portfolio.

The pool creator allows users to either Manually box-select a group of curves from the plot of
backtesting performance results, or run a grouping algorithm to automatically create a pool to
test.

The inputs to the pool creator are generated as output from the backtester. You can read about
the backtester and how to use it [here](./backtester_user_guide.html). The output allows the
user to easily import the results of the backtesting into other programs if desired.

If you want to skip reading about the tool generated CSV file for now, jump to the
[Walkthrough Guide](#walkthrough)

### Input CSV File Format

** The Performance CSV File **

![performance_csv](http://localhost:8000/resources/user_guides/pool_creator/performance_csv.png)

This input summarizes the performance results of the curves tested in the backtester. This CSV is
the full set of percentile statistics tables output from the backtester. The format is:

Parameters
-----------
key : str
    The name of the Asset the Kelly curve was generated for e.g. Bitcoin, Ethereum Plus, the user
    specified label for the set of training data to differentiate it from other training sets on
    the same Asset. e.g. 'Bull', 'Bear'
util : float
    The user specified util used in the backtesting simulation
duration : int
    The expiration date of the option in number of days. e.g. 7 is the option expires in 1 week
strike : float
    The strike price of the Put option as a multiple of the at-the-money (ATM) price. e.g. 1.0 is
    ATM, 0.9 is 10% out-of-the-money (OTM), and 1.1 is 10% in-the-money (ITM), etc.
p00_user_cagr : float
    The 0th percentile (minimum) of the CAGR results for the user A,B,C,D curve (red)
p25_user_cagr : float
    The 25th percentile of the CAGR results for the user A,B,C,D curve (red)
p50_user_cagr : float
    The 50th percentile (median) of the CAGR results for the user A,B,C,D curve (red)
p75_user_cagr : float
    The 75th percentile of the CAGR results for the user A,B,C,D curve (red)
p100_user_cagr : float
    The 100th percentile (maximum) of the CAGR results for the user A,B,C,D curve (red)
p00_opt_cagr : float
    The 0th percentile (minimum) of the CAGR results for the optimal boundary curve (blue)
p25_opt_cagr : float
    The 25th percentile of the CAGR results for the optimal boundary curve (blue)
p50_opt_cagr : float
    The 50th percentile (median) of the CAGR results for the optimal boundary curve (blue)
p75_opt_cagr : float
    The 75th percentile of the CAGR results for the optimal boundary curve (blue)
p100_opt_cagr : float
    The 100th percentile (maximum) of the CAGR results for the optimal boundary curve (blue)
p00_user_maxDD : float
    The 0th percentile (minimum) of the Max Drawdown results for the user A,B,C,D curve (red)
p25_user_maxDD : float
    The 25th percentile of the Max Drawdown results for the user A,B,C,D curve (red)
p50_user_maxDD : float
    The 50th percentile (median) of the Max Drawdown results for the user A,B,C,D curve (red)
p75_user_maxDD : float
    The 75th percentile of the Max Drawdown results for the user A,B,C,D curve (red)
p100_user_maxDD : float
    The 100th percentile (maximum) of the Max Drawdown results for the user A,B,C,D curve (red)
p00_opt_maxDD : float
    The 0th percentile (minimum) of the Max Drawdown results for the optimal boundary curve (blue)
p25_opt_maxDD : float
    The 25th percentile of the Max Drawdown results for the optimal boundary curve (blue)
p50_opt_maxDD : float
    The 50th percentile (median) of the Max Drawdown results for the optimal boundary curve (blue)
p75_opt_maxDD : float
    The 75th percentile of the Max Drawdown results for the optimal boundary curve (blue)
p100_opt_maxDD : float
    The 100th percentile (maximum) of the Max Drawdown results for the optimal boundary
    curve (blue)

## Walkthrough

<span style="color:red">**NOTE: This part of the guide assumes the Backtester tool has already
been run. If not, see this part of the guide**</span> [here](
./backtester_user_guide.html#walkthrough)

1\. Select the Batch Number. This should match the Batch Number selected in the Curve
Generator for the results you are interested in creating a portfolio for. These results are
automatically detected by the tool looking for sub-directories named batch_# in the directory
'batch_results', where the number is the number selected in the Curve Generator tool. For example:
./batch_results/batch_7

This Batch Number allows you to specify a number which will uniquely identify the log files
from different runs of this tool.

![1](http://localhost:8000/resources/user_guides/pool_creator/1_arrow.png)

2\. Click the Submit button.

![2](http://localhost:8000/resources/user_guides/pool_creator/2_arrow.png)

When the backtesting results are loaded, a plot comparing the CAGR to the Max Drawdown for
each backtesting simulation will display. One point in the plot corresponds to one input curve.

From here, the user will have two choices to create a pool, Manual or Automatic

### Manual Pool Creation

For manual, the process is as follows:

3\. Select the rows which correspond to curves the user wishes to add to the portfolio.

![row_select](http://localhost:8000/resources/user_guides/pool_creator/row_select_arrow.png)

4\. The selected curves will display in a table below containing the Current Selection.

5\. Click the Create Pool button on the Manual Pool Creation panel.

![manual_pool](http://localhost:8000/resources/user_guides/pool_creator/manual_pool_arrow.png)

Below, a new panel will appear containing the selected curves

![manual_output](http://localhost:8000/resources/user_guides/pool_creator/manual_output.png)

From here, the user can either choose to select one curve to use for the entire pool or keep the
curves separate.

6a\. To use separate curves, unselect the check box.

![6a](http://localhost:8000/resources/user_guides/pool_creator/single_curve_check_arrow.png)

7a\. Click Add Pool to Input Dataframe to add to the input for the Pool Backtester

![7a](http://localhost:8000/resources/user_guides/pool_creator/add_pool_arrow.png)

6b\. To use one curve, select the check box.

![6b](http://localhost:8000/resources/user_guides/pool_creator/single_curve_check_arrow.png)

7b\. Select the curve number to be used as the curve for the entire pool

![7a](http://localhost:8000/resources/user_guides/pool_creator/select_curve_arrow.png)

8\. Click Add Pool to Input Dataframe to add to the input for the Pool Backtester

![8](http://localhost:8000/resources/user_guides/pool_creator/add_pool_arrow.png)

### Automatic Pool Creation

3\. Select the number of performance groups to split the results by risk adjusted backtest
performance. First, the results are ranked by a score CAGR/MaxDD. Second, the number of groups
determines how the ranking is split.

For example, if number of groups is 4, group 1 is the top 25%, group 2 is 25%-50%, group 3 is 50%
to 75%, and group 4 is 75% to 100%

By setting this value to 1, the code will run only the clustering and use the Number of Clusters
parameter instead

![num_p_groups](http://localhost:8000/resources/user_guides/pool_creator/num_p_groups_arrow.png)

4\. Select the number of clusters to split the curves by their similarity in shape. First, a
similarity matrix is calculated for the points in one or more groups of curves, and then a
clustering algorithm is performed to group curves into pools.

By setting this value to 1, the code will run only the performance grouping and use the Number of
Performance Groups parameter instead.

![num_clusters](http://localhost:8000/resources/user_guides/pool_creator/num_clusters_arrow.png)

5\. Click the Create Pools button

![create_pools](http://localhost:8000/resources/user_guides/pool_creator/create_pools_arrow.png)

Below, a new panel will appear containing the grouped curves

![automatic_output](http://localhost:8000/resources/user_guides/pool_creator/automatic_output.png)

From here, the user can either choose to select one curve to use for the entire pool or keep the
curves separate.

6a\. To use separate curves, unselect the check box.

![6a](http://localhost:8000/resources/user_guides/pool_creator/single_curve_check_arrow.png)

7a\. Click Add Pool to Input Dataframe to add to the input for the Pool Backtester

![7a](http://localhost:8000/resources/user_guides/pool_creator/add_pool_arrow.png)

6b\. To use one curve, select the check box.

![6b](http://localhost:8000/resources/user_guides/pool_creator/single_curve_check_arrow.png)

7b\. Select the curve number to be used as the curve for the entire pool

![7a](http://localhost:8000/resources/user_guides/pool_creator/select_curve_arrow.png)

8\. Click Add Pool to Input Dataframe to add to the input for the Pool Backtester

![8](http://localhost:8000/resources/user_guides/pool_creator/add_pool_arrow.png)

From here, the output should display below, which is the input CSV to the Pool Backtester.

![output](http://localhost:8000/resources/user_guides/pool_creator/pool_backtester_input.png)

The format of this CSV will be discussed as part of the Pool Backtester [section](
./pool_backtester_user_guide.html) where it is used as input.


[Click here to Open the Pool Backtester](http://localhost:8505/)  \n
[Click here to continue to the Pool Backtester User Guide](./pool_backtester_user_guide.html)

"""
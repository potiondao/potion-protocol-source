"""
# Potion Analytics: THICC
# Curve Generator User Guide

## Introduction
The Curve Generator is a tool that lets the user demo generating Kelly curves for a Put option
from the perspective of the seller. This tool performs the generation based on two input CSV files.

The first file is a simple CSV configuration file where each row specifies a curve that the user
would like to generate. The second file contains historical price data for each asset which will
be used by the tool to calculate a probability distribution for the Asset's financial returns.
The distribution used here is a type of Student's T, which is a common one studied in finance
and is also capable of representing the 'fat tails' of big market events.

**These files do not need to be created by hand.**  \n

The configuration Input CSV File can be generated using the Subgraph Downloader tool:  \n
[Click here to Open the Subgraph Downloader](http://localhost:8508/)  \n
[Click here to Open Subgraph Downloader User Guide](./subgraph_downloader_user_guide.html)  \n

The Historical Price Data CSV File can be generated using the Historical Data Downloader tool:  \n
[Click here to Open the Historical Data Downloader](http://localhost:8507/)  \n
[Click here to Open the Historical Data Downloader User Guide](
http://localhost:8080/potion/user_guides/historical_data_downloader_user_guide.html)  \n

If you want to skip reading about the CSV files for now, jump to the
[Walkthrough Guide](#walkthrough)

### Input CSV File Format

The format of this CSV file is as follows:

![input_csv_format](http://localhost:8000/resources/user_guides/curve_gen/input_csv_format.png)

This input file will tell the curve generator app:  \n

Parameters
-----------
Asset : str
    Which Asset the user is interested in generating a curve for (BTC, ETH, etc.)
TrainingLabel : str
    A Training Label which is a label the user should use to uniquely identify training data
    selected. For example, if the user wanted to look at the same option generated from bull
    market or bear market data, they might choose ETH-bull and ETH-bear.
TrainingStart : str
    The start date of the training data window in the historical price data in the format %d/%m/%Y
TrainingEnd : str
    The end date of the training data window in the historical price data in the format %d/%m/%Y
StrikePct : float
    The strike price of the Put option as a multiple of the at-the-money (ATM) price. e.g. 1.0
    is ATM, 0.9 is 10% out-of-the-money (OTM), and 1.1 is 10% in-the-money (ITM), etc.
Expiration : int
    The expiration date of the option in number of days. e.g. 7 is the option expires in 1 week
CurrentPrice : float
    The current price of the asset so the user can display prices in absolute USDC terms if they
    choose that setting within the tool

### Historical Price Data File Format

The format of this CSV file is as follows:

![historical_csv_format](
http://localhost:8000/resources/user_guides/curve_gen/historical_csv_format.png)

This input file will tell the curve generator app:  \n

Parameters
-----------
MasterCalendar : str
    A column of dates recording the price of each asset on each historical day in
    the format %d/%m/%Y
Asset : float
    A column of prices. Can have as many columns as necessary to record the historical prices on
    each date for each asset of interest to the user

## Walkthrough

1\. Select the Input CSV File. This dropdown will automatically detect any CSV files in the
inputs directory

![1](http://localhost:8000/resources/user_guides/curve_gen/1_arrow.png)

2\. Select the Historical Prices CSV File. This dropdown will automatically detect any CSV
files in the resources directory

![2](http://localhost:8000/resources/user_guides/curve_gen/2_arrow.png)

3\. Select the Batch Number. The Batch Number is a number used to uniquely identify log files
between multiple runs in the log directory. Tools like the [Log File Widget](
http://localhost:8506/) use this number to determine which files to Zip into a convenient
archive file.

![3](http://localhost:8000/resources/user_guides/curve_gen/3_arrow.png)

4\. Choose a hypothetical starting amount of money (bankroll)

![4](http://localhost:8000/resources/user_guides/curve_gen/4_arrow.png)

5\. Click the Generate Curves button

![5](http://localhost:8000/resources/user_guides/curve_gen/5_arrow.png)

As the calculations complete, each generated curve will be displayed. The curve ID number
(determined by CSV row) is shown along with each of the parameters specified in the CSV file.

The Curve Plot shows a red and a blue line. The blue line is the optimal boundary output curve
from the Kelly calculation (discussed later in the guide). The red line is a best-fit line
which the user can adjust to their preferences by following along with this guide.

![generated_curve](http://localhost:8000/resources/user_guides/curve_gen/generated_curve.png)

On the X-axis of the plot, the values represent the utilization or betting fraction of the total
money available. A utilization of 0 would correspond to betting nothing, and a utilization of 1
would correspond to betting everything on the Put. On the Y-axis of the plot, the values
represent the premium collected for the Put.

The guide will circle back to the curves later, but for now let's talk about the Kelly calculation.

The Kelly calculation has two inputs, a probability distribution and a payoff function for the
Put. These inputs for each curve can be seen by expanding the Show PDF and Option Payout panel.

6\. Expand the PDF and Payout panel

![6](http://localhost:8000/resources/user_guides/curve_gen/6_arrow.png)

The blue line represents the probability density (PDF) at the expiration of the Put option. This
is calculated from the user supplied prices in the Historical Prices CSV File and the training
data window specified by the Input CSV File. Learn more about selecting these values [here](
./subgraph_downloader_user_guide.html).

The red line represents the payoff function of the Put in terms of profit and loss. If the
price drops to 0, the Put will lose everything, and if the price is above the strike, the Put
will expire worthless and a premium is collected.

The question the Kelly formula will answer is: if this bet was repeated over and over - according
to this probability distribution, would the Put seller be gaining money on average? or losing
money. The Kelly formula calculates whether there is 'casino edge' and the amount of premium
collected is covering the losses of when the price goes down on average.

Returning to the Kelly Curve plot, we can see the blue line is the optimal boundary curve
output from the Kelly calculation. According to the input probability: for premium amounts
above the blue curve, the Put seller would be making money on average. For premium amounts
below the blue curve, the Put seller would be losing money on average.

![adjusted_curve](http://localhost:8000/resources/user_guides/curve_gen/adjusted_curve.png)

Now, it is apparent why a user would want to adjust the red curve up into the area above the
blue curve. A higher curve means that the bet would be making more money on average.

### Why not just set the curve really really high?

The higher the asking price for the Put, the less competitive and less likely it is that a
buyer would be willing to pay that high price from a seller. Simulating a scenario with an
unrealistically high price is possible for the user to do with the tool, but it may not be
very useful. The simulator will assume a buyer is present to calculate the outputs.

### Why not set the curve really low (close to the blue curve)?

The lower the asking price for the Put, the more competitive and more likely it is that a
buyer would be willing to buy it from a seller. However, the blue line is also a theoretical
value being output by the calculator.

There are differences between the simulator and a live market (like assuming the order is
always filled, mentioned earlier). In addition, the data the user gives the calculator might
be bad or incomplete. If these errors and others were included in the math model, and the
calculation performed again - the blue curve might shift higher.

If the user sets the red curve close to the blue curve, they risk having a false sense of
security. The unknown 'true' blue curve would end up being above their red curve, and even
though the calculator said money would be earned on average it would be lost in practice.

Finding a balance between these two extremes will depend on the preferences of each user
running a simulation. A conservative user might set their curve high, while another user
might set their curve low.

### Ok, how can I adjust the curve in the tool?

To adjust the curve, use the Edit Curve panel.

7\. Expand the Edit Curve panel

![7](http://localhost:8000/resources/user_guides/curve_gen/7_arrow.png)

8\. Adjust the A, B, C, and D parameters

![8](http://localhost:8000/resources/user_guides/curve_gen/8_arrow.png)

9\. Click the Update Curve button

![9](http://localhost:8000/resources/user_guides/curve_gen/9_arrow.png)

The curve parameters should update in the Show Parameters panel, as well as the inputs on the
Edit Curve panel.

![param_table](http://localhost:8000/resources/user_guides/curve_gen/param_table.png)

### Other Features

On the panel Show Training Data Price Path, the selected region of training data used to
generate the PDF for the Kelly calculation is displayed.

First, the entire price path of the asset's history in the Historical Price Data File
is graphed. Second, the selected window of training data is graphed to show what prices were
used to generate the return PDF.

![10](http://localhost:8000/resources/user_guides/curve_gen/10_arrow.png)

On the Configure Plots panel, there are a few radio buttons which control settings about
the plots. First, the Select Curve Units toggle, will change the units of the Kelly Curve plot
to be in Relative terms (relative to the Put strike price) or in Absolute terms (absolute
USDC numbers).

Next, the Enable Curve Plot Grid toggle changes the grid on the Kelly Curve plot to be visible
or invisible. Finally, the Training Data Log Prices toggle changes the prices on the Training
Data Price Path panel to be in log scale. Sometimes, this is convenient viewing the full range
of data when an asset has appreciated in price a lot.

![11](http://localhost:8000/resources/user_guides/curve_gen/11.png)

At the bottom of the page, the Output CSVs panel can be expanded.

10\. Expand the Output CSVs panel

![output](http://localhost:8000/resources/user_guides/curve_gen/output.png)

The format of these CSVs will be discussed as part of the Backtester [section](
./backtester_user_guide.html) where they are used as inputs. When user adjustments are made
with the Edit Curve panel, these CSV outputs will update.

[Click here to Open the Backtester](http://localhost:8503/)  \n
[Click here to continue to the Backtester User Guide](./backtester_user_guide.html)  \n

"""

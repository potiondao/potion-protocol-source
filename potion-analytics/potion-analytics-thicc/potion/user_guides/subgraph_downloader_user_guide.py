"""
# Potion Analytics: THICC
# Subgraph Downloader and CSV Input Creator User Guide

Note: 'CoinGecko' is a registered trademark of Gecko Labs PTE LTD

## Introduction
The Subgraph Downloader is a tool that lets the user connect to the subgraph and
download existing Potions which the user may want to input to the simulator. If the user wants to
 simulate a curve for an asset on CoinGecko, there is also a method to manually select a Potion.
This tool requires a historical data file for different crypto Assets as an input. This file can
be created using the [Historical Data Downloader](http://localhost:8507/). Learn more by
consulting the [Historical Data Downloader User Guide](
http://localhost:8080/potion/user_guides/historical_data_downloader_user_guide.html).

This widget creates a CSV file which is the correct format the [Curve Generator](
http://localhost:8502/) tool is expecting. Learn more by consulting the
[Curve Generator User Guide](./curve_generator_user_guide.html).

## Walkthrough

<span style="color:red">**NOTE: This part of the guide assumes the Historical Data Downloader tool
has already been run and a CSV file was created. If not, see this part of the
guide**</span> [here](./historical_data_downloader_user_guide.html#walkthrough)

1\. Select the Input CSV File. This dropdown will automatically detect any CSV files in
the resources directory.

![1](http://localhost:8000/resources/user_guides/subgraph_downloader/1_arrow.png)

2\. Click the button to query the subgraph.

![2](http://localhost:8000/resources/user_guides/subgraph_downloader/3_arrow.png)

3\. Select the index of the DataFrame containing the row the user would like to add to the input
CSV which will be used by the Curve Generator tool.

![3](http://localhost:8000/resources/user_guides/subgraph_downloader/4_arrow.png)

4\. Click Add Row to Input.

![4](http://localhost:8000/resources/user_guides/subgraph_downloader/5_arrow.png)

** Optional: Add Assets from CoinGecko **

If the user's favorite token is not on the subgraph, it can be added from the list of CoinGecko
Assets.

5\. Select the Asset, Strike, and Expiration the user wants to simulate.

![5](http://localhost:8000/resources/user_guides/subgraph_downloader/6_arrow.png)

6\. Click Add Row to Input.

![6](http://localhost:8000/resources/user_guides/subgraph_downloader/7_arrow.png)

After adding any number of rows to the input file, panels will appear below containing the
training data selection:

![training](http://localhost:8000/resources/user_guides/subgraph_downloader/training.png)

7\. Select the start date for the training data window.

![7](http://localhost:8000/resources/user_guides/subgraph_downloader/8_arrow.png)

8\. Select the end date for the training data window.

![8](http://localhost:8000/resources/user_guides/subgraph_downloader/9_arrow.png)

9\. Select a user custom training label to uniquely identify this Potion from others with the same
Asset, Strike, and Expiration but a different training data window. Examples include: 'Full',
'Bull', 'Bear', 'PastYear', etc.

![9](http://localhost:8000/resources/user_guides/subgraph_downloader/10_arrow.png)

** Optional: Override the current price and specify a different one **

10\. Check the box to override the current price.

![10](http://localhost:8000/resources/user_guides/subgraph_downloader/11_arrow.png)

11\. Specify the custom current price.

![11](http://localhost:8000/resources/user_guides/subgraph_downloader/12_arrow.png)

12\. Click the Select Training Window button.

![12](http://localhost:8000/resources/user_guides/subgraph_downloader/13_arrow.png)

When the training data is selected, a red line will appear highlighting the selected price region.

![training_path](http://localhost:8000/resources/user_guides/subgraph_downloader/training_path.png)

13\. Choose a name for the CSV File.

![13](http://localhost:8000/resources/user_guides/subgraph_downloader/14_arrow.png)

14\. Click the button to write the CSV File.

![14](http://localhost:8000/resources/user_guides/subgraph_downloader/15_arrow.png)

15\. Continue to the Curve Generator now that the user has both the Historical Data CSV and the
Curve Input CSV File.

[Click here to Open the Curve Generator](http://localhost:8502/)  \n
[Click here to Open the Curve Generator User Guide](./curve_generator_user_guide.html)  \n

"""
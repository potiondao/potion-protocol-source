"""
# Potion Analytics: THICC
# Historical Data Downloader User Guide

Note: 'CoinGecko' is a registered trademark of Gecko Labs PTE LTD

## Introduction
The Historical Data Downloader is a tool that lets the user connect to the CoinGecko API and
download historical data for different crypto Assets as an input to the simulators. This widget
creates a CSV file which is the correct format the tool is expecting.

This CSV file is used by the [Curve Generator tool](./curve_generator_user_guide.html).

## Walkthrough

1\. Select a Ticker symbol the user is interested in downloading. This dropdown will automatically
be populated with the Ticker symbols CoinGecko reports in its API. Typing in the dropdown will
search the available tickers.

![1](http://localhost:8000/resources/user_guides/price_fetch/1_arrow.png)

2\. Click the Add Ticker to Download button.

![2](http://localhost:8000/resources/user_guides/price_fetch/2_arrow.png)

3\. Repeat Steps 1 and 2 until all of the Ticker symbols of interest are added.

As more tickers are added, they will appear in the table for Merging.

![3](http://localhost:8000/resources/user_guides/price_fetch/3.png)

4\. Choose a name for the CSV file. The file will be saved in the resources directory.

![4](http://localhost:8000/resources/user_guides/price_fetch/4_arrow.png)

5\. Click the Merge Into CSV button when the user wants to generate the CSV Output.

![5](http://localhost:8000/resources/user_guides/price_fetch/5_arrow.png)

After the CSV is created, the file will be displayed as a table below:

![output](http://localhost:8000/resources/user_guides/price_fetch/output.png)

6\. If the user would like to clear the selected tickers and start over, click the Clear Ticker
Table button.

![6](http://localhost:8000/resources/user_guides/price_fetch/6_arrow.png)

Next, the user should create an input CSV for the Curve Generator tool. This is done using the
Subgraph Downloader and Input CSV Creator tool:  \n
[Click here to Open the Subgraph Downloader](http://localhost:8508/)  \n
[Click here to Open the Subgraph Downloader User Guide](./subgraph_downloader_user_guide.html)

This output CSV is used for the Curve Generator tool:  \n
[Click here to Open the Curve Generator](http://localhost:8502/)  \n
[Click here to Open the Curve Generator User Guide](./curve_generator_user_guide.html)  \n

"""
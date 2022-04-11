"""
# Potion Analytics: THICC
# Log Management Widget User Guide

## Introduction

This Log Management widget allows the user to manage the results files from the various tools.

The backtesting tools output their results as a binary file for efficiency and speed. For
convenience, the Log Converter tool allows the user to convert this log to CSV. This is helpful
if the user would like to input the results into other programs for analysis.

The Log Archive tool allows the user to conveniently zip the output files into one zip archive.
Results output by the tool are stored in the batch_results directory.

## Walkthrough

** Log Conversion **

The output file from backtesting is stored as a binary file for efficiency. If the user would like
to covert the binary file into CSV format to load into other programs, this tool will convert the
file to CSV.

1\. Select the Log File the user would like to convert.

![1](http://localhost:8000/resources/user_guides/log_archive/1_arrow.png)

2\. Click the Convert to CSV button.

![2](http://localhost:8000/resources/user_guides/log_archive/2_arrow.png)

** Log Archive Tool **

The results files are stored in the directory batch_results. This tool collects the log files
and plot images that the user is interested in, and zips them into a convenient ZIP archive.

3\. Select the Batch Number for the results of interest.

![3](http://localhost:8000/resources/user_guides/log_archive/3_arrow.png)

4\. Select the type of files to include in the ZIP file, and whether to delete files after
including them in the archive.

![4](http://localhost:8000/resources/user_guides/log_archive/4_arrow.png)

5\. Click the Archive Results button.

![5](http://localhost:8000/resources/user_guides/log_archive/5_arrow.png)
"""
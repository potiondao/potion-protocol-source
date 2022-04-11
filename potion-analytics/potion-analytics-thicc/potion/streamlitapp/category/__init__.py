"""
This module provides the GUI for the portfolio creator tool
"""
PC_BATCH_NUMBER_HELP_TEXT = 'This number spinner allows you to specify a number which will uniquely identify the log ' \
                            'files from different runs of this tool.  \n\nResults and log files will appear in the ' \
                            'directory \'batch\\_results\' with the file prefix \'batch\\_\\*\'.  \n\nFor example: ' \
                            'batch\\_0\\_backtest\\_performance.csv'

PC_NUM_PER_GRPS_HELP_TEXT = 'Choose to split the curves by risk adjusted backtest performance. First, the results ' \
                            'are ranked by a score CAGR/MaxDD. Second, the number of groups determines how the ' \
                            'ranking is split. For example, if number of groups is 4, group 1 is the top 25%, group ' \
                            '2 is 25%-50%, group 3 is 50% to 75%, and group 4 is 75% to 100%  \n\n' \
                            'By setting this value to 1, the code will run only the clustering and use the ' \
                            'Number of Clusters parameter instead'

PC_NUM_POOLS_HELP_TEXT = 'Choose to split the curves by their similarity in shape. First, a similarity matrix is ' \
                         'calculated for the points in one or more groups of curves, and then a clustering algorithm ' \
                         'is performed to group curves into pools.  \n\n' \
                         'By setting this value to 1, the code will run only the performance grouping and use the ' \
                         'Number of Performance Groups parameter instead.'

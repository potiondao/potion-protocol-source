"""
This module provides the GUI for the curve creator tool
"""
CG_INPUT_FILE_HELP_TEXT = 'This dropdown allows you to select an input file for the curve generator. This file ' \
                          'specifies what Potion options you are interested in generating curves for and ' \
                          'simulating.  \n\nThe format of this CSV file can be found in the documentation ' \
                          '[here](https://127.0.0.1:80). **This file does not need to be created by hand.** ' \
                          'Learn more [here](https://127.0.0.1:80).  \n\n' \
                          'This input file will tell the curve generator app:  \n' \
                          '* which Assets you are interested in (BTC, ETH, etc.) \n' \
                          '* a Training Label which is a label you should use to uniquely identify ' \
                          'training data you selected. For example, if you wanted to look at the same option ' \
                          'generated from bull market or bear market data, you might choose ' \
                          'ETH-bull and ETH-bear. \n' \
                          '* The start date of the training data window in the historical price data  \n' \
                          '* The end date of the training data window in the historical price data  \n' \
                          '* The strike price of the option as a multiple of the at-the-money ' \
                          'price (e.g. 1.0 is ATM)  \n ' \
                          '* The expiration date of the option in number of days (e.g. 7 is the option ' \
                          'expires in 1 week)  \n' \
                          '* Finally, the current price of the asset so the user can display prices in absolute ' \
                          'terms.  \n\n' \
                          'This dropdown box will automatically detect any CSV file located in the current ' \
                          'directory of the project and lets you select the input file you want to use.'

CG_PRICES_FILE_HELP_TEXT = 'This dropdown allows you to select a historical prices file for the curve generator. ' \
                           'This file specifies the training data which will allow the generator to calculate ' \
                           'the distribution of historical returns for each underlying asset.  \n\n' \
                           'The format of this CSV file can be found in the documentation ' \
                           '[here](https://127.0.0.1:80). **This file does not need to be created by hand.** ' \
                           'Learn more [here](https://127.0.0.1:80).  \n\n' \
                           'This dropdown box will automatically detect any CSV file located in the resources ' \
                           'directory of the project and lets you select the input file you want to use.'

CG_BATCH_NUMBER_HELP_TEXT = 'This number spinner allows you to specify a number which will uniquely identify the log ' \
                            'files from different runs of this tool.  \n\nResults and log files will appear in the ' \
                            'directory \'batch\\_results\' with the file prefix \'batch\\_\\*\'.  \n\nFor example: ' \
                            'batch\\_0\\_curves.csv'

CG_INIT_BANKROLL_HELP_TEXT = 'This number spinner allows you to specify a hypothetical amount of starting cash to bet' \
                             ' with. In the curve generator, this number is for display purposes only (if you choose ' \
                             'to display the outputs in absolute units).'

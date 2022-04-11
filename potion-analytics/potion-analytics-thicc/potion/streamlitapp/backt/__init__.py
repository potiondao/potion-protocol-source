"""
This module provides the GUI tool for creating, running, and plotting backtesting simulations
"""
BT_BATCH_NUMBER_HELP_TEXT = 'This number spinner allows you to specify a number which will uniquely identify the log ' \
                            'files from different runs of this tool.  \n\nResults and log files will appear in the ' \
                            'directory \'batch\\_results\' with the file prefix \'batch\\_\\*\'.  \n\nFor example: ' \
                            'batch\\_0\\_backtest\\_performance.csv'

BT_INIT_BANKROLL_HELP_TEXT = 'This number spinner allows you to specify a hypothetical amount of starting cash to bet' \
                             ' with. In the backtester, this number determines where the user\'s bankroll plot ' \
                             'begins. This plot graphs the amount of cash the user has over the duration of ' \
                             'the simulation'

BT_PATH_GEN_METHOD_HELP_TEXT = 'Controls which probability distribution is used to generate the simulated price ' \
                               'paths. \nThe options include:  \n' \
                               '* Histogram - This distribution does not make any assumptions about what the ' \
                               'asset\'s return distribution may be. As more price data is collected the Histogram ' \
                               'will \'learn\' and approach the asset\'s return distribution.  \n' \
                               '* Student\'s T with Skew - The Student\'s T distribution is a common one studied ' \
                               'in finance. It has \'fat tails\' and can be used to model extreme events like ' \
                               'market crashes. The skewed version allows the distribution to not be required ' \
                               'to be symmetric. If you are not sure which to pick, start simulating paths with ' \
                               'Student\'s T since the simulation will be more conservative.'

BT_NUM_PATHS_HELP_TEXT = 'Chooses the number of future price paths which are simulated during the backtest'

BT_PATH_LEN_HELP_TEXT = 'Chooses the length of price paths in the simulation specified in number of days'

BT_UTIL_HElP_TEXT = 'Specifies the user\'s util (% of their bankroll in the bet) to use in the simulation. ' \
                    'The backtesting will assume the utilization on the curve under test is held constant ' \
                    'over the life of the simulation to demonstrate the behavior from using the ' \
                    'Kelly Criterion to bet. '

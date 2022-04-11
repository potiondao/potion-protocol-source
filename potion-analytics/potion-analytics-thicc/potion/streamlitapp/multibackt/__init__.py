"""
This module provides the GUI for the portfolio (multi asset) backtester tool
"""
PB_BATCH_NUMBER_HELP_TEXT = 'This number spinner allows you to specify a number which will uniquely identify the log ' \
                            'files from different runs of this tool.  \n\nResults and log files will appear in the ' \
                            'directory \'batch\\_results\' with the file prefix \'batch\\_\\*\'.  \n\nFor example: ' \
                            'batch\\_0\\_ma\\_backtest\\_0\\_user\\_util.svg'

PB_PATH_GEN_HELP_TEXT = 'Controls which probability distribution is used to generate the simulated price ' \
                        'paths. \nThe options include:  \n' \
                        '* Multivariate Normal - This is a simple normal distribution which has a covariance matrix ' \
                        'that specifies the relationship between the asset returns. This matrix can be ' \
                        'supplied manually below. If no custom covariance matrix is supplied, these parameters ' \
                        'will be estimated from historical price data.  \n' \
                        '* Multivariate Student\'s T - The Student\'s T distribution is a common one studied in ' \
                        'finance. It has \'fat tails\' and can be used to model extreme events like market crashes. ' \
                        'The covariance matrix specifies the linear dependence between the assets, and the tail ' \
                        'index specifies the nonlinear dependence. It is possible to specify these manually below. ' \
                        'If no custom covariance matrix is supplied, these parameters will be estimated from price ' \
                        'data. If you are not sure which to pick, start simulating paths with Multivariate ' \
                        'Student\'s T since the simulation will be more conservative.'

PB_NUM_PATHS_HELP_TEXT = 'Chooses the number of future price paths which are simulated during the backtest'

PB_PATH_LENGTH_HELP_TEXT = 'Chooses the length of price paths in the simulation specified in number of days'

PB_INIT_BANKROLL_HELP_TEXT = 'This number spinner allows you to specify a hypothetical amount of starting cash to bet' \
                             ' with. In the backtester, this number determines where the user\'s bankroll plot ' \
                             'begins. This plot graphs the amount of cash the user has over the duration of ' \
                             'the simulation'

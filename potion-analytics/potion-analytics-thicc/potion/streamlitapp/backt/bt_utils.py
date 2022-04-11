"""
This module provides helper functions for the backtesting tool
"""

def calculate_max_drawdown(bankroll):
    """
    Calculates the maximum drawdown of a 1-D numpy array

    bankroll : numpy.ndarray
        The array representing the betting bankroll

    Returns
    -------
    max_dd : float
        Maximum drawdown along the path as a percentage
    """
    highest_val_seen = 0.0
    max_drawdown_seen = 0.0
    for value in bankroll:

        if value >= highest_val_seen:
            highest_val_seen = value

        drawdown = (value - highest_val_seen) / highest_val_seen

        if drawdown < max_drawdown_seen:
            max_drawdown_seen = drawdown

    # Return as a percentage
    return max_drawdown_seen * 100.0

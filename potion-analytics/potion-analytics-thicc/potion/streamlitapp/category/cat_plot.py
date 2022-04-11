"""
This module provides the plots which the portfolio creator tool produces for the GUI
"""
import plotly.graph_objects as go
from potion.curve_gen.kelly import evaluate_premium_curve


def plot_curves_in_pool(pool_df, bf_list):
    """
    This function generates a plotly plot for displaying the curves contained in a pool

    Parameters
    -----------
    pool_df : pandas.DataFrame
        A DF containing the pool info
    bf_list : List[numpy.ndarray]
        A list of bet_fraction arrays to use as the X axis in the plot

    Returns
    -----------
    fig : plotly.graph_objects.Figure
        A Plotly figure to display
    """
    fig = go.Figure()

    for i, row in pool_df.iterrows():

        fit_params = [row.A, row.B, row.C, row.D]
        bet_fractions = bf_list[i]

        user_points_for_id = evaluate_premium_curve(fit_params, bet_fractions)

        lab = 'Curve {}'.format(row.ID)

        fig.add_trace(go.Scatter(x=bet_fractions, y=user_points_for_id, mode='lines', name=lab))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Utilisation',
        yaxis_title='Premium (%)').update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    return fig

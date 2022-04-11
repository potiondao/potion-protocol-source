
import os
import numpy as np
import pandas as pd
from scipy.stats import norm

import plotly.graph_objects as go

from potion.curve_gen.constraints.puts_no_arb_constraints import (
    monotonic_lb_cond, monotonic_ub_cond, convex_lb_cond, zero_bound_cond,
    call_zero_bound_by_pcp_cond, calendar_ub_cond, monotonic_lb, monotonic_ub, convex_lb,
    zero_bound, call_zero_bound_by_pcp, calendar_ub)
from potion.curve_gen.payoff.black_scholes import put
from potion.curve_gen.training.fit.helpers import calc_log_returns
from potion.curve_gen.kelly import evaluate_premium_curve
from potion.curve_gen.utils import build_generator_config
from potion.curve_gen.gen import configure_curve_gen, generate_curves
from potion.curve_gen.utils import make_payoff_dict, add_leg_to_dict
from potion.curve_gen.convolution.convolution import get_pdf_arrays
from potion.curve_gen.analysis.plot import (pdf_and_payout_sweep, kelly_growth_sweep,
                                            kelly_derivative_sweep, plot_curve, show)


def test_put_call(show_figs=True):
    """
    Testing put call parity using a synthetic long (sell put and buy call same strike)

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    payoff_dict = {
        'und_price': 1.0,
        'und_amt': 1.0
    }

    cfg = build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict)

    configure_curve_gen(cfg)
    curve_df, pdf_df, training_df = generate_curves(payoff_dict=payoff_dict,
                                                    bet_fractions=np.linspace(0.0, 0.9999, 500))

    pdf_x, pdfs_y = get_pdf_arrays()

    min_prem = 0.001
    max_prem = 0.03
    fig1 = pdf_and_payout_sweep(pdf_x, pdfs_y[0],
                                np.linspace(min_prem, max_prem, 10), 'ETH', legend=False)
    fig2 = kelly_growth_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                              np.linspace(0.0, 0.9999, 50))
    fig3 = kelly_derivative_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                                  np.linspace(0.0, 0.9999, 50))
    fig4 = plot_curve([curve_df.A.values[0], curve_df.B.values[0],
                       curve_df.C.values[0], curve_df.D.values[0]],
                      curve_df.bet_fractions.values[0], curve_df.curve_points.values[0])

    if show_figs:
        show(fig1)
        show(fig2)
        show(fig3)
        show(fig4)

    payoff_dict = make_payoff_dict(call_or_put='call', direction='long')
    payoff_dict = add_leg_to_dict(payoff_dict, strike=1.0, call_or_put='put', direction='short')

    cfg = build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict)

    configure_curve_gen(cfg)
    curve_df2, pdf_df2, training_df2 = generate_curves(payoff_dict=payoff_dict,
                                                       bet_fractions=np.linspace(0.0, 0.9999, 500))

    pdf_x, pdfs_y = get_pdf_arrays()

    min_prem = 0.001
    max_prem = 0.03
    fig1 = pdf_and_payout_sweep(pdf_x, pdfs_y[0],
                                np.linspace(min_prem, max_prem, 10), 'ETH', legend=False)
    fig2 = kelly_growth_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                              np.linspace(0.0, 0.9999, 50))
    fig3 = kelly_derivative_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                                  np.linspace(0.0, 0.9999, 50))
    fig4 = plot_curve([curve_df2.A.values[0], curve_df2.B.values[0],
                       curve_df2.C.values[0], curve_df2.D.values[0]],
                      curve_df2.bet_fractions.values[0], curve_df2.curve_points.values[0])

    if show_figs:
        show(fig1)
        show(fig2)
        show(fig3)
        show(fig4)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curve_df.bet_fractions.values[0], y=curve_df.curve_points.values[0],
                             mode='lines',
                             name='Underlying Kelly Curve'))
    fig.add_trace(go.Scatter(x=curve_df2.bet_fractions.values[0],
                             y=curve_df2.curve_points.values[0],
                             mode='lines',
                             name='Synthetic Kelly Curve'))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Util (%)',
        yaxis_title='Premium (%)').update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    show(fig)


def test_covered_call_vs_short_put(show_figs=True):
    """
    Testing a covered call vs a short put

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    payoff_dict = make_payoff_dict(call_or_put='call', direction='short')
    payoff_dict['und_price'] = 1.0
    payoff_dict['und_amt'] = 1.0

    cfg = build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict)

    configure_curve_gen(cfg)
    curve_df, pdf_df, training_df = generate_curves(payoff_dict=payoff_dict,
                                                    bet_fractions=np.linspace(0.0, 0.9999, 500))

    pdf_x, pdfs_y = get_pdf_arrays()

    min_prem = 0.001
    max_prem = 0.03
    fig1 = pdf_and_payout_sweep(pdf_x, pdfs_y[0],
                                np.linspace(min_prem, max_prem, 10), 'ETH', legend=False)
    fig2 = kelly_growth_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                              np.linspace(0.0, 0.9999, 50))
    fig3 = kelly_derivative_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                                  np.linspace(0.0, 0.9999, 50))
    fig4 = plot_curve([curve_df.A.values[0], curve_df.B.values[0],
                       curve_df.C.values[0], curve_df.D.values[0]],
                      curve_df.bet_fractions.values[0], curve_df.curve_points.values[0])

    if show_figs:
        show(fig1)
        show(fig2)
        show(fig3)
        show(fig4)

    payoff_dict = make_payoff_dict(call_or_put='put', direction='short')

    cfg = build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict)

    configure_curve_gen(cfg)
    curve_df2, pdf_df2, training_df2 = generate_curves(payoff_dict=payoff_dict,
                                                       bet_fractions=np.linspace(0.0, 0.9999, 500))

    pdf_x, pdfs_y = get_pdf_arrays()

    min_prem = 0.001
    max_prem = 0.03
    fig1 = pdf_and_payout_sweep(pdf_x, pdfs_y[0],
                                np.linspace(min_prem, max_prem, 10), 'ETH', legend=False)
    fig2 = kelly_growth_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                              np.linspace(0.0, 0.9999, 50))
    fig3 = kelly_derivative_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                                  np.linspace(0.0, 0.9999, 50))
    fig4 = plot_curve([curve_df2.A.values[0], curve_df2.B.values[0],
                       curve_df2.C.values[0], curve_df2.D.values[0]],
                      curve_df2.bet_fractions.values[0], curve_df2.curve_points.values[0])

    if show_figs:
        show(fig1)
        show(fig2)
        show(fig3)
        show(fig4)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curve_df.bet_fractions.values[0], y=curve_df.curve_points.values[0],
                             mode='lines',
                             name='Covered Call Kelly Curve'))
    fig.add_trace(go.Scatter(x=curve_df2.bet_fractions.values[0],
                             y=curve_df2.curve_points.values[0],
                             mode='lines',
                             name='Short Put Kelly Curve'))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Util (%)',
        yaxis_title='Premium (%)').update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    show(fig)


def test_gaussian_dist(show_figs=True):
    """
    Testing a gaussian distribution kelly vs the BSM premium

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    payoff_dict = make_payoff_dict(call_or_put='put', direction='short')

    cfg = build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict)

    configure_curve_gen(cfg)
    curve_df, pdf_df, training_df = generate_curves(payoff_dict=payoff_dict,
                                                    bet_fractions=np.linspace(0.0, 0.9999, 500),
                                                    initial_guess=(),
                                                    dist=norm)

    pdf_x, pdfs_y = get_pdf_arrays()

    min_prem = 0.001
    max_prem = 0.03
    fig1 = pdf_and_payout_sweep(pdf_x, pdfs_y[0],
                                np.linspace(min_prem, max_prem, 10), 'ETH', legend=False)
    fig2 = kelly_growth_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                              np.linspace(0.0, 0.9999, 50))
    fig3 = kelly_derivative_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                                  np.linspace(0.0, 0.9999, 50))

    bf = curve_df.bet_fractions.values[0]
    opt = curve_df.curve_points.values[0]
    params = [curve_df.A.values[0], curve_df.B.values[0],
              curve_df.C.values[0], curve_df.D.values[0]]

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=bf, y=opt, mode='lines', name='Gaussian Kelly Curve'))

    range_to_use = np.where((np.asarray(opt) > 1e-10) | (np.asarray(opt) < -1e-10))[0][-1]

    fig4.add_trace(
        go.Scatter(x=bf[:range_to_use+1],
                   y=evaluate_premium_curve(params, bf)[:range_to_use+1],
                   mode='lines', name='COSH Fit Curve'))

    log_returns = calc_log_returns(cfg.train_config.training_df.ethereum.dropna())
    last_year_returns = log_returns[-365:]

    historical_vol = log_returns.std().values[0] * np.sqrt(365.0)
    # historical_vol = last_year_returns.std().values[0] * np.sqrt(365.0)
    # print('HV: ', historical_vol)

    bsm_payoff = {
        'type': 'put',
        'dir': 'short',
        'amt': 1.0,
        'strike': 1.0,
        't': 1.0 / 365.0,
        'sigma': historical_vol,
        'r': 0.0,
        'q': 0.0
    }

    bsm_put, _ = put(1.0, bsm_payoff['strike'], bsm_payoff['t'], bsm_payoff['sigma'],
                     bsm_payoff['r'], bsm_payoff['q'])

    # print('BSM: ', bsm_put)

    fig4.add_trace(
        go.Scatter(x=bf, y=np.full_like(bf, bsm_put), mode='lines', name='BSM Premium'))

    fig4.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Util (%)',
        yaxis_title='Premium (%)').update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    fig4.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    if show_figs:
        show(fig1)
        show(fig2)
        show(fig3)
        show(fig4)


def test_vertical_spread(show_figs=True):
    """
    Testing a vertical spread

    Returns
    -------
    None
    """
    input_file = '../../inputs/ExampleCurveGenInputSingle.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    payoff_dict = make_payoff_dict(call_or_put='put', direction='short')
    payoff_dict = add_leg_to_dict(payoff_dict, 0.95, call_or_put='put', direction='long')

    cfg = build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict)

    configure_curve_gen(cfg)
    curve_df, pdf_df, training_df = generate_curves(payoff_dict=payoff_dict,
                                                    bet_fractions=np.linspace(0.0, 0.999, 50))

    pdf_x, pdfs_y = get_pdf_arrays()

    min_prem = 0.001
    max_prem = 0.03
    fig1 = pdf_and_payout_sweep(pdf_x, pdfs_y[0],
                                np.linspace(min_prem, max_prem, 10), 'ETH', legend=False)
    fig2 = kelly_growth_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                              np.linspace(0.0, 0.9999, 50))
    fig3 = kelly_derivative_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                                  np.linspace(0.0, 0.9999, 50))
    fig4 = plot_curve([curve_df.A.values[0], curve_df.B.values[0],
                       curve_df.C.values[0], curve_df.D.values[0]],
                      curve_df.bet_fractions.values[0], curve_df.curve_points.values[0])

    if show_figs:
        # show(fig1)
        # show(fig2)
        # show(fig3)
        show(fig4)

    payoff_dict = make_payoff_dict(call_or_put='put', direction='short')
    # payoff_dict = add_leg_to_dict(payoff_dict, 0.4, call_or_put='put', direction='long')

    cfg = build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict)

    configure_curve_gen(cfg)
    curve_df2, pdf_df2, training_df2 = generate_curves(payoff_dict=payoff_dict,
                                                    bet_fractions=np.linspace(0.0, 0.999, 50))

    pdf_x, pdfs_y = get_pdf_arrays()

    min_prem = 0.001
    max_prem = 0.03
    fig1 = pdf_and_payout_sweep(pdf_x, pdfs_y[0],
                                np.linspace(min_prem, max_prem, 10), 'ETH', legend=False)
    fig2 = kelly_growth_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                              np.linspace(0.0, 0.9999, 50))
    fig3 = kelly_derivative_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                                  np.linspace(0.0, 0.9999, 50))
    fig4 = plot_curve([curve_df2.A.values[0], curve_df2.B.values[0],
                       curve_df2.C.values[0], curve_df2.D.values[0]],
                      curve_df2.bet_fractions.values[0], curve_df2.curve_points.values[0])

    if show_figs:
        # show(fig1)
        # show(fig2)
        # show(fig3)
        show(fig4)

    payoff_dict = make_payoff_dict(call_or_put='put', direction='long')

    input_file2 = '../../inputs/ExampleCurveGenInputSingle2.csv'
    cfg = build_generator_config(input_file2, price_history_file, payoff_dict=payoff_dict)

    configure_curve_gen(cfg)
    curve_df3, pdf_df3, training_df3 = generate_curves(payoff_dict=payoff_dict,
                                                    bet_fractions=np.linspace(0.0, 0.999, 50))

    pdf_x, pdfs_y = get_pdf_arrays()

    min_prem = -0.01
    max_prem = -0.5
    fig1 = pdf_and_payout_sweep(pdf_x, pdfs_y[0],
                                np.linspace(min_prem, max_prem, 10), 'ETH', legend=False)
    fig2 = kelly_growth_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                              np.linspace(0.0, 0.9999, 50))
    fig3 = kelly_derivative_sweep(pdf_x, pdfs_y[0], np.linspace(min_prem, max_prem, 10),
                                  np.linspace(0.0, 0.9999, 50))
    fig4 = plot_curve([curve_df3.A.values[0], curve_df3.B.values[0],
                       curve_df3.C.values[0], curve_df3.D.values[0]],
                      curve_df3.bet_fractions.values[0], curve_df3.curve_points.values[0])

    if show_figs:
        # show(fig1)
        # show(fig2)
        # show(fig3)
        show(fig4)

    bf = curve_df.bet_fractions.values[0]
    opt_spread = curve_df.curve_points.values[0]
    opt_sh_put = curve_df2.curve_points.values[0]
    opt_lg_put = curve_df3.curve_points.values[0]

    opt_diff = np.asarray(opt_sh_put) + np.asarray(opt_lg_put)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bf, y=opt_spread,
                             mode='lines',
                             name='Bull Put Spread'))

    fig.add_trace(
        go.Scatter(x=bf, y=opt_sh_put,
                   mode='lines', name='Short Put'))
    fig.add_trace(
        go.Scatter(x=bf, y=opt_lg_put,
                   mode='lines', name='Long Put'))
    fig.add_trace(
        go.Scatter(x=bf, y=opt_diff,
                   mode='lines', name='Diff'))

    fig.update_layout(
        plot_bgcolor='rgb(230,230,230)',
        xaxis_title='Util (%)',
        yaxis_title='Premium (%)').update_xaxes(showgrid=True).update_yaxes(showgrid=True)

    fig.update_layout(legend=dict(
        yanchor="bottom",
        y=0.99,
        xanchor="right",
        x=0.01
    ))

    show(fig)


def initialize_put_and_condition_map(exps, bf, curve_df):

    put_map = {}
    condition_map = {}
    for u_i, util in enumerate(bf):

        cols = {exp: {} for exp in exps}
        conds = {exp: {} for exp in exps}
        for c_i, curve in curve_df.iterrows():

            premium = curve['curve_points'][u_i]

            col = cols[curve['Expiration']]
            cond = conds[curve['Expiration']]
            col[curve['StrikePercent']] = premium
            cond[curve['StrikePercent']] = True

        put_df = pd.DataFrame.from_dict(cols)
        cond_df = pd.DataFrame.from_dict(conds)

        put_map[util] = put_df
        condition_map[util] = cond_df

        # print('u_i: ', u_i, ' util: ', util)
        # print(put_df)
        # print(cond_df)

    return put_map, condition_map


def check_conditions(put_map, condition_map, bf, strikes: np.ndarray, s, r, q):
    print('Checking conditions')

    strikes_series = pd.Series(strikes)[::-1]
    last_strikes = strikes_series.shift(1)
    next_last_strikes = strikes_series.shift(2)

    for u_i, util in enumerate(bf):

        expirations = put_map[util]
        next_expirations = pd.Series(expirations.columns).shift(1)

        for expiration, next_expiration, cond_col in zip(
                expirations, next_expirations, condition_map[util]):
            # print('exp: ', expiration, ' nexp: ', next_expiration)

            tau = expiration / 365.0

            prices_per_strike = pd.Series(expirations[expiration])[::-1]
            last_price_per_strike = prices_per_strike.shift(1)
            next_last_price_per_strike = prices_per_strike.shift(2)

            if not np.isnan(next_expiration):
                next_exp_prices_per_strike = pd.Series(expirations[next_expiration])[::-1]
            else:
                next_exp_prices_per_strike = strikes_series.to_numpy() * np.exp(-r * tau)

            for s_i, (strike, last_strike, next_last_strike, price, next_exp_price, last_price,
                      next_last_price) in enumerate(
                    zip(strikes_series, last_strikes, next_last_strikes, prices_per_strike,
                        next_exp_prices_per_strike, last_price_per_strike,
                        next_last_price_per_strike)):
                # print(strike, last_strike, next_last_strike, price, last_price, next_last_price)

                all_conditions_hold = True

                if not np.isnan(last_price) and not np.isnan(last_strike):

                    lb_dict = {
                        'p_i': price,
                        'p_ii': last_price
                    }

                    ub_dict = {
                        'p_i': price,
                        'p_ii': last_price,
                        'k_i': strike,
                        'k_ii': last_strike,
                        'r': r,
                        'tau': tau
                    }

                    all_conditions_hold = all_conditions_hold & monotonic_lb_cond(lb_dict)
                    all_conditions_hold = all_conditions_hold & monotonic_ub_cond(ub_dict)

                if not np.isnan(last_price) and not np.isnan(last_strike) and not np.isnan(
                        next_last_price) and not np.isnan(next_last_strike):

                    conv_dict = {
                        'p_i': price,
                        'p_ii': last_price,
                        'p_iii': next_last_price,
                        'k_i': strike,
                        'k_ii': last_strike,
                        'k_iii': next_last_strike
                    }

                    all_conditions_hold = all_conditions_hold & convex_lb_cond(conv_dict)

                zero_dict = {
                    'p_i': price
                }

                call_zero_dict = {
                    'p_i': price,
                    'k_i': strike,
                    's': s,
                    'r': r,
                    'q': q,
                    'tau': tau
                }

                all_conditions_hold = all_conditions_hold & zero_bound_cond(zero_dict)
                all_conditions_hold = all_conditions_hold & call_zero_bound_by_pcp_cond(
                    call_zero_dict)

                if not np.isnan(next_expiration):

                    exp_tau = (next_expiration - expiration) / 365.0

                    cal_dict = {
                        'p_i': price,
                        'p_mm': next_exp_price,
                        'k_i': strike,
                        's': s,
                        'r': r,
                        'q': q,
                        'tau': tau,
                        'exp_tau': exp_tau
                    }

                    all_conditions_hold = all_conditions_hold & calendar_ub_cond(cal_dict)

                # print(all_conditions_hold)
                condition_map[util][cond_col][strike] = all_conditions_hold

    return put_map, condition_map


def plot_condition_results(put_map, condition_map, bf, strikes, label=''):

    for u_i, util in enumerate(bf):
        fig = go.Figure()

        for column, cond_col in zip(put_map[util], condition_map[util]):

            fig.add_trace(go.Scatter(x=strikes, y=put_map[util][column],
                                     mode='lines',
                                     name='Expiration: {}'.format(column)))

            for s_i, strike in enumerate(strikes):

                if condition_map[util][cond_col][strike]:
                    color = 'Green'
                else:
                    color = 'Red'

                fig.add_trace(go.Scatter(x=[strike], y=[put_map[util][column][strike]],
                                         mode='markers',
                                         marker=dict(
                                             color=color,
                                             size=10,
                                             line=dict(
                                                 color='Black',
                                                 width=2
                                             )
                                         ),
                                         showlegend=False))

        fig.update_layout(
            plot_bgcolor='rgb(230,230,230)',
            xaxis_title='Strike (%)',
            yaxis_title='Premium (%)',
            title_text='Util {}'.format(util)
        ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

        fig.update_layout(legend=dict(
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01
        ))

        # show(fig)
        if not os.path.exists('./images'):
            os.mkdir('./images')
        fig.write_image('images/{}_util{}.png'.format(label, util))


def test_no_arb_conditions():

    input_file = '../../inputs/NoArbTest.csv'
    price_history_file = '../../resources/webapp-coins.csv'

    r = 0.0
    q = 0.0

    payoff_dict = make_payoff_dict(call_or_put='put', direction='short', r=r, q=q)

    lbs = [
        monotonic_lb, convex_lb, zero_bound, call_zero_bound_by_pcp
    ]
    ubs = [
        monotonic_ub, calendar_ub
    ]

    cfg = build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict,
                                 lower_bounds_fcns=lbs, upper_bounds_fcns=ubs)
    # cfg = build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict)

    bf = np.linspace(0.0, 0.999, 50)
    configure_curve_gen(cfg)
    curve_df_no_arb, pdf_df_no_arb, training_df_no_arb = generate_curves(payoff_dict=payoff_dict,
                                                                         bet_fractions=bf)

    eth_full_curves_no_arb = curve_df_no_arb.loc[((curve_df_no_arb['Ticker'] == 'ethereum') &
                                    (curve_df_no_arb['Label'] == 'full'))]

    # print('efc: ', eth_full_curves)

    exps = eth_full_curves_no_arb['Expiration'].unique()
    print('Exps: ', exps)

    strikes = eth_full_curves_no_arb['StrikePercent'].unique()
    print('Strikes: ', strikes)

    put_map, condition_map = initialize_put_and_condition_map(exps, bf, eth_full_curves_no_arb)

    # Check no-arb conditions
    put_map, condition_map = check_conditions(put_map, condition_map, bf, strikes, 1.0, r, q)
    plot_condition_results(put_map, condition_map, bf, strikes, label='no-arbitrage-puts')

    cfg = build_generator_config(input_file, price_history_file, payoff_dict=payoff_dict)

    configure_curve_gen(cfg)
    curve_df_kelly, pdf_df_kelly, training_df_kelly = generate_curves(payoff_dict=payoff_dict,
                                                                      bet_fractions=bf)

    eth_full_curves_kelly = curve_df_kelly.loc[((curve_df_kelly['Ticker'] == 'ethereum') &
                                                (curve_df_kelly['Label'] == 'full'))]

    exps = eth_full_curves_kelly['Expiration'].unique()
    print('Exps: ', exps)

    strikes = eth_full_curves_kelly['StrikePercent'].unique()
    print('Strikes: ', strikes)

    put_map, condition_map = initialize_put_and_condition_map(exps, bf, eth_full_curves_kelly)
    put_map, condition_map = check_conditions(put_map, condition_map, bf, strikes, 1.0, r, q)
    plot_condition_results(put_map, condition_map, bf, strikes, label='kelly-puts')

    for (i, curve_no_arb), (_, curve_kelly) in zip(
            curve_df_no_arb.iterrows(), curve_df_kelly.iterrows()):

        bf = curve_no_arb.bet_fractions
        no_arb_curve_pts = curve_no_arb.curve_points
        kelly_curve_pts = curve_kelly.curve_points

        print('i: ', i)
        print(curve_no_arb)
        print(curve_kelly)

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=bf, y=no_arb_curve_pts,
                                 mode='lines',
                                 name='No-Arb Curve'))
        fig.add_trace(go.Scatter(x=bf, y=kelly_curve_pts,
                                 mode='lines',
                                 name='Kelly Curve'))

        fig.update_layout(
            plot_bgcolor='rgb(230,230,230)',
            xaxis_title='Util (%)',
            yaxis_title='Premium (%)',
            title_text='Kelly Curve vs. No-Arb'
        ).update_xaxes(showgrid=True).update_yaxes(showgrid=True)

        fig.update_layout(legend=dict(
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01
        ))

        ticker = curve_no_arb.Ticker
        label = curve_no_arb.Label
        exp = curve_no_arb.Expiration
        strike = curve_no_arb.StrikePercent

        fig.write_image('images/curve_{}_{}_{}_{}.png'.format(ticker, label, exp, strike))


if __name__ == '__main__':
    # test_put_call()
    # test_covered_call_vs_short_put()
    # test_gaussian_dist()
    # test_vertical_spread()
    test_no_arb_conditions()

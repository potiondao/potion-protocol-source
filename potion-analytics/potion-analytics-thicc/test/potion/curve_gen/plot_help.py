
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from potion.curve_gen.training.fit.tail_fit import perform_linear_replication


def exponential_line(x, a, b):
    return np.power(10, a) * np.power(x, b)


def histogram_plot(samples: np.ndarray,  plot_title: str, x_label: str, y_label: str,
                   num_bins: int, x_min, x_max):

    fig = plt.figure()
    ax = fig.gca()

    bin_counts, bin_edges, patches = ax.hist(samples, num_bins, density=True)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(plot_title)
    ax.grid(True)
    ax.set_xlim(x_min, x_max)

    return fig, ax, bin_counts, bin_edges


def loglog_plot(x: np.ndarray, y: np.ndarray, plot_title: str, x_label: str,
                y_label: str, style_str: str):

    fig = plt.figure()
    ax = fig.gca()

    ax.loglog(x, y, style_str)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(plot_title)
    ax.grid(True)

    return fig, ax


def plot_tail_fits(symbol, dist_params, fit_dict):

    left_m = dist_params[-2]
    right_m = dist_params[-1]

    log_rank = fit_dict['log_rank']
    left_deltas = fit_dict['left_log_delta']
    right_deltas = fit_dict['right_log_delta']
    left_b = fit_dict['left_b']
    right_b = fit_dict['right_b']

    left_rep = perform_linear_replication(
        log_rank, left_b, left_m)
    right_rep = perform_linear_replication(
        log_rank, right_b, right_m)

    fig = plt.figure()
    ax = fig.gca()
    ax.plot(left_deltas, log_rank, 'b')
    ax.plot(right_deltas, log_rank, 'g')
    ax.plot(left_rep, log_rank, 'b--')
    ax.plot(right_rep, log_rank, 'g--')
    ax.set_xlabel('ln(|return - origin|)')
    ax.set_ylabel('ln(rank)')
    r_sign = '+'
    l_sign = '-'
    if right_b < 0:
        r_sign = '-'
    if left_b < 0:
        l_sign = '-'
    legend_list = ['Left Tail Samples',
                   'Right Tail Samples',
                   'Left Tail y = {:6.4f}x {} {:6.4f}'.format(left_m, l_sign, np.abs(left_b)),
                   'Right Tail y = {:6.4f}x {} {:6.4f}'.format(right_m, r_sign, np.abs(right_b))]
    ax.legend(legend_list)
    ax.set_title('{} Right and Left Tail Hill Estimator'.format(symbol))
    ax.grid(True)

    return fig, ax


def plot_profit_and_loss(x, payout: np.ndarray):

    fig = plt.figure()
    ax = fig.gca()

    # Wrap the array in a df so we can manipulate easily
    payout_df = pd.DataFrame(payout, index=x, columns=['Payout'])

    # Test multiple profit and loss regions
    # payout_df.iloc[150:170] = payout_df.iloc[150:170] * -1

    # Detect where the payout function crosses zero and build dataframes for regions to plot
    change_points = []
    sign = None
    index = 0
    for val in payout:

        if sign is None:
            sign = np.sign(val)

        if val < 0:
            if sign > 0:
                change_points.append({
                    'i': index,
                    's': -1
                })
                sign = -1
        else:
            if sign < 0:
                change_points.append({
                    'i': index,
                    's': 1
                })
                sign = 1

        index += 1

    # print(change_points)

    fill_dfs = []
    start_index = 0
    for point in change_points:
        i = point['i']
        s = point['s']

        fill_df = payout_df.iloc[start_index:i, 0]
        fill_dfs.append({
            'd': fill_df,
            's': s
        })

        start_index = i

    # fill to the end of the x axis
    fill_df = payout_df.iloc[start_index:, 0]
    fill_dfs.append({
        'd': fill_df,
        's': -np.sign(payout_df.iloc[-1, 0])
    })

    ax.plot(x, payout)
    ax.grid(True)

    # Fill the area under the payout function as a profit or loss region
    for fill_df in fill_dfs:
        df = fill_df['d']
        s = fill_df['s']

        values = df.iloc[:].tolist()

        # Opposite sign you would expect because the zero crossing is
        # looking at the region of the plot before
        if s > 0:
            ax.fill_between(df.index, values, 0.0, alpha=0.3, color='red')
        else:
            ax.fill_between(df.index, values, 0.0, alpha=0.3, color='green')

    ax.set_ylabel('Profit and Loss')
    ax.set_xlabel('Strike')

    return fig, ax


def plot_pdf_payout_graphs(gen, include_odds=True, fig_size=None):

    if fig_size is None:
        fig, axs = plt.subplots(
            len(gen.optimal_premium_map.index), len(gen.columns), constrained_layout=True)
    else:
        fig, axs = plt.subplots(
            len(gen.optimal_premium_map.index), len(gen.columns), constrained_layout=True,
            figsize=fig_size)

    # Loop over the expirations
    for column_idx in range(len(gen.columns)):

        column = gen.columns[column_idx]
        # print('exp: {}'.format(column))

        if gen.log_domain_calc:
            pdf = gen.log_pdf_list[column_idx]
        else:
            pdf = gen.price_pdf_list[column_idx]

        if include_odds:
            odds_col = gen.odds_map[column]
        else:
            odds_col = []

        row_count = 0
        # Loop over the strikes
        for strike_pct in gen.optimal_premium_map.index:

            try:
                if len(gen.columns) == 1:
                    ax = axs[row_count]
                elif len(gen.optimal_premium_map.index) == 1:
                    ax = axs[column_idx]
                else:
                    ax = axs[row_count, column_idx]
            except TypeError:
                ax = axs

            if include_odds:
                odds_list = odds_col[strike_pct]
                for odd in odds_list:
                    if gen.log_domain_calc:
                        ax.plot(gen.log_x, odd)
                    else:
                        ax.plot(gen.x, odd)
            if gen.log_domain_calc:
                ax.plot(gen.log_x, pdf, 'k')
                ax.set_xlim([-1.0, 1.0])
            else:
                ax.plot(gen.x, pdf, 'k')
                ax.set_xlim([0, 2])

            # legend_list = ['PDF', 'Payoff']
            # ax1.legend(legend_list)
            ax.set_xlabel('Strike Outcome')
            ax.set_ylabel('Probability Density and Payout Odds')
            ax.set_title('Day {} Strike Pct {}'.format(column, int(strike_pct)))
            ax.grid(True)

            row_count = row_count + 1

    # mng = plt.get_current_fig_manager()
    # mng.window.state('zoomed')
    return fig, axs


def plot_kelly_curves(gen, fig_size=None):

    if fig_size is None:
        fig, axs = plt.subplots(len(gen.optimal_premium_map.index), len(gen.columns),
                                constrained_layout=True)
    else:
        fig, axs = plt.subplots(len(gen.optimal_premium_map.index), len(gen.columns),
                                constrained_layout=True, figsize=fig_size)

    # Loop over the expirations
    for column_idx in range(len(gen.columns)):

        column = gen.columns[column_idx]

        kelly_col = gen.kelly_map[column]
        bet_col = gen.bet_fraction_map[column]

        row_count = 0
        # Loop over the strikes
        for strike_pct in gen.kelly_map.index:

            try:
                if len(gen.columns) == 1:
                    ax = axs[row_count]
                elif len(gen.kelly_map.index) == 1:
                    ax = axs[column_idx]
                else:
                    ax = axs[row_count, column_idx]
            except TypeError:
                ax = axs

            fractions = bet_col[strike_pct]
            curve_list = kelly_col[strike_pct]

            for curve in curve_list:
                # logging.debug(curve)
                ax.plot(fractions, curve)
            # legend_list = ['Log Expected Growth Rate']
            # ax.legend(legend_list)
            ax.set_xlabel('Betting Fraction (0-100%)')
            ax.set_ylabel('k(f)')
            ax.set_title('Day {} Strike Pct {}'.format(column, int(strike_pct)))
            ax.grid(True)

            row_count = row_count + 1

    # mng = plt.get_current_fig_manager()
    # mng.window.state('zoomed')
    return fig, axs


def plot_jacobian_curves(gen):

    fig, axs = plt.subplots(len(gen.optimal_premium_map.index), len(gen.columns),
                            constrained_layout=True)

    # Loop over the expirations
    for column_idx in range(len(gen.columns)):

        column = gen.columns[column_idx]

        jac_col = gen.jacobian_map[column]
        bet_col = gen.bet_fraction_map[column]

        row_count = 0
        # Loop over the strikes
        for strike_pct in gen.jacobian_map.index:

            try:
                if len(gen.columns) == 1:
                    ax = axs[row_count]
                elif len(gen.jacobian_map.index) == 1:
                    ax = axs[column_idx]
                else:
                    ax = axs[row_count, column_idx]
            except TypeError:
                ax = axs

            fractions = bet_col[strike_pct]
            jac_list = jac_col[strike_pct]

            for curve in jac_list:
                ax.plot(fractions, curve)
            # legend_list = ['Log Expected Growth Rate']
            # ax.legend(legend_list)
            ax.set_xlabel('Betting Fraction (0-100%)')
            ax.set_ylabel('dk/df')
            ax.set_title('Day {} Strike Pct {}'.format(column, int(strike_pct)))
            ax.grid(True)

            row_count = row_count + 1

    # mng = plt.get_current_fig_manager()
    # mng.window.state('zoomed')
    return fig, axs


def plot_optimal_premiums(gen):

    fig, axs = plt.subplots(len(gen.optimal_premium_map.index), len(gen.columns),
                            constrained_layout=True)

    # Loop over the expirations
    for column_idx in range(len(gen.columns)):
        # print('col idx: {}'.format(column_idx))
        column = gen.columns[column_idx]
        # print(column)
        # print(gen.optimal_premium_map)
        opt_col = gen.optimal_premium_map[column]
        bet_col = gen.bet_fraction_map[column]
        fit_col = None
        if gen.opt_premium_fit_map is not None:
            fit_col = gen.opt_premium_fit_map[column]

        row_count = 0
        # Loop over the strikes
        for strike_pct in gen.optimal_premium_map.index:

            try:
                if len(gen.columns) == 1:
                    ax = axs[row_count]
                elif len(gen.optimal_premium_map.index) == 1:
                    ax = axs[column_idx]
                else:
                    ax = axs[row_count, column_idx]
            except TypeError:
                ax = axs

            fractions = bet_col[strike_pct]
            opt_premiums = opt_col[strike_pct]
            if gen.opt_premium_fit_map is not None:
                fit_params = fit_col[strike_pct]

                # logging.debug('Calc w/ params: {}'.format(fit_params))

                if gen.fit_type == 'EXP':
                    fit_y = fit_params[0] * np.exp(fit_params[1] * fractions) + fit_params[2]
                elif gen.fit_type == 'POLY':
                    fit_y = fit_params[0] * fractions ** 3 + fit_params[1] * fractions ** 2 + \
                            fit_params[2] * fractions + fit_params[3]
                elif gen.fit_type == 'COSH':
                    fit_y = fit_params[0] * fractions * np.cosh(fit_params[1] * (
                            fractions ** fit_params[2])) + fit_params[3]
                else:
                    raise ValueError('Unknown Fit Type: {}'.format(gen.fit_type))

                ax.plot(fractions, fit_y, color='r')
            # print(fractions)
            # print(opt_premiums)
            ax.plot(fractions, opt_premiums)
            ax.set_xlabel('Betting Fraction (0-100%)')
            ax.set_ylabel('Optimal Premium')
            ax.set_title('Day {} Strike Pct {}'.format(column, strike_pct))
            ax.grid(True)

            row_count = row_count + 1

    # mng = plt.get_current_fig_manager()
    # mng.window.showMaximized()
    # mng.frame.Maximize(True)
    # mng.window.state('zoomed')
    # plt.tight_layout()
    return fig, axs


def plot_full_premiums(gen):

    fig, axs = plt.subplots(len(gen.full_premium_map.index), len(gen.columns),
                            constrained_layout=True)

    # Loop over the expirations
    for column_idx in range(len(gen.columns)):

        column = gen.columns[column_idx]

        full_col = gen.full_premium_map[column]
        bet_col = gen.bet_fraction_map[column]
        fit_col = None
        if gen.full_premium_fit_map is not None:
            fit_col = gen.full_premium_fit_map[column]

        row_count = 0
        # Loop over the strikes
        for strike in gen.full_premium_map.index:

            try:
                if len(gen.columns) == 1:
                    ax = axs[row_count]
                elif len(gen.full_premium_map.index) == 1:
                    ax = axs[column_idx]
                else:
                    ax = axs[row_count, column_idx]
            except TypeError:
                ax = axs

            fractions = bet_col[strike]
            full_premiums = full_col[strike]
            if gen.full_premium_fit_map is not None:
                fit_params = fit_col[strike]

                # logging.debug('Calc w/ params: {}'.format(fit_params))

                if gen.fit_type == 'EXP':
                    fit_y = fit_params[0] * np.exp(fit_params[1] * fractions) + fit_params[2]
                elif gen.fit_type == 'POLY':
                    fit_y = fit_params[0] * fractions ** 3 + fit_params[1] * fractions ** 2 + \
                            fit_params[2] * fractions + fit_params[3]
                elif gen.fit_type == 'COSH':
                    fit_y = fit_params[0] * fractions * np.cosh(fit_params[1] * (
                            fractions ** fit_params[2])) + fit_params[3]
                else:
                    raise ValueError('Unknown Fit Type: {}'.format(gen.fit_type))

                ax.plot(fractions, fit_y, color='r')
            ax.plot(fractions, full_premiums)
            ax.set_xlabel('Betting Fraction (0-100%)')
            ax.set_ylabel('Optimal Premium')
            ax.set_title('Day {} Strike {}'.format(column, int(strike)))
            ax.grid(True)

            row_count = row_count + 1

    # mng = plt.get_current_fig_manager()
    # mng.window.showMaximized()
    # mng.frame.Maximize(True)
    # mng.window.state('zoomed')
    # plt.tight_layout()
    return fig, axs

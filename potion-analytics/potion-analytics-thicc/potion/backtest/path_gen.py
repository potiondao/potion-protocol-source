"""
This module provides functions which are used to generate backtesting paths. There are functions
which generate paths for single asset simulations as well as multi asset simulations. In addition,
for the multi asset simulations there are functions which find a covariance matrix from a set of
price histories.

For both single and multi asset paths, there are functions which generate according to different
probability distributions.
"""
import numpy as np
import pandas as pd
import scipy.interpolate as interpolate
from scipy.stats import norm
from scipy.linalg import cholesky
from potion.curve_gen.training.fit.helpers import calc_simple_returns, calc_log_returns
from potion.curve_gen.training.fit.tail_fit import fit_samples
from potion.curve_gen.training.distributions.skewed_students_t import SkewedT
from potion.curve_gen.domain_transformation import log_to_price_sample_points
from potion.curve_gen.training.distributions.multivariate_students_t import (
    mle_multi_var_t, MultiVarStudentT)


def prices_to_t_covariance_matrix(price_history_dict, log=True):
    """
    Takes a list of price histories and assets and uses MLE to fit a multi variable student t
    distribution to the returns, and calculates the covariance matrix which will be used to
    generate paths in multi variable backtesting simulations

    Parameters
    -----------
    price_history_dict : dict[List[float]]
        The dict mapping price history for each asset
    log : bool
        Boolean flag indicating whether to use log returns (default True)

    Returns
    -----------
    cov_matrix : DataFrame
        The covariance matrix estimated from the price histories
    asset_params : List[dict]
        Contains one dict for each asset, storing the asset name, marginal location, and
        marginal scale
    tail : float
        Estimate of the tail parameter nu
    """
    return_dfs = []

    # for index, price_hist in enumerate(price_history_list):
    for i, (asset, history) in enumerate(price_history_dict.items()):

        if log:
            return_df = calc_log_returns(pd.DataFrame(history))
        else:
            return_df = calc_simple_returns(pd.DataFrame(history))

        # Rename so we have named labels in the covariance matrix
        return_df = return_df.rename(columns={'Return': asset})
        return_dfs.append(return_df[asset])

    # Calculate the covariance matrix from all of the return histories
    all_ret_data = pd.concat(return_dfs, axis=1)
    all_ret_data.dropna(inplace=True)

    samples = []
    for (column_name, column_data) in all_ret_data.iteritems():
        samples.extend(column_data.values)

    dist_params, _ = fit_samples(
        pd.DataFrame(samples, columns=['Return']), 1.0, 2.5,
        left_threshold=0.1, right_threshold=0.1)

    nu = dist_params[-3]
    left_m = dist_params[-2]
    right_m = dist_params[-1]

    # print('nu: {} left: {} right: {}'.format(nu, left_m, right_m))
    tail = np.median(np.asarray([nu, left_m, right_m]))
    # tail = np.max(np.asarray([nu, left_m, right_m]))

    # print(tail)

    estimates = mle_multi_var_t(all_ret_data, tail)

    mu_est = estimates[0]
    cov_est = estimates[1]

    asset_params, columns = list(map(list,
                                     zip(*[[{
                                         'key': asset,
                                         'loc': mu_est[i],
                                         'scale': cov_est[i, i],
                                     }, asset]
                                         for i, asset in enumerate(price_history_dict)])))

    return pd.DataFrame(cov_est, columns=columns, index=columns), asset_params, tail


def prices_to_sample_covariance_matrix(price_history_dict, log=True):
    """
    Calculates sample covariance from a history of price data for multiple assets and uses that
    as input to a multi variable normal distribution for generating basic but unrealistic paths
    in backtesting simulations

    Parameters
    -----------
    price_history_dict : dict[List[float]]
        The dict mapping price history for each asset
    log : bool
        Boolean flag indicating whether to use log returns (default True)

    Returns
    -----------
    cov_matrix : DataFrame
        The covariance matrix estimated from the price histories
    asset_params : List[dict]
        Contains one dict for each asset, storing the asset name, marginal location, and
        marginal scale
    """
    return_dfs = []
    asset_params = []
    for i, (asset, history) in enumerate(price_history_dict.items()):

        # print('history: {}'.format(history))
        if log:
            return_df = calc_log_returns(pd.DataFrame(history))
        else:
            return_df = calc_simple_returns(pd.DataFrame(history))

        # Rename so we have named labels in the covariance matrix
        return_df = return_df.rename(columns={'Return': asset})
        return_dfs.append(return_df[asset])

        loc, scale = norm.fit(return_df.to_numpy())
        asset_params.append({
            'key': asset,
            'loc': loc,
            'scale': scale,
            # 'N': N
        })

    # Calculate the covariance matrix from all of the return histories
    all_ret_data = pd.concat(return_dfs, axis=1)
    covariance_matrix = all_ret_data.cov(ddof=1)

    return covariance_matrix, asset_params


def t_path_sampling(t_fit_params, n_paths=1, path_length=2, current_price=1.0):
    """
    This function generates a set of backtesting paths according to a student's t distribution

    Parameters
    ----------
    t_fit_params : List[float]
        A List containing the 4 distribution parameters: location, scale, skew, nu
    n_paths : int
        The number of paths to generate
    path_length : int
        The length of each path
    current_price : float
        The price at which the paths should start

    Returns
    -------
    path_set : List[List[float]]
        The nested List of paths n_paths by path_length
    """
    skewed_t = SkewedT()
    location = t_fit_params[0]
    scale = t_fit_params[1]
    skew = t_fit_params[2]
    nu = t_fit_params[3]

    # because current_price at start of path
    path_length -= 1

    path_list = []
    for i in range(n_paths):
        # print('l: {} s: {} sk: {} nu: {} pl: {}'.format(location, scale, skew, nu, path_length))
        log_deltas = skewed_t.rvs(skew, nu, loc=location, scale=scale, size=path_length)

        path = [current_price]
        last_price = current_price
        for log_delta in log_deltas:
            price = log_to_price_sample_points(log_delta, last_price)
            path.append(price)
            last_price = price

        path_list.append(path)

    return path_list


def multivariate_normal_path_sampling(n_paths, path_length, covariance_matrix, current_prices=None):
    """
    Generates sample paths for backtesting according to a multi variable normal distribution.

    Parameters
    ----------
    n_paths : int
        The number of paths to generate
    path_length : int
        The length of each path
    covariance_matrix : DataFrame
        The covariance matrix of the log return distribution estimated from the price histories
    current_prices : dict
        A dict mapping each asset to the price at which the paths should start

    Returns
    ----------
    path_dict : dict
        A dict containing each path value for each asset
    log_delta_list : List
        List containing log returns for each path
    """
    cov_size = len(covariance_matrix.columns)
    assets = covariance_matrix.columns

    if current_prices is None:
        current_prices = {}
        for asset in assets:
            current_prices[asset] = 1.0

    if len(current_prices.items()) != cov_size:
        raise ValueError('Current price dict must match number of assets')

    cho_decomp = cholesky(covariance_matrix)

    # Initialize the empty lists of paths for each asset
    path_dict = {}
    for asset_index, asset in enumerate(assets):
        path_dict[asset] = []

    log_delta_list = []
    for i in range(n_paths):

        # Generate uncorrelated random samples
        uncorrelated_sample_list = []
        for asset in assets:
            uncorrelated_samples = norm.rvs(loc=0.0, scale=1.0, size=path_length - 1)
            uncorrelated_sample_list.append(uncorrelated_samples)

        # Convert them to correlated random samples which are log deltas for each asset
        correlated_sample_list = np.dot(cho_decomp, uncorrelated_sample_list)
        log_delta_list.append(correlated_sample_list)

        for asset_index, asset in enumerate(assets):

            current_price = current_prices[asset]

            path = [current_price]
            last_price = current_price
            for log_delta in correlated_sample_list[asset_index]:
                price = log_to_price_sample_points(log_delta, last_price)
                path.append(price)
                last_price = price

            # Store the path for this asset in the dict like 'BTC': [1,2,3...]
            path_dict[asset].append(path)

    return path_dict, log_delta_list


def multivariate_t_path_sampling(n_paths, path_length, covariance_matrix, nu, current_prices=None):
    """
    Generates sample paths for backtesting according to a multi variable student t distribution.

    Parameters
    ----------
    n_paths : int
        The number of paths to generate
    path_length : int
        The length of each path
    covariance_matrix : DataFrame
        The covariance matrix of the log return distribution estimated from the price histories
    nu : float
        The degrees of freedom parameter which controls the tails of the distribution
    current_prices : dict
        A dict mapping each asset to the price at which the paths should start

    Returns
    ----------
    path_dict : dict
        A dict containing each path value for each asset
    log_delta_list : List
        List containing log returns for each path
    """
    cov_size = len(covariance_matrix.columns)
    assets = covariance_matrix.columns

    if current_prices is None:
        current_prices = {}
        for asset in assets:
            current_prices[asset] = 1.0

    if len(current_prices.items()) != cov_size:
        raise ValueError('Current price dict must match number of assets')

    # Initialize the empty lists of paths for each asset
    path_dict = {}
    for asset_index, asset in enumerate(assets):
        path_dict[asset] = []

    multi_var_t = MultiVarStudentT([0.0] * cov_size, covariance_matrix, nu)
    log_delta_list = []
    for i in range(n_paths):

        log_deltas = multi_var_t.rvs(path_length - 1)
        log_delta_list.append(log_deltas)
        # print(log_deltas)

        for asset in covariance_matrix.columns:
            asset_log_deltas = log_deltas[asset]

            asset_path = [current_prices[asset]]
            last_price = asset_path[0]
            for log_delta in asset_log_deltas:
                price = log_to_price_sample_points(log_delta, last_price)
                asset_path.append(price)
                last_price = price

            # Store the path for this asset in the dict like 'BTC': [1,2,3...]
            path_dict[asset].append(asset_path)

    return path_dict, log_delta_list


def path_sampling(prices, n_paths=1, path_length=2, n_hist_bins='auto', current_price=1.0):
    """
    Generates price paths from a histogram

    Parameters
    ----------
    prices : List[float]
        The history of past prices
    n_paths : int
        The number of paths to generate
    path_length : int
        The length of each path
    n_hist_bins : int
        The number of bins to use in the histogram
    current_price : float
        The price at which the paths should start

    Returns
    -------
    path_list : List[List[float]]
        The nested List of generated paths n_paths by path_length
    """
    returns = prices.div(prices.shift(1)).to_numpy()[1:] - 1

    # because current_price at start of path
    path_length -= 1

    # use inverse transform sampling to sample from empirical CDF
    hist, bin_edges = np.histogram(returns, bins=n_hist_bins, density=True)
    cum_values = np.zeros(bin_edges.shape)
    # we could use more sophisticated methods to integrate hist into CDF
    cum_values[1:] = np.cumsum(hist * np.diff(bin_edges))
    inv_cdf = interpolate.interp1d(cum_values, bin_edges)

    path_list = []
    for i in range(n_paths):
        # interpret deltas as percent returns, cumulate and apply them to produce path
        r = np.random.rand(path_length)
        deltas = inv_cdf(r)
        cum_deltas = np.cumprod(1 + deltas)
        path = np.insert(current_price * cum_deltas, 0, current_price)
        path_list.append(path)

    return path_list

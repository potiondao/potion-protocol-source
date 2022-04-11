"""
This module provides a class for splitting backtesting results into different category
groups so the user can have automatic creation of portfolios. These groups then have a
clustering algorithm run to group similar curves with the same pool
"""
import numpy as np
import pandas as pd
from scipy.stats import rankdata

from potion.streamlitapp.category.curve_cluster import CurveCluster
from potion.curve_gen.kelly import evaluate_premium_curve


class Categorizer:
    """
    Class for splitting backtesting results into different category groups so the user
    can have automatic creation of pools. These groups then have a clustering algorithm
    run to group similar curves with the same pool
    """

    def __init__(self, performance_df=None, curves_df=None):
        """
        Constructs the class and stores the dataframes used in calculations.

        Parameters
        -----------
        performance_df : pandas.DataFrame
            The dataframe containing the performance statistics
        curves_df : pandas.DataFrame
            The dataframe containing the curve info

        Raises
        -----------
        ValueError
            If the configuration DataFrames are missing
        """
        self.performance_df = performance_df
        self.curves_df = curves_df

        if self.performance_df is None:
            raise ValueError('Must specify performance DF to run categorization algorithm')

        if self.curves_df is None:
            raise ValueError('Must specify curves DF to run categorization algorithm')

    def create_historical_score_mapping(self, num_groups):
        """
        This function gets the CAGR and Drawdown results for backtesting and scores
        their performance

        Parameters
        -----------
        num_groups: int
            The number of performance groups the user wants to split results into

        Returns
        -----------
        performance_group_mapping : dict
            dict mapping curve id to ranking
        scores : List[float]
            A List of historical scores
        """
        # Get the columns we care about for calculating our score
        cagrs = self.performance_df.p50_user_cagr.values
        dds = self.performance_df.p50_user_maxDD.values

        # Set a threshold for max DD so we don't divide by 0
        div_0_threshold = 1e-20

        # Replace the zero elements
        dds[dds > -div_0_threshold] = -div_0_threshold

        # Rank the CAGRs and Max DD so that the values we are scoring are
        # relative no matter how good or bad in absolute terms. Also, the rank ensures
        # the values are always positive
        cagr_ranks = rankdata(cagrs)
        dd_ranks = rankdata(dds)

        # Calculate a score which increases when CAGR increases and increases when Max DD decreases
        scores = cagr_ranks / (1.0 / dd_ranks)

        # Split the groups by score percentile
        percent_per_group = 1.0 / num_groups

        # Calculate the score percentile boundaries
        pct_boundaries = [(i + 1) * percent_per_group for i in range(num_groups - 1)]

        # Sort the score so we can partition into groups by backtesting performance percentile
        score_series = pd.Series(scores, index=range(len(scores)))
        score_series.sort_values(inplace=True)

        # Calculate the percentile index boundaries and split the array into groups
        percentiles = [int(len(scores) * pct) for pct in pct_boundaries]
        performance_groups = np.split(score_series.index.to_numpy(), percentiles)

        # Maps the curve IDs to each performance group
        performance_group_mapping = {
            curve_id: group_num for group_num, group in enumerate(performance_groups)
            for curve_id in group}

        # print('performance map: {}'.format(performance_group_mapping))

        return performance_group_mapping, scores

    def cluster_based_on_category(self, num_groups, num_clusters, performance_group_mapping):
        """
        This function takes the groups of backtesting results for each curve and
        calculates the curves for each id. Once the curves are calculated they can be
        clustered by similarity within the performance group to produce a pool.

        Parameters
        -----------
        num_groups : int
            The number of performance groups the user wants to split results into
        num_clusters : int
            The number of clusters within each performance group
        performance_group_mapping : dict
            The dict backtest_id -> group_id, where highest group_id is best performing

        Returns
        -----------
        category_map : dict
            The dict objects containing the cluster counts and id numbers
        """
        # Calculates the premiums on the user's A, B, C, D curve at each bet fraction point so that
        # we can cluster the curves based on similarity
        user_premium_curves = [evaluate_premium_curve(
            [curve_row.A, curve_row.B, curve_row.C, curve_row.D],
            curve_row.bet_fractions) for i, curve_row in self.curves_df.iterrows()]

        # Create a list of lists containing the curve premium points in each category
        categories = [[user_premium_curves[curve_id]
                       for curve_id, curve_row in self.curves_df.iterrows()
                       if performance_group_mapping[curve_id] == group_num]
                      for group_num in range(num_groups)]

        # Create a list of lists containing the curve id numbers in each category
        category_ids = [[
            curve_id for curve_id, curve_row in self.curves_df.iterrows()
            if performance_group_mapping[curve_id] == group_num]
            for group_num in range(num_groups)]

        # Create the clustering objects for each group
        cluster_objects = [CurveCluster(num_clusters) for _ in range(num_groups)]

        # Pass the curves for each group to the appropriate cluster
        [cluster_obj.set_curve_mapping(
            category_curve) for cluster_obj, category_curve in zip(cluster_objects, categories)]

        # Perform the clustering on each curve group
        [cluster_obj.perform_clustering() for cluster_obj in cluster_objects]

        # Calculate the counts array that tracks the number of curves in each similarity cluster
        [cluster_obj.calculate_cluster_counts() for cluster_obj in cluster_objects]

        # Group it all together into a dict
        category_map = {group_num: {
            'ids': group_ids,
            'cluster': group_cluster_obj
        } for group_num, group_ids, group_cluster_obj in zip(
            range(num_groups), category_ids, cluster_objects)}

        return category_map

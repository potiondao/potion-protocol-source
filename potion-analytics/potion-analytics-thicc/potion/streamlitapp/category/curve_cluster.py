"""
This module provides a class which takes premium curves generated and performs a
clustering algorithm in order to group similar curves into different categories
"""
import numpy as np
from enum import Enum

from sklearn.metrics import mean_squared_error
from sklearn.cluster import SpectralClustering
from sklearn.cluster import DBSCAN

from potion.curve_gen.kelly import evaluate_premium_curve


class ClusteringMethod(Enum):
    """
    An Enum specifying the method to use when clustering curves
    """
    SPECTRAL = 0
    """Perform spectral clustering of curves"""
    DBSCAN = 1
    """Cluster curves using the DBSCAN algorithm"""


def similarity_matrix(ys):
    """
    Helper function that converts a python list of curves into a similarity matrix and returns it

    Parameters
    ----------
    ys : List[numpy.ndarray]
        The list of curves

    Returns
    -------
    smat : numpy.ndarray
        Similarity matrix
    """
    if len(ys) == 0:
        return 0.0

    # print('lys: {} ys: {}'.format(len(ys), ys))
    smat = np.zeros((len(ys), len(ys)))
    for i, y1 in enumerate(ys):
        for j, y2 in enumerate(ys):
            # print('i: {} j: {} y1: {} y2:{}'.format(i, j, y1, y2))
            rms = mean_squared_error(y1, y2, squared=False)
            smat[i, j] = rms
    # print('smat:\n{}'.format(smat))

    if len(ys) <= 1:
        return smat
    smat = 1 - smat / np.amax(smat)
    return smat


class CurveCluster:
    """
    This class takes premium curves generated and performs a
    clustering algorithm in order to group similar curves into different categories
    """

    def __init__(self, num_clusters, clustering_method=ClusteringMethod.SPECTRAL):
        """
        Constructs the class and specifies the number of categories (clusters) into
        which curves will be grouped.

        Parameters
        ----------
        num_clusters : int
            The number of categories to group curves into
        clustering_method : ClusteringMethod
            The method to use when clustering curves into similar groups. (Default Spectral)
        """
        self.num_clusters = num_clusters
        self.clustering_method = clustering_method

        self.curve_mapping = {}
        self.curve_mapping_flat = []
        self.curves_similarity = None
        self.clustering = None
        self.cluster_counts = None

    def create_curve_mapping(self, curves_df):
        """
        Iterates over each backtesting result and stores the premium points of the
        curve in a flat mapping to feed into the clustering algorithm. The flat mapping
        will be used to create the curve similarity matrix.

        Parameters
        ----------
        curves_df : pandas.DataFrame
            The curve DF containing all of the generated curve info

        Returns
        -------
        None
        """
        self.curve_mapping_flat = [evaluate_premium_curve(
            [row.A, row.B, row.C, row.D], row.bet_fractions)
            for i, row in curves_df.iterrows()]

    def set_curve_mapping(self, mapping):
        """
        Sets the curve_mapping_flat input to the clustering algorithm. Used to cluster a
        subset of curves rather than the entire database of curves

        Parameters
        ----------
        mapping : dict
            The curve input mapping we are setting

        Returns
        -------
        None
        """
        self.curve_mapping_flat = mapping

    def perform_clustering(self):
        """
        Performs the clustering algorithm on the curves and stores the results

        Returns
        -------
        None
        """
        self.curves_similarity = similarity_matrix(self.curve_mapping_flat)

        # print('cs len: {}'.format(len(self.curves_similarity)))

        if len(self.curves_similarity) < self.num_clusters:
            raise ValueError('Number of Curves must be >= number of clusters')

        if self.clustering_method == ClusteringMethod.SPECTRAL:
            self.clustering = SpectralClustering(
                self.num_clusters, affinity='precomputed').fit_predict(self.curves_similarity)
        elif self.clustering_method == ClusteringMethod.DBSCAN:
            self.clustering = DBSCAN(min_samples=1).fit_predict(self.curves_similarity)
        else:
            raise ValueError('Unknown Clustering Method: {}'.format(self.clustering_method))
        # print(self.clustering)

    def calculate_cluster_counts(self):
        """
        Iterates over the clustering results and counts the number of curves
        which belong to each category

        Returns
        -------
        None
        """
        self.cluster_counts = np.zeros(self.num_clusters)

        for cluster_id in self.clustering:
            self.cluster_counts[cluster_id] += 1

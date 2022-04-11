import unittest

import numpy as np

from potion.streamlitapp.category.curve_cluster import CurveCluster, ClusteringMethod


class CurveClusterTestCase(unittest.TestCase):

    def test_init(self):

        clusterer = CurveCluster(5, ClusteringMethod.DBSCAN)

        self.assertEqual(clusterer.num_clusters, 5)
        self.assertEqual(clusterer.clustering_method, ClusteringMethod.DBSCAN)
        self.assertEqual(clusterer.curve_mapping, {})
        self.assertEqual(clusterer.curve_mapping_flat, [])
        self.assertIsNone(clusterer.curves_similarity)
        self.assertIsNone(clusterer.clustering)
        self.assertIsNone(clusterer.cluster_counts)

    def test_create_curve_mapping(self):

        clusterer = CurveCluster(5)

        self.assertEqual((12, 10), np.shape(clusterer.curve_mapping_flat))

    def test_perform_clustering(self):

        clusterer = CurveCluster(2)

        clusterer.perform_clustering()

        # print(clusterer.clustering)

        vals = clusterer.clustering.tolist()
        one = [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0]
        two = [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1]

        self.assertTrue(one == vals or two == vals)

    def test_calculate_cluster_counts(self):

        clusterer = CurveCluster(2)

        clusterer.perform_clustering()
        clusterer.calculate_cluster_counts()

        # print(clusterer.clustering)
        # print(clusterer.cluster_counts)

        one = [4.0, 8.0]
        two = [8.0, 4.0]
        vals = clusterer.cluster_counts.tolist()

        self.assertTrue(one == vals or two == vals)


if __name__ == '__main__':
    unittest.main()

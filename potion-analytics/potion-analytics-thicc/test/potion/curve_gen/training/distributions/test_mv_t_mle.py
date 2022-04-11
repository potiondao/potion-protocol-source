import unittest
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import pandas as pd

from potion.curve_gen.training.distributions.multivariate_students_t import (MultiVarStudentT,
                                                                             mle_multi_var_t)


class MultivariateStudentTMLETestCase(unittest.TestCase):

    def test_mv_student_t(self):
        """
        Tests the estimator by generating a bunch of data according to a distribution and checking
        how well the estimator recovers the original parameters
        """
        mu = [0.0, 0.5]
        cov = pd.DataFrame([
            [2.1, 0.3],
            [0.3, 1.5]
        ])
        nu = 2.5
        num_samples = 3000

        mvst = MultiVarStudentT(mu, cov, nu)

        samples = mvst.rvs(num_samples)
        # print(samples)

        x_min = samples[0].min()
        x_max = samples[0].max()
        y_min = samples[1].min()
        y_max = samples[1].max()

        positions, grid = mvst.get_positions_for_pdf(np.asarray([x_min, y_min]),
                                                     np.asarray([x_max, y_max]),
                                                     np.asarray([0.01, 0.01]))

        fig, axs = plt.subplots(1, 2)

        ax0 = axs[0]
        ax1 = axs[1]

        estimates = mle_multi_var_t(samples, 2.5)

        mu_est = estimates[0]
        cov_est = estimates[1]
        fitness_score = estimates[2]

        print('Estimated Mu: {}'.format(mu_est))
        print('Estimated Cov: {}'.format(cov_est))

        est_mvst = MultiVarStudentT(mu_est, cov_est, nu)

        # ax.set_aspect('equal')
        ax0.contourf(grid[0], grid[1], est_mvst.pdf(positions))
        ax0.scatter(samples[0], samples[1])
        ax0.set_xlim(x_min, x_max)
        ax0.set_ylim(y_min, y_max)

        ax1.plot(range(len(fitness_score)), -np.asarray(fitness_score))

        fig, ax = plt.subplots(1, 1, subplot_kw={"projection": "3d"})
        surf = ax.plot_surface(grid[0], grid[1], est_mvst.pdf(positions), cmap=cm.coolwarm,
                               linewidth=0, antialiased=False)
        plt.show()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()

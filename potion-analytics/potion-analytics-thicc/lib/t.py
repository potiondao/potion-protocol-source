# **************************************************************
# This file contains Conner DiPaolo's Multivariate Student T
# MLE routine. This code which can be found
# here: https://gist.github.com/cdipaolo/9dd6794a4f0a2889ef60a5effa419093
# Since the repository is a gist with no setup.py, it cannot be installed
# through pip as a normal python package.
# This file uses the Unlicense which can be found here:
# https://unlicense.org/
# and has the text copied below.
# **************************************************************
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <https://unlicense.org>
import numpy as np
from scipy import special


def t(X, dof=3.5, iter=200, eps=1e-6):
    """t
    Estimates the mean and covariance of the dataset
    X (rows are datapoints) assuming they come from a
    student t likelihood with no priors and dof degrees
    of freedom using the EM algorithm.

    Implementation based on the algorithm detailed in Murphy
    Section 11.4.5 (page 362).

    :param X: dataset
    :type  X: np.array[n,d]
    :param dof: degrees of freedom for likelihood
    :type  dof: float > 2
    :param iter: maximum EM iterations
    :type  iter: int
    :param eps: tolerance for EM convergence
    :type  eps: float
    :return: estimated covariance, estimated mean, list of
             objectives at each iteration.
    :rtype: np.array[d,d], np.array[d], list[float]
    """
    # initialize parameters
    D = X.shape[1]
    N = X.shape[0]
    cov = np.cov(X, rowvar=False)
    mean = X.mean(axis=0)
    mu = X - mean
    delta = np.einsum('ij,ij->i', mu, np.linalg.solve(cov, mu.T).T)
    z = (dof + D) / (dof + delta)
    obj = [
        -N * np.linalg.slogdet(cov)[1] / 2 - (z * delta).sum() / 2 \
        - N * special.gammaln(dof / 2) + N * dof * np.log(dof / 2) / 2 + dof * (np.log(z) - z).sum() / 2
    ]

    # iterate
    for i in range(iter):
        # M step
        mean = (X * z[:, None]).sum(axis=0).reshape(-1, 1) / z.sum()
        mu = X - mean.squeeze()[None, :]
        cov = np.einsum('ij,ik->jk', mu, mu * z[:, None]) / N

        # E step
        delta = (mu * np.linalg.solve(cov, mu.T).T).sum(axis=1)
        delta = np.einsum('ij,ij->i', mu, np.linalg.solve(cov, mu.T).T)
        z = (dof + D) / (dof + delta)

        # store objective
        obj.append(
            -N * np.linalg.slogdet(cov)[1] / 2 - (z * delta).sum() / 2 \
            - N * special.gammaln(dof / 2) + N * dof * np.log(dof / 2) / 2 + dof * (np.log(z) - z).sum() / 2
        )

        if np.abs(obj[-1] - obj[-2]) < eps:
            break
    return cov, mean.squeeze(), obj
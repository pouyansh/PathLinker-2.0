#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from utils import iterator
from .pyrwr import PyRWR


class PPR(PyRWR):
    def __init__(self):
        super().__init__()

    def compute(self,
                seeds,
                c=0.15,
                epsilon=1e-9,
                max_iters=100,
                handles_deadend=True,
                device='cpu'):

        '''
        Compute the PPR score vector w.r.t. the seed node

        inputs
            seeds : list
                list of seeds
            c : float
                restart probability
            epsilon : float
                error tolerance for power iteration
            max_iters : int
                maximum number of iterations for power iteration
            handles_deadend : bool
                if true, it will handle the deadend issue in power iteration
                otherwise, it won't, i.e., no guarantee for sum of RWR scores
                to be 1 in directed graphs
        outputs
            r : ndarray
                PPR score vector
        '''

        self.normalize()
        seeds = [seed for seed in seeds]

        if len(seeds) == 0:
            raise ValueError('Seeds are empty')
        if min(seeds) < 0 or max(seeds) >= self.n:
            raise ValueError('Out of range of seed node id')

        #  q = np.zeros((self.n, 1))
        q = np.zeros(self.n)
        q[seeds] = 1.0 / len(seeds)

        r, residuals = iterator.iterate(self.nAT, q, c, epsilon,
                                        max_iters, handles_deadend, norm_type=1, device=device)
        return r

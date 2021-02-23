from statistics import mean

import util
from community import *

NUM_GENERATIONS = 5


class GenerationalCommunity:
    def __init__(self, x, y, commtype="village"):
        self.x = x
        self.y = y
        self.type = commtype
        self.children_val = 0.0
        self.adult_vals = [0.0] * NUM_GENERATIONS
        self.rate_of_change = 1.0
        self.hist = []
        self.neighbors = {}

    def to_dict(self, t="now"):
        if t == "now":
            val = self.val
        elif type(t) is int:
            val = self.hist[t]

        return {'x': self.x, 'y': self.y, 'type': self.type, 'val': val}

    @property
    def size(self):
        return COMM_SIZES[self.type]

    @property
    def val(self):
        return mean(self.adult_vals[-NUM_GENERATIONS:])

    @val.setter
    def val(self, newval):
        self.children_val = newval
        self.adult_vals = [newval for _ in self.adult_vals]

    def new_generation(self):
        self.hist.append(self.val)
        self.adult_vals.append(self.children_val)

    def update(self, newval):
        # self.children_val = newval
        self.children_val = self.val + self.rate_of_change * (newval - self.val)

    def jitter(self, amt):
        for i in range(-NUM_GENERATIONS, 0):
            self.adult_vals[i] = util.random_jitter(self.adult_vals[i], amt)

    @property
    def ind_neighbors(self):
        return [nn for n in self.neighbors for nn in n.neighbors
                if nn not in self.neighbors]

    def add_neighbor(self, other, dist):
        threshold = DIST_THRESHOLDS[(self.type, other.type)]
        self.neighbors[other] = (threshold - dist) / threshold


# def double_locus_opposite_cities(world):
#     for comm in world:
#         comm.val = 0.5
#     site1 = sorted(world, key=lambda c: (c.size, c.x + c.y), reverse=True)[0]
#     site2 = sorted((c for c in world if c is not site1),
#                    key=lambda c: (c.size, -(c.x + c.y)), reverse=True)[0]
#     site1.val = 0.0
#     site2.val = 1.0
#     site1.rate_of_change = 0.0
#     site2.rate_of_change = 0.0


# def neighbor_size_dist_weighted_update(comm, n_infl=1):
#     numer = (comm.hist[-1] * comm.size
#              + n_infl * sum(n.hist[-1] * n.size * wt
#                             for n, wt in comm.neighbors.items()))
#     denom = (comm.size
#              + n_infl * sum(n.size * wt for n, wt in comm.neighbors.items()))
#     weighted_val = numer / denom
#     return weighted_val

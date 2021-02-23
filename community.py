import util

COMM_SIZES = {'village': 1,
              'town': 2,
              'city': 5}

DIST_THRESHOLDS = {('village', 'village'): 8,
                   ('town', 'village'): 12,
                   ('town', 'town'): 20,
                   ('city', 'village'): 15,
                   ('city', 'town'): 25,
                   ('city', 'city'): 30}
DIST_THRESHOLDS[('village', 'town')] = DIST_THRESHOLDS[('town', 'village')]
DIST_THRESHOLDS[('village', 'city')] = DIST_THRESHOLDS[('city', 'village')]
DIST_THRESHOLDS[('town', 'city')] = DIST_THRESHOLDS[('city', 'town')]


class Community:
    def __init__(self, x, y, commtype="village"):
        self.x = x
        self.y = y
        self.type = commtype
        self.val = 0.0
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

    def new_generation(self):
        self.hist.append(self.val)

    def update(self, newval):
        self.val = self.val + self.rate_of_change * (newval - self.val)

    def jitter(self, amt):
        self.val = util.random_jitter(self.val, amt)

    def add_neighbor(self, other, dist):
        threshold = DIST_THRESHOLDS[(self.type, other.type)]
        self.neighbors[other] = (threshold - dist) / threshold

    @property
    def ind_neighbors(self):
        return [nn for n in self.neighbors for nn in n.neighbors
                if nn not in self.neighbors]

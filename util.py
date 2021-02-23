import random


def random_jitter(val, jitter=0.01):
    newval = val + jitter * random.uniform(-1, 1)
    if newval > 1.0:
        newval = 1.0
    elif newval < 0.0:
        newval = 0.0
    return newval

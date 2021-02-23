import sys
import random
from math import sqrt
import matplotlib.pyplot as plt

import logging
import os

from community import *
from plotting import *
# import util

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def init_savedir(dirname):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass

    logfilename = "lingnetsim.log"
    filehandler = logging.FileHandler(f"{dirname}/{logfilename}", mode='w')
    filehandler.setLevel(logging.INFO)
    logger.addHandler(filehandler)


def gen_world(size=100, density=4, seed=None, commclass=Community,
              savefig=False, savedir="figs"):
    if seed is None:
        seed = random.randrange(sys.maxsize)
    random.seed(seed)

    logger.info(f"Generating world with size={size}, density={density},"
                f"random seed={seed}, commclass={commclass}")

    if savefig:
        filename = "worldgen_vals.txt"
        logger.info(f"Saving worldgen values to '{filename}'")
        with open(f"{savedir}/{filename}", 'w') as f:
            f.write(f"World generated with size={size}, density={density},"
                    f"random seed={seed}")

    world = []
    for i in range((size // 10) ** 2 * density):
        x = random.randrange(size)
        y = random.randrange(size)
        world.append(commclass(x, y))
    if savefig:
        plot_world(world)
        plt.savefig(savedir + "/network-gen0-villages.pdf")

    # form initial network
    for i, comm1 in enumerate(world):
        for comm2 in world[i+1:]:
            dist = sqrt((comm1.x - comm2.x) ** 2 + (comm1.y - comm2.y) ** 2)
            if dist < DIST_THRESHOLDS[('village', 'village')]:
                comm1.add_neighbor(comm2, dist)
                comm2.add_neighbor(comm1, dist)
    if savefig:
        plot_world(world)
        plt.savefig(savedir + "/network-gen1-connections.pdf")

    # promote villages to towns
    for comm in sorted(world, reverse=True, key=lambda c: len(c.neighbors)):
        n_villages = len([n for n in comm.neighbors if n.type == "village"])
        n_towns = len([n for n in comm.neighbors if n.type == "town"])
        if n_villages - 5 * n_towns > 5:
            comm.type = 'town'
    if savefig:
        plot_world(world)
        plt.savefig(savedir + "/network-gen2-towns.pdf")

    # add medium distance connections
    for i, comm1 in enumerate(world):
        for comm2 in world[i+1:]:
            dist = sqrt((comm1.x - comm2.x) ** 2 + (comm1.y - comm2.y) ** 2)
            if comm1.type == "town" and comm2.type == "village" and \
                    dist < DIST_THRESHOLDS[("town", "village")]:
                comm1.add_neighbor(comm2, dist)
                comm2.add_neighbor(comm1, dist)
            elif comm1.type == "town" and comm2.type == "town" and \
                    dist < DIST_THRESHOLDS[("town", "town")]:
                comm1.add_neighbor(comm2, dist)
                comm2.add_neighbor(comm1, dist)
    if savefig:
        plot_world(world)
        plt.savefig(savedir + "/network-gen3-town-conn.pdf")

    # promote towns to cities
    for comm in sorted(world, reverse=True, key=lambda c: len(c.neighbors)):
        if comm.type != "town":
            continue
        n_villages = len([n for n in comm.neighbors if n.type == "village"])
        n_towns = len([n for n in comm.neighbors if n.type == "town"])
        n_cities = len([n for n in comm.neighbors if n.type == "city"])
        if n_towns - 4 * n_cities > 4:
            comm.type = 'city'
    if savefig:
        plot_world(world)
        plt.savefig(savedir + "/network-gen4-cities.pdf")

    # add long distance connections
    for i, comm1 in enumerate(world):
        for comm2 in world[i+1:]:
            dist = sqrt((comm1.x - comm2.x) ** 2 + (comm1.y - comm2.y) ** 2)
            if comm1.type == "city" and comm2.type == "village" and \
                    dist < DIST_THRESHOLDS[("city", "village")]:
                comm1.add_neighbor(comm2, dist)
                comm2.add_neighbor(comm1, dist)
            elif comm1.type == "city" and comm2.type == "town" and \
                    dist < DIST_THRESHOLDS[("city", "town")]:
                comm1.add_neighbor(comm2, dist)
                comm2.add_neighbor(comm1, dist)
            elif comm1.type == "city" and comm2.type == "city" and \
                    dist < DIST_THRESHOLDS[("city", "city")]:
                comm1.add_neighbor(comm2, dist)
                comm2.add_neighbor(comm1, dist)
    if savefig:
        plot_world(world)
        plt.savefig(savedir + "/network-gen5-city-conn.pdf")

    return world


#
# initialization algorithms
#

def single_locus_random_free(world):
    start_site = random.choice(world)
    start_site.val = 1.0


def single_locus_random_unchanging(world):
    start_site = random.choice(world)
    start_site.val = 1.0
    start_site.rate_of_change = 0


def single_locus_unchanging_city(world):
    start_site = sorted(world, key=lambda c: c.size, reverse=True)[0]
    start_site.val = 1.0
    start_site.rate_of_change = 0


def double_locus_random(world):
    for comm in world:
        comm.val = 0.5
    site1, site2 = random.choices(world, k=2)
    site1.val = 0.0
    site2.val = 1.0
    site1.rate_of_change = 0.0
    site2.rate_of_change = 0.0


def double_locus_opposite_cities(world):
    for comm in world:
        comm.val = 0.5
    site1 = sorted(world, key=lambda c: (c.size, c.x + c.y), reverse=True)[0]
    site2 = sorted((c for c in world if c is not site1),
                   key=lambda c: (c.size, -(c.x + c.y)), reverse=True)[0]
    site1.val = 0.0
    site2.val = 1.0
    site1.rate_of_change = 0.0
    site2.rate_of_change = 0.0


#
# Weighting/update algorithms
#

# def random_drift(comm):
#     difference = 0.01 * random.uniform(-1, 1)
#     newval = comm.val + difference
#     if newval > 1.0:
#         newval = 1.0
#     elif newval < 0.0:
#         newval = 0.0
#     return newval


def neighbor_weighted_update(comm, n_infl=0.10):
    numer = comm.hist[-1] + n_infl * sum(n.hist[-1] for n in comm.neighbors)
    denom = 1 + n_infl * len(comm.neighbors)
    weighted_val = numer / denom
    return weighted_val


def neighbor_size_weighted_update(comm, n_infl=0.10):
    numer = (comm.hist[-1] * comm.size
             + n_infl * sum(n.hist[-1] * n.size for n in comm.neighbors))
    denom = (comm.size
             + n_infl * sum(n.size for n in comm.neighbors))
    weighted_val = numer / denom
    return weighted_val


def neighbor_size_dist_weighted_update(comm, n_infl=1):
    numer = (comm.hist[-1] * comm.size
             + n_infl * sum(n.hist[-1] * n.size * wt
                            for n, wt in comm.neighbors.items()))
    denom = (comm.size
             + n_infl * sum(n.size * wt for n, wt in comm.neighbors.items()))
    weighted_val = numer / denom
    return weighted_val


#
# learning algorithms
#

def copy_input(comm, val):
    # val = comm.val + comm.rate_of_change * (val - comm.val)
    return val


def clamp(comm, val, cutoff=0.5):
    if val > cutoff:
        return 1.0
    elif val < cutoff:
        return 0.0
    else:
        return val


def init_sim(world, method="default"):
    if method == "default":
        method = single_locus
    logger.info(f"Initializing simulation with method '{method.__name__}'.")
    method(world)
    logger.info("Done.")


def run_sim(world, rounds, weighting="default", learning="default", randomize=False):
    if weighting == "default":
        weighting = neighbor_weighted_update
    if learning == "default":
        learning = copy_input

    logger.info(f"Running simulation with weighting method '{weighting.__name__}' "
                f"and learning method '{learning}'.")
    for i in range(rounds):
        for comm in world:
            comm.new_generation()
            if randomize:
                comm.jitter(0.05)
        for comm in world:
            weighted_input = weighting(comm)
            newval = learning(comm, weighted_input)
            comm.update(newval)
    logger.info("Done.")


def sim_simple(world, rounds, init="default", weighting="default",
               learning="default", randomize=False, interactive=False,
               savefig=False, savedir="figs", color="values"):
    init_sim(world, method=init)

    plot_world(world, color=color)
    if interactive:
        plt.show()
    if savefig:
        filename = "network-sim-start.pdf"
        logger.info(f"Saving figure {filename}.")
        plt.savefig(f"{savedir}/{filename}")

    run_sim(world, rounds, weighting=weighting, learning=learning,
            randomize=randomize)

    plot_world(world, color=color)
    if interactive:
        plt.show()
    if savefig:
        filename = "network-sim-end.pdf"
        logger.info(f"Saving figure {filename}.")
        plt.savefig(f"{savedir}/{filename}")

    plot_val_by_comm(world)
    if interactive:
        plt.show()
    if savefig:
        filename = "sim-results-by-comm.pdf"
        logger.info(f"Saving figure {filename}.")
        plt.savefig(f"{savedir}/{filename}")

    plot_avg_val(world)
    if interactive:
        plt.show()
    if savefig:
        filename = "sim-results-avg.pdf"
        logger.info(f"Saving figure {filename}.")
        plt.savefig(f"{savedir}/{filename}")


def interactive_view(world):
    rounds = len(world[0].hist)
    currtime = 0

    def key_event(e):
        nonlocal currtime

        if e.key == "right":
            currtime += 1
        elif e.key == "left":
            currtime -= 1
        elif e.key == "ctrl+right":
            currtime += 5
        elif e.key == "ctrl+left":
            currtime -= 5
        else:
            return

        currtime = currtime % rounds
        print(f"now at time: {currtime}")

        plt.cla()
        plot_world(world, color="values", t=currtime)
        fig.canvas.draw()

    fig = plt.gcf()
    fig.canvas.mpl_connect('key_press_event', key_event)
    plot_world(world, color="values", t=currtime)
    plt.show()


def demo_worldgen(seed=None):
    savefig = True
    savedir = "results-worldgen"
    init_savedir(savedir)

    gen_world(size=50, density=4, savefig=savefig, savedir=savedir)


def demo_simple(seed=None, interactive=False):
    savefig = True
    savedir = "results-single-locus"
    init_savedir(savedir)

    world = gen_world(size=50, density=4)
    sim_simple(
        world, rounds=50, interactive=False,
        init=single_locus_unchanging_city,
        weighting=neighbor_size_dist_weighted_update,
        savefig=savefig, savedir=savedir)
    if interactive:
        interactive_view(world)


def demo_double_locus(seed=None, interactive=False):
    savefig = True
    savedir = "results-double-locus"
    init_savedir(savedir)

    world = gen_world(size=50, density=4)
    sim_simple(
        world, rounds=20, interactive=False,
        init=double_locus_opposite_cities,
        weighting=neighbor_size_dist_weighted_update,
        savefig=savefig, savedir=savedir, color="values-twocolor")
    if interactive:
        interactive_view(world)


def demo_generations(seed=None, interactive=False):
    import lowbackmerger as lbm

    savefig = True
    savedir = "results-generations"
    init_savedir(savedir)

    world = gen_world(size=50, density=4,
                      commclass=lbm.GenerationalCommunity)
    sim_simple(
        world, rounds=20, interactive=False,
        init=single_locus_unchanging_city,
        weighting=neighbor_size_dist_weighted_update,
        learning=clamp,
        savefig=savefig, savedir=savedir, color="values-twocolor")
    if interactive:
        interactive_view(world)


def lowbackmerger_main(seed=None):
    from functools import partial
    import lowbackmerger as lbm

    savefig = True
    savedir = "results-lbm"
    init_savedir(savedir)

    clamp50 = partial(clamp, cutoff=0.5)
    # clamp20 = partial(clamp, cutoff=0.2)

    world = gen_world(size=100, density=4,
                      commclass=lbm.GenerationalCommunity)

    init_sim(world, method=double_locus_opposite_cities)

    plot_world(world, color="values-twocolor")
    if savefig:
        filename = "network-sim-start.pdf"
        logger.info(f"Saving figure {filename}.")
        plt.savefig(f"{savedir}/{filename}")

    run_sim(world, rounds=10,
            weighting=neighbor_size_dist_weighted_update,
            learning=copy_input,
            randomize=False)

    plot_world(world, color="values-twocolor")
    if savefig:
        filename = "network-sim-dialect-spread.pdf"
        logger.info(f"Saving figure {filename}.")
        plt.savefig(f"{savedir}/{filename}")

    run_sim(world, rounds=40,
            weighting=neighbor_size_dist_weighted_update,
            learning=clamp50,
            randomize=False)

    plot_world(world, color="values-twocolor")
    if savefig:
        filename = "network-sim-dialect-crystalize.pdf"
        logger.info(f"Saving figure {filename}.")
        plt.savefig(f"{savedir}/{filename}")

    run_sim(world, rounds=50,
            weighting=neighbor_size_dist_weighted_update,
            learning=clamp50,
            randomize=True)

    plot_world(world, color="values-twocolor")
    if savefig:
        filename = "network-sim-randomize.pdf"
        logger.info(f"Saving figure {filename}.")
        plt.savefig(f"{savedir}/{filename}")

    plot_val_by_comm(world)
    if savefig:
        filename = "sim-results-by-comm.pdf"
        logger.info(f"Saving figure {filename}.")
        plt.savefig(f"{savedir}/{filename}")

    plot_avg_val(world)
    if savefig:
        filename = "sim-results-avg.pdf"
        logger.info(f"Saving figure {filename}.")
        plt.savefig(f"{savedir}/{filename}")


if __name__ == "__main__":
    # demo_worldgen()
    demo_simple()
    # demo_double_locus()
    # demo_generations()
    # lowbackmerger_main()

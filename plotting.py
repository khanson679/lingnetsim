"""
Functions for plotting network and simulation results with matplotlib.
"""

from statistics import mean
import matplotlib.pyplot as plt
from matplotlib import collections as mc
import pandas as pd


def plot_nodes(world, color=None, t="now"):
    df = pd.DataFrame.from_records(comm.to_dict(t=t) for comm in world)

    colors = {'village': 0, 'town': 0.5, 'city': 1}
    sizes = {'village': 30, 'town': 90, 'city': 200}

    if color == "community_type":
        cdata = df['type'].map(colors)
        cmap = None
        edgecolor = None
    elif color == "values":
        cdata = "val"
        cmap = "Reds"
        edgecolor = "black"
    elif color == "values-twocolor":
        cdata = "val"
        cmap = "RdBu"
        edgecolor = "black"
    elif color is None:
        cdata = None
        cmap = None
        edgecolor = None
    else:
        raise ValueError(f"No such color scheme: {color}")

    plt.scatter(x='x', y='y', s=df['type'].map(sizes),
                c=cdata, cmap=cmap, vmin=0, vmax=1,
                data=df, edgecolors=edgecolor, linewidths=0.5)


def plot_edges(edges, ax, color=None):
    lines = [((c1.x, c1.y), (c2.x, c2.y)) for (c1, c2) in edges]
    colormap = {('village', 'village'): "C0",
                ('town', 'village'): "C1",
                ('village', 'town'): "C1",
                ('town', 'town'): "C2",
                ('city', 'village'): "C3",
                ('village', 'city'): "C3",
                ('city', 'town'): "C4",
                ('town', 'city'): "C4",
                ('city', 'city'): "C5"}

    if color == "connection_type":
        cdata = [colormap[(c1.type, c2.type)] for (c1, c2) in edges]
    elif color is None:
        cdata = "gray"
    else:
        raise ValueError(f"No such color scheme: {color}")

    lc = mc.LineCollection(lines, colors=cdata, linewidths=0.5, zorder=0)
    ax.add_collection(lc)


def plot_world(world, color="default", t="now"):
    plt.cla()
    plt.tight_layout()
    edges = {(c1, c2) for c1 in world for c2 in c1.neighbors}
    ax = plt.gca()

    node_color = None
    edge_color = None
    if color == "values":
        node_color = "values"
        edge_color = None
    elif color == "values-twocolor":
        node_color = "values-twocolor"
        edge_color = None
    elif color == "default":
        node_color = "community_type"
        edge_color = None
    else:
        raise ValueError(f"No such color scheme: {color}")

    plot_nodes(world, color=node_color, t=t)
    plot_edges(edges, ax, color=edge_color)


def plot_val_by_comm(world):
    plt.cla()
    plt.tight_layout()
    rounds = len(world[0].hist)
    for comm in world:
        plt.plot(range(rounds), comm.hist, linewidth=0.5)


def plot_avg_val(world):
    plt.cla()
    plt.tight_layout()
    rounds = len(world[0].hist)
    plt.plot(range(rounds),
             [mean(comm.hist[i] for comm in world) for i in range(rounds)])

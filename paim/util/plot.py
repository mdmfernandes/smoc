# -*- coding: utf-8 -*-
"""Graphics plotting functions"""

from matplotlib import pyplot as plt
from matplotlib import animation

import pandas as pd

import seaborn
seaborn.set(style='whitegrid')
#seaborn.set_context('notebook')

def plot_fronts(fronts, evaluate, ax, plot_colors):
    for i, inds in enumerate(fronts):
        par = [evaluate(ind) for ind in inds]

        df = pd.DataFrame(par)

        df[0] = df[0]*1e6   # Scale to uW

        df.plot(ax=ax, kind='scatter', label='Front ' + str(i+1),
                x=df.columns[0], y=df.columns[1], color=plot_colors[i % len(plot_colors)])
        

def plot_pareto_fronts(fronts, evaluate):
    """Plot the pareto fronts

    Arguments:
        fronts {list} -- list with the pareto fronts
    """
    plot_colors = seaborn.color_palette("Set1", n_colors=100)
    plt.ion()
    #plt.show()
    fig, ax = plt.subplots(1, figsize=(8, 8))

    plot_fronts(fronts, evaluate, ax, plot_colors)

    plt.xlabel('power (uW)')
    plt.ylabel('gain (dB)')

    #plt.draw()
    plt.pause(0.01)


def animate(frame_index, logbook, evaluate, ax, plot_colors, sortLogNondominated):
    """Updates all plots to match frame _i_ of the animation"""
    ax.clear()
    fronts = sortLogNondominated(logbook.select('pop')[frame_index], 
                                           len(logbook.select('pop')[frame_index]))    
    
    plot_fronts(fronts, evaluate, ax, plot_colors)
        
    ax.set_title('Animated Pareto Front\nt=' + str(frame_index), weight='bold')
    ax.set_xlabel('power (uW)');ax.set_ylabel('gain (dB)')
    return []

def plot_pareto_fronts_animated(logbook, evaluate, sortLogNondominated):
    #plt.ion()
    fig = plt.figure(figsize=(8,8))
    ax = fig.gca()
    plot_colors = seaborn.color_palette("Set1", n_colors=100)
    anim = animation.FuncAnimation(fig, lambda i: animate(i, logbook, evaluate, ax, plot_colors, sortLogNondominated), frames=len(logbook), interval=150, blit=True)
    anim.save('animation.gif', writer='imagemagick', fps=10)
    #plt.pause(0.01)


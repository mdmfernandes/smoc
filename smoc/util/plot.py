# This file is part of SMOC
# Copyright (C) 2018  Miguel Fernandes
#
# SMOC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SMOC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""Helpers to plot graphics."""

from bokeh.models import PrintfTickFormatter
from bokeh.palettes import viridis
from bokeh.plotting import ColumnDataSource, figure, output_file, show

from .text_format import eng_string


def plot_pareto_fronts(fronts, circuit_vars, objectives, plot_fname):
    """Plot the pareto fronts given by the optimizer.

    Arguments:
        fronts {list} -- pareto fronts
        circuit_vars {dict} -- circuit design variables w/ units
        objectives {dict} -- circuit optimization objectives w/ units
        plot_fname {str} -- path of the plot file
    """
    vars_names = list(circuit_vars.keys())
    vars_units = [var[1] for var in circuit_vars.values()]

    fit_names = list(objectives.keys())
    fit_units = [fit[1] for fit in objectives.values()]

    # Define the colors to use in the graphic, according to the number of pareto fronts
    # each front = one color
    num_colors = max(3, len(fronts))
    try:
        colors = viridis(num_colors)
    except KeyError as err:
        raise KeyError(f"The colors vector doesn't support {err} colors.")

    # Add the Fitnesses to the tooltips
    tooltips = [(fit, f"@{fit}") for fit in fit_names]

    # Add separator between fitnesses and circuit_variables
    tooltips.extend([(":::::::::::::::", "::::::::::::::")])

    # Add the variables to the tooltips
    tooltips.extend([(var, f"@{var}") for var in vars_names])

    # Create the figure
    date_time = plot_fname.split('/')[-1].split('.')[0]
    title = f"Plotting {len(fronts)} pareto fronts - {date_time.replace('-', ':')}"
    p = figure(plot_width=800, plot_height=800, tooltips=tooltips, title=title,
               active_scroll='wheel_zoom')

    for idx, inds in enumerate(fronts):
        # Get the fitness values
        fits = list(map(lambda ind: ind.fitness.values, inds))

        # The '*' separates the various fitnesses, otherwise it will try to zip
        # all the fitnesses at the same time and put them in x,y, which will give
        # an error if we have more than two fitness (and even with 2 the result
        # won't be the expected)
        (x, y) = zip(*fits)  # Unpack the fitnesses

        # Scale the power to uW
        #x = [val*1e6 for val in x]
        # or x = list(map(lambda x: x*1e6, x))
        # List comprehension is more pythonic and it's usually faster
        # if we need to use lambdas in map

        # Values to plot on the graphic
        source = dict(x=x, y=y)

        # Add the fitnesses to the tooltips
        for j, fit in enumerate(fit_names):
            source.update({fit: [f"{eng_string(f[j])}{fit_units[j]}" for f in fits]})

        # Add the circuit variables to the tooltips
        # ind[j] é a variável 'j' do individuo
        for j, var in enumerate(vars_names):
            source.update({var: [f"{eng_string(ind[j])}{vars_units[j]}" for ind in inds]})

        p.circle('x', 'y', source=ColumnDataSource(data=source), size=10,
                 color=colors[idx], muted_color=colors[idx], muted_alpha=0.1,
                 legend=f"Pareto {idx+1} (ind={len(inds)})")

    # Format the title
    p.title.text_font_size = '16pt'
    p.title.align = 'center'
    # Format the axis labels
    p.xaxis.axis_label = f"{fit_names[0]} [{fit_units[0]}]"
    p.xaxis.formatter = PrintfTickFormatter(format='%.2e')
    p.yaxis.axis_label = f"{fit_names[1]} [{fit_units[1]}]"
    p.axis.axis_label_text_font_style = 'bold'
    p.axis.axis_label_text_font_size = '11pt'
    # Format the legend
    p.legend.location = "bottom_right"
    p.legend.click_policy = "mute"
    p.legend.label_text_font_size = '8pt'

    output_file(plot_fname)

    show(p)


# # PODE SER UTIL
# print(logbook.chapters['population'].select("value"))
# print(logbook.chapters['fitness'].select("value"))

# def animate(frame_index, logbook, evaluate, ax, plot_colors, sortLogNondominated):
#     """Updates all plots to match frame _i_ of the animation"""
#     ax.clear()
#     fronts = sortLogNondominated(logbook.select('pop')[frame_index],
#                                            len(logbook.select('pop')[frame_index]))

#     plot_fronts(fronts, evaluate, ax, plot_colors)

#     ax.set_title('Animated Pareto Front\nt=' + str(frame_index), weight='bold')
#     ax.set_xlabel('power (uW)');ax.set_ylabel('gain (dB)')
#     return []

# def plot_pareto_fronts_animated(logbook, evaluate, sortLogNondominated):
#     #plt.ion()
#     fig = plt.figure(figsize=(8,8))
#     ax = fig.gca()
#     plot_colors = seaborn.color_palette("Set1", n_colors=100)
#     anim = animation.FuncAnimation(fig,
#                                    lambda i: animate(i, logbook, evaluate, ax,
#                                                      plot_colors, sortLogNondominated),
#                                    frames=len(logbook), interval=150, blit=True)
#     anim.save('animation.gif', writer='imagemagick', fps=10)
#     #plt.pause(0.01)

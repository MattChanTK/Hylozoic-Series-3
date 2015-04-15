import matplotlib.pyplot as plt
import matplotlib.axes as axes
import numpy as np
from time import clock, sleep
from collections import defaultdict
from sys import getsizeof
from datetime import timedelta
import os

import cbla_data_collect as cbla_data
from cbla_engine.save_figure import save


class Plotter(object):

    def __init__(self, data_file=None):

        # all data
        self.data = defaultdict(lambda: defaultdict(lambda: {'x': [], 'y': []}))
        if data_file:
            self.extract_data_files(data_file)

        # plot objects
        self.plot_objects = dict()
        self.__construct_plot_objects()

    def __construct_plot_objects(self):

        for node_name in self.data.keys():
            self.plot_objects[(node_name, 'history')] = PlotObject(fig_title='History Plot - %s' % node_name)
            self.plot_objects[(node_name, 'exemplars')] = PlotObject(fig_title='Exemplars Snapshots - %s' % node_name)


    def plot(self):

        grid_dim = (2, 4)
        engine_based_type = ('S', 'M', 'S1_predicted', 'in_idle_mode',)#'is_exploring')
        expert_based_type = ('action_values', 'mean_errors', 'action_counts', 'latest_rewards',) #'best_action')

        for node_name, node_data in self.data.items():
            for data_type, data_val in node_data.items():

                # cbla_engine-based data
                if data_type in engine_based_type:

                    # instantiate axis
                    ax_name = '%s' % data_type
                    ax_num = engine_based_type.index(data_type)+1
                    self.plot_objects[(node_name, 'history')].add_ax(ax_name=ax_name,
                                                        location=(grid_dim[0], grid_dim[1], ax_num))

                    # configure the plot
                    plot_config = dict()
                    plot_config['xlabel'] = 'time (minute)'
                    plot_config['ylabel'] = 'value'
                    plot_config['title'] = '%s vs. time plot' % data_type

                    if data_type in ('in_idle_mode', 'is_exploring'):
                        plot_config['int_yaxis'] = True
                        plot_config['ylim'] = (-0.5, 1.5)
                    elif data_type == 'M':
                        plot_config['int_yaxis'] = True
                        plot_config['ylim'] = (-0.5, 3.5)
                        plot_config['linestyle'] = ' '
                        plot_config['marker'] = '.'

                    # plot the evolution plot
                    plot_evolution(self.plot_objects[(node_name, 'history')].ax[ax_name], data_val['y'], data_val['x'], **plot_config)

                    print('%s: plotted evolution of %s' % (node_name, data_type))

                # expert-based data
                elif data_type in expert_based_type:

                    # instantiate axis
                    ax_name = '%s' % data_type
                    ax_num = len(engine_based_type) + expert_based_type.index(data_type) + 1
                    self.plot_objects[(node_name, 'history')].add_ax(ax_name=ax_name,
                                                        location=(grid_dim[0], grid_dim[1], ax_num))

                    # configure the plot
                    plot_config = dict()
                    plot_config['xlabel'] = 'time (minute)'
                    plot_config['ylabel'] = 'value'
                    plot_config['title'] = '%s vs. time plot' % data_type

                    # plot the evolution plot
                    plot_regional_evolution(self.plot_objects[(node_name, 'history')].ax[ax_name], data_val['y'], data_val['x'],
                                            **plot_config)

                    print('%s: plotted regional evolution of %s' % (node_name, data_type))

    def show_plots(self, plot_names=None, plot_stay=True):

        if plot_names is None:
            plt.show(block=plot_stay)
        else:
            for plot_name in plot_names:
                self.plot_objects[plot_name].fig.show()


    def update_plot(self, data_file):

        self.extract_data_files(data_file)
        self.plot()

    def extract_data_files(self, data_file):
        for node_name, raw_data in data_file['data'].items():
            t0 = raw_data[0]['time']
            for packet in raw_data:
                for data_type, data_val in packet.items():
                    self.data[node_name][data_type]['y'].append(data_val)
                    #self.data[node_name][data_type]['x'].append(packet['step'])
                    self.data[node_name][data_type]['x'].append(to_time_value(packet['time'] - t0, 'minute'))

            for data_type, data_element in self.data[node_name].items():
                print('%s --- %s' % (node_name, data_type))
                print(self.data[node_name][data_type]['y'][100])

    def save_all_plots(self, sub_folder_name):
        directory = os.path.join('cbla_saved_figures', sub_folder_name)
        for plot_obj in self.plot_objects.values():
            plot_obj.save_to_file(directory=directory, filename=plot_obj.fig_title)


class PlotObject(object):
    def __init__(self, fig_num=None, fig_title=None):
        self.fig = plt.figure(num=fig_num, dpi=100, facecolor='w', edgecolor='k')
        if isinstance(fig_title, str):
            self.fig.canvas.set_window_title(fig_title)
            self.fig_title = fig_title
        else:
            self.fig_title = str(id(self))

        self.ax = dict()

    def add_ax(self, ax_name, location: tuple):
        if not isinstance(location, tuple) or len(location) != 3:
            raise TypeError('Location must be a tuple with 3 elements!')

        self.ax[ax_name] = self.fig.add_subplot(*location)

    def save_to_file(self, directory, filename, size=(20, 10), dpi=300):
        orig_size = self.fig.get_size_inches()
        orig_dpi = self.fig.get_dpi()

        # make image bigger when saving to image
        self.fig.set_size_inches(size[0], size[1])
        self.fig.set_dpi(dpi)

        # save figure
        save(self.fig, directory=directory, filename=filename)

        # change back to original size
        self.fig.set_size_inches(orig_size[0], orig_size[1])
        self.fig.set_dpi(orig_dpi)


def plot_stay_up():
    plt.show(block=True)


def plot_evolution(ax: axes.Axes, y, x=None, **plot_config):

    # default config
    config = defaultdict(lambda: None)
    config['xlabel'] = 'time'
    for key, value in plot_config.items():
        config[key] = value

    # plotting the graph
    if x is None:
        x = np.arange(len(y))

    # check if element of x is tuple or just number
    lines = []
    if isinstance(y[0], (list, tuple)):
        for y_i in zip(*y):
            line, = ax.plot(x, y_i)
            lines.append(line)
    else:
        line, = ax.plot(x, y)
        lines.append(line)

    apply_plot_config(ax, config)

    return lines


def plot_regional_evolution(ax: axes.Axes, y, x=None, **plot_config):

    # default config
    config = defaultdict(lambda: None)
    config['xlabel'] = 'time'
    config['colourmap'] = 'prism'
    for key, value in plot_config.items():
        config[key] = value

    # plotting the graph
    if x is None:
        x = np.arange(len(y))

    # separating out the data for each region
    region_data = defaultdict(list)
    for i in range(len(y)):
        for region_id in y[i].keys():
            region_data[region_id].append((x[i], y[i][region_id]))

    # set the colour mapping for region ids
    region_ids = sorted(tuple(region_data.keys()))
    colours = plt.get_cmap(config['colourmap'])(np.linspace(0, 1.0, len(region_ids)))

    lines = []
    for i, data_i in region_data.items():
        x_i, y_i = tuple(zip(*data_i))
        line, = ax.plot(x_i, y_i)
        line.set_color(colours[region_ids.index(i)])
        lines.append(line)

    apply_plot_config(ax, config)

    return lines, region_ids


def plot_exemplars(ax: axes.Axes, y, x=None, **plot_config):
    # default config
    config = defaultdict(lambda: None)
    config['xlabel'] = 'time'
    config['colourmap'] = 'prism'
    for key, value in plot_config.items():
        config[key] = value

    # plotting the graph
    if x is None:
        x = np.arange(len(y))




def plot_model():
    pass

def apply_plot_config(ax: axes.Axes, config):

    # set label
    ax.set_title(config['title'])
    ax.set_xlabel(config['xlabel'])
    ax.set_ylabel(config['ylabel'])

    # set limit
    ax.set_ylim(config['ylim'])
    ax.set_xlim(config['xlim'])

    # set tick
    if config['int_yaxis']:
        ax.get_yaxis().set_major_locator(plt.MaxNLocator(integer=True))
    if config['int_xaxis']:
        ax.get_xaxis().set_major_locator(plt.MaxNLocator(integer=True))

    # line style
    if config['linestyle'] is not None:
        for line in ax.lines:
            try:
                line.set_linestyle(config['linestyle'])
            except:
                pass

    # marker style
    if config['marker'] is not None:
        for line in ax.lines:
            try:
                line.set_marker(config['marker'])
            except:
                pass

def to_time_value(time_delta: timedelta, time_type='second'):
    if time_type is 'day':
        time = time_delta.days + time_delta.seconds/86400 + time_delta.microseconds/8.64e10
    elif time_type is 'hour':
        time = time_delta.days/24 + time_delta.seconds/3600 + time_delta.microseconds/3.6e9
    elif time_type is 'minute':
        time = time_delta.days*1440 + time_delta.seconds/60 + time_delta.microseconds/6e7
    else:
        time = time_delta.days*86400 + time_delta.seconds + time_delta.microseconds*1e-6

    return time
__author__ = 'Matthew'
from collections import defaultdict
from datetime import timedelta
import os
import math

import matplotlib.pyplot as plt
import matplotlib.axes as axes
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from save_figure import save
from data_logger import DataLogger


class DataPlotter(object):

    colour_map = 'Set1'
    saved_figures_dir = os.path.join(os.getcwd(), 'saved_figures')

    def __init__(self, log_dir, log_header=None, log_timestamp=None, log_name=None,
                 packet_types=(DataLogger.packet_default_type, )):

        self.log_dict, self.log_name = DataLogger.retrieve_data(log_dir=log_dir, log_header=log_header,
                                                                log_timestamp=log_timestamp, log_name=log_name)

        self.plotting_packet_types = packet_types
        # all data
        self.data = defaultdict(lambda: defaultdict(lambda: {'x': [], 'y': []}))
        # state info
        self.state_info = defaultdict(dict)

        # extracting data and state info
        self._extract_data_files(self.plotting_packet_types)

        # plot objects
        self.plot_objects = dict()
        self._construct_plot_objects()

    def _construct_plot_objects(self):

        for node_name, node_data in self.data.items():

            self.plot_objects[(node_name, 'history')] = PlotObject(fig_title='History Plot - %s' % node_name)

    def _extract_data_files(self, packet_types):

        for session_data in self.log_dict:

            session_clock0 = session_data[DataLogger.session_clock0_key]

            for node_name, node_data in session_data.items():

                if node_name == 'session_id':
                    print(node_name)

                for packet_type in packet_types:

                    # if the node_data has the desired 'packet_type'
                    if isinstance(node_data, dict) and packet_type in node_data:
                        data_blocks = node_data[packet_type]

                        data_array = []
                        for data_block in data_blocks.values():
                            # chaining data blocks
                            data_array += data_block

                        # sort the array by time
                        data_array = sorted(data_array, key=lambda x: x[DataLogger.packet_time_key])

                        for packet in data_array:

                            packet_time = packet[DataLogger.packet_time_key]

                            for data_type, data_val in packet.items():
                                self.data[node_name][data_type]['y'].append(data_val)
                                self.data[node_name][data_type]['x'].append(packet_time - session_clock0)

                        for data_type, data_element in self.data[node_name].items():
                            print('Extracted %s --- %s' % (node_name, data_type))
                            # print(self.data[node_name][data_type]['y'][100])

    def plot(self):
        self.plot_histories()

    def plot_histories(self):

        grid_num_row = 2

        exclusion_list = ('packet_time', 'step', 'packet_type')

        for node_name, node_data in self.data.items():

            plot_order_list = sorted(node_data.keys())
            for exclude_type in exclusion_list:
                try:
                    plot_order_list.remove(exclude_type)
                except (AttributeError, ValueError):
                    pass

            grid_dim = (grid_num_row, math.ceil(len(plot_order_list)/grid_num_row))

            for data_type, data_val in node_data.items():

                if not data_type in plot_order_list:
                    continue

                # instantiate axis
                ax_name = '%s' % data_type
                ax_num = plot_order_list.index(data_type) + 1

                self.plot_objects[(node_name, 'history')].add_ax(ax_name=ax_name,
                                                                 location=(grid_dim[0], grid_dim[1], ax_num))

                # configure the plot
                plot_config = dict()
                plot_config['xlabel'] = 'time (minute)'
                plot_config['ylabel'] = 'value'
                plot_config['title'] = '%s vs. time plot' % data_type

                # plot the evolution plot
                try:
                    PlotObject.plot_evolution(self.plot_objects[(node_name, 'history')].ax[ax_name], data_val['y'], data_val['x'], **plot_config)
                except Exception:
                    pass
                else:
                    print('%s: plotted evolution of %s' % (node_name, data_type))

    def show_plots(self, plot_names=None, plot_stay=True):

        if plot_names is None:
            plt.show(block=plot_stay)
        else:
            for plot_name in plot_names:
                self.plot_objects[plot_name].fig.show()

    def update_plot(self):

        self._extract_data_files(self.plotting_packet_types)
        self.plot()


    def save_all_plots(self, sub_folder_name):
        directory = os.path.join(self.saved_figures_dir, sub_folder_name)
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

    def add_ax(self, ax_name, location: tuple, in_3d: bool=False):
        if not isinstance(location, tuple) or len(location) != 3:
            raise TypeError('Location must be a tuple with 3 elements!')

        if in_3d:
            projection = '3d'
        else:
            projection = None

        self.ax[ax_name] = self.fig.add_subplot(*location, projection=projection)

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

    @staticmethod
    def plot_stay_up():
        plt.show(block=True)

    @classmethod
    def plot_evolution(cls, ax: axes.Axes, y, x=None, **plot_config):

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

        PlotObject.apply_plot_config(ax, config)

        return lines

    @classmethod
    def apply_plot_config(cls, ax: axes.Axes, config):

        # set label
        ax.set_title(config['title'])
        ax.set_xlabel(config['xlabel'])

        if isinstance(ax, Axes3D):
            ax.set_zlabel(config['ylabel'])
            ax.set_ylabel(config['x2label'])
        else:
            ax.set_ylabel(config['ylabel'])

        # set limit
        ax.set_xlim(config['xlim'])

        if isinstance(ax, Axes3D):
            ax.set_zlim(config['ylim'])
            ax.set_ylim(config['x2lim'])
        else:
            ax.set_ylim(config['ylim'])

        # set tick
        if config['int_xaxis']:
            ax.get_xaxis().set_major_locator(plt.MaxNLocator(integer=True))
        if config['int_yaxis']:
            if isinstance(ax, Axes3D):
                ax.get_zaxis().set_major_locator(plt.MaxNLocator(integer=True))
            else:
                ax.get_yaxis().set_major_locator(plt.MaxNLocator(integer=True))
        if config['int_x2axis']:
            if isinstance(ax, Axes3D):
                ax.get_yaxis().set_major_locator(plt.MaxNLocator(integer=True))
            else:
                pass

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

        # marker size
        if config['markersize'] is not None:
            for line in ax.lines:
                try:
                    line.set_markersize(config['markersize'])
                except:
                    pass

            for line in ax.collections:
                try:
                    line.set_lw(config['markersize'])
                except:
                    pass

        # markert edge
        if config['marker_edge_width'] is not None and isinstance(config['marker_edge_width'], (float, int)):
            marker_edge_width = config['marker_edge_width']
        else:
            marker_edge_width = 0.01

        for line in ax.lines:
            try:
                line.set_markeredgewidth(marker_edge_width)
            except:
                pass

    @staticmethod
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


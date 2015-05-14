from collections import defaultdict
from datetime import timedelta
import os

import matplotlib.pyplot as plt
import matplotlib.axes as axes
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from .save_figure import save


colour_map = 'Set1'

class Plotter(object):

    def __init__(self, data_file=None):

        # all data
        self.data = defaultdict(lambda: defaultdict(lambda: {'x': [], 'y': []}))
        # state info
        self.state_info = defaultdict(dict)

        # extracting data and state info
        if data_file:
            self.extract_data_files(data_file)
        # plot objects
        self.plot_objects = dict()
        self.__construct_plot_objects()

    def __construct_plot_objects(self):

        for node_name in self.data.keys():
            self.plot_objects[(node_name, 'history')] = PlotObject(fig_title='History Plot - %s' % node_name)
            self.plot_objects[(node_name, 'regions_snapshot')] = PlotObject(fig_title='Regions Snapshots - %s' % node_name)
            self.plot_objects[(node_name, 'model')] = PlotObject(fig_title='Final Expert Model - %s' % node_name)

    def plot(self):
        self.plot_histories()
        self.plot_regions(tentacle_plot_dim=(2, 1, 0), protocell_plot_dim=(2, 0, 0))
        self.plot_models(tentacle_plot_dim=(2, 1, 0), protocell_plot_dim=(2, 0, 0))

    def plot_histories(self):

        grid_dim = (2, 4)
        engine_based_type = ('S', 'M', 'best_action', 'in_idle_mode',) #, 'is_exploring', 'S1_predicted',)
        expert_based_type = ('action_values', 'mean_errors', 'action_counts', 'latest_rewards',)

        for node_name, node_data in self.data.items():

            if (node_name, 'history') not in self.plot_objects:
                continue

            for data_type, data_val in node_data.items():

                # cbla_engine-based data
                if data_type in engine_based_type:

                    # instantiate axis
                    ax_name = '%s' % data_type
                    ax_num = engine_based_type.index(data_type) + 1
                    self.plot_objects[(node_name, 'history')].add_ax(ax_name=ax_name,
                                                                     location=(grid_dim[0], grid_dim[1], ax_num))

                    # configure the plot
                    plot_config = dict()
                    plot_config['xlabel'] = 'time (minute)'
                    plot_config['ylabel'] = 'value'
                    plot_config['title'] = '%s vs. time plot' % data_type

                    # special configurations
                    if data_type in ('in_idle_mode', 'is_exploring'):
                        plot_config['int_yaxis'] = True
                        plot_config['ylim'] = (-0.5, 1.5)
                        plot_config['linestyle'] = ' '
                        plot_config['marker'] = '.'
                    elif data_type in ('M', 'best_action') :
                        plot_config['int_yaxis'] = True
                        plot_config['linestyle'] = ' '
                        plot_config['marker'] = '.'
                        if 'tentacle' in node_name:
                            plot_config['ylim'] = (-0.5, 3.5)
                    elif data_type in ('S', 'S1'):
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
                    plot_regional_evolution(self.plot_objects[(node_name, 'history')].ax[ax_name],
                                            data_val['y'], data_val['x'], **plot_config)

                    print('%s: plotted regional evolution of %s' % (node_name, data_type))

    def plot_regions(self, **config):

        grid_dim = (2, 2)
        snapshot_num = 4
        snapshot_num = max(2, snapshot_num)  # making sure that it's over 2

        exemplars_plot_dim = defaultdict(lambda: (0, 0))

        for config_key, config_val in config.items():
            if 'plot_dim' in config_key and isinstance(config_val, tuple):
                exemplars_plot_dim[config_key.replace('_plot_dim', '')] = config_val

        for node_name, node_data in self.data.items():

            if (node_name, 'regions_snapshot') not in self.plot_objects:
                continue

            # plotting the exemplars in the region
            if 'exemplars' not in node_data.keys():
                continue

            # specify the dimensions to plot
            plot_dims = exemplars_plot_dim['default']
            for node_type in exemplars_plot_dim.keys():
                if node_type in node_name:
                    plot_dims = exemplars_plot_dim[node_type]

            exemplars_snapshots = node_data['exemplars']
            selected_snapshot_ids = [0]

            # select only certain number of snapshots
            try:
                total_snapshot_num = len(exemplars_snapshots['x'])
            except KeyError:
                continue
            num_middle = snapshot_num - 2
            if num_middle > 0:
                for i in range(num_middle):
                    selected_snapshot_ids.append(int((i+1)*total_snapshot_num/snapshot_num))
            selected_snapshot_ids.append(total_snapshot_num-1)
            selected_snapshot_ids = tuple(sorted(set(selected_snapshot_ids)))

            # instantiate axis
            ax_num = 1
            in_3d = False
            if len(plot_dims) > 2:
                in_3d = True

            for i in selected_snapshot_ids:

                # add axis to the plot object
                ax_name = 'Exemplars at t = %f' % exemplars_snapshots['x'][i]
                self.plot_objects[(node_name, 'regions_snapshot')].add_ax(ax_name=ax_name,
                                                                          location=(grid_dim[0], grid_dim[1], ax_num),
                                                                          in_3d=in_3d)

                # construct the data set for scatter plotting
                scatter_plot_data = defaultdict(list)
                for region_id, region_exemplars in exemplars_snapshots['y'][i].items():

                    data_pts = list(zip(*region_exemplars[0]))
                    label_pts = list(zip(*region_exemplars[1]))

                    # x-axis
                    try:
                        SM_data = tuple(data_pts[plot_dims[0]])
                    except IndexError:
                        print('SM(t) does not have dimension %d' % plot_dims[0])
                        break

                    # y-axis
                    try:
                        S1_data = tuple(label_pts[plot_dims[-1]])
                    except IndexError:
                        print('S(t+1) does not have dimension %d' % plot_dims[-1])
                        break

                    # x2-axis if 3d
                    if len(plot_dims) > 2:
                        try:
                            SM_data_2 = tuple(data_pts[plot_dims[1]])
                        except IndexError:
                            print('SM(t) does not have dimension %d' % plot_dims[1])
                            break
                        scatter_plot_data[region_id] = (SM_data, SM_data_2, S1_data)
                    else:
                        scatter_plot_data[region_id] = (SM_data, S1_data)

                # configure the plot
                plot_config = dict()
                if 'input_label_name' in self.state_info[node_name] and 'output_label_name' in self.state_info[node_name]:
                    labels = self.state_info[node_name]['input_label_name'] + self.state_info[node_name]['output_label_name']
                    plot_config['xlabel'] = labels[plot_dims[0]]
                    plot_config['x2label'] = labels[plot_dims[1]]
                else:
                    plot_config['xlabel'] = 'SM(t) [%d]' % plot_dims[0]
                    plot_config['x2label'] = 'SM(t) [%d]' % plot_dims[1]

                if 'output_label_name' in self.state_info[node_name]:
                    plot_config['ylabel'] = self.state_info[node_name]['input_label_name'][plot_dims[-1]]
                else:
                    plot_config['ylabel'] = 'S(t+1) [%d]' % plot_dims[-1]
                plot_config['title'] = 'Exemplars plot at t = %.2f' % exemplars_snapshots['x'][i]

                plot_config['int_xaxis'] = True
                plot_config['linestyle'] = ''
                plot_config['marker'] = 'o'

                # special configuration for tentacle nodes only
                if 'tentacle' in node_name:
                    plot_config['xlim'] = (-0.5, 3.5)

                # plot the exemplars
                plot_regional_points(self.plot_objects[(node_name, 'regions_snapshot')].ax[ax_name],
                                     region_data=scatter_plot_data, **plot_config)

                print('%s: plotted exemplars at t = %.2f' % (node_name, exemplars_snapshots['x'][i]))

                ax_num += 1

    def plot_models(self, **config):

        grid_dim = (1, 1)

        exemplars_plot_dim = defaultdict(lambda: (0, 0))

        for config_key, config_val in config.items():
            if '_plot_dim' in config_key and isinstance(config_val, tuple):
                exemplars_plot_dim[config_key.replace('_plot_dim', '')] = config_val



        for node_name, node_states in self.state_info.items():

            if (node_name, 'model') not in self.plot_objects:
                continue

            if 'learner_expert' not in node_states.keys():
                continue

            expert = node_states['learner_expert']


            # extract the exemplars
            info = defaultdict(dict)
            expert.save_expert_info(info, include_exemplars=True)
            exemplars_data = info['exemplars']
            prediction_model = info['prediction_model']

            # specify the dimensions to plot
            plot_dims = exemplars_plot_dim['default']
            for node_type in exemplars_plot_dim.keys():
                if node_type in node_name:
                    plot_dims = exemplars_plot_dim[node_type]

            in_3d = False
            if len(plot_dims) > 2:
                in_3d = True

            # add axis to the plot object
            ax_name = 'Expert Model for %s' % node_name
            ax_num = 1
            self.plot_objects[(node_name, 'model')].add_ax(ax_name=ax_name,
                                                           location=(grid_dim[0], grid_dim[1], ax_num),
                                                           in_3d=in_3d)


            # construct the data set for scatter plotting
            scatter_plot_data = dict()
            model_func = dict()
            for region_id, region_exemplars in exemplars_data.items():
                data_pts = list(zip(*region_exemplars[0]))
                label_pts = list(zip(*region_exemplars[1]))

                # x-axis
                try:
                    SM_data = tuple(data_pts[plot_dims[0]])
                except IndexError:
                    print('SM(t) does not have dimension %d' % plot_dims[0])
                    break

                # y-axis
                try:
                    S1_data = tuple(label_pts[plot_dims[-1]])
                except IndexError:
                    print('S(t+1) does not have dimension %d' % plot_dims[-1])
                    break

                # x2-axis if 3d
                if len(plot_dims) > 2:
                    try:
                        SM_data_2 = tuple(data_pts[plot_dims[1]])
                    except IndexError:
                        print('SM(t) does not have dimension %d' % plot_dims[1])
                        break
                    scatter_plot_data[region_id] = (SM_data, SM_data_2, S1_data)
                else:
                    scatter_plot_data[region_id] = (SM_data, S1_data)

                model_func[region_id] = prediction_model[region_id].predict

            # configure the plot
            plot_config = dict()
            if 'input_label_name' in self.state_info[node_name] and 'output_label_name' in self.state_info[node_name]:
                labels = self.state_info[node_name]['input_label_name'] + self.state_info[node_name][
                    'output_label_name']
                plot_config['xlabel'] = labels[plot_dims[0]]
                plot_config['x2label'] = labels[plot_dims[1]]
            else:
                plot_config['xlabel'] = 'SM(t) [%d]' % plot_dims[0]
                plot_config['x2label'] = 'SM(t) [%d]' % plot_dims[1]

            if 'output_label_name' in self.state_info[node_name]:
                plot_config['ylabel'] = self.state_info[node_name]['input_label_name'][plot_dims[-1]]
            else:
                plot_config['ylabel'] = 'S(t+1) [%d]' % plot_dims[-1]

            plot_config['int_xaxis'] = True
            plot_config['linestyle'] = ''
            plot_config['marker'] = 'o'

            # special configuration for tentacle nodes only
            if 'tentacle' in node_name:
                plot_config['xlim'] = (-0.5, 3.5)

            # plot the exemplars
            plot_expert_model(self.plot_objects[(node_name, 'model')].ax[ax_name],
                              region_data=scatter_plot_data, region_model_func=model_func, **plot_config)

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
                    # self.data[node_name][data_type]['x'].append(packet['step'])
                    self.data[node_name][data_type]['x'].append(to_time_value(packet['time'] - t0, 'minute'))

            for data_type, data_element in self.data[node_name].items():
                print('Extracted %s --- %s' % (node_name, data_type))
                # print(self.data[node_name][data_type]['y'][100])

        for node_name, raw_state in data_file['state'].items():
            self.state_info[node_name].update(raw_state)

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
    config['colourmap'] = colour_map
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


def plot_regional_points(ax: axes.Axes, region_data, **plot_config):

    # default config
    config = defaultdict(lambda: None)
    config['colourmap'] = colour_map
    config['marker'] = 'o'
    config['linestyle'] = ''
    config['markersize'] = 3
    for key, value in plot_config.items():
        config[key] = value

    # set the colour mapping for region ids
    region_ids = sorted(tuple(region_data.keys()))
    colours = plt.get_cmap(config['colourmap'])(np.linspace(0, 1.0, len(region_ids)))

    all_dots = []
    for i, data_i in region_data.items():

        dots, = ax.plot(*data_i)
        # dots = ax.scatter(x_i, y_i)
        dots.set_color(colours[region_ids.index(i)])
        all_dots.append(dots)

    apply_plot_config(ax, config)


def plot_regions_tree():
    pass


def plot_expert_model(ax: axes.Axes, region_data, region_model_func=None, **plot_config):
    # TODO still needs to actually plot the model
    plot_regional_points(ax, region_data, **plot_config)


def apply_plot_config(ax: axes.Axes, config):

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
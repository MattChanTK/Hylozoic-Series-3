__author__ = 'Matthew'

from abstract_node.data_plotter import *
import matplotlib.axes as axes


class CBLA_DataPlotter(DataPlotter):

    saved_figures_dir = 'cbla_saved_figures'

    def __init__(self, log_dir, log_header=None, log_timestamp=None, log_name=None,
                 packet_types=(DataLogger.packet_default_type, ),
                 info_types=(DataLogger.info_default_type,)):

        self.metrics = [] # session (list) -> node (dict) -> metrics (dict)

        super(CBLA_DataPlotter, self).__init__(log_dir=log_dir, log_header=log_header,
                                               log_timestamp=log_timestamp, log_name=log_name,
                                               packet_types=packet_types, info_types=info_types)

    def _construct_plot_objects(self):

        session_num = 1
        for session_data in self.data:
            for node_name, node_data in session_data.items():

                self.plot_objects[(session_num, node_name, 'history')] = CBLA_PlotObject(fig_title='History Plot - %s (S%d)' % (node_name, session_num))
                # self.plot_objects[(session_num, node_name, 'regions_snapshot')] = CBLA_PlotObject(fig_title='Regions Snapshots - %s' % node_name)
            session_num += 1

        # for node_name, node_data in self.data[-1]:
            # self.plot_objects[(node_name, 'model')] = CBLA_PlotObject(fig_title='Final Expert Model - %s' % node_name)

    def plot(self):
        self.compute_metrics()

        # self.plot_histories()
        # self.plot_regions(plot_dim=(3, 0))
        # self.plot_models(_plot_dim=(3, 0))

        session_num = 1
        for session_metrics in self.metrics:

            print('Session %d' % (session_num))
            for metric_type, metric in session_metrics.items():
                print('\t%s: %f' % (metric_type, metric))

            session_num += 1

    def compute_metrics(self):

        session_num = 1
        for session_data in self.data:

            session_metric = dict()
            session_variables = defaultdict(lambda: defaultdict(None))

            for node_name, node_data in session_data.items():

                if (session_num, node_name, 'history') not in self.plot_objects:
                    continue

                for data_type, data_val in node_data.items():

                    # M value for each node
                    if data_type == 'M':

                        normed_data_val = []
                        for data_point in data_val['y']:
                            normed_data_val.append(np.linalg.norm(data_point))

                        node_activation = np.mean(normed_data_val)
                        session_variables[node_name]['node_activation'] = node_activation

            # total activation - average activation among all nodes
            total_activation = []
            for node_variables in session_variables.values():
                total_activation.append(node_variables['node_activation'])
            total_activation = np.mean(total_activation)

            session_metric['total_activation'] = total_activation

            # proximal activation - average distance-weighted activation among all nodes


            self.metrics.append(session_metric)
            session_num += 1

    def plot_histories(self):

        grid_dim = (2, 4)
        engine_based_type = ('S', 'M', 'best_action', 'in_idle_mode',) #, 'is_exploring', 'S1_predicted',)
        expert_based_type = ('action_values', 'mean_errors', 'action_counts', 'latest_rewards',)

        session_num = 1
        for session_data in self.data:
            for node_name, node_data in session_data.items():

                if (session_num, node_name, 'history') not in self.plot_objects:
                    continue

                for data_type, data_val in node_data.items():

                    # cbla_engine-based data
                    if data_type in engine_based_type:

                        # instantiate axis
                        ax_name = '%s' % data_type
                        ax_num = engine_based_type.index(data_type) + 1
                        self.plot_objects[(session_num, node_name, 'history')].add_ax(ax_name=ax_name,
                                                                                      location=(grid_dim[0], grid_dim[1], ax_num))

                        # configure the plot
                        plot_config = dict()
                        plot_config['xlabel'] = 'time (second)'
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
                        CBLA_PlotObject.plot_evolution(self.plot_objects[(session_num, node_name, 'history')].ax[ax_name], data_val['y'], data_val['x'], **plot_config)

                        print('%s: plotted evolution of %s (S%d)' % (node_name, data_type, session_num))

                    # expert-based data
                    elif data_type in expert_based_type:

                        # instantiate axis
                        ax_name = '%s' % data_type
                        ax_num = len(engine_based_type) + expert_based_type.index(data_type) + 1
                        self.plot_objects[(session_num, node_name, 'history')].add_ax(ax_name=ax_name,
                                                                                      location=(grid_dim[0], grid_dim[1], ax_num))

                        # configure the plot
                        plot_config = dict()
                        plot_config['xlabel'] = 'time (second)'
                        plot_config['ylabel'] = 'value'
                        plot_config['title'] = '%s vs. time plot' % data_type

                        # plot the evolution plot
                        CBLA_PlotObject.plot_regional_evolution(self.plot_objects[(session_num, node_name, 'history')].ax[ax_name],
                                                                data_val['y'], data_val['x'], **plot_config)

                        print('%s: plotted regional evolution of %s (S%d)' % (node_name, data_type, session_num))

            session_num += 1

    def plot_regions(self, **config):

        grid_dim = (2, 2)
        snapshot_num = 4
        snapshot_num = max(2, snapshot_num)  # making sure that it's over 2

        exemplars_plot_dim = defaultdict(lambda: (0, 0))

        for config_key, config_val in config.items():
            if 'plot_dim' in config_key and isinstance(config_val, tuple):
                exemplars_plot_dim[config_key.replace('_plot_dim', '')] = config_val

        session_num = 1
        for session_data in self.data:
            for node_name, node_data in session_data.items():

                if (session_num, node_name, 'regions_snapshot') not in self.plot_objects:
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
                    self.plot_objects[(session_num, node_name, 'regions_snapshot')].add_ax(ax_name=ax_name,
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
                    CBLA_PlotObject.plot_regional_points(self.plot_objects[(session_num, node_name, 'regions_snapshot')].ax[ax_name],
                                                         region_data=scatter_plot_data, **plot_config)

                    print('%s: plotted exemplars at t = %.2f (S%d)' % (node_name, exemplars_snapshots['x'][i], session_num))

                    ax_num += 1

            session_num += 1

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
            CBLA_PlotObject.plot_expert_model(self.plot_objects[(node_name, 'model')].ax[ax_name],
                              region_data=scatter_plot_data, region_model_func=model_func, **plot_config)


class CBLA_PlotObject(PlotObject):

    @classmethod
    def plot_regional_evolution(cls, ax: axes.Axes, y, x=None, **plot_config):

        # default config
        config = defaultdict(lambda: None)
        config['xlabel'] = 'time'
        config['colourmap'] = cls.colour_map
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

        cls.apply_plot_config(ax, config)

        return lines, region_ids

    @classmethod
    def plot_regional_points(cls, ax: axes.Axes, region_data, **plot_config):

        # default config
        config = defaultdict(lambda: None)
        config['colourmap'] = cls.colour_map
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

        cls.apply_plot_config(ax, config)

    @classmethod
    def plot_expert_model(cls, ax: axes.Axes, region_data, region_model_func=None, **plot_config):
        # TODO still needs to actually plot the model
        cls.plot_regional_points(ax, region_data, **plot_config)

    @classmethod
    def plot_regions_tree(cls):
        pass

__author__ = 'Matthew'

import pickle
import glob
import os
import re
import Visualization as Viz
from copy import copy


teensy_names = ('HK_teensy_2_LED',)#'HK_teensy_2_SMA_0',
os.chdir("pickle_jar")

# search for all pickle files

file_names = []


for file in glob.glob("*.pkl"):
    try:
        file_names.append(file)
    except FileNotFoundError:
        continue


def visualize_CBLA(viz_data):


    # ------ plot the led/ambient light sensor data -------
    fig_num = 1
    name_list = []
    for name in viz_data.keys():
        type = re.split('_', name)[-1]

        if type == 'LED':
            name_list.append(copy(name))

    for name in name_list:

        expert = viz_data[name][0]
        action_history = viz_data[name][1]
        state_history = viz_data[name][2]
        mean_error_history = viz_data[name][3]

        expert.print()

        # find out what are the ids that existed
        region_ids = sorted(list(zip(*mean_error_history[-1]))[0])

        Viz.plot_expert_tree(expert, region_ids, filename=('Fig_' + str(fig_num)))
        Viz.plot_evolution(state_history, title='State vs Time', y_label='S(t)', fig_num=fig_num, subplot_num=261)
        Viz.plot_evolution(action_history, title='Action vs Time', marker_size=3, y_label='M(t)[0]', y_dim=0,
                           fig_num=fig_num, subplot_num=262)
        Viz.plot_model(expert, region_ids, x_idx=1, y_idx=0, fig_num=fig_num, subplot_num=263)
        Viz.plot_model(expert, region_ids, x_idx=0, y_idx=0, fig_num=fig_num, subplot_num=269)
        Viz.plot_regional_mean_errors(mean_error_history, region_ids, fig_num=fig_num, subplot_num=234)
        try:
            Viz.plot_model_3D(expert, region_ids, x_idx=(0, 1), y_idx=0, fig_num=fig_num, subplot_num=122)
        except Exception as e:
            print(e)

        fig_num += 1

    # ------- plot the tentacle/accelerometer data --------

    # find the names associated with the tentacle
    name_list = []
    for name in viz_data.keys():
        if 'SMA' in re.split('_', name):
            name_list.append(copy(name))

    for name in name_list:

        expert = viz_data[name][0]
        action_history = viz_data[name][1]
        state_history = viz_data[name][2]
        mean_error_history = viz_data[name][3]

        expert.print()

        # find out what are the ids that existed
        region_ids = sorted(list(zip(*mean_error_history[-1]))[0])

        Viz.plot_expert_tree(expert, region_ids, filename=('Fig_' + str(fig_num)))
        Viz.plot_evolution(state_history, title='State vs Time', y_label='S(t)', fig_num=fig_num, subplot_num=251)
        Viz.plot_evolution(action_history, title='Action vs Time', marker_size=3, y_label='M(t)[0]', y_dim=0,
                           fig_num=fig_num, subplot_num=252)
        # Viz.plot_model(expert, region_ids, x_idx=6, y_idx=0, fig_num=fig_num, subplot_num=253)
        # Viz.plot_model(expert, region_ids, x_idx=7, y_idx=1, fig_num=fig_num, subplot_num=254)
        # Viz.plot_model(expert, region_ids, x_idx=8, y_idx=2, fig_num=fig_num, subplot_num=255)


        Viz.plot_model(expert, region_ids, x_idx=4, y_idx=0, fig_num=fig_num, subplot_num=253)
        Viz.plot_model(expert, region_ids, x_idx=4, y_idx=1, fig_num=fig_num, subplot_num=254)
        Viz.plot_model(expert, region_ids, x_idx=4, y_idx=2, fig_num=fig_num, subplot_num=255)

        Viz.plot_regional_mean_errors(mean_error_history, region_ids, fig_num=fig_num, subplot_num=245)
        #
        # try:
        # Viz.plot_model_3D(expert, region_ids, x_idx=(6, 3), y_idx=0, fig_num=fig_num, subplot_num=246)
        # except Exception as e:
        #     print(e)
        #
        # try:
        #     Viz.plot_model_3D(expert, region_ids, x_idx=(7, 4), y_idx=1, fig_num=fig_num, subplot_num=247)
        # except Exception as e:
        #     print(e)
        # try:
        #     Viz.plot_model_3D(expert, region_ids, x_idx=(8, 5), y_idx=2, fig_num=fig_num, subplot_num=248)
        # except Exception as e:
        #     print(e)

        # try:
        #     Viz.plot_model_3D(expert, region_ids, x_idx=(0, 3), y_idx=0, fig_num=fig_num, subplot_num=246)
        # except Exception as e:
        #     print(e)
        #
        # try:
        #     Viz.plot_model_3D(expert, region_ids, x_idx=(1, 4), y_idx=1, fig_num=fig_num, subplot_num=247)
        # except Exception as e:
        #     print(e)
        # try:
        #     Viz.plot_model_3D(expert, region_ids, x_idx=(2, 5), y_idx=2, fig_num=fig_num, subplot_num=248)
        # except Exception as e:
        #     print(e)

        try:
            Viz.plot_model_3D(expert, region_ids, x_idx=(0, 4), y_idx=0, fig_num=fig_num, subplot_num=246)
        except Exception as e:
            print(e)

        try:
            Viz.plot_model_3D(expert, region_ids, x_idx=(1, 4), y_idx=1, fig_num=fig_num, subplot_num=247)
        except Exception as e:
            print(e)
        try:
            Viz.plot_model_3D(expert, region_ids, x_idx=(2, 4), y_idx=2, fig_num=fig_num, subplot_num=248)
        except Exception as e:
            print(e)

        fig_num += 1

    Viz.plot_show()


viz_data = dict()
for teensy_name in teensy_names:

    expert = None
    action_history = None
    state_history = None
    mearn_error_history = None

    for file in file_names:
        print(file)
        type = re.sub(teensy_name+'_', '', file)
        type = re.sub('.pkl', '', type)

        if type == 'expert_backup':
            with open (teensy_name+'_'+type+'.pkl', 'rb' ) as input:
                expert = pickle.load(input)
        elif type == 'action_history_backup':
            with open(teensy_name + '_' + type + '.pkl', 'rb') as input:
                action_history = pickle.load(input)
        elif type == 'state_history_backup':
            with open(teensy_name + '_' + type + '.pkl', 'rb') as input:
                state_history = pickle.load(input)
        elif type == 'mean_error_history_backup':
            with open(teensy_name + '_' + type + '.pkl', 'rb') as input:
                mean_error_history = pickle.load(input)

    try:
        viz_data[teensy_name] = [expert, action_history, state_history, mean_error_history]
    except NameError:
        pass

visualize_CBLA(viz_data)



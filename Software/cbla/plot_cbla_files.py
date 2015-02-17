__author__ = 'Matthew'

import pickle
import glob
import os
import re
from copy import copy
import numpy as np

import Visualization as Viz
from DataCollector import DataCollector


def main():

    os.chdir("pickle_jar")

    EXPERT_FILE_NAME = None #'cbla_data_15-02-11_21-35-54.pkl'
    time_range = -1

    try:
        if EXPERT_FILE_NAME is None:
            # get the newest file
            data_file_name = max(glob.iglob('cbla_data*.[Pp][Kk][Ll]'), key=os.path.getctime)
        else:
            data_file_name = EXPERT_FILE_NAME

    except FileNotFoundError:
        raise FileNotFoundError("Cannot find any data in %s" % os.getcwd())

    else:
        with open(data_file_name, 'rb') as input:
            data_import = pickle.load(input)

        try:
            data_collector = DataCollector(data_import)
        except TypeError:
            print("Invalid data format!")

    # iterate through the saved data
    viz_data = dict()
    for robot_name in data_collector.robot_names:
        print(robot_name)

        # extracting data
        expert = data_collector.get_element_val(robot_name, 'expert', index=time_range)
        # expert_time = data_collector.get_element_time(robot_name, 'expert', index=time_range)
        action_history = data_collector.get_named_var_data(robot_name, 'action', max_idx=time_range)
        prediction_history = data_collector.get_named_var_data(robot_name, 'prediction', max_idx=time_range)
        state_history = data_collector.get_named_var_data(robot_name, 'state', max_idx=time_range)
        error_history = data_collector.get_named_var_data(robot_name, 'mean_error', max_idx=time_range)['val']
        # error_history_time = data_collector.get_named_var_data(robot_name, 'mean_error', max_idx=time_range)['time']
        action_labels = data_collector.data_collection.get_robot_actuator_labels(robot_name)
        state_labels = data_collector.data_collection.get_robot_sensor_labels(robot_name)
        reward_history = data_collector.get_named_var_data(robot_name, 'reward', max_idx=time_range)['val']

        try:
            viz_data[robot_name] = [expert, action_history, state_history, error_history, action_labels, state_labels, reward_history]
        except NameError:
            pass
    file_name = re.sub('/.[pP][kK][lL]$', '', data_file_name)
    visualize_CBLA(viz_data, file_name)

def visualize_CBLA(viz_data, file_name=''):

    fig_num = 1
    # ------ plot the led/ambient light sensor data -------

    fig_num = _visualize_led_als(viz_data, fig_num, file_name)

    # ------- plot the tentacle/accelerometer data --------

    fig_num = _visualize_sma_acc(viz_data, fig_num, file_name)

    Viz.plot_show()

def _visualize_led_als(viz_data, fig_num=1, file_name=''):
    # ------ plot the led/ambient light sensor data -------
    fig_num = fig_num
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
        action_label = list(zip(*viz_data[name][4]))[1]
        state_label = list(zip(*viz_data[name][5]))[1]
        reward_history = viz_data[name][6]

        expert.print()

        # find out what are the ids that existed
        region_ids = sorted(list(zip(*mean_error_history[-1]))[0])

        Viz.plot_expert_tree(expert, region_ids, filename=(file_name + '_fig_' + str(fig_num)))
        Viz.plot_evolution(state_history['val'], time=None, title='State vs Time', y_label=state_label, fig_num=fig_num,
                           subplot_num=261)
        Viz.plot_evolution(action_history['val'], time=None, title='Action vs Time', marker_size=3,
                           y_label=action_label,
                           fig_num=fig_num, subplot_num=262)
        Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=1, y_idx=0, fig_num=fig_num,
                       subplot_num=263)
        # Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=0, y_idx=0, fig_num=fig_num, subplot_num=269)
        Viz.plot_regional_mean_errors(mean_error_history, region_ids, fig_num=fig_num, subplot_num=245)
        Viz.plot_evolution(zip(*[reward_history]), time=None, title='Reward vs Time', linestyle='-', y_label=['reward'],
                           fig_num=fig_num, subplot_num=246)

        try:
            Viz.plot_model_3D(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=(0, 1), y_idx=0,
                              fig_num=fig_num, subplot_num=122)
        except Exception as e:
            print(e)

        fig_num += 1

    return fig_num

def _visualize_sma_acc(viz_data, fig_num=1, file_name=''):
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
        action_label = list(zip(*viz_data[name][4]))[1]
        state_label = list(zip(*viz_data[name][5]))[1]
        reward_history = viz_data[name][6]

        expert.print()

        # find out what are the ids that existed
        region_ids = sorted(list(zip(*mean_error_history[-1]))[0])

        Viz.plot_expert_tree(expert, region_ids, filename=(file_name + '_fig_' + str(fig_num)))
        Viz.plot_evolution(state_history['val'], time=None, title='State vs Time', y_label=state_label, fig_num=fig_num,
                           subplot_num=221)
        Viz.plot_evolution(action_history['val'], time=None, title='Action vs Time', marker_size=3,
                           y_label=action_label,
                           fig_num=fig_num, subplot_num=222)
        # Viz.plot_model(expert, region_ids, x_idx=6, y_idx=0, fig_num=fig_num, subplot_num=253)
        # Viz.plot_model(expert, region_ids, x_idx=7, y_idx=1, fig_num=fig_num, subplot_num=254)
        # Viz.plot_model(expert, region_ids, x_idx=8, y_idx=2, fig_num=fig_num, subplot_num=255)


        # Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=4, y_idx=0, fig_num=fig_num, subplot_num=253, x_lim=(-1,4))
        # Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=4, y_idx=1, fig_num=fig_num, subplot_num=254, x_lim=(-1,4))
        # Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=4, y_idx=2, fig_num=fig_num, subplot_num=255, x_lim=(-1,4))

        Viz.plot_regional_mean_errors(mean_error_history, region_ids, fig_num=fig_num, subplot_num=223)
        Viz.plot_evolution(zip(*[reward_history]), time=None, title='Reward vs Time', linestyle='-', y_label='reward',
                           fig_num=fig_num, subplot_num=224)

        fig_num += 1

        try:
            Viz.plot_model_3D(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=(3, 4), y_idx=0,
                              fig_num=fig_num, subplot_num=131)
        except Exception as e:
            print(e)

        try:
            Viz.plot_model_3D(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=(3, 4), y_idx=1,
                              fig_num=fig_num, subplot_num=132)
        except Exception as e:
            print(e)
        try:
            Viz.plot_model_3D(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=(3, 4), y_idx=2,
                              fig_num=fig_num, subplot_num=133)
        except Exception as e:
            print(e)

        fig_num += 1
    return fig_num

if __name__ == "__main__":
    main()
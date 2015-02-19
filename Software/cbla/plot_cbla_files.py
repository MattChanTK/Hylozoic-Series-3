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

    EXPERT_FILE_NAME = None
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
            raise TypeError("Invalid data format!")

    # iterate through the saved data
    viz_data = dict()
    print("Robots in the data files:")
    for robot_name in data_collector.robot_names:
        print('\t' + robot_name)

        # extracting data in the right format
        viz_data[robot_name] = dict()

        # assigned data
        viz_data[robot_name]['expert'] = data_collector.get_assigned_element(robot_name, 'expert', 'val')
        viz_data[robot_name]['m label'] = data_collector.data_collection.get_robot_actuator_labels(robot_name)
        viz_data[robot_name]['s label'] = data_collector.data_collection.get_robot_sensor_labels(robot_name)

        # snapshot data
        viz_data[robot_name]['expert snapshot'] = data_collector.get_named_var_data(robot_name, 'expert history')['val']
        viz_data[robot_name]['region ids snapshot'] = data_collector.get_named_var_data(robot_name, 'region ids history')

        # continuous recording data
        viz_data[robot_name]['action'] = data_collector.get_named_var_data(robot_name, 'action', max_idx=time_range)
        viz_data[robot_name]['prediction'] = data_collector.get_named_var_data(robot_name, 'prediction', max_idx=time_range)
        viz_data[robot_name]['state'] = data_collector.get_named_var_data(robot_name, 'state', max_idx=time_range)
        viz_data[robot_name]['mean error'] = data_collector.get_named_var_data(robot_name, 'mean error', max_idx=time_range)['val']
        viz_data[robot_name]['action value'] = data_collector.get_named_var_data(robot_name, 'action value', max_idx=time_range)['val']
        viz_data[robot_name]['action count'] = data_collector.get_named_var_data(robot_name, 'action count', max_idx=time_range)['val']
        viz_data[robot_name]['reward'] = data_collector.get_named_var_data(robot_name, 'reward', max_idx=time_range)['val']
        viz_data[robot_name]['best action'] = data_collector.get_named_var_data(robot_name, 'best action', max_idx=time_range)['val']


    file_name = re.sub('/.[pP][kK][lL]$', '', data_file_name)
    #visualize_CBLA(viz_data, file_name)

    fig_num = 1
    fig_num = visualize_CBLA_exploration(viz_data, fig_num=fig_num)
    fig_num = visualize_CBLA_model(viz_data, fig_num=fig_num, file_name=file_name)
    Viz.plot_show()

def visualize_CBLA_exploration(viz_data, fig_num=1):

    fig_num = fig_num

    for name in viz_data.keys():

        if 'SMA' in re.split('_', name):
            type = 'SMA'
        elif 'LED' in re.split('_', name):
            type = 'LED'
        else:
            type = None

        expert = viz_data[name]['expert']
        action_history = viz_data[name]['action']
        state_history = viz_data[name]['state']
        mean_error_history = viz_data[name]['mean error']
        action_label = list(zip(*viz_data[name]['m label']))[1]
        state_label = list(zip(*viz_data[name]['s label']))[1]
        reward_history = viz_data[name]['reward']
        value_history = viz_data[name]['action value']
        action_count_history = viz_data[name]['action count']
        best_action_history = viz_data[name]['best action']

        # plot prediction error
        region_ids = sorted(list(zip(*mean_error_history[-1]))[0])
        Viz.plot_regional_mean_errors(mean_error_history, region_ids, fig_num=fig_num, subplot_num=231)

        # plot action value over time
        region_ids = sorted(list(zip(*value_history[-1]))[0])
        Viz.plot_regional_action_values(value_history, region_ids, fig_num=fig_num, subplot_num=232)

        # plot action count over time
        region_ids = sorted(list(zip(*action_count_history[-1]))[0])
        Viz.plot_regional_action_rate(action_count_history, region_ids, fig_num=fig_num, subplot_num=234)

        # plot best action over time
        Viz.plot_evolution(best_action_history, title='Best Action vs Time', y_label=('Best action',), marker_size=3, fig_num=fig_num, subplot_num=235)
        Viz.plot_evolution(action_history['val'], title='Best Action vs Time', y_label=('Selected action',), marker_size=3, fig_num=fig_num, subplot_num=235)

        # plot the model - 2D
        if type is 'LED':
            Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=1, y_idx=0,
                           fig_num=fig_num, subplot_num=133)
        elif type is 'SMA':
            Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=4, y_idx=0,
                           fig_num=fig_num, subplot_num=333)
            Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=4, y_idx=1,
                           fig_num=fig_num, subplot_num=336)
            Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=4, y_idx=2,
                           fig_num=fig_num, subplot_num=339)

        #plot the model - 3D
        # Viz.plot_model_3D(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=(0, 1), y_idx=0,
        #                    fig_num=fig_num, subplot_num=133)
        fig_num +=1

        print("Plotted %s's CBLA exploration graphs" % name)
    return fig_num

def visualize_CBLA_model(viz_data, fig_num=1, file_name=''):
    fig_num = fig_num

    for name in viz_data.keys():

        if 'SMA' in re.split('_', name):
            type = 'SMA'
        elif 'LED' in re.split('_', name):
            type = 'LED'
        else:
            type = None

        action_label = list(zip(*viz_data[name]['m label']))[1]
        state_label = list(zip(*viz_data[name]['s label']))[1]

        expert_history = viz_data[name]['expert snapshot']
        region_ids_history = viz_data[name]['region ids snapshot']

        if type == 'LED':
            for i in range(0, len(expert_history)):
                region_ids = sorted(region_ids_history['val'][i])
                time_step = region_ids_history['step'][i]

                Viz.plot_model(expert_history[i], region_ids, s_label=state_label, m_label=action_label, x_idx=1, y_idx=0,
                               fig_num=fig_num, subplot_num=(2, 4, i % 8 + 1), title='Prediction Models (t=%d)' % time_step)

                Viz.plot_expert_tree(expert_history[i], region_ids, folder_name=file_name,
                                     filename='%s_%d t=%d region' % (type, i, time_step))

                if (i + 1) % 8 == 0:
                    fig_num += 1

        elif type == 'SMA':

            for i in range(0, len(expert_history)):
                region_ids = sorted(region_ids_history['val'][i])
                time_step = region_ids_history['step'][i]

                Viz.plot_model(expert_history[i], region_ids, s_label=state_label, m_label=action_label, x_idx=4,
                               y_idx=0,
                               fig_num=fig_num, subplot_num=(3, 4, i % 4 + 1),
                               title='Prediction Models (t=%d)' % time_step)

                Viz.plot_model(expert_history[i], region_ids, s_label=state_label, m_label=action_label, x_idx=4,
                               y_idx=1,
                               fig_num=fig_num, subplot_num=(3, 4, i % 4 + 5),
                               title='Prediction Models (t=%d)' % time_step)

                Viz.plot_model(expert_history[i], region_ids, s_label=state_label, m_label=action_label, x_idx=4,
                               y_idx=2,
                               fig_num=fig_num, subplot_num=(3, 4, i % 4 + 9),
                               title='Prediction Models (t=%d)' % time_step)

                Viz.plot_expert_tree(expert_history[i], region_ids, folder_name=file_name,
                                     filename='%s_%d t=%d region' % (type, i, time_step))

                if (i + 1) % 4 == 0:
                    fig_num += 1
        fig_num += 1
        print("Plotted %s's CBLA model and tree evolution"%name)


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
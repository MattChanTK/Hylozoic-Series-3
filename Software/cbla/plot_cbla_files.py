__author__ = 'Matthew'

import pickle
import glob
import os
import re
from copy import copy
import numpy as np

import Visualization as Viz
from DataCollector import DataCollector
from save_figure import save


def main():

    os.chdir("pickle_jar")

    EXPERT_FILE_NAME = None #'cbla_data_15-03-02_22-16-41.pkl'
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
        with open(data_file_name, 'rb') as file_in:
            data_import = pickle.load(file_in)

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
        viz_data[robot_name]['m label'] = data_collector.get_robot_actuator_labels(robot_name)
        viz_data[robot_name]['s label'] = data_collector.get_robot_sensor_labels(robot_name)

        # snapshot data
        try:
            viz_data[robot_name]['exemplars snapshot'] = data_collector.get_named_var_data(robot_name, 'exemplars history')['val']
            viz_data[robot_name]['region ids snapshot'] = data_collector.get_named_var_data(robot_name, 'region ids history')
        except Exception:
            pass

        # continuous recording data
        viz_data[robot_name]['action'] = data_collector.get_named_var_data(robot_name, 'action', max_idx=time_range)
        viz_data[robot_name]['prediction'] = data_collector.get_named_var_data(robot_name, 'prediction', max_idx=time_range)
        viz_data[robot_name]['state'] = data_collector.get_named_var_data(robot_name, 'state', max_idx=time_range)
        viz_data[robot_name]['mean error'] = data_collector.get_named_var_data(robot_name, 'mean error', max_idx=time_range)
        viz_data[robot_name]['action value'] = data_collector.get_named_var_data(robot_name, 'action value', max_idx=time_range)
        viz_data[robot_name]['action count'] = data_collector.get_named_var_data(robot_name, 'action count', max_idx=time_range)
        viz_data[robot_name]['reward'] = data_collector.get_named_var_data(robot_name, 'reward', max_idx=time_range)['val']
        viz_data[robot_name]['best action'] = data_collector.get_named_var_data(robot_name, 'best action', max_idx=time_range)
        viz_data[robot_name]['idled'] = data_collector.get_named_var_data(robot_name, 'idled', max_idx=time_range)


    file_name = re.sub('/.[pP][kK][lL]$', '', data_file_name)
    #visualize_CBLA(viz_data, file_name)

    fig_num = 1
    # Viz.plot_ion()
    #fig_num = visualize_CBLA_idle_mode(viz_data, fig_num, file_name)
    fig_num = visualize_CBLA_exploration(viz_data, fig_num=fig_num, file_name=file_name)
    # # # input("press any key to plot the next graphs")
    # fig_num = visualize_CBLA_model(viz_data, fig_num=fig_num, file_name=file_name)
    Viz.plot_show(True)


def visualize_CBLA_exploration(viz_data, fig_num=1,file_name=''):

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
        region_ids = sorted(list(zip(*mean_error_history['val'][-1]))[0])
        Viz.plot_regional_mean_errors(mean_error_history['val'], region_ids, mean_error_history['time'],
                                      fig_num=fig_num, subplot_num=231)

        # plot action value over time
        region_ids = sorted(list(zip(*value_history['val'][-1]))[0])
        Viz.plot_regional_action_values(value_history['val'], region_ids, time=value_history['time'],
                                        fig_num=fig_num, subplot_num=232)

        # plot action count over time
        if type is 'LED':
            region_ids = sorted(list(zip(*action_count_history['val'][-1]))[0])
            Viz.plot_regional_action_rate(action_count_history['val'], region_ids, time=action_count_history['time'],
                                          fig_num=fig_num, subplot_num=234)


        if type is 'LED':
            # plot best action over time
            Viz.plot_evolution(best_action_history['val'], time=best_action_history['time'],
                               title='Best Action vs Time', y_label=('Best action',),
                               marker_size=3, fig_num=fig_num, subplot_num=235)
            Viz.plot_evolution(action_history['val'], time=action_history['time'],
                               title='Best Action vs Time', y_label=('Selected action',),
                               marker_size=3, fig_num=fig_num, subplot_num=235)

        elif type is 'SMA':
            # plot best action over time
            Viz.plot_evolution(best_action_history['val'], time=best_action_history['time'],
                               title='Best Action vs Time', y_label=('Best action',),
                               y_lim=(-1, 4), marker_size=6, fig_num=fig_num, subplot_num=235)
            Viz.plot_evolution(action_history['val'], time=action_history['time'],
                               title='Selected Action vs Time', y_label=('Selected action',),
                               y_lim=(-1, 4), marker_size=6, fig_num=fig_num, subplot_num=234)


        # plot the model - 2D
        if type is 'LED':
            Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, show_model=True,
                           x_idx=2, y_idx=0, fig_num=fig_num, subplot_num=133)

            # plot the model - 3D
            # Viz.plot_model_3D(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=(1, 2), y_idx=0,
            #                   fig_num=fig_num, subplot_num=133, data_only=False)
        elif type is 'SMA':
            Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, show_model=False,
                           x_idx=4, y_idx=0, x_lim=(-1, 4), fig_num=fig_num, subplot_num=333)
            Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, show_model=False,
                           x_idx=4, y_idx=1, x_lim=(-1, 4), fig_num=fig_num, subplot_num=336)
            Viz.plot_model(expert, region_ids, s_label=state_label, m_label=action_label, show_model=False,
                           x_idx=4, y_idx=2, x_lim=(-1, 4), fig_num=fig_num, subplot_num=339)

            folder = os.path.join(os.getcwd(), '%s figures' % file_name)
            save(os.path.join(folder, 'figure %d' % fig_num))
            fig_num += 1

            # # plot the model - 3D
            Viz.plot_model_3D(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=(3, 4), y_idx=0,
                               fig_num=fig_num, subplot_num=131, data_only=True)
            Viz.plot_model_3D(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=(3, 4), y_idx=1,
                              fig_num=fig_num, subplot_num=132, data_only=True)
            Viz.plot_model_3D(expert, region_ids, s_label=state_label, m_label=action_label, x_idx=(3, 4), y_idx=2,
                              fig_num=fig_num, subplot_num=133, data_only=True)

        folder = os.path.join(os.getcwd(), '%s figures' % file_name)
        save(os.path.join(folder, 'figure %d' % fig_num))
        fig_num += 1


        print("Plotted %s's CBLA exploration graphs" % name)
        Viz.plot_show()
        #input("press any key to plot the next robot")

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

        try:
            exemplars_history = viz_data[name]['exemplars snapshot']
            region_ids_history = viz_data[name]['region ids snapshot']
        except KeyError:
            continue

        if type == 'LED':
            subplot_num = 1
            for i in range(len(exemplars_history)):
            #for i in np.linspace(0, len(expert_history), int(min(len(expert_history), 8*3)), endpoint=False):
                i = int(i)
                region_ids = sorted(region_ids_history['val'][i])
                time_step = (region_ids_history['time'][i] - region_ids_history['time'][0]).total_seconds()

                Viz.plot_model(exemplars_history[i], region_ids, s_label=state_label, m_label=action_label,
                               show_model=True, model_intersect=150,
                               x_idx=2, y_idx=0, fig_num=fig_num, subplot_num=(2, 4, subplot_num),
                               title='Prediction Models (t=%d)' % time_step)


                if subplot_num >= 8:
                    folder = os.path.join(os.getcwd(), '%s figures' % file_name)
                    save(os.path.join(folder, 'figure %d' % fig_num))
                    fig_num += 1
                    subplot_num = 1
                else:
                    subplot_num += 1

        elif type == 'SMA':
            for i in range(len(exemplars_history)):
            #for i in np.linspace(0, len(exemplars_history), int(min(len(exemplars_history), 4 * 3)), endpoint=False):
                i = int(i)
                region_ids = sorted(region_ids_history['val'][i])
                time_step = (region_ids_history['time'][i] - region_ids_history['time'][0]).total_seconds()

                Viz.plot_model(exemplars_history[i], region_ids, s_label=state_label, m_label=action_label, show_model=False,
                               x_idx=4, y_idx=0, x_lim=(-1, 4), fig_num=fig_num, subplot_num=(3, 4, i % 4 + 1),
                               title='Prediction Models (t=%d)' % time_step)

                Viz.plot_model(exemplars_history[i], region_ids, s_label=state_label, m_label=action_label, show_model=False,
                               x_idx=4, y_idx=1,  x_lim=(-1, 4), fig_num=fig_num, subplot_num=(3, 4, i % 4 + 5),
                               title='Prediction Models (t=%d)' % time_step)

                Viz.plot_model(exemplars_history[i], region_ids, s_label=state_label, m_label=action_label, show_model=False,
                               x_idx=4, y_idx=2,  x_lim=(-1, 4), fig_num=fig_num, subplot_num=(3, 4, i % 4 + 9),
                               title='Prediction Models (t=%d)' % time_step)

                if (i + 1) % 4 == 0:
                    folder = os.path.join(os.getcwd(), '%s figures' % file_name)
                    save(os.path.join(folder, 'figure %d' % fig_num))
                    fig_num += 1


        print("Plotted %s's CBLA model and tree evolution" % name)
        Viz.plot_show()
        #input("press any key to plot the next robot")
        #Viz.plot_close()

        folder = os.path.join(os.getcwd(), '%s figures' % file_name)
        save(os.path.join(folder, 'figure %d' % fig_num))
        fig_num += 1

def visualize_CBLA_idle_mode(viz_data, fig_num=1,file_name=''):

    fig_num = fig_num

    for name in viz_data.keys():

        if 'SMA' in re.split('_', name):
            type = 'SMA'
            idle_mode_indicate = -1000
            y_lim = (-5000, 5000)
        elif 'LED' in re.split('_', name):
            type = 'LED'
            idle_mode_indicate = -400
            y_lim = (-600, 600)
        else:
            type = None
            idle_mode_indicate = -100
            y_lim = None


        action_history = viz_data[name]['action']
        value_history = viz_data[name]['action value']
        best_action_history = viz_data[name]['best action']
        idle_state_history = viz_data[name]['idled']


        # plot idle mode
        idle_mode = []

        for idling in idle_state_history['val']:

            if idling:
                idle_mode.append(idle_mode_indicate)
            else:
                idle_mode.append(None)


        Viz.plot_evolution(list(zip(idle_mode)), time=idle_state_history['time'],
                           title='', y_label=('',), y_lim=y_lim,
                           marker_size=3, fig_num=fig_num, subplot_num=111)


        # plot action value over time
        region_ids = sorted(list(zip(*value_history['val'][-1]))[0])
        Viz.plot_regional_action_values(value_history['val'], region_ids, time=value_history['time'],
                                        fig_num=fig_num, subplot_num=111)



        folder = os.path.join(os.getcwd(), '%s figures' % file_name)
        save(os.path.join(folder, 'figure %d' % fig_num))
        fig_num += 1


        print("Plotted %s's CBLA idle graphs" % name)
        Viz.plot_show()
        #input("press any key to plot the next robot")

    return fig_num


if __name__ == "__main__":
    main()
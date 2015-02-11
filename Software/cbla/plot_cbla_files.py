__author__ = 'Matthew'

import pickle
import glob
import os
import re
from copy import copy

import Visualization as Viz
from DataCollector import DataCollector


def main():

    os.chdir("pickle_jar")

    EXPERT_FILE_NAME = None

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
        expert = data_collector.get_element_val(robot_name, 'expert')
        action_history = list(zip(*data_collector.get_var_data(robot_name, 'action')))[0]
        prediction_history = list(zip(*data_collector.get_var_data(robot_name, 'prediction')))[0]
        state_history = list(zip(*data_collector.get_var_data(robot_name, 'state')))[0]
        error_history = list(zip(*data_collector.get_var_data(robot_name, 'mean_error')))[0]


        try:
            viz_data[robot_name] = [expert, action_history, state_history, error_history]
        except NameError:
            pass

    visualize_CBLA(viz_data)

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



if __name__ == "__main__":
    main()
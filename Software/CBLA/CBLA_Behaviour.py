import math
import random
from RegionsManager import Expert
from SimSystem import SimpleFunction as Robot
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pickle
import numpy as np
from copy import copy

import Visualization as Viz


if __name__ == "__main__":

    # number of time step
    sim_duration = 8000

    # use saved expert
    is_using_saved_expert = 0
    # initial actions
    Mi = ((0,),)

    # instantiate an Expert
    if is_using_saved_expert:
        with open('expert_backup.pkl', 'rb') as input:
            expert = pickle.load(input)
        with open('action_history_backup.pkl', 'rb') as input:
            action_history = pickle.load(input)
        with open('mean_error_history_backup.pkl', 'rb') as input:
            mean_error_history = pickle.load(input)
        with open('region_ids_history_backup.pkl', 'rb') as input:
            region_ids_history = pickle.load(input)

    else:
        expert = Expert()
        action_history = []
        mean_error_history = []
        region_ids_history = []

        # initial training action
        Mi = []
        for i in range(-70, 70):
            Mi.append((i,))
        Mi = tuple(Mi)


    # instantiate a Robot
    robot = Robot()


    # initial conditions
    t = 0
    S = (0,)
    M = Mi[0]
    exploring_rate = 0.2

    while t < sim_duration:
        t += 1

        print("\nTest case t =", t, " -- ", S, M)

        # have the expert make prediction
        S1_predicted = expert.predict(S, M)
        print("Predicted S1: ", S1_predicted)

        # do action
        action_history.append(M)
        robot.actuate(M)

        # read sensor
        S1 = robot.report()

        # add exemplar to expert
        expert.append(S + M, S1, S1_predicted)

        expert.split()  # won't actually split if the condition is not met


        # random action or the best action
        print("Exploring Rate: ", exploring_rate)
        is_exploring = (random.random() < exploring_rate)

        M1, L = expert.get_next_action(S1, is_exploring)

        print("Expected Reward", L)
        print("Next Action", M1)

        # record the mean errors of each region
        mean_errors = []
        region_ids = []
        expert.save_mean_errors(mean_errors, region_ids)
        mean_error_history.append(copy(mean_errors))
        region_ids_history.append(copy(region_ids))

        # set to current state

        S = S1
        if t < len(Mi):
            M = Mi[t]
        else:
            M = M1

        # update learning rate based on reward
        if L < 0.01:
            exploring_rate = 0.7
        if L > 10:
            exploring_rate = 0.2
        else:
            exploring_rate = -0.05*L + 0.7

        if t % 1000 == 0 or t >= sim_duration:
            with open('expert_backup.pkl', 'wb') as output:
                pickle.dump(expert, output, pickle.HIGHEST_PROTOCOL)

            with open('action_history_backup.pkl', 'wb') as output:
                pickle.dump(action_history, output, pickle.HIGHEST_PROTOCOL)

            with open('mean_error_history_backup.pkl', 'wb') as output:
                pickle.dump(mean_error_history, output, pickle.HIGHEST_PROTOCOL)

            with open('region_ids_history_backup.pkl', 'wb') as output:
                pickle.dump(region_ids_history, output, pickle.HIGHEST_PROTOCOL)


    expert.print()

    Viz.plot_evolution(action_history, fig_num=1, subplot_num=221)
    Viz.plot_model(expert, x_idx=1, y_idx=0, fig_num=1, subplot_num=222)
    Viz.plot_model(expert, x_idx=0, y_idx=0, fig_num=1, subplot_num=224)
    Viz.plot_regional_mean_errors(mean_error_history, region_ids_history, fig_num=1, subplot_num=223)
    plt.ioff()
    plt.show()


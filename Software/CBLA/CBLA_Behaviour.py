import math
import random
from RegionsManager import Expert
from SimSystem import SimpleFunction as Robot
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pickle
import numpy as np

import Visualization as Viz


if __name__ == "__main__":

    # number of time step
    sim_duration = 5000

    # use saved expert
    is_using_saved_expert = 1
    # initial actions
    Mi = ((0,),)

    # instantiate an Expert
    if is_using_saved_expert:
        with open('expert_backup.pkl', 'rb') as input:
            expert = pickle.load(input)
        with open('action_history_backup.pkl', 'rb') as input:
            action_history = pickle.load(input)
    else:
        expert = Expert()
        action_history = []

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

        if t % 1000 == 0:
            with open('expert_backup.pkl', 'wb') as output:
                pickle.dump(expert, output, pickle.HIGHEST_PROTOCOL)

            with open('action_history_backup.pkl', 'wb') as output:
                pickle.dump(action_history, output, pickle.HIGHEST_PROTOCOL)

    with open('expert_backup.pkl', 'wb') as output:
        pickle.dump(expert, output, pickle.HIGHEST_PROTOCOL)

    with open('action_history_backup.pkl', 'wb') as output:
        pickle.dump(action_history, output, pickle.HIGHEST_PROTOCOL)

    expert.print()

    Viz.plot_evolution(action_history)
    Viz.plot_model(expert)
    plt.ioff()
    plt.show()


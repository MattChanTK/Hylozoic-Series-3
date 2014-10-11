
import math
import random
from RegionsManager import Expert
from SimSystem import SimpleFunction as Robot
import matplotlib.pyplot as plt
import pickle

if __name__ == "__main__":

    # number of time step
    sim_duration = 3000

    # use saved expert
    is_using_saved_expert = 1

    # instantiate an Expert
    if is_using_saved_expert:
        with open('expert_backup.pkl', 'rb') as input:
            expert = pickle.load(input)
        with open('action_history_backup.pkl', 'rb') as input:
            action_history = pickle.load(input)
    else:
        expert = Expert()
        action_history = []

    # instantiate a Robot
    robot = Robot()

    # initial conditions
    t = 0
    S = (0,)
    M = (0,)



    while t < sim_duration:
        t += 1

        print("\nTest case t =",t, " -- ", S, M)

        # have the expert make prediction
        S1_predicted = expert.predict(S, M)
        print("Predicted S1: ", S1_predicted)

        # do action
        robot.actuate(M)

        # read sensor
        S1 = robot.report()

        # add exemplar to expert
        expert.append(S + M, S1, S1_predicted)

        expert.split()  # won't actually split if the condition is not met


        # random action or the best action
        dice = random.random()
        if dice < 0.2:
            M1 = (random.randrange(-100, 100),)
        else:
            M1, L = expert.get_next_action(S1)
            action_history.append(M1)
            print("Expected Reward", L)
        print("Next Action", M1)

        # set to current state
        S = S1
        M = M1

        if t % 1000 == 0:
            with open('expert_backup.pkl', 'wb') as output:
                pickle.dump(expert, output, pickle.HIGHEST_PROTOCOL)

            with open('action_history_backup.pkl', 'wb') as output:
                pickle.dump(action_history, output, pickle.HIGHEST_PROTOCOL)


    expert.print()
    plt.plot(action_history, 'b.')
    plt.show()


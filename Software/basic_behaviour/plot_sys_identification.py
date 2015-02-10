import pickle
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os
import numpy as np


ACC_MG_PER_LSB = 3.9
ADC_RES = 2**12

teensy_names = ('test_teensy_7', 'test_teensy_1',)
#teensy_names = ('HK_teensy_1','HK_teensy_2', 'HK_teensy_3')

curr_dir = os.getcwd()
os.chdir(os.path.join(curr_dir, "pickle_jar"))

figure_num = 1
for teensy_name in teensy_names:

    for j in range(4):
        filename = teensy_name + '_tentacle_' + str(j) + '_state_history.pkl'

        state = None
        try:
            with open(filename, 'rb') as input:
                try:
                    state = pickle.load(input)
                except EOFError:
                    continue
        except FileNotFoundError:
            continue

        state = list(zip(*state))
        time = state[0]
        action = state[1]
        cycling = state[2]
        ir_state = [np.array(state[3])/ADC_RES*100, np.array(state[4])/ADC_RES*100]

        # find the g-force per LSB (assume first 10 data points is zero G
        acc_state_raw_0 = [np.mean(np.array(state[5])[0:10]), np.mean(np.array(state[6])[0:10]), np.mean(np.array(state[7])[0:10])]
        acc_magnitude = np.sqrt((acc_state_raw_0[0] ** 2 + acc_state_raw_0[1] ** 2 + acc_state_raw_0[1] ** 2))
        ACC_MG_PER_LSB = 1000/acc_magnitude
        acc_state = [np.array(state[5]) * ACC_MG_PER_LSB, np.array(state[6]) * ACC_MG_PER_LSB,
                     np.array(state[7]) * ACC_MG_PER_LSB]
        acc_magnitude = np.sqrt((acc_state[0]**2+acc_state[1]**2+acc_state[1]**2))
        acc_state.append(acc_magnitude)
        #print(ACC_MG_PER_LSB)


        fig = plt.figure(figure_num)
        fig.suptitle(filename)

        # time vs action
        ax = fig.add_subplot(221)
        plt.title("Time vs Action")
        ax.plot(time, action)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xlabel('time(s)')
        plt.ylabel('action [0,1,2,3]')
        plt.ylim((-1, 4))



        # time vs cycling
        # ax = fig.add_subplot(222)
        # plt.title("Time vs Cycling")
        # ax.plot(time, cycling)
        # ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        # plt.xlabel('time(s)')
        # plt.ylabel('Cycle [0,1]')
        # plt.ylim((-1, 2))


        # time vs IR states
        ax = fig.add_subplot(223)
        plt.title("Time vs IR State")
        for j in range(len(ir_state)):
            ax.plot(time, ir_state[j], label='IR %d' %j)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xlabel('time(s)')
        plt.ylabel('percent max')
        plt.ylim(0, max(max(map(max, ir_state)), 100))


        ax = fig.add_subplot(122)
        plt.title("Time vs Accelerometer states")
        for j in range(len(acc_state)-1):
            ax.plot(time, acc_state[j], label='Acc %d' %j)
        ax.plot(time,acc_state[-1], label='Magnitude' )
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xlabel('time(s)')
        plt.ylabel('milli g-force')
        plt.ylim((min(list(map(min, acc_state)))-1, max(list(map(max, acc_state)))+1))

        figure_num += 1

    for j in range(1):
        filename = teensy_name + '_protocell_' + str(j) + '_state_history.pkl'

        state = None
        try:
            with open(filename, 'rb') as input:
                state = pickle.load(input)
        except FileNotFoundError:
            continue

        state = list(zip(*state))
        time = state[0]
        action = state[1]
        als_state = np.array(state[2])/ADC_RES*100


        fig = plt.figure(figure_num)
        fig.suptitle(filename)

        # time vs action
        ax = fig.add_subplot(121)
        plt.title("Time vs Action")
        ax.plot(time, action)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xlabel('time(s)')
        plt.ylabel('action [0...255]')
        plt.ylim((-1, max(action)+1))


        # time vs cycling
        ax = fig.add_subplot(122)
        plt.title("Time vs Ambient Light Sesnor state")
        ax.plot(time, als_state)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xlabel('time(s)')
        plt.ylabel('percent max')
        plt.ylim(0, max(max(als_state), 100))


        figure_num += 1

plt.show()
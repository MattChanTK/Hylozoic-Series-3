__author__ = 'Matthew'

import pickle
import Visualization as Viz

import matplotlib.pyplot as plt


with open('test_teensy_1_SMA_action_history_backup.pkl', 'rb') as input:
    action_history = pickle.load(input)

with open('test_teensy_1_SMA_state_history_backup.pkl', 'rb') as input:
    state_history = pickle.load(input)

print(action_history)
print(state_history)


#Viz.plot_evolution(action_history, y_dim=0)
plt.figure(1)
plt.plot(action_history)
plt.ylim((-1, 4))

plt.figure(2)
plt.plot(state_history)

plt.ioff()
plt.show()
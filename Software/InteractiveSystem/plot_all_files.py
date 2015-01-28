__author__ = 'Matthew'

import pickle
import glob
import os
import re

from CBLA import CBLA_Behaviours

teensy_names = (  'HK_teensy_2_LED',)#'HK_teensy_2_SMA_0',

# search for all pickle files

file_names = []

for file in glob.glob("*.pkl"):
    try:
        file_names.append(file)
    except FileNotFoundError:
        continue

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


    viz_data[teensy_name] = [expert, action_history, state_history, mean_error_history]

CBLA_Behaviours.visualize(viz_data)

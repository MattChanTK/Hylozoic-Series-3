# pyHylozoic3


## Interactive System ([interactive_system](interactive_system/interactive_system))

It is a Python module that was written to enable the communication with many Teensy devices simultaneously. A Teensy-Interface thread is created for each Teensy device and synchronize the copies of the hash tables on the Teensy and the computer continuously. Applications on the computer side can control and sample the states of the Teensy devices by modifying the values in the hash tables.

## Abstract Node Layer ([abstract_node](abstract_node/abstract_node))

An additional layer of abstraction was built to represent the sculpture as a network of node. Each node runs as its own thread and possesses a set of input and output variables. Behaviour of each node can be programmed individually. A pre-scripted version of the behaviours will be programmed to compare with the CBLA version in user studies.

## Curiosity Driven Learning Algorithm ([cbla](cbla/cbla))
The CBLA is a type of reinforcement learning algorithm, where the reduction of prediction error is the reward. During the learning process, it will explore regions of the state space that are neither too predictable nor too random; it wants to focus on areas that have the highest potential for new knowledge. To structure the learning process and identify interesting
regions of the state-space, the CBLA automatically segments the state-space into regions; an expert in each region makes predictions about the effects of an action and adjusts its prediction model based on the actual resultant state. The value of each expert is determined by its record of error reduction. This value will then determine the execution likelihood of the action associated with this expert.


## GUI ([hmi_gui](hmi_gui/hmi_gui), [custom_gui](custom_gui/custom_gui))
A basic GUI that display values of input, output, and internal variables. It's based on [Tkinter](https://wiki.python.org/moin/TkInter). A textbox can also be added to change values of the the output variables. *custom_gui* implemented installation-specific GUI. 
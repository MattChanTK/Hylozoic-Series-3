CBLA Test Bed
======================

## Topic
Development of curiosity-driven reinforcement learning algorithm for large-scale sculpture systems. 

Supervised by Dr. Dana Kulic and Dr. Rob Gorbet


## Background

In the Hylozoic Series kinetic sculptures built by Philip Beesley Architect Inc., the designers use a network of microcontrollers to control and sample a sizable number of actuators and sensors. Each node in the network can perform a simple set of interactive behaviours. My research focuses on introducing a Curiosity-Based Learning Algorithm (CBLA) to replace pre-scripted responses in the Hylozoic series installation.  The CBLA algorithm re-casts the interactive sculpture into a set of agents driven by an intrinsic desire to learn.  Presented with a set of input and output parameters that it can observe and control, each agent tries to understand its own mechanisms, its surrounding environment, and the occupants by learning models relating its inputs and outputs. We hypothesize that the occupants will find the behaviours which emerge during CBLA-based control to be interesting, more life-like, and less robotic. 


## Technical Components

There are five main technical challenges in this research project.

### 1. The control hardware and software of the sculptural systems
Compared to previous generations, the CBLA requires the control and sensing of a much larger number of actuators and sensors at a relatively high frequency. To accommodate that, a new hardware platform was built. This hardware platform uses Teensy 3.1 microcontrollers to interface with the sensors and actuators. A set of PCB was custom designed to enable control and sampling of over 24 actuators and 18 sensors using a combination of GPIO. SPI, and I2C interfaces. In addition, a communication protocol was developed to interface each Teensy microcontroller with a computer through USB. The computer is expected to control over 16 Teensy devices at the same time.

### 2. The interfacing software
A Python module was written to enable the communication with many Teensy devices simultaneously. A Teensy-Interface thread is created for each Teensy device and synchronize the copies of the hash tables on the Teensy and the computer continuously. Applications on the computer side can control and sample the states of the Teensy devices by modifying the values in the hash tables. 

### 3. Abstract nodes layer
An additional layer of abstraction was built to represent the sculpture as a network of node. Each node runs as its own thread and possesses a set of input and output variables. Behaviour of each node can be programmed individually. A pre-scripted version of the behaviours will be programmed to compare with the CBLA version in user studies. 

### 4. Curiosity Drivern Learning Algorithm
The CBLA is a type of reinforcement learning algorithm, where the reduction of prediction error is the reward. During the learning process, it will explore regions of the state space that are neither too predictable nor too random; it wants to focus on areas that have the highest potential for new knowledge. To structure the learning process and identify interesting
regions of the state-space, the CBLA automatically segments the state-space into regions; an expert in each region makes predictions about the effects of an action and adjusts its prediction model based on the actual resultant state. The value of each expert is determined by its record of error reduction. This value will then determine the execution likelihood of the action associated with this expert.

### 5. User Study
A user study will be conducted to test the efficacy of increasing users’ interest level in an interactive art
sculpture, by using a curiosity-based learning algorithm (CBLA) to adjust the sculpture’s dynamic behaviours. Simply put, we would like to test whether behaviours generated using the CBLA are more interesting than pre-programmed behaviours designed by human experts. The test subjects will report their level of interest at several points in time as they interact with sculpture, with the two versions of behaviours. Afterward, a short survey will be given to assess the subjects’ overall
experience. The results of this study will enable designers to design more engaging and interesting interactive art sculptures.


Project Page: http://tuzzer.github.io/CBLA-Test-Bed

## Software
<b>InteractiveSystem</b>: code for the Teensy-based system to communicate with the computer

<b>CBLA</b>: simulation of the curiosity-based learning algorithm

## Hardware
<b>PCB Design</b>: Eagle schematic, PCB layout, and library files for the CBLA Test Bed. Also contains gerber files sent to PCB fabrication house. 

<b>Reference</b>: contains datasheets and useful tutorials relevant to the project. 

pyHylozoic3 Software User Guide
=====================================

Installing the pyHylozoic3 Software
--------------------------------
Under the Software/pyHylozoic3/ directory, run install_pyHylozoic3.bat.

The *python* keyword must  be set to execute Python 3.4+. 
Additional steps might be required in install libusb0 which is necessary for a *pyHylozoic3* system to run.


Software Overview
---------------------------------

The control software of the sculpture consists of a low-level firmware layer and high-level application layer. The two layers are connected via USB. The low-level layer consists of the firmware that interfaces with the peripherals that connect with the actuators and sensors. It resides on a custom Control Module that interfaces with the physical electronic components. The high-level layer consists of the tools that facilitate communication between the two layers and the application that dictates the system behaviour. The abstraction provided by the high-level layer allows flexibility in defining the nodes and their relationships to each other. 

A low-level layer of firmware written in C++ runs on the Teensy 3 USB-based development boards which interface with the peripherals that connect with the actuators and sensors. High-level software written in Python 3.4 runs on a central computer. The use of the central computer as a development platform provides flexibility for development free from the limited processing power and specialized functions inherent to the Teensy microcontroller hardware. 

Moreover, Python 3.4 is cross-platform and supports multi-threading, permitting operation within many operating systems and allowing multiple sets of software instructions to be executed in parallel. Code that is necessary for communicating with the low-level layer is packed into a Python module named *interactive-system*. Developers can then develop applications that control and retrieve information from the sculptural system firmware using the software utilities provided by the Python Package. Each application can run on its own thread. While care should be exercised to avoid conflicts among threads, this should permit multiple applications to execute simultaneously.	

A pyHylozoic3 system executes as an application that communicates with the low-level layer by extending the *interactive-system* Python module. Other applications such as an occupancy map that uses the sensors on the sculpture to interpret the locations of the occupants can run simultaneously, taking advantage of the multi-threading properties of the high-level platform.

At the high-level layer, the Teensy Interface module in the *interactive-system* package is used to create a thread for each Teensy device. The thread looks for changes in those parameters and performs synchronization. Each Teensy device on the low-level layer is represented by a Teensy Interface thread on the high-level layer. Teensy devices are considered as slave devices in this communication mechanism. Only the Teensy Interface, the Master, can initiate a read or write request. An InteractiveCmd thread can modify a Teensy's output parameters and retrieve its input parameters through its Teensy Interface. A communication protocol must be defined for each implementation and it is paired with a corresponding Teensy firmware. 

Between the Nodes and the Teensy Interface, there is the InteractiveCmd. Its job is to forward messages to the correct Teensy Interface and hide the physical implementation of the low-level layer devices from the Nodes. In addition, since the InteractiveCmd module enables the control and sampling of any actuators and sensors in the system, a Node can be constructed unconstrained by spatial or hardware specificities. Each Node, physical or virtual, is represented by a set of input and output variables which can be accessed by any other nodes in the system, and each runs continuously in its own thread. Input variables are simply variables in the memory that Nodes have read access to. Similarly, output variables are variables that Nodes have write access to. Multiple Nodes can share one input variable while only one Node can be associated with one output variable. 

At the lowest level, Input Nodes continuously update their associated variables, and Output Nodes continuously send output requests to InteractiveCmd through the Messenger. Different types of Input and Output nodes are configured to run at a loop period compatible with the physical components that they represent. This mechanism makes implementation of the higher level Nodes much easier by eliminating the need for communicating with the InteractiveCmd by means of sending individual messages. Instead, each of the input and output variables can be accessed from the memory at any time. These variables are used as building blocks for higher level Nodes. In addition, intermediate level Nodes can embed extra functionalities. For instance, a LED Driver ramps up or dims an LED to the desired brightness level. A higher-level Node controlling that LED using the LED Driver can then operate at a lower update period and process more complex logic. This Node Abstraction system makes developing CBLA Nodes much simpler by eliminating the need for managing logic requiring different frequencies of control under one thread. 

The addition of the Messenger node between the InteractiveCmd, and Input and Output Nodes streamlines the communication by reducing the number of messages. Over USB, each packet can contain up to 64 bytes. If each Node communicates with the InteractiveCmd directly, there will be many messages that might only require one or two bytes. A large portion of the communication bandwidth will be wasted and the update rate of the Nodes will be significantly throttled. Since many messages are likely to be delivered to the same Teensy, those messages can be combined and delivered as a single packet. The job of the Messenger Node is to collect all the messages, combine them appropriately, and deliver them to the InteractiveCmd periodically. Although this means that each message must wait for the next delivery cycle to be sent out, this mechanism allows the system to handle a much higher throughput. To avoid commands or requests being missed, the rate of each Input or Output node is set to be at least three times the Messenger's update period. 


Initializing the Teensy Interfaces
----------------------------------------

The Teensy Interface is part of the *interactive-system*. Therefoe, one must first import interactive_system.

>>> import interactive_system

Teensy Interface are created by instantiating the Teensy Manager. It will search for all the Teensy devices that are connected and instantiate a Teensy Interface thread for each Teensy device.

>>> teensy_manager = interactive_system.TeensyManager(import_config=True, protocols_dict=protocols)

If *import_config* is true, in the directory where the program executes, a directory named *protocol_variables* must be created. In it, two files that list out the input and output variables and their properites respectively must be created. Otherwise, only the default set of input nad output variables would be created. Each pair of file correspond to a particular protocol.

In addition, a dictionary of protocol should also be pased to the *protocol_dict* parameter. Each protocol extends *interactive_system.SystemParameter*. 

Moreover, a file named *teensy_config* must be created in the directory where the program executes.  It assigns names and their corresponding protocol to Teensy devices based on their Serial Number. 





---
layout: index
---



# Software

## Overview

The software for the CBLA Test Bed was written to enable both reliable local functions and complex inter-node functions.
The main microcontroller used in the current version of the CBLA Test Bed is Teensy 3.1. All Teensy devices are connected to computer through USB connection. The computer is acting as a master node and the Teensy are acting as slave nodes. The main function of the computer is to enable complex behaviours that requires co-ordinations of multiple Teensy slave nodes. 

There are mainly two types of software. The first type of software is the firmware. They are the software that get uploaded onto the Teensy. They are written in Arduino and compiled using Teensyduino. They perform low-level and local functions. These functions should continue to function even if the connection to the computer is severed. The firmware is mainly responsible for routines that require high update rates, such as controlling the timing pattern of the brightness of an LED. The second type of software is the Python script. They perform high-level functions such as coordinating all Teensy devices connected to the computer, controlling Teensy devices from the computer, and displaying sensor readings. To run those Python scripts, the software packages listed under _System Requirements_ must be installed and set up appropriately. 

  
## System Requirements

* Windows OS (tested on Windows 8, but should work on XP, Vista and 7 too)
* [Python 3.3+](https://www.python.org/downloads/)
* [PyUSB](https://github.com/walac/pyusb)
* [libusb-win32](http://sourceforge.net/p/libusb-win32/wiki/Home/)
* [QT-5](https://qt-project.org/downloads)
* [PySide](https://qt-project.org/wiki/PySide_Binaries_Windows)
* [Arduino IDE](http://www.arduino.cc/en/Main/Software)
* [Teensyduino add-on](https://www.pjrc.com/teensy/td_download.html)

  
## Python Functional Modules

The Python scripts facilitate all communications among the Teensy devices. They can mainly be separated into three functional modules. Each module are encapsulated in ways that modifications of implementation details in one module will not affect another module, as long as all the required parameters are given correctly. 
Below gives a high-level overview of the functions and requirements of each module and how they interact with other modules. In a nutshell, one modifies the interface between the computer and Teensy devices at the _Teensy Manager_ module; the input and output parameters and the messaging protocol at the _System Parameters_ module; and the system behaviours (i.e. what to do with the input data and what output command to send out) at the _Behaviours_ module. The best practice would be to creating a sub-class from those modules and overriding only the necessary functions. 
  
### Teensy Manager

```
File: 			TeensyInterface.py
Base class: 	TeensyInterface.TeensyManager
```

The _Teensy Manager_ is responsible for sending to and receiving messages from the Teensy devices. At start-up, it scans for all Teensy devices connected to the computer. After that, it creates one thread for each Teensy device. This allows messages to be sent to all Teensy devices in parallel. 
Each Teensy device is identifiable by its unique serial number. The _Teensy Manager_ will assign name to each Teensy device. This allows programming of the _Behaviours_ module without knowing the location of the actual hardware. In addition, Teensy devices can be replaced simply modifying the mapping between names and serial numbers. 
Furthermore, additional features that increase the reliability of the system can be added to the _Teensy Manager_. Some of these features might be monitoring connection of Teensy devices, prioritizing the Teensy threads, and incorporating new interface method such as Ethernet, and wireless SPI. 

In the Teensy threads, each transfer consists of one packet, or 64 bytes, of data. Only the computer can initiate communication. During the lifetime of a Teensy Thread, it constantly checks for a parameter change event invoked by the _System Parameters_ module. The parameters are what define the action, or _behaviour_ of the system. When a parameter change event is detected, the Teensy thread will initiate an transfer of message. After that, it will wait for a reply from the Teensy device. Currently, the reply message consists of sensor readings and other state information measured right after the new set of parameters is applied. If an valid reply message was received, the message will parsed and the Teensy device's _System Parameters_ module will be updated accordingly. 

To ensure that the correct messages are received by the Teensy devices, the first and last byte of each message will be the message signature. The message signature is basically two 8-bit random numbers generated at each transfer. The middle 62-bytes will be the message content, which is specified in the _System Parameters_ module. After sending the message, the Teensy thread will be waiting for a reply from the Teensy device. The reply message must contain the correct message signature. If an invalid message signature is received more than 5 times or if a timeout of 100ms is reached, an error message will be printed to the terminal and the Teensy thread will be terminated. The _Teensy Manager_ will then remove the dead Teensy thread from the list of active Teensy devices. Note that it is up to the _Behaviours_ modules to handle the disconnection of Teensy devices. 



### System Parameters

```
Files: 			SystemParameters.py
				TestUnitConfigurations.py
Base class: 	SystemParameters.SystemParameters
Sub-classes:  	TestUnitConfigurations.SimplifiedTestUnit
				TestUnitConfigurations.FullTestUnit
```

A _System Parameters_ is instantiated within each Teensy thread. In other word, if desired, each Teensy device may have different sets of input and output parameters. The output parameters specify the action that can be performed by the sculptural system. For example, an action may be "blink LED" and its parameter is the blinking period. The firmware on the Teensy device will take care of low-level timing of the LED actuation, while the Python scripts on the computer can specify how often the LED should turn on or off. In scheme, a transfer of message is only necessary when a change in parameter is required. Moreover, even when the connection between computer and a Teensy device is severed, the Teensy device will continue to function according to the latest parameter values before the disconnection.  Input parameters are the sensor readings and state information measured right after the latest parameter change request (which can be empty) is sent. The idea is that the list of output parameters will always be synchronized between the computer and the Teensy. On the other hand, the input parameters represents the state of the system corresponding an action enforced by the computer. It is up to the _Behaviours_ module to decide what to do with the input parameters. 

Currently, each parameter is stored as a dictionary, or a hash table. Each entry has key which is a string, and a value, which can be of any type. One can modify the list of parameters by overriding the `__init__()` function. In `compose_message_content()` and `parse_message_content()`, one has to specify how to translate those system parameters, to data that can fit in a 62-bytes message and vice versa. The specification of the protocol is completely flexible, as long as the same protocol is implemented on the Teensy devices' firmware. 


### Behaviours

```
Files: 			InteractiveCMD.py
				Behaviours.py
Base class: 	InteractiveCMD.InteractiveCMD
Sub-classes: 	Behaviours.HardcodedBehaviours
				Behaviours.HardcodedBehaviours_test
```

The _Behaviours_ module is where one can program how outputs parameters should be changed and how the input parameters can be used. In the base class `InteractiveCMD`, it prompts the user to enter the command that specify which Teensy to command and what are the changes in parameters. By overriding the `run()` function, one can modify the system's behaviours. In order to effect a change in parameters on a Teensy device, the _Behaviours_ module has to create a `command_object`. It basically has two parameters: the Teensy ID and a queue of change requests for that particular Teensy. To submit change requests to multiple Teensy devices, multiple instances of `command_object` must be created.  These `command_object`'s will then be stored in a queue, called `cmd_q`, within the _Behaviours_ module. Once all the desired commands are entered in the `cmd_q`, a `send_commands()` function can be invoked to send them to the _Teensy Manager_, which will then be sent to the Teensy devices. If all commands in the queue are destined for different Teensy devices, they can all be applied in parallel since one thread will be created to apply each of those commands. If multiple commands are destined to the same Teensy devices, those commands will be sent sequentially. If there are conflicts between the different commands (i.e. one command instructs Teensy to turn a LED on while the other instructs it to turn it off), the command happened later in the queue will be applied. 

  
## Graphical User Interface (GUI)

This has yet to be started. It will most likely be written using QT-5 frame work. Currently, I am considering either writing it in its native language, C++, or in Python using PySide as a wrapper. 


## Teensy Firmware

Description to be written

## Curiosity-Based Learning Algorithm (CBLA)

The CBLA code will be written as a _Behaviours_ module. It is still under development. 

  
## Current Works

* GUI tool for tuning of parameters
* List of input and output parameters for the CBLA Test Bed
* An unit testing script as a behaviours which allows the users to check if the hardware are connected correctly. 


## Project Timeline

Date				| Deliverable
-------------			| -------------
August 28, 2014			| [_hardware_] Complete assembly and testing of prototype hardware
September 3, 2014		| [_software_] Complete the coding of reflex behaviours
September 5, 2014		| [_hardware_] Complete PCB layout of the sound module
September 8, 2014		| [_hardware_] ==Order final version of PCB==
September 10, 2014		| [_software_] Specify the software architecture of the CBLA algorithm
September 23, 2014		| [_software_] Review simulation of CBLA algorithm with simplified model 
September 30, 2014		| Confirm user study venue
September 30, 2014		| [_hardware_] ==Complete assembly and testing of final test bed hardware==
October 13, 2014		| [_software_] Review GUI for CBLA Test bed
October 13, 2014		| Review proposal for the 1st round of user study
November 11, 2014		| Submit initial ORE application form
December 2, 2014		| [_software_] Review CBLA algorithm that will be used for user study
December 17, 2014		| [_software_] ==Finalize CBLA algorithm for user study==
December 17, 2014		| Subjects recruitment for the 1st round of user study begins
January	12, 2015		| ==1st round of user study begins==
January 31, 2015		| 1st round of user study ends
February 13, 2015		| Complete analysis on the 1st round of user study
February 24, 2015		| Review proposal for the 2nd round of user study
March 3, 2015			| Submit revision to the ORE application
March 16, 2015			| Subjects recruitment for the 2nd round of user study begins
April 6, 2015			| 2nd round of user study begins
April 24, 2015			| 2nd round of user study ends
May 12, 2015			| Complete analysis on the 2nd round of user study
Early-June, 2015		| MASc seminar
Mid-August, 2015		| ==MASc thesis submission==


_Updated on 2014-08-22_

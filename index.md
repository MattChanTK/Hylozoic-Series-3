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
* [Teensyduino Add-on](https://www.pjrc.com/teensy/td_download.html)


## Python Functional Modules

The Python scripts facilitate all communications among the Teensy devices. They can mainly be separated into three functional modules. Each module are encapsulated in ways that modifications of implementation details in one module will not affect another module, as long as all the required parameters are given correctly. 
Below gives a high-level overview of the functions and requirements of each module and how they interact with other modules. In a nutshell, one modifies the interface between the computer and Teensy devices at the Teensy Manager module; the input and output parameters and the messaging protocol at the System Parameters module; and the system behaviours (i.e. what to do with the input data and what output command to send out) at the Behaviours module. The best practice would be to creating a sub-class from those modules and overriding only the necessary functions. 

### Teensy Manager

```
File: TeensyInterface.py
Base class: TeensyInterface.TeensyManager
```

The Teensy Manager is responsible for sending to and receiving messages from the Teensy devices. At start-up, it scans for all Teensy devices connected to the computer. After that, it creates one thread for each Teensy device. This allows messages to be sent to all Teensy devices in parallel. 
Each Teensy device is identifiable by its unique serial number. The Teensy Manager will assign name to each Teensy device. This allows programming of the _Behaviours_ module without knowing the location of the actual hardware. In addition, Teensy devices can be replaced simply modifying the mapping between names and serial numbers. 
Furthermore, additional features that increase the reliability of the system can be added to the Teensy Manager. Some of these features might be monitoring connection of Teensy devices, prioritizing the Teensy threads, and incorporating new interface method such as Ethernet, and wireless SPI. 

In the Teensy threads, each transfer consists of one packet, or 64 bytes, of data. Only the computer can initiate communication. During the lifetime of a Teensy Thread, it constantly checks for a parameter change event invoked by the _System Parameters_ module. The parameters are what define the action, or _behaviour_ of the system. When a parameter change event is detected, the Teensy thread will initiate an transfer of message. After that, it will wait for a reply from the Teensy device. Currently, the reply message consists of sensor readings and other state information measured right after the new set of parameters is applied. If an valid reply message was received, the message will parsed and the Teensy device's _System Parameters_ module will be updated accordingly. 

To ensure that the correct messages are received by the Teensy devices, the first and last byte of each message will be the message signature. The message signature is basically two 8-bit random numbers generated at each transfer. The middle 62-bytes will be the message content, which is specified in the _System Parameters_ module. After sending the message, the Teensy thread will be waiting for a reply from the Teensy device. The reply message must contain the correct message signature. If invalid message signatures was received more than 5 times or if a timeout of 100ms is reached, an error message will be printed to the terminal and the Teensy thread will be terminated. The Teensy Manager will then remove the dead Teensy thread from the list of active Teensy devices. Note that it is up to the _Behaviours_ modules to handle the disconnection of Teensy devices. 



### System Parameters

```
File: SystemParameters.py, TestUnitConfigurations.py
Base class: SystemParameters.SystemParameters
Sub-classes:  TestUnitConfigurations.SimplifiedTestUnit, TestUnitConfigurations.FullTestUnit
```

### Behaviours

```
File: InteractiveCMD.py, Behaviours.py
Base class: InteractiveCMD.InteractiveCMD
Sub-classes: Behaviours.HardcodedBehaviours, HardcodedBehaviours_test
```

## Graphical User Interface (GUI)

## Teensy Firmware


## Current Works

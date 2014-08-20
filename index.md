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


## Python Software Modules

### Teensy Manager

### System Parameters

### Behaviours


## Graphical User Interface (GUI)

## Teensy Firmware


## Current Works

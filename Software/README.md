# Hylozoic Series 3 Software

## pyHylozoic3

The pyHylozoic3 directory is a set of Python Modules that make up the Hylozoic Series 3 software framework and its key features. It is written for Python 3.4+ (with libraries packaged with [Anaconda](https://www.continuum.io/downloads)) and tested on Windows 7, 8, 8.1, and 10. To install, run the [*install_pyHylozoic3.bat*](pyHylozoic3/install_pyHylozoic3.bat). To communicate with Teensy devices over USB, [libusb0.1](http://www.libusb.org/) is also required. Its installation files for Windows PC can be found in the [libraries](_libraries) directory.

## Firmware (teensy_firmware)

For different hardware configurations, different firmware (written in Arduino/C++) is required. This firmware goes with a matching set of [pyHylozoic3](pyHylozoic3) based communication protocol and behaviours code. Common utilities and base class files can be found in the [libraries](libraries) directory.

In the [teensy_firmware](teensy_firmware) directory, there are also standalone software that does not require the use of [pyHylozoic3](pyHylozoic3).


## Complex Behaviours (complex_behaviours)

Complex projects that use the [abstract_node](pyHylozoic3/abstract_node/abstract_node) module in the [pyHylozoic3](pyHylozoic3) are located in the [complex_behaviours](complex_behaviours) directory. This includes system that runs [CBLA](pyHylozoic3/cbla/cbla) and more elaborate prescripted behaviours. In addition, [hmi_gui](pyHylozoic3/hmi_gui/hmi_gui) can also be used to create a simple GUI that outputs internal data and basic textbox-based controls.


## Basic Behaviours (basic_behaviours)

Simple test or demo codes that only uses the [interactive_system](pyHylozoic3/interactive_system) module are found in the [basic_behaviours](basic_behaviours) directory.
Example basic behaviours include [basic actuation cycling](basic_behaviours/Behaviours.py), [End-Of-Line testing script](basic_behaviours/EOL_Tool.py), and [internode test](basic_behaviours/Behaviours.py) that demonstrated the possibilibity of nehgbourhood behaviours.
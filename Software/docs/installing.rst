.. How to install Hylozoic Series 3 Software

Installing pyHylozoic3 Software
=====================================

Install Python 3.3+ (Anaconda)
-----------------------------
Anaconda can be downloaded here: https://www.continuum.io/downloads. 

**IMPORTANT**: Download the one for Python 3.x only. The one for Python 2.7 would not work!

Download the PBLA software from github
--------------------------------------
Git Respository: https://github.com/dkadish/Hylozoic-Series-3

Install the pyHylozoic3 Software
--------------------------------
Under the Software/pyHylozoic3/ directory, run install_pyHylozoic3.bat

Install the USB drivers
-----------------------
Under Software/_libraries/libusb-win32-bin-1.2.6.0/bin, run inf-wizard.exe on all of the Teensyduino Interface 0's that you find.

Follow the instructions in libusb-win32-bin-README.txt.

Go to the AMD64 subdirectory and run install-filter-win.exe and select Install A Device Filter.
Next. Find VID: 16c0 and PID:0486, ending in mi:00.
Install that one.
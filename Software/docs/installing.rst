.. How to install Hylozoic Series 3 Software

Installing Hylozoic Series 3 Software
=====================================

Install Python 3.3+ (Anaconda)
-----------------------------

Download the PBLA software from github
--------------------------------------

Install the PyHylozoic3 Software
--------------------------------
Under the Software/pyHylozoic3/ directory, run install_pyHylozoic3.bat

Install the USB drivers
-----------------------
Under Software/_libraries/libusb-win32-bin-1.2.6.0/bin, run inf-wizard.exe on all of the Teensyduino Interface 0's that you find.

Follow the instructions in libusb-win32-bin-README.txt.

Go to the AMD64 subdirectory and run install-filter-win.exe and select Install A Device Filter.
Next. Find VID: 16c0 and PID:0486, ending in mi:00.
Install that one.
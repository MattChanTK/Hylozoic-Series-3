__author__ = 'Matthew'

#!/usr/bin/python

# Import PySide classes
import sys
from PySide import QtCore
from PySide.QtGui import *


# Create a Qt application
app = QApplication(sys.argv)
# Create a Label and show it
label = QLabel("Hello World")
label.show()
# Enter Qt application main loop
app.exec_()
sys.exit()
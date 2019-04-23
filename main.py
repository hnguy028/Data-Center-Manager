##
#   main.py - Main script to DC_Manager
##

from PyQt5.QtWidgets import *
from CustomWidgets import *
import sys


# QApplication widget for the outer frame of the application
class DCApplication:

    def __init__(self):
        self.app = QApplication([])

        # set style
        QApplication.setStyle(QStyleFactory.create("Fusion"))

        # main window, handles menu bar, toolbar, status bar, etc
        self.main_window = DCMainWindow()

    def exec(self):
        return self.app.exec_()


if __name__ == "__main__":
    app = DCApplication()
    sys.exit(app.exec())

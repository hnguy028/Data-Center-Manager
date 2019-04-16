##
#   application.py
##
import config as _global_

from PyQt5.QtWidgets import *
from CustomWidgets import *


class DCApplication:

    def __init__(self):
        self.app = QApplication([])
        QApplication.setStyle(QStyleFactory.create("Fusion"))

        # main window, handles menu bar, toolbar, status bar, etc
        self.main_window = DCMainWindow()

    def exec(self):
        return self.app.exec_()

##
#   application.py
##
import config as _global_

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import xml.etree.ElementTree as ET


class DCApplication:

    def __init__(self):
        self.app = QApplication([])
        QApplication.setStyle(QStyleFactory.create("Fusion"))

        # main window, handles menu bar, toolbar, status bar, etc
        self.window = QMainWindow()
        self.window.resize(_global_.WINDOW_WIDTH, _global_.WINDOW_HEIGHT)
        self.window.setWindowTitle(_global_.APPLICATION_NAME)
        self.window.setWindowIcon(QIcon(_global_.WINDOW_ICON))

        # frame, which should contain all proceeding widgets
        self.frame = QFrame()
        self.frame.resize(_global_.WINDOW_WIDTH, _global_.WINDOW_HEIGHT)

        self.window.setCentralWidget(self.frame)

        self.layout = QGridLayout()

        self.frame.setLayout(self.layout)

        self.window.show()

        self.data_dict = {}

    def load_configurations(self):
        # load information from xml files and pass along to compose to create ui objects
        default_dc = self.load_selection(_global_.XML_DIRECTORY, 'DC_Mngr.xml')

        default_stn = self.load_selection(_global_.XML_DIRECTORY + default_dc + '/', 'StnGrps.xml')


    def load_selection(self, url, lvl_name):
        # load information from xml files and pass along to compose to create ui objects
        tree = ET.parse(url + lvl_name)
        root = tree.getroot()

        result_list = []

        for child in root:
            if child.find('Enbld').text.lower() in ["true", "t"]:
                result_list.append(child.find('Nm').text)

        self.data_dict[root.tag] = result_list

        return result_list[0] if len(result_list) > 0 else None

    def compose(self):
        if 'DC_Mngr' in self.data_dict.keys():
            self.layout.addWidget(add_drop_down(self.data_dict['DC_Mngr'], action))

        if 'StnGrps' in self.data_dict.keys():
            self.layout.addWidget(add_drop_down(self.data_dict['StnGrps'], action))


    def exec(self):
        return self.app.exec_()


def add_drop_down(item_list, func, title=None):
    obj_frame = QFrame()
    obj_frame.setMaximumSize(100, 70)

    layout = QVBoxLayout()

    if title is not None:
        label = QLabel(title)
        layout.addWidget(label)

    dropdownlist = QComboBox()

    for item in item_list:
        dropdownlist.addItem(item)
        # https://stackoverflow.com/questions/45820268/qcombobox-in-pyqt-how-could-i-set-the-options-in-one-combo-box-which-depends-on
        # dropdownlist.addItem(name, data)

    dropdownlist.currentTextChanged.connect(func)

    layout.addWidget(dropdownlist)

    obj_frame.setLayout(layout)

    return obj_frame


def action(item):
    print("We have selected item: " + str(item))

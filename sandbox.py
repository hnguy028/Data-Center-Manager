##
#   sandbox.py
##
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from CustomWidgets import *
import xml.etree.ElementTree as ET


def test():
    tree = ET.parse("C:/Users/hinguyen/Git/DC_Manager/include/data/DC_Mngr.xml")
    root = tree.getroot()

    result_list = []

    for child in root:
        if child.find('Enbld').text.lower() in ["false", "f"]:
            print("asd")
        # if child.find('Enbld').text.lower() in ["true", "t"]:
        #     result_list.append(child.find('Nm').text)


def callMethod(method):
    method


def test2():
    app = QApplication(sys.argv)
    tree = XmlTreeWidget(_path="C:/Users/hinguyen/Git/DC_Manager/include/data", _file_name="PrcssLst.xml")
    tree.load()
    tree.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    print("Dev Testing")
    test2()

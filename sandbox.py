##
#   sandbox.py
##
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from CustomWidgets import *
import xml.etree.ElementTree as ET


def test():
    tree = ET.parse("C:/Users/hinguyen/Git/DC_Manager/include/data/PrcssLst.xml")
    root = tree.getroot()

    result_list = []

    l = list(root)
    i = l[3]
    t = list(i)
    if "test" in t[0].attrib and t[0].attrib["test"] == True:
        print("sdffs")
    # print("test" in t[0].attrib)

    # for child in root:
    #     if child.find('Enbld').text.lower() in ["false", "f"]:
    #         print("asd")
        # if child.find('Enbld').text.lower() in ["true", "t"]:
        #     result_list.append(child.find('Nm').text)


def callMethod(method):
    method


def test2():
    app = QApplication(sys.argv)
    tree = XmlTreeWidget()
    # tree.set_default(_path="C:/Users/hinguyen/Git/DC_Manager/include/data", _file_name="PrcssLst.xml")
    tree1 = ET.parse("C:/Users/hinguyen/Git/DC_Manager/include/data/ALGO00CAN0_StationInfo.xml")
    root1 = tree1.getroot()
    tree.load(root1)
    tree.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    print("Dev Testing")
    test2()
    # test()

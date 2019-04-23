##
#   sandbox.py - testing script, not called in the main application
##
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from CustomWidgets import *
import xml.etree.ElementTree as ET
import config as _global_


def test():
    tree = ET.parse("C:/Users/hinguyen/Git/DC_Manager/include/data/PrcssLst.xml")
    root = tree.getroot()

    li = [
        (["Archvr"], "Testing"),
        (["RINEX2", "Dly30S"], "Nothing"),
        (["DtArchvl", "ArchvlDC", "RINEX2", "_15M_HR"], "skdjfhasdlkfhasdl")
    ]
    #
    update_xml(root, li)
    tree.write("C:/Users/hinguyen/Git/DC_Manager/include/data/PrcssLst2.xml")

    x = root.findall("testing")
    print(x)


def callMethod(method):
    method


#
def update_xml(root, data):
    for inst in data:
        xml_path, val = inst
        update_xml_rec(val, root, xml_path)


#
def update_xml_rec(val, node, tags):
    tag = tags.pop(0)

    if len(tags) > 0:
        update_xml_rec(val, node.findall(tag)[0], tags)
    else:
        node.findall(tag)[0].text = val


def test2():
    app = QApplication(sys.argv)
    tree = XmlTreeWidget()
    # tree.set_default(_path="C:/Users/hinguyen/Git/DC_Manager/include/data", _file_name="PrcssLst.xml")
    tree1 = ET.parse("C:/Users/hinguyen/Git/DC_Manager/include/data/StnLst.xml")
    root1 = tree1.getroot()
    print('ALGO00CAN0' in [i.text for i in root1.findall("Stn/Nm")])


def test3():
    # getattr(_global_, self.dc + '_Mltcst_IP')
    t = getattr(_global_, 'ROOT_DIRECTORY')
    print(t)


if __name__ == "__main__":
    print("Dev Testing")
    test2()
    # test3()

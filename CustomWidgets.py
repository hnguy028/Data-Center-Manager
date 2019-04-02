import config as _global_
import os, sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, uic
import xml.etree.ElementTree as ET


class DCMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(DCMainWindow, self).__init__()
        self.uic = uic.loadUi(_global_.UI_DIRECTORY + _global_.DC_SELECTION, self)
        self.show()

        # self.resize(_global_.WINDOW_WIDTH, _global_.WINDOW_HEIGHT)
        self.setWindowTitle(_global_.APPLICATION_NAME)
        self.setWindowIcon(QIcon(_global_.WINDOW_ICON))

        # load combo box (drop down menus) from xml
        self.uic.cbx_dcs_1.set_default(_path=_global_.XML_DIRECTORY, _file_name=_global_.DC_MNGR)
        self.uic.cbx_dcs_1.update_selection()

        self.uic.cbx_dcs_2.set_default(_path=_global_.XML_DIRECTORY, _dir=self.uic.cbx_dcs_1.currentText(), _file_name=_global_.STN_GRPS)
        self.uic.cbx_dcs_2.update_selection()

        self.uic.cbx_dcs_3.set_default(_path=_global_.XML_DIRECTORY, _dir=os.path.join(self.uic.cbx_dcs_1.currentText(), self.uic.cbx_dcs_2.currentText()), _file_name=_global_.STN_LST)
        self.uic.cbx_dcs_3.update_selection()

        # link combo boxes
        self.uic.cbx_dcs_1.set_dependent(self.uic.cbx_dcs_2)
        self.uic.cbx_dcs_2.set_dependent(self.uic.cbx_dcs_3)

        self.uic.btn_dcs.clicked.connect(self.handle_button)
        self.xml_module = None

    def handle_button(self):
        # get path from combox box currentText function
        self.xml_module = XmlEditor(parent=self, _path=_global_.XML_DIRECTORY, _file_name="ALGO00CAN0_StationInfo.xml")

        self.xml_module.show()
        # todo : lock parent window until child windows is closed


class DependentComboBox(QtWidgets.QComboBox):

    path = None
    file = None
    dir = None

    file_path = None
    xml_root = None
    xml_tree = None

    dependent = None

    def __init__(self, parent=None):
        super(DependentComboBox, self).__init__(parent=parent)

    def set_default(self, _path=None, _dir=None, _file_name=None):
        self.path = _path if _path else ""
        self.dir = _dir if _dir else ""
        self.file = _file_name if _file_name else ""

        self.load_xml(self.dir)

    def set_dependent(self, _dependent):
        self.dependent = _dependent
        self.currentTextChanged.connect(self.update_dependent)

    def update_dependent(self, _name):
        self.dependent.update_selection(_name)

    def load_xml(self, _dir):
        if not os.path.isfile(os.path.join(self.path, _dir, self.file)):
            return

        self.file_path = os.path.join(self.path, _dir, self.file)
        self.xml_tree = ET.parse(self.file_path)
        self.xml_root = self.xml_tree.getroot()

    def update_selection(self, _selection=None):
        # load xml file form selection
        if _selection:
            self.load_xml(_selection)

        # clear selection
        self.clear()

        # load category into dropdown list
        for child in self.xml_root:
            if not child.find('Enbld') or child.find('Enbld').text.lower() in ["true", "t"]:
                self.addItem(child.find('Nm').text)

        # set default to index 0
        self.setCurrentIndex(0)

        # update dependent if not None
        if self.dependent:
            self.dependent.update_selection(os.path.join(_selection, self.currentText()))


class XmlEditor(QtWidgets.QDialog):

    path = None
    file = None
    file_path = None

    xml_tree = None
    xml_root = None

    def __init__(self, parent=None, _path="", _file_name=""):
        super(XmlEditor, self).__init__(parent=parent)

        self.path = _path
        self.file = _file_name
        self.file_path = os.path.join(self.path, self.file)

        if os.path.isfile(self.file_path):
            self.xml_tree = ET.parse(self.file_path)
            self.xml_root = self.xml_tree.getroot()

        # load ui
        self.uic = uic.loadUi(_global_.UI_DIRECTORY + _global_.DC_XML_TREE, self)

        # load tree with xml data
        self.uic.treeWidget.set_default(self.xml_root)
        self.uic.treeWidget.load()
        self.uic.treeWidget.show()

        # handle accept event
        self.uic.buttonBox.accepted.connect(self.write_to_xml_root)

    def write_to_xml_root(self):
        # equivalent to self.xml_root
        root = self.uic.treeWidget.invisibleRootItem().child(0)
        self._write_to_xml_root(root, self.xml_root)

        # write to file
        self.xml_tree.write("text_output.xml")

    # recursive step
    def _write_to_xml_root(self, root, _xml_root):
        if _xml_root.text and root.text(0) != _xml_root.tag:
            print("Error - _write_to_xml_root")
            sys.exit()

        count = root.childCount()

        if count > 0:
            for i in range(count):
                self._write_to_xml_root(root.child(i), list(_xml_root)[i])
        else:
            # At leaf node
            text_col = 1

            if root.text(text_col):
                # there is a text input at the column index
                if "constant" in _xml_root.attrib and _xml_root.attrib["constant"] == "True":
                    pass
                else:
                    if _xml_root.text and root.text(text_col).lower() != _xml_root.text.lower():
                        _xml_root.text = str(root.text(text_col).lower())
                # print(root.text(text_col), " - ", _xml_root.text)

            chk_bx = root.checkState(1)
            xml_val = str(_xml_root.text).lower() in ["true", "t"]
            if chk_bx != xml_val:
                _xml_root.text = str(bool(chk_bx))
            # print node tag, text at column index if any, then the check state
            # print(root.text(0), root.text(1), root.checkState(1))

    def reload(self):
        if os.path.isfile(self.file_path):
            self.xml_tree = ET.parse(self.file_path)
            self.xml_root = self.xml_tree.getroot()

        self.load(self.xml_root)


class XmlTreeWidget(QtWidgets.QTreeWidget):

    xml_root = None

    def __init__(self, parent=None):
        super(XmlTreeWidget, self).__init__(parent=parent)
        self._set_headers(["Process", "Something"])

    def set_default(self, _root=None):
        self.xml_root = _root

        # size of headers will depend on the depth of the xml tree
        self._set_headers(["Process", "Something"])

    def _set_headers(self, _headers=None):
        for i in range(len(_headers)):
            self.headerItem().setText(i, _headers[i])

    def load(self, new_root=None):
        if new_root:
            self.xml_root = new_root

        self._load(self.xml_root, self)
        self.resizeColumnToContents(0)
        self.expandAll()

    # recursive load over children
    def _load(self, _xml_node, _tree_root):
        curr_node = QtWidgets.QTreeWidgetItem(_tree_root)
        curr_node.setText(0, _xml_node.tag)
        curr_node.setFlags(curr_node.flags())
        # todo : make column index 0 uneditable

        if len(_xml_node) > 0:
            for child in _xml_node:
                self._load(child, curr_node)
        else:
            # no children, so it must be an input

            in_col_index = 1
            if _xml_node.text and _xml_node.text in ["true", "false"]:
                # first param is the column index where the check box exists
                curr_node.setCheckState(in_col_index, Qt.Checked if _xml_node.text == "true" else Qt.Unchecked)
            else:
                # check node attribute [constant | edit | null]
                if _xml_node.text is not None:
                    curr_node.setText(in_col_index, _xml_node.text)
                    # set condition to be editable
                    curr_node.setFlags(curr_node.flags() | Qt.ItemIsEditable)


import os
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
import xml.etree.ElementTree as ET


class DependentComboBox(QtWidgets.QComboBox):

    def __init__(self, _path="/", _dir="", _file_name=None, parent=None):
        super(DependentComboBox, self).__init__(parent=parent)

        self.path = _path
        self.file = _file_name
        self.dir = _dir
        self.file_path = os.path.join(self.path, self.dir, self.file)

        if os.path.isfile(self.file_path):
            self.xml_tree = ET.parse(self.file_path)
            self.xml_root = self.xml_tree.getroot()

        self.dependent = None

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


class XmlTreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, _path="", _file_name="", parent=None):
        super(XmlTreeWidget, self).__init__(parent=parent)
        self.path = _path
        self.file = _file_name
        self.file_path = os.path.join(self.path, self.file)

        if os.path.isfile(self.file_path):
            self.xml_tree = ET.parse(self.file_path)
            self.xml_root = self.xml_tree.getroot()

        # size of headers will depend on the depth of the xml tree
        self._set_headers(["Process","Something"])

    def _set_headers(self, _headers=None):
        for i in range(len(_headers)):
            self.headerItem().setText(i, _headers[i])

    def load(self):
        self._load(self.xml_root, self)

    def _load(self, _xml_node, _tree_root):
        curr_node = QtWidgets.QTreeWidgetItem(_tree_root)
        curr_node.setText(0, _xml_node.tag)
        curr_node.setFlags(curr_node.flags())

        if len(_xml_node) > 0:
            for child in _xml_node:
                self._load(child, curr_node)
        else:
            # no children, so it must be an input
            text = _xml_node.text.lower()
            if text in ["true", "false"]:
                # first param is the column index where the check box exists
                curr_node.setCheckState(1, Qt.Checked if text == "true" else Qt.Unchecked)
            else:
                # editable text input?
                pass

    # loads original values again from xml process list
    def reload(self):
        if os.path.isfile(self.file_path):
            self.xml_tree = ET.parse(self.file_path)
            self.xml_root = self.xml_tree.getroot()

        self.load()

    def save_to_file(self):
        pass

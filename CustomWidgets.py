##
#   CustomWidget.py - custom defined widget classes for gui
##
import config as _global_
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, uic
from FileManager import *


# Top Level Window - load in all gui objects, populate with respective information from xml files.
class DCMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(DCMainWindow, self).__init__()

        # load reference to gui object on the main window
        self.uic = uic.loadUi(_global_.UI_DIRECTORY + _global_.DC_SELECTION, self)
        self.show()

        # self.resize(_global_.WINDOW_WIDTH, _global_.WINDOW_HEIGHT)
        self.setWindowTitle(_global_.APPLICATION_NAME)
        self.setWindowIcon(QIcon(_global_.WINDOW_ICON))

        # load combo box information (drop down menus) from xml files
        self.uic.cbx_dcs_1.set_default(_path=_global_.XML_DIRECTORY, _dir="", _file_name=_global_.DC_MNGR)
        self.uic.cbx_dcs_1.update_selection()

        self.uic.cbx_dcs_2.set_default(_path=_global_.XML_DIRECTORY, _dir=self.uic.cbx_dcs_1.currentText(), _file_name=_global_.STN_GRPS)
        self.uic.cbx_dcs_2.update_selection()

        self.uic.cbx_dcs_3.set_default(_path=_global_.XML_DIRECTORY, _dir=os.path.join(self.uic.cbx_dcs_1.currentText(), self.uic.cbx_dcs_2.currentText()), _file_name=_global_.STN_LST, _dir_redundancy=True)
        self.uic.cbx_dcs_3.update_selection()

        # link combo boxes
        self.uic.cbx_dcs_1.set_dependent(self.uic.cbx_dcs_2)
        self.uic.cbx_dcs_2.set_dependent(self.uic.cbx_dcs_3)

        # set event handlers
        self.uic.btn_dcs.clicked.connect(self.handle_process_button)
        # self.uic.btn_dcs_gen.clicked.connect(self.handle_generate_button)

        self.uic.cbx_dcs_3.currentTextChanged.connect(self.load_process_listview)

        self.uic.actionAdd_DC_Station.triggered.connect(self.load_dc_editor)

        # load and populate xml process selection
        self.prc_list = self.uic.process_list_view
        self.load_process_listview()

        # init xml reference dialog
        self.xml_module = None

    # currently implemented with dc_add_menu.ui for proof of concept
    def load_dc_editor(self):
        dc_editor = uic.loadUi(_global_.UI_DIRECTORY + "dc_add_menu.ui")
        dc_editor.label.setText(dc_editor.label.text() + "\n(leave blank to add stations to " + self.uic.cbx_dcs_2.currentText() + ")")

        # if user clicks ok
        if dc_editor.exec_() == QtWidgets.QDialog.Accepted:
            # create directory file manager
            fm = DirectoryFM(path=_global_.XML_DIRECTORY, dc=self.uic.cbx_dcs_1.currentText(),
                             dc_group=self.uic.cbx_dcs_2.currentText(),
                             station_name=self.uic.cbx_dcs_3.currentText())

            textbox1 = dc_editor.plainTextEdit
            textbox2 = dc_editor.plainTextEdit_2

            if textbox2.toPlainText():
                stationList = textbox2.toPlainText().split(",")

                if textbox1.toPlainText():
                    # add new group and station - to current data center
                    fm.add_station_group(textbox1.toPlainText(), stationList)
                else:
                    # add new stations - to current group
                    for station_name in stationList:
                        fm.add_station(station_name)

                # send signal to dc combo box to propagate update
                self.uic.cbx_dcs_1.update_dependent(self.uic.cbx_dcs_1.currentText())

    # todo : alternative implementation with tree view
    # if add station is clicked open the dc_editor dialog
    def _load_dc_editor(self):
        dc_editor = uic.loadUi(_global_.UI_DIRECTORY + "dc_editor.ui")

        # if user clicks ok
        if dc_editor.exec_() == QtWidgets.QDialog.Accepted:
            # create directory file manager
            fm = DirectoryFM(path=_global_.XML_DIRECTORY, dc=self.uic.cbx_dcs_1.currentText(),
                                dc_group=self.uic.cbx_dcs_2.currentText(),  station_name=self.uic.cbx_dcs_3.currentText())

            # add new stations - to current group
            # fm.add_station("STA000CAN0")

            # add new group and station - to current data center
            # fm.add_station_group("Test", ["STA000CAN0"])

        # send signal to dc combo box to propagate update
        self.uic.cbx_dcs_1.update_dependent(self.uic.cbx_dcs_1.currentText())

    # load process list with respect to selected combo boxes
    def load_process_listview(self):
        # compose xml file path
        prcss_loc = os.path.join(_global_.XML_DIRECTORY, self.uic.cbx_dcs_1.currentText(), self.uic.cbx_dcs_2.currentText(), self.uic.cbx_dcs_3.currentText())

        self.prc_list.populate(prcss_loc)

    def handle_process_button(self):
        # get path from combox box currentText function
        location = os.path.join(_global_.XML_DIRECTORY, self.uic.cbx_dcs_1.currentText(), self.uic.cbx_dcs_2.currentText(), self.uic.cbx_dcs_3.currentText())

        # get selected file from process list view
        sel_process = self.prc_list.get_selected()
        print(sel_process)

        # station info.xml
        self.xml_module = self.get_xml_module(sel_process)

        if self.xml_module is None:
            return
        elif self.xml_module.exec_() == QtWidgets.QDialog.Accepted:
            self.xml_module.write_to_xml_root()

            # if process list was edited then update process list view
            if sel_process == "ProcessList":
                # re update the list view to add/remove from xml
                self.load_process_listview()

                # generate any files that were checked
                self.generate_files()
        else:
            pass

        self.xml_module = None

    # handle generation of xml files
    def generate_files(self):
        # load in process list
        prcss_root = ET.parse(os.path.join(_global_.XML_DIRECTORY, self.uic.cbx_dcs_1.currentText(), self.uic.cbx_dcs_2.currentText(), self.uic.cbx_dcs_3.currentText(),  _global_.PRCSS_LST)).getroot()

        # if archvr value is set to true then generate file
        if prcss_root.findall("Archvr")[0].text == "True":
            # generate all selected processes from processlist.xml

            fm = ArchvrFM(path=_global_.XML_DIRECTORY, dc=self.uic.cbx_dcs_1.currentText(),
                          dc_group=self.uic.cbx_dcs_2.currentText(), station_name=self.uic.cbx_dcs_3.currentText())

        if prcss_root.findall("Stn_R_Sync")[0].text == "True":
            pass

    # def handle_generate_button(self):
    #     # loop through process list
    #     # if enbld == true, then we generate the corresponding xml files
    #     sel_process = self.prc_list.get_selected()
    #     if sel_process == "Archvr":
    #         fm = ArchvrFM(path=_global_.XML_DIRECTORY, dc=self.uic.cbx_dcs_1.currentText(),
    #                             dc_group=self.uic.cbx_dcs_2.currentText(),  station_name=self.uic.cbx_dcs_3.currentText())

    def get_xml_module(self, process_name):
        # construct path
        location = os.path.join(_global_.XML_DIRECTORY, self.uic.cbx_dcs_1.currentText(),
                                 self.uic.cbx_dcs_2.currentText(), self.uic.cbx_dcs_3.currentText())

        # load xml file
        if process_name == "StationInfo":
            return XmlEditor(parent=self, _path=location,
                             _file_name=self.uic.cbx_dcs_3.currentText() + "_StationInfo.xml")
        elif process_name == "ProcessList":
            return XmlEditor(parent=self, _path=location,
                             _file_name="PrcssLst.xml")
        elif process_name == "Archvr":
            return XmlEditor(parent=self, _path=location,
                             _file_name=self.uic.cbx_dcs_3.currentText()[:6] + "_NTRIPRTCM2File_Config.xml")
        else:
            print("Not Implemented")


# Combo boxes that will update its dependent when changed
class DependentComboBox(QtWidgets.QComboBox):

    path = None
    file = None
    dir = None

    file_path = None
    xml_root = None
    xml_tree = None

    dir_redundancy = False
    dependent = None

    def __init__(self, parent=None):
        super(DependentComboBox, self).__init__(parent=parent)

    def set_default(self, _path=None, _dir=None, _file_name=None, _dir_redundancy=False):
        self.path = _path if _path else ""
        self.dir = _dir if _dir else ""
        self.file = _file_name if _file_name else ""

        self.dir_redundancy = _dir_redundancy
        self.load_xml(self.dir)

    def set_dependent(self, _dependent):
        self.dependent = _dependent
        self.currentTextChanged.connect(self.update_dependent)

    def update_dependent(self, _name):
        self.dependent.update_selection(os.path.join(self.dir, _name))

    def load_xml(self, _dir):
        if not os.path.isfile(os.path.join(self.path, _dir, self.file)):
            return

        self.dir = _dir

        self.file_path = os.path.join(self.path, _dir, self.file)
        self.xml_tree = ET.parse(self.file_path)
        self.xml_root = self.xml_tree.getroot()

    def reload(self):
        self.file_path = os.path.join(self.path, self.dir, self.file)
        self.xml_tree = ET.parse(self.file_path)
        self.xml_root = self.xml_tree.getroot()

    def update_selection(self, _selection=""):
        self.blockSignals(True)

        # load xml file form selection
        _selection = _selection if _selection else self.dir
        self.load_xml(_selection)

        # clear list
        self.clear()

        self.blockSignals(False)

        # load category into dropdown list
        for child in self.xml_root:
            if not child.find('Enbld') or child.find('Enbld').text.lower() in ["true", "t"]:
                self.addItem(child.find('Nm').text)

        # set selected choice to first item
        self.setCurrentIndex(0)

        # update dependent if not None
        if self.dependent:
            self.dependent.update_selection(os.path.join(_selection, self.currentText()))


# XmlEditor - modifies the xml file from changes in XmlTreeWidget
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

        # load ui object references
        self.uic = uic.loadUi(_global_.UI_DIRECTORY + _global_.DC_XML_TREE, self)

        # load tree with xml data
        self.uic.treeWidget.set_default(self.xml_root)
        self.uic.treeWidget.load()
        self.uic.treeWidget.show()

    # write changes from the xml object in memory to file
    def write_to_xml_root(self, path=None, file_name=None):
        if self.xml_root is None:
            print("No xml loaded")
            return

        # equivalent to self.xml_root
        root = self.uic.treeWidget.invisibleRootItem().child(0)

        # recursive loop over tree to update changes DFS stylz
        self._write_to_xml_root(root, self.xml_root)

        # get file path
        dl_path = path if path else self.path
        dl_file_name = file_name if file_name else self.file

        dl_loc = os.path.join(dl_path, dl_file_name)

        # copy current xml file to create backup
        shutil.copy(dl_loc, dl_loc + ".bckup")

        # write to file
        self.xml_tree.write(dl_loc)

    # recursive step - root=tree widget node, _xml_root=xml etree node
    def _write_to_xml_root(self, root, _xml_root):
        if _xml_root.text and root.text(0) != _xml_root.tag:
            print("Error - _write_to_xml_root")
            sys.exit()

        count = root.childCount()

        if count > 0:
            for i in range(count):
                self._write_to_xml_root(root.child(i), list(_xml_root)[i])
        else:
            # Now at leaf node
            text_col = 1

            # check if there is a text input at the column index
            if root.text(text_col):
                if "constant" in _xml_root.attrib and _xml_root.attrib["constant"] == "True":
                    pass
                else:
                    if _xml_root.text and root.text(text_col).lower() != _xml_root.text.lower():
                        _xml_root.text = str(root.text(text_col).lower())

            # else we assume its a checkbox

            # # get check state from the dialog window
            # chk_bx = root.checkState(1)
            #
            # # get check state from xml file
            # xml_val = str(_xml_root.text).lower() in ["true", "t"]
            #
            # if chk_bx != xml_val:
            #     # update xml node
            #     _xml_root.text = str(bool(chk_bx))
            _xml_root.text = str(bool(root.checkState(1)))

    # reload from xml file
    def reload(self):
        if os.path.isfile(self.file_path):
            self.xml_tree = ET.parse(self.file_path)
            self.xml_root = self.xml_tree.getroot()

        self.load(self.xml_root)


# XmlTreeWidget - loads and displays selected xml file
class XmlTreeWidget(QtWidgets.QTreeWidget):

    xml_root = None

    def __init__(self, parent=None):
        super(XmlTreeWidget, self).__init__(parent=parent)

    def set_default(self, _root=None):
        self.xml_root = _root

        # size of headers will depend on the depth of the xml tree
        self._set_headers(["Tag", "Data"])

    def _set_headers(self, _headers=None):
        for i in range(len(_headers)):
            self.headerItem().setText(i, _headers[i])

    # load view from tree root object
    def load(self, new_root=None):
        if new_root:
            self.xml_root = new_root

        if self.xml_root is None:
            print("Cannot Access Xml file")
            return

        self._load(self.xml_root, self)

        # set default expanded view
        self.expandAll()
        self.resizeColumnToContents(1)

        # self.hideColumn(2)

    # recursive load over children
    def _load(self, _xml_node, _tree_root):
        curr_node = QtWidgets.QTreeWidgetItem(_tree_root)
        curr_node.setText(0, _xml_node.tag)
        curr_node.setFlags(curr_node.flags())

        # todo : make column index 0 (tags in the xml tree) immutable

        if len(_xml_node) > 0:
            for child in _xml_node:
                self._load(child, curr_node)
        else:
            # at leaf node, so it must be an input

            in_col_index = 1

            # if the value is true/false, display check box
            if _xml_node.text and _xml_node.text.lower() in ["true", "false"]:
                # first param is the column index where the check box exists
                curr_node.setCheckState(in_col_index, Qt.Checked if _xml_node.text.lower() == "true" else Qt.Unchecked)
            else:
                # check node attribute [constant | edit | null]
                if _xml_node.text is not None:
                    curr_node.setText(in_col_index, _xml_node.text)
                    # set condition to be editable
                    curr_node.setFlags(curr_node.flags() | Qt.ItemIsEditable)

    # def determineEditableText(self, index):
    #     # add extra hidden column which will determine if data can be edited?
    #     item = self.currentItem()
    #     print(index.column())
    #     if index.column() >= 1 and (item.flags() and Qt.ItemIsEditable):
    #         pass
    #     else:
    #         item.setFlags(item.flags() ^ Qt.ItemIsEditable)


##
#   This widget displays the data center/data center groups/stations, as well as allows the user to add/remove a group
##
class StationsTreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, parent=None):
        super(StationsTreeWidget, self).__init__(parent=parent)

    # todo : load all dcs/dc groups/stations
    # add station function (dc,sta_grp,sta)

    # display as tree, at last child add editable "ADD" button (Some QtObject!!)

    # right click remove option? - at least add function to remove given depth (dc/dc_group/station)
    # create confirmation menu?

    # all changes will be stored in a data structure then committed to tree once confirmed!! (QTAccepted)

    def loadXML(self):
        pass


# ProcessListView - displays list of processes to be selected
class ProcessListView(QtWidgets.QListWidget):

    def __init__(self, parent=None):
        super(ProcessListView, self).__init__(parent=parent)

        # set single selection mode
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # connect event trigger
        self.itemSelectionChanged.connect(self.print)

    def print(self):
        print(self.get_selected())

    # todo : check if file exits, if not write option in red ?
    def populate(self, process_loc=""):
        # block any actions that are called when list is updated
        self.blockSignals(True)

        # clear list of processes
        self.clearSelection()
        self.clear()

        # add station info and process list
        self.addItems(["StationInfo", "ProcessList"])

        # load processes from prcsslist.xml
        prcss_file = os.path.join(process_loc, _global_.PRCSS_LST)

        # iterate through prcsslst xml and if enbld == True then add to list
        if os.path.isfile(prcss_file):
            xml_root = ET.parse(prcss_file).getroot()

            for child in xml_root:
                item = QtWidgets.QListWidgetItem(child.tag)

                if len(child) > 0:
                    for _child in child.findall('Enbld'):
                        if not _child.text or _child.text.lower() in ["false", "f"]:
                            item.setFlags(Qt.NoItemFlags)
                else:
                    if not child.text or child.text.lower() in ["false", "f"]:
                            item.setFlags(Qt.NoItemFlags)

                self.addItem(item)

        # re enable signals
        self.blockSignals(False)

    def get_selected(self):
        return self.selectedItems()[0].text() if self.selectedItems() else 'None'

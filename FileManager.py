##
#   FileManager.py - handles modification and initial loading of files
##
import config as _global_
import os, shutil
import xml.etree.ElementTree as ET
from abc import abstractmethod


class FileManager:

    def __init__(self, path, dc, dc_group, station_name):
        self.path = path
        self.dc = dc
        self.dc_group = dc_group
        self.station_nm = station_name

        self.paths = {'root': path,
                      'dc_path': os.path.join(path, dc),
                      'dc_group_path': os.path.join(path, dc, dc_group),
                      'station_path': os.path.join(path, dc, dc_group, station_name)}

        self.overwrite_flag = True

    @abstractmethod
    def configure_default(self):
        pass

    def get_file_path(self):
        return self.file_path


##
#   DirectoryManager - Handles modification of directory structure (add/rm stations, groups and/or data centers)
##
class DirectoryFM(FileManager):
    
    def __init__(self, path, dc, dc_group, station_name):
        super(DirectoryFM, self).__init__(path, dc, dc_group, station_name)
        # load xml trees

    def configure_default(self):
        # load file templates
        pass

    def add_data_center(self):
        pass

    def add_station_group(self, group_name, station_names, enabled=True, path=None):
        # add to StnGrps.xml
        stn_grps_filename = os.path.join(path if path is not None else self.paths['dc_path'], _global_.STN_GRPS)
        grp_tree = ET.parse(stn_grps_filename)
        grp_root = grp_tree.getroot()

        # check if group already exists
        # todo : if group already exists then batch add new stations
        if os.path.exists(os.path.join(self.paths['dc_path'], group_name)) or group_name in [i.text for i in grp_root.findall("Grp/Nm")]:
            return

        # otherwise create directory and add stations to group
        dc_group_path = os.path.join(self.paths['dc_path'], group_name)
        os.mkdir(dc_group_path)

        # add group to StnGrps.xml
        grp_node = ET.SubElement(grp_root, 'Grp')

        nm_node = ET.SubElement(grp_node, 'Nm')
        nm_node.text = group_name

        enbld_node = ET.SubElement(grp_node, 'Enbld')
        enbld_node.text = str(enabled)

        # write to xml
        grp_tree.write(stn_grps_filename)

        # add/create required xml files
        shutil.copyfile(os.path.join(_global_.TEMPLATE_DIRECTORY, _global_.STN_LST),
                        os.path.join(dc_group_path, _global_.STN_LST))

        # add stations
        for station in station_names:
            self.add_station(station, enabled=enabled, path=dc_group_path)

    #
    def add_station(self, station_name, enabled=True, path=None):
        # load StnLst.xml
        dc_group_path = path if path is not None else self.paths['dc_group_path']
        stn_lst_filename = os.path.join(dc_group_path, _global_.STN_LST)
        tree = ET.parse(stn_lst_filename)
        root = tree.getroot()

        # check if the station already exists (directory and xml instance)
        if os.path.exists(os.path.join(dc_group_path, station_name)) or station_name.upper() in [i.text for i in root.findall("Stn/Nm")]:
            return

        # create station directory
        os.mkdir(os.path.join(dc_group_path, station_name))

        # add station to StnLst.xml
        stn_node = ET.SubElement(root, 'Stn')

        nm_node = ET.SubElement(stn_node, 'Nm')
        nm_node.text = station_name

        enbld_node = ET.SubElement(stn_node, 'Enbld')
        enbld_node.text = str(enabled)

        tree.write(stn_lst_filename)

        # add/create stationInfo.xml and processList.xml

        return


class ArchvrFM(FileManager):

    def __init__(self, path, dc, dc_group, station_name):
        super(ArchvrFM, self).__init__(path, dc, dc_group, station_name)

        # copy from template folder
        self.file_name = os.path.join(self.paths['station_path'], self.station_nm[:6] + "_NTRIPRTCM2File_Config.xml")
        if os.path.isfile(self.file_name) and not self.overwrite_flag:
            # already exists and we do not want to overwrite
            return
        else:
            shutil.copyfile(os.path.join(_global_.TEMPLATE_DIRECTORY, _global_.ARCHVR_FILE_NAME),
                            self.file_name)

        # load reference to xml
        self.xml_tree = ET.parse(self.file_name)
        self.xml_root = self.xml_tree.getroot()

        # load from main config file DfltPrmtrs.xml
        self.dfltprmtrs_xml = os.path.join(_global_.ROOT_DIRECTORY, _global_.DfltPrmtrs)
        self.dfltprmtrs_xml_tree = ET.parse(self.dfltprmtrs_xml)
        self.dfltprmtrs_xml_root = self.dfltprmtrs_xml_tree.getroot()

        # load from main config file [STA]_Stns_NTRIP_Cnfg.xml
        self.ntrip_config_xml = os.path.join(self.paths['dc_group_path'], self.dc_group + "_NTRIP_Cnfg.xml")
        self.ntrip_xml_tree = ET.parse(self.ntrip_config_xml)
        self.ntrip_xml_root = self.ntrip_xml_tree.getroot()

        # fill in values
        self.configure_default()

        # write to xml
        self.xml_tree.write(self.file_name)

    def configure_default(self):
        # (["Path", "to", "xml", "node"], "text_value")
        update_info = [
            ([_global_.RTCMRdrLgFlPth], self.xml_root.findall(_global_.RTCMRdrLgFlPth)[0].text + self.station_nm[:6] + "/"),
            # ([_global_.RTCMRdrLgFlPth], self.dfltprmtrs_xml_root.findall(_global_.ArchvRTCM_LgPth)[0].text + self.station_nm + "/"),
            ([_global_.RTCMRdrLgFlStnNm], self.station_nm[0:4]),
            ([_global_.RTCMRdrLgFlCntryCd], self.station_nm[-4:-1]),
            ([_global_.RTCMRdrLgFlStnMnmntNmbr], self.station_nm[4:5]),
            ([_global_.RTCMRdrLgFlMnmntRcvrNmbr], self.station_nm[5:6]),
            ([_global_.RTCMRdrStnNmbr], self.station_nm[3:6]), # map["NRC100"]

            # RTCMDataInSrc
            ([_global_.RTCMDataInSrc, _global_.RTCMObsInIPPswd, _global_.IPEnbldFlg], "True"),
            ([_global_.RTCMDataInSrc, _global_.RTCMObsInIPPswd, _global_.IP], self.ntrip_xml_root.findall(_global_.IP)[0].text),
            ([_global_.RTCMDataInSrc, _global_.RTCMObsInIPPswd, _global_.PrtNmbr], self.ntrip_xml_root.findall(_global_.PrtNmbr)[0].text),
            ([_global_.RTCMDataInSrc, _global_.RTCMObsInIPPswd, _global_.Prtcl], self.ntrip_xml_root.findall(_global_.Prtcl)[0].text),
            ([_global_.RTCMDataInSrc, _global_.RTCMObsInIPPswd, _global_.NTRIPEnbldFlg], self.ntrip_xml_root.findall(_global_.NTRIPEnbldFlg)[0].text),
            ([_global_.RTCMDataInSrc, _global_.RTCMObsInIPPswd, _global_.NTRIPPswd], self.ntrip_xml_root.findall(_global_.NTRIPPswd)[0].text),
            ([_global_.RTCMDataInSrc, _global_.RTCMObsInIPPswd, _global_.NTRIPUsrNm], self.ntrip_xml_root.findall(_global_.NTRIPUsrNm)[0].text),
            ([_global_.RTCMDataInSrc, _global_.RTCMObsInIPPswd, _global_.NTRIPMntPnt], self.station_nm[:6]),

            # RTCMPrcsLst
            # not yet implemented since they are defaulted to true? if so then we can just load from the stub file
            # ([_global_.RTCMPrcsLst, _global_.PrcsFlgs, _global_.ReadRTCMObs_Flg], "True"),

            # RTCMOutDstn
            ([_global_.RTCMOutDstn, _global_.RTCMOutDataPth], self.xml_root.findall("/".join([_global_.RTCMOutDstn, _global_.RTCMOutDataPth]))[0].text + self.station_nm[:6] + "/"),
            ([_global_.RTCMOutDstn, _global_.RTCMObsOutIPPswd, _global_.IP], self.dfltprmtrs_xml_root.findall(self.dc + '_Mltcst_IP')[0].text),
            ([_global_.RTCMOutDstn, _global_.RTCMObsOutIPPswd, _global_.PrtNmbr], self.dfltprmtrs_xml_root.findall(self.dc + '_RTCM3_Prt')[0].text),
        ]

        update_xml(self.xml_root, update_info)


# Static Functions
def copy_template(src, new_filename, dest=None):
    path = os.path.dirname(os.path.abspath(src))
    # filename = os.path.basename(src)

    shutil.copyfile(src, os.path.join(path, new_filename))


# follows the list of tags defined in data from root to node and writes the value to the node
def update_xml(root, data):
    for inst in data:
        xml_path, val = inst

        node = root.findall("/".join(xml_path))
        if node is not None and len(node) > 0:
            node[0].text = val

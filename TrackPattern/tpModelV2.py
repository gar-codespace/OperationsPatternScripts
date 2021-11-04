import jmri
import time
from codecs import open as cOpen
import json
from shutil import copy as sCopy
from os import system, path as oPath, mkdir
from sys import path as sPath
sPath.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsTrackPattern')
# import tpViewV1 as tpView
# import tpControllerV1 as tpControl
# import tpModelEntities

class guiSubmitData(jmri.jmrit.automat.AbstractAutomaton):
    '''Input from the GUI'''

    def init(self):
        pass
        return

    def handle(self):

        return False

class guiRefresh(jmri.jmrit.automat.AbstractAutomaton):
    '''Output to the GUI'''

    def init(self):
        pass
        return

    def handle(self):
        configFile = tpModelEntities.readConfigFile()

        return False

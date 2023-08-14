"""
Exports a JMRI manifest into a csv.
Exports a OPS switch list into a csv.
Both exports are formated for import into the TrainPlayer Quick Keys script suite.
Called by listeners attached to the Train Manager.
Can also be called as a stand alone script.
"""

import jmri
import sys
from os import path as OS_PATH

SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b1'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b2'

PLUGIN_ROOT = OS_PATH.join(jmri.util.FileUtil.getPreferencesPath(), SCRIPT_DIR)
sys.path.append(PLUGIN_ROOT)
from opsEntities import PSE


PSE.PLUGIN_ROOT = PLUGIN_ROOT
PSE.SCRIPT_DIR = SCRIPT_DIR
PSE.JMRI = jmri
PSE.SYS = sys
PSE.OS_PATH = OS_PATH

from opsEntities import PSE
from Subroutines.o2o import ModelWorkEvents
from Subroutines.o2o import ModelEntities
from Subroutines.o2o import Listeners
from opsBundle import Bundle

Bundle.BUNDLE_DIR = PSE.OS_PATH.join(PLUGIN_ROOT, 'opsBundle')

PSE.PLUGIN_ROOT = PLUGIN_ROOT
PSE.BUNDLE = Bundle.getBundleForLocale()
PSE.ENCODING = 'utf-8'

SCRIPT_NAME ='OperationsPatternScripts.StandAloneExport'
SCRIPT_REV = 20230201


class StandAloneLogging():
    """
    """

    def __init__(self):

        # fileName = 'StandAloneExportLog.txt'
        # targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH , 'operations', 'buildstatus', fileName)

        self.logger = PSE.Logger(targetPath)
        self.o2oLog = PSE.LOGGING.getLogger('TP.StandAlone')

        return
    
    def startLogging(self):

        self.logger.startLogger('TP')
        self.logger.initialLogMessage(self.o2oLog)

        return

    def stopLogging(self):

        self.logger.stopLogger('TP')

        return


class ConvertJmriManifestStandAlone(jmri.jmrit.automat.AbstractAutomaton):
    """
    Converts a JMRI manifest to a Quick Keys work events list.
    This is the stand alone version.
    """

    def init(self):

        fileName = 'OPS StandAloneExport.txt'
        logFileTarget = PSE.OS_PATH.join(PSE.PROFILE_PATH , 'operations', 'buildstatus', fileName)
        self.logger = PSE.Logger(logFileTarget)
        self.logger.startLogger('OPS')

        self.console = PSE.APPS.SystemConsole.getConsole()
        self.trainsWindow = PSE.JMRI.jmrit.operations.trains.TrainsTableFrame()

        return

    def handle(self):

        self.psLog = PSE.LOGGING.getLogger('OPS.StandAloneExport')
        self.logger.initialLogMessage(self.psLog)

        Listeners.addTrainsListener()

        self.console.setVisible(True)
        self.trainsWindow.setVisible(True)

        self.psLog.info('ConvertJmriManifestStandAlone')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return False


if __name__ == "__builtin__":
    ConvertJmriManifestStandAlone().start()




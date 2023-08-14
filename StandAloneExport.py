"""
Exports a JMRI manifest into a TrainPlayer Quick Keys compatable csv.
Called by o2o listeners attached to the Train Manager.
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

from Subroutines.o2o import Listeners
from opsBundle import Bundle

Bundle.BUNDLE_DIR = PSE.OS_PATH.join(PLUGIN_ROOT, 'opsBundle')

PSE.PLUGIN_ROOT = PLUGIN_ROOT
PSE.BUNDLE = Bundle.getBundleForLocale()
PSE.ENCODING = 'utf-8'

SCRIPT_NAME ='OperationsPatternScripts.StandAloneExport'
SCRIPT_REV = 20230201


class StandAloneExport(jmri.jmrit.automat.AbstractAutomaton):

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
    StandAloneExport().start()

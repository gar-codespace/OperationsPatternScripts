"""
Exports a JMRI manifest into a TrainPlayer Quick Keys compatable csv.
Creates a Train List and Work Order for a built train.
Called by o2o listeners attached to each train via the Train Manager.

To use, Edit/Preferences.../Start Up
select Add/Run Script
Navigate to and select StandAloneExport.py
"""

import jmri
import sys
from os import path as OS_PATH

SCRIPT_NAME ='OperationsPatternScripts.StandAloneExport'
SCRIPT_REV = 20231001
SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b3'

PLUGIN_ROOT = OS_PATH.join(jmri.util.FileUtil.getPreferencesPath(), SCRIPT_DIR)
sys.path.append(PLUGIN_ROOT)
from opsEntities import PSE

PSE.PLUGIN_ROOT = PLUGIN_ROOT
PSE.SCRIPT_DIR = SCRIPT_DIR
PSE.JMRI = jmri
PSE.SYS = sys
PSE.OS_PATH = OS_PATH

from opsEntities import PluginListeners
from opsBundle import Bundle

PSE.PLUGIN_ROOT = PLUGIN_ROOT
PSE.BUNDLE = Bundle.getBundleForLocale()

PSE.validateConfigFile()
configFile = PSE.readConfigFile()
encodingSelection = configFile['Main Script']['CP']['ES']
PSE.ENCODING = configFile['Main Script']['CP']['EO'][encodingSelection]


class StandAloneExport(jmri.jmrit.automat.AbstractAutomaton):

    def init(self):

        fileName = 'OPS StandAloneExport.txt'
        logFileTarget = PSE.OS_PATH.join(PSE.PROFILE_PATH , 'operations', 'buildstatus', fileName)
        self.logger = PSE.Logger(logFileTarget)
        self.logger.startLogger('OPS')

        return

    def handle(self):

        self.psLog = PSE.LOGGING.getLogger('OPS.StandAloneExport')
        self.logger.initialLogMessage(self.psLog)

        PSE.makeReportFolders()

        PluginListeners.addTrainsTableListener()
        PluginListeners.addTrainListener()

        PSE.openSystemConsole()
        PSE.JMRI.jmrit.operations.trains.TrainsTableFrame()

        self.psLog.info('ConvertJmriManifestStandAlone')

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return False


if __name__ == "__builtin__":
    StandAloneExport().start()

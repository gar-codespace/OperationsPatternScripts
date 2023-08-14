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

        fileName = 'BuiltTrainExportLog.txt'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH , 'operations', 'buildstatus', fileName)

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

        self.SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.BuiltTrainExport.o2oWorkEventsBuilder'

        self.standAloneLogging = StandAloneLogging()
        self.o2oLog = PSE.LOGGING.getLogger('TP.o2oWorkEventsBuilder')

        print('here')

        return

    def getNewestTrain(self):

        return FindTrain().findNewestTrain()

    def passInTrain(self, train):

        self.train = train

        return

    def handle(self):

        self.standAloneLogging.startLogging()



        if not ModelEntities.tpDirectoryExists():
            self.o2oLog.warning('TrainPlayer Reports directory not found')
            self.o2oLog.warning('TrainPlayer manifest export did not complete')

            return False

        self.o2oLog.debug('ModelWorkEvents.jmriManifestConversion')

        self.train.setPrinted(True)

        o2o = ModelWorkEvents.jmriManifestConversion(self.train)
        o2o.jmriManifestGetter()
        o2o.convertHeader()
        o2o.convertBody()
        o2oWorkEvents = o2o.geto2oWorkEvents()
    # Common post processor for ModelWorkEvents.ConvertPtMergedForm.o2oButton and BuiltTrainExport.o2oWorkEventsBuilder.handle
        o2o = ModelWorkEvents.o2oWorkEvents(o2oWorkEvents)
        o2o.o2oHeader()
        o2o.o2oLocations()
        o2o.saveList()

        self.o2oLog.info('Export JMRI manifest to TrainPlayer: ' + self.train.getName())
        self.o2oLog.info('Export to TrainPlayer script location: ' + PLUGIN_ROOT)


        print(self.SCRIPT_NAME + ' ' + str(SCRIPT_REV))


        self.standAloneLogging.stopLogging()

        return False

ConvertJmriManifestStandAlone().satrt()




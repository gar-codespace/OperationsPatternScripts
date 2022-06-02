"""Exports a TrainPlayer manifest into a csv for import into the TrainPlayer o2o script suite.
Callable from the pattern scripts subroutine or stand alone.
"""

import jmri

import time
from sys import path as sysPath

SCRIPT_NAME ='OperationsPatternScripts.TrainPlayerSubroutine.BuiltTrainExport'
SCRIPT_REV = 20220101

SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b1'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b2'

class StandAloneLogging():
    """Called when this script is used by itself"""

    def __init__(self):

        logPath = PatternScriptEntities.PROFILE_PATH  + 'operations\\buildstatus\\BuiltTrainExportLog.txt'
        self.logger = PatternScriptEntities.Logger(logPath)
        self.tpLog = PatternScriptEntities.LOGGING.getLogger('TP.StandAlone')

        return

    def startLogging(self):

        self.logger.startLogger('TP')
        self.logger.initialLogMessage(self.tpLog)

        return

    def stopLogging(self):

        self.logger.stopLogger('TP')

        return


class FindTrain:
    """Called when this script is used by itself"""

    def __init__(self):

        self.tpLog = PatternScriptEntities.LOGGING.getLogger('TP.FindTrain')

        return

    def findNewestTrain(self):
        """If more than 1 train is built, pick the newest one"""

        self.tpLog.debug('findNewestTrain')

        if not PatternScriptEntities.TM.isAnyTrainBuilt():

            return

        newestBuildTime = ''
        for train in self.getBuiltTrains():
            testDate = self.getTrainBuiltDate(train)
            if testDate > newestBuildTime:
                newestBuildTime = testDate
                newestTrain = train

        return newestTrain

    def getBuiltTrains(self):

        self.tpLog.debug('getBuiltTrains')

        builtTrainList = []
        for train in PatternScriptEntities.TM.getTrainsByStatusList():
            if train.isBuilt():
                builtTrainList.append(train)

        return builtTrainList

    def getTrainBuiltDate(self, train):

        manifest = jmri.util.FileUtil.readFile(jmri.jmrit.operations.trains.JsonManifest(train).getFile())

        return PatternScriptEntities.loadJson(manifest)['date']


class ManifestForTrainPlayer(jmri.jmrit.automat.AbstractAutomaton):
    """Runs on JMRI train builds"""

    def init(self):

        self.SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.BuiltTrainExport.ManifestForTrainPlayer'
        self.SCRIPT_REV = 20220101

        self.standAloneLogging = StandAloneLogging()
        self.tpLog = PatternScriptEntities.LOGGING.getLogger('TP.ManifestForTrainPlayer')

        return

    def getNewestTrain(self):

        return FindTrain().findNewestTrain()

    def passInTrain(self, train):

        self.train = train

        return

    def handle(self):

        self.standAloneLogging.startLogging()

        timeNow = time.time()

        if PatternScriptEntities.CheckTpDestination().directoryExists():

            self.tpLog.debug('Model.ExportJmriLocations')
            jmriExport = Model.ExportJmriLocations()
            locationList = jmriExport.makeLocationList()
            jmriExport.toTrainPlayer(locationList)

            self.tpLog.debug('Model.JmriTranslationToTp')
            jmriManifestTranslator = Model.JmriTranslationToTp()
            builtTrainAsDict = jmriManifestTranslator.getTrainAsDict(self.train)
            translatedManifest = jmriManifestTranslator.translateManifestHeader(builtTrainAsDict)
            translatedManifest['locations'] = jmriManifestTranslator.translateManifestBody(builtTrainAsDict)

            self.tpLog.debug('Model.ProcessWorkEventList')
            processedManifest = Model.ProcessWorkEventList()
            processedManifest.writeTpWorkEventListAsJson(translatedManifest)
            tpManifestHeader = processedManifest.makeTpHeader(translatedManifest)
            tpManifestLocations = processedManifest.makeTpLocations(translatedManifest)

            self.tpLog.debug('Model.WriteWorkEventListToTp')
            Model.WriteWorkEventListToTp(tpManifestHeader + tpManifestLocations).asCsv()

            self.tpLog.info('Export JMRI manifest to TrainPlyer: ' + self.train.getName())
        else:
            self.tpLog.warning('TrainPlayer Reports directory not found, manifest export did not complete')


        self.tpLog.info('Export to TrainPlayer script location: ' + PLUGIN_ROOT)
        self.tpLog.info('Manifest export (sec): ' + ('%s' % (time.time() - timeNow))[:6])
        print(self.SCRIPT_NAME + ' ' + str(self.SCRIPT_REV))
        print('Manifest export (sec): ' + ('%s' % (time.time() - timeNow))[:6])

        self.standAloneLogging.stopLogging()

        return False

if __name__ == "__builtin__":

    PLUGIN_ROOT = jmri.util.FileUtil.getPreferencesPath() + SCRIPT_DIR
    sysPath.append(PLUGIN_ROOT)
    from psEntities import PatternScriptEntities
    from TrainPlayerSubroutine import Model

    PatternScriptEntities.ENCODING = 'utf-8'

    tpManifest = ManifestForTrainPlayer()
    newestTrain = tpManifest.getNewestTrain()
    if newestTrain:
        tpManifest.passInTrain(newestTrain)
        tpManifest.start()

else:

    PLUGIN_ROOT = jmri.util.FileUtil.getPreferencesPath() + SCRIPT_DIR
    from psEntities import PatternScriptEntities
    from TrainPlayerSubroutine import Model

"""
Exports a JMRI manifest into a csv for import into the TrainPlayer Quick Keys script suite.
Callable from the pattern scripts subroutine or stand alone.
"""

import jmri
import time

SCRIPT_NAME ='OperationsPatternScripts.o2oSubroutine.BuiltTrainExport'
SCRIPT_REV = 20230201

SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b1'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b2'


class StandAloneLogging():
    """Called when this script is used by itself"""

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


class FindTrain:
    """ """

    def __init__(self):

        self.o2oLog = PSE.LOGGING.getLogger('TP.FindTrain')

        self.builtTrainList = []

        return
        
    def findNewestTrain(self):
        """If more than 1 train is built, pick the newest one"""

        self.o2oLog.debug('findNewestTrain')

        if not PSE.TM.isAnyTrainBuilt():

            return

        newestBuildTime = ''
        for train in self.getBuiltTrains():
            testDate = self.getTrainBuiltDate(train)
            if testDate > newestBuildTime:
                newestBuildTime = testDate
                newestTrain = train

        return newestTrain

    def getBuiltTrains(self):

        self.o2oLog.debug('getBuiltTrains')

        for train in PSE.TM.getTrainsByStatusList():
            if train.isBuilt():
                self.builtTrainList.append(train)

        return self.builtTrainList

    # def resetBuildTrains(self):

    #     for train in self.builtTrainList:
    #         train.reset()

    #     return

    def getTrainBuiltDate(self, train):

        manifest = jmri.util.FileUtil.readFile(jmri.jmrit.operations.trains.JsonManifest(train).getFile())

        return PSE.loadJson(manifest)['date']


class o2oWorkEventsBuilder(jmri.jmrit.automat.AbstractAutomaton):
    """Runs when a JMRI train is built"""

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

        startTime = time.time()

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

        runTime = time.time() - startTime
        self.o2oLog.info('Manifest export (sec): ' + str(round(runTime, 4)))

        print(self.SCRIPT_NAME + ' ' + str(SCRIPT_REV))
        print('Manifest export (sec): ' + str(round(runTime, 4)))

        self.standAloneLogging.stopLogging()

        return False

if __name__ == "__builtin__":

    import jmri
    from sys import path as sysPath
    from os import path as osPath

    PLUGIN_ROOT = osPath.join(jmri.util.FileUtil.getPreferencesPath(), SCRIPT_DIR)
    sysPath.append(PLUGIN_ROOT)

    from opsEntities import PSE
    from Subroutines.o2o import ModelWorkEvents
    from Subroutines.o2o import ModelEntities
    from opsBundle import Bundle

    Bundle.BUNDLE_DIR = PSE.OS_PATH.join(PLUGIN_ROOT, 'opsBundle')

    PSE.PLUGIN_ROOT = PLUGIN_ROOT
    PSE.BUNDLE = Bundle.getBundleForLocale()
    PSE.ENCODING = 'utf-8'

    tpManifest = o2oWorkEventsBuilder()
    newestTrain = tpManifest.getNewestTrain()
    if newestTrain:
        tpManifest.passInTrain(newestTrain)
        tpManifest.start()

else:

    from os import path as osPath

    PLUGIN_ROOT = osPath.join(jmri.util.FileUtil.getPreferencesPath(), SCRIPT_DIR)

    from opsEntities import PSE
    from Subroutines.o2o import ModelWorkEvents
    from Subroutines.o2o import ModelEntities

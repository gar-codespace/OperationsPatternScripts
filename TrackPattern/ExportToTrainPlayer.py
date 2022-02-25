# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import logging
from json import loads as jsonLoads, load as jsonLoad, dumps as jsonDumps
from HTMLParser import HTMLParser
from codecs import open as codecsOpen
from os import mkdir as osMakeDir

try:
    import psEntities.MainScriptEntities
    setEncoding = psEntities.MainScriptEntities.setEncoding()
except ImportError:
    setEncoding = 'utf-8'

scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer'
scriptRev = 20220101


class CheckTpDestination():
    '''Verify or create a TrainPlayer destination directory'''

    def __init__(self):
        self.scriptName = 'OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.CheckTpDestination'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.CheckTpDestination')

        return

    def directoryExists(self):

        try:
            osMakeDir(jmri.util.FileUtil.getHomePath() + 'AppData\\Roaming\\TrainPlayer\\Reports')
            self.psLog.warning('TrainPlayer destination directory created')
        except OSError:
            self.psLog.info('TrainPlayer destination directory OK')

        print(scriptName + ' ' + str(scriptRev))

        return

class ExportJmriLocations():
    '''Writes a list of location names and comments for the whole profile'''

    def __init__(self):
        self.scriptName = 'OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.LocationsForTrainPlayer'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.ExportJmriLocations')
        self.jLM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        self.toLoc = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Locations.csv"

        return

    def toTrainPlayer(self):
        '''Exports JMRI location name/location comment pairs for TP Advanced Ops'''

        eMessage = 'No missing entries for location export for TrainPlayer'
        locationList = self.jLM.getLocationsByIdList()
        with codecsOpen(self.toLoc, 'wb', encoding=setEncoding) as csvWorkFile:
            csvLocations = u'Locale,Industry\n'
            for location in locationList:
                jLocTrackList = location.getTrackIdsByIdList()
                for track in jLocTrackList:
                    jTrackId = location.getTrackById(track)
                    jLocale = unicode(location.getName(), setEncoding) + u';' + unicode(jTrackId.getName(), setEncoding)
                    jTrackComment = unicode(jTrackId.getComment(), setEncoding)
                    if not (jTrackComment):
                        jTrackComment = 'Null'
                        eMessage = 'Missing location comment entries for JMRI locations export to TrainPlayer'
                    csvLocations = csvLocations + jLocale + ',' + jTrackComment + '\n'
            csvWorkFile.write(csvLocations)
        self.psLog.info(eMessage)
        print(self.scriptName + ' ' + str(scriptRev))

        return

class TrackPatternTranslationToTp():
    '''Translate Track Patterns from OperationsPatternScripts to TrainPlayer format'''

    def __init__(self, body=None):

        self.body = body
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.TrackPatternTranslationToTp'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.TrackPatternTranslationToTp')

        return

    def modifySwitchList(self):
        '''Replaces car['Set to'] = [ ] with the track comment'''

        self.psLog.debug('modifySwitchList')
        location = psEntities.MainScriptEntities.readConfigFile('TP')['PL']
        lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)

        for loco in self.body['Locos']:
            if 'Hold' in loco['Set to']:
                loco['Set to'] = lm.getLocationByName(location).getTrackByName(loco['Track'], None).getComment()
            else:
                loco['Set to'] = lm.getLocationByName(location).getTrackByName(loco['Set to'], None).getComment()

        for car in self.body['Cars']:
            if 'Hold' in car['Set to']:
                car['Set to'] = lm.getLocationByName(location).getTrackByName(car['Track'], None).getComment()
            else:
                car['Set to'] = lm.getLocationByName(location).getTrackByName(car['Set to'], None).getComment()

        return self.body

    def appendSwitchList(self):

        self.psLog.debug('appendSwitchList')
        reportTitle = psEntities.MainScriptEntities.readConfigFile('TP')['RT']['TP']
        jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
        with codecsOpen(jsonFile, 'r', encoding=psEntities.MainScriptEntities.setEncoding()) as jsonWorkFile:
            jsonSwitchList = jsonWorkFile.read()
        switchList = jsonLoads(jsonSwitchList)
        switchListName = switchList['description']
        try:
            trackDetailList = switchList['tracks']
            locoList = trackDetailList[0]['Locos']
            locoList += self.body['Locos']
            trackDetailList[0]['Locos'] = locoList
            carList = trackDetailList[0]['Cars']
            carList += self.body['Cars']
            trackDetailList[0]['Cars'] = carList
        except KeyError:
            switchList['tracks'] = [self.body]

        return switchList

class JmriTranslationToTp():
    '''Translate manifests from JMRI to TrainPlayer format'''

    def __init__(self, inputList=None):

        self.inputList = inputList
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.JmriTranslationToTp'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.JmriTranslationToTp')

        self.comment = u'Train comment place holder'
        self.jTM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.trains.TrainManager)

        return

    def findNewestManifest(self):
        '''If more than 1 train is built, pick the newest one'''

        if self.jTM.isAnyTrainBuilt():
            trainListByStatus = self.jTM.getTrainsByStatusList()
            newestBuildTime = ''
            for train in trainListByStatus:
                if train.isBuilt():
                    workEventFile =  jmri.util.FileUtil.getProfilePath() + 'operations\jsonManifests\\train-' + train.getName() + ".json"
                    with open(workEventFile) as workEventObject:
                        workEventList = jsonLoad(workEventObject)
                    if workEventList[u'date'] > newestBuildTime:
                        newestBuildTime = workEventList[u'date']
                        newestTrain = workEventList
                        trainComment = train.getComment()
            self.psLog.info('Train ' + newestTrain['userName'] + ' is newest')
        else:
            self.psLog.info('No trains are built')

        return newestTrain, trainComment

class ProcessWorkEventList():
    '''Process the translated work event lists as a CSV list formatted for the TrainPlayer side scripts'''

    def __init__(self, input=None):

        self.inputList = input
        self.switchListName = input
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.ProcessWorkEventList'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.ProcessWorkEventList')

        self.comment = u'Train comment place holder'
        self.jTM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.trains.TrainManager)

        return

    def writeWorkEventListAsJson(self):

        self.psLog.debug('writeWorkEventListAsJson')
        reportTitle = self.inputList['description']
        jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
        jsonObject = jsonDumps(self.inputList, indent=2, sort_keys=True)
        with codecsOpen(jsonFile, 'wb', encoding=psEntities.MainScriptEntities.setEncoding()) as jsonWorkFile:
            jsonWorkFile.write(jsonObject)

        return reportTitle

    def readFromFile(self):

        self.psLog.debug('readFromFile')
        try:
            jsonCopyFrom = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + self.switchListName + '.json'
            self.psLog.debug('TrainPlayer switch list read from file')
        except:
            self.psLog.critical('TrainPlayer switch list could not be read')
            return

        with codecsOpen(jsonCopyFrom, 'r', encoding=setEncoding) as jsonWorkFile:
            jsonSwitchList = jsonWorkFile.read()

        print(self.scriptName + ' ' + str(self.scriptRev))

        return jsonLoads(jsonSwitchList)

    def makeHeader(self):

        self.psLog.debug('makeHeader')
        # https://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
        header = 'HN,' + HTMLParser().unescape(self.inputList['railroad']) + '\n'
        header += 'HT,' + HTMLParser().unescape(self.inputList['userName']) + '\n'
        header += 'HD,' + HTMLParser().unescape(self.inputList['description']) + '\n'
        header += 'HC,' + self.comment + '\n'
        header += 'HV,' + HTMLParser().unescape(self.inputList['date']) + '\n'
        header += u'WT,' + str(len(self.inputList['tracks'])) + '\n'

        return header

    def makeBody(self):

        self.psLog.debug('makeBody')
        locoLines = ''
        carLines = ''
        x = 1
        for track in self.inputList['tracks']:
            workEventNumber = u'WE,' + str(x) + ',' + HTMLParser().unescape(track['Name'])

            if track['Locos']:
                for loco in track['Locos']:
                    locoLines += '\n' + ",".join(self.parseLoco(loco))
            else:
                self.psLog.info('No locomotives in list')

            if track['Cars']:
                for car in track['Cars']:
                    carLines += '\n' + ",".join(self.parseCar(car))
            else:
                self.psLog.info('No cars in list')

            x += 1

        return workEventNumber + locoLines + carLines

    def parseLoco(self, xLoco):

        return [xLoco[u'PUSO'], xLoco[u'Road'] + xLoco[u'Number'], xLoco[u'Road'], xLoco[u'Number'], u'O', xLoco[u'Track'], xLoco[u'Set to']]

    def parseCar(self, xCar):

        return [xCar[u'PUSO'], xCar[u'Road'] + xCar[u'Number'], xCar[u'Road'], xCar[u'Number'], xCar[u'Load'], xCar[u'Track'], xCar[u'Set to']]

class WriteWorkEventListToTp():

    def __init__(self, workEventList):

        self.workEventList = workEventList
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.writeWorkEventListToTp'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.WriteWorkEventListToTp')
        return

    def asCsv(self):

        self.psLog.debug('asCsv')
        weCopyTo = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Work Events.csv"
        with codecsOpen(weCopyTo, 'wb', encoding=setEncoding) as csvWorkFile:
            csvWorkFile.write(self.workEventList)

        return

class ManifestForTrainPlayer(jmri.jmrit.automat.AbstractAutomaton):
    '''Processes a manifest built from the JMRI trains panel'''

    def init(self):
        self.scriptName = 'OperationsExportToTrainPlayer.ManifestForTrainPlayer'
        self.scriptRev = 20220101
    # fire up logging
        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\ManifestScript.txt'
        self.psLog = logging.getLogger('MS')
        self.psLog.setLevel(10)
        logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        msFileHandler = logging.FileHandler(logPath, mode='w', encoding='utf-8')
        psFileHandler.setFormatter(logFileFormat)
        self.psLog.addHandler(msFileHandler)
        self.psLog.debug('Log File for Pattern Scripts Plugin - debug level initialized')
        self.psLog.info('Log File for Pattern Scripts Plugin - info level initialized')
        self.psLog.warning('Log File for Pattern Scripts Plugin - warning level initialized')
        self.psLog.error('Log File for Pattern Scripts Plugin - error level initialized')
        self.psLog.critical('Log File for Pattern Scripts Plugin - critical level initialized')
    # Boilerplate
        self.jTM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.trains.TrainManager)
        self.jProfilePath = jmri.util.FileUtil.getProfilePath()

        return

    def handle(self):

        OperationsExportToTrainPlayer.CheckTpDestination().directoryExists()

        self.psLog.removeHandler(msFileHandler)

        return False

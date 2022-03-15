import jmri
import logging
import time
from json import loads as jsonLoads, dumps as jsonDumps
from HTMLParser import HTMLParser
from codecs import open as codecsOpen
from os import mkdir as osMakeDir

try:
    from psEntities import MainScriptEntities
    _lm = MainScriptEntities._lm
    _tm = MainScriptEntities._tm
    _setEncoding = MainScriptEntities.setEncoding()
except ImportError:
    _lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
    _tm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.trains.TrainManager)
    _setEncoding = 'utf-8'

scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer'
scriptRev = 20220101

_jmriLocationsPath = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Locations.csv"
_jmriManifestPath = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Work Events.csv"

class CheckTpDestination():
    '''Verify or create a TrainPlayer destination directory'''

    def __init__(self):
        self.scriptName = 'OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.CheckTpDestination'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.CheckTpDestination')
        self.tpLog = logging.getLogger('TP.CheckTpDestination')

        return

    def directoryExists(self):

        try:
            osMakeDir(jmri.util.FileUtil.getHomePath() + 'AppData\\Roaming\\TrainPlayer\\Reports')
            self.psLog.warning('TrainPlayer destination directory created')
            self.tpLog.warning('TrainPlayer destination directory created')
        except OSError:
            self.psLog.info('TrainPlayer destination directory OK')
            self.tpLog.info('TrainPlayer destination directory OK')

        print(scriptName + ' ' + str(scriptRev))

        return

class ExportJmriLocations():
    '''Writes a list of location names and comments for the whole profile'''

    def __init__(self):
        self.scriptName = 'OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.LocationsForTrainPlayer'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.ExportJmriLocations')
        self.tpLog = logging.getLogger('TP.ExportJmriLocations')

        return

    def makeLocationList(self):
        '''Creates the TrainPlayer Advanced Ops compatable JMRI location list'''

        i = 0
        csvLocations = ''
        for locationId in _lm.getLocationsByIdList():
            for trackId in locationId.getTrackIdsByIdList():
                track = locationId.getTrackById(trackId)
                aoLocale = unicode(locationId.getName(), _setEncoding) + u';' + unicode(track.getName(), _setEncoding)
                trackComment = unicode(track.getComment(), _setEncoding)
                if not (trackComment):
                    i += 1
                csvLocations += aoLocale + ',' + trackComment + '\n'

        self.psLog.info(str(i) + ' missing track comments for locations export to TrainPlayer')
        self.tpLog.info(str(i) + ' missing track comments for locations export to TrainPlayer')
        print(self.scriptName + ' ' + str(scriptRev))

        return csvLocations

    def toTrainPlayer(self, csvLocations):
        '''Exports JMRI location;track pairs and track comments for TP Advanced Ops'''

        with codecsOpen(_jmriLocationsPath, 'wb', encoding=_setEncoding) as csvWorkFile:
            csvHeader = u'Locale,Industry\n'
            csvWorkFile.write(csvHeader + csvLocations)

        print(self.scriptName + ' ' + str(scriptRev))

        return

class TrackPatternTranslationToTp():
    '''Translate Track Patterns from OperationsPatternScripts for TrainPlayer O2O script compatability'''

    def __init__(self):

        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.TrackPatternTranslationToTp'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.TrackPatternTranslationToTp')
        self.tpLog = logging.getLogger('TP.TrackPatternTranslationToTp')

        return

    def modifySwitchList(self, setCarsForm, textBoxEntry):
        '''Replaces car['Set to'] = [ ] with the track comment'''

        self.psLog.debug('modifySwitchList')
        self.tpLog.debug('modifySwitchList')

        location = setCarsForm['locations'][0]['locationName']
        trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
        locationTracks = _lm.getLocationByName(location).getTracksList()
        trackList = []
        for track in locationTracks:
            trackList.append(track.getName())

        userInputList = []
        for userInput in textBoxEntry:
            inputText = unicode(userInput.getText(), MainScriptEntities.setEncoding())
            if inputText in trackList:
                userInputList.append(inputText)
            else:
                userInputList.append(trackName)

        i = 0
        locoList = []
        for loco in setCarsForm['locations'][0]['tracks'][0]['locos']:
            loco['Set to'] = location + ';' + userInputList[i]
            locoList.append(loco)
            i += 1
        setCarsForm['locations'][0]['tracks'][0]['locos'] = locoList

        carList = []
        for car in setCarsForm['locations'][0]['tracks'][0]['cars']:
            car['Set to'] = location + ';' +  userInputList[i]
            carList.append(car)
            i += 1
        setCarsForm['locations'][0]['tracks'][0]['cars'] = carList

        return setCarsForm

    def appendSwitchList(self, modifiedForm):

        self.psLog.debug('appendSwitchList')
        self.tpLog.debug('appendSwitchList')

        headerNames = MainScriptEntities.readConfigFile('TP')
        reportTitle = headerNames['TD']['TP']
        jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
        with codecsOpen(jsonFile, 'r', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
            jsonSwitchList = jsonWorkFile.read()
        tpSwitchList = jsonLoads(jsonSwitchList)

        for loco in modifiedForm['locations'][0]['tracks'][0]['locos']:
            tpSwitchList['locations'][0]['tracks'][0]['locos'].append(loco)

        for car in modifiedForm['locations'][0]['tracks'][0]['cars']:
            tpSwitchList['locations'][0]['tracks'][0]['cars'].append(car)

        return tpSwitchList

class JmriTranslationToTp():
    '''Translate manifests from JMRI for TrainPlayer O2O script compatability'''

    def __init__(self):

        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.JmriTranslationToTp'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.JmriTranslationToTp')
        self.tpLog = logging.getLogger('TP.JmriTranslationToTp')

        return

    def findNewestManifest(self):
        '''If more than 1 train is built, pick the newest one'''

        if not _tm.isAnyTrainBuilt():
            self.psLog.info('No trains are built')
            self.tpLog.info('No trains are built')

            return

        newestBuildTime = ''
        for train in self.getBuiltTrains():
            trainAsDict = self.getTrainAsDict(train)
            if trainAsDict['date'] > newestBuildTime:
                newestBuildTime = trainAsDict['date']
                newestTrain = trainAsDict

        self.psLog.info('Train ' + newestTrain[u'userName'] + ' is newest')
        self.tpLog.info('Train ' + newestTrain[u'userName'] + ' is newest')

        return newestTrain

    def getBuiltTrains(self):

        builtTrainList = []
        for train in _tm.getTrainsByStatusList():
            if train.isBuilt():
                builtTrainList.append(train)

        return builtTrainList

    def getTrainAsDict(self, train):

        manifest = jmri.util.FileUtil.readFile(jmri.jmrit.operations.trains.JsonManifest(train).getFile())
        trainAsDict = jsonLoads(manifest)
        trainAsDict['comment'] = train.getComment()

        return trainAsDict

    def translateManifestHeader(self, completeJmriManifest):

        self.psLog.debug('translateManifestHeader')
        self.tpLog.debug('translateManifestHeader')

        jmriDateAsEpoch = self.convertJmriDateToEpoch(completeJmriManifest[u'date'])
        completeJmriManifest['date'] = self.jmriTimeStamp(jmriDateAsEpoch)
        completeJmriManifest['trainDescription'] = 'TrainPlayer Work Events'
        completeJmriManifest['trainName'] = completeJmriManifest['userName']
        completeJmriManifest['trainComment'] = completeJmriManifest['comment']
        completeJmriManifest.pop('description', 'Description')
        completeJmriManifest.pop('userName', 'Name')
        completeJmriManifest.pop('comment', 'Comment')

        return completeJmriManifest

    def translateManifestBody(self, completeJmriManifest):

        self.psLog.debug('translateManifestBody')
        self.tpLog.debug('translateManifestBody')

        locationList = []
        for location in completeJmriManifest[u'locations']:

            tpLocation = {}
            locationName = location['userName']
            tpLocation['locationName'] = location['userName']
            tpLocation['tracks'] = []

            locoList = []
            carList = []
            for loco in location[u'engines'][u'add']:
                line = self.parseRollingStockAsDict(loco, locationName)
                line['PUSO'] = 'PL'
                locoList.append(line)
            for loco in location[u'engines'][u'remove']:
                line = self.parseRollingStockAsDict(loco, locationName)
                line['PUSO'] = 'SL'
                locoList.append(line)
            for car in location['cars']['add']:
                line = self.parseRollingStockAsDict(car, locationName)
                line['PUSO'] = 'PC'
                carList.append(line)
            for car in location['cars']['remove']:
                line = self.parseRollingStockAsDict(car, locationName)
                line['PUSO'] = 'SC'
                carList.append(line)

            locationTrack = {}
            locationTrack['locos'] = locoList
            locationTrack['cars'] = carList
            locationTrack['trackName'] = 'Track Name'
            locationTrack['length'] = 0

            tpLocation['tracks'].append(locationTrack)

            locationList.append(tpLocation)

        return locationList

    def parseRollingStockAsDict(self, rS, lN):

        rsDict = {}
        rsDict['Road'] = rS[u'road']
        rsDict['Number'] = rS[u'number']

        try:
            rsDict[u'Model'] = rS[u'model']
        except KeyError:
            rsDict[u'Model'] = 'N/A'
        try:
            rsDict[u'Type'] = rS[u'carType'] + "-" + rS[u'carSubType']
        except:
            rsDict[u'Type'] = rS[u'carType']
        try:
            rsDict[u'Load'] = rS['load']
        except:
            rsDict[u'Load'] = 'O'
        rsDict[u'Length'] = rS[u'length']
        rsDict[u'Weight'] = rS[u'weightTons']
        rsDict[u'Track'] = rS[u'location'][u'track'][u'userName']
        rsDict[u'Set to'] = lN + ';' + rS[u'destination'][u'track'][u'userName']
        try:
            jFinalDestination = rS[u'finalDestination'][u'userName']
            try:
                jFinalTrack = rS[u'finalDestination'][u'track'][u'userName']
            except KeyError:
                jFinalTrack = 'Any'
            rsDict[u'FD&Track'] = jFinalDestination + ';' + jFinalTrack
        except:
            rsDict[u'FD&Track'] = rS[u'destination'][u'userName'] + ';' + rS[u'destination'][u'track'][u'userName']

        return rsDict

    def convertJmriDateToEpoch(self, jmriTime):
        '''2022-02-26T17:16:17.807+0000'''

        return time.mktime(time.strptime(jmriTime, "%Y-%m-%dT%H:%M:%S.%f+0000"))

    def jmriTimeStamp(self, jmriTime):
        '''Valid Time, get local time adjusted for time zone and dst'''

        if time.localtime(jmriTime).tm_isdst and time.daylight: # If local dst and dst are both 1
            timeOffset = time.altzone
        else:
            timeOffset = time.timezone # in seconds

        return time.strftime('%a %b %d %Y %I:%M %p %Z', time.gmtime(jmriTime + timeOffset))

class ProcessWorkEventList():
    '''Process the translated work event lists to a CSV list formatted for the TrainPlayer side scripts'''

    def __init__(self):

        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.ProcessWorkEventList'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.ProcessWorkEventList')
        self.tpLog = logging.getLogger('TP.ProcessWorkEventList')

        return

    def makeTpHeader(self, appendedTpSwitchList):
        '''The jason manifest is encoded in HTML Entity'''
        # csv writer does not encode utf-8

        self.psLog.debug('makeTpHeader')
        self.tpLog.debug('makeTpHeader')
        # https://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
        header = 'HN,' + HTMLParser().unescape(appendedTpSwitchList['railroad']) + '\n'
        header += 'HT,' + HTMLParser().unescape(appendedTpSwitchList['trainName']) + '\n'
        header += 'HD,' + HTMLParser().unescape(appendedTpSwitchList['trainDescription']) + '\n'
        header += 'HC,' + HTMLParser().unescape(appendedTpSwitchList['trainComment']) + '\n'
        header += 'HV,' + HTMLParser().unescape(appendedTpSwitchList['date']) + '\n'
        header += u'WT,' + str(len(appendedTpSwitchList['locations'])) + '\n'

        return header

    def makeTpLocations(self, appendedTpSwitchList):
        '''The jason manifest is encoded in HTML Entity'''
        # csv writer does not encode utf-8

        self.psLog.debug('makeTpLocations')
        self.tpLog.debug('makeTpLocations')

        tpLocations = ''

        i = 1
        for location in appendedTpSwitchList['locations']:
            tpLocations += u'WE,' + str(i) + ',' + HTMLParser().unescape(location['locationName']) + '\n'
            for track in location['tracks']:
                for loco in track['locos']:
                    tpLocations += ",".join(self.makeLine(loco)) + '\n'
                for car in track['cars']:
                    tpLocations += ",".join(self.makeLine(car)) + '\n'
            i += 1

        return tpLocations + '\n'

    def makeLine(self, rS):

        return [rS[u'PUSO'], rS[u'Road'] + rS[u'Number'], rS[u'Road'], rS[u'Number'], rS[u'Load'], rS[u'Track'], rS[u'Set to'], rS['FD&Track']]

    def writeWorkEventListAsJson(self, appendedTpSwitchList):

        self.psLog.debug('writeWorkEventListAsJson')
        self.tpLog.debug('writeWorkEventListAsJson')

        reportTitle = appendedTpSwitchList['trainDescription']
        jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
        jsonObject = jsonDumps(appendedTpSwitchList, indent=2, sort_keys=True)
        with codecsOpen(jsonFile, 'wb', encoding=_setEncoding) as jsonWorkFile:
            jsonWorkFile.write(jsonObject)

        return

class WriteWorkEventListToTp():

    def __init__(self, workEventList):

        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.writeWorkEventListToTp'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.WriteWorkEventListToTp')
        self.tpLog = logging.getLogger('TP.WriteWorkEventListToTp')

        self.workEventList = workEventList

        return

    def asCsv(self):

        self.psLog.debug('asCsv')
        self.tpLog.debug('asCsv')

        with codecsOpen(_jmriManifestPath, 'wb', encoding=_setEncoding) as csvWorkFile:
            csvWorkFile.write(self.workEventList)

        return

class ManifestForTrainPlayer(jmri.jmrit.automat.AbstractAutomaton):
    '''Runs on JMRI train manifest builds'''

    def init(self):
        self.scriptName = 'ExportToTrainPlayer.ManifestForTrainPlayer'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.ManifestForTrainPlayer')

        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\TrainPlayerScriptsLog.txt'
        self.tpLog = logging.getLogger('TP')
        self.tpLog.setLevel(10)
        logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.tpFileHandler = logging.FileHandler(logPath, mode='w', encoding=_setEncoding)
        self.tpFileHandler.setFormatter(logFileFormat)
        self.tpLog.addHandler(self.tpFileHandler)
        self.tpLog.debug('Log File for Pattern Scripts Plugin - debug level test message')
        self.tpLog.info('Log File for Pattern Scripts Plugin - info level test message')
        self.tpLog.warning('Log File for Pattern Scripts Plugin - warning level test message')
        self.tpLog.error('Log File for Pattern Scripts Plugin - error level test message')
        self.tpLog.critical('Log File for Pattern Scripts Plugin - critical level test message')

        self.jProfilePath = jmri.util.FileUtil.getProfilePath()

        return

    def handle(self):

        timeNow = time.time()

        CheckTpDestination().directoryExists()

        jmriExport = ExportJmriLocations()
        locationList = jmriExport.makeLocationList()
        jmriExport.toTrainPlayer(locationList)

        jmriManifestTranslator = JmriTranslationToTp()
        newestTrain = jmriManifestTranslator.findNewestManifest()
        if newestTrain:
            translatedManifest = jmriManifestTranslator.translateManifestHeader(newestTrain)
            translatedManifest['locations'] = jmriManifestTranslator.translateManifestBody(newestTrain)

            processedManifest = ProcessWorkEventList()
            processedManifest.writeWorkEventListAsJson(translatedManifest)
            tpManifestHeader = processedManifest.makeTpHeader(translatedManifest)
            tpManifestLocations = processedManifest.makeTpLocations(translatedManifest)

            WriteWorkEventListToTp(tpManifestHeader + tpManifestLocations).asCsv()

        self.psLog.info('Manifest export (sec): ' + ('%s' % (time.time() - timeNow))[:6])
        self.tpLog.info('Manifest export (sec): ' + ('%s' % (time.time() - timeNow))[:6])

        print(self.scriptName + ' ' + str(self.scriptRev))
        print('Manifest export (sec): ' + ('%s' % (time.time() - timeNow))[:6])

        return False

if __name__ == "__builtin__":
    ManifestForTrainPlayer().start()

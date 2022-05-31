# coding=utf-8
# © 2021, 2022 Greg Ritacco

from json import loads as jsonLoads, dumps as jsonDumps
from codecs import open as codecsOpen

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.Model'
SCRIPT_REV = 20220101

psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.Model')

class ExportJmriLocations:
    """Writes a list of location names and comments for the whole profile"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ExportJmriLocations')

        return

    def makeLocationList(self):
        """Creates the TrainPlayer Advanced Ops compatable JMRI location list"""

        csvLocations = ''
        i = 0
        for location in PatternScriptEntities.LM.getLocationsByIdList():
            tracks = location.getTracksList()
            for track in tracks:
                aoLocale = unicode(location.getName(), PatternScriptEntities.ENCODING) \
                    + u';' + unicode(track.getName(), PatternScriptEntities.ENCODING)
                trackComment = unicode(track.getComment(), PatternScriptEntities.ENCODING)
                if not trackComment:
                    i += 1
                csvLocations += aoLocale + ',' + trackComment + '\n'

        self.psLog.info(str(i) + ' missing track comments for locations export to TrainPlayer')

        return csvLocations

    def toTrainPlayer(self, csvLocations):
        """Exports JMRI location;track pairs and track comments for TrainPlayer Advanced Ops"""

        if PatternScriptEntities.CheckTpDestination().directoryExists():

            jmriLocationsPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() \
                    + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Locations.csv"

            jmriLocationsFile = u'Locale,Industry\n' + csvLocations
            PatternScriptEntities.genericWriteReport(jmriLocationsPath, jmriLocationsFile)

            self.psLog.info('TrainPlayer locations export completed')

        print(SCRIPT_NAME + '.ExportJmriLocations ' + str(SCRIPT_REV))

        return

class TrackPatternTranslationToTp:
    """Translate Track Patterns from OperationsPatternScripts for TrainPlayer O2O script compatability"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.TrainPlayerTranslationToTp')

        return

    def modifySwitchList(self, setCarsForm, textBoxEntry):
        """Replaces car['Set to'] = [ ] with the track comment"""

        self.psLog.debug('PatternTracksExport.modifySwitchList')

        location = setCarsForm['locations'][0]['locationName']
        trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
        locationTracks = PatternScriptEntities.LM.getLocationByName(location).getTracksList()
        trackList = []
        for track in locationTracks:
            trackList.append(track.getName())

        userInputList = []
        for userInput in textBoxEntry:
            inputText = unicode(userInput.getText(), PatternScriptEntities.ENCODING)
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

        self.psLog.debug('PatternTracksExport.appendSwitchList')

        headerNames = PatternScriptEntities.readConfigFile('PT')
        reportTitle = PatternScriptEntities.BUNDLE['Work Event List for TrainPlayer']
        # reportTitle = headerNames['TD']['TP']
        jsonFile = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + reportTitle + '.json'
        with codecsOpen(jsonFile, 'r', encoding=PatternScriptEntities.ENCODING) as jsonWorkFile:
            jsonSwitchList = jsonWorkFile.read()
        tpSwitchList = jsonLoads(jsonSwitchList)

        for loco in modifiedForm['locations'][0]['tracks'][0]['locos']:
            tpSwitchList['locations'][0]['tracks'][0]['locos'].append(loco)

        for car in modifiedForm['locations'][0]['tracks'][0]['cars']:
            tpSwitchList['locations'][0]['tracks'][0]['cars'].append(car)

        return tpSwitchList

class JmriTranslationToTp:
    """Translate manifests from JMRI for TrainPlayer o2o script compatability"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.JmriTranslationToTp')

        print(SCRIPT_NAME + '.JmriTranslationToTp ' + str(SCRIPT_REV))

        return

    def getTrainAsDict(self, train):

        manifest = PatternScriptEntities.JMRI.util.FileUtil.readFile( \
                PatternScriptEntities.JMRI.jmrit.operations.trains.JsonManifest(train).getFile() \
                )
        trainAsDict = jsonLoads(manifest)
        trainAsDict['comment'] = train.getComment()

        return trainAsDict

    def translateManifestHeader(self, completeJmriManifest):

        self.psLog.debug('Model.translateManifestHeader')

        jmriDateAsEpoch = ModelEntities.convertJmriDateToEpoch(completeJmriManifest[u'date'])
        completeJmriManifest['date'] = PatternScriptEntities.timeStamp(jmriDateAsEpoch)
        completeJmriManifest['trainDescription'] = completeJmriManifest['description']
        completeJmriManifest['trainName'] = completeJmriManifest['userName']
        completeJmriManifest['trainComment'] = completeJmriManifest['comment']
        completeJmriManifest.pop('description', 'Description')
        completeJmriManifest.pop('userName', 'Name')
        completeJmriManifest.pop('comment', 'Comment')

        return completeJmriManifest

    def translateManifestBody(self, completeJmriManifest):

        self.psLog.debug('Model.translateManifestBody')

        locationList = []
        for location in completeJmriManifest[u'locations']:
            tpLocation = ModelEntities.parseJmriLocations(location)
            locationList.append(tpLocation)

        return locationList

class ProcessWorkEventList:
    """Process the translated work event lists to a CSV list formatted for the TrainPlayer o2o scripts"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ProcessWorkEventList')

        return

    def makeTpHeader(self, appendedTpSwitchList):
        """The jason manifest is encoded in HTML Entity"""
        # csv writer does not encode utf-8

        self.psLog.debug('Model.makeTpHeader')

        header = 'HN,' + appendedTpSwitchList['railroad'] + '\n'
        header += 'HT,' + appendedTpSwitchList['trainName'] + '\n'
        header += 'HD,' + appendedTpSwitchList['trainDescription'] + '\n'
        header += 'HC,' + appendedTpSwitchList['trainComment'] + '\n'
        header += 'HV,' + appendedTpSwitchList['date'] + '\n'
        header += u'WT,' + str(len(appendedTpSwitchList['locations'])) + '\n'

        return header

    def makeTpLocations(self, appendedTpSwitchList):
        """The jason manifest is encoded in HTML Entity"""
        # csv writer does not encode utf-8

        self.psLog.debug('Model.makeTpLocations')

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

        return [rS[u'PUSO'], rS[u'Road'] + rS[u'Number'], rS[u'Road'], rS[u'Number'], \
            rS[u'Load'], rS[u'Track'], rS[u'Set to'], rS['FD&Track']]

    def writeTpWorkEventListAsJson(self, appendedTpSwitchList):

        self.psLog.debug('Model.writeTpWorkEventListAsJson')

        reportTitle = appendedTpSwitchList['trainDescription']
        jsonReoprtPath = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + reportTitle + '.json'
        jsonReport = jsonDumps(appendedTpSwitchList, indent=2, sort_keys=True)
        PatternScriptEntities.genericWriteReport(jsonReoprtPath, jsonReport)

        print(SCRIPT_NAME + '.ProcessWorkEventList ' + str(SCRIPT_REV))

        return

class WriteWorkEventListToTp:

    def __init__(self, workEventList):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.WriteWorkEventListToTp')

        self.jmriManifestPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() \
                + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Work Events.csv"
        self.workEventList = workEventList

        return

    def asCsv(self):

        self.psLog.debug('Model.WriteWorkEventListToTp.asCsv')

        if PatternScriptEntities.CheckTpDestination().directoryExists():
            PatternScriptEntities.genericWriteReport(self.jmriManifestPath, self.workEventList)

        print(SCRIPT_NAME + '.WriteWorkEventListToTp ' + str(SCRIPT_REV))

        return

class UpdateInventory:

    def __init__(self):

        self.errorReport = 'Update Inventory Error Report'
        self.setCarsError = ''
        self.notFoundError = ''

        tpInventory = ModelEntities.getTpInventory()
        self.tpInventoryList = ModelEntities.makeTpInventoryList(tpInventory)

        return

    def checkList(self):

        if self.tpInventoryList:
            return True
        else:
            return False

    def update(self):

        updatedInventory = ModelEntities.ProcessInventory()
        updatedInventory.makeJmriLocationList()

        for carLabel, trackLabel in self.tpInventoryList:

            rs = PatternScriptEntities.getRollingStock(carLabel)
            if not rs:
                continue

            setToLoc, setToTrack = updatedInventory.getSetToLocation(trackLabel)
            setResult = rs.setLocation(setToLoc, setToTrack)
            if setResult != 'okay':
                self.setCarsError += '\n' + setResult + \
                        PatternScriptEntities.BUNDLE[' for ID '] + rs.getId()

        self.notFoundError = updatedInventory.getErrorReport()

        print(SCRIPT_NAME + '.UpdateInventory ' + str(SCRIPT_REV))

        return

    def getErrorReport(self):

        self.errorReport += '\n\n' + PatternScriptEntities.BUNDLE['List of cars not updated'] + '\n'
        if self.setCarsError:
            self.errorReport += self.setCarsError
        else:
            self.errorReport += PatternScriptEntities.BUNDLE['No errors']

        self.errorReport += '\n\n' + PatternScriptEntities.BUNDLE['List of tracks not found'] + '\n'
        notFoundErrors = self.notFoundErrors()
        if notFoundErrors:
            self.errorReport += notFoundErrors
        else:
            self.errorReport += PatternScriptEntities.BUNDLE['No errors']

        return self.errorReport

    def notFoundErrors(self):

        processedErrors = ''
        for error in self.notFoundError:
            processedErrors += '\n' + PatternScriptEntities.BUNDLE['JMRI track comment not found: '] + error

        return processedErrors

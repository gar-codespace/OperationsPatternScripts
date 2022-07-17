# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.Model'
SCRIPT_REV = 20220101

class ExportJmriLocations:
    """Writes a list of location names and comments for the whole profile"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ExportJmriLocations')

        return

    def makeLocationHash(self):

        locationHash = {}

        for location in PatternScriptEntities.LM.getLocationsByIdList():
            locationName = unicode(location.getName(), PatternScriptEntities.ENCODING)
            tracks = location.getTracksList()
            for track in tracks:
                trackName = unicode(track.getName(), PatternScriptEntities.ENCODING)
                trackComment = unicode(track.getComment(), PatternScriptEntities.ENCODING)
                locationHash[locationName + u';' + trackName] = trackComment

        return locationHash

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
        reportTitle = PatternScriptEntities.BUNDLE[u'Work Event List for TrainPlayer©']
        jsonFile = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + reportTitle + '.json'
        jsonSwitchList = PatternScriptEntities.genericReadReport(jsonFile)
        tpSwitchList =  PatternScriptEntities.loadJson(jsonSwitchList)

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

        trainAsDict = PatternScriptEntities.loadJson(manifest)
        trainAsDict['comment'] = train.getComment()

        return trainAsDict

    def translateManifestHeader(self, completeJmriManifest):

        self.psLog.debug('Model.translateManifestHeader')

        jmriDateAsEpoch = PatternScriptEntities.convertJmriDateToEpoch(completeJmriManifest[u'date'])
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
        loadTypeRubric = ModelEntities.getLoadTypeRubric('OperationsCarRoster', './loads/load')

        for location in completeJmriManifest[u'locations']:
            tpLocation = ModelEntities.parseJmriLocations(location, loadTypeRubric)
            locationList.append(tpLocation)

        return locationList

class ProcessWorkEventList:
    """Process the translated work event lists to a CSV list formatted for the TrainPlayer o2o scripts"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ProcessWorkEventList')
        self.locationHash = ExportJmriLocations().makeLocationHash()

        return

    def makeTpHeader(self, appendedTpSwitchList):
        """The jason manifest is encoded in HTML Entity,
        csv writer does not encode utf-8,
        stolen from: https://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
        """

        self.psLog.debug('Model.makeTpHeader')
        header = 'HN,' + PatternScriptEntities.HTML_PARSER().unescape(appendedTpSwitchList['railroad']) + '\n'
        header += 'HT,' + PatternScriptEntities.HTML_PARSER().unescape(appendedTpSwitchList['trainName']) + '\n'
        header += 'HD,' + PatternScriptEntities.HTML_PARSER().unescape(appendedTpSwitchList['trainDescription']) + '\n'
        header += 'HC,' + PatternScriptEntities.HTML_PARSER().unescape(appendedTpSwitchList['trainComment']) + '\n'
        header += 'HV,' + PatternScriptEntities.HTML_PARSER().unescape(appendedTpSwitchList['date']) + '\n'
        header += u'WT,' + str(len(appendedTpSwitchList['locations'])) + '\n'

        return header

    def makeTpLocations(self, appendedTpSwitchList):
        """The jason manifest is encoded in HTML Entity,
        csv writer does not encode utf-8
        """

        self.psLog.debug('Model.makeTpLocations')

        tpLocations = ''

        i = 1
        for location in appendedTpSwitchList['locations']:
            tpLocations += u'WE,' + str(i) + ',' + location['locationName'] + '\n'
            for track in location['tracks']:
                for loco in track['locos']:
                    tpLocations += ",".join(self.makeLine(loco)) + '\n'
                for car in track['cars']:
                    tpLocations += ",".join(self.makeLine(car)) + '\n'
            i += 1

        return tpLocations + '\n'

    def makeLine(self, rS):

        # trackComment = self.locationHash[rS[u'Set to']]

        ID = rS[PatternScriptEntities.SB.handleGetMessage('Road')] + rS[PatternScriptEntities.SB.handleGetMessage('Number')]
    # Process FD&T
        FDandT = rS[PatternScriptEntities.SB.handleGetMessage('FD&Track')]
        FDandT = FDandT.replace(', ', ';')
    # Pickup Cars are tagged with their final destination, all others tagged with destination
        if rS[u'PUSO'] == 'PC':
            rsSetTo = FDandT
        else:
            rsSetTo = rS[u'Set to']
    # Process load Type into a single character string
        loadType = rS[PatternScriptEntities.SB.handleGetMessage('Load_Type')]
        if rS[PatternScriptEntities.SB.handleGetMessage('Load_Type')] == 'Empty':
            loadType = 'E'
        if rS[PatternScriptEntities.SB.handleGetMessage('Load_Type')] == 'Load':
            loadType = 'L'

        rsLine  = [
                  rS[u'PUSO'] + ','
                + ID + ','
                + rS[PatternScriptEntities.SB.handleGetMessage('Road')] + ','
                + rS[PatternScriptEntities.SB.handleGetMessage('Number')] + ','
                + rS[PatternScriptEntities.SB.handleGetMessage('Type')] + ','
                + loadType + ','
                + rS[PatternScriptEntities.SB.handleGetMessage('Load')] + ','
                + rS[PatternScriptEntities.SB.handleGetMessage('Track')] + ','
                + rsSetTo
                ]

        return rsLine

    def writeTpWorkEventListAsJson(self, appendedTpSwitchList):

        self.psLog.debug('Model.writeTpWorkEventListAsJson')

        reportTitle = appendedTpSwitchList['trainDescription']
        jsonReoprtPath = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + reportTitle + '.json'
        jsonReport = PatternScriptEntities.dumpJson(appendedTpSwitchList)
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

        self.errorReport = PatternScriptEntities.BUNDLE['Update Inventory Error Report']
        self.setCarsError = ''
        self.carsNotFound = [] # A list so it can be sorted
        self.locationNotFound = ''

        tpInventory = ModelEntities.getTpInventory()
        tpInventory.pop(0)
        self.tpInventoryList = ModelEntities.makeTpInventoryList(tpInventory)

        return

    def checkList(self):

        if self.tpInventoryList:
            return True
        else:
            return False

    def update(self):

        jmriLocationHash = ModelEntities.makeJmriLocationHash()

        for carLabel, trackLabel in self.tpInventoryList:

            rs = PatternScriptEntities.getRollingStockById(carLabel)
            if not rs:
                self.carsNotFound.append(carLabel)
                continue

            try:
                setToLoc, setToTrack = ModelEntities.getSetToLocationAndTrack(jmriLocationHash[trackLabel])
            except KeyError:
                self.locationNotFound += '\n' + trackLabel + ' - not a JMRI track track comment'
                continue

            setResult = rs.setLocation(setToLoc, setToTrack)
            if setResult != 'okay':
                self.setCarsError += '\n' + rs.getId()  + ' - ' + setResult

        print(SCRIPT_NAME + '.UpdateInventory ' + str(SCRIPT_REV))

        return

    def updateExisting(self):

        for lineItem in self.tpInventoryList:

            if lineItem[2].startswith('E'):
                engine = ModelEntities.updateEngine(lineItem)
            else:
                car = ModelEntities.updateCar(lineItem)

        return

    def getErrorReport(self):

        self.errorReport += '\n\n' + PatternScriptEntities.BUNDLE['List of rolling stock not updated:']
        self.errorReport += '\n' + self.setCarsError

        self.errorReport += '\n\n' + PatternScriptEntities.BUNDLE['List of tracks not found:']
        self.errorReport += '\n' + self.locationNotFound

        self.errorReport += '\n\n' + PatternScriptEntities.BUNDLE[u'TrainPlayer© cars not found in JMRI roster:']
        self.errorReport += '\n' + '\n'.join(sorted(self.carsNotFound[1:-1])) # [0] is the header

        return self.errorReport

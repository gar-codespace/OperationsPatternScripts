# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from o2oSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelWorkEvents'
SCRIPT_REV = 20220101


class TrackPatternTranslationToTp:
    """TrainPlayer Manifest-
        Translate Track Patterns from OperationsPatternScripts for TrainPlayer O2O script compatability
        """

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
    """TrainPlayer Manifest-
        Translate manifests from JMRI for TrainPlayer o2o script compatability
        """

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

        for location in completeJmriManifest[u'locations']:
            tpLocation = ModelEntities.parseJmriLocations(location)
            locationList.append(tpLocation)

        return locationList


class ProcessWorkEventList:
    """TrainPlayer Manifest-
        Process the translated work event lists to a CSV list formatted for the
        TrainPlayer o2o scripts
        """

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ProcessWorkEventList')

        rsFile = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRollingStockData.json'
        tpRollingStockData = PatternScriptEntities.genericReadReport(rsFile)
        self.tpRollingStockData =  PatternScriptEntities.loadJson(tpRollingStockData)

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
        """This makes a rolling stock line for the TP o2o file
        Identify the rolling stock by its TP car_ID"""

        ID = rS[PatternScriptEntities.SB.handleGetMessage('Road')] + rS[PatternScriptEntities.SB.handleGetMessage('Number')]
        tpID = self.tpRollingStockData[ID]
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
                + tpID + ','
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

        reportTitle = appendedTpSwitchList['trainName']
        jsonReoprtPath = PatternScriptEntities.PROFILE_PATH + 'operations\\patternReports\\' + reportTitle + '.json'
        jsonReport = PatternScriptEntities.dumpJson(appendedTpSwitchList)
        PatternScriptEntities.genericWriteReport(jsonReoprtPath, jsonReport)

        print(SCRIPT_NAME + '.ProcessWorkEventList ' + str(SCRIPT_REV))

        return


class WriteWorkEventListToTp:
    """TrainPlayer Manifest-
        Writes the o2o work events list
        """

    def __init__(self, workEventList):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.WriteWorkEventListToTp')

        self.jmriManifestPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() \
                + "AppData\Roaming\TrainPlayer\Reports\JMRI Report - Work Events.csv"
        self.workEventList = workEventList

        return

    def asCsv(self):

        self.psLog.debug('Model.WriteWorkEventListToTp.asCsv')

        if PatternScriptEntities.CheckTpDestination().directoryExists():
            PatternScriptEntities.genericWriteReport(self.jmriManifestPath, self.workEventList)

        print(SCRIPT_NAME + '.WriteWorkEventListToTp ' + str(SCRIPT_REV))

        return

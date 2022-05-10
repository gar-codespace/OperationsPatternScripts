# coding=utf-8
# © 2021, 2022 Greg Ritacco

import jmri
import java

import logging
import time
from json import loads as jsonLoads, dumps as jsonDumps
from HTMLParser import HTMLParser
from codecs import open as codecsOpen
from os import mkdir as osMakeDir
from sys import path as sysPath

SCRIPT_NAME ='OperationsPatternScripts.TrainPlayerSubroutine.PatternTracksExport'
SCRIPT_REV = 20220101

from psEntities import PatternScriptEntities


# class CheckTpDestination:
#     '''Verify or create a TrainPlayer destination directory'''
#
#     def __init__(self):
#
#         self.psLog = logging.getLogger('PS.TP.CheckTpDestination')
#
#         return
#
#     def directoryExists(self):
#
#         try:
#             osMakeDir(jmri.util.FileUtil.getHomePath() + 'AppData\\Roaming\\TrainPlayer\\Reports')
#             self.psLog.warning('TrainPlayer destination directory created')
#         except OSError:
#             self.psLog.info('TrainPlayer destination directory OK')
#
#         return

class ExportJmriLocations:
    '''Writes a list of location names and comments for the whole profile'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.ExportJmriLocations')

        return

    def makeLocationList(self):
        '''Creates the TrainPlayer Advanced Ops compatable JMRI location list'''

        csvLocations = ''
        i = 0
        for location in PatternScriptEntities.LM.getLocationsByIdList():
            tracks = location.getTracksList()
            for track in tracks:
                aoLocale = unicode(location.getName(), PatternScriptEntities.setEncoding()) + u';' + unicode(track.getName(), PatternScriptEntities.setEncoding())
                trackComment = unicode(track.getComment(), PatternScriptEntities.setEncoding())
                if not trackComment:
                    i += 1
                csvLocations += aoLocale + ',' + trackComment + '\n'

        self.psLog.info(str(i) + ' missing track comments for locations export to TrainPlayer')

        return csvLocations

    def toTrainPlayer(self, csvLocations):
        '''Exports JMRI location;track pairs and track comments for TrainPlayer Advanced Ops'''

        jmriLocationsPath = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Locations.csv"
        try: # Catch TrainPlayer not installed
            with codecsOpen(jmriLocationsPath, 'wb', encoding=PatternScriptEntities.setEncoding()) as csvWorkFile:
                csvHeader = u'Locale,Industry\n'
                csvWorkFile.write(csvHeader + csvLocations)
        except IOError:
                self.psLog.warning('Directory not found, TrainPlayer locations export did not complete')

        print(SCRIPT_NAME + '.ExportJmriLocations ' + str(SCRIPT_REV))

        return

class TrackPatternTranslationToTp:
    '''Translate Track Patterns from OperationsPatternScripts for TrainPlayer O2O script compatability'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.TrainPlayerTranslationToTp')

        return

    def modifySwitchList(self, setCarsForm, textBoxEntry):
        '''Replaces car['Set to'] = [ ] with the track comment'''

        self.psLog.debug('modifySwitchList')

        location = setCarsForm['locations'][0]['locationName']
        trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
        locationTracks = PatternScriptEntities.LM.getLocationByName(location).getTracksList()
        trackList = []
        for track in locationTracks:
            trackList.append(track.getName())

        userInputList = []
        for userInput in textBoxEntry:
            inputText = unicode(userInput.getText(), PatternScriptEntities.setEncoding())
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

        headerNames = PatternScriptEntities.readConfigFile('PT')
        reportTitle = headerNames['TD']['TP']
        jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
        with codecsOpen(jsonFile, 'r', encoding=PatternScriptEntities.setEncoding()) as jsonWorkFile:
            jsonSwitchList = jsonWorkFile.read()
        tpSwitchList = jsonLoads(jsonSwitchList)

        for loco in modifiedForm['locations'][0]['tracks'][0]['locos']:
            tpSwitchList['locations'][0]['tracks'][0]['locos'].append(loco)

        for car in modifiedForm['locations'][0]['tracks'][0]['cars']:
            tpSwitchList['locations'][0]['tracks'][0]['cars'].append(car)

        return tpSwitchList

class JmriTranslationToTp:
    '''Translate manifests from JMRI for TrainPlayer O2O script compatability'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.JmriTranslationToTp')

        print(SCRIPT_NAME + '.JmriTranslationToTp ' + str(SCRIPT_REV))

        return

    def getTrainAsDict(self, train):

        manifest = jmri.util.FileUtil.readFile(jmri.jmrit.operations.trains.JsonManifest(train).getFile())
        trainAsDict = jsonLoads(manifest)
        trainAsDict['comment'] = train.getComment()

        return trainAsDict

    def translateManifestHeader(self, completeJmriManifest):

        self.psLog.debug('translateManifestHeader')

        jmriDateAsEpoch = self.convertJmriDateToEpoch(completeJmriManifest[u'date'])
        completeJmriManifest['date'] = PatternScriptEntities.timeStamp(jmriDateAsEpoch)
        completeJmriManifest['trainDescription'] = completeJmriManifest['description']
        completeJmriManifest['trainName'] = completeJmriManifest['userName']
        completeJmriManifest['trainComment'] = completeJmriManifest['comment']
        completeJmriManifest.pop('description', 'Description')
        completeJmriManifest.pop('userName', 'Name')
        completeJmriManifest.pop('comment', 'Comment')

        return completeJmriManifest

    def convertJmriDateToEpoch(self, jmriTime):
        '''2022-02-26T17:16:17.807+0000'''

        epochTime = time.mktime(time.strptime(jmriTime, "%Y-%m-%dT%H:%M:%S.%f+0000"))

        if time.localtime(epochTime).tm_isdst and time.daylight: # If local dst and dst are both 1
            epochTime -= time.altzone
        else:
            epochTime -= time.timezone # in seconds

        return epochTime

    def translateManifestBody(self, completeJmriManifest):

        self.psLog.debug('translateManifestBody')

        locationList = []
        for location in completeJmriManifest[u'locations']:

            tpLocation = {}
            tpLocation['locationName'] = location['userName']
            tpLocation['tracks'] = []

            locoList = []
            carList = []
            for loco in location[u'engines'][u'add']:
                line = self.parseRollingStockAsDict(loco)
                line['PUSO'] = 'PL'
                locoList.append(line)
            for loco in location[u'engines'][u'remove']:
                line = self.parseRollingStockAsDict(loco)
                line['PUSO'] = 'SL'
                locoList.append(line)
            for car in location['cars']['add']:
                line = self.parseRollingStockAsDict(car)
                line['PUSO'] = 'PC'
                carList.append(line)
            for car in location['cars']['remove']:
                line = self.parseRollingStockAsDict(car)
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

    def parseRollingStockAsDict(self, rS):

        rsDict = {}
        rsDict['Road'] = unicode(rS[u'road'], PatternScriptEntities.setEncoding())
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
        rsDict[u'Track'] = unicode(rS[u'location'][u'track'][u'userName'], PatternScriptEntities.setEncoding())
        # rsDict[u'Set to'] = unicode(lN, PatternScriptEntities.setEncoding()) + u';' + unicode(rS[u'destination'][u'track'][u'userName'], PatternScriptEntities.setEncoding())
        rsDict[u'Set to'] = unicode(rS[u'destination'][u'userName'], PatternScriptEntities.setEncoding()) + u';' + unicode(rS[u'destination'][u'track'][u'userName'], PatternScriptEntities.setEncoding())
        try:
            jFinalDestination = unicode(rS[u'finalDestination'][u'userName'], PatternScriptEntities.setEncoding())
            try:
                jFinalTrack = unicode(rS[u'finalDestination'][u'track'][u'userName'], PatternScriptEntities.setEncoding())
            except KeyError:
                jFinalTrack = u'Any'
            rsDict[u'FD&Track'] = jFinalDestination + ';' + jFinalTrack
        except:
            rsDict[u'FD&Track'] = unicode(rS[u'destination'][u'userName'], PatternScriptEntities.setEncoding()) + u';' + unicode(rS[u'destination'][u'track'][u'userName'], PatternScriptEntities.setEncoding())

        return rsDict

class ProcessWorkEventList:
    '''Process the translated work event lists to a CSV list formatted for the TrainPlayer side scripts'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.ProcessWorkEventList')

        return

    def writeTpWorkEventListAsJson(self, appendedTpSwitchList):

        self.psLog.debug('writeTpWorkEventListAsJson')

        reportTitle = appendedTpSwitchList['trainDescription']
        jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
        jsonObject = jsonDumps(appendedTpSwitchList, indent=2, sort_keys=True)
        with codecsOpen(jsonFile, 'wb', encoding=PatternScriptEntities.setEncoding()) as jsonWorkFile:
            jsonWorkFile.write(jsonObject)

        print(SCRIPT_NAME + '.ProcessWorkEventList ' + str(SCRIPT_REV))

        return

    def makeTpHeader(self, appendedTpSwitchList):
        '''The jason manifest is encoded in HTML Entity'''
        # csv writer does not encode utf-8

        self.psLog.debug('makeTpHeader')
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

class WriteWorkEventListToTp:

    def __init__(self, workEventList):

        self.psLog = logging.getLogger('PS.TP.WriteWorkEventListToTp')

        self.jmriManifestPath = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Work Events.csv"
        self.workEventList = workEventList

        return

    def asCsv(self):

        self.psLog.debug('asCsv')

        try: # Catch TrainPlayer not installed
            with codecsOpen(self.jmriManifestPath, 'wb', encoding=PatternScriptEntities.setEncoding()) as csvWorkFile:
                csvWorkFile.write(self.workEventList)
        except IOError:
            self.psLog.warning('Directory not found, TrainPlayer switch list export did not complete')

        print(SCRIPT_NAME + '.WriteWorkEventListToTp ' + str(SCRIPT_REV))

        return

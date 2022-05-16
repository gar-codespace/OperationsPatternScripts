# coding=utf-8
# © 2021, 2022 Greg Ritacco

import jmri

import logging
# import time
from json import loads as jsonLoads, dumps as jsonDumps
from os import mkdir as osMakeDir
from codecs import open as codecsOpen
from HTMLParser import HTMLParser

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.Model'
SCRIPT_REV = 20220101
psLog = logging.getLogger('PS.TP.Model')

print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

class CheckTpDestination:
    '''Verify or create a TrainPlayer destination directory'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.CheckTpDestination')

        return

    def directoryExists(self):

        try:
            osMakeDir(jmri.util.FileUtil.getHomePath() + 'AppData\\Roaming\\TrainPlayer\\Reports')
            self.psLog.warning('TrainPlayer destination directory created')
        except OSError:
            self.psLog.info('TrainPlayer destination directory OK')

        return

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
                aoLocale = unicode(location.getName(), PatternScriptEntities.ENCODING) + u';' + unicode(track.getName(), PatternScriptEntities.ENCODING)
                trackComment = unicode(track.getComment(), PatternScriptEntities.ENCODING)
                if not trackComment:
                    i += 1
                csvLocations += aoLocale + ',' + trackComment + '\n'

        self.psLog.info(str(i) + ' missing track comments for locations export to TrainPlayer')

        return csvLocations

    def toTrainPlayer(self, csvLocations):
        '''Exports JMRI location;track pairs and track comments for TrainPlayer Advanced Ops'''

        jmriLocationsPath = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Locations.csv"
        try: # Catch TrainPlayer not installed
            with codecsOpen(jmriLocationsPath, 'wb', encoding=PatternScriptEntities.ENCODING) as csvWorkFile:
                csvHeader = u'Locale,Industry\n'
                csvWorkFile.write(csvHeader + csvLocations)
        except IOError:
                self.psLog.warning('Directory not found, TrainPlayer locations export did not complete')

        print(SCRIPT_NAME + '.ExportJmriLocations ' + str(SCRIPT_REV))

        return

class JmriTranslationToTp:
    '''Translate manifests from JMRI for TrainPlayer o2o script compatability'''

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

        self.psLog.debug('translateManifestBody')

        locationList = []
        for location in completeJmriManifest[u'locations']:
            tpLocation = ModelEntities.parseJmriLocations(location)
            locationList.append(tpLocation)

        return locationList

class ProcessWorkEventList:
    '''Process the translated work event lists to a CSV list formatted for the TrainPlayer o2o scripts'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.ProcessWorkEventList')

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

    def writeTpWorkEventListAsJson(self, appendedTpSwitchList):

        self.psLog.debug('writeTpWorkEventListAsJson')

        reportTitle = appendedTpSwitchList['trainDescription']
        jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
        jsonObject = jsonDumps(appendedTpSwitchList, indent=2, sort_keys=True)
        with codecsOpen(jsonFile, 'wb', encoding=PatternScriptEntities.ENCODING) as jsonWorkFile:
            jsonWorkFile.write(jsonObject)

        print(SCRIPT_NAME + '.ProcessWorkEventList ' + str(SCRIPT_REV))

        return

class WriteWorkEventListToTp:

    def __init__(self, workEventList):

        self.psLog = logging.getLogger('PS.TP.WriteWorkEventListToTp')

        self.jmriManifestPath = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Work Events.csv"
        self.workEventList = workEventList

        return

    def asCsv(self):

        self.psLog.debug('asCsv')

        try: # Catch TrainPlayer not installed
            with codecsOpen(self.jmriManifestPath, 'wb', encoding=PatternScriptEntities.ENCODING) as csvWorkFile:
                csvWorkFile.write(self.workEventList)
        except IOError:
            self.psLog.warning('Directory not found, TrainPlayer switch list export did not complete')

        print(SCRIPT_NAME + '.WriteWorkEventListToTp ' + str(SCRIPT_REV))

        return

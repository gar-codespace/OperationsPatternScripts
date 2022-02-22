# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import logging
from json import loads as jsonLoads, load as jsonLoad
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
psLog = logging.getLogger('PS.TP.ExportToTrainPlayer')

class CheckTpDestination():
    '''Verify or create a TrainPlayer destination directory'''

    def __init__(self):
        self.scriptName = 'OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.CheckTpDestination'
        self.scriptRev = 20220101

        return

    def directoryExists(self):

        try:
            osMakeDir(jmri.util.FileUtil.getHomePath() + 'AppData\\Roaming\\TrainPlayer\\Reports')
            psLog.warning('TrainPlayer destination directory created')
        except OSError:
            psLog.info('TrainPlayer destination directory OK')

        print(scriptName + ' ' + str(scriptRev))
        return

class JmriLocationsToTrainPlayer():
    '''Writes a list of location names and comments for the whole profile'''

    def __init__(self):
        self.scriptName = 'OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.LocationsForTrainPlayer'
        self.scriptRev = 20220101
        self.jLM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        self.toLoc = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Locations.csv"

        return

    def exportLocations(self):

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
        psLog.info(eMessage)
        print(self.scriptName + ' ' + str(scriptRev))

        return
class JmriTranslationToTp():

    def __init__(self, body):

        self.body = body
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.JmriTranslationToTp'
        self.scriptRev = 20220101

        return

    def modifyJmriSwitchListForTp(self):
        '''Replaces car['Set to'] = [ ] with the track comment'''

        psLog.debug('modifySwitchListForTp')
        location = psEntities.MainScriptEntities.readConfigFile('TP')['PL']
        lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)

        for car in self.body['Cars']:
            if 'Hold' in car['Set to']:
                car['Set to'] = lm.getLocationByName(location).getTrackByName(car['Track'], None).getComment()
            else:
                car['Set to'] = lm.getLocationByName(location).getTrackByName(car['Set to'], None).getComment()

        return self.body

    def appendSwitchListForTp(self):

        psLog.debug('appendSwitchListForTp')
        reportTitle = psEntities.MainScriptEntities.readConfigFile('TP')['RT']['TP']
        jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
        with codecsOpen(jsonFile, 'r', encoding=psEntities.MainScriptEntities.setEncoding()) as jsonWorkFile:
            jsonSwitchList = jsonWorkFile.read()
        switchList = jsonLoads(jsonSwitchList)
        switchListName = switchList['description']
        print(self.body)
        # trackDetailList = self.body['tracks']
        # if not trackDetailList:
        #     self.body['Name'] = 'TrainPlayer'
        #     self.body['Length'] = 0
        #     trackDetailList.append(self.body)
        # else:
        #     carList = trackDetailList[0]['Cars']
        #     carList += self.body['Cars']
        #     trackDetailList[0]['Cars'] = carList
        # switchList['tracks'] = trackDetailList

        # jsonObject = jsonDumps(switchList, indent=2, sort_keys=True)
        # with codecsOpen(jsonFile, 'wb', encoding=psEntities.MainScriptEntities.setEncoding()) as jsonWorkFile:
        #     jsonWorkFile.write(jsonObject)

        return switchList

class WorkEventListForTrainPlayer():

    def __init__(self, switchListName):

        self.switchListName = switchListName
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.SwitchListForTrainPlayer'
        self.scriptRev = 20220101

        return

    def modifyJmriSwitchListForTp(self):
        '''Replaces car['Set to'] = [ ] with the track comment'''

        psLog.debug('modifySwitchListForTp')
        location = psEntities.MainScriptEntities.readConfigFile('TP')['PL']
        lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        for car in body['Cars']:
            if 'Hold' in car['Set to']:
                car['Set to'] = lm.getLocationByName(location).getTrackByName(car['Track'], None).getComment()
            else:
                car['Set to'] = lm.getLocationByName(location).getTrackByName(car['Set to'], None).getComment()

        return body

    def readFromFile(self):

        try:
            jsonCopyFrom = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + self.switchListName + '.json'
            psLog.debug('TrainPlayer switch list read from file')
        except:
            psLog.critical('TrainPlayer switch list could not be read')
            return

        with codecsOpen(jsonCopyFrom, 'r', encoding=setEncoding) as jsonWorkFile:
            jsonSwitchList = jsonWorkFile.read()

        print(self.scriptName + ' ' + str(self.scriptRev))

        return jsonLoads(jsonSwitchList)

class CsvListFromFile():
    '''Process the inputted data as a CSV list formatted for the TrainPlayer side scripts'''

    def __init__(self, inputList=None):

        self.inputList = inputList
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.MakeCsvListFromFile'
        self.scriptRev = 20220101
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
            psLog.info('Train ' + newestTrain['userName'] + ' is newest')
        else:
            psLog.info('No trains are built')

        return newestTrain, trainComment

    def makeHeader(self):

        # https://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
        header = 'HN,' + HTMLParser().unescape(self.inputList['railroad']) + '\n'
        header += 'HT,' + HTMLParser().unescape(self.inputList['userName']) + '\n'
        header += 'HD,' + HTMLParser().unescape(self.inputList['description']) + '\n'
        header += 'HC,' + self.comment + '\n'
        header += 'HV,' + HTMLParser().unescape(self.inputList['date']) + '\n'
        header += u'WT,' + str(len(self.inputList['tracks'])) + '\n'

        return header

    def makeBody(self):

        locoCount = ''
        carCount = ''
        x = 1
        for track in self.inputList['tracks']:
            workEventNumber = u'WE,' + str(x) + ',' + HTMLParser().unescape(track['Name'])

            try:
                for loco in track['Locos']:
                    # locoCount += ",".join(self.parseLoco(car)) + '\n'
                    pass
            except KeyError:
                psLog.info('No locomotives in list')

            try:
                for car in track['Cars']:
                    carCount += '\n' + ",".join(self.parseCar(car))
            except KeyError:
                psLog.info('No cars in list')
            x += 1

        return workEventNumber + carCount

    def parseCar(self, xCar):

        return [xCar[u'PUSO'], xCar[u'Road'] + xCar[u'Number'], xCar[u'Road'], xCar[u'Number'], xCar[u'Load'], xCar[u'Track'], xCar[u'Set to']]

    def makeList(self):

        csvList = self.makeHeader()
        csvList += self.makeBody()

        print(self.scriptName + ' ' + str(self.scriptRev))

        return csvList

class writeWorkEventListToTp():

    def __init__(self, workEventList):

        self.workEventList = workEventList
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.writeWorkEventListToTp'
        self.scriptRev = 20220101

    def writeAsCsv(self):

        weCopyTo = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Work Events.csv"
        with codecsOpen(weCopyTo, 'wb', encoding=setEncoding) as csvWorkFile:
            csvWorkFile.write(self.workEventList)

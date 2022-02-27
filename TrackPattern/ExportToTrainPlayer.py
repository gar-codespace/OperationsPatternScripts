import jmri
import logging
import time
from json import loads as jsonLoads, dumps as jsonDumps
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

jmriLocationsPath = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Locations.csv"
jmriManifestPath = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Work Events.csv"

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
        self.jLM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)

        return

    def toTrainPlayer(self):
        '''Exports JMRI location name/location comment pairs for TP Advanced Ops'''

        eMessage = 'No missing entries for location export for TrainPlayer'
        locationList = self.jLM.getLocationsByIdList()
        with codecsOpen(jmriLocationsPath, 'wb', encoding=setEncoding) as csvWorkFile:
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
                loco['Set to'] = location + ';' + lm.getLocationByName(location).getTrackByName(loco['Track'], None).getName()
            else:
                loco['Set to'] = location + ';' + lm.getLocationByName(location).getTrackByName(loco['Set to'], None).getName()

        for car in self.body['Cars']:
            if 'Hold' in car['Set to']:
                car['Set to'] = location + ';' + lm.getLocationByName(location).getTrackByName(car['Track'], None).getName()
            else:
                car['Set to'] = location + ';' + lm.getLocationByName(location).getTrackByName(car['Set to'], None).getName()

        return self.body

    def appendSwitchList(self):

        self.psLog.debug('appendSwitchList')
        reportTitle = psEntities.MainScriptEntities.readConfigFile('TP')['RT']['TP']
        jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
        with codecsOpen(jsonFile, 'r', encoding=psEntities.MainScriptEntities.setEncoding()) as jsonWorkFile:
            jsonSwitchList = jsonWorkFile.read()
        switchList = jsonLoads(jsonSwitchList)
        switchList['comment'] = 'TrainPlayer Switch List'
        
        try:
            trackDetailList = switchList['locations']
        except KeyError:
            switchList['locations'] = [self.body]
            return switchList

        locoList = trackDetailList[0]['Locos']
        locoList += self.body['Locos']
        trackDetailList[0]['Locos'] = locoList
        carList = trackDetailList[0]['Cars']
        carList += self.body['Cars']
        trackDetailList[0]['Cars'] = carList

        return switchList

class JmriTranslationToTp():
    '''Translate manifests from JMRI to TrainPlayer format'''

    def __init__(self):

        # self.inputList = inputList
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.JmriTranslationToTp'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.JmriTranslationToTp')

        # self.comment = u'TrainPlayer Switch List'
        self.jTM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.trains.TrainManager)

        return

    def findNewestManifest(self):
        '''If more than 1 train is built, pick the newest one'''

        newestTrain = ''
        trainComment = ''
        if self.jTM.isAnyTrainBuilt():
            trainListByStatus = self.jTM.getTrainsByStatusList()
            newestBuildTime = ''
            for train in trainListByStatus:
                if train.isBuilt():
                    workEventFile =  jmri.util.FileUtil.getProfilePath() + 'operations\jsonManifests\\train-' + train.getName() + ".json"
                    with codecsOpen(workEventFile, 'r', encoding=psEntities.MainScriptEntities.setEncoding()) as workEventObject:
                        switchList = workEventObject.read()
                        workEventList = jsonLoads(switchList)
                    if workEventList[u'date'] > newestBuildTime:
                        newestBuildTime = workEventList[u'date']
                        newestTrain = workEventList
                        newestTrain['comment'] = train.getComment()
            self.psLog.info('Train ' + newestTrain[u'userName'] + ' is newest')
        else:
            self.psLog.info('No trains are built')

        return newestTrain

    def translateManifestHeader(self, completeJmriManifest):

        jmriDateAsEpoch = self.convertJmriDateToEpoch(completeJmriManifest[u'date'])
        completeJmriManifest[u'date'] = self.jmriTimeStamp(jmriDateAsEpoch)
        completeJmriManifest[u'description'] = 'TrainPlayer Work Events'

        return completeJmriManifest

    def translateManifestBody(self, completeJmriManifest):

        locationList = []
        for location in completeJmriManifest[u'locations']:
            locationName = location['userName']
            locationDict = {}
            locos = []
            cars = []
            for loco in location[u'engines'][u'add']:
                line = self.parseRollingStockAsDict(loco, locationName)
                line['PUSO'] = 'PL'
                locos.append(line)
            for loco in location[u'engines'][u'remove']:
                line = self.parseRollingStockAsDict(loco, locationName)
                line['PUSO'] = 'SL'
                locos.append(line)
            for car in location['cars']['add']:
                line = self.parseRollingStockAsDict(car, locationName)
                line['PUSO'] = 'PC'
                cars.append(line)
            for car in location['cars']['remove']:
                line = self.parseRollingStockAsDict(car, locationName)
                line['PUSO'] = 'SC'
                cars.append(line)
            locationDict['Name'] = location['userName']
            locationDict['Locos'] = locos
            locationDict['Cars'] = cars
            locationList.append(locationDict)
        completeJmriManifest[u'locations'] = locationList

        return completeJmriManifest

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
    '''Process the translated work event lists as a CSV list formatted for the TrainPlayer side scripts'''

    def __init__(self, input=None):

        self.inputList = input
        self.switchListName = input
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.ProcessWorkEventList'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.ProcessWorkEventList')

        self.jTM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.trains.TrainManager)

        return

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
        '''The jason manifest is encoded in HTML Entity'''
        # csv writer does not encode utf-8

        self.psLog.debug('makeHeader')
        # https://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
        header = 'HN,' + HTMLParser().unescape(self.inputList['railroad']) + '\n'
        header += 'HT,' + HTMLParser().unescape(self.inputList['userName']) + '\n'
        header += 'HD,' + HTMLParser().unescape(self.inputList['description']) + '\n'
        header += 'HC,' + HTMLParser().unescape(self.inputList['comment']) + '\n'
        header += 'HV,' + HTMLParser().unescape(self.inputList['date']) + '\n'
        header += u'WT,' + str(len(self.inputList['locations'])) + '\n'

        return header

    def makeBody(self):
        '''The jason manifest is encoded in HTML Entity'''
        # csv writer does not encode utf-8

        self.psLog.debug('makeBody')
        body = ''
        x = 1
        for location in self.inputList['locations']:

            workEventNumber = u'WE,' + str(x) + ',' + HTMLParser().unescape(location['Name'])

            locoLines = ''
            for loco in location['Locos']:
                locoLines += '\n' + ",".join(self.makeLine(loco))

            carLines = ''
            for car in location['Cars']:
                carLines += '\n' + ",".join(self.makeLine(car))

            x += 1
            body += workEventNumber + locoLines + carLines + '\n'

        return body

    def makeLine(self, rS):

        return [rS[u'PUSO'], rS[u'Road'] + rS[u'Number'], rS[u'Road'], rS[u'Number'], rS[u'Load'], rS[u'Track'], rS[u'Set to'], rS['FD&Track']]

    def writeWorkEventListAsJson(self):

        self.psLog.debug('writeWorkEventListAsJson')
        reportTitle = self.inputList['description']
        jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
        jsonObject = jsonDumps(self.inputList, indent=2, sort_keys=True)
        with codecsOpen(jsonFile, 'wb', encoding=psEntities.MainScriptEntities.setEncoding()) as jsonWorkFile:
            jsonWorkFile.write(jsonObject)

        return reportTitle

class WriteWorkEventListToTp():

    def __init__(self, workEventList):

        self.workEventList = workEventList
        self.scriptName ='OperationsPatternScripts.TrackPattern.ExportToTrainPlayer.writeWorkEventListToTp'
        self.scriptRev = 20220101
        self.psLog = logging.getLogger('PS.EX.WriteWorkEventListToTp')
        return

    def asCsv(self):

        self.psLog.debug('asCsv')
        with codecsOpen(jmriManifestPath, 'wb', encoding=setEncoding) as csvWorkFile:
            csvWorkFile.write(self.workEventList)

        return

class ManifestForTrainPlayer(jmri.jmrit.automat.AbstractAutomaton):
    '''Processes a manifest built from the JMRI trains panel'''

    def init(self):
        self.scriptName = 'OperationsExportToTrainPlayer.ManifestForTrainPlayer'
        self.scriptRev = 20220101
    # fire up logging
        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\TrainPlayerScriptsLog.txt'
        # logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternLog.txt'
        # self.psLog = logging.getLogger('MS')
        self.tpLog = logging.getLogger('TP')
        self.tpLog.setLevel(10)
        logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.tpFileHandler = logging.FileHandler(logPath, mode='w', encoding=setEncoding)
        self.tpFileHandler.setFormatter(logFileFormat)
        self.tpLog.addHandler(self.tpFileHandler)
        self.tpLog.debug('Log File for Pattern Scripts Plugin - debug level initialized')
        self.tpLog.info('Log File for Pattern Scripts Plugin - info level initialized')
        self.tpLog.warning('Log File for Pattern Scripts Plugin - warning level initialized')
        self.tpLog.error('Log File for Pattern Scripts Plugin - error level initialized')
        self.tpLog.critical('Log File for Pattern Scripts Plugin - critical level initialized')
    # # Boilerplate
        self.jTM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.trains.TrainManager)
        self.jProfilePath = jmri.util.FileUtil.getProfilePath()

        return

    def handle(self):

        CheckTpDestination().directoryExists()
        ExportJmriLocations().toTrainPlayer()

        newestTrain = JmriTranslationToTp().findNewestManifest()
        completeManifest = JmriTranslationToTp().translateManifestHeader(newestTrain)
        completeManifest = JmriTranslationToTp().translateManifestBody(completeManifest)

        processedManifest = ProcessWorkEventList(completeManifest)
        processedManifest.writeWorkEventListAsJson()

        WriteWorkEventListToTp(processedManifest.makeHeader() + processedManifest.makeBody()).asCsv()
        # self.psLog.removeHandler(self.msFileHandler)

        return False

if __name__ == "__builtin__":
    ManifestForTrainPlayer().start()

# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from o2oSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelWorkEvents'
SCRIPT_REV = 20220101


class ConvertPtMergedForm:
    """Converts the generic merged form into the o2o format work event json"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.o2o.ConvertPtMergedForm')

        self.o2oSwitchList = {}

        self.cars = []
        self.locos = []

        return

    def o2oSwitchListGetter(self):

        o2oSwitchListName = PatternScriptEntities.BUNDLE['o2o Work Events']
        o2oSwitchListPath = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + o2oSwitchListName + '.json'
        o2oSwitchList = PatternScriptEntities.genericReadReport(o2oSwitchListPath)
        self.o2oSwitchList = PatternScriptEntities.loadJson(o2oSwitchList)

        return

    def thinTheHerd(self):
        """Reduces the elements to those in parsePtRs"""

        for car in self.o2oSwitchList['locations'][0]['tracks'][0]['cars']:
            parsedRS = self.parsePtRs(car)
            parsedRS['PUSO'] = 'SC'
            self.cars.append(parsedRS)

        for loco in self.o2oSwitchList['locations'][0]['tracks'][0]['locos']:
            parsedRS = self.parsePtRs(loco)
            parsedRS['PUSO'] = 'SL'
            self.locos.append(parsedRS)

        return

    def parsePtRs(self, rs):
        """The load field ie either Load(car) or Model(loco).
            Pattern scripts have only one location,
            so Location and Destination are the same.
            How to combine this with parseRs?
            They do the sae thing.
            """

        parsedRS = {}
        parsedRS['Road'] = rs['Road']
        parsedRS['Number'] = rs['Number']
        parsedRS['Type'] = rs['Type']
        try:
            parsedRS['Load Type'] = ModelEntities.getLoadType(rs['Type'], rs['Load'])
            parsedRS['Load'] = rs['Load']
        except:
            parsedRS['Load Type'] = 'O'
            parsedRS['Load'] = rs['Model']
        parsedRS['Location'] = rs['Location']
        parsedRS['Track'] = rs['Track']
        parsedRS['Destination'] = rs['Location']
        parsedSetTo = self.parseSetTo(rs['Set_To'])
        parsedRS['Set_To'] = parsedSetTo

        return parsedRS

    def parseSetTo(self, setTo):
        """Used by:
            parsePtRs
            """

        x = setTo.split('[')
        y = x[1].split(']')

        return y[0]

    def o2oSwitchListUpdater(self):

        self.o2oSwitchList['locations'][0]['tracks'][0]['cars'] = self.cars
        self.o2oSwitchList['locations'][0]['tracks'][0]['locos'] = self.locos

        return self.o2oSwitchList


class ConvertJmriManifest:
    """This class converts the JMRI format manifest json into o2o format work event json"""

    def __init__(self, builtTrain):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.o2o.ConvertJmriManifest')

        self.builtTrain = builtTrain
        self.jmriManifest = {}
        self.o2oWorkEvents = {}

        return

    def getJmriManifest(self):

        self.psLog.debug('getJmriManifest')

        reportName = self.builtTrain.getName()
        jsonFileName = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\train-' + reportName + '.json'
        workEventList = PatternScriptEntities.genericReadReport(jsonFileName)
        self.jmriManifest = PatternScriptEntities.loadJson(workEventList)

        return

    def convertHeader(self):

        self.psLog.debug('convertHeader')

        self.o2oWorkEvents['railroad'] = PatternScriptEntities.HTML_PARSER().unescape(self.jmriManifest['railroad'])
        self.o2oWorkEvents['trainName'] = PatternScriptEntities.HTML_PARSER().unescape(self.jmriManifest['userName'])
        self.o2oWorkEvents['trainDescription'] = PatternScriptEntities.HTML_PARSER().unescape(self.jmriManifest['description'])
        self.o2oWorkEvents['trainComment'] = PatternScriptEntities.HTML_PARSER().unescape(self.jmriManifest['description'])

        epoch = PatternScriptEntities.convertJmriDateToEpoch(self.jmriManifest['date'])
        self.o2oWorkEvents['date'] = PatternScriptEntities.timeStamp(epoch)
        self.o2oWorkEvents['locations'] = []

        return

    def convertBody(self):

        self.psLog.debug('convertBody')

        for location in self.jmriManifest['locations']:

            cars = []
            for car in location['cars']['add']:
                parsedRS = self.parseRS(car)
                parsedRS['PUSO'] = u'PC'
                cars.append(parsedRS)
            for car in location['cars']['remove']:
                parsedRS = self.parseRS(car)
                parsedRS['PUSO'] = u'SC'
                cars.append(parsedRS)

            locos = []
            for loco in location['engines']['add']:
                parsedRS = self.parseRS(car)
                parsedRS['PUSO'] = u'PL'
                locos.append(parsedRS)
            for loco in location['engines']['add']:
                parsedRS = self.parseRS(car)
                parsedRS['PUSO'] = u'SL'
                locos.append(parsedRS)

            # self.o2oWorkEvents['locations'].append({'locationName': location['userName'], 'cars': cars, 'locos': locos})
            self.o2oWorkEvents['locations'].append({'locationName': location['userName'], 'tracks': [{'trackName': 'xyz', 'cars': cars, 'locos': locos}]})

        return

    def parseRS(self, rs):
        """The load field ie either Load or Model.
            How to combine this with parsePtRs?
            They do the sae thing.
            """

        parsedRS = {}
        parsedRS['Road'] = rs['road']
        parsedRS['Number'] = rs['number']
        parsedRS['Type'] = rs['carType']
        parsedRS['Load Type'] = ModelEntities.getLoadType(rs['carType'], rs['load'])
        try:
            parsedRS['Load'] = rs['load']
        except:
            parsedRS['Load'] = rs['model']
        parsedRS['Location'] = rs['location']['userName']
        parsedRS['Track'] = rs['location']['track']['userName']
        parsedRS['Destination'] = rs['destination']['userName']
        parsedRS['Set_To'] = '[' + rs['destination']['track']['userName'] + ']'

        return parsedRS

    def geto2oWorkEvents(self):

        return self.o2oWorkEvents


class o2oWorkEvents:
    """This class makes the o2o work event list for TrainPlayer
        tpRollingStockData lets the plugin use TP rs IDs
        """

    def __init__(self, workEvents):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.o2o.o2oWorkEvents')

        jsonFileName = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRollingStockData.json'
        tpRollingStockData = PatternScriptEntities.genericReadReport(jsonFileName)
        self.tpRollingStockData = PatternScriptEntities.loadJson(tpRollingStockData)

        self.workEvents = workEvents
        self.o2oList = ''

        workEventName = PatternScriptEntities.BUNDLE['o2o Work Events']
        self.o2oWorkEventPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() \
                + 'AppData\Roaming\TrainPlayer\Reports\JMRI Report - o2o Work Events.csv'

        return

    def o2oHeader(self):

        self.psLog.debug('o2oHeader')

        self.o2oList = 'HN,' + self.workEvents['railroad'] + '\n'
        self.o2oList += 'HT,' + self.workEvents['trainName'] + '\n'
        self.o2oList += 'HD,' + self.workEvents['trainDescription'] + '\n'
        self.o2oList += 'HC,' + self.workEvents['trainComment'] + '\n'
        self.o2oList += 'HV,' + self.workEvents['date'] + '\n'

        self.o2oList += 'WT,' + str(len(self.workEvents['locations'])) + '\n'

        return

    def o2oLocations(self):
        """This has to work for both JMRI and o2o generated lists"""

        self.psLog.debug('o2oLocations')

        counter = 1

        for location in self.workEvents['locations']:
            self.o2oList += u'WE,' + str(counter) + ',' + location['locationName'] + '\n'
            for track in location['tracks']:
                for car in track['cars']:
                    self.o2oList += self.makeLine(car) + '\n'
                for loco in track['locos']:
                    self.o2oList += self.makeLine(loco) + '\n'

            counter += 1

        return

    def makeLine(self, rs):
        """This makes a rolling stock line for the TP o2o file.
            Identify the rolling stock by its TP car_ID
            format: PUSO, TP ID, Road, Number, Car Type, L/E/O, Load or Model, From, To
            """

        ID = rs['Road'] + rs['Number']
        tpID = self.tpRollingStockData[ID]
        load = ''
        try:
            load = rs['Load']
        except:
            load = rs['Model']

        pu = rs['Location'] + ';' + rs['Track']

        # setTo = PatternScriptEntities.parseSetTo(rs['Set_To'])
        so = rs['Destination'] + ';' + rs['Set_To']

        return rs['PUSO'] + ',' + tpID + ',' + rs['Road'] + ',' + rs['Number'] + ',' + rs['Type'] + ',' + rs['Load Type'] + ',' + load + ',' + pu + ',' + so

    def saveList(self):

        self.psLog.debug('saveList')

        if PatternScriptEntities.tpDirectoryExists():
            PatternScriptEntities.genericWriteReport(self.o2oWorkEventPath, self.o2oList)

        print(SCRIPT_NAME + '.o2oWorkEvents ' + str(SCRIPT_REV))

        return



# class ResetWorkEvents:
#     """Creates a new work events json when the set cars button is pressed on the pattern scripts sub"""
#
#     def __init__(self):
#
#         self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.o2o.ResetWorkEvents')
#
#         self.workEvents = {}
#
#         return
#
#     def makePsWorkEventsHeader(self):
#
#         self.psLog.debug('makePsWorkEventsHeader')
#
#         OSU = PatternScriptEntities.JMRI.jmrit.operations.setup
#         patternLocation = PatternScriptEntities.readConfigFile('PT')['PL']
#         location = PatternScriptEntities.LM.getLocationByName(patternLocation)
#
#         self.workEvents['railroad'] = unicode(OSU.Setup.getRailroadName(), PatternScriptEntities.ENCODING)
#         self.workEvents['trainName'] = unicode(OSU.Setup.getComment(), PatternScriptEntities.ENCODING)
#         self.workEvents['trainDescription'] = PatternScriptEntities.BUNDLE['o2o Work Events']
#         self.workEvents['trainComment'] = location.getComment()
#         self.workEvents['date'] = PatternScriptEntities.timeStamp()
#
        locationName = PatternScriptEntities.readConfigFile()['PT']['PL']
        trackDict = [{'cars': [], 'locos': []}]
        locationDict = {'locationName': locationName, 'tracks': trackDict}
        self.workEvents['locations'] = [locationDict]
#
#         return
#
#     def writeWorkEvents(self):
#
#         self.psLog.debug('writeWorkEvents')
#
#         ModelEntities.writeWorkEvents(self.workEvents)
#
#         return

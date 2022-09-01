# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from o2oSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelWorkEvents'
SCRIPT_REV = 20220101


class ResetWorkEvents:
    """Creates a new work events json when the set cars button is pressed on the pattern scripts sub"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.o2o.ResetWorkEvents')

        self.workEvents = {}

        return

    def makePsWorkEventsHeader(self):

        self.psLog.debug('makePsWorkEventsHeader')

        self.workEvents['railroad'] = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getRailroadName()
        self.workEvents['trainName'] = 'Place Holder'
        self.workEvents['trainDescription'] = 'Place Holder'
        self.workEvents['trainComment'] = 'Place Holder'
        self.workEvents['date'] = PatternScriptEntities.timeStamp()

        locationName = PatternScriptEntities.readConfigFile()['PT']['PL']
        locationDict = {'locationName':locationName, 'cars':[], 'locos': []}
        self.workEvents['locations'] = [locationDict]

        return

    def writeWorkEvents(self):

        self.psLog.debug('writeWorkEvents')

        ModelEntities.writeWorkEvents(self.workEvents)

        return


class ConvertPtMergedForm:
    """Converts the generic merged form into the o2o format work event json"""

    def __init__(self, mergedForm):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.o2o.ConvertPtMergedForm')

        self.workEvents = {}
        self.mergedForm = mergedForm
        self.cars = []
        self.locos = []

        return

    def thinTheHerd(self):
        """Reduces the elements to those in parsePsWorkEventRs"""

        for car in self.mergedForm['locations']['cars']:
            parsedRS = self.parsePsWorkEventRs(car)
            parsedRS['PUSO'] = 'SC'
            self.cars.append(parsedRS)

        for loco in self.mergedForm['locations']['locos']:
            parsedRS = self.parsePsWorkEventRs(loco)
            parsedRS['PUSO'] = 'SL'
            self.locos.append(parsedRS)

        return

    def parsePsWorkEventRs(self, rs):
        """The load field ie either Load or Model.
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
        parsedRS['Destination'] = rs['Destination']
        parsedRS['Set to'] = rs['Set to']

        return parsedRS

    def getWorkEvents(self):

        self.workEvents = ModelEntities.getWorkEvents()

        return

    def appendRs(self):

        appendedCars = self.workEvents['locations'][0]['cars'] + self.cars
        appendedLocos = self.workEvents['locations'][0]['locos'] + self.locos

        self.workEvents['locations'][0]['cars'] = appendedCars
        self.workEvents['locations'][0]['locos'] = appendedLocos

        return

    def writePtWorkEvents(self):

        ModelEntities.writeWorkEvents(self.workEvents)

        return


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

            self.o2oWorkEvents['locations'].append({'locationName': location['userName'], 'cars': cars, 'locos': locos})

        return

    def parseRS(self, rs):
        """The load field ie either Load or Model.
            How to combine this with parsePsWorkEventRs?
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
        parsedRS['Set to'] = rs['destination']['track']['userName']

        return parsedRS

    def geto2oWorkEvents(self):

        return self.o2oWorkEvents


class o2oWorkEvents:
    """This class makes the o2o work event list for TrainPlayer"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.o2o.o2oWorkEvents')

        jsonFileName = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRollingStockData.json'
        tpRollingStockData = PatternScriptEntities.genericReadReport(jsonFileName)
        self.tpRollingStockData = PatternScriptEntities.loadJson(tpRollingStockData)

        self.workEvents = {}
        self.o2oList = ''

        reportName = PatternScriptEntities.readConfigFile('o2o')['RN']
        self.o2oWorkEventPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() \
                + 'AppData\Roaming\TrainPlayer\Reports\JMRI Report ' + reportName + '.csv'

        return

    def getWorkEvents(self):

        self.workEvents = ModelEntities.getWorkEvents()

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

        self.psLog.debug('o2oLocations')

        for i, location in enumerate(self.workEvents['locations'], start=1):
            self.o2oList += u'WE,' + str(i) + ',' + location['locationName'] + '\n'
            for car in location['cars']:
                self.o2oList += self.makeLine(car) + '\n'
            for loco in location['locos']:
                self.o2oList += self.makeLine(loco) + '\n'

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
        so = rs['Destination'] + ';' + rs['Set to']

        return rs['PUSO'] + ',' + tpID + ',' + rs['Road'] + ',' + rs['Number'] + ',' + rs['Type'] + ',' + rs['Load Type'] + ',' + load + ',' + pu + ',' + so

    def saveList(self):

        self.psLog.debug('saveList')

        if PatternScriptEntities.CheckTpDestination().directoryExists():
            PatternScriptEntities.genericWriteReport(self.o2oWorkEventPath, self.o2oList)

        print(SCRIPT_NAME + '.o2oWorkEvents ' + str(SCRIPT_REV))

        return

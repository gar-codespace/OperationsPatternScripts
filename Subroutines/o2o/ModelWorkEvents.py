# coding=utf-8
# © 2023 Greg Ritacco

"""Creates the TrainPlayer JMRI Report - o2o Work Events.csv file from either PatternTracksSubroutine or BuiltTrainExport"""

from opsEntities import PSE
from Subroutines.o2o import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.o2o.ModelWorkEvents')



def o2oWorkListMaker():
    """Mini controller to convert the Patterns ops-work-list.json into an o2o work events file."""

    o2oWorkList = opsWorkListConversion().convert()

    o2o = o2oWorkEvents(o2oWorkList)
    o2o.o2oHeader()
    o2o.o2oLocations()
    o2o.saveList()

    print(SCRIPT_NAME + '.o2oWorkListMaker ' + str(SCRIPT_REV))

    return


class opsWorkListConversion:
    """Converts a worklist generated by the Patterns subroutine into an o2o compatable work list."""

    def __init__(self):

        self.opsWorkList = {}
        self.o2oWorkList = {}
        self.cars = []
        self.locos = []

        return

    def workListGetter(self):

        reportName = PSE.BUNDLE['ops-work-list']
        fileName = reportName + '.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

        opsWorkList = PSE.genericReadReport(targetPath)
        self.opsWorkList = PSE.loadJson(opsWorkList)

        return

    def rsGetter(self):

        for track in self.opsWorkList['locations'][0]['tracks']:
            for car in track['cars']:
                parsed = self.parsePtRs(car)
                parsed['PUSO'] = 'SC'
                self.cars.append(parsed)
            for loco in track['locos']:
                parsed = self.parsePtRs(loco)
                parsed['PUSO'] = 'SL'
                self.locos.append(parsed)

        return

    def parsePtRs(self, rs):
        """The load field is either Load(car) or Model(loco).
            Pattern scripts have only one location,
            so Location and Destination are the same.
            """

        parsedRS = {}
        parsedRS['Road'] = rs['Road']
        parsedRS['Number'] = rs['Number']
        parsedRS['Type'] = rs['Type']
        try:
            parsedRS['Load Type'] = PSE.getShortLoadType(rs)
            parsedRS['Load'] = rs['Load']
        except:
            parsedRS['Load'] = rs['Model']
        parsedRS['Location'] = rs['Location']
        parsedRS['Track'] = rs['Track']
        parsedRS['Destination'] = rs['Location']
        parsedSetTo = self.parseSetTo(rs['Set_To'])
        parsedRS['Set_To'] = parsedSetTo

        return parsedRS

    def parseSetTo(self, setTo):
        """format: [Freight House]   """

        return setTo[1:-1].split(']')[0]

    def o2oWorkListUpdater(self):

        try:
            self.o2oWorkList['railroadName'] = PSE.expandedHeader()
        except:
            self.o2oWorkList['railroadName'] = self.opsWorkList['railroadName']

        self.o2oWorkList['railroadDescription'] = self.opsWorkList['railroadDescription']
        self.o2oWorkList['trainName'] = self.opsWorkList['trainName']
        self.o2oWorkList['trainDescription'] = self.opsWorkList['trainDescription']
        # self.o2oWorkList['trainComment'] = self.opsWorkList['trainComment']
        self.o2oWorkList['date'] = self.opsWorkList['date']

        location = self.opsWorkList['locations'][0]['locationName']

        self.o2oWorkList['locations'] = [{'locationName':location,'tracks':[{'trackName':'', 'length':'', 'cars':[], 'locos':[]}]}]
        self.o2oWorkList['locations'][0]['tracks'][0]['cars'] = self.cars
        self.o2oWorkList['locations'][0]['tracks'][0]['locos'] = self.locos

        return

    def convert(self):
        """Mini controller to convert the work list."""

        self.workListGetter()
        self.rsGetter()
        self.o2oWorkListUpdater()

        return self.o2oWorkList


class jmriManifestConversion:
    """Converts the JMRI generated manifest for use by o2oWorkEvents"""

    def __init__(self, builtTrain):

        self.configFile = PSE.readConfigFile()

        self.builtTrain = builtTrain
        self.jmriManifest = {}
        self.o2oWorkEvents = {}

        return

    def jmriManifestGetter(self):

        _psLog.debug('jmriManifestConversion.jmriManifestGetter')

        reportName = self.builtTrain.getName()
        fileName = 'train-' + reportName + '.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

        workEventList = PSE.genericReadReport(targetPath)
        self.jmriManifest = PSE.loadJson(workEventList)

        return

    def convertHeader(self):
        """Train comment is not in the JMRI train.json file."""

        _psLog.debug('jmriManifestConversion.convertHeader')

        if self.configFile['Main Script']['CP'][__package__]:

            OSU = PSE.JMRI.jmrit.operations.setup
            extendedHeader = unicode(OSU.Setup.getRailroadName(), PSE.ENCODING)
            self.o2oWorkEvents['railroadName'] = extendedHeader
        else:
            self.o2oWorkEvents['railroadName'] = PSE.HTML_PARSER().unescape(self.jmriManifest['railroad'])

        self.o2oWorkEvents['railroadDescription'] = PSE.JMRI.jmrit.operations.setup.Setup.getComment()
        self.o2oWorkEvents['trainName'] = PSE.HTML_PARSER().unescape(self.jmriManifest['userName'])
        self.o2oWorkEvents['trainDescription'] = PSE.HTML_PARSER().unescape(self.jmriManifest['description'])
        # self.o2oWorkEvents['trainComment'] = PSE.HTML_PARSER().unescape(self.jmriManifest['description'])

        epoch = PSE.convertJmriDateToEpoch(self.jmriManifest['date'])
        self.o2oWorkEvents['date'] = PSE.validTime(epoch)
        self.o2oWorkEvents['locations'] = []

        return

    def convertBody(self):

        _psLog.debug('jmriManifestConversion.convertBody')

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
                parsedRS = self.parseRS(loco)
                parsedRS['PUSO'] = u'PL'
                locos.append(parsedRS)
            for loco in location['engines']['remove']:
                parsedRS = self.parseRS(loco)
                parsedRS['PUSO'] = u'SL'
                locos.append(parsedRS)

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
        try:
            parsedRS['Load Type'] = PSE.getShortLoadType(rs)
            parsedRS['Load'] = rs['load']
        except:
            parsedRS['Load'] = rs['model']

        parsedRS['Location'] = rs['location']['userName']
        parsedRS['Track'] = rs['location']['track']['userName']
        parsedRS['Destination'] = rs['destination']['userName']
        parsedRS['Set_To'] = rs['destination']['track']['userName']

        return parsedRS

    def geto2oWorkEvents(self):

        return self.o2oWorkEvents


class o2oWorkEvents:
    """This class makes the o2o work event list for TrainPlayer.
        TrainPlayer rolling stock IDs are used to identify TP RS,
        using tpRollingStockData.json as the LUT.
        """

    def __init__(self, workEvents):

        self.tpRollingStockData = ModelEntities.getTpRailroadJson('tpRollingStockData')
        self.inverseTpRollingStockData = {v:k for k,v in self.tpRollingStockData.items()}
        # https://stackoverflow.com/questions/2568673/inverse-dictionary-lookup-in-python

        self.workEvents = workEvents
        self.o2oList = ''

        fileName = 'JMRI Report - o2o Work Events.csv'
        self.o2oWorkEventPath = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getHomePath(), 'AppData', 'Roaming', 'TrainPlayer', 'Reports', fileName)

        return

    def o2oHeader(self):

        _psLog.debug('o2oWorkEvents.o2oHeader')
        
        self.o2oList = 'HN,' + self.workEvents['railroadName'] + '\n'
        self.o2oList += 'HT,' + self.workEvents['trainName'] + '\n'
        self.o2oList += 'HD,' + self.workEvents['trainDescription'] + '\n'
        # self.o2oList += 'HC,' + self.workEvents['trainComment'] + '\n'
        self.o2oList += 'HV,' + self.workEvents['date'] + '\n'
        self.o2oList += 'WT,' + str(len(self.workEvents['locations'])) + '\n'

        return

    def o2oLocations(self):
        """This has to work for both JMRI and o2o generated lists"""

        _psLog.debug('o2oWorkEvents.o2oLocations')

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
        tpID = self.inverseTpRollingStockData[ID]
        load = ''
        try:
            load = rs['Load']
        except:
            load = rs['Model']

        try: # Locos don't use load type
            lt = rs['Load Type']
        except:
            lt = u'X'

        pu = rs['Location'] + ';' + rs['Track']

        so = rs['Destination'] + ';' + rs['Set_To']

        return rs['PUSO'] + ',' + tpID + ',' + rs['Road'] + ',' + rs['Number'] + ',' + rs['Type'] + ',' + lt + ',' + load + ',' + pu + ',' + so

    def saveList(self):

        _psLog.debug('o2oWorkEvents.saveList')

        if ModelEntities.tpDirectoryExists():
            PSE.genericWriteReport(self.o2oWorkEventPath, self.o2oList)

        print(SCRIPT_NAME + '.o2oWorkEvents ' + str(SCRIPT_REV))

        return

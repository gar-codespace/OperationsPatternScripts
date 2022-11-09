# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Creates the TrainPlayer JMRI Report - o2o Work Events.csv file from either PatternTracksSubroutine or BuiltTrainExport"""

from opsEntities import PSE
from o2oSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelWorkEvents'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.o2o.ModelWorkEvents')


def appendSetCarsForm(ptSetCarsForm):
    """Prepend the ptSetCarsForm to o2o Work Events.json.
        Used by:
        o2oSubroutine.Controller.o2oSwitchList
        """

    reportTitle = PSE.BUNDLE['o2o Work Events']
    fileName = reportTitle + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
# Load the existing o2o switch list
    o2oSwitchList = PSE.genericReadReport(targetPath)
    o2oSwitchList = PSE.loadJson(o2oSwitchList)
# Append cars and locos from ptSetCarsForm
    o2oSwitchListCars = o2oSwitchList['locations'][0]['tracks'][0]['cars']
    ptSetCarsFormCars = ptSetCarsForm['locations'][0]['tracks'][0]['cars']
    o2oSwitchList['locations'][0]['tracks'][0]['cars'] = o2oSwitchListCars + ptSetCarsFormCars
#
    o2oSwitchListLocos = o2oSwitchList['locations'][0]['tracks'][0]['locos']
    ptSetCarsFormLocos = ptSetCarsForm['locations'][0]['tracks'][0]['locos']
    o2oSwitchList['locations'][0]['tracks'][0]['locos'] = o2oSwitchListLocos + ptSetCarsFormLocos
# Write the appended file
    o2oSwitchList = PSE.dumpJson(o2oSwitchList)
    PSE.genericWriteReport(targetPath, o2oSwitchList)

    return


class o2oSwitchListConversion:
    """Converts the appended o2o switchlist for use by o2oWorkEvents"""

    def __init__(self):

        self.o2oSwitchList = {}

        self.cars = []
        self.locos = []

        return

    def o2oSwitchListGetter(self):

        reportName = PSE.BUNDLE['o2o Work Events']
        fileName = reportName + '.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

        o2oSwitchList = PSE.genericReadReport(targetPath)
        self.o2oSwitchList = PSE.loadJson(o2oSwitchList)

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
        """The load field is either Load(car) or Model(loco).
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
        """Used by:
            parsePtRs
            """

        x = setTo.split('[')
        y = x[1].split(']')

        return y[0]

    def o2oSwitchListUpdater(self):

        self.o2oSwitchList['locations'][0]['tracks'][0]['cars'] = self.cars
        self.o2oSwitchList['locations'][0]['tracks'][0]['locos'] = self.locos

        return

    def getO2oSwitchList(self):

        return self.o2oSwitchList

class jmriManifestConversion:
    """Converts the JMRI generated manifest for use by o2oWorkEvents"""

    def __init__(self, builtTrain):

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

        _psLog.debug('jmriManifestConversion.convertHeader')

        self.o2oWorkEvents['railroad'] = PSE.HTML_PARSER().unescape(self.jmriManifest['railroad'])
        self.o2oWorkEvents['trainName'] = PSE.HTML_PARSER().unescape(self.jmriManifest['userName'])
        self.o2oWorkEvents['trainDescription'] = PSE.HTML_PARSER().unescape(self.jmriManifest['description'])
        self.o2oWorkEvents['trainComment'] = PSE.HTML_PARSER().unescape(self.jmriManifest['description'])

        epoch = PSE.convertJmriDateToEpoch(self.jmriManifest['date'])
        self.o2oWorkEvents['date'] = PSE.timeStamp(epoch)
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

        reportName = 'tpRollingStockData'
        fileName = reportName + '.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        tpRollingStockData = PSE.genericReadReport(targetPath)
        self.tpRollingStockData = PSE.loadJson(tpRollingStockData)

        self.workEvents = workEvents
        self.o2oList = ''

        fileName = 'JMRI Report - o2o Work Events.csv'
        self.o2oWorkEventPath = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getHomePath(), 'AppData', 'Roaming', 'TrainPlayer', 'Reports', fileName)

        return

    def o2oHeader(self):

        _psLog.debug('o2oWorkEvents.o2oHeader')

        self.o2oList = 'HN,' + self.workEvents['railroad'] + '\n'
        self.o2oList += 'HT,' + self.workEvents['trainName'] + '\n'
        self.o2oList += 'HD,' + self.workEvents['trainDescription'] + '\n'
        self.o2oList += 'HC,' + self.workEvents['trainComment'] + '\n'
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
        tpID = self.tpRollingStockData[ID]
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

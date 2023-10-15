# coding=utf-8
# © 2023 Greg Ritacco

"""
Creates the TrainPlayer JMRI Report - o2o Workevents.csv file from either PatternTracksSubroutine or BuiltTrainExport
"""

from opsEntities import PSE
from Subroutines_Activated.o2o import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.o2o.ModelWorkEvents')

def convertOpsSwitchList():
    """
    Mini controller.
    Converts the Patterns ops-Switch List.json into an o2o work events file.
    Called by: Listeners - PROPERTY_CHANGE_EVENT.propertyName == 'patternsSwitchList' 
    """

    opsSwitchList = opsSwitchListConversion()
    if not opsSwitchList.validate():
        return
    
    tpWorkEventsList = opsSwitchList.convert()
    # o2oWorkEvents(tpWorkEventsList).makeList()

    print(SCRIPT_NAME + '.convertOpsSwitchList ' + str(SCRIPT_REV))

    return

def convertJmriManifest():
    """
    Mini controller.
    Converts a JMRI manifest to a Quick Keys work events list.
    Called by: Listeners - PROPERTY_CHANGE_EVENT.propertyName == 'TrainBuilt'
    """

    newestTrain = FindTrain().findNewestTrain()

    tpWorkEventsList = jmriManifestConversion(newestTrain).convert()
    o2oWorkEvents(tpWorkEventsList).makeList()

    return

def workListFromManifest():
    """
    Makes an o2o work list from an OPS modified JMRI manifest json.
    """

    newestTrain = FindTrain().findNewestTrain()
    # jsonManifest = PSE.JMRI.jmrit.operations.trains.JsonManifest(newestTrain).getFile()
    # jsonManifest = PSE.JMRI.util.FileUtil.readFile(jsonManifest)
    jsonManifest = ModelEntities.getManifestForTrain(newestTrain)
    # print(jsonManifest)



    
    # o2oWorkEvents().makeList(jsonManifest)

    return


class o2oWorkEvents:
    """
    This class makes the o2o work event list for TrainPlayer from:
    A stock JMRI generated manifest
    An OPS modified JMRI manifest
    An OPS generated Set Cars switch list
    """

    def __init__(self):

        self.jsonInput = ''
        self.opsSwitchList = ''

        self.o2oWorkEvents = ''
        outPutName = 'JMRI Report - o2o Workevents.csv'
        self.o2oWorkEventPath = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getHomePath(), 'AppData', 'Roaming', 'TrainPlayer', 'Reports', outPutName)

        return

    def getManifest(self, train):
        """
        Gets a train manifest, stock or modified by OPS.
        """

        manifestName = 'train-{}.json'.format(train.toString())
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', manifestName)

        if not PSE.JAVA_IO.File(targetPath).isFile():
            _psLog.info(manifestName + ' not found')
            return {}

        report = PSE.genericReadReport(targetPath)
        self.jsonInput = PSE.loadJson(report)

        self.makeWorkEvents()

        return
    
    def makeWorkEvents(self):
        """
        Mini controller.
        """
        
        self.o2oHeader()
        self.o2oLocations()

        
        
        # self.saveList()

        print(self.o2oWorkEvents)

        return
    
    def o2oHeader(self):

        _psLog.debug('o2oWorkEvents.o2oHeader')

        self.o2oWorkEvents = 'HN,' + self.jsonInput['railroad'].replace('\n', ';') + '\n'
        self.o2oWorkEvents += 'HT,' + self.jsonInput['userName'] + '\n'
        self.o2oWorkEvents += 'HD,' + self.jsonInput['description'] + '\n'
        epochTime = PSE.convertJmriDateToEpoch(self.jsonInput['date'])
        self.o2oWorkEvents += 'HV,' + PSE.validTime(epochTime) + '\n'
        self.o2oWorkEvents += 'WT,' + str(len(self.jsonInput['locations'])) + '\n'

        return

    def o2oLocations(self):
        """
        This works for both JMRI and o2o generated lists.
        """

        _psLog.debug('o2oWorkEvents.o2oLocations')

        counter = 1

        for location in self.jsonInput['locations']:
            self.o2oWorkEvents += 'WE,{},{}\n'.format(str(counter), location['userName'])

            for loco in location['engines']['add']:
                pass
            for loco in location['engines']['remove']:
                pass
            for car in location['cars']['add']:
                pass
            for car in location['cars']['remove']:
                pass

            counter += 1

        return

    def makeLine(self, rs):
        """
        This makes a rolling stock line for the TP o2o file.
        format: PUSO, TP ID, Road, Number, Car Type, L/E/O, Load or Model, From, To
        """

        ID = rs['road'] + ' ' + rs['number']
        load = ''
        try:
            load = rs['load']
        except:
            load = rs['model']

        try: # Locos don't use load type
            lt = rs['loadType']
        except:
            lt = 'X'

        pu = rs['location'] + ';' + rs['track']

        so = rs['destination'] + ';' + rs['setTo']

        return rs['puso'] + ',' + ID + ',' + rs['road'] + ',' + rs['number'] + ',' + rs['carType'] + ',' + lt + ',' + load + ',' + pu + ',' + so

    def saveList(self):

        _psLog.debug('o2oWorkEvents.saveList')

        if ModelEntities.tpDirectoryExists():
            PSE.genericWriteReport(self.o2oWorkEventPath, self.o2oWorkEvents)

        print(SCRIPT_NAME + '.o2oWorkEvents ' + str(SCRIPT_REV))

        return
    





class FindTrain:
    """
    Find a particular train using various crateria.
    """

    def __init__(self):

        self.builtTrainList = []
        self.getBuiltTrains()

        return
        
    def findNewestTrain(self):
        """
        If more than 1 train is built, pick the newest one.
        Returns a train object.
        """

        _psLog.debug('findNewestTrain')

        if not PSE.TM.isAnyTrainBuilt():
            return

        newestBuildTime = ''
        for train in self.getBuiltTrains():
            trainManifest = PSE.JMRI.jmrit.operations.trains.JsonManifest(train).getFile()
            trainManifest = PSE.JMRI.util.FileUtil.readFile(trainManifest)
            testDate = PSE.loadJson(trainManifest)['date']
            if testDate > newestBuildTime:
                newestBuildTime = testDate
                newestTrain = train

        return newestTrain

    def getBuiltTrains(self):

        _psLog.debug('getBuiltTrains')

        return [train for train in PSE.TM.getTrainsByStatusList() if train.isBuilt()]


class opsSwitchListConversion:
    """
    Converts a switch list generated by the Patterns subroutine into an TrainPlayer/Quick Keys compatable work events list.
    """

    def __init__(self):

        self.inputFileName = PSE.getBundleItem('ops-Switch List') + '.json'
        self.inputTargetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', self.inputFileName)

        self.opsSwitchList = {}
        self.cars = []
        self.locos = []

        self.tpWorkEventsList = {}

        self.validationResult = True

        return
    
    def validate(self):

        if not PSE.JAVA_IO.File(self.inputTargetPath).isFile():
            print('ALERT: not found-ops-Switch List.json')
            self.validationResult = False

        return self.validationResult

    def convert(self):
        """
        Mini controller.
        """

        self.switchListGetter()
        self.makeTpWorkEventsList()
        # self.addTracksToList()

        return self.tpWorkEventsList
    
    def switchListGetter(self):

        opsSwitchList = PSE.genericReadReport(self.inputTargetPath)
        self.opsSwitchList = PSE.loadJson(opsSwitchList)

        return
    
    def makeTpWorkEventsList(self):

        self.tpWorkEventsList['railroadName'] = self.opsSwitchList['railroad']
        self.tpWorkEventsList['railroadDescription'] = self.opsSwitchList['description']
        self.tpWorkEventsList['trainName'] = self.opsSwitchList['userName']
        self.tpWorkEventsList['trainDescription'] = self.opsSwitchList['userName']
        self.tpWorkEventsList['date'] = self.opsSwitchList['date']
        self.tpWorkEventsList['locations'] = self.opsSwitchList['locations']


        print(self.tpWorkEventsList)
        return

    def addTracksToList(self):

        tracks = []

        for track in self.opsSwitchList['tracks']:
            trackItems = {}
            self.cars = []
            self.locos = []
            for car in track['cars']:
                parsed = self.parsePtRs(car)
                parsed['puso'] = 'SC'
                self.cars.append(parsed)
            for loco in track['locos']:
                parsed = self.parsePtRs(loco)
                parsed['puso'] = 'SL'
                self.locos.append(parsed)
            trackItems['cars'] = self.cars
            trackItems['locos'] = self.locos
            tracks.append(trackItems)

        self.tpWorkEventsList['locations'][0].update({'tracks':tracks})

        return

    def parsePtRs(self, rs):
        """
        The load field is either Load(car) or Model(loco).
        Pattern scripts have only one location.
        Location and Destination are the same.
        """

        parsedRS = {}
        parsedRS['road'] = rs[PSE.SB.handleGetMessage('Road')]
        parsedRS['number'] = rs[PSE.SB.handleGetMessage('Number')]
        parsedRS['carType'] = rs[PSE.SB.handleGetMessage('Type')]
        parsedRS['destination'] = rs[PSE.SB.handleGetMessage('Location')]
        parsedRS['location'] = rs[PSE.SB.handleGetMessage('Location')]
        parsedRS['track'] = rs[PSE.SB.handleGetMessage('Track')]
        try:
            parsedRS['loadType'] = PSE.getShortLoadType(rs)
            parsedRS['load'] = rs[PSE.SB.handleGetMessage('Load')]
        except:
            parsedRS['load'] = rs[PSE.SB.handleGetMessage('Model')]

        if self.parseSetTo(rs['setTo']) == PSE.getBundleItem('Hold'):
            parsedSetTo = rs[PSE.SB.handleGetMessage('Track')]
        else:
            parsedSetTo = self.parseSetTo(rs['setTo'])
        parsedRS['setTo'] = parsedSetTo

        return parsedRS

    def parseSetTo(self, setTo):
        """
        format: [Freight House]   
        """

        return setTo[1:-1].split(']')[0]


class jmriManifestConversion:
    """
    Converts the JMRI generated manifest for use by o2oWorkEvents.
    """

    def __init__(self, builtTrain):

        self.builtTrain = builtTrain
        self.jmriManifest = {}
        self.o2oWorkEvents = {}

        self.cars = []
        self.locos = []

        return

    def convert(self):
        """
        Mini controller.
        """

        self.jmriManifestGetter()
        self.convertHeader()
        self.convertBody()

        return self.o2oWorkEvents
    
    def jmriManifestGetter(self):

        _psLog.debug('jmriManifestConversion.jmriManifestGetter')

        reportName = self.builtTrain.getName()
        fileName = 'train-' + reportName + '.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

        workEventList = PSE.genericReadReport(targetPath)
        self.jmriManifest = PSE.loadJson(workEventList)

        return

    def convertHeader(self):
        """
        Train comment is not in the JMRI train.json file.
        """

        _psLog.debug('jmriManifestConversion.convertHeader')

        self.o2oWorkEvents['railroadName'] = PSE.HTML_PARSER().unescape(self.jmriManifest['railroad'])
        self.o2oWorkEvents['railroadDescription'] = PSE.JMRI.jmrit.operations.setup.Setup.getComment()
        self.o2oWorkEvents['trainName'] = PSE.HTML_PARSER().unescape(self.jmriManifest['userName'])
        self.o2oWorkEvents['trainDescription'] = PSE.HTML_PARSER().unescape(self.jmriManifest['description'])

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
                parsedRS['puso'] = 'PC'
                cars.append(parsedRS)
            for car in location['cars']['remove']:
                parsedRS = self.parseRS(car)
                parsedRS['puso'] = 'SC'
                cars.append(parsedRS)

            locos = []
            for loco in location['engines']['add']:
                parsedRS = self.parseRS(loco)
                parsedRS['puso'] = 'PL'
                locos.append(parsedRS)
            for loco in location['engines']['remove']:
                parsedRS = self.parseRS(loco)
                parsedRS['puso'] = 'SL'
                locos.append(parsedRS)

            self.o2oWorkEvents['locations'].append({'locationName': location['userName'], 'tracks': [{'cars': cars, 'locos': locos}]})

        return

    def parseRS(self, rs):
        """
        The load field ie either Load or Model.
        """

        parsedRS = {}
        parsedRS['road'] = rs['road']
        parsedRS['number'] = rs['number']
        parsedRS['carType'] = rs['carType']
        parsedRS['location'] = rs['location']['userName']
        parsedRS['track'] = rs['location']['track']['userName']
        parsedRS['destination'] = rs['destination']['userName']
        parsedRS['setTo'] = rs['destination']['track']['userName']

        try:
            parsedRS['loadType'] = PSE.getShortLoadType(rs)
            parsedRS['load'] = rs['load']
        except:
            parsedRS['load'] = rs['model']

        return parsedRS

    def geto2oWorkEvents(self):

        return self.o2oWorkEvents



# class o2oWorkEvents:
#     """
#     This class makes the o2o work event list for TrainPlayer.
#     """

#     def __init__(self, workEvents):

#         self.workEvents = workEvents
#         self.o2oList = ''

#         fileName = 'JMRI Report - o2o Workevents.csv'
#         self.o2oWorkEventPath = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getHomePath(), 'AppData', 'Roaming', 'TrainPlayer', 'Reports', fileName)

#         return

#     def makeList(self):
#         """
#         Mini controller.
#         """
        
#         self.o2oHeader()
#         self.o2oLocations()
#         self.saveList()

#         return
    
#     def o2oHeader(self):

#         _psLog.debug('o2oWorkEvents.o2oHeader')

#         self.o2oList = 'HN,' + PSE.getExtendedRailroadName().replace('\n', ';') + '\n'
#         self.o2oList += 'HT,' + self.workEvents['trainName'] + '\n'
#         self.o2oList += 'HD,' + self.workEvents['trainDescription'] + '\n'
#         self.o2oList += 'HV,' + self.workEvents['date'] + '\n'
#         self.o2oList += 'WT,' + str(len(self.workEvents['locations'])) + '\n'

#         return

#     def o2oLocations(self):
#         """
#         This works for both JMRI and o2o generated lists.
#         """

#         _psLog.debug('o2oWorkEvents.o2oLocations')

#         counter = 1

#         for location in self.workEvents['locations']:
#             self.o2oList += 'WE,' + str(counter) + ',' + location['locationName'] + '\n'
#             for track in location['tracks']:
#                 for car in track['cars']:
#                     self.o2oList += self.makeLine(car) + '\n'
#                 for loco in track['locos']:
#                     self.o2oList += self.makeLine(loco) + '\n'

#             counter += 1

#         return

#     def makeLine(self, rs):
#         """
#         This makes a rolling stock line for the TP o2o file.
#         format: PUSO, TP ID, Road, Number, Car Type, L/E/O, Load or Model, From, To
#         """

#         ID = rs['road'] + ' ' + rs['number']
#         load = ''
#         try:
#             load = rs['load']
#         except:
#             load = rs['model']

#         try: # Locos don't use load type
#             lt = rs['loadType']
#         except:
#             lt = 'X'

#         pu = rs['location'] + ';' + rs['track']

#         so = rs['destination'] + ';' + rs['setTo']

#         return rs['puso'] + ',' + ID + ',' + rs['road'] + ',' + rs['number'] + ',' + rs['carType'] + ',' + lt + ',' + load + ',' + pu + ',' + so

#     def saveList(self):

#         _psLog.debug('o2oWorkEvents.saveList')

#         if ModelEntities.tpDirectoryExists():
#             PSE.genericWriteReport(self.o2oWorkEventPath, self.o2oList)

#         print(SCRIPT_NAME + '.o2oWorkEvents ' + str(SCRIPT_REV))

#         return
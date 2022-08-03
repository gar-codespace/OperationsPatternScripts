# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.ModelImport'
SCRIPT_REV = 20220101

class TrainPlayerImporter:

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ModelImport')

        self.tpLocationsFile = 'TrainPlayer Export - Locations.txt'
        self.tpIndustriesFile = 'TrainPlayer Export - Industries.txt'
        self.tpInventoryFile = 'TrainPlayer Export - Inventory.txt'

        self.tpLocations = []
        self.tpIndustries = []
        self.tpInventory = []
        self.okCounter = 0

        self.rrFile = 'tpRailroad.json'
        self.rr = {}
        self.rrLocations = {}
        self.rrIndustries = {}
        self.rrInventory = {}

        return

    def checkFiles(self):

        try:
            self.tpLocations = ModelEntities.getTpExport(self.tpLocationsFile)
            self.psLog.info('TrainPlayer Locations file OK')
            self.okCounter += 1
        except:
            self.psLog.warning('TrainPlayer Locations file not found')
            print('Not found: ' + self.tpLocationsFile)

        try:
            self.tpIndustries = ModelEntities.getTpExport(self.tpIndustriesFile)
            self.psLog.info('TrainPlayer Industries file OK')
            self.okCounter += 1
        except:
            self.psLog.warning('TrainPlayer Locations file not found')
            print('Not found: ' + self.tpIndustriesFile)

        try:
            self.tpInventory = ModelEntities.getTpExport(self.tpInventoryFile)
            self.psLog.info('TrainPlayer Inventory file OK')
            self.okCounter += 1
        except:
            self.psLog.warning('TrainPlayer Inventory file not found')
            print('Not found: ' + self.tpInventoryFile)

        return

    def makeRrHeader(self):
        """Add the date"""

        self.rr[u'railroadName'] = self.tpLocations.pop(0)
        self.rr[u'railroadDescription'] = self.tpLocations.pop(0)
        self.rr[u'date'] = u'date'

        return


    def makeRrLocations(self):
        """self.tpLocations format: TP ID; JMRI Location Name; JMRI Track Name; TP Label, TP Type; TP Spaces"""

        locationList = [u'Undefined']

        self.tpLocations.pop(0)
        self.tpLocations.pop(0)
        self.tpLocations.pop(0)

        for lineItem in self.tpLocations:
            splitLine = lineItem.split(';')
            locationList.append(splitLine[1])
            self.rrLocations[splitLine[0]] = {u'location': splitLine[1], u'track': splitLine[2], u'type': self.getTrackType(splitLine[4]), u'capacity': splitLine[5]}

        self.rr['locations'] = list(set(locationList))
        self.rr['locales'] = self.rrLocations
        print(self.rr)

        return

    def getTrackType(self, tpType):

        rubric = {'industry': u'spur', u'interchange': 'interchange', u'staging': 'staging', u'class yard': 'yard'}

        return rubric[tpType]

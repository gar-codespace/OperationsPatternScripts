# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Use the TP inventory, locations and industries text files to generate the tpRailroadData.json file"""

from opsEntities import PSE
from o2oSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelImport'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.o2o.ModelImport')

def importTpRailroad():
    """Mini controller generates the tpRailroadData.json file"""

    trainPlayerImport = TrainPlayerImporter()
# Import the three TrainPlayer export files
    if not trainPlayerImport.getTpReportFiles():
        boilerplateErrors()
        return False
# Test the integrity of the locations file
    if not trainPlayerImport.checkLocationsFile():
        boilerplateErrors()
        return False
# Test the integrity of the Industries file
    if not trainPlayerImport.checkIndustriesFile():
        boilerplateErrors()
        return False

    trainPlayerImport.processFileHeaders()
    trainPlayerImport.getRrLocations()
    trainPlayerImport.getRrLocales()

    trainPlayerImport.getAllTpRoads()
    trainPlayerImport.getAllTpIndustry()

    trainPlayerImport.getAllTpCarAar()
    trainPlayerImport.getAllTpCarLoads()
    trainPlayerImport.getAllTpCarKernels()

    trainPlayerImport.getAllTpLocoTypes()
    trainPlayerImport.getAllTpLocoModels()
    trainPlayerImport.getAllTpLocoConsists()

    trainPlayerImport.writeTPLayoutData()

    return True

def boilerplateErrors():
    _psLog.critical('Error: TrainPlayer export issue.')
    PSE.openOutputPanel(PSE.BUNDLE['ALERT: TrainPlayer export issue.'])
    PSE.openOutputPanel(PSE.BUNDLE['From TrainPlayer, re-export layout to JMRI.'])
    PSE.openOutputPanel(PSE.BUNDLE['TrainPlayer layout not imported to JMRI.'])
    PSE.openOutputPanel('')

    return

class TrainPlayerImporter:

    def __init__(self):

        o2oConfig =  PSE.readConfigFile('o2o')

        self.tpLocationsFile = o2oConfig['RF']['TRL']
        self.tpIndustriesFile = o2oConfig['RF']['TRI']
        self.tpRollingStockFile = o2oConfig['RF']['TRR']

        self.tpLocations = []
        self.tpIndustries = []
        self.tpInventory = []

        reportName = 'tpRailroadData'
        fileName = reportName + '.json'
        self.rrFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        self.rr = {}

        return

    def getTpReportFiles(self):
        """Returns true if all 3 files import ok."""

        _psLog.debug('getTpReportFiles')

        fileCheck = True

        self.tpLocations = ModelEntities.getTpExport(self.tpLocationsFile)
        if self.tpLocations:
            _psLog.info('TrainPlayer Locations file OK')
        else:
            _psLog.critical('TrainPlayer Locations file not found')
            PSE.openOutputPanel(PSE.BUNDLE['ALERT: TrainPlayer Locations file not found.'])
            print('Not found: ' + self.tpLocationsFile)
            fileCheck = False


        self.tpIndustries = ModelEntities.getTpExport(self.tpIndustriesFile)
        if self.tpIndustries:
            _psLog.info('TrainPlayer Industries file OK')
        else:
            _psLog.critical('TrainPlayer Industries file not found')
            PSE.openOutputPanel(PSE.BUNDLE['ALERT: TrainPlayer Industries file not found.'])
            print('Not found: ' + self.tpIndustriesFile)
            fileCheck = False


        self.tpInventory = ModelEntities.getTpExport(self.tpRollingStockFile)
        if self.tpInventory:
            _psLog.info('TrainPlayer Inventory file OK')
        else:
            _psLog.critical('TrainPlayer Inventory file not found')
            PSE.openOutputPanel(PSE.BUNDLE['ALERT: TrainPlayer Inventory file not found.'])
            print('Not found: ' + self.tpRollingStockFile)
            fileCheck = False

        return fileCheck

    def checkLocationsFile(self):
        """Each line in the locations file should have 5 semi colons."""

        if [line.count(';') for line in self.tpLocations if line.count(';') != 5]:
            _psLog.critical('Error: Locations file formatting error.')
            PSE.openOutputPanel(PSE.BUNDLE['Check TrainPlayer-Advanced Ops-Locales for semi colon.'])
            print('Error: Locations file formatting error')

            return False

        return True

    def checkIndustriesFile(self):
        """Each line in the industries file should have 10 semi colons."""

        if [line.count(';') for line in self.tpIndustries if line.count(';') != 10]:
            _psLog.critical('Error: Industries file formatting error.')
            PSE.openOutputPanel(PSE.BUNDLE['Check TrainPlayer-Advanced Ops-Industries for errors.'])
            print('Error: Industries file formatting error')

            return False

        return True

    def processFileHeaders(self):
        """Process the header info from the TP report files.
            replace(';', '') removes the semi colons at the end of each header line.
            """

        _psLog.debug('processFileHeaders')

        self.rr[u'trainplayerDate'] = self.tpLocations.pop(0).replace(';', '')

        rrData = self.tpLocations.pop(0).split(';')
        self.rr[u'railroadName'] = rrData[0]
        self.rr[u'railroadParent'] = rrData[1]
        self.rr[u'railroadDescription'] = rrData[2]
        self.rr[u'railroadYear'] = rrData[3]

        self.rr[u'date'] = PSE.timeStamp()
        self.tpLocations.pop(0) # Remove key

        self.tpIndustries.pop(0) # Remove date
        self.tpIndustries.pop(0) # Remove key

        self.tpInventory.pop(0) # Remove date
        self.tpInventory.pop(0) # Remove key

        return

    def getRrLocations(self):
        """self.tpLocations format: TP ID; JMRI Location Name; JMRI Track Name; TP Label; TP Type; TP Spaces.
            Makes a list of just the locations.
            """
        _psLog.debug('getRrLocations')

        locationList = [u'Unknown']
        rrLocations = {}

        for lineItem in self.tpLocations:
            splitLine = lineItem.split(';')
            locationList.append(splitLine[1])

        self.rr['locations'] = list(set(locationList))

        return

    def getRrLocales(self):
        """self.tpLocations format: TP ID; JMRI Location Name; JMRI Track Name; TP Label; TP Type; TP Spaces.
            Makes a list of tuples of the locales and their data.
            locale format: (location, {ID, Capacity, Type, Track})
            """
        _psLog.debug('getRrLocales')

        locales = {}
        locales['00'] = {u'location': 'Unknown', u'track': '~', u'label': '~', u'type': 'class yard', u'capacity': '100'}

        for lineItem in self.tpLocations:
            splitLine = lineItem.split(';')
            locales[splitLine[0]] = {u'location': splitLine[1], u'track': splitLine[2], u'label': splitLine[3], u'type': splitLine[4], u'capacity': splitLine[5]}

        self.rr['locales'] = locales

        return

    def getAllTpIndustry(self):
        """self.tpIndustryList format: ID, JMRI Location Name, JMRI Track Name, Industry, AAR, S/R, Load, Staging, ViaIn
            Makes a list of tuples of the industries and their data.
            industry format: [JMRI Location Name, {ID, JMRI Track Name, Industry, AAR, schedule(label, aar, receive, ship), Staging, ViaIn, ViaOut}]
            """

        _psLog.debug('getAllTpIndustry')

        industryDict = {}
        receive = ''
        ship = ''
        for lineItem in self.tpIndustries:
            splitLine = lineItem.split(';')
            if splitLine[5] == 'S':
                receive = 'Empty'
                ship = splitLine[6]
            else:
                receive = splitLine[6]
                ship = 'Empty'
            schedule = (splitLine[3], splitLine[4], receive, ship)
            industryDict[splitLine[0]] = {u'location': splitLine[1], u'track': splitLine[2], u'label': splitLine[3], u'type': splitLine[4], u'schedule': schedule, u'staging': splitLine[7], u'viaIn': splitLine[8], u'viaOut': splitLine[9]}

        self.rr['industries'] = industryDict

        return

    def getAllTpRoads(self):

        _psLog.debug('getAllTpRoads')

        roadList = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            road, number = ModelEntities.parseCarId(splitItem[0])
            roadList.append(road)

        self.rr['roads'] = list(set(roadList))

        return

    def getAllTpCarAar(self):

        _psLog.debug('getAllTpCarAar')

        allItems = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('E'):
                continue
            else:
                allItems.append(splitItem[2])

        self.rr['carAAR'] = list(set(allItems))

        return

    def getAllTpCarLoads(self):

        _psLog.debug('getAllTpCarLoads')

        carLoads = {}
        xList = []
        for lineItem in self.tpIndustries:
            splitLine = lineItem.split(';')
            xList.append((splitLine[4], splitLine[6]))

        for aar in self.rr['carAAR']:
            loadList = []
            for item in xList:
                if item[0] == aar:
                    loadList.append(item[1])
            carLoads[aar] = list(set(loadList))

        self.rr['carLoads'] = carLoads

        return

    def getAllTpCarKernels(self):

        _psLog.debug('getAllTpCarKernels')

        allItems = []

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('E'):
                continue
            else:
                allItems.append(splitItem[6])

        self.rr['carKernel'] = list(set(allItems))

        return

    def getAllTpLocoTypes(self):
        """Don't include tenders"""

        _psLog.debug('getAllTpLocoTypes')

        allItems = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('ET'):
                continue
            if splitItem[2].startswith('E'):
                allItems.append(splitItem[2])

        self.rr['locoTypes'] = list(set(allItems))

        return

    def getAllTpLocoModels(self):
        """character length fromOperations.xml\<max_len_string_attibute length="10" />
            List of tuples: (JMRI model, JMRI type)
            Don't include tenders
            """
        _psLog.debug('getAllTpLocoModels')

        allItems = []

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('ET'):
                continue
            if splitItem[2].startswith('E'):
                allItems.append((splitItem[1][0:11], splitItem[2]))

        self.rr['locoModels'] = list(set(allItems))

        return

    def getAllTpLocoConsists(self):

        _psLog.debug('getAllTpLocoConsists')

        allItems = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('ET'):
                continue
            if splitItem[2].startswith('E'):
                allItems.append(splitItem[6])

        self.rr['locoConsists'] = list(set(allItems))

        return

    def writeTPLayoutData(self):

        _psLog.debug('writeTPLayoutData')

        formattedRrFile = PSE.dumpJson(self.rr)
        PSE.genericWriteReport(self.rrFile, formattedRrFile)

        return

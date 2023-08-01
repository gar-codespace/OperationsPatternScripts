# coding=utf-8
# © 2023 Greg Ritacco

"""
Use the TrainPlayer/Reports: rolling stock, locations and industries text files to generate the tpRailroadData.json file.
"""

from opsEntities import PSE
from Subroutines.o2o import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.o2o.ModelImport')
    
def importTpRailroad():
    """
    Mini controller.
    Generates the tpRailroadData.json file
    Generates the tpRollingStockData.txt file
    """

    PSE.closeOutputFrame()
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
# Test the integrity of the Rolling Stock file
    if not trainPlayerImport.checkInventoryFile():
        boilerplateErrors()
        return False
    
    trainPlayerImport.processLocationsHeader()
    trainPlayerImport.processIndustriesHeader()
    trainPlayerImport.processTpInventory()
    trainPlayerImport.getLocationIds()
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

    trainPlayerImport.writeLayoutData()
    trainPlayerImport.writeRollingStockData()

    return True

def boilerplateErrors():

    _psLog.critical('ERROR: Missing or corrupt TrainPlayer export file.')
    _psLog.critical('TrainPlayer railroad not imported')

    b = PSE.getBundleItem('From TrainPlayer, re-export layout to JMRI.')
    c = PSE.getBundleItem('TrainPlayer layout not imported to JMRI.')
    message = b + '\n' + c + '\n'

    PSE.openOutputFrame(message)

    return

class TrainPlayerImporter:

    def __init__(self):

        self.configFile =  PSE.readConfigFile()

        self.tpLocations = []
        self.tpIndustries = []
        self.tpInventory = []

        self.tpEngineAar = []
        self.tpCabooseAar = []
        self.tpPassAar = []
        self.tpMowAar = []

        reportName = self.configFile['o2o']['RF']['RRD']
        fileName = reportName + '.json'
        self.rrFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        self.rr = {}

        reportName = self.configFile['o2o']['RF']['RSD']
        fileName = reportName + '.txt'
        self.inventoryFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        return

    def getTpReportFiles(self):
        """
        Returns true if all 3 TrainPlayer export files import ok.
        """

        _psLog.debug('getTpReportFiles')

        fileCheck = True

        self.tpLocations = ModelEntities.getTpExport(self.configFile['o2o']['RF']['TRL'])
        if self.tpLocations:
            _psLog.info('TrainPlayer Report - Locations.txt file found')
        else:
            _psLog.critical('TrainPlayer Report - Locations.txt file not found')
            PSE.openOutputFrame(PSE.getBundleItem('ALERT: File not found:') + ' TrainPlayer Report - Locations.txt')
            fileCheck = False


        self.tpIndustries = ModelEntities.getTpExport(self.configFile['o2o']['RF']['TRI'])
        if self.tpIndustries:
            _psLog.info('TrainPlayer Report - Industries.txt file found')
        else:
            _psLog.critical('TrainPlayer Report - Industries.txt file not found')
            PSE.openOutputFrame(PSE.getBundleItem('ALERT: File not found:') + ' TrainPlayer Report - Industries.txt')
            fileCheck = False


        self.tpInventory = ModelEntities.getTpExport(self.configFile['o2o']['RF']['TRR'])
        if self.tpInventory:
            _psLog.info('TrainPlayer Report - Rolling Stock.txt file found')
        else:
            _psLog.critical('TrainPlayer Inventory file not found')
            PSE.openOutputFrame(PSE.getBundleItem('ALERT: File not found:') + ' TrainPlayer Report - Rolling Stock.txt')
            fileCheck = False

        return fileCheck

    def checkLocationsFile(self):
        """
        Each line in the locations file should have 5 semicolons.
        """

        if [line.count(';') for line in self.tpLocations if line.count(';') != 5]:
            _psLog.critical('Error: Locations file formatting error.')
            PSE.openOutputFrame(PSE.getBundleItem('Check TrainPlayer-Advanced Ops-Locales for semicolon.'))

            return False

        return True

    def checkIndustriesFile(self):
        """
        Each line in the industries file should have 10 semicolons.
        """

        if [line.count(';') for line in self.tpIndustries if line.count(';') != 10]:
            _psLog.critical('Error: Industries file formatting error.')
            PSE.openOutputFrame(PSE.getBundleItem('Check TrainPlayer-Advanced Ops-Industries for errors.'))

            return False

        return True

    def checkInventoryFile(self):
        """
        Each line in the rolling stock file should have 7 semicolons.
        """

        if [line.count(';') for line in self.tpInventory if line.count(';') != 7]:
            PSE.openOutputFrame(PSE.getBundleItem('ALERT: import error, Rolling Stock not imported.'))
            _psLog.critical('Error: Rolling Stock file formatting error.')

            return False

        return True
    
    def processLocationsHeader(self):
        """
        Process the header info from TrainPlayer Report - Locations.txt.
        """

        _psLog.debug('processLocationsHeader')

        rrData = self.tpLocations.pop(0).split(';') # Pop off the date and layout name
        self.rr['Extended_buildDate'] = rrData[0]
        self.rr['Extended_layoutName'] = rrData[1]

        rrData = self.tpLocations.pop(0).split(';') # Pop off the details line
        self.rr['Extended_operatingRoad'] = rrData[0]
        self.rr['Extended_territory'] = rrData[1]
        self.rr['Extended_location'] = rrData[2]
        self.rr['Extended_year'] = rrData[3]
        self.rr['Extended_divisions'] = rrData[4].split(',')
        self.rr['Extended_scale'] = rrData[5]

    # A few blank lines were added to make expansion easy.
        self.tpLocations.pop(0)
        self.tpLocations.pop(0)
        self.tpLocations.pop(0)

        return

    def processIndustriesHeader(self):
        """
        Process the header info from TrainPlayer Report - Industries.txt.
        """

        _psLog.debug('processIndustriesHeader')

        self.tpIndustries.pop(0) # Remove date
        self.tpIndustries.pop(0) # Remove key

    # A few blank lines were added to make expansion easy.
        self.tpIndustries.pop(0)
        self.tpIndustries.pop(0)
        self.tpIndustries.pop(0)

        self.tpIndustries.sort()

        return
    
    def processTpInventory(self):
        """
        Write the Random Roads AAR lists or the default from the config file into tpRailroadData.json
        """

        _psLog.debug('processTpInventory')

        self.tpEngineAar = self.tpInventory.pop(0).split(';')[1].split(' ')
        self.tpCabooseAar = self.tpInventory.pop(0).split(';')[1].split(' ')
        self.tpMowAar = self.tpInventory.pop(0).split(';')[1].split(' ')
        self.tpPassAar = self.tpInventory.pop(0).split(';')[1].split(' ')
        self.tpExpressAAR = self.tpInventory.pop(0).split(';')[1].split(' ')
    # A few blank lines were added to make expansion easy.
        self.tpInventory.pop(0)
        self.tpInventory.pop(0)
        self.tpInventory.pop(0)

        if self.tpEngineAar:
            self.rr['AAR_Engine'] = self.tpEngineAar
        else:
            self.rr['AAR_Engine'] = self.configFile['o2o']['XE']

        if self.tpCabooseAar:
            self.rr['AAR_Caboose'] = self.tpCabooseAar
        else:
            self.rr['AAR_Caboose'] = self.configFile['o2o']['XC']

        if self.tpMowAar:
            self.rr['AAR_MOW'] = self.tpMowAar
        else:
            self.rr['AAR_MOW'] = self.configFile['o2o']['XM']

        if self.tpPassAar:
            self.rr['AAR_Passenger'] = self.tpPassAar
        else:
            self.rr['AAR_Passenger'] = self.configFile['o2o']['XP']

        if self.tpExpressAAR:
            self.rr['AAR_Express'] = self.tpExpressAAR
        else:
            self.rr['AAR_Express'] = self.configFile['o2o']['XX']

        return

    def getLocationIds(self):
        """
        Add location IDs to tpRailroadData.json.
        """

        _psLog.debug('getLocationIds')

        tpLocationIds = ['00']

        for lineItem in self.tpLocations:
            splitLine = lineItem.split(';')
            tpLocationIds.append(splitLine[0])

        self.rr['LocationRoster_locationIds'] = tpLocationIds

        return

    def getRrLocations(self):
        """
        self.tpLocations format: TP ID; JMRI Location Name; JMRI Track Name; TP Label; TP Type; TP Spaces.
        Makes a list of just the locations.
        """
        _psLog.debug('getRrLocations')

        locationList = [PSE.getBundleItem('Unreported')]

        for lineItem in self.tpLocations:
            splitLine = lineItem.split(';')
            locationList.append(splitLine[1])

        self.rr['LocationRoster_locations'] = list(set(locationList))

        return

    def getRrLocales(self):
        """
        self.tpLocations format: TP ID; JMRI Location Name; JMRI Track Name; TP Label; TP Type; TP Spaces.
        Makes a list of tuples of the locales and their data.
        locale format: (location, {ID, Capacity, Type, Track})
        """
        _psLog.debug('getRrLocales')

        locales = {}
        uLocation = PSE.getBundleItem('Unreported')
        
        locales['00'] = {u'location': uLocation, u'track': '~', u'label': '~', u'type': 'class yard', u'capacity': '100'}

        for lineItem in self.tpLocations:
            splitLine = lineItem.split(';')
            locales[splitLine[0]] = {u'location': splitLine[1], u'track': splitLine[2], u'label': splitLine[3], u'type': splitLine[4], u'capacity': splitLine[5]}

        self.rr['LocationRoster_location'] = locales

        return

    def getAllTpIndustry(self):
        """
        self.tpIndustryList format: JMRI Location Name[0], JMRI Track Name[1], Track Label[2], AAR[3], S/R[4], Load Name[5], Staging[6], ViaIn[7], ViaOut[8], TP ID[9]
        Makes a list of tuples of the industries and their data.
        industry format: [JMRI Location Name, {ID, JMRI Track Name, Industry, AAR, schedule(label, aar, [receive, ship]), Staging, ViaIn, ViaOut}]
        """

        _psLog.debug('getAllTpIndustry')

        tpBackup = self.tpIndustries[:]

        industryDict = {}
        locale = ''
        while self.tpIndustries:
            line = self.tpIndustries.pop(0).split(';')
            
            if line[0] + line[1] == locale:
            # Add to existing
                trackLabel = line[2]
                aarName = line[3]
                sr = line[4]
                loadName = line[5]
                stagingName = line[6]
                viaIn = line[7]
                viaOut = line[8]
                scheduleItem = (aarName, sr, loadName, stagingName, viaIn, viaOut)
                industryDict[tpId]['c-schedule'][trackLabel].append(scheduleItem)
            else:
            # Start a new one
                locationName = line[0]
                trackName = line[1]
                trackLabel = line[2]
                aarName = line[3]
                sr = line[4]
                loadName = line[5]
                stagingName = line[6]
                viaIn = line[7]
                viaOut = line[8]
                tpId = line[9]
                scheduleItem = (aarName, sr, loadName, stagingName, viaIn, viaOut)
                schedule = {trackLabel:[scheduleItem]}
                industryDict[tpId] = {u'a-location': locationName, u'b-track': trackName, u'c-schedule': schedule}

            locale = line[0] + line[1]
            
        self.rr['LocationRoster_spurs'] = industryDict

        self.tpIndustries = tpBackup[:]

        return

    def getAllTpRoads(self):

        _psLog.debug('getAllTpRoads')

        roadList = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            road, number = ModelEntities.parseCarId(splitItem[0])
            roadList.append(road)

        self.rr['CarRoster_roads'] = list(set(roadList))

        return

    def getAllTpCarAar(self):
        """
        In TrainPlayer they are car AAR.
        In JMRI they are car types.
        """

        _psLog.debug('getAllTpCarAar')

        allItems = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('E'):
                continue
            else:
                allItems.append(splitItem[2])

        self.rr['CarRoster_types'] = list(set(allItems))

        return

    def getAllTpCarLoads(self):

        _psLog.debug('getAllTpCarLoads')

        carLoads = {}
        aarNameLoadNameList = []
        for industry in self.tpIndustries:
            splitLine = industry.split(';')
            aarNameLoadNameList.append((splitLine[3], splitLine[5]))

        aarNameLoadNameList = list(set(aarNameLoadNameList))

        for aar in self.rr['CarRoster_types']:
            loadList = []
            for item in aarNameLoadNameList:
                if item[0] == aar:
                    loadList.append(item[1])

            carLoads[aar] = list(set(loadList))

        self.rr['CarRoster_loads'] = carLoads

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

        self.rr['CarRoster_newKernels'] = list(set(allItems))

        return

    def getAllTpLocoTypes(self):
        """
        Don't include tenders
        """

        _psLog.debug('getAllTpLocoTypes')

        allItems = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('ET'):
                continue
            if splitItem[2].startswith('E'):
                allItems.append(splitItem[2])

        self.rr['EngineRoster_types'] = list(set(allItems))

        return

    def getAllTpLocoModels(self):
        """
        Character length fromOperations.xml\<max_len_string_attibute length="10" />
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

        self.rr['EngineRoster_models'] = list(set(allItems))

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

        self.rr['EngineRoster_newConsists'] = list(set(allItems))

        return

    def writeLayoutData(self):

        _psLog.debug('writeLayoutData')

        PSE.genericWriteReport(self.rrFile, PSE.dumpJson(self.rr))

        return
    
    def writeRollingStockData(self):

        _psLog.debug('writeRollingStockData')

        inventory = ''
        for item in self.tpInventory:
            inventory += item + '\n'

        inventory = inventory[:-1]

        PSE.genericWriteReport(self.inventoryFile, inventory)

        return

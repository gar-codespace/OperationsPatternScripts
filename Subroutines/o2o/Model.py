# coding=utf-8
# © 2023 Greg Ritacco

"""From tpRailroadData.json, a new JMRI railroad is created or updated."""

from opsEntities import PSE
from Subroutines.o2o import ModelEntities
from Subroutines.o2o import BuiltTrainExport

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

FILE_LIST = ['OperationsTrainRoster.xml', 'OperationsRouteRoster.xml']


_psLog = PSE.LOGGING.getLogger('OPS.o2o.Model')

def resetConfigFileItems():
    """Called from PSE.remoteCalls('resetCalls')"""

    # configFile = PSE.readConfigFile()
    # PSE.writeConfigFile(configFile)

    return
    
def newJmriRailroad():
    """
    Mini controller to make a new JMRI railroad.
    tpRailroadData.json and TrainPlayer Report - Rolling Stock.txt
    are used as source files.
    Called by:
    Controller.StartUp.newJmriRailroad
    """

    PSE.closeSubordinateWindows()
    PSE.remoteCalls('resetCalls')

    PSE.TMX.makeBackupFile('operations/OperationsTrainRoster.xml')
    PSE.TMX.makeBackupFile('operations/OperationsRouteRoster.xml')

    PSE.TM.dispose()
    PSE.RM.dispose()
    PSE.DM.dispose()
    PSE.LM.dispose()
    # PSE.SM.dispose()
    PSE.CM.dispose()
    PSE.EM.dispose()

    Initiator().initialize()

    Attributator().attributate()

    Localculator().localculate()

    ModelEntities.newSchedules()

    Divisionator().divisionate()

    RStockulator().makeNew()

    ModelEntities.addCarTypesToSpurs()
    
    print('New JMRI railroad built from TrainPlayer data')
    _psLog.info('New JMRI railroad built from TrainPlayer data')

    return

def updateJmriRailroad():
    """
    Mini controller to update JMRI railroad.
    Does not change Trains and Routes.
    Cars and engines are updated.
    Schedules are rewritten from scratch.
    Locations uses LM to update everything.
    Called by:
    Controller.StartUp.updateJmriRailroad
    """

    PSE.closeSubordinateWindows()
    PSE.remoteCalls('refreshCalls')
    
    BuiltTrainExport.FindTrain().trainResetter()

    Attributator().attributate()

    Localculator().localculate()

    ModelEntities.newSchedules()

    Divisionator().divisionate()

    ModelEntities.addCarTypesToSpurs()

    RStockulator().updater()

    print('JMRI railroad updated from TrainPlayer data')
    _psLog.info('JMRI railroad updated from TrainPlayer data')

    return

def updateJmriRollingingStock():
    """
    Mini controller to update only the rolling stock.
    Called by:
    Controller.Startup.updateJmriRollingingStock
    """

    PSE.closeSubordinateWindows()
    BuiltTrainExport.FindTrain().trainResetter()

    Attributator().attributate()

    RStockulator().updater()

    print('JMRI rolling stock updated')
    _psLog.info('JMRI rolling stock updated')

    return


class TpLocaleculator:
    """Makes the tpLocaleData.json file."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.TpLocaleculator'

        self.sourceData = {}
        self.tpLocaleData = {}

        self.locationList = []

        return

    def getTpRrData(self):

        self.sourceData = ModelEntities.getTpRailroadJson('tpRailroadData')

        return

    def getLocations(self):

        for id, data in self.sourceData['locales'].items():
            self.locationList.append(data['location'])

        self.locationList = list(set(self.locationList))

        return

    def makeLocationRubric(self):

        locationScratch = {}
        for location in self.locationList:
            idScratch = []
            for id, data in self.sourceData['locales'].items():
                if data['location'] == location:
                    idScratch.append(id)

            locationScratch[location] = idScratch

        self.tpLocaleData['locations'] = locationScratch

        return

    def makeTrackIdRubric(self):

        trackData = {}
        for id, data in self.sourceData['locales'].items():
            otherTrack = (data['location'], data['track'], data['type'])
            trackData[id] = otherTrack

        self.tpLocaleData['tracks'] = trackData

        return

    def exists(self):
        """Catches press of Update button before New button."""

        fileName = 'tpLocaleData.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        if PSE.JAVA_IO.File(targetPath).isFile():

            return True
        else:
            message = PSE.BUNDLE['Alert: Create a new JMRI layout first.']
            PSE.openOutputFrame(message)
            _psLog.critical('Alert: Create a new JMRI layout first.')

            return False

    def isValid(self):
        """
        Catch  all user errors here.
        Can't have staging and non-staging track types at the same location.
        """ 

        stagingLocations = []
        nonstagingLocations = []

        for id, trackData in self.tpLocaleData['tracks'].items():
            if trackData[2] == 'staging':
                stagingLocations.append(trackData[0])
            else:
                nonstagingLocations.append(trackData[0])

        result = list(set(stagingLocations) & set(nonstagingLocations))
        if len(result) == 0:
            _psLog.info('tpLocaleData file OK, no location/track conflicts')
            return True
        else:
            a = PSE.BUNDLE['ALERT: Staging and non-staging tracks at same location: '] + str(result)
            b = PSE.BUNDLE['JMRI does not allow staging and non-staging track types at the same location.']
            c = PSE.BUNDLE['No changes were made to your JMRI layout.']
            message = a + '\n' + b + '\n' + c + '\n'
            PSE.openOutputFrame(message)

            _psLog.critical('ALERT: Staging and non-staging tracks at same location: ' + str(result))

            return False

    def write(self):

        fileName = 'tpLocaleData.json'
        filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        PSE.genericWriteReport(filePath, PSE.dumpJson(self.tpLocaleData))

        return

    def make(self):
        """Mini controller"""

        self.getTpRrData()
        self.getLocations()
        self.makeLocationRubric()
        self.makeTrackIdRubric()

        print(self.scriptName + ' ' + str(SCRIPT_REV))
        _psLog.info('tpLocaleData.json created')

        return


class Initiator:
    """Make tweeks to Operations.xml here."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Initiator'

        self.OSU = PSE.JMRI.jmrit.operations.setup

        self.configFile =  PSE.readConfigFile()
        self.TpRailroad = ModelEntities.getTpRailroadJson('tpRailroadData')

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def initialize(self):
        """
        Mini controller to make settings changes,
        some of which are personal.
        """

        self.o2oDetailsToConFig()
        self.setRailroadDetails()
        self.tweakOperationsXml()
        self.setReportMessageFormat()

        _psLog.info('JMRI operations settings updated')

        return

    def o2oDetailsToConFig(self):
        """Optional railroad details from the TrainPlayer layout are added to the config file."""

        self.configFile['Main Script']['LD'].update({'OR':self.TpRailroad['operatingRoad']})
        self.configFile['Main Script']['LD'].update({'TR':self.TpRailroad['territory']})
        self.configFile['Main Script']['LD'].update({'LO':self.TpRailroad['location']})
        self.configFile['Main Script']['LD'].update({'YR':self.TpRailroad['year']})
        self.configFile['Main Script']['LD'].update({'SC':self.TpRailroad['scale']})
        self.configFile['Main Script']['LD'].update({'LN':self.TpRailroad['layoutName']})
        self.configFile['Main Script']['LD'].update({'BD':self.TpRailroad['buildDate']})
        self.configFile['Main Script']['LD'].update({'ML':PSE.JMRI.jmrit.operations.setup.Setup.getMaxTrainLength()})

        PSE.writeConfigFile(self.configFile)
        self.configFile =  PSE.readConfigFile()

        return

    def setRailroadDetails(self):
        """Optional railroad details from the TrainPlayer layout are added to JMRI."""

        _psLog.debug('setRailroadDetails')

    # Set the name
        layoutName = self.configFile['Main Script']['LD']['LN']

        self.OSU.Setup.setRailroadName(layoutName)
    # Set the year
        rrYear = self.configFile['Main Script']['LD']['YR']
        if rrYear:
            self.OSU.Setup.setYearModeled(rrYear)

        rrScale = self.configFile['Main Script']['LD']['SC']
        if rrScale:
            self.OSU.Setup.setScale(self.configFile['Main Script']['SR'][rrScale.upper()])

        return

    def tweakOperationsXml(self):
        """Some of these are just favorites of mine."""

        _psLog.debug('tweakOperationsXml')

        self.OSU.Setup.setMainMenuEnabled(self.configFile['Main Script']['TO']['SME'])
        self.OSU.Setup.setCloseWindowOnSaveEnabled(self.configFile['Main Script']['TO']['CWS'])
        self.OSU.Setup.setBuildAggressive(self.configFile['Main Script']['TO']['SBA'])
        self.OSU.Setup.setStagingTrackImmediatelyAvail(self.configFile['Main Script']['TO']['SIA'])
        self.OSU.Setup.setCarTypes(self.configFile['Main Script']['TO']['SCT'])
        self.OSU.Setup.setStagingTryNormalBuildEnabled(self.configFile['Main Script']['TO']['TNB'])
        self.OSU.Setup.setManifestEditorEnabled(self.configFile['Main Script']['TO']['SME'])

        return

    def setReportMessageFormat(self):
        """Sets the default message format as defined in the configFile."""

        self.OSU.Setup.setPickupManifestMessageFormat(self.configFile['o2o']['RMF']['PUC'])
        self.OSU.Setup.setDropManifestMessageFormat(self.configFile['o2o']['RMF']['SOC'])
        self.OSU.Setup.setLocalManifestMessageFormat(self.configFile['o2o']['RMF']['MC'])
        self.OSU.Setup.setPickupEngineMessageFormat(self.configFile['o2o']['RMF']['PUL'])
        self.OSU.Setup.setDropEngineMessageFormat(self.configFile['o2o']['RMF']['SOL'])

        return


class Attributator:
    """
    Sets all the rolling stock attributes.
    TCM - Temporary Context Manager.
    Nothing is removed from OperationsCarRoster.xml, only added to.
    """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Attributator'

        self.tpRailroadData = ModelEntities.getTpRailroadJson('tpRailroadData')

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def attributate(self):
        """Mini controller to add rolling stock attributes to the RS xml files."""

        self.addRoads()
        self.addCarAar()
        self.addCarLoads()
        self.addCarKernels()
        self.addLocoModels()
        self.addLocoTypes()
        self.addLocoConsist()

        _psLog.info('New rolling stock attributes')

        return

    def addRoads(self):
        """
        Add any new road name from the tpRailroadData.json file.
        Don't do this: newNames = list(set(self.tpRailroadData['roads']) - set(TCM.getNames()))
        Null lists cause the default list to be added.
        """

        _psLog.debug('addRoads')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarRoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        for xName in self.tpRailroadData['roads']:
            TCM.addName(xName)

        return

    def addCarAar(self):
        """Add any new type names using the aar names from the tpRailroadData.json file."""

        _psLog.debug('addCarAar')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarTypes
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        for xName in self.tpRailroadData['carAAR']:
            TCM.addName(xName)

        return

    def addCarLoads(self):
        """
        Add the loads and load types for each car type (TP AAR) in tpRailroadData.json.
        Empty is the only TP empty type.
        """

        _psLog.debug('addCarLoads')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarLoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        carLoads = self.tpRailroadData['carLoads']
        for aar in self.tpRailroadData['carAAR']:
            TCM.addType(aar)
            TCM.addName(aar, 'Empty')
            TCM.addName(aar, 'Load')
            TCM.setLoadType(aar, 'Empty', 'empty')
            TCM.setLoadType(aar, 'Load', 'load')

            for load in carLoads[aar]:
                TCM.addName(aar, load)
                TCM.setLoadType(aar, load, 'load')

        return

    def addCarKernels(self):
        """Add new kernels using those from tpRailroadData.json."""

        _psLog.debug('addCarKernels')

        for xName in self.tpRailroadData['carKernel']:
            PSE.KM.newKernel(xName)

        return

    def addLocoModels(self):
        """Add new engine models using the model names from the tpRailroadData.json file."""

        _psLog.debug('addLocoModels')

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineModels
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        for xName in self.tpRailroadData['locoModels']:
            xModel = xName[0]
            xType = xName[1]
            TCM.addName(xModel)
            TCM.setModelType(xModel, xType)
            TCM.setModelLength(xModel, '40')

        return

    def addLocoTypes(self):
        """Add new engine types using the type names from the tpRailroadData.json file."""

        _psLog.debug('addLocoTypes')

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineTypes
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        for xName in self.tpRailroadData['locoTypes']:
            TCM.addName(xName)

        return

    def addLocoConsist(self):
        """Add new JMRI consist names using the consist names from the tpRailroadData.json file."""

        _psLog.debug('addLocoConsist')

        for xName in self.tpRailroadData['locoConsists']:
            PSE.ZM.newConsist(xName)

        return


class Localculator:
    """Locations and tracks are updated using Location Manager."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Localculator'

        self.configFile = PSE.readConfigFile()
        self.tpRailroadData = ModelEntities.getTpRailroadJson('tpRailroadData')

        self.currentLocations = []
        self.importedLocations = []
        self.continuingLocations = []
        self.newLocations = []
        self.oldLocations = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def localculate(self):
        """Mini controller to update JMRL locations."""

        self.getCurrentLocations()
        self.getImportedLocations()
        self.parseLocations()
        self.updateContinuingLocations()
        self.addNewLocations()
        self.deleteOldLocations()

        _psLog.info('Locations created or updated')

        return

    def getCurrentLocations(self):

        for locationName in PSE.getAllLocationNames():
            location = PSE.LM.getLocationByName(locationName)
            allTracks = location.getTracksList()
            for track in allTracks:
                self.currentLocations.append(location.getName() + ';' + track.getName())

        return

    def getImportedLocations(self):

        for index, item in self.tpRailroadData['locales'].items():
            self.importedLocations.append(item['location'] + ';' + item['track'])

        return

    def parseLocations(self):

        self.continuingLocations = list(set(self.currentLocations).intersection(set(self.importedLocations)))
        self.newLocations = list(set(self.importedLocations) - set(self.currentLocations))
        self.oldLocations = list(set(self.currentLocations) - set(self.importedLocations))

        return

    def updateContinuingLocations(self):
        """The only attribs that are updated are Length, Type and Schedule."""

        oldMaxLength = self.configFile['Main Script']['LD']['ML']
        newMaxLength = PSE.JMRI.jmrit.operations.setup.Setup.getMaxTrainLength()

        for location in self.continuingLocations:
            lt = location.split(';')
            locationName = lt[0]
            trackName = lt[1]
            length = 0
            type = ''
            for index, trackData in self.tpRailroadData['locales'].items():
                if trackData['location'] == locationName and trackData['track'] == trackName:
                    length = self.configFile['o2o']['DL'] * int(trackData['capacity'])
                    type = self.configFile['o2o']['TR'][trackData['type']]
                    label = trackData['label']

            track = PSE.LM.getLocationByName(locationName).getTrackByName(trackName, None)
            track.setTrackType(type)
            if track.getLength() == oldMaxLength:
                track.setLength(newMaxLength)
            
            if track.getTrackType() == 'Spur':
                track.setLength(length)
                newSchedule = PSE.SM.getScheduleByName(label)
                track.setSchedule(newSchedule)
                # PSE.LM.getLocationByName(locationName).firePropertyChange(track.SCHEDULE_ID_CHANGED_PROPERTY, None, newSchedule.getId())

        self.configFile['Main Script']['LD'].update({'DT':newMaxLength})
        PSE.writeConfigFile(self.configFile)
        self.configFile =  PSE.readConfigFile()

        return

    def addNewLocations(self):

        maxTrackLength = self.configFile['Main Script']['LD']['DT']

        for location in self.newLocations:
            lt = location.split(';')
            locationName = lt[0]
            trackName = lt[1]
            length = 0
            type = ''
            for index, trackData in self.tpRailroadData['locales'].items():
                length = (self.configFile['o2o']['DL'] + 4) * int(trackData['capacity'])
                if length == 0:
                    length = maxTrackLength

                if trackData['location'] == locationName and trackData['track'] == trackName:
                    type = self.configFile['o2o']['TR'][trackData['type']]
                    location = PSE.LM.newLocation(locationName)
                    track = location.addTrack(trackName, type)
                    track.setLength(length)

                    ModelEntities.setTrackAttribs(trackData)

        return

    def deleteOldLocations(self):

        for location in self.oldLocations:
            lt = location.split(';')
            locationName = lt[0]
            trackName = lt[1]
            location = PSE.LM.getLocationByName(locationName)
            location.deleteTrack(location.getTrackByName(trackName, None))

        for location in self.oldLocations:
            lt = location.split(';')
            locationName = lt[0]
            marker = 0
            for index, item in self.tpRailroadData['locales'].items():
                if item['location'] == locationName:
                    marker += 1

            if marker == 0:
                PSE.LM.deregister(PSE.LM.getLocationByNme(locationName))

        return


class Divisionator:
    """All methods involving divisions."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Divisionator'
        self.tpRailroadData = ModelEntities.getTpRailroadJson('tpRailroadData')

        self.tpDivisions = self.tpRailroadData['divisions'] # List of strings
        self.jmriDivisions = [] # list of strings
        for division in PSE.DM.getList():
            self.jmriDivisions.append(division.getName())

        self.newDivisions = []
        self.obsoleteDivisions = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def divisionate(self):
        """Mini controller to process divisions."""

        self.parseDivisions()
        self.removeObsoleteDivisions()
        self.addNewDivisions()
        self.addDivisionToLocations()
        self.addDivisionToLocations()
        self.addUnreportedToUnknown()

        _psLog.info('Divisions updated')

        return

    def parseDivisions(self):

        self.newDivisions = list(set(self.tpDivisions) - set(self.jmriDivisions))
        self.obsoleteDivisions = list(set(self.jmriDivisions) - set(self.tpDivisions))

        return

    def removeObsoleteDivisions(self):

        if len(self.obsoleteDivisions) == 0:
            return

        for division in self.obsoleteDivisions:
            obsolete = PSE.DM.getDivisionByName(division)
            PSE.DM.deregister(obsolete)

        return

    def addNewDivisions(self):

        for division in self.newDivisions:
            PSE.DM.newDivision(division)

        return

    def addDivisionToLocations(self):
        """Edge case, if there is only one division, add all locations to it."""

        if PSE.DM.getNumberOfdivisions() != 1:
            return

        division = PSE.DM.getList()[0]

        for location in PSE.LM.getList():
            location.setDivision(division)
                
        return

    def addUnreportedToUnknown(self):
        """
        This method adds a division named Unknown.
        Add the location named Unreported to the division named Unknown.
        """

        location = PSE.LM.getLocationByName('Unreported')
        division = PSE.DM.newDivision(PSE.BUNDLE['Unknown'])

        location.setDivision(division)

        return


class RStockulator:
    """All methods concerning rolling stock."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.RStockulator'

        self.configFile = PSE.readConfigFile('o2o')
        self.jmriCars = PSE.CM.getList()
        self.jmriLocos = PSE.EM.getList()

        self.tpRollingStockFileName = self.configFile['RF']['TRR']

        self.tpInventory = []
        self.tpCars = {}
        self.tpLocos = {}

        self.currentRsData = {}
        self.newRsData = {}

        self.newTpIds = []
        self.oldTpIds = []
        self.continuingTpIds = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def makeNew(self):
        """Mini controller to make new rosters of JMRI rolling stock."""

        self.makeNewTpRollingStockData()
        self.parseTpRollingStock()
        self.newJmriRs()

        _psLog.info('New rolling stock')

        return

    def updater(self):
        """Mini controller to update JMRI rolling stock."""

        if not self.checkFile():
            return

        self.getcurrentTpRsData()
        self.makeNewTpRollingStockData()
        self.parseTpRollingStock()
        self.updateJmriRs()
        self.deregisterOldRs()
        self.newJmriRs()

        _psLog.info('Updated rolling stock')

        return

    def checkFile(self):

        fileName = 'tpRollingStockData.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        if PSE.JAVA_IO.File(targetPath).isFile():

            return True
        else:
            message = PSE.BUNDLE['Alert: Create a new JMRI layout first.']
            PSE.openOutputFrame(message)
            _psLog.critical('Alert: Create a new JMRI layout first.')

            return False

    def getcurrentTpRsData(self):

        fileName = 'tpRollingStockData.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        self.currentRsData = PSE.loadJson(PSE.genericReadReport(targetPath))

        return

    def makeNewTpRollingStockData(self):
        """Makes a json LUT: TP road + TP Number : TP ID"""

        _psLog.debug('makeNewTpRollingStockData')

        self.getTpInventory()
        self.splitTpList()

        for item in self.tpInventory:
            try:
                line = item.split(';')
                name, number = ModelEntities.parseCarId(line[0])
                self.newRsData[line[7]] = name + number
            except:
                _psLog.warning('Line not parsed: ' + item)
                pass

        fileName = 'tpRollingStockData.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        formattedRsFile = PSE.dumpJson(self.newRsData)
        PSE.genericWriteReport(targetPath, formattedRsFile)

        return

    def getTpInventory(self):

        try:
            self.tpInventory = ModelEntities.getTpExport(self.tpRollingStockFileName)
            self.tpInventory.pop(0) # Remove the date
            self.tpInventory.pop(0) # Remove the key
            _psLog.info('TrainPlayer Inventory file OK')
        except:
            _psLog.warning('TrainPlayer Inventory file not found')

        return

    def splitTpList(self):
        """
        self.tpInventory string format:
        TP Car ; TP Type ; TP AAR; JMRI Location; JMRI Track; TP Load; TP Kernel, TP ID
        TP Loco; TP Model; TP AAR; JMRI Location; JMRI Track; TP Load; TP Consist, TP ID

        self.tpCars  dictionary format: {TP ID :  {type: TP Collection, aar: TP AAR, location: JMRI Location, track: JMRI Track, load: TP Load, kernel: TP Kernel, id: JMRI ID}}
        self.tpLocos dictionary format: {TP ID :  [Model, AAR, JMRI Location, JMRI Track, 'unloadable', Consist, JMRI ID]}
        """

        _psLog.debug('splitTpList')

        for item in self.tpInventory:
            line = item.split(';')
            if line[2].startswith('ET'):
                continue
            if line[2].startswith('E'):
                # self.tpLocos[line[0].replace(" ", "")] = {'model': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'consist': line[6]}
                self.tpLocos[line[7]] = {'model': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'consist': line[6], 'id': line[0]}
            else:
                # self.tpCars[line[0].replace(" ", "")] = {'type': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'kernel': line[6]}
                self.tpCars[line[7]] = {'type': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'kernel': line[6], 'id': line[0]}

        return

    def parseTpRollingStock(self):
        """Makes 3 lists, continnuing, new and old rolling stock."""

        currentRsIds = []
        for id in self.currentRsData:
            currentRsIds.append(id)

        newRsIds = []
        for id in self.newRsData:
            newRsIds.append(id)

        self.continuingTpIds = list(set(currentRsIds).intersection(set(newRsIds)))
        self.newTpIds = list(set(newRsIds) - (set(currentRsIds)))
        self.oldTpIds = list(set(currentRsIds) - (set(newRsIds)))

        return

    def newJmriRs(self):

        for id in self.newTpIds:
            newJmriId = self.newRsData[id]
            rsRoad, rsNumber = ModelEntities.parseCarId(newJmriId)

            try:
                self.tpCars[id]['aar']
                PSE.CM.newRS(rsRoad, rsNumber)
            except:
                pass

            try:
                self.tpLocos[id]['aar']
                PSE.EM.newRS(rsRoad, rsNumber)
            except:
                pass

        self.currentRsData = self.newRsData
        self.setGenericRsAttribs(self.newTpIds)
        self.setSpecificRsAttribs(self.newTpIds)

        return

    def updateJmriRs(self):

        self.setGenericRsAttribs(self.continuingTpIds)

        return

    def setGenericRsAttribs(self, idList):
        """
        Used when updating rolling stock.
        Sets only the road name, number, kernal/consist, location, track and load.
        """

        _psLog.debug('setGenericRsAttribs')

        for id in idList:
            currentJmriId = self.currentRsData[id]
            if PSE.EM.getById(currentJmriId):
                newRsAttribs = self.tpLocos[id]
                rs = PSE.EM.getById(currentJmriId)
                
                rs.setConsist(PSE.ZM.getConsistByName(newRsAttribs['consist']))

            elif PSE.CM.getById(currentJmriId):
                newRsAttribs = self.tpCars[id]
                rs = PSE.CM.getById(currentJmriId)
                shipLoadName, destination = self.getLoadFromSchedule(newRsAttribs)
                if shipLoadName:
                    rs.setLoadName(shipLoadName)
                if destination:
                    rs.setFinalDestination(destination)
                rs.setKernel(PSE.KM.getKernelByName(newRsAttribs['kernel']))

            rsRoad, rsNumber = ModelEntities.parseCarId(newRsAttribs['id'])
            xLocation, xTrack = ModelEntities.getSetToLocationAndTrack(newRsAttribs['location'], newRsAttribs['track'])

            oldRoad = rs.getRoadName()
            rs.setRoadName(rsRoad)
            rs.firePropertyChange("rolling stock road", oldRoad, rsRoad)

            oldNumber = rs.getNumber()
            rs.setNumber(rsNumber)
            rs.firePropertyChange("rolling stock number", oldNumber, rsNumber)

            # oldTrack = rs.getTrack()
            rs.setLocation(xLocation, xTrack, True)
            # rs.firePropertyChange(TRACK_CHANGED_PROPERTY, oldTrack, xTrack)

            rs.setTypeName(newRsAttribs['aar'])

        return

    def setSpecificRsAttribs(self, idList):
        """
        Used when adding new rolling stock.
        TP ID  : {'kernel': u'', 'type': u'box x23 prr', 'aar': u'XM', 'load': u'Empty', 'location': u'City', 'track': u'701'}
        """

        _psLog.debug('setSpecificRsAttribs')

        for id in idList:
            currentJmriId = self.currentRsData[id]
            if PSE.EM.getById(currentJmriId):
                newRsAttribs = self.tpLocos[id]
                newLoco = PSE.EM.getById(currentJmriId)
                newLoco.setLength(str(self.configFile['DL']))
                newLoco.setModel(newRsAttribs['model'][0:11])
            # Setting the model will automatically set the type
                newLoco.setWeight('2')
                newLoco.setColor('Black')
                newLoco.setConsist(PSE.ZM.getConsistByName(newRsAttribs['consist']))

            elif PSE.CM.getById(currentJmriId):
                newRsAttribs = self.tpCars[id]
                newCar = PSE.CM.getById(currentJmriId)
                if newRsAttribs['aar'] in self.configFile['CX']:
                    newCar.setCaboose(True)
                if newRsAttribs['aar'] in self.configFile['PX']:
                    newCar.setPassenger(True)
                newCar.setLength(str(self.configFile['DL']))
                newCar.setWeight('2')
                newCar.setColor('Red')

            else:
                print('Exclude rolling stock: ' + currentJmriId)

        return

    def getLoadFromSchedule(self, attribs):

        location = PSE.LM.getLocationByName(attribs['location'])
        track = location.getTrackByName(attribs['track'], None)

        if location.isStaging():
            return 'E', None

        try:
            jSchedule = track.getSchedule()
            jItem = jSchedule.getItemByType(attribs['aar'])
            return jItem.getShipLoadName(), jItem.getDestination()
            
        except:
             return None, None

    def deregisterOldRs(self):

        for id in self.oldTpIds:
            disposeJmriId = self.currentRsData[id]
            try:
                PSE.EM.deregister(PSE.EM.getById(disposeJmriId))
            except:
                PSE.CM.deregister(PSE.CM.getById(disposeJmriId))            

        return

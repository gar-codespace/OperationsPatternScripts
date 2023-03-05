# coding=utf-8
# © 2023 Greg Ritacco

"""From tpRailroadData.json, a new JMRI railroad is created or updated."""

from opsEntities import PSE
from Subroutines.o2o import ModelImport
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

def getTrainPlayerRailroad():

    if ModelImport.importTpRailroad():
        print('TrainPlayer railroad data imported OK')
        _psLog.info('TrainPlayer railroad data imported OK')
        PSE.closeOutputFrame()
        PSE.closeSubordinateWindows()
        BuiltTrainExport.FindTrain().trainResetter()

        return True

    else:
        print('TrainPlayer railroad not imported')
        _psLog.critical('TrainPlayer railroad not imported')
        _psLog.critical('JMRI railroad not updated')

        return False


def newJmriRailroad():
    """
    Mini controller to make a new JMRI railroad.
    tpRailroadData.json and TrainPlayer Report - Rolling Stock.txt
    are used as source files.
    Called by:
    Controller.StartUp.newJmriRailroad
    """

    PSE.TMX.makeBackupFile('operations/OperationsTrainRoster.xml')
    PSE.TMX.makeBackupFile('operations/OperationsRouteRoster.xml')

    PSE.TM.dispose()
    PSE.RM.dispose()
    PSE.DM.dispose()
    PSE.SM.dispose()
    PSE.LM.dispose()
    PSE.CM.dispose()
    PSE.EM.dispose()

    Initiator().initialize()
    Attributator().attributate()
    ModelEntities.rebuildSchedules()
    Locationator().creater()
    Divisionator().divisionate()
    ModelEntities.addCarTypesToSpurs()
    RStockulator().makeNew()
    
    print('New JMRI railroad built from TrainPlayer data')
    _psLog.info('New JMRI railroad built from TrainPlayer data')

    return

def updateJmriLocations():
    """
    Mini controller.
    Applies changes made to the TrainPlayer/OC/Locations tab.
    Does not change Trains and Routes.
    Schedules are rewritten from scratch.
    Locations uses LM to update everything.
    Rolling stock is not updated.
    Called by:
    Controller.StartUp.updateJmriLocations
    """
    
    Attributator().attributate()
    ModelEntities.rebuildSchedules()
    Locationator().updater()
    Divisionator().divisionate()
    ModelEntities.addCarTypesToSpurs()
    RStockulator().updater()

    print('JMRI locations updated from TrainPlayer data')
    _psLog.info('JMRI locations updated from TrainPlayer data')

    return

def updateJmriIndustries():
    """
    Mini controller.
    Applies changes made to the TrainPlayer/OC/Industries tab.
    Rolling stock is not updated.
    Locations are otherwise not changed.
    Called by:
    Controller.Startup.updateJmriIndustries
    """
    
    Attributator().attributate()
    ModelEntities.rebuildSchedules()
    ModelEntities.addCarTypesToSpurs()

    print('JMRI industries updated from TrainPlayer data')
    _psLog.info('JMRI industries updated from TrainPlayer data')

    return

def updateJmriRollingingStock():
    """
    Mini controller.
    Applies changes made to TrainPlayer rolling stock.
    Called by:
    Controller.Startup.updateJmriRollingingStock
    """

    Attributator().attributate()
    RStockulator().updater()

    print('JMRI rolling stock updated from TrainPlayer data')
    _psLog.info('JMRI rolling stock updated from TrainPlayer data')

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

        self.deleteDataJson()
        self.o2oDetailsToConFig()
        self.setRailroadDetails()
        self.tweakOperationsXml()
        self.setReportMessageFormat()

        _psLog.info('JMRI operations settings updated')

        return
    
    def deleteDataJson(self):

        listOfFiles = ['jmriRailroadData', 'tpLocaleData', 'tpRollingStockData']
        for file in listOfFiles:
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', file + '.json')
            if PSE.JAVA_IO.File(targetFile).isFile():
                PSE.JAVA_IO.File(targetFile).delete()

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


class Locationator:
    """Locations and tracks are updated using Location Manager."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Locationator'

        self.configFile = PSE.readConfigFile()
        self.currentIds = []
        self.updatedIds = []

        self.currentRrData = {}
        self.updatedRrData = {}
        self.continuingIds = []
        self.newIds = []
        self.oldIds = []
        self.emptyLocations = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return
    
    def updater(self):
        """
        Mini controller.
        Updates JMRI locations.
        """

        self.getCurrentRrData()
        self.getUpdatedRrData()
        self.parseLocationIds()
        self.updateContinuingLocations()
        self.removeOldTracks()
        self.getEmptyLocations()
        self.removeEmptyLocations()
        self.makeNewLocations()
        self.makeJmriData()

        return
    
    def creater(self):
        """
        Mini controller.
        Makes new JMRI locations.
        """

        self.getUpdatedRrData()
        self.newmakeNewIds()
        self.makeNewLocations()
        self.makeJmriData()

        return
    
    def getCurrentRrData(self):

        self.currentRrData = ModelEntities.getTpRailroadJson('jmriRailroadData')

        return

    def getUpdatedRrData(self):

        self.updatedRrData = ModelEntities.getTpRailroadJson('tpRailroadData')

        return
    
    def newmakeNewIds(self):

        self.newIds = self.updatedRrData['locationIds']

    def parseLocationIds(self):

        self.currentIds = self.currentRrData['locationIds']
        self.updatedIds = self.updatedRrData['locationIds']

        self.newIds = list(set(self.updatedIds).difference(set(self.currentIds)))
        self.oldIds = list(set(self.currentIds).difference(set(self.updatedIds)))
        self.continuingIds = list(set(self.currentIds) - set(self.oldIds))



        return
    
    def updateContinuingLocations(self):

        for id in self.continuingIds:

            trackType = self.configFile['o2o']['TR'][self.updatedRrData['locales'][id]['type']]
            spurLength = (self.configFile['o2o']['DL'] + 4) * int(self.updatedRrData['locales'][id]['capacity'])
            currentLocation = PSE.LM.getLocationByName(self.currentRrData['locales'][id]['location'])
            updatedLocation = PSE.LM.newLocation(self.updatedRrData['locales'][id]['location'])

            try:
                track = updatedLocation.getTrackByName(self.currentRrData['locales'][id]['track'], None)
                track.setName(self.updatedRrData['locales'][id]['track'])
                track.setTrackType(trackType)
            except:
                track = currentLocation.getTrackByName(self.currentRrData['locales'][id]['track'], None)
                track.copyTrack(self.updatedRrData['locales'][id]['track'], updatedLocation)
                currentLocation.deleteTrack(track)
                
            self.updatedRrData['locales'][id]['spurLength'] = spurLength
            self.updatedRrData['locales'][id]['defaultLength'] = PSE.JMRI.jmrit.operations.setup.Setup.getMaxTrainLength()
            ModelEntities.setTrackAttribs(self.updatedRrData['locales'][id])
            # print(self.updatedRrData['locales'][id])

            # if trackType == 'Spur':
            #     track.setLength(length)
            
        return

    def makeNewLocations(self):

        for id in self.newIds:

            trackData = self.updatedRrData['locales'][id]
            spurLength = (self.configFile['o2o']['DL'] + 4) * int(trackData['capacity'])
            trackType = self.configFile['o2o']['TR'][trackData['type']]

            location = PSE.LM.newLocation(trackData['location'])
            location.addTrack(trackData['track'], trackType)

            trackData['spurLength'] = spurLength
            trackData['defaultLength'] = PSE.JMRI.jmrit.operations.setup.Setup.getMaxTrainLength()

            # ModelEntities.setTrackAttribs(self.updatedRrData['locales'][id])
            ModelEntities.setTrackAttribs(trackData)

        return

    def removeOldTracks(self):

        for id in self.oldIds:

            currentLocation = PSE.LM.getLocationByName(self.currentRrData['locales'][id]['location'])
            currentLocation.deleteTrack(currentLocation.getTrackByName(self.currentRrData['locales'][id]['track'], None))

        return

    def getEmptyLocations(self):

        for location in PSE.getAllLocationNames():
            if len(PSE.LM.getLocationByName(location).getTracksList()) == 0:
                self.emptyLocations.append(location)

        return
    
    def removeEmptyLocations(self):

        for emptyLocation in self.emptyLocations:
            PSE.LM.deregister(PSE.LM.getLocationByName(emptyLocation))

        return
    
    def makeJmriData(self):

        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'tpRailroadData.json')
        copyFrom = PSE.JAVA_IO.File(targetFile).toPath()

        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jmriRailroadData.json')
        copyTo = PSE.JAVA_IO.File(targetFile).toPath()

        PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)

        return


class Divisionator:
    """All methods involving divisions."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Divisionator'
        # self.tpRailroadData = ModelEntities.getTpRailroadJson('tpRailroadData')

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
        self.addUnreportedToUnknown()

        _psLog.info('Divisions updated')

        return

    def parseDivisions(self):

        updateDivisions = ModelEntities.getTpRailroadJson('tpRailroadData')['divisions']
        currentDivisions = [division.getName() for division in PSE.DM.getList()]

        self.newDivisions = list(set(updateDivisions) - set(currentDivisions))
        self.obsoleteDivisions = list(set(currentDivisions) - set(updateDivisions))

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
        division = PSE.DM.newDivision('Unknown')

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
        """Checks the validity of tpRollingStockData.json"""

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
                self.tpLocos[line[7]] = {'model': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'consist': line[6], 'id': line[0]}
            else:
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

            # oldRoad = rs.getRoadName()
            rs.setRoadName(rsRoad)
            # rs.firePropertyChange("rolling stock road", oldRoad, rsRoad)

            oldNumber = rs.getNumber()
            rs.setNumber(rsNumber)
            rs.firePropertyChange("rolling stock number", oldNumber, rsNumber)

            # # oldTrack = rs.getTrack()
            rs.setLocation(xLocation, xTrack, True)
            # # rs.firePropertyChange(TRACK_CHANGED_PROPERTY, oldTrack, xTrack)

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

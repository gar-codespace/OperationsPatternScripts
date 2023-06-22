# coding=utf-8
# © 2023 Greg Ritacco

"""From tpRailroadData.json, a new JMRI railroad is created or updated."""

from opsEntities import PSE
from Subroutines.o2o import ModelImport
from Subroutines.o2o import ModelEntities
from Subroutines.o2o import BuiltTrainExport

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.o2o.Model')


def getTrainPlayerRailroad():

    if ModelImport.importTpRailroad():
        print('TrainPlayer railroad data imported OK')
        _psLog.info('TrainPlayer railroad data imported OK')
        PSE.closeOutputFrame()
        BuiltTrainExport.FindTrain().trainResetter()

        return True

    else:
        print('TrainPlayer railroad not imported')
        _psLog.critical('TrainPlayer railroad not imported')
        _psLog.critical('JMRI railroad not updated')

        return False


def initializeJmriRailroad():
    """
    Mini controller to initialize a JMRI railroad for TrainPlayer import.
    Does not change Trains and Routes.
    Called by:
    Controller.StartUp.initializeJmriRailroad
    """

    PSE.DM.dispose()
    PSE.SM.dispose()
    PSE.LM.dispose()
    PSE.CM.dispose()
    PSE.EM.dispose()
    
    print('JMRI data has been initiallized')
    _psLog.info('JMRI data has been initiallized')

    return

def updateJmriLocations():
    """
    Mini controller.
    Applies changes made to the TrainPlayer/OC/Locations, Industries, and Cars tabs.
    Does not change Trains and Routes.
    Schedules are rewritten from scratch.
    Locations uses LM to update everything.
    Called by:
    Controller.StartUp.updateJmriLocations
    """

# This part does the locations    
    Initiator().incrementor()
    Attributator().attributist()
    Locationator().locationist()
    Divisionator().divisionist()
    print('JMRI locations updated from TrainPlayer data')
    _psLog.info('JMRI locations updated from TrainPlayer data')

# This part does the tracks
    ScheduleAuteur().auteurist()
    Trackulator().trackist()
    print('JMRI tracks updated from TrainPlayer data')
    _psLog.info('JMRI tracks updated from TrainPlayer data')

# This part does the rolling stock
    RStockulator().updator()
    RStockulator().scheduleApplicator()
    print('JMRI rolling stock updated from TrainPlayer data')
    _psLog.info('JMRI rolling stock updated from TrainPlayer data')

    return

def updateJmriTracks():
    """
    Mini controller.
    Uses LM to update tracks and track attributes.
    Also updates rolling stock.
    Called by:
    Controller.Startup.updateJmriTracks
    """
    
    if not PSE.getAllLocationNames():
        message = PSE.BUNDLE['Alert: No JMRI locations were found.']
        PSE.openOutputFrame(message)        
        return

    Attributator().attributist()
    ScheduleAuteur().auteurist()
    Trackulator().trackist()
    print('JMRI tracks updated from TrainPlayer data')
    _psLog.info('JMRI tracks updated from TrainPlayer data')

# This part does the rolling stock
    RStockulator().updator()
    RStockulator().scheduleApplicator()
    print('JMRI rolling stock updated from TrainPlayer data')
    _psLog.info('JMRI rolling stock updated from TrainPlayer data')
    return

def updateJmriRollingingStock():
    """
    Mini controller.
    Applies changes made to TrainPlayer rolling stock.
    Loads cars at spurs per schedule.
    Sets cars load at staging to E.
    Called by:
    Controller.Startup.updateJmriRollingingStock
    """

    if not PSE.getAllTracks():
        message = PSE.BUNDLE['Alert: No JMRI tracks were found.']
        PSE.openOutputFrame(message)
        return

    Attributator().attributist()
    RStockulator().updator()
    RStockulator().scheduleApplicator()
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

    def initialist(self):
        """
        Mini controller to make settings changes,
        some of which are personal.
        """

        self.deleteDataJson()
        self.o2oDetailsToConFig()
        self.setRailroadDetails()
        self.tweakOperationsXml()
        self.setReportMessageFormat()

        _psLog.info('Layout details added')
        _psLog.info('JMRI operations settings updated')

        return
    
    def incrementor(self):
        """
        Mini controller to update railroad details.
        """

        self.o2oDetailsToConFig()
        self.setRailroadDetails()

        _psLog.info('Layout details updated')

        return
    
    def deleteDataJson(self):

        listOfFiles = ['jmriRailroadData', 'tpLocaleData', 'tpRollingStockData']
        for file in listOfFiles:
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', file + '.json')
            if PSE.JAVA_IO.File(targetFile).isFile():
                PSE.JAVA_IO.File(targetFile).delete()

        return

    def o2oDetailsToConFig(self):
        """
        Optional railroad details from the TrainPlayer layout are added to the config file.
        """

        self.configFile['Main Script']['LD'].update({'OR':self.TpRailroad['operatingRoad']})
        self.configFile['Main Script']['LD'].update({'TR':self.TpRailroad['territory']})
        self.configFile['Main Script']['LD'].update({'LO':self.TpRailroad['location']})
        self.configFile['Main Script']['LD'].update({'YR':self.TpRailroad['year']})
        self.configFile['Main Script']['LD'].update({'SC':self.TpRailroad['scale']})
        self.configFile['Main Script']['LD'].update({'BD':self.TpRailroad['buildDate']})

        PSE.writeConfigFile(self.configFile)
        self.configFile =  PSE.readConfigFile()

        return

    def setRailroadDetails(self):
        """
        Optional railroad details from the TrainPlayer layout are added to JMRI.
        """

        _psLog.debug('setRailroadDetails')

    # Set the name
        self.OSU.Setup.setRailroadName(self.TpRailroad['layoutName'])
    # Set the year
        rrYear = self.configFile['Main Script']['LD']['YR']
        if rrYear:
            self.OSU.Setup.setYearModeled(rrYear)

        rrScale = self.configFile['Main Script']['LD']['SC']
        if rrScale:
            self.OSU.Setup.setScale(self.configFile['Main Script']['SR'][rrScale.upper()])

        PSE.JMRI.jmrit.operations.setup.OperationsSettingsPanel().savePreferences()

        return

    def tweakOperationsXml(self):
        """
        Some of these are just favorites of mine.
        """

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
        """
        Sets the default message format as defined in the configFile.
        """

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

    def attributist(self):
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
    
    def disposal(self):
        """Runs when Initialize JMRI Railroad is selected"""

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarRoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        TCM.dispose()

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarTypes
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        TCM.dispose()

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarLoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        TCM.dispose()

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineModels
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        TCM.dispose()

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineTypes
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        TCM.dispose()

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
        """
        Add any new type names using the aar names from the tpRailroadData.json file.
        """

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
        """
        Add new kernels using those from tpRailroadData.json.
        """

        _psLog.debug('addCarKernels')

        for xName in self.tpRailroadData['carKernel']:
            PSE.KM.newKernel(xName)

        return

    def addLocoModels(self):
        """
        Add new engine models using the model names from the tpRailroadData.json file.
        """

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
        """
        Add new engine types using the type names from the tpRailroadData.json file.
        """

        _psLog.debug('addLocoTypes')

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineTypes
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        
        for xName in self.tpRailroadData['locoTypes']:
            TCM.addName(xName)

        return

    def addLocoConsist(self):
        """
        Add new JMRI consist names using the consist names from the tpRailroadData.json file.
        """

        _psLog.debug('addLocoConsist')

        for xName in self.tpRailroadData['locoConsists']:
            PSE.ZM.newConsist(xName)

        return


class ScheduleAuteur:
    """
    Everything to do with schedules.
    """

    def __init__(self):

        self.tpIndustries = ModelEntities.getTpRailroadJson('tpRailroadData')['industries']
        self.allSchedules = []
        self.scheduleItems = []
        self.composedItems = []

        return
    
    def auteurist(self):
        """
        Mini controller.
        """

        self.disposeSchedules()
        self.addSchedules()

        return
    
    def disposeSchedules(self):

        PSE.SM.dispose()

        return
    
    def addSchedules(self):
        """
        TrainPlayer Staging is mapped to JMRI Destination.
        TrainPlayer ViaIn is mapped to JMRI Road.
        ViaOut is not currently used.
        """

        _psLog.debug('addSchedules')

        for _, industry in self.tpIndustries.items():
            scheduleForIndustry = industry['c-schedule']
            for scheduleName, self.scheduleItems in scheduleForIndustry.items():
                
                schedule = PSE.SM.newSchedule(scheduleName)
                self.composeSchedule()

                for item in self.composedItems:
                    scheduleItem = schedule.addItem(item[0])
                    scheduleItem.setReceiveLoadName(item[1])
                    scheduleItem.setShipLoadName(item[2])
                    scheduleItem.setDestination(PSE.LM.getLocationByName(item[3]))
                    scheduleItem.setRoadName(item[4])
                    # scheduleItem.useViaOutForSomething(item[5])

        return
    
    def composeSchedule(self):
        """
        Mini controller.
        When a match is found, the current and match items are removed from scheduleItems,
        and processed and added to composedItems.       
        scheduleItem format = (aarName, sr, loadName, stagingName, viaIn, viaOut)
        Lists are immutable while iterating.
        """

        _psLog.debug('composeSchedule')

        self.composedItems = []
        self.symetric() # First - find same aar, S/R same load name.
        self.asymetric() # Second - find same aar, S/R different load name.
        self.mono() # Third - everything left is a single node.

        if len(self.scheduleItems) != 0:
            _psLog.warning('Some schedule items were not applied.')
            print('Some schedule items were not applied.')

        return
    
    def symetric(self):
        """Same aar, ship/receive the same load."""

        indexLength = len(self.scheduleItems) - 1
        if indexLength == 0:
            return

        for _ in range(indexLength): # scheduleItems is iterated by proxy.
            currentItem = self.scheduleItems.pop(0)
            match = False
            for i in range(len(self.scheduleItems)):
                testItem = self.scheduleItems[i]
                if currentItem[0] == testItem[0] and currentItem[1] != testItem[1] and currentItem[2] == testItem[2]:
                    self.composedItems.append(self.symetricDoubleNode(currentItem, testItem))
                    match = True
                    break

            if match:
                self.scheduleItems.pop(i)
            else:
                self.scheduleItems.append(currentItem)

            if len(self.scheduleItems) < 2:
                break

        return

    def asymetric(self):
        """Same aar, ship/receive different load."""

        indexLength = len(self.scheduleItems) - 1
        if indexLength == 0:
            return

        for _ in range(indexLength): # scheduleItems is iterated by proxy.
            currentItem = self.scheduleItems.pop(0)
            match = False
            # i = 0
            for i in range(len(self.scheduleItems)):
                testItem = self.scheduleItems[i]
                if currentItem[0] == testItem[0] and currentItem[1] != testItem[1] and currentItem[2] != testItem[2]:
                    self.composedItems.append(self.asymetricDoubleNode(currentItem, testItem))
                    match = True
                    break

            if match:
                self.scheduleItems.pop(i)
            else:
                self.scheduleItems.append(currentItem)

            if len(self.scheduleItems) < 2:
                break

        return

    def mono(self):
        """
        For each aar, either an S or an R, but not both.
        """

        indexLength = len(self.scheduleItems)
        if indexLength == 0:
            return
        
        for z in range(indexLength):
            currentItem = self.scheduleItems.pop(0)
            self.composedItems.append(self.singleNode(currentItem))

        return

    def symetricDoubleNode(self, node1, node2):
        """
        For each AAR with a ship and recieve.
        S/R the same load name.
        """

        composedNode = []
        if node1[3]:
            fd = node1[3]
        else:
            fd = node2[3]

        composedNode = [node1[0], node1[2], node2[2], fd, node1[4], node1[5]]

        return composedNode

    def asymetricDoubleNode(self, node1, node2):
        """
        For each AAR with a ship and recieve.
        S/R are different load names.
        scheduleItem = (aarName, sr, loadName, stagingName, viaIn, viaOut)
        """

        composedNode = []
        if node1[3]:
            fd = node1[3]
        else:
            fd = node2[3]

        if node1[1] == 'R':
            composedNode = [node1[0], node1[2], node2[2], fd, node1[4], node1[5]]
        else:
            composedNode = [node1[0], node2[2], node1[2], fd, node1[4], node1[5]]

        return composedNode
    
    def singleNode(self, node):
        """
        For each AAR when either the ship or recieve is an empty.
        """

        if node[2] == 'empty':
            node[2] = 'Empty'

        composedNode = []
        if node[1] == 'R':
            composedNode = [node[0], node[2], 'Empty', node[3], node[4], node[5]]
        else:
            composedNode = [node[0], 'Empty', node[2], node[3], node[4], node[5]]

        return composedNode
    

class Locationator:
    """
    Locations are updated using Location Manager.
    """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Locationator'

        self.configFile = PSE.readConfigFile()

        self.currentRrData = {}
        self.updatedRrData = {}

        self.continuingLocations = []
        self.newLocations = []
        self.oldLocations = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return
    
    def locationist(self):
        """
        Mini controller.
        Updates new or continuing locations and delets obsolete locations.
        """

        self.getCurrentRrData()
        self.getUpdatedRrData()
        self.parseLocations()
        self.addNewLocations()
        self.deleteOldLocations()

        PSE.LMX.save()

        return
    
    def getCurrentRrData(self):

        self.currentRrData = ModelEntities.getCurrentRrData()

        return

    def getUpdatedRrData(self):

        self.updatedRrData = ModelEntities.getTpRailroadJson('tpRailroadData')

        return
    
    def parseLocations(self):
        """
        Create three lists:
        self.continuingLocations = []
        self.newLocations = []
        self.oldLocations = []
        """

        currentLocations = self.currentRrData['locations']
        updatedLocations = self.updatedRrData['locations']

        self.newLocations = list(set(updatedLocations).difference(set(currentLocations)))
        self.oldLocations = list(set(currentLocations).difference(set(updatedLocations)))
        self.continuingLocations = list(set(currentLocations).difference(set(self.oldLocations)))

        return
    
    def addNewLocations(self):

        for location in self.newLocations:
            PSE.LM.newLocation(location)

        return
    
    def deleteOldLocations(self):

        for location in self.oldLocations:
            PSE.LM.deregister(PSE.LM.getLocationByName(location))

        return


class Divisionator:
    """
    All methods involving divisions.
    """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Divisionator'

        self.newDivisions = []
        self.obsoleteDivisions = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def divisionist(self):
        """
        Mini controller to process divisions.
        """

        self.parseDivisions()
        self.removeObsoleteDivisions()
        self.addNewDivisions()
        self.addDivisionToLocations()
        self.addUnreportedToUnknown()

        _psLog.info('Divisions updated')

        return

    def parseDivisions(self):

        updateDivisions = ModelEntities.getTpRailroadJson('tpRailroadData')['divisions']
        if updateDivisions[0] == '':
            updateDivisions = []
        
        currentDivisions = [division.getName() for division in PSE.DM.getList()]

        self.newDivisions = list(set(updateDivisions) - set(currentDivisions))
        self.obsoleteDivisions = list(set(currentDivisions) - set(updateDivisions))

        return

    def removeObsoleteDivisions(self):
        """
        First remove all divisions that are not in the TrainPlayer export.
        Second, for every location check that the assigned division is valid.
        If no, set the division to unassigned.
        """

        for division in self.obsoleteDivisions:
            obsolete = PSE.DM.getDivisionByName(division)
            PSE.DM.deregister(obsolete)

        allDivisions = PSE.getAllDivisionNames()
        locations = PSE.getAllLocationNames()
        for location in locations:
            divisionName = PSE.LM.getLocationByName(location).getDivisionName()
            if divisionName not in allDivisions and PSE.DM.getNumberOfdivisions() != 0:
                PSE.LM.getLocationByName(location).setDivision(PSE.DM.newDivision('Unassigned'))
            if divisionName not in allDivisions and PSE.DM.getNumberOfdivisions() == 0:
                PSE.LM.getLocationByName(location).setDivision(None)
        return

    def addNewDivisions(self):

        for division in self.newDivisions:
            PSE.DM.newDivision(division)

        return

    def addDivisionToLocations(self):
        """
        If there is only one division, add all locations to it.
        """

        if PSE.DM.getNumberOfdivisions() == 1:
            division = PSE.DM.getList()[0]
            [location.setDivision(division) for location in PSE.LM.getList()]

        if PSE.DM.getNumberOfdivisions() > 1:
            division = PSE.DM.newDivision(PSE.BUNDLE['Unassigned'])
            [location.setDivision(division) for location in PSE.LM.getList() if not location.getDivision()]

        return

    def addUnreportedToUnknown(self):
        """
        This method adds a division named Unknown.
        Add the location named Unreported to the division named Unknown.
        """

        if PSE.DM.getNumberOfdivisions() != 0:
            location = PSE.LM.getLocationByName('Unreported')
            # location = PSE.LM.getLocationByName(PSE.BUNDLE['Unreported'])

            division = PSE.DM.newDivision(PSE.BUNDLE['Unknown'])

            location.setDivision(division)

        return


class Trackulator:
    """
    Locations are updated using Location Manager.
    """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Trackulator'

        self.configFile = PSE.readConfigFile()

        self.currentRrData = {}
        self.updatedRrData = {}

        self.currentTrackIds = []
        self.updatedTrackIds = []
        self.continuingTrackIds = []
        self.newTrackIds = []
        self.oldTrackIds = []

        self.continuingTracks = []
        self.newTracks = []
        self.oldTracks = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def trackist(self):
        """
        Mini controller.
        Updates JMRI tracks and track attributes.
        """

        self.getCurrentRrData()
        self.getUpdatedRrData()
        self.getTrackIds()

        self.parseTrackIds()
        self.updateContinuingTracks()
        self.addNewTracks()
        self.deleteOldTracks()
        ModelEntities.addCarTypesToSpurs()
        self.addSchedulesToSpurs()

        return
    
    def getCurrentRrData(self):

        self.currentRrData = ModelEntities.getCurrentRrData()

        return

    def getUpdatedRrData(self):

        self.updatedRrData = ModelEntities.getTpRailroadJson('tpRailroadData')

        return
    
    def getTrackIds(self):

        # print(self.currentRrData['locales'])

        for trackId in self.currentRrData['locales']:
            self.currentTrackIds.append(trackId)

        for trackId in self.updatedRrData['locales']:
            self.updatedTrackIds.append(trackId)

        return
    
    def parseTrackIds(self):

        self.newTrackIds = list(set(self.updatedTrackIds).difference(set(self.currentTrackIds)))
        self.oldTrackIds = list(set(self.currentTrackIds).difference(set(self.updatedTrackIds)))
        self.continuingTrackIds = list(set(self.currentTrackIds).difference(set(self.oldTrackIds)))

        return

    def updateContinuingTracks(self):
        """
        format: "1": {"capacity": "12", "label": "FH", "location": "Fulton Terminal", "track": "Freight House", "type": "industry"}, 
        """


        for continuingTrackId in self.continuingTrackIds:
            currentTrackData = self.currentRrData['locales'][continuingTrackId]
            updatedTrackData = self.updatedRrData['locales'][continuingTrackId]


            if currentTrackData['location'] == updatedTrackData['location']:
                trackType = self.configFile['o2o']['TR'][updatedTrackData['type']]
                trackLength = int(updatedTrackData['capacity']) * (self.configFile['o2o']['DL'] + 4)
        # If the location is the same, only update the tracks name, type and length
                currentLocation = PSE.LM.getLocationByName(currentTrackData['location'])
                currentTrack = currentLocation.getTrackByName(currentTrackData['track'], None)
                currentTrack.setName(updatedTrackData['track'])
                currentTrack.setTrackType(trackType)
                currentTrack.setLength(trackLength)
            else:
        # If the locations differ, copy the current track, update name, type and length, and delete the current track
                currentLocation = PSE.LM.getLocationByName(currentTrackData['location'])
                currentTrack = currentLocation.getTrackByName(currentTrackData['track'], None)
                updatedLocation = PSE.LM.getLocationByName(updatedTrackData['location'])
                updatedTrack = currentTrack.copyTrack(updatedTrackData['track'], updatedLocation)
                updatedTrack.setName(updatedTrackData['track'])
                updatedTrack.setTrackType(trackType)
                updatedTrack.setLength(trackLength)

                currentLocation.deleteTrack(currentTrack)

        return

    def addNewTracks(self):
        """
        format: "1": {"capacity": "12", "label": "FH", "location": "Fulton Terminal", "track": "Freight House", "type": "industry"}, 
        """

        o2oConfig = self.configFile['o2o']

        for newTrackId in self.newTrackIds:
            newTrackData = self.updatedRrData['locales'][newTrackId]
            location = PSE.LM.getLocationByName(newTrackData['location'])
            trackType = o2oConfig['TR'][newTrackData['type']]
            track = location.addTrack(newTrackData['track'], trackType)
            trackLength = int(newTrackData['capacity']) * (o2oConfig['DL'] + 4)
            track.setLength(trackLength)
            trackComment = 'TrainPlayer ID:' + str(newTrackId)
            track.setComment(trackComment)

            if newTrackData['type'] == 'staging':
                track.setAddCustomLoadsAnySpurEnabled(o2oConfig['SM']['SCL'])
                track.setRemoveCustomLoadsEnabled(o2oConfig['SM']['RCL'])
                track.setLoadSwapEnabled(o2oConfig['SM']['LEE'])

            if newTrackData['track'] == '~' or newTrackData['type'] == 'XO reserved':
                track.setTrainDirections(0)

        return

    def deleteOldTracks(self):

        for oldTrackId in self.oldTrackIds:
            oldTrackData = self.currentRrData['locales'][oldTrackId]
            location = PSE.LM.getLocationByName(oldTrackData['location'])
            track = location.getTrackByName(oldTrackData['track'], None)
            location.deleteTrack(track)

        return

    def addSchedulesToSpurs(self):

        for id, data in self.updatedRrData['industries'].items():
            location = PSE.LM.getLocationByName(data['a-location'])
            track = location.getTrackByName(data['b-track'], 'Spur')
            scheduleName = data['c-schedule'].keys()[0]
            schedule = PSE.SM.getScheduleByName(scheduleName)
            track.setSchedule(schedule)

        return


class RStockulator:
    """
    All methods concerning rolling stock.
    """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.RStockulator'

        self.configFile = PSE.readConfigFile('o2o')
        self.tpRollingStockFileName = self.configFile['RF']['TRR']

        self.jmriCars = PSE.CM.getList()
        self.jmriLocos = PSE.EM.getList()

        self.tpInventory = []
        self.tpCars = {}
        self.tpLocos = {}

        self.listOfSpurs = []
        self.carList = []
        self.shipList = []

        return

    def updator(self):
        """
        Mini controller to update JMRI rolling stock.
        """

        self.getTpInventory()
        self.splitTpList()
        self.parseTpRollingStock()
        self.deleteOldRollingStock()
        self.updateRollingStock()

        print(self.scriptName + '.updator ' + str(SCRIPT_REV))
        _psLog.info('Updated rolling stock')

        return

    def scheduleApplicator(self):
        """
        Mini controller sets the loads for cars at spurs.
        """

        self.getAllSpurs()
        self.applySpursSchedule()
        self.setCarsAtStaging()

        print(self.scriptName + '.scheduleApplicator ' + str(SCRIPT_REV))

        return
    
    def getAllSpurs(self):

        for track in PSE.getAllTracks():
            if track.getTrackTypeName() == 'spur':
                self.listOfSpurs.append(track)

        return
    
    def applySpursSchedule(self):

        for spur in self.listOfSpurs:
            self.carList = PSE.CM.getList(spur)
            self.shipList = self.getShipList(spur)
            self.applySchedule()

        return
    
    def applySchedule(self):

        for car in self.carList:
            for ship in self.shipList:
                if car.getTypeName() == ship[0]:
                    car.setLoadName(ship[1])

        return
    
    def getShipList(self, spur):
        """
        A track can be a spur and not have a schedule.
        """

        try:
            spurSchedule = spur.getSchedule()
            items = spurSchedule.getItemsBySequenceList()
        except:
             _psLog.warning('No schedule for track: ' + spur.getName())
             return
        
        shipList = []
        for item in items:
            shipList.append((item.getTypeName(), item.getShipLoadName()))

        return shipList
    
    def setCarsAtStaging(self):

        for car in PSE.CM.getList():
            if car.getTrack().getTrackTypeName() == 'staging':
                car.setLoadName('E')

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
        """
        Makes a list of obsolete cars and locos.
        """

        updatedLocoIds = []
        for id, data in self.tpLocos.items():
            updatedLocoIds.append(data['id'])

        currentLocoIds = []
        for item in self.jmriLocos:
            currentLocoIds.append(item.getRoadName() + ' ' + item.getNumber())

        updatedCarIds = []
        for id, data in self.tpCars.items():
            updatedCarIds.append(data['id'])

        currentCarIds = []
        for item in self.jmriCars:
            currentCarIds.append(item.getRoadName() + ' ' + item.getNumber())

        self.oldTpLocoIds = list(set(currentLocoIds).difference(set(updatedLocoIds)))
        self.oldTpCarIds = list(set(currentCarIds).difference(set(updatedCarIds)))

        return

    def deleteOldRollingStock(self):

        for loco in self.oldTpLocoIds:
            locoId = loco.replace(' ', '')
            PSE.EM.deregister(PSE.EM.getById(locoId))

        for car in self.oldTpCarIds:
            carId = car.replace(' ', '')
            PSE.CM.deregister(PSE.CM.getById(carId))

        return

    def updateRollingStock(self):
        """
        Whether the RS is new or continuing, its 'base' attributes are updated.
        """

        _psLog.debug('setBaseCarAttribs')
        for id, data in self.tpCars.items():
            self.setBaseCarAttribs(data)

        _psLog.debug('setBaseLocoAttribs')
        for id, data in self.tpLocos.items():
            self.setBaseLocoAttribs(data)

        return

    def setBaseLocoAttribs(self, locoData):
        """
        Sets only the consist, length, model, type, location, track.
        self.tpLocos dictionary format: {TP ID :  [Model, AAR, JMRI Location, JMRI Track, 'unloadable', Consist, JMRI ID]}
        """

        locoId = locoData['id'].split()
        loco = PSE.EM.newRS(locoId[0], locoId[1])

        loco.setTypeName(locoData['aar'])
        loco.setModel(locoData['model'])
        loco.setLength(str(self.configFile['DL']))
        consist = PSE.ZM.getConsistByName(locoData['consist'])
        loco.setConsist(consist)

        location = PSE.LM.getLocationByName(locoData['location'])
        track = location.getTrackByName(locoData['track'], None)
        loco.setLocation(location, track, True)


        return

    def setBaseCarAttribs(self, carData):
        """
        Sets only the kernel, length, type, location, track.
        self.tpCars  dictionary format: {TP ID :  {type: TP Collection, aar: TP AAR, location: JMRI Location, track: JMRI Track, load: TP Load, kernel: TP Kernel, id: JMRI ID}}
        """

        carId = carData['id'].split()
        car = PSE.CM.newRS(carId[0], carId[1])

        car.setTypeName(carData['aar'])
        car.setLoadName(carData['load'])
        car.setLength(str(self.configFile['DL']))
        kernel = PSE.KM.getKernelByName(carData['kernel'])
        car.setKernel(kernel)

        location = PSE.LM.getLocationByName(carData['location'])
        track = location.getTrackByName(carData['track'], None)
        car.setLocation(location, track, True)

        return

# coding=utf-8
# © 2023 Greg Ritacco

"""
Resets all the data in the car, engine and locations xml.
Resets the ConfigFile.
From tpRailroadData.json, a JMRI railroad is created or updated.
"""

from opsEntities import PSE
from Subroutines.o2o import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Model')

def initializeSubroutine():
    """
    """

    return

def resetConfigFileItems():

    return

def refreshSubroutine():

    return

def resetBuiltTrains():
    """
    Resets all the trains that are built.
    """

    for train in PSE.TM.getTrainsByStatusList():
        if train.isBuilt():
            train.reset()

    return

def initializeJmriRailroad():
    """
    Mini controller.
    Reset the JMRI railroad for TrainPlayer import.
    Does not change Trains and Routes.
    Called by:
    Controller.StartUp.initializeJmriRailroad
    """

    PSE.DM.dispose()
    PSE.SM.dispose()
    PSE.LM.dispose()
    PSE.CM.dispose()
    PSE.EM.dispose()

    resetData = Resetter()
    resetData.setupResetter()
    resetData.carResetter()
    resetData.locoResetter()
    resetData.configFileResetter()

    Initializer().Initialize()

    _psLog.info('JMRI data has been reset')

    return

def updateJmriLocations():
    """
    Mini controller.
    Action for the Import Locations button.
    Changes are rippled through Industries, Cars and Extended Header
    Does not change Trains and Routes.
    Schedules are rewritten from scratch.
    Called by:
    Controller.StartUp.updateJmriLocations
    """

# This part does the locations
    locationator = Locationator()
    if not locationator.validate():
        return
    
    Attributator().updateRsAttributes() # Put this here to add all types to all locations

    locationator.updateLocations()
    
    Divisionator().divisionist()

    _psLog.info('JMRI locations updated from TrainPlayer data')

# This part does the tracks
    trackulator = Trackulator()
    if not trackulator.validate():
        return

    ScheduleAuteur().updateSchedules()
    trackulator.updateTracks()

    ModelEntities.deselectCarTypesAtSpurs()
    ModelEntities.selectCarTypesAtSpurs()

    _psLog.info('JMRI tracks updated from TrainPlayer data')
    

# This part does the rolling stock
    rollingStockulator = RollingStockulator()
    if not rollingStockulator.validate():
        return
    
    rollingStockulator.updateRollingStock()

    _psLog.info('JMRI rolling stock updated from TrainPlayer data')

# This part does the extended header
    ExtendedDetails().update()

    return

def updateJmriTracks():
    """
    Mini controller.
    Action for the Import Industries button.
    Changes are rippled through Cars and Extended Header
    Uses LM to update tracks and track attributes.
    Called by:
    Controller.Startup.updateJmriTracks
    """

    Attributator().updateRsAttributes()

    trackulator = Trackulator()
    if not trackulator.validate():
        return
    
    ScheduleAuteur().updateSchedules()
    trackulator.updateTracks()
    
    ModelEntities.deselectCarTypesAtSpurs()
    ModelEntities.selectCarTypesAtSpurs()

    _psLog.info('JMRI tracks updated from TrainPlayer data')

# This part does the rolling stock
    rollingStockulator = RollingStockulator()
    if not rollingStockulator.validate():
        return
    
    rollingStockulator.updateRollingStock()

    _psLog.info('JMRI rolling stock updated from TrainPlayer data')

# This part does the extended header
    ExtendedDetails().update()

    return

def updateJmriRollingingStock():
    """
    Mini controller.
    Action for the Import Cars button.
    Changes are rippled through Extended Header
    Loads cars at spurs per schedule.
    Sets cars load at staging to E.
    Called by:
    Controller.Startup.updateJmriRollingingStock
    """

    Attributator().updateRsAttributes()

# This part does the rolling stock
    rollingStockulator = RollingStockulator()
    if not rollingStockulator.validate():
        return
    
    rollingStockulator.updateRollingStock()

    _psLog.info('JMRI rolling stock updated from TrainPlayer data')

# This part does the extended header
    ExtendedDetails().update()
    
    return

def updateJmriProperties():
    """
    Action on press of the Import Extended Header button.
    """

    ExtendedDetails().update()

    _psLog.info('JMRI railroad properties updated from TrainPlayer data')

    return


class Resetter:
    """
    Reset XML details and Config File entries.
    """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Resetter'

        self.configFile =  PSE.readConfigFile()
        self.tpRailroad = ModelEntities.getTpRailroadJson('tpRailroadData')

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return
    
    def setupResetter(self):
        """
        Mini controller.
        """

        self.resetSetup()

        return
    
    def carResetter(self):
        """
        Mini controller.
        """

        self.resetCarTypes()
        self.resetCarRoadNames()
        self.resetCarColors()
        self.resetCarLengths()
        self.resetCarKernels()

        return
    
    def locoResetter(self):
        """
        Mini controller.
        """

        self.resetLocoLengths()
        self.resetLocoConsists()
        self.resetLocoModels()
        self.resetLocoTypes()

        return
    
    def configFileResetter(self):
        """
        Mini controller.
        """

        self.resetConfigFile()

        return
    
    def setupResetter(self):
        """
        """

        OSU = PSE.JMRI.jmrit.operations.setup
        OSU.Setup.setYearModeled('')
        OSU.Setup.setRailroadName('My JMRI Railroad')

        return
    
    def resetCarTypes(self):
        """
        If at least one car type is not added, JMRI will populate car types with a long list of defaults.
        """

        _psLog.debug('resetCarTypes')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarTypes
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        for type in TCM.getNames():
            TCM.deleteName(type)
        TCM.addName('xyz')

        return

    def resetCarRoadNames(self):
        """
        If at least one road name is not added, JMRI will populate road names with a long list of defaults.
        """
        _psLog.debug('resetCarRoadNames')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarRoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        for road in TCM.getNames():
            TCM.deleteName(road)

        TCM.addName('xyz')

        return

    def resetCarColors(self):
        """
        """

        _psLog.debug('resetCarColors')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarColors
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        for color in TCM.getNames():
            TCM.deleteName(color)
            
        color = PSE.getBundleItem('Generic')
        TCM.addName(color)

        return

    def resetCarLengths(self):
        """
        """

        _psLog.debug('resetCarLengths')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarLengths
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        for length in TCM.getNames():
            TCM.deleteName(length)

        TCM.addName(str(self.configFile['o2o']['DL']))

        return

    def resetCarKernels(self):
        """
        """
        _psLog.debug('resetCarKernels')

        for kernel in PSE.KM.getNameList():
            PSE.KM.deleteKernel(kernel)

        return

    def resetLocoLengths(self):
        """
        """

        _psLog.debug('resetLocoLengths')

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineLengths
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        for length in TCM.getNames():
            TCM.deleteName(length)

        TCM.addName(str(self.configFile['o2o']['DL']))

        return

    def resetLocoConsists(self):
        """
        """

        _psLog.debug('resetLocoConsists')

        for consist in PSE.ZM.getNameList():
            PSE.ZM.deleteConsist(consist)

        return
    
    def resetLocoModels(self):
        """
        """

        _psLog.debug('resetLocoModels')

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineModels
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        for model in TCM.getNames():
            TCM.deleteName(model)

        TCM.addName('xyz')

        return
    
    def resetLocoTypes(self):
        """
        """

        _psLog.debug('resetLocoTypes')

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineTypes
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        for type in TCM.getNames():
            TCM.deleteName(type)

        TCM.addName('xyz')

        return

    def resetConfigFile(self):
        """
        """

        _psLog.debug('resetConfigFile')

        self.configFile['Main Script']['LD'].update({"BD":""})
        self.configFile['Main Script']['LD'].update({"JN":""})
        self.configFile['Main Script']['LD'].update({"LN":""})
        self.configFile['Main Script']['LD'].update({"LO":""})
        self.configFile['Main Script']['LD'].update({"OR":""})
        self.configFile['Main Script']['LD'].update({"SC":""})
        self.configFile['Main Script']['LD'].update({"TR":""})
        self.configFile['Main Script']['LD'].update({"YR":""})

        PSE.writeConfigFile(self.configFile)

        return

class Initializer:
    """Make tweeks to Operations.xml here."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Initializer'

        self.OSU = PSE.JMRI.jmrit.operations.setup

        self.configFile =  PSE.readConfigFile()
        self.tpRailroad = ModelEntities.getTpRailroadJson('tpRailroadData')

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def Initialize(self):
        """
        Mini controller.
        Make settings changes.
        Some of these are personal.
        """

        self.tweakOperationsXml()
        self.setReportMessageFormat()

        _psLog.info('Layout details added')
        _psLog.info('JMRI operations settings updated')

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
        self.OSU.Setup.setAutoSaveEnabled(self.configFile['Main Script']['TO']['ASE'])

        return

    def setReportMessageFormat(self):
        """
        Sets the default message format as defined in the configFile.
        https://github.com/JMRI/JMRI/blob/master/java/src/jmri/jmrit/operations/setup/Setup.java
        """

        SB = PSE.JMRI.jmrit.operations.setup.Bundle()

        messageList = []
        for item in self.configFile['o2o']['RMF']['MC']:
            translatedItem = SB.handleGetMessage(self.configFile['o2o']['RMO'][item])
            messageList.append(translatedItem)
        self.OSU.Setup.setLocalManifestMessageFormat(messageList)

        messageList = []
        for item in self.configFile['o2o']['RMF']['PUC']:
            translatedItem = SB.handleGetMessage(self.configFile['o2o']['RMO'][item])
            messageList.append(translatedItem)
        self.OSU.Setup.setPickupManifestMessageFormat(messageList)

        messageList = []
        for item in self.configFile['o2o']['RMF']['SOC']:
            translatedItem = SB.handleGetMessage(self.configFile['o2o']['RMO'][item])
            messageList.append(translatedItem)
        self.OSU.Setup.setDropManifestMessageFormat(messageList)

        messageList = []
        for item in self.configFile['o2o']['RMF']['PUL']:
            translatedItem = SB.handleGetMessage(self.configFile['o2o']['RMO'][item])
            messageList.append(translatedItem)
        self.OSU.Setup.setPickupEngineMessageFormat(messageList)

        messageList = []
        for item in self.configFile['o2o']['RMF']['SOL']:
            translatedItem = SB.handleGetMessage(self.configFile['o2o']['RMO'][item])
            messageList.append(translatedItem)
        self.OSU.Setup.setDropEngineMessageFormat(messageList)

        return


class ExtendedDetails:
    """
    Adds the extended details that are part of the Quick Keys export, if used.
    """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.ExtendedDetails'

        self.configFile =  PSE.readConfigFile()

        self.tpRailroad = ModelEntities.getTpRailroadJson('tpRailroadData')

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return
    
    def update(self):
        """
        Mini controller to update railroad properties.
        """

        self.o2oDetailsToConFig()
        self.setRailroadDetails()

        _psLog.info('Layout details updated')

        return

    def o2oDetailsToConFig(self):
        """
        Optional Extended Header data from the TrainPlayer layout are added to the config file.
        """

        self.configFile['Main Script']['LD'].update({'OR':self.tpRailroad['Extended_operatingRoad']})
        self.configFile['Main Script']['LD'].update({'TR':self.tpRailroad['Extended_territory']})
        self.configFile['Main Script']['LD'].update({'LO':self.tpRailroad['Extended_location']})
        self.configFile['Main Script']['LD'].update({'YR':self.tpRailroad['Extended_year']})
        self.configFile['Main Script']['LD'].update({'SC':self.tpRailroad['Extended_scale']})
        self.configFile['Main Script']['LD'].update({'BD':self.tpRailroad['Extended_buildDate']})
        self.configFile['Main Script']['LD'].update({'LN':self.tpRailroad['Extended_layoutName']})
        
        self.configFile['Main Script']['LD'].update({'JN':PSE.makeCompositRailroadName(self.configFile['Main Script']['LD'])})

        PSE.writeConfigFile(self.configFile)
        self.configFile =  PSE.readConfigFile()

        return
    
    def setRailroadDetails(self):
        """
        Writes the o2o railroad name, scale and year data from o2o to JMRI settings.
        """

        _psLog.debug('setRailroadDetails')

        OSU = PSE.JMRI.jmrit.operations.setup
    # Set the railroad name
        rrName = self.configFile['Main Script']['LD']['LN']
        OSU.Setup.setRailroadName(rrName)
    # Set the year
        rrYear = self.configFile['Main Script']['LD']['YR']
        if rrYear:
            OSU.Setup.setYearModeled(rrYear)
    # Set the scale
        rrScale = self.configFile['Main Script']['LD']['SC']
        if rrScale:
            OSU.Setup.setScale(self.configFile['Main Script']['SR'][rrScale.upper()])

        PSE.JMRI.jmrit.operations.setup.OperationsSettingsPanel().savePreferences()

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
    
    def updateRsAttributes(self):
        """
        Mini controller to update rolling stock attributes to the RS xml files.
        """

        self.addRoads()
        self.addCarAar()
        self.addCarLoads()
        self.addCabooseLoads()
        self.addPassengerLoads()
        self.addCarKernels()

        self.addLocoModels()
        self.addLocoTypes()
        self.addLocoConsist()

        _psLog.info('New rolling stock attributes')

        return
    
    def addRoads(self):
        """
        Delets all existing road names first.
        Add any new road name from the tpRailroadData.json file.
        Don't do this: newNames = list(set(self.tpRailroadData['roads']) - set(TCM.getNames()))
        Null lists cause the default list to be added.
        """

        _psLog.debug('addRoads')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarRoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        for road in self.tpRailroadData['CarRoster_roads']:
            TCM.addName(road)

        TCM.deleteName('xyz')

        return
    
    def addCarAar(self):
        """
        Deletes all existing car types first.
        Add any new type names using the aar names from the tpRailroadData.json file.
        """

        _psLog.debug('addCarAar')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarTypes
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        for type in self.tpRailroadData['CarRoster_types']:
            TCM.addName(type)
        TCM.deleteName('xyz')

        return

    def addCarLoads(self):
        """
        Add the loads and load types for each car type (TP AAR) in tpRailroadData.json.
        Empty is the only TP empty type.
        """

        _psLog.debug('addCarLoads')

        empty = PSE.getBundleItem('Empty')
        load = PSE.getBundleItem('load')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarLoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        carLoads = self.tpRailroadData['CarRoster_loads']
        for aar in self.tpRailroadData['CarRoster_types']:
            TCM.addType(aar)
            TCM.addName(aar, 'Empty')
            TCM.addName(aar, 'load')
            TCM.setLoadType(aar, 'Empty', 'empty')
            TCM.setLoadType(aar, 'load', 'load')

            for loadName in carLoads[aar]:
                TCM.addName(aar, loadName)
                TCM.setLoadType(aar, loadName, 'load')

        return
    
    def addCabooseLoads(self):
        """
        Adds load name Occupied to cabeese.
        """

        _psLog.debug('addCabooseLoads')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarLoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        load = PSE.getBundleItem('Occupied')

        for car in self.tpRailroadData['AAR_Caboose']:
            TCM.addName(car, load)
            TCM.setLoadType(car, load, 'load')

        return

    def addPassengerLoads(self):
        """
        Adds load name Occupied to cabeese.
        """

        _psLog.debug('addPassengerLoads')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarLoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        load = PSE.getBundleItem('Occupied')

        for car in self.tpRailroadData['AAR_Passenger']:
            TCM.addName(car, load)
            TCM.setLoadType(car, load, 'load')

        return
    
    def addCarKernels(self):
        """
        Add new kernels using those from tpRailroadData.json.
        """

        _psLog.debug('addCarKernels')

        for xName in self.tpRailroadData['CarRoster_newKernels']:
            PSE.KM.newKernel(xName)

        return

    def addLocoModels(self):
        """
        Add new engine models using the model names from the tpRailroadData.json file.
        """

        _psLog.debug('addLocoModels')

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineModels
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)

        for model in TCM.getNames():
            TCM.deleteName(model)

        for xName in self.tpRailroadData['EngineRoster_models']:
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


        for type in TCM.getNames():
            TCM.deleteName(type)


        for xName in self.tpRailroadData['EngineRoster_types']:
            TCM.addName(xName)

        return

    def addLocoConsist(self):
        """
        Add new JMRI consist names using the consist names from the tpRailroadData.json file.
        """

        _psLog.debug('addLocoConsist')

        for xName in self.tpRailroadData['EngineRoster_newConsists']:
            PSE.ZM.newConsist(xName)

        return


class ScheduleAuteur:
    """
    Everything to do with schedules.
    """

    def __init__(self):

        self.tpIndustries = ModelEntities.getTpRailroadJson('tpRailroadData')['LocationRoster_spurs']
        self.allSchedules = []
        self.scheduleItems = []
        self.composedItems = []

        return
    
    def updateSchedules(self):
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
                    destination = self.checkDestination(item[3])
                    scheduleItem.setDestination(destination)
                    scheduleItem.setRoadName(item[4])
                    # scheduleItem.useViaOutForSomething(item[5])

        return
    
    def checkDestination(self, testDest):
        """
        Validates the schedule items destination was typed correctly into TrainPlayer.
        """

        if not testDest:
            return None

        checkDest = PSE.LM.getLocationByName(testDest)
        try:
            checkDest.getName()
            return checkDest

        except AttributeError:
            _psLog.critical('ALERT: Not a valid location:' + ' ' + testDest)

            PSE.openOutputFrame(PSE.getBundleItem('ALERT: Not a valid location:') + ' ' + testDest)
            PSE.openOutputFrame('Error at: TrainPlayer/Advanced Ops/Industries/Staging')
            return None

    
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

        self.validationResult = True

        self.currentRrData = ModelEntities.getCurrentRrData()
        self.updatedRrData = ModelEntities.getTpRailroadJson('tpRailroadData')

        self.continuingLocations = []
        self.newLocations = []
        self.oldLocations = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return
    
    def validate(self):
        """
        Mini controller.
        Add new validations here.
        """

        self.validateStaging()

        return self.validationResult

    def validateStaging(self):
        """
        Check that staging locations don't have other track types.
        """

        stagingList = []
        nonStagingList = []
        for _, locale in self.updatedRrData['LocationRoster_location'].items():
            if locale['type'] == 'staging':
                stagingList.append(locale['location'])
            else:
                nonStagingList.append(locale['location'])

        invalidLocations = list(set(stagingList).intersection(nonStagingList))
        if invalidLocations:
            _psLog.critical('ALERT: staging and non staging tracks at:' + ' ' + str(invalidLocations))
            PSE.openOutputFrame(PSE.getBundleItem('ALERT: staging and non staging tracks at:') + ' ' + str(invalidLocations))
            PSE.openOutputFrame(PSE.getBundleItem('Import terminated without completion'))

            self.validationResult = False
        else:
            _psLog.info('No conflicts at staging')

        return
    
    def updateLocations(self):
        """
        Mini controller.
        Updates new or continuing locations and delets obsolete locations.
        """

        self.parseLocations()
        self.addNewLocations()
        self.deleteOldLocations()

        return True
    
    def parseLocations(self):
        """
        Create three lists:
        self.continuingLocations = []
        self.newLocations = []
        self.oldLocations = []
        """

        currentLocations = self.currentRrData['locations']
        updatedLocations = self.updatedRrData['LocationRoster_locations']

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
        self.checkAssignedDivisions()
        self.addNewDivisions()
        self.addDivisionToLocations()
        self.addUnreportedToNull()

        _psLog.info('Divisions updated')

        return

    def parseDivisions(self):

        updateDivisions = ModelEntities.getTpRailroadJson('tpRailroadData')['Extended_divisions']
        if updateDivisions[0] == '':
            updateDivisions = []
        
        currentDivisions = [division.getName() for division in PSE.DM.getList()]

        self.newDivisions = list(set(updateDivisions) - set(currentDivisions))
        self.obsoleteDivisions = list(set(currentDivisions) - set(updateDivisions))

        return

    def removeObsoleteDivisions(self):
        """
        Remove all divisions that are not in the TrainPlayer export.
        """

        for division in self.obsoleteDivisions:
            obsolete = PSE.DM.getDivisionByName(division)
            PSE.DM.deregister(obsolete)

        return
    
    def checkAssignedDivisions(self):
        """        
        For every location check that the assigned division is valid.
        If not, set the division to None.
        """

        allDivisions = PSE.getAllDivisionNames()
        allLocations = PSE.getAllLocationNames()

        for location in allLocations:
            if PSE.LM.getLocationByName(location).getDivisionName() in allDivisions:
                continue
            else:
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

        return

    def addUnreportedToNull(self):
        """
        Add the location named 'Unreported' to the null division.
        """       

        # location = PSE.LM.getLocationByName('Unreported')
        location = PSE.LM.getLocationByName(PSE.getBundleItem('Unreported'))
        location.setDivision(None)

        return


class Trackulator:
    """
    Locations are updated using Location Manager.
    """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Trackulator'

        self.configFile = PSE.readConfigFile()

        self.validationResult = True

        self.currentRrData = ModelEntities.getCurrentRrData()
        self.updatedRrData = ModelEntities.getTpRailroadJson('tpRailroadData')

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

    def validate(self):
        """
        Mini controller.
        Add new validations here.
        """

        self.checkLocations()
        self.testLocationChanges()

        return self.validationResult
    
    def checkLocations(self):
        """
        Checks that there are locations to add tracks to.
        """

        if not PSE.getAllLocationNames():
            PSE.openOutputFrame(PSE.getBundleItem('ALERT: No JMRI locations were found.'))
            self.validationResult = False

        return
    
    def testLocationChanges(self):
        """
        If the Industries button is pressed out of sequence.
        Tests that no locations changes were made.
        """

        currentLocations = []
        for _, data in self.currentRrData['locales'].items():
            currentLocations.append(data['location'])

        updatedLocations = []
        for _, data in self.updatedRrData['LocationRoster_location'].items():
            updatedLocations.append(data['location'])

        testResult = list(set(currentLocations).difference(updatedLocations))
        if len(testResult) == 0:
            return
        else:
            _psLog.critical('ALERT: Not a valid location:' + ' ' + str(testResult))
            PSE.openOutputFrame(PSE.getBundleItem('ALERT: Not a valid location:') + ' ' + str(testResult))
            PSE.openOutputFrame(PSE.getBundleItem('Industries not imported. Import Locations recommended'))

            self.validationResult = False

            return
    
    def updateTracks(self):
        """
        Mini controller.
        Updates JMRI tracks and track attributes.
        """

        self.getTrackIds()
        self.parseTrackIds()
        self.updateContinuingTracks()
        self.addNewTracks()
        self.deleteOldTracks()
        self.addSchedulesToSpurs()

        return

    
    def getTrackIds(self):

        for trackId in self.currentRrData['locales']:
            self.currentTrackIds.append(trackId)

        for trackId in self.updatedRrData['LocationRoster_location']:
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
            updatedTrackData = self.updatedRrData['LocationRoster_location'][continuingTrackId]

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
            newTrackData = self.updatedRrData['LocationRoster_location'][newTrackId]
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
            if oldTrackId == '0':
                continue
            oldTrackData = self.currentRrData['locales'][oldTrackId]
            location = PSE.LM.getLocationByName(oldTrackData['location'])
            track = location.getTrackByName(oldTrackData['track'], None)
            location.deleteTrack(track)

        return

    def addSchedulesToSpurs(self):
        """
        Catches TrainPlayer error: track is not a spur but has an industries entry.
        """

        for _, data in self.updatedRrData['LocationRoster_spurs'].items():
            location = PSE.LM.getLocationByName(data['a-location'])
            track = location.getTrackByName(data['b-track'], 'Spur')
            if not track:
                _psLog.critical('ALERT: Not a spur track: ' + data['b-track'])
                PSE.openOutputFrame(PSE.getBundleItem('ALERT: Not a spur track:') + ' ' + data['b-track'])
                continue
            scheduleName = data['c-schedule'].keys()[0]
            schedule = PSE.SM.getScheduleByName(scheduleName)
            track.setSchedule(schedule)
        return


class RollingStockulator:
    """
    All methods concerning rolling stock.
    """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.RollingStockulator'

        self.configFile = PSE.readConfigFile()

        self.validationResult = True

        self.tpRailroad = ModelEntities.getTpRailroadJson('tpRailroadData')

        reportName = self.configFile['o2o']['RF']['RSD']
        fileName = reportName + '.txt'
        filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        self.tpInventory =  PSE.genericReadReport(filePath)
        self.tpInventory =  self.tpInventory.split('\n')
        # self.tpInventory = ModelEntities.getTpExport(self.configFile['o2o']['RF']['TRR'])

        self.jmriCars = PSE.CM.getList()
        self.jmriLocos = PSE.EM.getList()

        self.tpCars = {}
        self.tpLocos = {}

        self.listOfSpurs = []
        self.carList = []
        self.shipList = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def validate(self):
        """
        Add validations here.
        """

        self.checkTracks()

        return  self.validationResult
    
    def checkTracks(self):

        if not PSE.getAllTracks():     
            PSE.openOutputFrame(PSE.getBundleItem('ALERT: No JMRI tracks were found.'))
            self.validationResult = False

        return

    
    def updateRollingStock(self):
        """
        Mini controller.
        Updates the Rolling Stock XML.
        """

        _psLog.debug('updateRollingStock')
        
        self.parseTpInventory()
        self.getOldRollingStock()
        self.deleteOldRollingStock()
        self.updateBaseAttributes()
        self.scheduleApplicator()

        return

    def parseTpInventory(self):
        """
        self.tpInventory string format:
        TP Car ; TP Type ; TP AAR; JMRI Location; JMRI Track; TP Load; TP Kernel, TP ID
        TP Loco; TP Model; TP AAR; JMRI Location; JMRI Track; TP Load; TP Consist, TP ID

        self.tpCars  dictionary format: {TP ID :  {type: TP Collection, aar: TP AAR, location: JMRI Location, track: JMRI Track, load: TP Load, kernel: TP Kernel, id: JMRI ID}}
        self.tpLocos dictionary format: {TP ID :  [Model, AAR, JMRI Location, JMRI Track, 'unloadable', Consist, JMRI ID]}
        """

        for item in self.tpInventory:
            line = item.split(';')
            if line[2].startswith('ET'):
                # TrainPlayer tenders are not added to inventory
                continue

            location = line[3]
            track = line[4]
            if not self.testLocale(location, track):
                _psLog.critical('ALERT: Not a valid locale: ' + line[0] + ', ' + location + ', ' + track)
                PSE.openOutputFrame(PSE.getBundleItem('ALERT: Not a valid locale:') + line[0] + ', ' + location + ', ' + track)
                PSE.openOutputFrame(PSE.getBundleItem('ALERT: rolling stock skipped, parsing error.'))
                continue

            if line[2].startswith('E'):
                self.tpLocos[line[7]] = {'model': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'consist': line[6], 'id': line[0]}
            else:
                self.tpCars[line[7]] = {'type': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'kernel': line[6], 'id': line[0]}

        return

    def testLocale(self, location, track):
        """
        Returns the result of testing the location and track.
        """

        locationName = PSE.locationNameLookup(location)

        if PSE.LM.getLocationByName(locationName) == None:

            return False
        
        if PSE.LM.getLocationByName(locationName).getTrackByName(track, None) == None:

            return False
        
        return True

    def getOldRollingStock(self):
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
        for _, data in self.tpCars.items():
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

    def updateBaseAttributes(self):
        """
        Whether the RS is new or continuing, its 'base' attributes are updated.
        """

        _psLog.debug('updateBaseAttributes')

        for _, data in self.tpCars.items():
            self.setBaseCarAttribs(data)
    
        _psLog.debug('setBaseLocoAttribs')

        for _, data in self.tpLocos.items():
            self.setBaseLocoAttribs(data)

        return

    def setBaseCarAttribs(self, carData):
        """
        Maybe add color to base attribs?
        Sets only the kernel, length, type, location, track.
        self.tpCars  dictionary format: {TP ID :  {type: TP Collection, aar: TP AAR, location: JMRI Location, track: JMRI Track, load: TP Load, kernel: TP Kernel, id: JMRI ID}}
        """

        load = PSE.getBundleItem('Occupied')
        color = PSE.getBundleItem('Generic')

        carId = self.splitId(carData['id'])
        car = PSE.CM.newRS(carId[0], carId[1])

        car.setTypeName(carData['aar'])
        car.setLoadName(carData['load'])
        car.setColor(color)

        if carData['aar'] in self.tpRailroad['AAR_Caboose']:
            car.setCaboose(True)
            car.setLoadName(load)
        if carData['aar'] in self.tpRailroad['AAR_Passenger']:
            car.setPassenger(True)
            car.setLoadName(load)
        if carData['aar'] in self.tpRailroad['AAR_Express']:
            car.setPassenger(True)

        car.setLength(str(self.configFile['o2o']['DL']))
        kernel = PSE.KM.getKernelByName(carData['kernel'])
        car.setKernel(kernel)

        locationName = PSE.locationNameLookup(carData['location'])
        location = PSE.LM.getLocationByName(locationName)
        track = location.getTrackByName(carData['track'], None)
        car.setLocation(location, track, True)

        return
    
    def setBaseLocoAttribs(self, locoData):
        """
        Sets only the consist, length, model, type, location, track.
        self.tpLocos dictionary format: {TP ID :  [Model, AAR, JMRI Location, JMRI Track, 'unloadable', Consist, JMRI ID]}
        """

        color = PSE.getBundleItem('Generic')

        locoId = self.splitId(locoData['id'])
        loco = PSE.EM.newRS(locoId[0], locoId[1])

        loco.setTypeName(locoData['aar'])
        loco.setModel(locoData['model'])
        loco.setLength(str(self.configFile['o2o']['DL']))
        consist = PSE.ZM.getConsistByName(locoData['consist'])
        loco.setConsist(consist)
        loco.setColor(color)

        locationName = PSE.locationNameLookup(locoData['location'])
        location = PSE.LM.getLocationByName(locationName)
        track = location.getTrackByName(locoData['track'], None)
        loco.setLocation(location, track, True)

        return

    def splitId(self, rsData):
        """
        Returns the road name and road number as a list.
        """

        dataId = rsData.split(' ')
        try:
            return [dataId[0], dataId[1]]
        except IndexError:
            roadName = ''
            roadNumber = ''
            for char in rsData:
                if not char.isdigit():
                    roadName = roadName + char
                else:
                    roadNumber = roadNumber + char
            return [roadName, roadNumber]
        
    def scheduleApplicator(self):
        """
        Mini controller sets the loads for cars at spurs.
        """

        _psLog.debug('scheduleApplicator')

        self.getAllSpurs()
        self.applySpursScheduleToCars()
        self.setCarsAtStaging()

        return
    
    def getAllSpurs(self):
        """
        Returns an unordered list of spurs as strings.
        """

        for track in PSE.getAllTracks():
            if track.getTrackTypeName() == 'spur':
                self.listOfSpurs.append(track)

        return
    
    def applySpursScheduleToCars(self):
        """
        Applies a suprs schedule to each car at the spur.
        """

        for spur in self.listOfSpurs:
            self.carList = PSE.CM.getList(spur)
            self.shipList = self.getShipList(spur)
            self.applyScheduleItemToCar()

        return
    
    def applyScheduleItemToCar(self):

        for car in self.carList:
            litmus = 0
            for ship in self.shipList:
                if car.getTypeName() == ship[0]:
                    currentTrack = car.getTrack()
                    currentSchedule = currentTrack.getSchedule()
                    currentScheduleItem = currentSchedule.getItemByType(ship[0])
                    currentLoad = currentScheduleItem.getShipLoadName()
                    currentDestination = currentScheduleItem.getDestinationName()
                    currentDestination = PSE.LM.getLocationByName(currentDestination)

                    car.setLoadName(currentLoad)
                    car.setFinalDestination(currentDestination)
                    litmus = 1

            if litmus == 0:
                PSE.openOutputFrame(PSE.getBundleItem('ALERT: Schedule item not found for car:') + ' ' + car.getRoadName() + ' ' + car.getNumber() + ' ' + car.getTrackName())
                PSE.openOutputFrame(PSE.getBundleItem('Track does not serve this car type'))

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
            shipList.append((item.getTypeName(), item.getShipLoadName(), item.getDestinationName()))

        return shipList
    
    def setCarsAtStaging(self):

        for car in PSE.CM.getList():
            if car.getTrack().getTrackTypeName() == 'staging':
                car.setLoadName('E')

        return

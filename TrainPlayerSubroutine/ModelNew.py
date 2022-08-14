# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""From tpRailroadData.json, a new rr is created and the xml files are seeded"""

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelRollingStock

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.ModelAttributes'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ModelAttributes')

def getTpRailroadData():
    """Add error handling"""

    tpRailroadData = {}
    reportPath = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRailroadData.json'

    try:
        PatternScriptEntities.JAVA_IO.File(reportPath).isFile()
        _psLog.info('tpRailroadData.json OK')
    except:
        _psLog.warning('tpRailroadData.json not found')
        return

    tpRailroadData = PatternScriptEntities.genericReadReport(reportPath)
    tpRailroadData = PatternScriptEntities.loadJson(tpRailroadData)

    return tpRailroadData

def deleteOperationsXml():
    """Move the list to the config file
        For now keep the trains and routes xml
        """

    opsFileList = ['Operations', 'OperationsCarRoster', 'OperationsEngineRoster', 'OperationsLocationRoster']
    reportPath = PatternScriptEntities.PROFILE_PATH + 'operations\\'

    for file in opsFileList:
        xmlName =  PatternScriptEntities.PROFILE_PATH + 'operations\\' + file + '.xml'
        bakName =  PatternScriptEntities.PROFILE_PATH + 'operations\\' + file + '.xml.bak'
        try:
            PatternScriptEntities.JAVA_IO.File(xmlName).delete()
        except:
            print('Not found: ', xmlName)
        try:
            PatternScriptEntities.JAVA_IO.File(bakName).delete()
        except:
            print('Not found: ', bakName)

    return

def newJmriRailroad():
    """Mini controller to make a new JMRI railroad form the .json and TP Inventory.txt files"""

    deleteOperationsXml()

    newJmriRailroad = NewJmriRailroad()
    newJmriRailroad.addNewXml()
    newJmriRailroad.updateOperations()

    allRsRosters = NewRsAttributes()
    allRsRosters.newRoads()
    allRsRosters.newCarAar()
    allRsRosters.newCarLoads()
    allRsRosters.newCarKernels()

    allRsRosters.newLocoModels()
    allRsRosters.newLocoTypes()
    allRsRosters.newLocoConsist()

    newLocations = NewLocationsTracks()
    newLocations.newLocations()
    newLocations.newTracks()
    # newLocations.deselectSpurTypes()
    # newLocations.refineSpurTypes()

    newInventory = ModelRollingStock.UpdateInventory()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    # newInventory.deregisterJmriOrphans()
    newInventory.updateRollingStock()

    return


class NewJmriRailroad:
    """Adds the operations xml files if needed and updates Operatios.xml"""

    def __init__(self):

        self.TpRailroad = getTpRailroadData()

        self.Operations = PatternScriptEntities.OMX
        self.OperationsCarRoster = PatternScriptEntities.CMX
        self.OperationsEngineRoster = PatternScriptEntities.EMX
        self.OperationsLocationRoster = PatternScriptEntities.LMX

        return

    def addNewXml(self):
        """ Routes is not built since there is no TP equivalent.
            Trains is not built since JMRI trains is the point of this subroutine.
            """
        _psLog.debug('addNewXml')

        pathPrefix = PatternScriptEntities.PROFILE_PATH + 'operations\\'
        xmlList = ['Operations', 'OperationsCarRoster', 'OperationsEngineRoster', 'OperationsLocationRoster']
        for file in xmlList:
            filePath = pathPrefix + file + '.xml'
            if PatternScriptEntities.JAVA_IO.File(filePath).isFile():
                continue

            getattr(self, file).initialize()
            getattr(self, file).writeOperationsFile()

        return

    def updateOperations(self):
        """Make tweeks to Operations.xml here"""

        _psLog.debug('updateOperations')

        OSU = PatternScriptEntities.JMRI.jmrit.operations.setup
        OSU.Setup.setRailroadName(self.TpRailroad['railroadName'])
        OSU.Setup.setComment(self.TpRailroad['railroadDescription'])
        # Move the below items to the config file
        OSU.Setup.setMainMenuEnabled(True)
        OSU.Setup.setCloseWindowOnSaveEnabled(True)

        OSU.OperationsSetupXml.save()
        # Reload the Panal Pro window to display updates
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return


class NewRsAttributes:
    """TCM - Temporary Context Manager"""

    def __init__(self):

        self.tpRailroadData = getTpRailroadData()

        return

    def newRoads(self):
        """Replace defailt JMRI road names with the road names from the tpRailroadData.json file"""

        _psLog.debug('newRoads')

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarRoads)
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['roads']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.addName(xName)

        return

    def newCarAar(self):
        """Replace defailt JMRI road names with the road names from the tpRailroadData.json file"""

        _psLog.debug('newCarAar')

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarTypes)
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['carAAR']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.addName(xName)

        return

    def newCarLoads(self):
        """Add the loads and load types for each car type (TP AAR) in tpRailroadData.json"""

        _psLog.debug('newCarLoads')

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarLoads)

        carLoads = self.tpRailroadData['carLoads']
        for aar in self.tpRailroadData['carAAR']:
            aar = unicode(aar, PatternScriptEntities.ENCODING)
            TCM.addType(aar)
            TCM.addName(aar, 'Empty')
            TCM.addName(aar, 'Load')
            TCM.setLoadType(aar, 'Empty', 'empty')
            TCM.setLoadType(aar, 'Load', 'load')
            for load in carLoads[aar]:
                TCM.addName(aar, load)
                TCM.setLoadType(aar, load, 'load')

        return

    def newCarKernels(self):
        """Updates the car roster kernels with those from tpRailroadData.json"""

        _psLog.debug('newCarKernels')

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.KernelManager)
        nameList = TCM.getNameList()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteKernel(xName)
        for xName in self.tpRailroadData['carKernel']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.newKernel(xName)

        return

    def newLocoModels(self):
        """Replace defailt JMRI engine models with the model names from the tpRailroadData.json file"""

        _psLog.debug('newLocoModels')

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.EngineModels)
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['locoModels']:
            xModel = unicode(xName[0], PatternScriptEntities.ENCODING)
            xType = unicode(xName[1], PatternScriptEntities.ENCODING)
            TCM.addName(xModel)
            TCM.setModelType(xModel, xType)
            TCM.setModelLength(xModel, '40')

        return

    def newLocoTypes(self):
        """Replace defailt JMRI engine types with the type names from the tpRailroadData.json file"""

        _psLog.debug('newLocoTypes')

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.EngineTypes)
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['locoTypes']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)

            TCM.addName(xName)
        return

    def newLocoConsist(self):
        """Replace defailt JMRI consist names with the consist names from the tpRailroadData.json file"""

        _psLog.debug('newLocoConsist')

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.ConsistManager)
        nameList = TCM.getNameList()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteConsist(xName)
        for xName in self.tpRailroadData['locoConsists']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.newConsist(xName)

        return


class NewLocationsTracks:

    def __init__(self):

        self.tpRailroadData = getTpRailroadData()

        return

    def newLocations(self):

        _psLog.debug('newLocations')

        for location in self.tpRailroadData['locations']:
            newLocation = PatternScriptEntities.LM.newLocation(location)

        PatternScriptEntities.LMX.save()

        return

    def newTracks(self):

        _psLog.debug('newTracks')

        for item in self.tpRailroadData['locales']:
            loc = PatternScriptEntities.LM.getLocationByName(item[0])
            xTrack = loc.addTrack(item[1]['track'], item[1]['type'])
            xTrack.setComment(item[1]['ID'])
            trackLength = int(item[1]['capacity']) * 40
            xTrack.setLength(trackLength)

        PatternScriptEntities.LMX.save()

        return

    def deselectSpurTypes(self):
        """Deselect all types for spur tracks"""

        _psLog.debug('deselectSpurTypes')

        for item in self.tpRailroadData['locales']:
            if item[1]['type'] == 'Spur':
                loc = PatternScriptEntities.LM.getLocationByName(item[0])
                track = loc.getTrackByName(item[1]['track'], None)
                for typeName in loc.getTypeNames():
                    track.deleteTypeName(typeName)


    def refineSpurTypes(self):
        """Select specific car types for the spur, as defined in TP"""

        _psLog.debug('refineSpurTypes')

        for item in self.tpRailroadData['industries']:
            track = PatternScriptEntities.LM.getLocationByName(item[0]).getTrackByName(item[1]['track'], None)
            track.addTypeName(item[1]['type'])


        return

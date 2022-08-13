# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""From tpRailroadData.json, a new rr is created and the xml files are seeded"""

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.ModelCreate'
SCRIPT_REV = 20220101

def updateRailroadAttributes():
    """Mini Controller to update the OperationsCarRoster.xml roads and types elements
        and the OperationsEngineRoster.xml models and types elements
        """

    newJmriRailroad = NewJmriRailroad()

    newJmriRailroad.addNewXml()
    newJmriRailroad.updateOperations()

    allRsRosters = UpdateRsAttributes()

    allRsRosters.updateRoads()
    allRsRosters.updateCarAar()
    allRsRosters.updateCarLoads()
    allRsRosters.updateCarKernels()

    allRsRosters.updateLocoModels()
    allRsRosters.updateLocoTypes()
    allRsRosters.updateLocoConsist()

    updatedLocations = UpdateLocations()

    updatedLocations.updateLocations()
    updatedLocations.updateTracks()
    updatedLocations.deselectSpurTypes()
    updatedLocations.refineSpurTypes()

    return

def getTpRailroadData():
    """Add error handling"""

    tpRailroadData = {}
    reportPath = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRailroadData.json'

    try:
        PatternScriptEntities.JAVA_IO.File(reportPath).isFile()
    except:
        return

    tpRailroadData = PatternScriptEntities.genericReadReport(reportPath)
    tpRailroadData = PatternScriptEntities.loadJson(tpRailroadData)

    return tpRailroadData

class NewJmriRailroad:
    """Adds the operations xml files if needed and updates Operatios.xml"""

    def __init__(self):

        rrFile = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRailroadData.json'
        TpRailroad = PatternScriptEntities.genericReadReport(rrFile)
        self.TpRailroad = PatternScriptEntities.loadJson(TpRailroad)

        self.Operations = PatternScriptEntities.OMX
        self.OperationsCarRoster = PatternScriptEntities.CMX
        self.OperationsEngineRoster = PatternScriptEntities.EMX
        self.OperationsLocationRoster = PatternScriptEntities.LMX

        return

    def addNewXml(self):
        """ Routes is not built since there is no TP equivalent.
            Trains is not built since JMRI trains is the point of this subroutine.
            """

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

        OSU = PatternScriptEntities.JMRI.jmrit.operations.setup
        OSU.Setup.setRailroadName(self.TpRailroad['railroadName'])
        OSU.Setup.setComment(self.TpRailroad['railroadDescription'])
        OSU.Setup.setMainMenuEnabled(True)

        OSU.OperationsSetupXml.save()
        # Reload the Panal Pro window to display updates

        return


class UpdateRsAttributes:
    """TCM - Temporary Context Manager"""

    def __init__(self):

        self.tpRailroadData = getTpRailroadData()

        return

    def updateRoads(self):
        """Replace defailt JMRI road names with the road names from the tpRailroadData.json file"""

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarRoads)
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['roads']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.addName(xName)

        return

    def updateCarAar(self):
        """Replace defailt JMRI road names with the road names from the tpRailroadData.json file"""

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarTypes)
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['carAAR']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.addName(xName)

        return

    def updateCarLoads(self):
        """Add the loads and load types for each car type (TP AAR) in tpRailroadData.json"""

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

    def updateCarKernels(self):
        """Updates the car roster kernels with those from tpRailroadData.json"""

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.KernelManager)
        nameList = TCM.getNameList()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteKernel(xName)
        for xName in self.tpRailroadData['carKernel']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.newKernel(xName)

        return

    def updateLocoModels(self):
        """Replace defailt JMRI engine models with the model names from the tpRailroadData.json file"""

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

    def updateLocoTypes(self):
        """Replace defailt JMRI engine types with the type names from the tpRailroadData.json file"""

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.EngineTypes)
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['locoTypes']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)

            TCM.addName(xName)
        return

    def updateLocoConsist(self):
        """Replace defailt JMRI consist names with the consist names from the tpRailroadData.json file"""

        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.ConsistManager)
        nameList = TCM.getNameList()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteConsist(xName)
        for xName in self.tpRailroadData['locoConsists']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.newConsist(xName)

        return


class UpdateLocations:

    def __init__(self):

        self.tpRailroadData = getTpRailroadData()

        return

    def updateLocations(self):

        for location in self.tpRailroadData['locations']:
            newLocation = PatternScriptEntities.LM.newLocation(location)

        PatternScriptEntities.LMX.save()

        return

    def updateTracks(self):

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

        for item in self.tpRailroadData['locales']:
            if item[1]['type'] == 'Spur':
                loc = PatternScriptEntities.LM.getLocationByName(item[0])
                track = loc.getTrackByName(item[1]['track'], None)
                for item in loc.getTypeNames():
                    track.deleteTypeName(item)


    def refineSpurTypes(self):
        """Select specific car types for the spur, as defined in TP"""

        for item in self.tpRailroadData['industries']:
            track = PatternScriptEntities.LM.getLocationByName(item[0]).getTrackByName(item[1]['track'], None)
            track.addTypeName(item[1]['type'])


        return

# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""From tpRailroadData.json, a new rr is created and the xml files are seeded"""

from psEntities import PatternScriptEntities
from o2oSubroutine import ModelRollingStock

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelAttributes'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ModelAttributes')


def getTpRailroadData():
    """Add error handling"""

    tpRailroad = []
    reportPath = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRailroadData.json'

    try:
        PatternScriptEntities.JAVA_IO.File(reportPath).isFile()
        _psLog.info('tpRailroadData.json OK')
    except:
        _psLog.warning('tpRailroadData.json not found')
        return

    report = PatternScriptEntities.genericReadReport(reportPath)
    tpRailroad = PatternScriptEntities.loadJson(report)

    return tpRailroad

def newJmriRailroad():
    """Mini controller to make a new JMRI railroad from the tpRailroadData.json and TP Inventory.txt files
        Add code to close appropriate windows"""

    jmriRailroad = SetupXML()
    jmriRailroad.deleteAllXml()
    jmriRailroad.addOperationsXml()
    jmriRailroad.addCoreXml()
    jmriRailroad.tweakOperationsXml()

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
    newLocations.newSchedules()
    newLocations.newTracks()
    newLocations.deselectSpurTypes()
    newLocations.refineSpurTypes()

    newInventory = ModelRollingStock.Inventory()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.newCars()
    newInventory.newLocos()

    return

def updateRollingStock():
    """ """


    # jmriRailroad = SetupXML()
    # jmriRailroad.deleteCoreXml()
    # jmriRailroad.addCoreXml()
    # newInventory.deregisterJmriOrphans()

    return

class SetupXML:

    def __init__(self):

        self.tpConfig =  PatternScriptEntities.readConfigFile('o2o')

        self.TpRailroad = getTpRailroadData()

        self.Operations = PatternScriptEntities.OMX
        self.OperationsCarRoster = PatternScriptEntities.CMX
        self.OperationsEngineRoster = PatternScriptEntities.EMX
        self.OperationsLocationRoster = PatternScriptEntities.LMX

        return

    def deleteAllXml(self):

        reportPath = PatternScriptEntities.PROFILE_PATH + 'operations\\'
        opsFileList = PatternScriptEntities.JAVA_IO.File(reportPath).listFiles()
        for file in opsFileList:
            if file.toString().endswith('.xml') or file.toString().endswith('.bak'):
                file.delete()

        PatternScriptEntities.LM.dispose()
        PatternScriptEntities.CM.dispose()
        PatternScriptEntities.EM.dispose()

        return

    def deleteCoreXml(self):

        coreFileList = PatternScriptEntities.readConfigFile('o2o')['CFL']
        reportPath = PatternScriptEntities.PROFILE_PATH + 'operations\\'

        for file in coreFileList:
            xmlName =  reportPath + file + '.xml'
            bakName =  reportPath + file + '.xml.bak'
            PatternScriptEntities.JAVA_IO.File(xmlName).delete()
            PatternScriptEntities.JAVA_IO.File(bakName).delete()

        PatternScriptEntities.LM.dispose()
        PatternScriptEntities.CM.dispose()
        PatternScriptEntities.EM.dispose()
        return

    def addOperationsXml(self):

        self.Operations.writeOperationsFile()

        return

    def addCoreXml(self):
        """The routes xml is not built since there is no TP equivalent.
            The trains xml is not built since JMRI trains is the reason for this subroutine.
            """
        _psLog.debug('addCoreXml')

        pathPrefix = PatternScriptEntities.PROFILE_PATH + 'operations\\'
        coreFileList = PatternScriptEntities.readConfigFile('o2o')['CFL']
        for file in coreFileList:
            filePath = pathPrefix + file + '.xml'

            getattr(self, file).writeOperationsFile()

        return

    def tweakOperationsXml(self):
        """Make tweeks to Operations.xml here"""

        _psLog.debug('tweakOperationsXml')

        OSU = PatternScriptEntities.JMRI.jmrit.operations.setup
        OSU.Setup.setRailroadName(self.TpRailroad['railroadName'])
        OSU.Setup.setComment(self.TpRailroad['railroadDescription'])

        OSU.Setup.setMainMenuEnabled(self.tpConfig['SME'])
        OSU.Setup.setCloseWindowOnSaveEnabled(self.tpConfig['CWS'])
        OSU.Setup.setBuildAggressive(self.tpConfig['SBA'])
        OSU.Setup.setStagingTrackImmediatelyAvail(self.tpConfig['SIA'])
        OSU.Setup.setCarTypes(self.tpConfig['SCT'])

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

        tc = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarRoads
        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)
        # TCM.dispose()
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['roads']:
            xName = unicode(xName, PatternScriptEntities.ENCODING)
            TCM.addName(xName)

        return

    def newCarAar(self):
        """Replace defailt JMRI type names with the aar names from the tpRailroadData.json file"""

        _psLog.debug('newCarAar')

        tc = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarTypes
        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)
        TCM.dispose()
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

        tc = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarLoads
        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)
        carLoads = self.tpRailroadData['carLoads']
        for aar in self.tpRailroadData['carAAR']:
            aar = unicode(aar, PatternScriptEntities.ENCODING)
            TCM.addType(aar)
            TCM.addName(aar, 'Empty')
            TCM.addName(aar, 'Load')
            TCM.setLoadType(aar, 'Empty', 'empty')
            TCM.setLoadType(aar, 'Load', 'load')
        # TP has only Empty as the empty type
            for load in carLoads[aar]:
                TCM.addName(aar, load)
                TCM.setLoadType(aar, load, 'load')

        return

    def newCarKernels(self):
        """Updates the car roster kernels with those from tpRailroadData.json"""

        _psLog.debug('newCarKernels')

        tc = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.KernelManager
        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)
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

        tc = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.EngineModels
        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)
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

        tc = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.EngineTypes
        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)
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

        tc = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.ConsistManager
        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)
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
        self.tpConfig =  PatternScriptEntities.readConfigFile('o2o')

        return

    def tweakStagingTracks(self, track):
        """Tweak default settings for staging Tracks here"""

        track.setAddCustomLoadsAnySpurEnabled(self.tpConfig['SCL'])
        track.setRemoveCustomLoadsEnabled(self.tpConfig['RCL'])
        track.setLoadEmptyEnabled(self.tpConfig['LEE'])

        return

    def newLocations(self):

        _psLog.debug('newLocations')

        for location in self.tpRailroadData['locations']:
            newLocation = PatternScriptEntities.LM.newLocation(location)

        PatternScriptEntities.LMX.save()

        return

    def newSchedules(self):
        """Creates new schedules from tpRailroadData.json [industries]
            The schedule name is the TP track label
            """

        _psLog.debug('newSchedules')

        tc = PatternScriptEntities.JMRI.jmrit.operations.locations.schedules.ScheduleManager
        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)
        TCM.dispose()
        for id, industry in self.tpRailroadData['industries'].items():
            scheduleLineItem = industry['schedule']
            schedule = TCM.newSchedule(scheduleLineItem[0])
            scheduleItem = schedule.addItem(scheduleLineItem[1])
            scheduleItem.setReceiveLoadName(scheduleLineItem[2])
            scheduleItem.setShipLoadName(scheduleLineItem[3])

        # PatternScriptEntities.LMX.save()
        return

    def newTracks(self):

        _psLog.debug('newTracks')

        tc = PatternScriptEntities.JMRI.jmrit.operations.locations.schedules.ScheduleManager
        TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)
        # TCM.dispose()
        for item in self.tpRailroadData['locales']:
            loc = PatternScriptEntities.LM.getLocationByName(item[1]['location'])
            xTrack = loc.addTrack(item[1]['track'], item[1]['type'])
            xTrack.setComment(item[0])
            trackLength = int(item[1]['capacity']) * 44
            xTrack.setLength(trackLength)
            if item[1]['type'] == 'Spur':
                xTrack.setSchedule(TCM.getScheduleByName(item[1]['label']))
            if item[1]['type'] == 'Staging':
                self.tweakStagingTracks(xTrack)

        # PatternScriptEntities.LMX.save()
        return

    def deselectSpurTypes(self):
        """Deselect all types for spur tracks"""

        _psLog.debug('deselectSpurTypes')

        for item in self.tpRailroadData['locales']:
            if item[1]['type'] == 'Spur':
                loc = PatternScriptEntities.LM.getLocationByName(item[1]['location'])
                track = loc.getTrackByName(item[1]['track'], None)
                for typeName in loc.getTypeNames():
                    track.deleteTypeName(typeName)

        return

    def refineSpurTypes(self):
        """Select specific car types for the spur, as defined in TP"""

        _psLog.debug('refineSpurTypes')

        for id, attribs in self.tpRailroadData['industries'].items():
            track = PatternScriptEntities.LM.getLocationByName(attribs['location']).getTrackByName(attribs['track'], None)
            track.addTypeName(attribs['type'])

        return

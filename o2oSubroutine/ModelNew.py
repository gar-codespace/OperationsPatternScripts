# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""From tpRailroadData.json, a new rr is created and the xml files are seeded"""

from psEntities import PatternScriptEntities
from o2oSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelNew'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ModelNew')


def newJmriRailroad():
    """Mini controller to make a new JMRI railroad from the tpRailroadData.json and TP Inventory.txt files
        Add code to close appropriate windows"""

    jmriRailroad = SetupXML()
    jmriRailroad.deleteAllXml()
    jmriRailroad.addOperationsXml()
    jmriRailroad.addCoreXml()
    jmriRailroad.tweakOperationsXml()
    PatternScriptEntities.OMX.save()

    allRsRosters = NewRsAttributes()
    allRsRosters.newRoads()
    allRsRosters.newCarAar()
    allRsRosters.newCarLoads()
    allRsRosters.newCarKernels()

    allRsRosters.newLocoModels()
    allRsRosters.newLocoTypes()
    allRsRosters.newLocoConsist()

    newLocations = NewLocationsAndTracks()
    newLocations.newLocations()
    newLocations.newSchedules()
    newLocations.newTracks()
    newLocations.deselectSpurTypes()
    newLocations.refineSpurTypes()
    PatternScriptEntities.LMX.save()

    newInventory = NewRollingStock()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.newCars()
    newInventory.newLocos()
    PatternScriptEntities.CMX.save()
    PatternScriptEntities.EMX.save()

    return

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


class SetupXML:

    def __init__(self):

        self.o2oConfig =  PatternScriptEntities.readConfigFile('o2o')

        self.TpRailroad = getTpRailroadData()

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

        PatternScriptEntities.OMX.writeOperationsFile()

        return

    def addCoreXml(self):
        """The routes xml is not built since there is no TP equivalent.
            The trains xml is not built since JMRI trains is the reason for this subroutine.
            """
        _psLog.debug('addCoreXml')

        coreFileList = PatternScriptEntities.readConfigFile('o2o')['CFL']

        for file in coreFileList:
            getattr(PatternScriptEntities, file).writeOperationsFile()

        return

    def tweakOperationsXml(self):
        """Make tweeks to Operations.xml here
            Some of these are just favorites of mine
            """

        _psLog.debug('tweakOperationsXml')

        OSU = PatternScriptEntities.JMRI.jmrit.operations.setup
        OSU.Setup.setRailroadName(self.TpRailroad['railroadName'])
        OSU.Setup.setComment(self.TpRailroad['railroadDescription'])

        OSU.Setup.setMainMenuEnabled(self.o2oConfig['SME'])
        OSU.Setup.setCloseWindowOnSaveEnabled(self.o2oConfig['CWS'])
        OSU.Setup.setBuildAggressive(self.o2oConfig['SBA'])
        OSU.Setup.setStagingTrackImmediatelyAvail(self.o2oConfig['SIA'])
        OSU.Setup.setCarTypes(self.o2oConfig['SCT'])
        OSU.Setup.setStagingTryNormalBuildEnabled(self.o2oConfig['TNB'])
        OSU.Setup.setManifestEditorEnabled(self.o2oConfig['SME'])

        OSU.Setup.setPickupManifestMessageFormat(self.o2oConfig['PUC'])
        OSU.Setup.setDropManifestMessageFormat(self.o2oConfig['SOC'])
        OSU.Setup.setLocalManifestMessageFormat(self.o2oConfig['MC'])
        OSU.Setup.setPickupEngineMessageFormat(self.o2oConfig['PUL'])
        OSU.Setup.setDropEngineMessageFormat(self.o2oConfig['SOL'])

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
        # Empty is the only TP empty type
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


class NewLocationsAndTracks:

    def __init__(self):

        self.tpRailroadData = getTpRailroadData()
        self.o2oConfig =  PatternScriptEntities.readConfigFile('o2o')

        return

    def tweakStagingTracks(self, track):
        """Tweak default settings for staging Tracks here"""

        track.setAddCustomLoadsAnySpurEnabled(self.o2oConfig['SCL'])
        track.setRemoveCustomLoadsEnabled(self.o2oConfig['RCL'])
        track.setLoadEmptyEnabled(self.o2oConfig['LEE'])

        return

    def newLocations(self):

        _psLog.debug('newLocations')

        for location in self.tpRailroadData['locations']:
            newLocation = PatternScriptEntities.LM.newLocation(location)

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

class NewRollingStock:
    """Updates the JMRI RS inventory.
        Deletes JMRI RS not in TP Inventory.txt
        """

    def __init__(self):

        self.o2oConfig = PatternScriptEntities.readConfigFile('o2o')

        self.tpRollingStockFile = self.o2oConfig['TRR']
        self.tpInventory = []
        self.tpCars = {}
        self.tpLocos = {}

        self.jmriCars = PatternScriptEntities.CM.getList()
        self.jmriLocos = PatternScriptEntities.EM.getList()

        return

    def getTpInventory(self):

        try:
            self.tpInventory = ModelEntities.getTpExport(self.tpRollingStockFile)
            self.tpInventory.pop(0) # Remove the date
            self.tpInventory.pop(0) # Remove the key
            _psLog.info('TrainPlayer Inventory file OK')
        except:
            _psLog.warning('Not found: ' + self.tpRollingStockFile)
            pass

        return

    def splitTpList(self):
        """self.tpInventory string format:
            TP Car ; TP Type ; TP AAR; JMRI Location; JMRI Track; TP Load; TP Kernel
            TP Loco; TP Model; TP AAR; JMRI Location; JMRI Track; TP Load; TP Consist

            self.tpCars  dictionary format: {JMRI ID :  {type: TP Collection, aar: TP AAR, location: JMRI Location, track: JMRI Track, load: TP Load, kernel: TP Kernel}}
            self.tpLocos dictionary format: {JMRI ID :  [Model, AAR, JMRI Location, JMRI Track, 'unloadable', Consist]}
            """

        _psLog.debug('TsplitTpList')

        for item in self.tpInventory:
            line = item.split(';')
            if line[2].startswith('ET'):
                continue
            if line[2].startswith('E'):
                self.tpLocos[line[0]] = {'model': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'consist': line[6]}
            else:
                self.tpCars[line[0]] = {'type': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'kernel': line[6]}

        return

    def newCars(self):
        """'kernel': u'', 'type': u'box x23 prr', 'aar': u'XM', 'load': u'Empty', 'location': u'City', 'track': u'701'}"""

        _psLog.debug('newCars')

        for id, attribs in self.tpCars.items():
            rsRoad, rsNumber = ModelEntities.parseCarId(id)
            updatedCar = PatternScriptEntities.CM.newRS(rsRoad, rsNumber)
            xLocation, xTrack = ModelEntities.getSetToLocationAndTrack(attribs['location'], attribs['track'])
            if not xLocation:
                _psLog.warning(id + 'not set at: ' + attribs['location'], attribs['track'])
                continue
            updatedCar.setLocation(xLocation, xTrack, True)
            updatedCar.setTypeName(attribs['aar'])
            if attribs['aar'].startswith('N'):
                updatedCar.setCaboose(True)
            if attribs['aar'] in self.o2oConfig['PC']:
                updatedCar.setPassenger(True)
            updatedCar.setLength('40')
            updatedCar.setWeight('2')
            updatedCar.setColor('Red')
            updatedCar.setLoadName(attribs['load'])
            try:
                if xTrack.getTrackTypeName() == 'staging':
                    updatedCar.setLoadName('E')
            except:
                print('Not found', xTrack, updatedCar.getId())
            updatedCar.setKernel(PatternScriptEntities.KM.getKernelByName(attribs['kernel']))

        return

    def newLocos(self):

        _psLog.debug('newLocos')

        for id, attribs in self.tpLocos.items():
            rsRoad, rsNumber = ModelEntities.parseCarId(id)
            updatedLoco = PatternScriptEntities.EM.newRS(rsRoad, rsNumber)
            location, track = ModelEntities.getSetToLocationAndTrack(attribs['location'], attribs['track'])
            if not location:
                _psLog.warning(id + 'not set at: ' + attribs['location'], attribs['track'])
                continue
            updatedLoco.setLocation(location, track, True)
            updatedLoco.setLength('40')
            updatedLoco.setModel(attribs['model'][0:11])
        # Setting the model will automatically set the type
            updatedLoco.setWeight('2')
            updatedLoco.setColor('Black')
            updatedLoco.setConsist(PatternScriptEntities.ZM.getConsistByName(attribs['consist']))

        return

# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""From tpRailroadData.json, a new rr is created and the xml files are seeded"""

from psEntities import PSE
from o2oSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.Model'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('PS.TP.Model')


def newJmriRailroad():
    """Mini controller to make a new JMRI railroad from the tpRailroadData.json and TrainPlayer Report - Rolling Stock.txt files"""

    ModelEntities.closeTroublesomeWindows()

    PSE.TM.dispose()
    PSE.RM.dispose()
    PSE.LM.dispose()
    PSE.SM.dispose()
    PSE.CM.dispose()
    PSE.EM.dispose()

    jmriRailroad = SetupXML()
    jmriRailroad.tweakOperationsXml()

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
    newLocations.addCarTypesToSpurs()

    newInventory = NewRollingStock()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.makeTpRollingStockData()
    newInventory.newCars()
    newInventory.newLocos()

    _psLog.debug('setNonSpurTrackLength')
    ModelEntities.setNonSpurTrackLength()

    PSE.CMX.save()
    PSE.EMX.save()
    PSE.LMX.save()
    PSE.RMX.save()
    PSE.TMX.save()
    PSE.OMX.save()

    PSE.OMX.initialize()
    PSE.TMX.initialize()
    PSE.RMX.initialize()
    PSE.LMX.initialize()
    PSE.CMX.initialize()
    PSE.EMX.initialize()

    return

def updateJmriRailroad():
    """Mini controller to update JMRI railroad from the tpRailroadData.json and
        TrainPlayer Report - Rolling Stock.txt files.
        Does not change the Trains and Routes xml.
        Nothing fancy, new car and engine xml files are written.
        Used by:
        Controller.StartUp.updateRailroad
        """

    ModelEntities.closeTroublesomeWindows()

    PSE.CM.dispose()
    PSE.EM.dispose()

    allRsRosters = NewRsAttributes()
    allRsRosters.newRoads()
    allRsRosters.newCarAar()
    allRsRosters.newCarLoads()
    allRsRosters.newCarKernels()

    allRsRosters.newLocoModels()
    allRsRosters.newLocoTypes()
    allRsRosters.newLocoConsist()

    updateLocations = UpdateLocationsAndTracks()
    updateLocations.getContinuingLocations()
    updateLocations.getContinuingTracks()
    PSE.LM.dispose()
    PSE.SM.dispose()
    updateLocations.newSchedules()
    updateLocations.addNewLocations()
    updateLocations.addContinuingLocations()
    updateLocations.addNewTracks()
    updateLocations.addContinuingTracks()
    updateLocations.addCarTypesToSpurs()

    newInventory = NewRollingStock()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.makeTpRollingStockData()
    newInventory.newCars()
    newInventory.newLocos()

    _psLog.debug('setNonSpurTrackLength')
    ModelEntities.setNonSpurTrackLength()

    PSE.CMX.save()
    PSE.EMX.save()
    PSE.LMX.save()

    PSE.OMX.initialize()
    PSE.TMX.initialize()
    PSE.RMX.initialize()
    PSE.LMX.initialize()
    PSE.CMX.initialize()
    PSE.EMX.initialize()

    return


class UpdateLocationsAndTracks():

    def __init__(self):

        self.importedRailroad = ModelEntities.getTpRailroadData()

        allCurrentLocationNames = PSE.getAllLocationNames()
        self.newLocationNames = list(set(self.importedRailroad['locations']) - set(allCurrentLocationNames))
        self.continuingLocationNames = list(set(self.importedRailroad['locations']) - set(self.newLocationNames))

        importedRailroadTrackIds = [id for id in self.importedRailroad['locales']]
        allCurrentRailroadTrackIds = ModelEntities.getAllTrackIds()
        self.newTrackIds = list(set(importedRailroadTrackIds) - set(allCurrentRailroadTrackIds))
        self.continuingTrackIds = list(set(allCurrentRailroadTrackIds) - set(self.newTrackIds))

        self.allTracksHash = {}
        for track in PSE.getAllTracks():
            self.allTracksHash[track.getComment()] = track # (TP track ID, JMRI track object)

        self.continuingLocations = {}
        self.continuingTracks = {}

        return

    def getContinuingLocations(self):
        """A dictionary of all the continuing location objects by name."""

        _psLog.info('getContinuingLocations')

        for location in self.continuingLocationNames:
            self.continuingLocations[location] = PSE.LM.getLocationByName(location)

        return

    def getContinuingTracks(self):
        """A dictionary of all the continuing track objects by TP track ID."""

        _psLog.info('getContinuingTracks')

        for id in self.continuingTrackIds:
            self.continuingTracks[id] = self.allTracksHash[id]

        return

    def newSchedules(self):
        """Creates new schedules from tpRailroadData.json [industries]
            The schedule name is the TP track label
            """

        _psLog.debug('newSchedules')

        for id, industry in self.importedRailroad['industries'].items():
            ModelEntities.makeNewSchedule(id, industry)

        return

    def addNewLocations(self):

        if not self.newLocationNames:
            _psLog.info('0 locations added')

            return

        for i, location in enumerate(self.newLocationNames, start=1):
            PSE.LM.newLocation(location)
            # print(i)

        print(str(i) + ' locations added')
        _psLog.info(str(i) + ' locations added')

        return

    def addContinuingLocations(self):

        if not self.continuingLocationNames:
            _psLog.info('0 locations updated')

            return

        for i, location in enumerate(self.continuingLocationNames, start=1):
            ModelEntities.updateContinuingLocation(location)


        print(str(i) + ' locations updated')
        _psLog.info(str(i) + ' locations updated')

        return

    def addNewTracks(self):

        if not self.newTrackIds:
            _psLog.info('0 tracks added')

            return

        for i, trackId in enumerate(self.newTrackIds):
            trackData = self.importedRailroad['locales'][trackId]
            ModelEntities.makeNewTrack(trackId, trackData)

        print(str(i) + ' tracks added')
        _psLog.info(str(i) + ' tracks added')

        return

    def addContinuingTracks(self):

        if not self.continuingTrackIds:
            _psLog.info('0 tracks updated')

            return

        for i, trackId in enumerate(self.continuingTrackIds):
            trackData = self.importedRailroad['locales'][trackId]
            previousTrackData = self.allTracksHash[trackId]
            ModelEntities.updateContinuingTracks(trackId, trackData, previousTrackData)

        print(str(i) + ' tracks updated')
        _psLog.info(str(i) + ' tracks updated')

        return

    def addCarTypesToSpurs(self):
        """Checks the car types check box for car types used at each spur"""

        _psLog.debug('addCarTypesToSpurs')

        for id, industry in self.importedRailroad['industries'].items():
            ModelEntities.selectCarTypes(id, industry)

        return


class SetupXML:
    """Make tweeks to Operations.xml here."""

    def __init__(self):

        self.o2oConfig =  PSE.readConfigFile('o2o')
        self.TpRailroad = ModelEntities.getTpRailroadData()

        return

    def tweakOperationsXml(self):
        """Some of these are just favorites of mine."""

        _psLog.debug('tweakOperationsXml')

        OSU = PSE.JMRI.jmrit.operations.setup
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

        self.tpRailroadData = ModelEntities.getTpRailroadData()

        return

    def newRoads(self):
        """Replace defailt JMRI road names with the road names from the tpRailroadData.json file"""

        _psLog.debug('newRoads')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarRoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        # TCM.dispose()
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PSE.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['roads']:
            xName = unicode(xName, PSE.ENCODING)
            TCM.addName(xName)

        return

    def newCarAar(self):
        """Replace defailt JMRI type names with the aar names from the tpRailroadData.json file"""

        _psLog.debug('newCarAar')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarTypes
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        TCM.dispose()
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PSE.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['carAAR']:
            xName = unicode(xName, PSE.ENCODING)
            TCM.addName(xName)

        return

    def newCarLoads(self):
        """Add the loads and load types for each car type (TP AAR) in tpRailroadData.json"""

        _psLog.debug('newCarLoads')

        tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarLoads
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        carLoads = self.tpRailroadData['carLoads']
        for aar in self.tpRailroadData['carAAR']:
            aar = unicode(aar, PSE.ENCODING)
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

        # tc = PSE.JMRI.jmrit.operations.rollingstock.cars.KernelManager
        # TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        nameList = PSE.KM.getNameList()
        for xName in nameList:
            xName = unicode(xName, PSE.ENCODING)
            PSE.KM.deleteKernel(xName)
        for xName in self.tpRailroadData['carKernel']:
            xName = unicode(xName, PSE.ENCODING)
            PSE.KM.newKernel(xName)

        return

    def newLocoModels(self):
        """Replace defailt JMRI engine models with the model names from the tpRailroadData.json file"""

        _psLog.debug('newLocoModels')

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineModels
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PSE.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['locoModels']:
            xModel = unicode(xName[0], PSE.ENCODING)
            xType = unicode(xName[1], PSE.ENCODING)
            TCM.addName(xModel)
            TCM.setModelType(xModel, xType)
            TCM.setModelLength(xModel, '40')

        return

    def newLocoTypes(self):
        """Replace defailt JMRI engine types with the type names from the tpRailroadData.json file"""

        _psLog.debug('newLocoTypes')

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineTypes
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        nameList = TCM.getNames()
        for xName in nameList:
            xName = unicode(xName, PSE.ENCODING)
            TCM.deleteName(xName)
        for xName in self.tpRailroadData['locoTypes']:
            xName = unicode(xName, PSE.ENCODING)
            TCM.addName(xName)

        return

    def newLocoConsist(self):
        """Replace defailt JMRI consist names with the consist names from the tpRailroadData.json file"""

        _psLog.debug('newLocoConsist')

        # tc = PSE.JMRI.jmrit.operations.rollingstock.engines.ConsistManager
        # TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        nameList = PSE.ZM.getNameList()
        for xName in nameList:
            xName = unicode(xName, PSE.ENCODING)
            PSE.ZM.deleteConsist(xName)
        for xName in self.tpRailroadData['locoConsists']:
            xName = unicode(xName, PSE.ENCODING)
            PSE.ZM.newConsist(xName)

        return


class NewLocationsAndTracks:

    def __init__(self):

        self.tpRailroadData = ModelEntities.getTpRailroadData()

        return

    def newLocations(self):

        _psLog.debug('newLocations')

        for location in self.tpRailroadData['locations']:
            newLocation = PSE.LM.newLocation(location)

        return

    def newTracks(self):
        """Set spur length to spaces from TP
            Deselect all types for spur tracks
            """

        _psLog.debug('newTracks')

        for trackId, trackData in self.tpRailroadData['locales'].items():
            ModelEntities.makeNewTrack(trackId, trackData)

        return

    def newSchedules(self):
        """Creates new schedules from tpRailroadData.json [industries]
            The schedule name is the TP track label
            """

        _psLog.debug('newSchedules')

        for id, industry in self.tpRailroadData['industries'].items():
            ModelEntities.makeNewSchedule(id, industry)

        return

    def addCarTypesToSpurs(self):
        """Checks the car types check box for car types used at each spur"""

        _psLog.debug('addCarTypesToSpurs')

        for id, industry in self.tpRailroadData['industries'].items():
            ModelEntities.selectCarTypes(id, industry)

        return


class NewRollingStock:
    """Updates the JMRI RS inventory.
        Deletes JMRI RS not in TP Inventory.txt
        """

    def __init__(self):

        self.o2oConfig = PSE.readConfigFile('o2o')

        self.tpRollingStockFile = self.o2oConfig['TRR']
        self.tpInventory = []
        self.tpCars = {}
        self.tpLocos = {}

        self.jmriCars = PSE.CM.getList()
        self.jmriLocos = PSE.EM.getList()

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

    def makeTpRollingStockData(self):
        """Makes a json LUT: TP road + TP Number : TP ID"""

        _psLog.debug('makeTpRollingStockData')

        rsData = {}
        for item in self.tpInventory:
            line = item.split(';')
            name, number = ModelEntities.parseCarId(line[0])
            rsData[name + number] = line[7]


        reportName = 'tpRollingStockData'
        fileName = reportName + '.json'
        targetDir = PSE.PROFILE_PATH + '\\operations'
        targetPath = PSE.OS_Path.join(targetDir, fileName)

        formattedRsFile = PSE.dumpJson(rsData)
        PSE.genericWriteReport(targetPath, formattedRsFile)

        return


    def newCars(self):
        """'kernel': u'', 'type': u'box x23 prr', 'aar': u'XM', 'load': u'Empty', 'location': u'City', 'track': u'701'}"""

        _psLog.debug('newCars')

        for id, attribs in self.tpCars.items():
            rsRoad, rsNumber = ModelEntities.parseCarId(id)
            updatedCar = PSE.CM.newRS(rsRoad, rsNumber)
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
            updatedCar.setKernel(PSE.KM.getKernelByName(attribs['kernel']))

        return

    def newLocos(self):

        _psLog.debug('newLocos')

        for id, attribs in self.tpLocos.items():
            rsRoad, rsNumber = ModelEntities.parseCarId(id)
            updatedLoco = PSE.EM.newRS(rsRoad, rsNumber)
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
            updatedLoco.setConsist(PSE.ZM.getConsistByName(attribs['consist']))

        return

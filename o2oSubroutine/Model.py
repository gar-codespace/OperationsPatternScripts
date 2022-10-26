# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""From tpRailroadData.json, a new rr is created and the xml files are seeded."""

from opsEntities import PSE
from PatternTracksSubroutine import Model
from o2oSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.Model'
SCRIPT_REV = 20220101

"""Maybe move FILE_LIST to configFile.json?"""
FILE_LIST = ['OperationsTrainRoster.xml', 'OperationsRouteRoster.xml']

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Model')

def newJmriRailroad():
    """Mini controller to make a new JMRI railroad.
        tpRailroadData.json and TrainPlayer Report - Rolling Stock.txt
        are used as source files.
        Used by:
        Controller.StartUp.newJmriRailroad
        """

    ModelEntities.closeTroublesomeWindows()

    PSE.TM.dispose()
    PSE.RM.dispose()
    PSE.LM.dispose()
    PSE.SM.dispose()
    PSE.CM.dispose()
    PSE.EM.dispose()

    jmriRailroad = SetupXML()
    jmriRailroad.tweakOperationsXml()

    allRsRosters = AddRsAttributes()
    allRsRosters.addRoads()
    allRsRosters.addCarAar()
    allRsRosters.addCarLoads()
    allRsRosters.addCarKernels()
    allRsRosters.addLocoModels()
    allRsRosters.addLocoTypes()
    allRsRosters.addLocoConsist()

    newLocations = NewLocationsAndTracks()
    newLocations.newLocations()

    ModelEntities.newSchedules()

    newLocations.newTracks()

    ModelEntities.setTrackLength()
    ModelEntities.addCarTypesToSpurs()
    MakeTpLocaleData().make()

    newInventory = NewRollingStock()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.makeTpRollingStockData()
    newInventory.newCars()
    newInventory.newLocos()

    PSE.CMX.save()
    PSE.EMX.save()
    PSE.LMX.save()
    PSE.OMX.save()

    return

def updateJmriRailroad():
    """Mini controller to update JMRI railroad.
        Does not change Trains and Routes.
        Cars, engines and schedules are rewritten from scratch.
        Locations uses LM to update everything.
        Used by:
        Controller.StartUp.updateJmriRailroad
        """

    ModelEntities.closeTroublesomeWindows()

    PSE.SM.dispose()
    PSE.CM.dispose()
    PSE.EM.dispose()

    allRsRosters = AddRsAttributes()
    allRsRosters.addRoads()
    allRsRosters.addCarAar()
    allRsRosters.addCarLoads()
    allRsRosters.addCarKernels()
    allRsRosters.addLocoModels()
    allRsRosters.addLocoTypes()
    allRsRosters.addLocoConsist()

    updatedLocations = UpdateLocationsAndTracks()

    updatedLocations.getCurrent()
    MakeTpLocaleData().make()
    updatedLocations.getUpdated()

    updatedLocations.renameLocations()
    updatedLocations.parseLocations()
    updatedLocations.addNewLocations()

    updatedLocations.parseTracks()
    updatedLocations.renameTracks()
    updatedLocations.addNewTracks()

    ModelEntities.newSchedules()

    updatedLocations.updateTrackParams()

    ModelEntities.setTrackLength()
    ModelEntities.addCarTypesToSpurs()

    newInventory = NewRollingStock()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.makeTpRollingStockData()
    newInventory.newCars()
    newInventory.newLocos()

    updatedLocations.deleteOldTracks()
    updatedLocations.deleteOldLocations()

    PSE.CMX.save()
    PSE.EMX.save()

    return

def updateJmriRollingingStock():
    """Mini controller to update only the rolling stock.
        Used by:
        Controller.Startup.updateJmriRollingingStock
        """

    ModelEntities.closeTroublesomeWindows()

    PSE.CM.dispose()
    PSE.EM.dispose()

    allRsRosters = AddRsAttributes()
    allRsRosters.addRoads()
    allRsRosters.addCarAar()
    allRsRosters.addCarLoads()
    allRsRosters.addCarKernels()
    allRsRosters.addLocoModels()
    allRsRosters.addLocoTypes()
    allRsRosters.addLocoConsist()

    newInventory = NewRollingStock()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.makeTpRollingStockData()
    newInventory.newCars()
    newInventory.newLocos()

    PSE.CMX.save()
    PSE.EMX.save()

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

        OSU.Setup.setMainMenuEnabled(self.o2oConfig['TO']['SME'])
        OSU.Setup.setCloseWindowOnSaveEnabled(self.o2oConfig['TO']['CWS'])
        OSU.Setup.setBuildAggressive(self.o2oConfig['TO']['SBA'])
        OSU.Setup.setStagingTrackImmediatelyAvail(self.o2oConfig['TO']['SIA'])
        OSU.Setup.setCarTypes(self.o2oConfig['TO']['SCT'])
        OSU.Setup.setStagingTryNormalBuildEnabled(self.o2oConfig['TO']['TNB'])
        OSU.Setup.setManifestEditorEnabled(self.o2oConfig['TO']['SME'])

        OSU.Setup.setPickupManifestMessageFormat(self.o2oConfig['TO']['PUC'])
        OSU.Setup.setDropManifestMessageFormat(self.o2oConfig['TO']['SOC'])
        OSU.Setup.setLocalManifestMessageFormat(self.o2oConfig['TO']['MC'])
        OSU.Setup.setPickupEngineMessageFormat(self.o2oConfig['TO']['PUL'])
        OSU.Setup.setDropEngineMessageFormat(self.o2oConfig['TO']['SOL'])

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return


class MakeTpLocaleData:
    """Makes the tpLocaleData.json file."""

    def __init__(self):

        self.sourceData = {}
        self.tpLocaleData = {}

        self.locationList = []

        return

    def getTpRrData(self):

        fileName = 'tpRailroadData.json'
        filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        self.sourceData = PSE.loadJson(PSE.genericReadReport(filePath))

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

        trackScratch = {}
        trackData = {}
        for id, data in self.sourceData['locales'].items():
            otherTrack = (data['location'], data['track'], data['type'])
            trackData[id] = otherTrack

        self.tpLocaleData['tracks'] = trackData

        return

    def writeTpLocaleData(self):

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
        self.writeTpLocaleData()

        return


class AddRsAttributes:
    """TCM - Temporary Context Manager.
        Nothing is removed from OperationsCarRoster.xml, only added to.
        """

    def __init__(self):

        self.tpRailroadData = ModelEntities.getTpRailroadData()

        return

    def addRoads(self):
        """Add any new road name from the tpRailroadData.json file.
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
        """Add the loads and load types for each car type (TP AAR) in tpRailroadData.json.
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

        nameList = PSE.KM.getNameList()
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

        nameList = PSE.ZM.getNameList()
        for xName in self.tpRailroadData['locoConsists']:
            PSE.ZM.newConsist(xName)

        return


class UpdateLocationsAndTracks:
    """Locations and tracks are updated using Location Manager."""

    def __init__(self):

        self.o2oConfig = PSE.readConfigFile('o2o')
        self.tpRailroadData = ModelEntities.getTpRailroadData()

        self.currentLocale = {}
        self.updatedLocale = {}

        self.newLocations = []
        self.oldLocations = []

        self.continuingTracks = []
        self.newTracks = []
        self.oldTracks = []

        return

    def getCurrent(self):
        """self.currentLocale = the existing tpLocaleData.json"""

        _psLog.debug('getCurrent')

        fileName = 'tpLocaleData.json'
        filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        self.currentLocale = PSE.loadJson(PSE.genericReadReport(filePath))

        return

    def getUpdated(self):
        """self.updatedLocale = a new tpLocaleData.json"""

        _psLog.debug('getUpdated')

        fileName = 'tpLocaleData.json'
        filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        self.updatedLocale = PSE.loadJson(PSE.genericReadReport(filePath))

        return

    def renameLocations(self):
        """Way too nested."""

        _psLog.debug('renameLocations')

        for cLocation, cIds in self.currentLocale['locations'].items():
            for uLocation, uIds in self.updatedLocale['locations'].items():
                if cIds == uIds:
                    typeNames = PSE.LM.getLocationByName(cLocation).getTypeNames()
                    PSE.LM.getLocationByName(cLocation).setName(uLocation)
                    for typeName in typeNames:
                        PSE.LM.getLocationByName(uLocation).addTypeName(typeName)

        return

    def parseLocations(self):

        _psLog.debug('parseLocations')

        currentLocations = PSE.getAllLocationNames()
        updateLocations = [uLocation for uLocation, uIds in self.updatedLocale['locations'].items()]

        self.newLocations = list(set(updateLocations) - set(currentLocations))
        self.oldLocations = list(set(currentLocations) - set(updateLocations))

        return

    def addNewLocations(self):

        _psLog.debug('addNewLocations')

        for location in self.newLocations:
            PSE.LM.newLocation(location)

        return

    def parseTracks(self):

        _psLog.debug('parseTracks')

        currentKeys = self.currentLocale['tracks'].keys()
        updateKeys = self.updatedLocale['tracks'].keys()

        oldKeys = list(set(currentKeys) - set(updateKeys))
        continuingKeys = list(set(currentKeys) - set(oldKeys))
        newKeys = list(set(updateKeys) - set(currentKeys))

        for key in oldKeys:
            self.oldTracks.append(self.currentLocale['tracks'][key])

        for key in newKeys:
            self.newTracks.append(self.updatedLocale['tracks'][key])

        for key in continuingKeys:
            cTrack = self.currentLocale['tracks'][key]
            uTrack = self.updatedLocale['tracks'][key]
            if cTrack[0] == uTrack[0]:
                self.continuingTracks.append(cTrack)
            else:
                self.newTracks.append(uTrack)
                self.oldTracks.append(cTrack)

        _psLog.info('Continuing tracks: ' + str(self.continuingTracks))
        _psLog.info('New tracks: ' + str(self.newTracks))
        _psLog.info('Old tracks: ' + str(self.oldTracks))

        return

    def renameTracks(self):
        """Rename tracks that have not changed locations.
            Too much indenting?
            """

        _psLog.debug('renameTracks')

        print(self.continuingTracks)

        for cTrack in self.continuingTracks:
            for id, data in self.currentLocale['tracks'].items():
                if cTrack == self.currentLocale['tracks'][id]:
                    uTrack = self.updatedLocale['tracks'][id]
                    trackType = self.o2oConfig['TR'][cTrack[2]]
                    PSE.LM.getLocationByName(cTrack[0]).getTrackByName(cTrack[1], trackType).setName(uTrack[1])

        return

    def updateTrackParams(self):
        """For all continuing track IDs, update the type, train dirs, and track attribs."""

        _psLog.debug('updateTrackParams')

        for id, trackData in self.tpRailroadData['locales'].items():

            location = PSE.LM.getLocationByName(self.updatedLocale['tracks'][id][0])
            cTrackType = self.currentLocale['tracks'][id][2]

            track = location.getTrackByName(self.updatedLocale['tracks'][id][1], self.o2oConfig['TR'][cTrackType])

            uTrackType = self.updatedLocale['tracks'][id][2]
            jmriTrackType = self.o2oConfig['TR'][uTrackType]

            track.setTrackType(jmriTrackType)
            track.setTrainDirections(15)
            ModelEntities.setTrackAttribs(trackData)

        return

    def addNewTracks(self):

        _psLog.debug('addNewTracks')

        for locTrack in self.newTracks:
            trackId = self.updatedLocale['tracks'][locTrack]
            trackData = self.tpRailroadData['locales'][trackId]
            ModelEntities.makeNewTrack(trackId, trackData)

        return

    def deleteOldTracks(self):

        for item in self.oldTracks:
            trackType = self.o2oConfig['TR'][item[2]]
            location = PSE.LM.getLocationByName(item[0])
            track = location.getTrackByName(item[1], trackType)
            location.deleteTrack(track)
            track.dispose()

        return

    def deleteOldLocations(self):

        for item in self.oldLocations:
            location = PSE.LM.getLocationByName(item)
            PSE.LM.deregister(location)
            location.dispose()

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

        _psLog.debug('newTracks')

        for trackId, trackData in self.tpRailroadData['locales'].items():
            ModelEntities.makeNewTrack(trackId, trackData)

        return


class NewRollingStock:

    def __init__(self):

        self.o2oConfig = PSE.readConfigFile('o2o')

        self.tpRollingStockFile = self.o2oConfig['RF']['TRR']
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
            _psLog.warning('TrainPlayer Inventory file not found')

        return

    def splitTpList(self):
        """self.tpInventory string format:
            TP Car ; TP Type ; TP AAR; JMRI Location; JMRI Track; TP Load; TP Kernel
            TP Loco; TP Model; TP AAR; JMRI Location; JMRI Track; TP Load; TP Consist

            self.tpCars  dictionary format: {JMRI ID :  {type: TP Collection, aar: TP AAR, location: JMRI Location, track: JMRI Track, load: TP Load, kernel: TP Kernel}}
            self.tpLocos dictionary format: {JMRI ID :  [Model, AAR, JMRI Location, JMRI Track, 'unloadable', Consist]}
            """

        _psLog.debug('splitTpList')

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
            try:
                line = item.split(';')
                name, number = ModelEntities.parseCarId(line[0])
                rsData[name + number] = line[7]
            except:
                _psLog.warning('Line not parsed: ' + item)
                pass

        fileName = 'tpRollingStockData.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

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

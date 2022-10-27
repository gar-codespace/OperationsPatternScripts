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

    tpLocaleData = MakeTpLocaleData()
    tpLocaleData.make()
    if tpLocaleData.isValid():
        tpLocaleData.write()
    else:
        return False

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

    return True

def updateJmriRailroad():
    """Mini controller to update JMRI railroad.
        Does not change Trains and Routes.
        Cars, engines and schedules are rewritten from scratch.
        Locations uses LM to update everything.
        Used by:
        Controller.StartUp.updateJmriRailroad
        """

    tpLocaleData = MakeTpLocaleData()
    tpLocaleData.make()
    if not tpLocaleData.isValid():
        return False

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
    tpLocaleData.write()
    updatedLocations.getUpdated()

    updatedLocations.parseLocations()
    updatedLocations.processLocations()
    updatedLocations.addNewLocations()

    ModelEntities.newSchedules()

    updatedLocations.parseTracks()
    updatedLocations.deleteOldTracks()
    updatedLocations.addNewTracks()
    updatedLocations.recastTracks()

    ModelEntities.setTrackLength()
    ModelEntities.addCarTypesToSpurs()

    newInventory = NewRollingStock()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.makeTpRollingStockData()
    newInventory.newCars()
    newInventory.newLocos()

    updatedLocations.deleteOldLocations()

    PSE.CMX.save()
    PSE.EMX.save()

    return True

def updateJmriRollingingStock():
    """Mini controller to update only the rolling stock.
        Used by:
        Controller.Startup.updateJmriRollingingStock
        """

    try:
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

        return True

    except:
        return False


class SetupXML:
    """Make tweeks to Operations.xml here."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.SetupXML'

        self.o2oConfig =  PSE.readConfigFile('o2o')
        self.TpRailroad = ModelEntities.getTpRailroadData()

        print(self.scriptName + ' ' + str(SCRIPT_REV))

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

        return


class MakeTpLocaleData:
    """Makes the tpLocaleData.json file."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.MakeTpLocaleData'

        self.sourceData = {}
        self.tpLocaleData = {}

        self.locationList = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

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

    def isValid(self):
        """Catch  all user errors here.
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
            PSE.outputPanel(PSE.BUNDLE['ALERT: Staging and non staging tracks at same location: '] + str(result))
            _psLog.critical('ALERT: Staging and non staging tracks at same location: ' + str(result))
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

        return


class AddRsAttributes:
    """TCM - Temporary Context Manager.
        Nothing is removed from OperationsCarRoster.xml, only added to.
        """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.AddRsAttributes'

        self.tpRailroadData = ModelEntities.getTpRailroadData()

        print(self.scriptName + ' ' + str(SCRIPT_REV))

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

        self.scriptName = SCRIPT_NAME + '.UpdateLocationsAndTracks'

        self.o2oConfig = PSE.readConfigFile('o2o')
        self.tpRailroadData = ModelEntities.getTpRailroadData()

        self.currentLocale = {}
        self.updatedLocale = {}

        self.oldLocations = []
        self.newLocations = []
        self.renameLocations = []

        self.oldKeys = []
        self.newKeys = []
        self.continuingKeys = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

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

    def parseLocations(self):

        _psLog.debug('parseLocations')

        currentLocations = PSE.getAllLocationNames()
        updateLocations = [uLocation for uLocation, uIds in self.updatedLocale['locations'].items()]

        unchangedLocations = []
        modifiedLocations = []
        for cLocation, cIds in self.currentLocale['locations'].items():
            for uLocation, uIds in self.updatedLocale['locations'].items():
                if cIds == uIds and cLocation == uLocation:
                    unchangedLocations.append(cLocation)
                if cIds == uIds and cLocation != uLocation:
                    self.renameLocations.append((cLocation, uLocation))
                    modifiedLocations.append(cLocation)
                    modifiedLocations.append(uLocation)

        self.newLocations = list(set(updateLocations) - set(unchangedLocations) - set(modifiedLocations))

        return

    def processLocations(self):

        _psLog.debug('renameLocations')

        for item in self.renameLocations:
            PSE.LM.getLocationByName(item[0]).setName(item[1])

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

        self.oldKeys = list(set(currentKeys) - set(updateKeys))
        self.newKeys = list(set(updateKeys) - set(currentKeys))

        for cKey, cData in self.currentLocale['tracks'].items():
            for uKey, uData in self.updatedLocale['tracks'].items():
                if cKey == uKey and cData[0] == uData[0]:
                    self.continuingKeys.append(cKey)
                if cKey == uKey and cData[0] != uData[0]:
                    self.newKeys.append(cKey)
                    self.oldKeys.append(cKey)

        _psLog.info('Old keys: ' + str(self.oldKeys))
        _psLog.info('New keys: ' + str(self.newKeys))
        _psLog.info('Continuing keys: ' + str(self.continuingKeys))

        return

    def recastTracks(self):
        """For tracks that have not changed locations, update:
            name
            track type
            train diretions (keep this?)
            track attributes
            """

        _psLog.debug('recastTracks')

        for key in self.continuingKeys:
            location = self.updatedLocale['tracks'][key][0]

            track = self.currentLocale['tracks'][key][1]
            trackType = self.currentLocale['tracks'][key][2]
            jmriTrackType = self.o2oConfig['TR'][trackType]

            newTrack = self.updatedLocale['tracks'][key][1]
            newTrackType = self.updatedLocale['tracks'][key][2]
            newJmriTrackType = self.o2oConfig['TR'][newTrackType]

            location = PSE.LM.getLocationByName(location)
            track = location.getTrackByName(track, jmriTrackType)
            track.setName(newTrack)
            location.getTrackByName(newTrack, jmriTrackType).setTrackType(newJmriTrackType)
            location.getTrackByName(newTrack, newJmriTrackType).setTrainDirections(15)

            trackData = self.tpRailroadData['locales'][key]
            ModelEntities.setTrackAttribs(trackData)

        return

    def addNewTracks(self):

        _psLog.debug('addNewTracks')

        for key in self.newKeys:
            trackData = self.tpRailroadData['locales'][key]
            ModelEntities.makeNewTrack(key, trackData)

        return

    def deleteOldTracks(self):

        # print(self.oldKeys)

        for key in self.oldKeys:
            cTrackData = self.currentLocale['tracks'][key]

            # print(cTrackData)

            trackType = self.o2oConfig['TR'][cTrackData[2]]
            location = PSE.LM.getLocationByName(cTrackData[0])
            track = location.getTrackByName(cTrackData[1], trackType)
            location.deleteTrack(track)
            track.dispose()

        return

    def deleteOldLocations(self):
        """Delete locations which have no tracks."""

        for location in PSE.LM.getList():
            if not location.getTracksList():
                PSE.LM.deregister(location)
                location.dispose()

        return


class NewLocationsAndTracks:

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.NewLocationsAndTracks'
        self.tpRailroadData = ModelEntities.getTpRailroadData()

        print(self.scriptName + ' ' + str(SCRIPT_REV))

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

        self.scriptName = SCRIPT_NAME + '.NewRollingStock'

        self.o2oConfig = PSE.readConfigFile('o2o')

        self.tpRollingStockFile = self.o2oConfig['RF']['TRR']
        self.tpInventory = []
        self.tpCars = {}
        self.tpLocos = {}

        self.jmriCars = PSE.CM.getList()
        self.jmriLocos = PSE.EM.getList()

        print(self.scriptName + ' ' + str(SCRIPT_REV))

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

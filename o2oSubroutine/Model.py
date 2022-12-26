# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""From tpRailroadData.json, a new rr is created and the xml files are seeded."""

from opsEntities import PSE
from o2oSubroutine import ModelEntities
from o2oSubroutine import BuiltTrainExport
from PatternTracksSubroutine import ModelEntities as ptModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.Model'
SCRIPT_REV = 20221010

FILE_LIST = ['OperationsTrainRoster.xml', 'OperationsRouteRoster.xml']

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Model')


def o2oWorkEventReset():
    """Creates a new o2o Work Events.json file
        Called by:
        PT Sub Controller.StartUp.setRsButton
        """

    fileName = PSE.BUNDLE['o2o Work Events'] + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    newHeader = ptModelEntities.makeGenericHeader()
    newHeader = PSE.dumpJson(newHeader)
    PSE.genericWriteReport(targetPath, newHeader)

    return

def newJmriRailroad():
    """Mini controller to make a new JMRI railroad.
        tpRailroadData.json and TrainPlayer Report - Rolling Stock.txt
        are used as source files.
        Called by:
        Controller.StartUp.newJmriRailroad
        """

    tpLocaleData = MakeTpLocaleData()
    tpLocaleData.make()
    if tpLocaleData.isValid():
        tpLocaleData.write()
    else:
        return False

    PSE.closeTroublesomeWindows()

    PSE.TMX.makeBackupFile('operations/OperationsTrainRoster.xml')
    PSE.TMX.makeBackupFile('operations/OperationsRouteRoster.xml')

    PSE.TM.dispose()
    PSE.RM.dispose()
    PSE.DM.dispose()
    PSE.LM.dispose()
    PSE.SM.dispose()
    PSE.CM.dispose()
    PSE.EM.dispose()

    jmriRailroad = SetupXML()
    jmriRailroad.addDetailsToConFig()
    jmriRailroad.setRailroadDetails()
    jmriRailroad.tweakOperationsXml()
    jmriRailroad.setReportMessageFormat()

    allRsRosters = RollingStockAttributes()
    allRsRosters.addRoads()
    allRsRosters.addCarAar()
    allRsRosters.addCarLoads()
    allRsRosters.addCarKernels()
    allRsRosters.addLocoModels()
    allRsRosters.addLocoTypes()
    allRsRosters.addLocoConsist()

    divisions = Divisionator()
    divisions.parseDivisions()
    divisions.addNewDivisions()

    newLocations = Locationator()
    newLocations.newLocations()

    divisions.addDivisionToLocations()

    ModelEntities.newSchedules()

    newLocations.newTracks()

    ModelEntities.setTrackLength()
    ModelEntities.addCarTypesToSpurs()

    newInventory = RollingStockonator()
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
        Called by:
        Controller.StartUp.updateJmriRailroad
        """

    tpLocaleData = MakeTpLocaleData()
    tpLocaleData.make()
    if not tpLocaleData.isValid():
        return False

    resetTrains = BuiltTrainExport.FindTrain()
    resetTrains.getBuiltTrains()
    resetTrains.resetBuildTrains()

    PSE.closeTroublesomeWindows()

    PSE.SM.dispose()
    PSE.CM.dispose()
    PSE.EM.dispose()

    jmriRailroad = SetupXML()
    jmriRailroad.addDetailsToConFig()
    jmriRailroad.setRailroadDetails()

    allRsRosters = RollingStockAttributes()
    allRsRosters.addRoads()
    allRsRosters.addCarAar()
    allRsRosters.addCarLoads()
    allRsRosters.addCarKernels()
    allRsRosters.addLocoModels()
    allRsRosters.addLocoTypes()
    allRsRosters.addLocoConsist()

    updateDivisions = Divisionator()
    updateDivisions.parseDivisions()
    updateDivisions.addNewDivisions()




    newLocations = Locationator()
    updateDivisions.addDivisionToLocations()

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

    newInventory = RollingStockonator()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.makeTpRollingStockData()
    newInventory.newCars()
    newInventory.newLocos()

    updatedLocations.deleteOldLocations()

    PSE.CMX.save()
    PSE.EMX.save()
    PSE.OMX.save()

    return True

def updateJmriRollingingStock():
    """Mini controller to update only the rolling stock.
        Called by:
        Controller.Startup.updateJmriRollingingStock
        """

    resetTrains = BuiltTrainExport.FindTrain()
    resetTrains.getBuiltTrains()
    resetTrains.resetBuildTrains()

    try:
        PSE.closeTroublesomeWindows()

        PSE.CM.dispose()
        PSE.EM.dispose()

        allRsRosters = RollingStockAttributes()
        allRsRosters.addRoads()
        allRsRosters.addCarAar()
        allRsRosters.addCarLoads()
        allRsRosters.addCarKernels()
        allRsRosters.addLocoModels()
        allRsRosters.addLocoTypes()
        allRsRosters.addLocoConsist()

        newInventory = RollingStockonator()
        newInventory.getTpInventory()
        newInventory.splitTpList()
        newInventory.makeTpRollingStockData()
        newInventory.newCars()
        newInventory.newLocos()

        PSE.CMX.save()
        PSE.EMX.save()

        return True

    except:
        _psLog.warning('TrainPlayer data file(s) not found')
        return False


class SetupXML:
    """Make tweeks to Operations.xml here."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.SetupXML'

        self.OSU = PSE.JMRI.jmrit.operations.setup

        self.o2oConfig =  PSE.readConfigFile()
        self.TpRailroad = PSE.getTpRailroadJson('tpRailroadData')

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def addDetailsToConFig(self):
        """The optional railroad details from the TP Master Script are addad."""

        self.o2oConfig['JP'].update({'OR':self.TpRailroad['operatingRoad']})
        self.o2oConfig['JP'].update({'TR':self.TpRailroad['territory']})
        self.o2oConfig['JP'].update({'LO':self.TpRailroad['location']})
        self.o2oConfig['JP'].update({'YR':self.TpRailroad['year']})
        self.o2oConfig['JP'].update({'SC':self.TpRailroad['scale']})
        self.o2oConfig['JP'].update({'LN':self.TpRailroad['layoutName']})
        self.o2oConfig['JP'].update({'BD':self.TpRailroad['buildDate']})

        self.o2oConfig['CP'].update({'LN':self.TpRailroad['layoutName']})

        PSE.writeConfigFile(self.o2oConfig)
        self.o2oConfig =  PSE.readConfigFile()

        return

    def setRailroadDetails(self):

        _psLog.debug('setRailroadDetails')

    # Set the name
        layoutName = self.o2oConfig['JP']['LN']

        self.OSU.Setup.setRailroadName(layoutName)
    # Set the year
        rrYear = self.o2oConfig['JP']['YR']
        if rrYear:
            self.OSU.Setup.setYearModeled(rrYear)

        rrScale = self.o2oConfig['JP']['SC']
        if rrScale:
            self.OSU.Setup.setScale(self.o2oConfig['o2o']['SR'][rrScale.upper()])

        return

    def tweakOperationsXml(self):
        """Some of these are just favorites of mine."""

        _psLog.debug('tweakOperationsXml')

        self.OSU.Setup.setMainMenuEnabled(self.o2oConfig['o2o']['TO']['SME'])
        self.OSU.Setup.setCloseWindowOnSaveEnabled(self.o2oConfig['o2o']['TO']['CWS'])
        self.OSU.Setup.setBuildAggressive(self.o2oConfig['o2o']['TO']['SBA'])
        self.OSU.Setup.setStagingTrackImmediatelyAvail(self.o2oConfig['o2o']['TO']['SIA'])
        self.OSU.Setup.setCarTypes(self.o2oConfig['o2o']['TO']['SCT'])
        self.OSU.Setup.setStagingTryNormalBuildEnabled(self.o2oConfig['o2o']['TO']['TNB'])
        self.OSU.Setup.setManifestEditorEnabled(self.o2oConfig['o2o']['TO']['SME'])

        return

    def setReportMessageFormat(self):
        """Sets the default message format as defined in the configFile."""

        self.OSU.Setup.setPickupManifestMessageFormat(self.o2oConfig['o2o']['TO']['PUC'])
        self.OSU.Setup.setDropManifestMessageFormat(self.o2oConfig['o2o']['TO']['SOC'])
        self.OSU.Setup.setLocalManifestMessageFormat(self.o2oConfig['o2o']['TO']['MC'])
        self.OSU.Setup.setPickupEngineMessageFormat(self.o2oConfig['o2o']['TO']['PUL'])
        self.OSU.Setup.setDropEngineMessageFormat(self.o2oConfig['o2o']['TO']['SOL'])

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

        # fileName = 'tpRailroadData.json'
        # filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        # self.sourceData = PSE.loadJson(PSE.genericReadReport(filePath))

        self.sourceData = PSE.getTpRailroadJson('tpRailroadData')

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
            a = PSE.BUNDLE['ALERT: Staging and non-staging tracks at same location: '] + str(result)
            b = PSE.BUNDLE['JMRI does not allow staging and non-staging track types at the same location.']
            c = PSE.BUNDLE['No changes were made to your JMRI layout.']
            message = a + '\n' + b + '\n' + c + '\n'

            _psLog.critical('ALERT: Staging and non-staging tracks at same location: ' + str(result))

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


class RollingStockAttributes:
    """TCM - Temporary Context Manager.
        Nothing is removed from OperationsCarRoster.xml, only added to.
        """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.RollingStockAttributes'

        self.tpRailroadData = PSE.getTpRailroadJson('tpRailroadData')

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
        self.tpRailroadData = PSE.getTpRailroadJson('tpRailroadData')

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

        # currentLocations = PSE.getAllLocationNames()
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

        _psLog.debug('processLocations')

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
        """Deletes leftover tracks from unchanged locations."""

        for key in self.oldKeys:
            cTrackData = self.currentLocale['tracks'][key]
            trackType = self.o2oConfig['TR'][cTrackData[2]]
            location = PSE.LM.getLocationByName(cTrackData[0])
            try:
                track = location.getTrackByName(cTrackData[1], trackType)
                location.deleteTrack(track)
                track.dispose()
            except:
                print('Not found: ' + cTrackData[0] + ' ' + cTrackData[1])
        return

    def deleteOldLocations(self):
        """Delete locations which have no tracks."""

        for location in PSE.LM.getList():
            if not location.getTracksList():
                PSE.LM.deregister(location)
                location.dispose()

        return
class Divisionator:
    """All methods involving divisions."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Divisionator'
        self.tpRailroadData = PSE.getTpRailroadJson('tpRailroadData')

        self.tpDivisions = self.tpRailroadData['divisions'] # List of strings
        self.jmriDivisions = [] # list of strings
        for division in PSE.DM.getList():
            self.jmriDivisions.append(division)

        self.newDivisions = []
        self.obsoleteDivisions = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def parseDivisions(self):

        self.newDivisions = list(set(self.tpDivisions) - set(self.jmriDivisions))
        self.obsoleteDivisions = list(set(self.jmriDivisions) - set(self.tpDivisions))

        return

    def addNewDivisions(self):
        """ """

        if len(self.newDivisions) == 0:
            return

        PSE.DM.newDivision(PSE.BUNDLE['Unknown'])

        for division in self.newDivisions:
            PSE.DM.newDivision(division)

        return

    def addDivisionToLocations(self):
        """If there is only one division, add all locations to it, 
            otherwise divisions are set by the user.
            """

        soleDivision = self.jmriDivisions
        unknownDivision = self.jmriDivisions

        if len(unknownDivision) != 2: # one named division and Unknown
            return

        if unknownDivision[0].getName() == 'Unknown':
            unknownDivision.pop(1)
            soleDivision.pop(0)
        else:
            unknownDivision.pop(0)
            soleDivision.pop(1)

        for location in PSE.LM.getList():
            if location.getName() == PSE.BUNDLE['Unreported']:
                location.setDivision(unknownDivision[0])
            else:
                location.setDivision(soleDivision[0])
                
        return

class Locationator:

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Locationator'
        self.tpRailroadData = PSE.getTpRailroadJson('tpRailroadData')

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    # def addNewDivisions(self):
    #     """ """

    #     divisionList = self.tpRailroadData['divisions']

    #     if len(divisionList[0]) == 0:
    #         return

    #     PSE.DM.newDivision(PSE.BUNDLE['Unknown'])

    #     for division in divisionList:
    #         PSE.DM.newDivision(division)

    #     return

    # def addDivisionToLocations(self):
    #     """If there is only one division, add all locations to it, 
    #         otherwise divisions are set by the user.
    #         """

    #     soleDivision = PSE.DM.getList()
    #     unknownDivision = PSE.DM.getList()

    #     if len(unknownDivision) != 2: # one named division and Unknown
    #         return

    #     if unknownDivision[0].getName() == 'Unknown':
    #         unknownDivision.pop(1)
    #         soleDivision.pop(0)
    #     else:
    #         unknownDivision.pop(0)
    #         soleDivision.pop(1)

    #     for location in PSE.LM.getList():
    #         if location.getName() == PSE.BUNDLE['Unreported']:
    #             location.setDivision(unknownDivision[0])
    #         else:
    #             location.setDivision(soleDivision[0])
                
    #     return

    def newLocations(self):

        _psLog.debug('newLocations')

        for location in self.tpRailroadData['locations']:
            newLocation = PSE.LM.newLocation(location)
            if newLocation.getName() == PSE.BUNDLE['Unreported']:
                newLocation.setTrainDirections(0)

        return

    def newTracks(self):

        _psLog.debug('newTracks')

        for trackId, trackData in self.tpRailroadData['locales'].items():
            ModelEntities.makeNewTrack(trackId, trackData)

        return


class RollingStockonator:

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.RollingStockonator'

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
            if attribs['aar'] in self.o2oConfig['CC']:
                updatedCar.setCaboose(True)
            if attribs['aar'] in self.o2oConfig['PC']:
                updatedCar.setPassenger(True)
            updatedCar.setLength('40')
            updatedCar.setWeight('2')
            updatedCar.setColor('Red')

            shipLoadName = self.getLoadFromSchedule(attribs)
            updatedCar.setLoadName(shipLoadName)
            
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

    def getLoadFromSchedule(self, attribs):

        location = PSE.LM.getLocationByName(attribs['location'])
        track = location.getTrackByName(attribs['track'], 'Spur')

        try:
            jSchedule = track.getSchedule()
            jItem = jSchedule.getItemByType(attribs['aar'])
            return jItem.getShipLoadName()
        except:
            return attribs['load']
  
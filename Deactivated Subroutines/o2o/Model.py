# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""From tpRailroadData.json, a new rr is created and the xml files are seeded."""

from opsEntities import PSE
from Subroutines.o2o import ModelEntities
from Subroutines.o2o import BuiltTrainExport

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

FILE_LIST = ['OperationsTrainRoster.xml', 'OperationsRouteRoster.xml']

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Model')


def newJmriRailroad():
    """Mini controller to make a new JMRI railroad.
        tpRailroadData.json and TrainPlayer Report - Rolling Stock.txt
        are used as source files.
        Called by:
        Controller.StartUp.newJmriRailroad
        """

    tpLocaleData = TpLocaleculator()
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

    jmriRailroad = Initiator()
    jmriRailroad.o2oDetailsToConFig()
    jmriRailroad.setRailroadDetails()
    # jmriRailroad.tweakOperationsXml()
    jmriRailroad.setReportMessageFormat()

    allRsRosters = Attributator()
    allRsRosters.addRoads()
    allRsRosters.addCarAar()
    allRsRosters.addCarLoads()
    allRsRosters.addCarKernels()
    allRsRosters.addLocoModels()
    allRsRosters.addLocoTypes()
    allRsRosters.addLocoConsist()

    PSE.CMX.save()
    PSE.EMX.save()

    newLocations = Locationator()
    newLocations.getUpdatedLocale()
    newLocations.getNewLocations()
    newLocations.addNewLocations()

    newDivisions = Divisionator()
    newDivisions.parseDivisions()
    newDivisions.addNewDivisions()
    newDivisions.addDivisionToLocations()
    newDivisions.addUnreportedToUnknown()

    ModelEntities.newSchedules()

    newLocations.parseTracks()
    newLocations.addNewTracks()

    ModelEntities.setTrackLength()
    ModelEntities.addCarTypesToSpurs()

    newInventory = RStockulator()
    newInventory.makeNewTpRollingStockData()
    newInventory.parseTpRollingStock()
    newInventory.newJmriRs()

    # PSE.CMX.save()
    # PSE.EMX.save()
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

    tpLocaleTest = TpLocaleculator()
    tpLocaleTest.make()
    if tpLocaleTest.isValid():
        pass
    else:
        return False

    tpLocaleData = TpLocaleculator()
    tpLocaleData.make()
    if tpLocaleData.exists():
        pass
    else:
        return False

    resetTrains = BuiltTrainExport.FindTrain()
    resetTrains.getBuiltTrains()
    resetTrains.resetBuildTrains()

    PSE.closeTroublesomeWindows()

    PSE.SM.dispose()
    # PSE.CM.dispose()
    # PSE.EM.dispose()

    jmriRailroad = Initiator()
    jmriRailroad.o2oDetailsToConFig()
    jmriRailroad.setRailroadDetails()

    allRsRosters = Attributator()
    allRsRosters.addRoads()
    allRsRosters.addCarAar()
    allRsRosters.addCarLoads()
    allRsRosters.addCarKernels()
    allRsRosters.addLocoModels()
    allRsRosters.addLocoTypes()
    allRsRosters.addLocoConsist()

    updateDivisions = Divisionator()
    updateDivisions.parseDivisions()
    updateDivisions.removeObsoleteDivisions()
    updateDivisions.addNewDivisions()

    updatedLocations = Locationator()
    updatedLocations.getCurrentLocale()
    tpLocaleData.write()
    updatedLocations.getUpdatedLocale()

    updatedLocations.getNewLocations()
    updatedLocations.addNewLocations()

    updateDivisions.addDivisionToLocations()
    updateDivisions.addUnreportedToUnknown()

    ModelEntities.newSchedules()

    updatedLocations.parseTracks()
    updatedLocations.deleteOldTracks()
    updatedLocations.addNewTracks()
    updatedLocations.recastTracks()

    ModelEntities.setTrackLength()
    ModelEntities.addCarTypesToSpurs()

    newInventory = RStockulator()
    newInventory.getcurrentTpRsData()
    newInventory.makeNewTpRollingStockData()
    newInventory.parseTpRollingStock()
    newInventory.updateJmriRs()
    newInventory.deregisterOldRs()

    updatedLocations.deleteOldLocations()

    # PSE.CMX.save()
    # PSE.EMX.save()
    PSE.OMX.save()

    # tpLocaleData.make()
    # tpLocaleData.write()

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

        allRsRosters = Attributator()
        allRsRosters.addRoads()
        allRsRosters.addCarAar()
        allRsRosters.addCarLoads()
        allRsRosters.addCarKernels()
        allRsRosters.addLocoModels()
        allRsRosters.addLocoTypes()
        allRsRosters.addLocoConsist()

        newInventory = RStockulator()
        newInventory.getcurrentTpRsData()
        newInventory.makeNewTpRollingStockData()
        newInventory.parseTpRollingStock()
        newInventory.updateJmriRs()
        newInventory.deregisterOldRs()
        newInventory.newJmriRs()

        # PSE.CMX.save()
        # PSE.EMX.save()

        return True

    except:
        _psLog.warning('TrainPlayer data file(s) not found')
        return False


class TpLocaleculator:
    """Makes the tpLocaleData.json file."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.TpLocaleculator'

        self.sourceData = {}
        self.tpLocaleData = {}

        self.locationList = []

        return

    def getTpRrData(self):

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

        trackData = {}
        for id, data in self.sourceData['locales'].items():
            otherTrack = (data['location'], data['track'], data['type'])
            trackData[id] = otherTrack

        self.tpLocaleData['tracks'] = trackData

        return

    def exists(self):
        """Catches press of Update button before New button."""

        fileName = 'tpLocaleData.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        if PSE.JAVA_IO.File(targetPath).isFile():

            return True
        else:
            message = PSE.BUNDLE['Alert: Create a new JMRI layout first.']
            PSE.openOutputFrame(message)
            _psLog.critical('Alert: Create a new JMRI layout first.')

            return False

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
            PSE.openOutputFrame(message)

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
        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return


class Initiator:
    """Make tweeks to Operations.xml here."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Initiator'

        self.OSU = PSE.JMRI.jmrit.operations.setup

        self.o2oConfig =  PSE.readConfigFile()
        self.TpRailroad = PSE.getTpRailroadJson('tpRailroadData')

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def o2oDetailsToConFig(self):
        """Optional railroad details from the TrainPlayer layout are added to the config file."""

        self.o2oConfig['Main Script']['LD'].update({'OR':self.TpRailroad['operatingRoad']})
        self.o2oConfig['Main Script']['LD'].update({'TR':self.TpRailroad['territory']})
        self.o2oConfig['Main Script']['LD'].update({'LO':self.TpRailroad['location']})
        self.o2oConfig['Main Script']['LD'].update({'YR':self.TpRailroad['year']})
        self.o2oConfig['Main Script']['LD'].update({'SC':self.TpRailroad['scale']})
        self.o2oConfig['Main Script']['LD'].update({'LN':self.TpRailroad['layoutName']})
        self.o2oConfig['Main Script']['LD'].update({'BD':self.TpRailroad['buildDate']})

        PSE.writeConfigFile(self.o2oConfig)
        self.o2oConfig =  PSE.readConfigFile()

        return

    def setRailroadDetails(self):
        """Optional railroad details from the TrainPlayer layout are added to JMRI."""

        _psLog.debug('setRailroadDetails')

    # Set the name
        layoutName = self.o2oConfig['Main Script']['LD']['LN']

        self.OSU.Setup.setRailroadName(layoutName)
    # Set the year
        rrYear = self.o2oConfig['Main Script']['LD']['YR']
        if rrYear:
            self.OSU.Setup.setYearModeled(rrYear)

        rrScale = self.o2oConfig['Main Script']['LD']['SC']
        if rrScale:
            self.OSU.Setup.setScale(self.o2oConfig['Main Script']['SR'][rrScale.upper()])

        return

    # def tweakOperationsXml(self):
    #     """Some of these are just favorites of mine."""

    #     _psLog.debug('tweakOperationsXml')

    #     self.OSU.Setup.setMainMenuEnabled(self.o2oConfig['o2o']['TO']['SME'])
    #     self.OSU.Setup.setCloseWindowOnSaveEnabled(self.o2oConfig['o2o']['TO']['CWS'])
    #     self.OSU.Setup.setBuildAggressive(self.o2oConfig['o2o']['TO']['SBA'])
    #     self.OSU.Setup.setStagingTrackImmediatelyAvail(self.o2oConfig['o2o']['TO']['SIA'])
    #     self.OSU.Setup.setCarTypes(self.o2oConfig['o2o']['TO']['SCT'])
    #     self.OSU.Setup.setStagingTryNormalBuildEnabled(self.o2oConfig['o2o']['TO']['TNB'])
    #     self.OSU.Setup.setManifestEditorEnabled(self.o2oConfig['o2o']['TO']['SME'])

    #     return

    def setReportMessageFormat(self):
        """Sets the default message format as defined in the configFile."""

        self.OSU.Setup.setPickupManifestMessageFormat(self.o2oConfig['o2o']['RMF']['PUC'])
        self.OSU.Setup.setDropManifestMessageFormat(self.o2oConfig['o2o']['RMF']['SOC'])
        self.OSU.Setup.setLocalManifestMessageFormat(self.o2oConfig['o2o']['RMF']['MC'])
        self.OSU.Setup.setPickupEngineMessageFormat(self.o2oConfig['o2o']['RMF']['PUL'])
        self.OSU.Setup.setDropEngineMessageFormat(self.o2oConfig['o2o']['RMF']['SOL'])

        return


class Attributator:
    """Sets all the rolling stock attributes.
        TCM - Temporary Context Manager.
        Nothing is removed from OperationsCarRoster.xml, only added to.
        """

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Attributator'

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

        for xName in self.tpRailroadData['locoConsists']:
            PSE.ZM.newConsist(xName)

        return


class Locationator:
    """JMRI considers tracks to be a subset of a location.
        Locations and tracks are updated using Location Manager."""

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.Locationator'

        self.o2oConfig = PSE.readConfigFile('o2o')
        self.tpRailroadData = PSE.getTpRailroadJson('tpRailroadData')

        self.currentLocale = {'locations':{}, 'tracks':{}}
        self.updatedLocale = {}

        self.newLocations = []
        self.unchangedLocations = []
        self.renameLocations = []
        self.oldLocations = []

        self.oldKeys = []
        self.newKeys = []
        self.continuingKeys = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def getLocaleData(self):

        _psLog.debug('getLocaleData')

        fileName = 'tpLocaleData.json'
        filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        return PSE.loadJson(PSE.genericReadReport(filePath))

    def getCurrentLocale(self):
        """The current locale is the state of the JMRI date before the update button is pressed.
            self.currentLocale = the existing tpLocaleData.json
            """

        _psLog.debug('getCurrentLocale')

        self.currentLocale = self.getLocaleData()

        return

    def getUpdatedLocale(self):
        """The updated locale is the data in the TP exports that the JMRI data will be changed to.
            self.updatedLocale = a new tpLocaleData.json
            """

        _psLog.debug('getUpdatedLocale')

        self.updatedLocale = self.getLocaleData()

        return

    def getNewLocations(self):
        """A list of new location names to be added to JMRI."""

        currentLocations = [location for location in self.currentLocale['locations']]
        updatedLocations = [location for location in self.updatedLocale['locations']]

        self.newLocations = list(set(updatedLocations) - set(currentLocations))

        return

    def getUpdatedLocations(self):
        """A list of existing JMRI location names whose name has changed."""

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
            self.jmriDivisions.append(division.getName())

        self.newDivisions = []
        self.obsoleteDivisions = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def parseDivisions(self):

        self.newDivisions = list(set(self.tpDivisions) - set(self.jmriDivisions))
        self.obsoleteDivisions = list(set(self.jmriDivisions) - set(self.tpDivisions))

        return

    def removeObsoleteDivisions(self):

        if len(self.obsoleteDivisions) == 0:
            return

        for division in self.obsoleteDivisions:
            obsolete = PSE.DM.getDivisionByName(division)
            PSE.DM.deregister(obsolete)

        return

    def addNewDivisions(self):

        for division in self.newDivisions:
            PSE.DM.newDivision(division)

        return

    def addDivisionToLocations(self):
        """Edge case, if there is only one division, add all locations to it."""

        if PSE.DM.getNumberOfdivisions() != 1:
            return

        division = PSE.DM.getList()[0]

        for location in PSE.LM.getList():
            location.setDivision(division)
                
        return

    def addUnreportedToUnknown(self):
        """This method adds a division named Unknown.
            Add the location named Unreported to the division named Unknown.
            """

        location = PSE.LM.getLocationByName(PSE.BUNDLE['Unreported'])
        division = PSE.DM.newDivision(PSE.BUNDLE['Unknown'])

        location.setDivision(division)

        return


class RStockulator:

    def __init__(self):

        self.scriptName = SCRIPT_NAME + '.RStockulator'

        self.o2oConfig = PSE.readConfigFile('o2o')

        self.tpRollingStockFile = self.o2oConfig['RF']['TRR']
        self.tpInventory = []
        self.tpCars = {}
        self.tpLocos = {}

        self.jmriCars = PSE.CM.getList()
        self.jmriLocos = PSE.EM.getList()

        self.currentRsData = {}
        self.newRsData = {}

        self.newTpIds = []
        self.oldTpIds = []
        self.continuingTpIds = []

        print(self.scriptName + ' ' + str(SCRIPT_REV))

        return

    def getcurrentTpRsData(self):

        fileName = 'tpRollingStockData.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        self.currentRsData = PSE.loadJson(PSE.genericReadReport(targetPath))

        return

    def makeNewTpRollingStockData(self):
        """Makes a json LUT: TP road + TP Number : TP ID"""

        _psLog.debug('makeNewTpRollingStockData')

        self.getTpInventory()
        self.splitTpList()

        for item in self.tpInventory:
            try:
                line = item.split(';')
                name, number = ModelEntities.parseCarId(line[0])
                # self.newRsData[name + number] = line[7]
                self.newRsData[line[7]] = name + number
            except:
                _psLog.warning('Line not parsed: ' + item)
                pass

        fileName = 'tpRollingStockData.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        formattedRsFile = PSE.dumpJson(self.newRsData)
        PSE.genericWriteReport(targetPath, formattedRsFile)

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
                # self.tpLocos[line[0].replace(" ", "")] = {'model': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'consist': line[6]}
                self.tpLocos[line[7]] = {'model': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'consist': line[6], 'id': line[0]}
            else:
                # self.tpCars[line[0].replace(" ", "")] = {'type': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'kernel': line[6]}
                self.tpCars[line[7]] = {'type': line[1], 'aar': line[2], 'location': line[3], 'track': line[4], 'load': line[5], 'kernel': line[6], 'id': line[0]}

        return

    def parseTpRollingStock(self):
        """Makes 3 lists, continnuing, new and old rolling stock."""

        currentRsIds = []
        for id in self.currentRsData:
            currentRsIds.append(id)

        newRsIds = []
        for id in self.newRsData:
            newRsIds.append(id)

        self.continuingTpIds = list(set(currentRsIds).intersection(set(newRsIds)))
        self.newTpIds = list(set(newRsIds).difference(set(currentRsIds)))
        self.oldTpIds = list(set(currentRsIds).difference(set(newRsIds)))

        return

    def updateJmriRs(self):

        self.setGenericRsAttribs(self.continuingTpIds)

        return

    def newJmriRs(self):

        for id in self.newTpIds:
            newJmriId = self.newRsData[id]
            rsRoad, rsNumber = ModelEntities.parseCarId(newJmriId)

            try:
                self.tpCars[id]['aar']
                PSE.CM.newRS(rsRoad, rsNumber)
            except:
                pass

            try:
                self.tpLocos[id]['aar']
                PSE.EM.newRS(rsRoad, rsNumber)
            except:
                pass

        self.currentRsData = self.newRsData
        self.setGenericRsAttribs(self.newTpIds)
        self.setSpecificRsAttribs(self.newTpIds)

        return

    def setGenericRsAttribs(self, idList):
        """Used when updating rolling stock.
            Sets only the road name, number, kernal/consist, location, track and load.
            """

        _psLog.debug('setGenericRsAttribs')

        for id in idList:
            currentJmriId = self.currentRsData[id]
            if PSE.EM.getById(currentJmriId):
                newRsAttribs = self.tpLocos[id]
                rs = PSE.EM.getById(currentJmriId)
                rs.setConsist(PSE.ZM.getConsistByName(newRsAttribs['consist']))

            elif PSE.CM.getById(currentJmriId):
                newRsAttribs = self.tpCars[id]
                rs = PSE.CM.getById(currentJmriId)
                shipLoadName = self.getLoadFromSchedule(newRsAttribs)
                if shipLoadName:
                    rs.setLoadName(shipLoadName)
                rs.setKernel(PSE.KM.getKernelByName(newRsAttribs['kernel']))

            rsRoad, rsNumber = ModelEntities.parseCarId(newRsAttribs['id'])
            xLocation, xTrack = ModelEntities.getSetToLocationAndTrack(newRsAttribs['location'], newRsAttribs['track'])

            rs.setRoadName(rsRoad)
            rs.setNumber(rsNumber)
            rs.setLocation(xLocation, xTrack, True)
            rs.setTypeName(newRsAttribs['aar'])

        return

    def setSpecificRsAttribs(self, idList):
        """Used when adding new rolling stock.
            TP ID  : {'kernel': u'', 'type': u'box x23 prr', 'aar': u'XM', 'load': u'Empty', 'location': u'City', 'track': u'701'}
            """

        _psLog.debug('setSpecificRsAttribs')

        for id in idList:
            currentJmriId = self.currentRsData[id]
            if PSE.EM.getById(currentJmriId):
                newRsAttribs = self.tpLocos[id]
                newLoco = PSE.EM.getById(currentJmriId)
                newLoco.setLength('40')
                newLoco.setModel(newRsAttribs['model'][0:11])
            # Setting the model will automatically set the type
                newLoco.setWeight('2')
                newLoco.setColor('Black')
                newLoco.setConsist(PSE.ZM.getConsistByName(newRsAttribs['consist']))

            elif PSE.CM.getById(currentJmriId):
                newRsAttribs = self.tpCars[id]
                newCar = PSE.CM.getById(currentJmriId)
                if newRsAttribs['aar'] in self.o2oConfig['CC']:
                    newCar.setCaboose(True)
                if newRsAttribs['aar'] in self.o2oConfig['PC']:
                    newCar.setPassenger(True)
                newCar.setLength('40')
                newCar.setWeight('2')
                newCar.setColor('Red')

            else:
                print('Exclude rolling stock: ' + currentJmriId)

        return

    def getLoadFromSchedule(self, attribs):

        location = PSE.LM.getLocationByName(attribs['location'])
        track = location.getTrackByName(attribs['track'], None)

        if location.isStaging():
            return 'E'

        try:
            jSchedule = track.getSchedule()
            jItem = jSchedule.getItemByType(attribs['aar'])
            return jItem.getShipLoadName()
            
        except:
             return

    def deregisterOldRs(self):

        for id in self.oldTpIds:
            disposeJmriId = self.currentRsData[id]
            try:
                PSE.EM.deregister(PSE.EM.getById(disposeJmriId))
            except:
                PSE.CM.deregister(PSE.CM.getById(disposeJmriId))            

        return

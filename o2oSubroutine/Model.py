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

    deleteFiles()
    deleteRoads()
    deleteCarAar()

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

    PSE.EMX.save()
    PSE.CMX.save()
    PSE.LMX.save()
    PSE.OMX.save()

    PSE.EM.initialize()
    PSE.CM.initialize()
    PSE.LM.initialize()
    PSE.OM.initialize()

    return

def updateJmriRailroad():
    """Mini controller to update JMRI railroad.
        Does not change the Trains and Routes xml.
        Nothing fancy, new location, car and engine xml files are written,
        routes and trains are backed up and restored.
        Used by:
        Controller.StartUp.updateJmriRailroad
        """

    ModelEntities.closeTroublesomeWindows()

    PSE.TM.dispose()
    PSE.RM.dispose()
    PSE.LM.dispose()
    PSE.SM.dispose()
    PSE.CM.dispose()
    PSE.EM.dispose()

    copyFiles('', '.bak')

    deleteRoads()
    deleteCarAar()

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

    copyFiles('.bak', '')
    PSE.RMX.initialize()
    PSE.TMX.initialize()

    PSE.EM.initialize()
    PSE.CM.initialize()
    PSE.LM.initialize()
    PSE.RM.initialize()
    PSE.TM.initialize()

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

    PSE.EM.initialize()
    PSE.CM.initialize()

    return

def deleteFiles():

    for fileName in FILE_LIST:
        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        if PSE.JAVA_IO.File(targetFile).delete():
            _psLog.info('Deleted: ' + fileName)
        else:
            _psLog.warning('Not deleted: ' + fileName)

    return

def copyFiles(fromSuffix, toSuffix):
    """Utility to backup and restore any operations xml file.
        Specify a null suffix as ''
        This method is abstracted to backup and restore, which is not a feature of JMRI backup()
        """

    for fileName in FILE_LIST:
        fromName = fileName + fromSuffix
        toName = fileName + toSuffix

        sourceFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fromName)
        sourceFile = PSE.JAVA_IO.File(sourceFile).toPath()

        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', toName)
        targetFile = PSE.JAVA_IO.File(targetFile).toPath()

        try:
            PSE.JAVA_NIO.Files.copy(sourceFile, targetFile, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)
            _psLog.info('Copied: ' + fileName)
        except:
            _psLog.warning('Not copied: ' + fileName)

    return

def deleteRoads():
    """Deletes the 'stock' road names that are part of a new JMRI car xml."""

    _psLog.debug('deleteRoads')

    tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarRoads
    TCM = PSE.JMRI.InstanceManager.getDefault(tc)
    nameList = TCM.getNames()
    for xName in nameList:
        TCM.deleteName(xName)

    return

def deleteCarAar():
    """Deletes the 'stock' car types that are part of a new JMRI car xml."""

    _psLog.debug('deleteCarAar')

    tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarTypes
    TCM = PSE.JMRI.InstanceManager.getDefault(tc)
    nameList = TCM.getNames()
    for xName in nameList:
        TCM.deleteName(xName)

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
            # aar = unicode(aar, PSE.ENCODING)
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
            # xName = unicode(xName, PSE.ENCODING)
            PSE.KM.newKernel(xName)

        return

    def addLocoModels(self):
        """Add new engine models using the model names from the tpRailroadData.json file."""

        _psLog.debug('addLocoModels')

        tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineModels
        TCM = PSE.JMRI.InstanceManager.getDefault(tc)
        nameList = TCM.getNames()
        for xName in self.tpRailroadData['locoModels']:
            # xModel = unicode(xName[0], PSE.ENCODING)
            # xType = unicode(xName[1], PSE.ENCODING)
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
        nameList = TCM.getNames()
        for xName in self.tpRailroadData['locoTypes']:
            # xName = unicode(xName, PSE.ENCODING)
            TCM.addName(xName)

        return

    def addLocoConsist(self):
        """Add new JMRI consist names using the consist names from the tpRailroadData.json file."""

        _psLog.debug('addLocoConsist')

        nameList = PSE.ZM.getNameList()
        for xName in self.tpRailroadData['locoConsists']:
            # xName = unicode(xName, PSE.ENCODING)
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
        """Set spur length to spaces from TP.
            Deselect all types for spur tracks.
            """

        _psLog.debug('newTracks')

        for trackId, trackData in self.tpRailroadData['locales'].items():
            ModelEntities.makeNewTrack(trackId, trackData)

        return

    def newSchedules(self):
        """Creates new schedules from tpRailroadData.json [industries].
            The schedule name is the TP track label.
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

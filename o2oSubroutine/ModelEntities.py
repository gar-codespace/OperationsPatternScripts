# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelEntities'
SCRIPT_REV = 20220101

def writeWorkEvents(psWorkEvents):
    """Writes the o2o work events file"""

    workEventName = PatternScriptEntities.BUNDLE['o2o Work Events']

    jsonFileName = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + workEventName + '.json'
    jsonFile = PatternScriptEntities.dumpJson(psWorkEvents)
    PatternScriptEntities.genericWriteReport(jsonFileName, jsonFile)

    return

def getWorkEvents():
    """Gets the o2o work events file"""

    workEventName = PatternScriptEntities.BUNDLE['o2o Work Events']
    jsonFileName = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + workEventName + '.json'
    workEventList = PatternScriptEntities.genericReadReport(jsonFileName)
    jsonFile = PatternScriptEntities.loadJson(workEventList)

    return jsonFile

def getLoadType(type, load):

    tc = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarLoads
    TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)

    lt = 'O'
    loadType = TCM.getLoadType(type, load)
    if loadType == 'empty':
        lt = 'E'
    if loadType == 'load':
        lt = 'L'

    return lt

def getTpExport(fileName):
    """Generic file getter"""

    fullPath = "AppData\\Roaming\\TrainPlayer\\Reports\\" + fileName
    tpExportPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() + fullPath

    if PatternScriptEntities.JAVA_IO.File(tpExportPath).isFile():
        tpExport = PatternScriptEntities.genericReadReport(tpExportPath).split('\n')
        return tpExport
    else:
        return
    return

def addNewRs(rsAttribs):
    """rsAttribs format: RoadNumber, AAR, Location, Track, Loaded, Kernel, Type
    Note: TrainPlayer AAR is used as JMRI type name
    Note: TrainPlayer Type is used as JMRI engine model
    """

    roadName, roadNumber = parseCarId(rsAttribs[0])

    if rsAttribs[1].startswith('E') and rsAttribs[1] != 'ET':
        PatternScriptEntities.EM.newRS(roadName, roadNumber)
        rs = PatternScriptEntities.EM.getByRoadAndNumber(roadName, roadNumber)
        rs.setModel(rsAttribs[6])

    else:
        PatternScriptEntities.CM.newRS(roadName, roadNumber)
        rs = PatternScriptEntities.CM.getByRoadAndNumber(roadName, roadNumber)

    rs.setTypeName(rsAttribs[1])
    rs.setLength("40")
    rs.setColor("Color")
    if rsAttribs[1] == '1':
        rs.setLoad('L')

    return

def parseCarId(carId):
    """Splits a TP car id into a JMRI road name and number"""

    rsRoad = ''
    rsNumber = ''

    for character in carId:
        if character.isspace() or character == '-':
            continue
        if character.isdecimal():
            rsNumber += character
        else:
            rsRoad += character

    return rsRoad, rsNumber

def getSetToLocationAndTrack(locationName, trackName):
    """Called by:
        ModelNew.NewRollingStock.newCars
        ModelNew.NewRollingStock.newLocos
        """

    try:
        location = PatternScriptEntities.LM.getLocationByName(locationName)
        track = location.getTrackByName(trackName, None)
        return location, track
    except:
        print('Not found: ', location, track)
        return None, None

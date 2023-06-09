# coding=utf-8
# © 2023 Greg Ritacco

"""o2o"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.o2o.ModelEntities')


"""o2o.Model and o2o.ModelWorkEvents"""


def getTpRailroadJson(reportName):
    """
    Any of the TP exports imported into JMRI as a json file:
    tpRailroadData
    tpRollingStockData
    tpLocaleData
    """

    fileName = reportName + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

    if not PSE.JAVA_IO.File(targetPath).isFile():
        _psLog.info(fileName + '.json not found')
        return {}

    PSE.JAVA_IO.File(targetPath).isFile()
    report = PSE.genericReadReport(targetPath)
    tpReport = PSE.loadJson(report)

    _psLog.info(fileName + ': OK')

    return tpReport

def getCurrentRrData():
    """
    Directly retrieve the current RR's data from the JMRI XML.
    """

    currentRrData = {}

    locales = {}
    locations = []
    for location in PSE.LM.getLocationsByNameList():
        locations.append(location.getName())
        locale = {}
        for track in location.getTracksList():
            locale['location'] = location.getName()
            locale['track'] = track.getName()
            locale['type'] = track.getTrackType()
            locale['capacity'] = track.getLength()
            locales[track.getId()] = locale

    currentRrData['locations'] = locations
    currentRrData['locales'] = locales

    return currentRrData


"""o2o.ModelWorkEvents and o2o.BuiltTrainExport"""


def tpDirectoryExists():
    """Checks for the Reports folder in TraipPlayer."""

    tpDirectory = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getHomePath(), 'AppData', 'Roaming', 'TrainPlayer', 'Reports')

    if PSE.JAVA_IO.File(tpDirectory).isDirectory():
        _psLog.info('TrainPlayer destination directory OK')
        return True
    else:
        _psLog.warning('TrainPlayer Reports destination directory not found')
        print('TrainPlayer Reports destination directory not found')
        return


"""o2o.Model"""


def addCarTypesToSpurs():
    """Checks the car types check box for car types used at each spur"""

    _psLog.debug('addCarTypesToSpurs')

    industries = getTpRailroadJson('tpRailroadData')['industries']
    deselectCarTypes(industries)
    selectCarTypes(industries)

    return

def deselectCarTypes(industries):
    """
    For each track in industries, deselect all the RS types,
    Called by:
    Model.UpdateLocationsAndTracks.addCarTypesToSpurs
    """

    for id, industry in industries.items():
        location = PSE.LM.getLocationByName(industry['a-location'])
        track = location.getTrackByName(industry['b-track'], None)
        for typeName in track.getTypeNames():
            track.deleteTypeName(typeName)

    return

def selectCarTypes(industries):
    """
    Select just the RS types used by that track, leaving unused types deselected.
    Called by:
    Model.UpdateLocationsAndTracks.addCarTypesToSpurs
    """

    for id, industry in industries.items():
        track = PSE.LM.getLocationByName(industry['a-location']).getTrackByName(industry['b-track'], None)
        for schedule, details in industry['c-schedule'].items():
            for detail in details:
                track.addTypeName(detail[0])

    return

def getSetToLocationAndTrack(locationName, trackName):
    """
    Called by:
    ModelNew.NewRollingStock.newCars
    ModelNew.NewRollingStock.newLocos
    """

    try:
        location = PSE.LM.getLocationByName(locationName)
        track = location.getTrackByName(trackName, None)
        return location, track
    except:
        print('Location and track not found: ', locationName, trackName)
        return None, None

def setTrackAttribs(trackData):
    """
    Mini controller to set the attributes for each track,
    based on TrainPlayer track type.
    Called by:
    """

    if trackData['type'] == 'industry':
        setTrackTypeIndustry(trackData)

    if trackData['type'] == 'interchange':
        setTrackTypeInterchange(trackData)

    if trackData['type'] == 'staging':
        setTrackTypeStaging(trackData)

    if trackData['type'] == 'class yard':
        setTrackTypeClassYard(trackData)

    if trackData['type'] == 'XO reserved':
        setTrackTypeXoReserved(trackData)

    return

def setTrackTypeIndustry(trackData):
    """
    Settings for TP 'industry' track types.
    Called by:
    setTrackAttribs
    """

    location = PSE.LM.getLocationByName(trackData['location'])
    track = location.getTrackByName(trackData['track'], None)

    track.setLength(trackData['spurLength'])
    track.setSchedule(PSE.SM.getScheduleByName(trackData['label']))

    return

def setTrackTypeInterchange(trackData):
    """
    Settings for TP 'interchange' track types.
    Select all car and loco types.
    Called by:
    setTrackAttribs
    """

    location = PSE.LM.getLocationByName(trackData['location'])
    track = location.getTrackByName(trackData['track'], None)
    track.setLength(trackData['spurLength'])
    for type in track.getTypeNames():
        track.addTypeName(type)

    return

def setTrackTypeStaging(trackData):
    """
    Settings for TP 'staging' track types.
    Called by:
    setTrackAttribs
    """

    o2oConfig =  PSE.readConfigFile('o2o')

    location = PSE.LM.getLocationByName(trackData['location'])
    track = location.getTrackByName(trackData['track'], None)
    track.setLength(trackData['spurLength'])

    track.setAddCustomLoadsAnySpurEnabled(o2oConfig['SM']['SCL'])
    track.setRemoveCustomLoadsEnabled(o2oConfig['SM']['RCL'])
    track.setLoadEmptyEnabled(o2oConfig['SM']['LEE'])

    return

def setTrackTypeClassYard(trackData):
    """
    Settings for TP 'class yard' track types.
    Called by:
    setTrackAttribs
    """

    location = PSE.LM.getLocationByName(trackData['location'])
    track = location.getTrackByName(trackData['track'], None)
    track.setLength(trackData['spurLength'])

    return

def setTrackTypeXoReserved(trackData):
    """
    Settings for TP 'XO reserved' track types.
    XO tracks are spurs with all train directions turned off.
    All car types are selected.
    Called by:
    setTrackAttribs
    """

    track = setTrackTypeIndustry(trackData)
    track.setLength(trackData['spurLength'])
    track.setTrainDirections(0)
    for type in track.getTypeNames():
        track.addTypeName(type)

    return


"""o2o.ModelWorkEvents"""


def getWorkEvents():
    """
    Gets the o2o work events file
    Called by:
    ModelWorkEvents.ConvertPtMergedForm.getWorkEvents
    ModelWorkEvents.o2oWorkEvents.getWorkEvents
    """

    reportName = PSE.BUNDLE['o2o Work Events']
    fileName = reportName + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    workEventList = PSE.genericReadReport(targetPath)
    jsonFile = PSE.loadJson(workEventList)

    return jsonFile


"""o2o.ModelImport"""


def getTpExport(fileName):
    """
    Generic file getter, fileName includes .txt
    Called by:
    ModelImport.TrainPlayerImporter.getTpReportFiles
    """

    targetPath = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getHomePath(), 'AppData', 'Roaming', 'TrainPlayer', 'Reports', fileName)

    if PSE.JAVA_IO.File(targetPath).isFile():
        tpExport = PSE.genericReadReport(targetPath).split('\n')
        return tpExport
    else:
        return False

def parseCarId(carId):
    """
    Splits a TP car id into a JMRI road name and number
    Called by:
    ModelImport.TrainPlayerImporter.getAllTpRoads
    ModelNew.NewRollingStock.makeTpRollingStockData
    ModelNew.NewRollingStock.newCars
    ModelNew.NewRollingStock.newLocos
    """

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

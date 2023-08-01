# coding=utf-8
# © 2023 Greg Ritacco

"""
Support methods for o2o Model* level modules.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.o2o.ModelEntities')

def getTpRailroadJson(reportName):
    """
    Generic json getter even though tpRailroadData is the only file retrieved.
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
    format: "1": {"capacity": "12", "label": "FH", "location": "Fulton Terminal", "track": "Freight House", "type": "industry"},
    """

    currentRrData = {}
    locations = []
    locales = {}
    for location in PSE.LM.getLocationsByNameList():
        locations.append(location.getName())
        for track in location.getTracksList():
            locale = {}
            locale['location'] = location.getName()
            locale['track'] = track.getName()
            locale['type'] = track.getTrackType()
            locale['capacity'] = track.getLength()

            trackId = getTrackId(track.getComment())
            locales[trackId] = locale

    currentRrData['locations'] = locations
    currentRrData['locales'] = locales

    return currentRrData

def getTrackId(trackComment):
    """
    Gets the TrainPlayer trackID from the JMRI track comment.
    ID must be an integer.
    """

    try:
        trackId = trackComment.split(':')
        trackId = int(trackId[1])
    except:
        trackId = 999

    return str(trackId)
    
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


def addTypesToTracks():
    """
    Depricated
    """


    tc = PSE.JMRI.jmrit.operations.rollingstock.cars.CarTypes
    TCM = PSE.JMRI.InstanceManager.getDefault(tc)
    typeList = TCM.getNames()

    tc = PSE.JMRI.jmrit.operations.rollingstock.engines.EngineTypes
    TCM = PSE.JMRI.InstanceManager.getDefault(tc)

    typeList += TCM.getNames()

    for location in PSE.LM.getList():
        for type in typeList:
            location.addTypeName(type)      

    for track in PSE.getAllTracks():
        for type in typeList:
            track.addTypeName(type)

    return

def deselectCarTypesAtSpurs():
    """
    For each track in industries, deselect all the RS types,
    Called by:
    Model.UpdateLocationsAndTracks.addCarTypesToSpurs
    """

    spurs = getTpRailroadJson('tpRailroadData')['LocationRoster_spurs']

    for _, spur in spurs.items():
        location = PSE.LM.getLocationByName(spur['a-location'])
        track = location.getTrackByName(spur['b-track'], None)

        for typeName in track.getTypeNames():
            track.deleteTypeName(typeName)

    return

def selectCarTypesAtSpurs():
    """
    Select just the RS types used by that track, leaving unused types deselected.
    Called by:
    Model.UpdateLocationsAndTracks.addCarTypesToSpurs
    """

    industries = getTpRailroadJson('tpRailroadData')['LocationRoster_spurs']

    for _, industry in industries.items():
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
        print('Exception at: o2o.ModelEntities.getSetToLocationAndTrack')
        print('Location and track not found: ', locationName, trackName)
        return None, None


"""o2o.ModelWorkEvents"""


def getWorkEvents():
    """
    Gets the o2o work events file
    Called by:
    ModelWorkEvents.ConvertPtMergedForm.getWorkEvents
    ModelWorkEvents.o2oWorkEvents.getWorkEvents
    """

    reportName = PSE.getBundleItem('o2o Work Events')

    fileName = reportName + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    workEventList = PSE.genericReadReport(targetPath)
    jsonFile = PSE.loadJson(workEventList)

    return jsonFile


"""o2o.ModelImport"""


def getTpExport(fileName):
    """
    Generic file getter, fileName includes .txt
    Returns the text file as a list, each line is an element
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

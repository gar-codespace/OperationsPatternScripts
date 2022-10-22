# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE
import apps
import jmri.jmrit
import jmri.util.swing

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelEntities'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.o2o.ModelEntities')

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

def selectCarTypes(id, industry):
    """Used by:
        Model.NewLocationsAndTracks.addCarTypesToSpurs
        Model.UpdateLocationsAndTracks.addCarTypesToSpurs
        """

    track = PSE.LM.getLocationByName(industry['location']).getTrackByName(industry['track'], None)
    track.addTypeName(industry['type'])

    return

# def setNonSpurTrackLength():
#     """All non spur tracks length set to number of cars occupying track.
#         Used by:
#         Model.newJmriRailroad
#         Model.updateJmriRailroad
#         """
#
#     trackList = PSE.getAllTracks()
#     for track in trackList:
#         if track.getTrackType() == 'Spur':
#             continue
#         rsTotal = track.getNumberCars() + track.getNumberEngines()
#         if rsTotal == 0:
#             rsTotal = 1
#         newTrackLength = rsTotal * PSE.readConfigFile('o2o')['DL']
#         track.setLength(newTrackLength)
#         if track.getName() == '~':
#             track.setLength(1000)
#
#     return

# def deleteAllSchedules():
#     """Used by:
#         Model.UpdateLocationsAndTracks
#         """
#
#     PSE.SM.dispose()
#
#     return

def makeNewSchedule(id, industry):
    """Used by:
        Model.NewLocationsAndTracks.newSchedules
        Model.UpdateLocationsAndTracks
        """

    scheduleLineItem = industry['schedule']
    schedule = PSE.SM.newSchedule(scheduleLineItem[0])
    scheduleItem = schedule.addItem(scheduleLineItem[1])
    scheduleItem.setReceiveLoadName(scheduleLineItem[2])
    scheduleItem.setShipLoadName(scheduleLineItem[3])

    return

def makeNewTrack(trackId, trackData):
    """Set spur length to 'spaces' from TP.
        Deselect all types for spur tracks.
        Used by:
        Model.NewLocationsAndTracks.newLocations
        Model.UpdateLocationsAndTracks.addNewTracks
        """

    _psLog.debug('makeNewTrack')

    typeRubric = PSE.readConfigFile('o2o')['TR']
    jmriTrackType = typeRubric[trackData['type']]

    loc = PSE.LM.getLocationByName(trackData['location'])
    xTrack = loc.addTrack(trackData['track'], jmriTrackType)
    # xTrack.setComment(trackId)

    if trackData['type'] == 'industry':
        trackLength = int(trackData['capacity']) * PSE.readConfigFile('o2o')['DL']
        xTrack.setLength(trackLength)
        xTrack.setSchedule(PSE.SM.getScheduleByName(trackData['label']))
        for typeName in loc.getTypeNames():
            xTrack.deleteTypeName(typeName)
    if trackData['type'] == 'staging':
        tweakStagingTracks(xTrack)
    if trackData['type'] == 'XO reserved':
        xTrack.setTrainDirections(0)

    return

def tweakStagingTracks(track):
    """Tweak default settings for staging Tracks here
        Used by:
        makeNewTrack
        """

    o2oConfig =  PSE.readConfigFile('o2o')

    track.setAddCustomLoadsAnySpurEnabled(o2oConfig['SM']['SCL'])
    track.setRemoveCustomLoadsEnabled(o2oConfig['SM']['RCL'])
    track.setLoadEmptyEnabled(o2oConfig['SM']['LEE'])

    return

# def getTpTrackByTpId(tpTrackId):
#
#     importedRailroad = getTpRailroadData()
#     trackData = importedRailroad['locales'][tpTrackId]
#     location = PSE.LM.getLocationByName(trackData['location'])
#     track = location.getTrackByName(trackData['track'], None)
#
#     return track

# def getJmriTracksByTpId():
#
#     jmriTracks = {}
#     for location in PSE.LM.getLocationsByNameList():
#         for track in location.getTracksList():
#             jmriTracks[track.getComment()] = (location.getName(), track.getName())
#
#     return jmriTracks

def getWorkEvents():
    """Gets the o2o work events file
        Used by:
        ModelWorkEvents.ConvertPtMergedForm.getWorkEvents
        ModelWorkEvents.o2oWorkEvents.getWorkEvents
        """

    reportName = PSE.BUNDLE['o2o Work Events']
    fileName = reportName + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    workEventList = PSE.genericReadReport(targetPath)
    jsonFile = PSE.loadJson(workEventList)

    return jsonFile

def getTpExport(fileName):
    """Generic file getter, fileName includes .txt
        Used by:
        ModelImport.TrainPlayerImporter.getTpReportFiles
        """

    targetPath = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getHomePath(), 'AppData', 'Roaming', 'TrainPlayer', 'Reports', fileName)

    if PSE.JAVA_IO.File(targetPath).isFile():
        tpExport = PSE.genericReadReport(targetPath).split('\n')
        return tpExport
    else:
        return False

def parseCarId(carId):
    """Splits a TP car id into a JMRI road name and number
        Used by:
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

def getSetToLocationAndTrack(locationName, trackName):
    """Used by:
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

def closeTroublesomeWindows():
    """Close all the 'Troublesome' windows when the New JMRI Railroad button is pressed.
        Used by:
        o2oSubroutine.Model.newJmriRailroad
        o2oSubroutine.Model.updateJmriRailroad
        """

    for frameName in PSE.JMRI.util.JmriJFrame.getFrameList():
        if not 'JmriJFrame' in frameName.__str__():
            frameName.dispose()

    return

def getTpRailroadData():
    """Add error handling"""

    tpRailroad = []

    reportName = 'tpRailroadData'
    fileName = reportName + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

    try:
        PSE.JAVA_IO.File(targetPath).isFile()
        _psLog.info('tpRailroadData.json OK')
    except:
        _psLog.warning('tpRailroadData.json not found')
        return

    report = PSE.genericReadReport(targetPath)
    tpRailroad = PSE.loadJson(report)

    return tpRailroad

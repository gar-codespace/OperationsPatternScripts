# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelEntities'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('PS.TP.ModelNew')


def selectCarTypes(id, industry):
    """Used by:
        Model.NewLocationsAndTracks.addCarTypesToSpurs
        Model.UpdateLocationsAndTracks.addCarTypesToSpurs
        """

    track = PSE.LM.getLocationByName(industry['location']).getTrackByName(industry['track'], None)
    track.addTypeName(industry['type'])

    return

def setNonSpurTrackLength():
    """All non spur tracks length set to number of cars occupying track.
        Move default multiplier to the config file
        Used by:
        Model.newJmriRailroad
        Model.updateJmriRailroad
        """

    trackList = PSE.getAllTracks()
    for track in trackList:
        if track.getTrackType() == 'Spur':
            continue
        rsTotal = track.getNumberCars() + track.getNumberEngines()
        if rsTotal == 0:
            rsTotal = 1
        newTrackLength = rsTotal * 44
        track.setLength(newTrackLength)

    return

def makeNewSchedule(id, industry):
    """Used by:
        Model.NewLocationsAndTracks.newSchedules
        """

    tc = PSE.JMRI.jmrit.operations.locations.schedules.ScheduleManager
    TCM = PSE.JMRI.InstanceManager.getDefault(tc)

    scheduleLineItem = industry['schedule']
    schedule = TCM.newSchedule(scheduleLineItem[0])
    scheduleItem = schedule.addItem(scheduleLineItem[1])
    scheduleItem.setReceiveLoadName(scheduleLineItem[2])
    scheduleItem.setShipLoadName(scheduleLineItem[3])

    return

def makeNewTrack(trackId, trackData):
    """Set spur length to spaces from TP
        Deselect all types for spur tracks
        Used by:
        Model.NewLocationsAndTracks.newLocations
        Model.UpdateLocationsAndTracks.addNewTracks
        Model.UpdateLocationsAndTracks.updateContinuingTracks
        """

    tc = PSE.JMRI.jmrit.operations.locations.schedules.ScheduleManager
    TCM = PSE.JMRI.InstanceManager.getDefault(tc)

    loc = PSE.LM.getLocationByName(trackData['location'])
    xTrack = loc.addTrack(trackData['track'], trackData['type'])
    xTrack.setComment(trackId)
    trackLength = int(trackData['capacity']) * 44
    xTrack.setLength(trackLength)
    _psLog.debug('deselectCarTypesForSpurs')
    if trackData['type'] == 'Spur':
        xTrack.setSchedule(TCM.getScheduleByName(trackData['label']))
        for typeName in loc.getTypeNames():
            xTrack.deleteTypeName(typeName)
    if trackData['type'] == 'Staging':
        tweakStagingTracks(xTrack)

    return

def tweakStagingTracks(track):
    """Tweak default settings for staging Tracks here
        Used by:
        makeNewTrack
        """

    o2oConfig =  PSE.readConfigFile('o2o')

    track.setAddCustomLoadsAnySpurEnabled(o2oConfig['SCL'])
    track.setRemoveCustomLoadsEnabled(o2oConfig['RCL'])
    track.setLoadEmptyEnabled(o2oConfig['LEE'])

    return

def getTpTrackByTpId(tpTrackId):

    importedRailroad = getTpRailroadData()
    trackData = importedRailroad['locales'][tpTrackId]
    location = PSE.LM.getLocationByName(trackData['location'])
    track = location.getTrackByName(trackData['track'], None)

    return track

def getJmriTracksByTpId():

    jmriTracks = {}
    for location in PSE.LM.getLocationsByNameList():
        for track in location.getTracksList():
            jmriTracks[track.getComment()] = (location.getName(), track.getName())

    return jmriTracks

def getWorkEvents():
    """Gets the o2o work events file
        Used by:
        ModelWorkEvents.ConvertPtMergedForm.getWorkEvents
        ModelWorkEvents.o2oWorkEvents.getWorkEvents
        """

    reportName = PSE.BUNDLE['o2o Work Events']
    fileName = reportName + '.json'
    targetDir = PSE.PROFILE_PATH + '\\operations\\jsonManifests'
    targetPath = PSE.OS_Path.join(targetDir, fileName)

    workEventList = PSE.genericReadReport(targetPath)
    jsonFile = PSE.loadJson(workEventList)

    return jsonFile

def getTpExport(fileName):
    """Generic file getter, fileName includes .txt
        Used by:
        ModelImport.TrainPlayerImporter.getTpReportFiles
        """

    targetDir = PSE.JMRI.util.FileUtil.getHomePath() + '\\AppData\\Roaming\\TrainPlayer\\Reports'
    targetPath = PSE.OS_Path.join(targetDir, fileName)

    if PSE.JAVA_IO.File(targetPath).isFile():
        tpExport = PSE.genericReadReport(targetPath).split('\n')
        return tpExport
    else:
        return
    return

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
        print('Not found: ', locationName, trackName)
        return None, None

def closeTroublesomeWindows():
    """Close all the 'Troublesome' windows when the New JMRI Railroad button is pressed.
        Lazy work around, figure this our for real later.
        """

    frames = ['JMRI System Console', 'PanelPro', 'Pattern Scripts']

    for frameName in PSE.JMRI.util.JmriJFrame.getFrameList():
        frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
        if not frame.getTitle() in frames:
            frame.dispose()

    return

def getTpRailroadData():
    """Add error handling"""

    tpRailroad = []

    reportName = 'tpRailroadData'
    fileName = reportName + '.json'
    targetDir = PSE.PROFILE_PATH + '\\operations'
    targetPath = PSE.OS_Path.join(targetDir, fileName)

    try:
        PSE.JAVA_IO.File(targetPath).isFile()
        _psLog.info('tpRailroadData.json OK')
    except:
        _psLog.warning('tpRailroadData.json not found')
        return

    report = PSE.genericReadReport(targetPath)
    tpRailroad = PSE.loadJson(report)

    return tpRailroad

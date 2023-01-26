# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

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

def deselectCarTypes(industries):
    """For each track in industries, deselect all the RS types,
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
    """Select just the RS types used by that track, leaving unused types deselected.
        Called by:
        Model.UpdateLocationsAndTracks.addCarTypesToSpurs
        """

    for id, industry in industries.items():
        track = PSE.LM.getLocationByName(industry['a-location']).getTrackByName(industry['b-track'], None)
        for schedule, details in industry['c-schedule'].items():
            for detail in details:
                track.addTypeName(detail[0])

    return

def setTrackLength():
    """Set an existing tracks length."""

    _psLog.debug('setTrackLength')

    o2oConfig = PSE.readConfigFile('o2o')
    tpRailroadData = PSE.getTpRailroadJson('tpRailroadData')

    for id, trackData in tpRailroadData['locales'].items():
        location = PSE.LM.getLocationByName(trackData['location'])
        trackType = o2oConfig['TR'][trackData['type']]
        track = location.getTrackByName(trackData['track'], trackType)

        trackLength = int(trackData['capacity']) * o2oConfig['DL']
        track.setLength(trackLength)

    return

def newSchedules():
    """Write the industry schedules.
        viaIn and viaOut are not being used.
        """

    tpIndustries = PSE.getTpRailroadJson('tpRailroadData')['industries']

    for id, industry in tpIndustries.items():
        schedulesPerIndustry = industry['c-schedule']
        for scheduleName, scheduleItems in schedulesPerIndustry.items():
            schedule = PSE.SM.newSchedule(scheduleName)
            for parsedItem in parseSchedules(scheduleItems):
                scheduleItem = schedule.addItem(parsedItem[0])
                scheduleItem.setReceiveLoadName(parsedItem[1])
                scheduleItem.setShipLoadName(parsedItem[2])
                scheduleItem.setDestination(PSE.LM.getLocationByName(parsedItem[3]))

    return

def parseSchedules(scheduleItems):
    """For all schedules, replace Null with Empty,
        A duplicate is two TP/Industries rows with the same aar and the same ship/recieve.
        ModelImport.TrainPlayerImporter.processFileHeaders.self.tpIndustries.sort() or this won't work.
        scheduleItem: aarName[0], receiveLoad[1], shipload[2], stagingName[3], viaIn[4], viaOut[5]
        """

    parsedItems = []
# Find ship/receive duplicates
    dupes = []
    for item in scheduleItems:
        rAar = item[0]
        rLoad = item[1]
        sLoad = item[2]
        for lookUp in scheduleItems:
            if rAar == lookUp[0] and rLoad == lookUp[2] and sLoad == lookUp[1]:
                dupes.append(item)

# Merge duplicates
    merged = [item for item in dupes if not item[1]]

# Add duplicates to the schedule
    for item in merged:
        parsedItems.append([item[0], item[2], item[2], item[3], item[4], item[5]])

# Find the singles
    singles = [item for item in scheduleItems if item not in dupes]

# Add singles to the schedule
    for item in singles:
        if not item[1]:
            parsedItems.append([item[0], 'Empty', item[2], item[3], item[4], item[5]])
        else:
            parsedItems.append([item[0], item[1], 'Empty', item[3], item[4], item[5]])

    return parsedItems

def addCarTypesToSpurs():
    """Checks the car types check box for car types used at each spur"""

    _psLog.debug('addCarTypesToSpurs')

    industries = PSE.getTpRailroadJson('tpRailroadData')['industries']
    deselectCarTypes(industries)
    selectCarTypes(industries)

    return

def makeNewTrack(trackId, trackData):
    """Set spur length to 'spaces' from TP.
        Deselect all types for spur tracks.
        Called by:
        Model.Locationator.newLocations
        Model.UpdateLocationsAndTracks.addNewTracks
        """

    _psLog.debug('makeNewTrack')

    o2oConfig = PSE.readConfigFile('o2o')
    jmriTrackType = o2oConfig['TR'][trackData['type']]

    location = PSE.LM.getLocationByName(trackData['location'])
    location.addTrack(trackData['track'], jmriTrackType)

    setTrackAttribs(trackData)

    return

def setTrackAttribs(trackData):
    """Mini controller to set the attributes for each track,
        based on TrainPlayer track type.
        Called by:
        makeNewTrack
        Model.UpdateLocationsAndTracks.updateTrackParams
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
    """Settings for TP 'industry' track types.
        Called by:
        setTrackAttribs
        """

    location = PSE.LM.getLocationByName(trackData['location'])
    track = location.getTrackByName(trackData['track'], None)

    track.setSchedule(PSE.SM.getScheduleByName(trackData['label']))

    return track

def setTrackTypeInterchange(trackData):
    """Settings for TP 'interchange' track types.
        Select all car and loco types.
        Called by:
        setTrackAttribs
        """

    location = PSE.LM.getLocationByName(trackData['location'])
    track = location.getTrackByName(trackData['track'], None)
    for type in track.getTypeNames():
        track.addTypeName(type)

    return

def setTrackTypeStaging(trackData):
    """Settings for TP 'staging' track types.
        Called by:
        setTrackAttribs
        """

    o2oConfig =  PSE.readConfigFile('o2o')

    location = PSE.LM.getLocationByName(trackData['location'])
    track = location.getTrackByName(trackData['track'], None)

    track.setAddCustomLoadsAnySpurEnabled(o2oConfig['SM']['SCL'])
    track.setRemoveCustomLoadsEnabled(o2oConfig['SM']['RCL'])
    track.setLoadEmptyEnabled(o2oConfig['SM']['LEE'])

    return track

def setTrackTypeClassYard(trackData):
    """Settings for TP 'class yard' track types.
        Called by:
        setTrackAttribs
        """

    return

def setTrackTypeXoReserved(trackData):
    """Settings for TP 'XO reserved' track types.
        XO tracks are spurs with all train directions turned off.
        All car types are selected.
        Called by:
        setTrackAttribs
        """

    track = setTrackTypeIndustry(trackData)
    track.setTrainDirections(0)
    for type in track.getTypeNames():
        track.addTypeName(type)

    return track

def getWorkEvents():
    """Gets the o2o work events file
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

def getTpExport(fileName):
    """Generic file getter, fileName includes .txt
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
    """Splits a TP car id into a JMRI road name and number
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

def getSetToLocationAndTrack(locationName, trackName):
    """Called by:
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
        
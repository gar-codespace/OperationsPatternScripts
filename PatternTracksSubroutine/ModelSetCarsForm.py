# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Process methods for the Set Cars Form for Track X form"""

# import logging
# from codecs import open as codecsOpen
# from json import loads as jsonLoads, dumps as jsonDumps

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ModelEntities
from TrainPlayerSubroutine import PatternTracksExport

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ModelSetCarsForm'
SCRIPT_REV = 20220101
psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.ModelSetCarsForm')

def testValidityOfForm(setCarsForm, textBoxEntry):

    psLog.debug('ModelSetCarsForm.testValidityOfForm')

    locoCount = len(setCarsForm['locations'][0]['tracks'][0]['locos'])
    carCount = len(setCarsForm['locations'][0]['tracks'][0]['cars'])

    if len(textBoxEntry) == locoCount + carCount:
        return True
    else:
        psLog.critical('mismatched input list and car roster lengths')
        return False

def setRsToTrack(setCarsForm, textBoxEntry):

    psLog.debug('ModelSetCarsForm.setRsToTrack')

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), PatternScriptEntities.ENCODING))

    i = 0
    setCount = 0

    allTracksAtLoc = ModelEntities.getTracksByLocation(None)
    fromTrack = unicode(setCarsForm['locations'][0]['tracks'][0]['trackName'], PatternScriptEntities.ENCODING)
    for loco in setCarsForm['locations'][0]['tracks'][0]['locos']:
        if not unicode(userInputList[i], PatternScriptEntities.ENCODING) in allTracksAtLoc: # Catches invalid track typed into box, skips empty entries
            i += 1
            continue
        if userInputList[i] == fromTrack:
            i += 1
            continue
        locoObject =  PatternScriptEntities.EM.getByRoadAndNumber(loco['Road'], loco['Number'])
        try: # Catches on the fly edit of name or road
            setResult = setRs(locoObject, userInputList[i])
        except AttributeError:
            i += 1
            continue
        if setResult == 'okay':
            setCount += 1
        i += 1

    PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.EngineManagerXml.save()

    for car in setCarsForm['locations'][0]['tracks'][0]['cars']:
        if not unicode(userInputList[i], PatternScriptEntities.ENCODING) in allTracksAtLoc:
            i += 1
            continue
        if userInputList[i] == fromTrack:
            i += 1
            continue
        carObject =  PatternScriptEntities.CM.getByRoadAndNumber(car['Road'], car['Number'])
        try: # Catches on the fly edit of name or road
            setResult = setRs(carObject, userInputList[i])
        except AttributeError:
            i += 1
            continue
        if setResult == 'okay':
            setCount += 1
        i += 1

    PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarManagerXml.save()

    psLog.info('Rolling stock count: ' + str(setCount) + ', processed from track: ' + fromTrack)

    return

def setRs(rollingStock, userInputListItem):

    location = PatternScriptEntities.readConfigFile('PT')['PL']
    locationObject = PatternScriptEntities.LM.getLocationByName(unicode(location, PatternScriptEntities.ENCODING))
    toTrackObject = locationObject.getTrackByName(unicode(userInputListItem, PatternScriptEntities.ENCODING), None)

    ignoreTrackLength = PatternScriptEntities.readConfigFile('PT')['PI']
    if ignoreTrackLength:
        trackLength = toTrackObject.getLength()
        toTrackObject.setLength(9999)
        setResult = rollingStock.setLocation(locationObject, toTrackObject)
        toTrackObject.setLength(trackLength)
    else:
        setResult = rollingStock.setLocation(locationObject, toTrackObject)

    if toTrackObject.getTrackType() == 'Spur' and setResult == 'okay':
        rollingStock.updateLoad()
        rollingStock.setMoves(rollingStock.getMoves() + 1)
        deleteFd(rollingStock)
    if PatternScriptEntities.readConfigFile('PT')['AS'] and setResult == 'okay':
        applySchedule(toTrackObject, rollingStock)

    return setResult

def deleteFd(carObject):

    carObject.setFinalDestinationTrack(None)
    carObject.setFinalDestination(None)

    return

def applySchedule(toTrackObject, carObject):
    """If the to-track is a spur, try to set the load/empty requirement for the track"""

    location = PatternScriptEntities.readConfigFile('PT')['PL']
    schedule = getSchedule(location, toTrackObject.getName())
    if schedule:
        carType = carObject.getTypeName()
        carObject.setLoadName(schedule.getItemByType(carType).getShipLoadName())
        carObject.setDestination(schedule.getItemByType(carType).getDestination(), schedule.getItemByType(carType).getDestinationTrack(), True) # force set dest
        schedule.getItemByType(carType).setHits(schedule.getItemByType(carType).getHits() + 1)

    return

def getSchedule(locationString, trackString):
    """Returns a schedule if there is one"""

    track = PatternScriptEntities.LM.getLocationByName(locationString).getTrackByName(trackString, 'Spur')

    if track:
        schedule = PatternScriptEntities.SM.getScheduleByName(track.getScheduleName())

        return schedule

    return

def exportSetCarsFormToTp(setCarsForm, textBoxEntry):

    psLog.debug('ModelSetCarsForm.exportSetCarsFormToTp')

    if PatternScriptEntities.CheckTpDestination().directoryExists():

        jmriExport = PatternTracksExport.ExportJmriLocations()
        locationList = jmriExport.makeLocationList()
        jmriExport.toTrainPlayer(locationList)

        tpSwitchList = PatternTracksExport.TrackPatternTranslationToTp()
        modifiedSwitchList = tpSwitchList.modifySwitchList(setCarsForm, textBoxEntry)
        appendedTpSwitchList = tpSwitchList.appendSwitchList(modifiedSwitchList)

        tpWorkEventProcessor = PatternTracksExport.ProcessWorkEventList()
        tpWorkEventProcessor.writeTpWorkEventListAsJson(appendedTpSwitchList)
        tpSwitchListHeader = tpWorkEventProcessor.makeTpHeader(appendedTpSwitchList)
        tpSwitchListLocations = tpWorkEventProcessor.makeTpLocations(appendedTpSwitchList)

        PatternTracksExport.WriteWorkEventListToTp(tpSwitchListHeader + tpSwitchListLocations).asCsv()

    return

def makeLocationDict(setCarsForm, textBoxEntry):
    """Replaces car['Set to'] = [ ] with either [Hold] or ["some other valid track"]"""

    psLog.debug('ModelSetCarsForm.makeLocationDict')

    trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
    location = setCarsForm['locations'][0]['locationName']
    allTracksAtLoc = ModelEntities.getTracksByLocation(None)

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), PatternScriptEntities.ENCODING))

    longestTrackString = 6 # 6 is the length of [Hold]
    for track in PatternScriptEntities.readConfigFile('PT')['PT']: # Pattern Tracks
        if len(track) > longestTrackString:
            longestTrackString = len(track)

    i = 0
    locoList = []
    for loco in setCarsForm['locations'][0]['tracks'][0]['locos']:
        setTrack = u'Hold'
        userInput = unicode(userInputList[i], PatternScriptEntities.ENCODING)
        if userInput in allTracksAtLoc and userInput != trackName:
            setTrack = userInput
        loco['Set to'] = PatternScriptEntities.formatText('[' + setTrack + ']', longestTrackString + 2)
        locoList.append(loco)
        i += 1

    carList = []
    for car in setCarsForm['locations'][0]['tracks'][0]['cars']:
        setTrack = u'Hold'
        userInput = unicode(userInputList[i], PatternScriptEntities.ENCODING)
        if userInput in allTracksAtLoc and userInput != trackName:
            setTrack = userInput
        car['Set to'] = PatternScriptEntities.formatText('[' + setTrack + ']', longestTrackString + 2)
        carList.append(car)
        i += 1

    trackDetails = {}
    trackDetails['trackName'] = trackName
    trackDetails['length'] = 1
    trackDetails['locos'] = locoList
    trackDetails['cars'] = carList

    locationDict = {}
    locationDict['locationName'] = location
    locationDict['tracks'] = [trackDetails]

    return locationDict

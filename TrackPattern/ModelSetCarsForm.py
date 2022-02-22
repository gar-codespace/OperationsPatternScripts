# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import java.awt
import logging
from codecs import open as codecsOpen
from json import loads as jsonLoads, dumps as jsonDumps

import psEntities.MainScriptEntities
import TrackPattern.ModelEntities
import TrackPattern.ExportToTrainPlayer

'''Data crunching for the Pattern Reprot for Track X Form'''

scriptName = 'OperationsPatternScripts.TrackPattern.ModelSetCarsForm'
scriptRev = 20220101
psLog = logging.getLogger('PS.TP.ModelSetCarsForm')

def testFormValidity(body, textBoxEntry):

    if len(textBoxEntry) == len(body['Locos']) + len(body['Cars']):
        return True
    else:
        psLog.critical('mismatched input list and car roster lengths')
        return False

def setCarsToTrack(body, textBoxEntry):

    psLog.debug('setCarsToTrack')
    trackData = []

    em = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.engines.EngineManager)
    cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
    lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)

    ignoreTrackLength = psEntities.MainScriptEntities.readConfigFile('TP')['PI']
    location = psEntities.MainScriptEntities.readConfigFile('TP')['PL']
    locationObject = lm.getLocationByName(unicode(location, psEntities.MainScriptEntities.setEncoding()))
    allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(location, None)
    fromTrack = unicode(body['Name'], psEntities.MainScriptEntities.setEncoding())

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), psEntities.MainScriptEntities.setEncoding()))

    i = 0
    setCount = 0

    for loco in body['Locos']:

        toTrack = fromTrack
        if userInputList[i]:
            toTrack = userInputList[i]

        locoObject = em.newRS(loco['Road'], loco['Number'])
        toTrackObject = locationObject.getTrackByName(unicode(toTrack, psEntities.MainScriptEntities.setEncoding()), None)
        if ignoreTrackLength:
            trackLength = toTrackObject.getLength()
            toTrackObject.setLength(9999)
            setResult = locoObject.setLocation(locationObject, toTrackObject)
            toTrackObject.setLength(trackLength)
        else:
            setResult = locoObject.setLocation(locationObject, toTrackObject)

        if setResult == 'okay' and toTrack != fromTrack:
            setCount += 1

        i += 1
    jmri.jmrit.operations.rollingstock.engines.EngineManagerXml.save()

    for car in body['Cars']:

        toTrack = fromTrack
        if userInputList[i]:
            toTrack = userInputList[i]

        carObject = cm.newRS(car['Road'], car['Number'])
        toTrackObject = locationObject.getTrackByName(unicode(toTrack, psEntities.MainScriptEntities.setEncoding()), None)
        if ignoreTrackLength:
            trackLength = toTrackObject.getLength()
            toTrackObject.setLength(9999)
            setResult = carObject.setLocation(locationObject, toTrackObject)
            toTrackObject.setLength(trackLength)
        else:
            setResult = carObject.setLocation(locationObject, toTrackObject)

        if setResult == 'okay' and toTrack != fromTrack:
            setCount += 1
            schedule = getSchedule(location, toTrack)
            applySchedule(carObject, schedule)

        i += 1

    psLog.info('Rolling stock count: ' + str(setCount) + ', processed from track: ' + fromTrack)
    jmri.jmrit.operations.rollingstock.cars.CarManagerXml.save()

    return

def writeTpSwitchListFromJson(switchListName):
    '''Writes the switch list for TrainPlayer'''

    TrackPattern.ExportToTrainPlayer.CheckTpDestination().directoryExists()
    TrackPattern.ExportToTrainPlayer.JmriLocationsToTrainPlayer().exportLocations()
    tpWorkEventList = TrackPattern.ExportToTrainPlayer.WorkEventListForTrainPlayer(switchListName).readFromFile()
    if not tpWorkEventList:
        psLog.critical('No work event list read in')
        return
    tpCsvWorkEventList = TrackPattern.ExportToTrainPlayer.CsvListFromFile(tpWorkEventList).makeList()
    TrackPattern.ExportToTrainPlayer.writeWorkEventListToTp(tpCsvWorkEventList).writeAsCsv()

    return

def makeSetCarsSwitchList(body, textBoxEntry):

    psLog.debug('makeSetCarsSwitchList')

    if len(textBoxEntry) != len(body['Locos']) + len(body['Cars']):
        psLog.critical('mismatched input list and car roster lengths')
        return None

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), psEntities.MainScriptEntities.setEncoding()))

    location = psEntities.MainScriptEntities.readConfigFile('TP')['PL']
    allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(location, None)
    trackName = unicode(body['Name'], psEntities.MainScriptEntities.setEncoding())
    i = 0
    for loco in body['Locos']:
        setTrack = unicode('Hold', psEntities.MainScriptEntities.setEncoding())
        userInput = unicode(userInputList[i], psEntities.MainScriptEntities.setEncoding())
        if userInput in allTracksAtLoc and userInput != trackName:
            setTrack = userInput
        loco['Set to'] = setTrack
        i += 1
    for car in body['Cars']:
        setTrack = unicode('Hold', psEntities.MainScriptEntities.setEncoding())
        userInput = unicode(userInputList[i], psEntities.MainScriptEntities.setEncoding())
        if userInput in allTracksAtLoc and userInput != trackName:
            setTrack = userInput
        car['Set to'] = setTrack
        i += 1

    return body

def modifySwitchListForPrint(body):
    '''Replaces car['Set to'] = [ ] with either [Hold] or ["some other track"]'''

    psLog.debug('modifySwitchListForPrint')
    longestTrackString = 1
    for track in psEntities.MainScriptEntities.readConfigFile('TP')['PT']: # Pattern Tracks
        if len(track) > longestTrackString:
            longestTrackString = len(track)

    if longestTrackString < 7:
        longestTrackString = 6

    for loco in body['Locos']:
        carSetTo = unicode(loco['Set to'], psEntities.MainScriptEntities.setEncoding())
        loco['Set to'] = TrackPattern.ModelEntities.formatText('[' + carSetTo + ']', longestTrackString + 2)

    for car in body['Cars']:
        carSetTo = unicode(car['Set to'], psEntities.MainScriptEntities.setEncoding())
        car['Set to'] = TrackPattern.ModelEntities.formatText('[' + carSetTo + ']', longestTrackString + 2)

    return body

# def modifySwitchListForTp(body):
#     '''Replaces car['Set to'] = [ ] with the track comment'''
#
#     psLog.debug('modifySwitchListForTp')
#     location = psEntities.MainScriptEntities.readConfigFile('TP')['PL']
#     lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
#     for car in body['Cars']:
#         if 'Hold' in car['Set to']:
#             car['Set to'] = lm.getLocationByName(location).getTrackByName(car['Track'], None).getComment()
#         else:
#             car['Set to'] = lm.getLocationByName(location).getTrackByName(car['Set to'], None).getComment()
#
#     return body

# def appendSwitchListForTp(body):
#
#     psLog.debug('appendSwitchListForTp')
#     reportTitle = psEntities.MainScriptEntities.readConfigFile('TP')['RT']['TP']
#     jsonFile = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + reportTitle + '.json'
#     with codecsOpen(jsonFile, 'r', encoding=psEntities.MainScriptEntities.setEncoding()) as jsonWorkFile:
#         jsonSwitchList = jsonWorkFile.read()
#     switchList = jsonLoads(jsonSwitchList)
#     switchListName = switchList['description']
#     trackDetailList = switchList['tracks']
#
#     if not trackDetailList:
#         body['Name'] = 'TrainPlayer'
#         body['Length'] = 0
#         trackDetailList.append(body)
#     else:
#         carList = trackDetailList[0]['Cars']
#         # carList.append(body['Cars'])
#         carList += body['Cars']
#         trackDetailList[0]['Cars'] = carList
#     switchList['tracks'] = trackDetailList
#
#     jsonObject = jsonDumps(switchList, indent=2, sort_keys=True)
#     with codecsOpen(jsonFile, 'wb', encoding=psEntities.MainScriptEntities.setEncoding()) as jsonWorkFile:
#         jsonWorkFile.write(jsonObject)
#
#     return reportTitle

def getSchedule(locationString, trackString):
    '''Returns a schedule if there is one'''

    psLog.debug('getSchedule')

    lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
    sm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.schedules.ScheduleManager)
    track = lm.getLocationByName(locationString).getTrackByName(trackString, 'Spur')

    if (track):
        schedule = sm.getScheduleByName(track.getScheduleName())
        return schedule

    return

def applySchedule(carObject, scheduleObject=None):
    '''Mini "controller" to plug in additional schedule methods.
    The schedule is applied when setting into a spur.
    Increment move count only when set to a spur.'''

    if not scheduleObject:

        return

    if (psEntities.MainScriptEntities.readConfigFile('TP')['AS']): # apply schedule flag
        applyLoadRubric(carObject, scheduleObject)
        applyFdRubric(carObject, scheduleObject)
        carObject.setMoves(carObject.getMoves() + 1)

    return

def getTrackObject(locationString, trackString):

    psLog.debug('getTrackObject')

    lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
    trackObject = lm.getLocationByName(locationString).getTrackByName(trackString, None)

    return trackObject

def applyLoadRubric(carObject, scheduleObject=None):
    '''Apply loads by schedule, RWE/RWL, custom L/E, then default'''

    carType = carObject.getTypeName()
# Toggle the default loads if used
    if (carObject.getLoadName() == TrackPattern._defaultLoadLoad):
        carObject.setLoadName(TrackPattern._defaultLoadEmpty)
    elif (carObject.getLoadName() == TrackPattern._defaultLoadEmpty):
        carObject.setLoadName(TrackPattern._defaultLoadLoad)
# Toggle the custom loads
    try: # first try to apply the schedule
        carObject.setLoadName(scheduleObject.getItemByType(carType).getShipLoadName())
        scheduleObject.getItemByType(carType).setHits(scheduleObject.getItemByType(carType).getHits() + 1)
    except:
        try: # apply values from RWE or RWL
            if (carObject.getLoadType() == 'Empty'): # toggle the load
                carObject.setLoadName(carObject.getReturnWhenLoadedLoadName())
            else:
                carObject.setLoadName(carObject.getReturnWhenEmptyLoadName())
        except:
            try: # apply values from custom empty
                if (carObject.getLoadType() == 'Empty'): # toggle the load
                    carObject.setLoadName(TrackPattern._carTypeByLoadDict.get(carType))
                else:
                    carObject.setLoadName(TrackPattern._carTypeByEmptyDict.get(carType))
            except: # when all else fails, apply the default loads
                if (carObject.getLoadType() == 'Empty'): # toggle the load
                    carObject.setLoadName(TrackPattern._defaultLoadLoad)
                else:
                    carObject.setLoadName(TrackPattern._defaultLoadEmpty)

    return

def applyFdRubric(carObject, scheduleObject=None):
    '''For spurs only, sets the values for the cars destination and track from the schedule or RWE/RWL'''

    patternIgnore = psEntities.MainScriptEntities.readConfigFile('TP')['PI']
    carType = carObject.getTypeName()
    carObject.setFinalDestination(None)
    carObject.setFinalDestinationTrack(None)

    try: # first try to apply the schedule
        trySchedule = carObject.setDestination(scheduleObject.getItemByType(carType).getDestination(), scheduleObject.getItemByType(carType).getDestinationTrack())
        if (trySchedule.startswith('rolling')):
            trySchedule = carObject.setDestination(scheduleObject.getItemByType(carType).getDestination(), scheduleObject.getItemByType(carType).getDestinationTrack(), patternIgnore)
            if (trySchedule != 'okay'):
                psLog.warning('Schedule destination not applied: ' + trySchedule)
        elif (trySchedule != 'okay'):
            psLog.warning('Schedule destination not applied: ' + trySchedule)
    except:
        if (carObject.getLoadType() == 'Load'): # load has already been toggled
            applyRWL = carObject.setDestination(carObject.getReturnWhenLoadedDestination(), carObject.getReturnWhenLoadedDestTrack(), patternIgnore)
            if (applyRWL != 'okay'):
                psLog.info('RWL destination not applied: ' + applyRWL)
        if (carObject.getLoadType() == 'Empty'): # load has already been toggled
            applyRWE = carObject.setDestination(carObject.getReturnWhenEmptyDestination(), carObject.getReturnWhenEmptyDestTrack(), patternIgnore)
            if (applyRWE != 'okay'):
                psLog.info('RWE destination not applied: ' + applyRWE)

    return

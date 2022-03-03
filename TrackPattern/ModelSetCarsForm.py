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

scriptName = 'OperationsPatternScripts.TrackPattern.ModelSetCarsForm'
scriptRev = 20220101
psLog = logging.getLogger('PS.TP.ModelSetCarsForm')

def testValidityOfForm(setCarsForm, textBoxEntry):

    psLog.debug('testValidityOfForm')

    locoCount = len(setCarsForm['locations'][0]['tracks'][0]['locos'])
    carCount = len(setCarsForm['locations'][0]['tracks'][0]['cars'])

    if len(textBoxEntry) == locoCount + carCount:
        return True
    else:
        psLog.critical('mismatched input list and car roster lengths')
        return False

def printSwitchList(setCarsForm, textBoxEntry):

    psLog.debug('printSwitchList')

    modifiedsetCarsForm = modifySetCarsList(setCarsForm, textBoxEntry)

    headerNames = psEntities.MainScriptEntities.readConfigFile('TP')
    patternListForJson = TrackPattern.Model.makePatternHeader()
    patternListForJson['trainDescription'] = headerNames['TD']['SC']
    patternListForJson['trainName'] = headerNames['TN']['SC']
    patternListForJson['trainComment'] = headerNames['TC']['SC']
    patternListForJson['locations'] = modifiedsetCarsForm['locations']

    workEventName = TrackPattern.Model.writeWorkEventListAsJson(patternListForJson)
    textWorkEventList = TrackPattern.Model.readJsonWorkEventList(workEventName)
    textListForPrint = TrackPattern.Model.makeTextListForPrint(textWorkEventList)
    TrackPattern.Model.writeTextSwitchList(workEventName, textListForPrint)
    TrackPattern.View.displayTextSwitchList(workEventName)

    return

def setCarsToTrack(setCarsForm, textBoxEntry):

    psLog.debug('setCarsToTrack')

    trackData = []
    em = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.engines.EngineManager)
    cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
    lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
    ignoreTrackLength = psEntities.MainScriptEntities.readConfigFile('TP')['PI']

    location = setCarsForm['locations'][0]['locationName']
    locationObject = lm.getLocationByName(unicode(location, psEntities.MainScriptEntities.setEncoding()))
    allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(location, None)
    fromTrack = unicode(setCarsForm['locations'][0]['tracks'][0]['trackName'], psEntities.MainScriptEntities.setEncoding())

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), psEntities.MainScriptEntities.setEncoding()))

    i = 0
    setCount = 0

    for loco in setCarsForm['locations'][0]['tracks'][0]['locos']:

        toTrack = fromTrack
        if userInputList[i]:
            toTrack = userInputList[i]

        locoObject = em.newRS(loco['Road'], loco['Number'])
        toTrackObject = locationObject.getTrackByName(unicode(toTrack, psEntities.MainScriptEntities.setEncoding()), None)

        if unicode(toTrack, psEntities.MainScriptEntities.setEncoding()) in allTracksAtLoc: # Catches invalid track typed into box
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

    for car in setCarsForm['locations'][0]['tracks'][0]['cars']:

        toTrack = fromTrack
        if userInputList[i]:
            toTrack = userInputList[i]

        carObject = cm.newRS(car['Road'], car['Number'])
        toTrackObject = locationObject.getTrackByName(unicode(toTrack, psEntities.MainScriptEntities.setEncoding()), None)

        if unicode(toTrack, psEntities.MainScriptEntities.setEncoding()) in allTracksAtLoc: # Catches invalid track typed into box
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
    jmri.jmrit.operations.rollingstock.cars.CarManagerXml.save()

    psLog.info('Rolling stock count: ' + str(setCount) + ', processed from track: ' + fromTrack)

    return

def exportToTrainPlayer(setCarsForm, textBoxEntry):

    psLog.debug('exportToTrainPlayer')

    TrackPattern.ExportToTrainPlayer.CheckTpDestination().directoryExists()
    TrackPattern.ExportToTrainPlayer.ExportJmriLocations().toTrainPlayer()

    tpSwitchList = TrackPattern.ExportToTrainPlayer.TrackPatternTranslationToTp()
    modifiedSwitchList = tpSwitchList.modifySwitchList(setCarsForm, textBoxEntry)
    appendedTpSwitchList = tpSwitchList.appendSwitchList(modifiedSwitchList)
    tpWorkEventProcessor = TrackPattern.ExportToTrainPlayer.ProcessWorkEventList()
    tpWorkEventProcessor.writeWorkEventListAsJson(appendedTpSwitchList)
    tpSwitchListHeader = tpWorkEventProcessor.makeTpHeader(appendedTpSwitchList)
    tpSwitchListLocations = tpWorkEventProcessor.makeTpLocations(appendedTpSwitchList)
    TrackPattern.ExportToTrainPlayer.WriteWorkEventListToTp(tpSwitchListHeader + tpSwitchListLocations).asCsv()

    return

def writeTpSwitchListFromJson(switchListName):
    '''Writes the switch list for TrainPlayer'''

    psLog.debug('writeTpSwitchListFromJson')

    TrackPattern.ExportToTrainPlayer.CheckTpDestination().directoryExists()
    TrackPattern.ExportToTrainPlayer.JmriLocationsToTrainPlayer().exportLocations()
    tpWorkEventList = TrackPattern.ExportToTrainPlayer.WorkEventListForTrainPlayer(switchListName).readFromFile()
    if not tpWorkEventList:
        psLog.critical('No work event list read in')
        return
    tpCsvWorkEventList = TrackPattern.ExportToTrainPlayer.CsvListFromFile(tpWorkEventList).makeList()
    TrackPattern.ExportToTrainPlayer.writeWorkEventListToTp(tpCsvWorkEventList).writeAsCsv()

    return

def modifySetCarsList(setCarsForm, textBoxEntry):
    '''Replaces car['Set to'] = [ ] with either [Hold] or ["some other valid track"]'''

    psLog.debug('modifySetCarsList')

    trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
    location = setCarsForm['locations'][0]['locationName']
    allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(location, None)

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), psEntities.MainScriptEntities.setEncoding()))

    longestTrackString = 6 # 6 is the length of [Hold]
    for track in psEntities.MainScriptEntities.readConfigFile('TP')['PT']: # Pattern Tracks
        if len(track) > longestTrackString:
            longestTrackString = len(track)

    i = 0
    locoList = setCarsForm['locations'][0]['tracks'][0]['locos']
    for loco in locoList:
        setTrack = u'Hold'
        userInput = unicode(userInputList[i], psEntities.MainScriptEntities.setEncoding())
        if userInput in allTracksAtLoc and userInput != trackName:
            setTrack = userInput
        loco['Set to'] = TrackPattern.ModelEntities.formatText('[' + setTrack + ']', longestTrackString + 2)
        i += 1
    setCarsForm['locations'][0]['tracks'][0]['locos'] = locoList

    carList = setCarsForm['locations'][0]['tracks'][0]['cars']
    for car in carList:
        setTrack = u'Hold'
        userInput = unicode(userInputList[i], psEntities.MainScriptEntities.setEncoding())
        if userInput in allTracksAtLoc and userInput != trackName:
            setTrack = userInput
        car['Set to'] = TrackPattern.ModelEntities.formatText('[' + setTrack + ']', longestTrackString + 2)
        i += 1
    setCarsForm['locations'][0]['tracks'][0]['cars'] = carList

    return setCarsForm

def getSchedule(locationString, trackString):
    '''Returns a schedule if there is one'''

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

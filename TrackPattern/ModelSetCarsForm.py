# coding=utf-8
# Extended ìÄÅÉî
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
import logging
from codecs import open as cOpen
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern')
import MainScriptEntities
import TrackPattern.ModelEntities

'''Data crunching for the Set Cars Form'''

scriptRev = 'TrackPattern.ModelSetCarsForm v20211210'
psLog = logging.getLogger('PS.TP.ModelSetCarsForm')

def processYpForPrint(trackData, textBoxEntry):
    psLog.debug('processYpForPrint')
    userInputList = [] # create a list of user inputs for the set car destinations
    for userInput in textBoxEntry: # Read in the user input
        userInputList.append(unicode(userInput.getText(), MainScriptEntities.setEncoding()))
    i = 0
    track = trackData['ZZ'][0] # There is only one track in trackData
    if (len(userInputList) == len(track['TR'])): # check that the lengths of the input list and car roster match
        psLog.debug('input list and car roster lengths match')
        trackLocation = trackData['YL']
        trackName = unicode(track['TN'], MainScriptEntities.setEncoding())
        allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(trackLocation, None)
        for setTo in track['TR']:
            setTrack = unicode('Hold', MainScriptEntities.setEncoding())
            if (userInputList[i] in allTracksAtLoc and userInputList[i] != trackName):
                setTrack = unicode(userInputList[i], MainScriptEntities.setEncoding())
            setTrack = TrackPattern.ModelEntities.formatText(' [' + setTrack + '] ', 8)
            setTo.update({'Set to': setTrack}) # replaces empty brackets with the marked ones
            i += 1
    else:
        psLog.critical('mismatched input list and car roster lengths')
        trackData = []

    return trackData

def writeSwitchList(trackData):
    '''Writes the TXT switch list to notepad and optionally creates the CSV switch list '''

    for track in trackData['ZZ']:
        trackName = track['TN']
# Write the switch list
    textSwitchList = TrackPattern.ModelEntities.makeSwitchlist(trackData, False)
    textCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\Switch list (' + trackData['YL'] + ') (' + trackName + ').txt'
    with cOpen(textCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as textWorkFile:
        textWorkFile.write(textSwitchList)
# Write the CSV switch list
    if (jmri.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled()):
        csvSwitchList = TrackPattern.ModelEntities.makeCsvSwitchlist(trackData)
        csvCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists\\Switch list (' + trackData['YL'] + ') (' + trackName + ').csv'
        with cOpen(csvCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as csvWorkFile:
            csvWorkFile.write(csvSwitchList)
    return textCopyTo

def setCarsToTrack(trackData, textBoxEntry):
# Boilerplate
    cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
    lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
    ignoreLength =  MainScriptEntities.readConfigFile('TP')['PI'] # flag to ignore track length
# Get user inputs
    userInputList = [] # create a list of user inputs from the text input boxes
    for userInput in textBoxEntry: # Read in and check the user input
        userInputList.append(unicode(userInput.getText(), MainScriptEntities.setEncoding()))
# Set cars
    i = 0
    track = trackData['ZZ'][0]
    if (len(userInputList) == len(track['TR'])): # check that the lengths of the -input list- and -car roster- match
        psLog.debug('input list and car roster lengths match')
        locationString = trackData['YL']
        locationObject = lm.getLocationByName(unicode(trackData['YL'], MainScriptEntities.setEncoding()))
        fromTrackString = unicode(track['TN'], MainScriptEntities.setEncoding())
        allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(locationString, None)
        # scheduleObject, fromTrackObject = getScheduleAndTrack(locationString, fromTrackString)
        setCount = 0
        for car in track['TR']:
            carObject = cm.newRS(car['Road'], car['Number'])
            if (userInputList[i] in allTracksAtLoc and userInputList[i] != fromTrackString):
                toTrackObject = locationObject.getTrackByName(unicode(userInputList[i], MainScriptEntities.setEncoding()), None)
                locationObject.setStatus(carObject.testDestination(locationObject, toTrackObject))
                if (locationObject.getStatus() == 'okay' or locationObject.getStatus().startswith('car has')):
                    carObject.setLocation(locationObject, toTrackObject)
                    scheduleObject = getToTrackSchedule(toTrackObject)
                    applySchedule(carObject, toTrackObject, scheduleObject)
                    setCount += 1
                else:
                    psLog.warning(carObject.getRoadName() + ' ' + carObject.getNumber() + ' not set exception: ' + carObject.testDestination(locationObject, toTrackObject))
                if (locationObject.getStatus().startswith('rolling') and ignoreLength):
                    trackLength = toTrackObject.getLength()
                    toTrackObject.setLength(9999)
                    locationObject.setStatus(carObject.testDestination(locationObject, toTrackObject))
                    if (locationObject.getStatus() == 'okay' or locationObject.getStatus().startswith('car has')):
                        carObject.setLocation(locationObject, toTrackObject)
                        scheduleObject = getToTrackSchedule(toTrackObject)
                        applySchedule(carObject, toTrackObject, scheduleObject)
                        psLog.warning('Track length exceeded for ' + toTrackObject.getName())
                        setCount += 1
                    else:
                        psLog.warning(carObject.getRoadName() + ' ' + carObject.getNumber() + ' not set exception: ' + carObject.testDestination(locationObject, toTrackObject))
                    toTrackObject.setLength(trackLength)
                    setCount += 1
            i += 1
        psLog.info(str(setCount) + ' cars were processed from track ' + fromTrackString)
        jmri.jmrit.operations.rollingstock.cars.CarManagerXml.save()
    else:
        psLog.critical('mismatched input list and car roster lengths')

    return

def getToTrackSchedule(toTrackObject):
    '''Returns the tracks schedule object'''

    psLog.debug('getToTrackSchedule')

    sm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.schedules.ScheduleManager)
    scheduleObject = None
    scheduleObject = sm.getScheduleByName(toTrackObject.getScheduleName())

    return scheduleObject

def getScheduleAndTrack(locationString, trackString):
    '''Returns a schedule object and track object'''

    psLog.debug('getScheduleAndTrack')

    lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
    sm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.schedules.ScheduleManager)
    scheduleObject = None
    trackObject = lm.getLocationByName(locationString).getTrackByName(trackString, 'Spur')

    if (trackObject):
        scheduleObject = sm.getScheduleByName(trackObject.getScheduleName())

    return scheduleObject, trackObject

def applySchedule(carObject, toTrackObject, scheduleObject):
    '''Mini "controller" to plug in additional schedule methods
    Increment move count only when set to a spur'''

    try:
        if (toTrackObject.getTrackType() == 'Spur'):
            trackPatternConfig = MainScriptEntities.readConfigFile('TP')
            if (trackPatternConfig['AS']):
                applyLoadRubric(carObject, scheduleObject)
                applyFdRubric(carObject, scheduleObject)
            carObject.setMoves(carObject.getMoves() + 1)
    except:
        pass

    return


def applyLoadRubric(carObject, scheduleObject=None):
    '''For spurs only, sets the values for shipped cars by priority'''

    carType = carObject.getTypeName()
# Toggle the default loads if used
    if (carObject.getLoadName() == MainScriptEntities.defaultLoadLoad):
        carObject.setLoadName(MainScriptEntities.defaultLoadEmpty)
    elif (carObject.getLoadName() == MainScriptEntities.defaultLoadEmpty):
        carObject.setLoadName(MainScriptEntities.defaultLoadLoad)
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
                    carObject.setLoadName(MainScriptEntities.carTypeByLoadDict.get(carType))
                else:
                    carObject.setLoadName(MainScriptEntities.carTypeByEmptyDict.get(carType))
            except: # when all else fails, apply the default loads
                if (carObject.getLoadType() == 'Empty'): # toggle the load
                    carObject.setLoadName(MainScriptEntities.defaultLoadLoad)
                else:
                    carObject.setLoadName(MainScriptEntities.defaultLoadEmpty)

    return

def applyFdRubric(carObject, scheduleObject=None):
    '''For spurs only, sets the values for the cars destination and track from the schedule or RWE/RWL'''

    patternIgnore = MainScriptEntities.readConfigFile('TP')['PI']
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
    

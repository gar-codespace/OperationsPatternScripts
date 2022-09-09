# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Process methods for the Set Cars Form for Track X form"""

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ModelSetCarsForm'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.ModelSetCarsForm')

def mergeForms(setCarsForm, textBoxEntry):
    """Mini controller that merges the two inputs.
        Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.switchListButton
        ControllerSetCarsForm.CreateSetCarsFormGui.setRsButton
        """

    userInputList = makeUserInputList(textBoxEntry)
    merged = merge(setCarsForm, userInputList)
    workEventName = PatternScriptEntities.BUNDLE['Switch List for Track']
    ModelEntities.writeWorkEventListAsJson(merged, workEventName)

    return

def makeUserInputList(textBoxEntry):
    """Used by:
        switchListButton
        """

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), PatternScriptEntities.ENCODING))

    return userInputList

def merge(setCarsForm, userInputList):
    """Merge the values in textBoxEntry into the ['Set_To'] field of setCarsForm.
        This preps the setCarsForm for the o2o sub.
        Used by:
        switchListButton
        """

    _psLog.debug('ModelSetCarsForm.mergeForms')

    longestTrackString = findLongestTrackString()
    allTracksAtLoc = ModelEntities.getTracksByLocation(None)

    i = 0
    locos = setCarsForm['locations'][0]['tracks'][0]['locos']
    for loco in locos:
        setTrack = setCarsForm['locations'][0]['tracks'][0]['trackName']
        setTrack = PatternScriptEntities.formatText('[' + setTrack + ']', longestTrackString + 1)
        loco.update({'Set_To': setTrack})

        userInput = unicode(userInputList[i], PatternScriptEntities.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PatternScriptEntities.formatText('[' + userInput + ']', longestTrackString + 1)
            loco.update({'Set_To': setTrack})
        i += 1

    cars = setCarsForm['locations'][0]['tracks'][0]['cars']
    for car in cars:
        setTrack = setCarsForm['locations'][0]['tracks'][0]['trackName']
        setTrack = PatternScriptEntities.formatText('[' + setTrack + ']', longestTrackString + 1)
        car.update({'Set_To': setTrack})

        userInput = unicode(userInputList[i], PatternScriptEntities.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PatternScriptEntities.formatText('[' + userInput + ']', longestTrackString + 1)
            car.update({'Set_To': setTrack})
        i += 1

    return setCarsForm

def findLongestTrackString():
    """Used by:
        mergeForms
        """

    longestTrackString = 6 # 6 is the length of [Hold]
    for track in PatternScriptEntities.readConfigFile('PT')['PT']: # Pattern Tracks
        if len(track) > longestTrackString:
            longestTrackString = len(track)

    return longestTrackString

def setRsToTrack():
    """Mini controller that moves the selected RS to a different track.
        Subject to track length and RS type restrictions.
        Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.setRsButton
        """

    _psLog.debug('ModelSetCarsForm.setRsToTrack')

    workEventName = PatternScriptEntities.BUNDLE['Switch List for Track']
    workEvents = PatternScriptEntities.readJsonWorkEventList(workEventName)
    moveRollingStock(workEvents)

    return

def moveRollingStock(workEvents):

    setCount = 0

    ignoreTrackLength = PatternScriptEntities.readConfigFile('PT')['PI']
    location = PatternScriptEntities.readConfigFile('PT')['PL']
    toLocation = PatternScriptEntities.LM.getLocationByName(unicode(location, PatternScriptEntities.ENCODING))

    locos = workEvents['locations'][0]['tracks'][0]['locos']
    for loco in locos:
        rollingStock = PatternScriptEntities.EM.getByRoadAndNumber(loco['Road'], loco['Number'])
        setTo = PatternScriptEntities.parseSetTo(loco['Set_To'])
        toTrack = toLocation.getTrackByName(setTo, None)
        if ignoreTrackLength:
            setResult = rollingStock.setLocation(toLocation, toTrack, True)
        else:
            setResult = rollingStock.setLocation(toLocation, toTrack)

        if setResult == 'okay':
            setCount += 1
    # PatternScriptEntities.EMX.save()

    cars = workEvents['locations'][0]['tracks'][0]['cars']
    for car in cars:
        rollingStock = PatternScriptEntities.CM.getByRoadAndNumber(car['Road'], car['Number'])
        setTo = PatternScriptEntities.parseSetTo(car['Set_To'])
        toTrack = toLocation.getTrackByName(setTo, None)
        if ignoreTrackLength:
            setResult = rollingStock.setLocation(toLocation, toTrack, True)
        else:
            setResult = rollingStock.setLocation(toLocation, toTrack)

        if setResult == 'okay':
            rsUpdate(toTrack, rollingStock)
            scheduleUpdate(toTrack, rollingStock)
            setCount += 1
    # PatternScriptEntities.CMX.save()

    _psLog.info('Rolling stock count: ' + str(setCount) + ', processed.')

    return

def parseSetTo(setTo):
    """Moved to PatternScriptEntities """

    x = setTo.split('[')
    y = x[1].split(']')

    return y[0]


def rsUpdate(toTrack, rollingStock):
    """Used by:
        moveRollingStock
        """

    if toTrack.getTrackType() == 'Spur':
        rollingStock.setMoves(rollingStock.getMoves() + 1)

    rollingStock.setFinalDestinationTrack(None)
    rollingStock.setFinalDestination(None)

    return

def scheduleUpdate(toTrack, rollingStock):
    """If the to-track is a spur, try to set the load/empty requirement for the track
        Honors apply schedule flag. Toggles default L/E for spurs.
        Used by:
        moveRollingStock
        """

    schedule = PatternScriptEntities.SM.getScheduleByName(toTrack.getScheduleName())
    if schedule and PatternScriptEntities.readConfigFile('PT')['AS']:
        carType = rollingStock.getTypeName()
        rollingStock.setLoadName(schedule.getItemByType(carType).getShipLoadName())
        rollingStock.setDestination(schedule.getItemByType(carType).getDestination(), schedule.getItemByType(carType).getDestinationTrack(), True) # force set dest
        schedule.getItemByType(carType).setHits(schedule.getItemByType(carType).getHits() + 1)
    else:
        if toTrack.getTrackType() == 'Spur':
            rollingStock.updateLoad() # Toggles default load

    return

def testValidityOfForm(setCarsForm, textBoxEntry):
    """Checks that both submitted forms are the same length
        Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.quickCheck
        """

    _psLog.debug('ModelSetCarsForm.testValidityOfForm')

    locoCount = len(setCarsForm['locations'][0]['tracks'][0]['locos'])
    carCount = len(setCarsForm['locations'][0]['tracks'][0]['cars'])

    if len(textBoxEntry) == locoCount + carCount:
        return True
    else:
        _psLog.critical('mismatched input list and car roster lengths')
        return False

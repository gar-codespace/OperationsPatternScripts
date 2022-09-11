# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Process methods for the Set Cars Form for Track X form"""

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ModelSetCarsForm'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.ModelSetCarsForm')

def writeToJson(setCarsForm):
    """Mini controller that writes the set cars form to json.
        Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.switchListButton
        ControllerSetCarsForm.CreateSetCarsFormGui.setRsButton
        """

    switchListName = PatternScriptEntities.BUNDLE['Switch List for Track']
    switchListPath = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + switchListName + '.json'

    switchListReport = PatternScriptEntities.dumpJson(setCarsForm)
    PatternScriptEntities.genericWriteReport(switchListPath, switchListReport)

    return

def setRsButton(textBoxEntry):
    """Mini controller that moves the selected RS to the selected track.
        Subject to track length and RS type restrictions.
        Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.setRsButton
        """

    _psLog.debug('ModelSetCarsForm.setRsToTrack')

    switchListName = PatternScriptEntities.BUNDLE['Switch List for Track']
    switchListPath = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + switchListName + '.json'
    switchList = PatternScriptEntities.genericReadReport(switchListPath)
    switchList = PatternScriptEntities.loadJson(switchList)

    moveRollingStock(switchList, textBoxEntry)

    return

def moveRollingStock(switchList, textBoxEntry):
    """Similar to:
        ViewEntities.merge
        """

    setCount = 0
    i = 0

    ignoreTrackLength = PatternScriptEntities.readConfigFile('PT')['PI']

    allTracksAtLoc = PatternScriptEntities.getTracksByLocation(None)

    location = PatternScriptEntities.readConfigFile('PT')['PL']
    toLocation = PatternScriptEntities.LM.getLocationByName(unicode(location, PatternScriptEntities.ENCODING))

    locos = switchList['locations'][0]['tracks'][0]['locos']
    for loco in locos:
        setTrack = switchList['locations'][0]['tracks'][0]['trackName']
        userInput = unicode(textBoxEntry[i].getText(), PatternScriptEntities.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = userInput

        toTrack = toLocation.getTrackByName(setTrack, None)

        rollingStock = PatternScriptEntities.EM.getByRoadAndNumber(loco['Road'], loco['Number'])
        if ignoreTrackLength:
            setResult = rollingStock.setLocation(toLocation, toTrack, True)
        else:
            setResult = rollingStock.setLocation(toLocation, toTrack)

        if setResult == 'okay':
            setCount += 1
        i += 1
    # PatternScriptEntities.EMX.save()

    cars = switchList['locations'][0]['tracks'][0]['cars']
    for car in cars:
        setTrack = switchList['locations'][0]['tracks'][0]['trackName']
        userInput = unicode(textBoxEntry[i].getText(), PatternScriptEntities.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = userInput

        toTrack = toLocation.getTrackByName(setTrack, None)

        rollingStock = PatternScriptEntities.CM.getByRoadAndNumber(car['Road'], car['Number'])
        # setResult = rollingStock.setLocation(toLocation, toTrack)
        setResult = ''
        x = toTrack.isRollingStockAccepted(rollingStock)
        if ignoreTrackLength:
            if x == 'okay':
                setResult = rollingStock.setLocation(toLocation, toTrack, True)

        if setResult == 'okay':
            rsUpdate(toTrack, rollingStock)
            scheduleUpdate(toTrack, rollingStock)
            setCount += 1
        i += 1
    # PatternScriptEntities.CMX.save()

    _psLog.info('Rolling stock count: ' + str(setCount) + ', processed.')

    return

# def parseSetTo(setTo):
#     """Moved to PatternScriptEntities """
#
#     x = setTo.split('[')
#     y = x[1].split(']')
#
#     return y[0]

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

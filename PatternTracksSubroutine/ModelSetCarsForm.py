# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Process methods for the Set Cars Form for Track X form"""

from opsEntities import PSE
from PatternTracksSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ModelSetCarsForm'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.PT.ModelSetCarsForm')

def writeToJson(setCarsForm):
    """Mini controller that writes the set cars form to json.
        Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.switchListButton
        ControllerSetCarsForm.CreateSetCarsFormGui.setRsButton
        """

    reportTitle = PSE.BUNDLE['Switch List for Track']
    fileName = reportTitle + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    switchListReport = PSE.dumpJson(setCarsForm)
    PSE.genericWriteReport(targetPath, switchListReport)

    return

def setRsButton(textBoxEntry):
    """Mini controller that moves the selected RS to the selected track.
        Subject to track length and RS type restrictions.
        Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.setRsButton
        """

    _psLog.debug('setRsButton')

    reportTitle = PSE.BUNDLE['Switch List for Track']
    fileName = reportTitle + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    switchList = PSE.genericReadReport(targetPath)
    switchList = PSE.loadJson(switchList)

    moveRollingStock(switchList, textBoxEntry)

    return

def o2oButton(ptSetCarsForm):
    """Mini controller that appends the ptSetCarsForm to o2o Work Events.json.
        Used by:
        ControllerptSetCarsForm.CreateptSetCarsFormGui.o2oButton
        """
    reportTitle = PSE.BUNDLE['o2o Work Events']
    fileName = reportTitle + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
# Load the existing o2o switch list
    o2oSwitchList = PSE.genericReadReport(targetPath)
    o2oSwitchList = PSE.loadJson(o2oSwitchList)
# Append cars and locos from ptSetCarsForm
    o2oSwitchListCars = o2oSwitchList['locations'][0]['tracks'][0]['cars']
    ptSetCarsFormCars = ptSetCarsForm['locations'][0]['tracks'][0]['cars']
    o2oSwitchList['locations'][0]['tracks'][0]['cars'] = o2oSwitchListCars + ptSetCarsFormCars

    o2oSwitchListLocos = o2oSwitchList['locations'][0]['tracks'][0]['locos']
    ptSetCarsFormLocos = ptSetCarsForm['locations'][0]['tracks'][0]['locos']
    o2oSwitchList['locations'][0]['tracks'][0]['locos'] = o2oSwitchListLocos + ptSetCarsFormLocos
# Write the appended file
    o2oSwitchList = PSE.dumpJson(o2oSwitchList)
    PSE.genericWriteReport(targetPath, o2oSwitchList)

    return

def moveRollingStock(switchList, textBoxEntry):
    """Similar to:
        ViewEntities.merge
        """

    setCount = 0
    i = 0

    ignoreTrackLength = PSE.readConfigFile('PT')['PI']

    allTracksAtLoc = PSE.getTracksNamesByLocation(None)

    location = PSE.readConfigFile('PT')['PL']
    toLocation = PSE.LM.getLocationByName(unicode(location, PSE.ENCODING))

    locos = switchList['locations'][0]['tracks'][0]['locos']
    for loco in locos:
        setTrack = switchList['locations'][0]['tracks'][0]['trackName']
        userInput = unicode(textBoxEntry[i].getText(), PSE.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = userInput

        toTrack = toLocation.getTrackByName(setTrack, None)

        rollingStock = PSE.EM.getByRoadAndNumber(loco['Road'], loco['Number'])
        setResult = rollingStock.setLocation(toLocation, toTrack)
        if ignoreTrackLength and toTrack.isTypeNameAccepted(loco['Type']):
            setResult = rollingStock.setLocation(toLocation, toTrack, True)

        if setResult == 'okay':
            setCount += 1
        i += 1

    cars = switchList['locations'][0]['tracks'][0]['cars']
    for car in cars:
        setTrack = switchList['locations'][0]['tracks'][0]['trackName']
        userInput = unicode(textBoxEntry[i].getText(), PSE.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = userInput

        toTrack = toLocation.getTrackByName(setTrack, None)

        rollingStock = PSE.CM.getByRoadAndNumber(car['Road'], car['Number'])
        setResult = rollingStock.setLocation(toLocation, toTrack)
        setResult = ''
        if ignoreTrackLength and toTrack.isTypeNameAccepted(car['Type']):
            setResult = rollingStock.setLocation(toLocation, toTrack, True)

        if setResult == 'okay':
            rsUpdate(toTrack, rollingStock)
            scheduleUpdate(toTrack, rollingStock)
            setCount += 1
        i += 1

    _psLog.info('Rolling stock count: ' + str(setCount) + ', processed.')

    return

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

    schedule = PSE.SM.getScheduleByName(toTrack.getScheduleName())
    if schedule and PSE.readConfigFile('PT')['AS']:
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

    _psLog.debug('testValidityOfForm')

    locoCount = len(setCarsForm['locations'][0]['tracks'][0]['locos'])
    carCount = len(setCarsForm['locations'][0]['tracks'][0]['cars'])

    if len(textBoxEntry) == locoCount + carCount:
        return True
    else:
        _psLog.critical('mismatched input list and car roster lengths')
        return False

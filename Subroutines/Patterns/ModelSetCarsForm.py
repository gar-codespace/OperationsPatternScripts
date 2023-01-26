# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Process methods for the Set Cars Form for Track X form"""

from opsEntities import PSE
from Subroutines.Patterns import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.PT.ModelSetCarsForm')


def makeMergedForm(setCarsForm, buttonDict):
    """Called by:
        ControllerSetCarsForm.CreateSetCarsFormGui.o2oButton
        switchListButton
        """

    inputList = ModelEntities.makeUserInputList(buttonDict)
    mergedForm = ModelEntities.merge(setCarsForm, inputList)

    return mergedForm



def setRsToTrack():
    """Mini controller that moves the selected RS to the selected track.
        Subject to track length and RS type restrictions.
        Called by:
        ControllerSetCarsForm.CreateSetCarsFormGui.setRsButton
        """

    _psLog.debug('setRsButton')

    reportTitle = PSE.BUNDLE['Switch List for Track']
    fileName = reportTitle + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'Patterns', fileName)

    switchList = PSE.genericReadReport(targetPath)
    switchList = PSE.loadJson(switchList)

    moveRollingStock(switchList)

    return

def o2oButton(ptSetCarsForm):
    """Mini controller that appends the ptSetCarsForm to o2o Work Events.json.
        Called by:
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

def moveRollingStock(switchList):
    """Similar to:
        ViewEntities.merge
        """

    setCount = 0
    i = -1

    configFile = PSE.readConfigFile()

    ignoreTrackLength = configFile['Patterns']['PI']
    applySchedule = configFile['Patterns']['AS']
    # location = configFile['Patterns']['PL']

    allTracksAtLoc = ModelEntities.getTrackNamesByLocation(None)

    toLocation = PSE.LM.getLocationByName(unicode(switchList['locations'][0]['locationName'], PSE.ENCODING))

    locos = switchList['locations'][0]['tracks'][0]['locos']
    for loco in locos:
        i += 1
        rollingStock = PSE.EM.getByRoadAndNumber(loco['Road'], loco['Number'])
        if not rollingStock:
            _psLog.warning('Not found; ' + car['Road'] + car['Number'])
            continue

        setTo = loco['Set_To'][1:-1].split(']')[0]

        if not setTo in allTracksAtLoc:
            continue

        toTrack = toLocation.getTrackByName(setTo, None)

        setResult = rollingStock.setLocation(toLocation, toTrack)
        if ignoreTrackLength and toTrack.isTypeNameAccepted(loco['Type']):
            setResult = rollingStock.setLocation(toLocation, toTrack, True)

        if setResult == 'okay':
            setCount += 1
        
    cars = switchList['locations'][0]['tracks'][0]['cars']
    for car in cars:
        i += 1
        rollingStock = PSE.CM.getByRoadAndNumber(car['Road'], car['Number'])
        if not rollingStock:
            _psLog.warning('Not found; ' + car['Road'] + car['Number'])
            continue

        setTo = car['Set_To'][1:-1].split(']')[0]
        
        if not setTo in allTracksAtLoc:
            continue

        toTrack = toLocation.getTrackByName(setTo, None)

        setResult = rollingStock.setLocation(toLocation, toTrack)
        if ignoreTrackLength and toTrack.isTypeNameAccepted(car['Type']):
            setResult = rollingStock.setLocation(toLocation, toTrack, True)

        if setResult == 'okay':
            rsUpdate(toTrack, rollingStock)
            if applySchedule:
                scheduleUpdate(toTrack, rollingStock)
            setCount += 1

    _psLog.info('Rolling stock count: ' + str(setCount) + ', processed.')

    return

def rsUpdate(toTrack, rollingStock):
    """Called by:
        moveRollingStock
        """

    if toTrack.getTrackType() == 'Spur':
        rollingStock.setMoves(rollingStock.getMoves() + 1)

    return

def scheduleUpdate(toTrack, rollingStock):
    """If the to-track is a spur, try to set the load/empty requirement for the track.
        Called by:
        moveRollingStock
        """
    try:
        schedule = PSE.SM.getScheduleByName(toTrack.getScheduleName())
    except:
        return

    carType = rollingStock.getTypeName()
    rollingStock.setLoadName(schedule.getItemByType(carType).getShipLoadName())
    rollingStock.setDestination(schedule.getItemByType(carType).getDestination(), schedule.getItemByType(carType).getDestinationTrack(), True) # force set dest
    schedule.getItemByType(carType).setHits(schedule.getItemByType(carType).getHits() + 1)

    return

def testValidityOfForm(setCarsForm, textBoxEntry):
    """Checks that both submitted forms are the same length
        Called by:
        ControllerSetCarsForm.CreateSetCarsFormGui.quickCheck
        """

    _psLog.debug('testValidityOfForm')

    locoCount = len(setCarsForm['locations'][0]['tracks'][0]['locos'])
    carCount = len(setCarsForm['locations'][0]['tracks'][0]['cars'])

    if len(textBoxEntry) == locoCount + carCount:
        return True
    else:
        _psLog.critical('Mismatched input list and car roster lengths')
        PSE.openOutputFrame(PSE.BUNDLE['FAIL: Mismatched input list and car roster lengths'])
        return False

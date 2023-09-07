# coding=utf-8
# © 2023 Greg Ritacco

"""
Methods for the Set Cars Form for Track X form
"""

from opsEntities import PSE
from Subroutines.Patterns import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.PT.ModelSetCarsForm')

def appendSwitchList(mergedForm):
    """
    Appends switch lists into one form to make the ops-switch-list file.
    Also used by o2o.
    """

    fileName = PSE.getBundleItem('ops-switch-list') + '.json'    
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    currentWorkList = PSE.jsonLoadS(PSE.genericReadReport(targetPath))

    currentWorkList['tracks'].append(mergedForm['tracks'][0])

    currentWorkList = PSE.dumpJson(currentWorkList)
    PSE.genericWriteReport(targetPath, currentWorkList)

    return

def formIsValid(setCarsForm, textBoxEntry):
    """
    Checks that both submitted forms are the same length
    Called by:
    ControllerSetCarsForm.CreateSetCarsForm.quickCheck
    """

    _psLog.debug('testValidityOfForm')

    locoCount = len(setCarsForm['tracks'][0]['locos'])
    carCount = len(setCarsForm['tracks'][0]['cars'])

    if len(textBoxEntry) == locoCount + carCount:
        return True
    else:
        return False

def makeMergedForm(setCarsForm, buttonDict):
    """
    Called by:
    ControllerSetCarsForm.CreateSetCarsForm.o2oButton
    switchListButton
    """

    inputList = ModelEntities.makeUserInputList(buttonDict)
    mergedForm = ModelEntities.merge(setCarsForm, inputList)

    return mergedForm

def moveRollingStock(switchList):
    """
    """

    configFile = PSE.readConfigFile()

    ignoreTrackLength = configFile['Patterns']['PI']
    applySchedule = configFile['Patterns']['AS']
    allTracksAtLoc = ModelEntities.getTrackNamesByLocation(None)
    toLocation = PSE.LM.getLocationByName(configFile['Patterns']['PL'])

    setCount = 0
    i = -1
    locos = switchList['tracks'][0]['locos']
    for loco in locos:
        i += 1
        rollingStock = PSE.EM.getByRoadAndNumber(loco[PSE.SB.handleGetMessage('Road')], loco[PSE.SB.handleGetMessage('Number')])
        if not rollingStock:
            _psLog.warning('Not found; ' + car[PSE.SB.handleGetMessage('Road')] + car[PSE.SB.handleGetMessage('Number')])
            continue

        setTo = loco['setTo'][1:-1].split(']')[0]
        if setTo == PSE.getBundleItem('Hold') or setTo not in allTracksAtLoc:
            continue

        toTrack = toLocation.getTrackByName(setTo, None)

        setResult = rollingStock.setLocation(toLocation, toTrack)
        if ignoreTrackLength and toTrack.isTypeNameAccepted(loco[PSE.SB.handleGetMessage('Type')]):
            setResult = rollingStock.setLocation(toLocation, toTrack, True)

        if setResult == 'okay':
            setCount += 1
        
    cars = switchList['tracks'][0]['cars']
    for car in cars:
        i += 1
        rollingStock = PSE.CM.getByRoadAndNumber(car[PSE.SB.handleGetMessage('Road')], car[PSE.SB.handleGetMessage('Number')])
        if not rollingStock:
            _psLog.warning('Not found; ' + car[PSE.SB.handleGetMessage('Road')] + car[PSE.SB.handleGetMessage('Number')])
            continue

        setTo = car['setTo'][1:-1].split(']')[0]
        if setTo == PSE.getBundleItem('Hold') or setTo not in allTracksAtLoc:
            continue
        
        toTrack = toLocation.getTrackByName(setTo, None)

        setResult = rollingStock.setLocation(toLocation, toTrack)
        if ignoreTrackLength and toTrack.isTypeNameAccepted(car[PSE.SB.handleGetMessage('Type')]):
            setResult = rollingStock.setLocation(toLocation, toTrack, True)

        if setResult == 'okay':
            rsUpdate(toTrack, rollingStock)
            if applySchedule:
                scheduleUpdate(toTrack, rollingStock)
            setCount += 1

    _psLog.info('Rolling stock count: ' + str(setCount) + ', processed.')

    return

def rsUpdate(toTrack, rollingStock):
    """
    Called by:
    moveRollingStock
    """

    if toTrack.getTrackType() == 'Spur':
        rollingStock.setMoves(rollingStock.getMoves() + 1)

    return

def scheduleUpdate(toTrack, rollingStock):
    """
    If the to-track is a spur, try to set the load/empty requirement for the track.
    Called by:
    moveRollingStock
    """

    if toTrack.getTrackType() != 'Spur':
        return

    try:
        schedule = PSE.SM.getScheduleByName(toTrack.getScheduleName())
    except:
        print('Exception at: Patterns.Model.scheduleUpdate')
        return

    carType = rollingStock.getTypeName()
    rollingStock.setLoadName(schedule.getItemByType(carType).getShipLoadName())
    rollingStock.setDestination(schedule.getItemByType(carType).getDestination(), schedule.getItemByType(carType).getDestinationTrack(), True) # force set dest
    schedule.getItemByType(carType).setHits(schedule.getItemByType(carType).getHits() + 1)

    return

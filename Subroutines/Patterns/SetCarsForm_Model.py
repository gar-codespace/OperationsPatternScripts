# coding=utf-8
# © 2023 Greg Ritacco

"""
Methods for the Set Cars Form for Track X form
"""

from opsEntities import PSE
from Subroutines.Patterns import View
from Subroutines.Patterns import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.PT.ModelSetCarsForm')

def formIsValid(setCarsForm, textBoxEntry):
    """
    Checks that both submitted forms are the same length
    Called by:
    ControllerSetCarsForm.CreateSetCarsForm.quickCheck
    """

    _psLog.debug('testValidityOfForm')

    locoCount = len(setCarsForm['locations'][0]['tracks'][0]['locos'])
    carCount = len(setCarsForm['locations'][0]['tracks'][0]['cars'])

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

def setRsToTrack():
    """
    Subject to track length and RS type restrictions.
    Called by:
    ControllerSetCarsForm.CreateSetCarsForm.setRsButton
    """

    _psLog.debug('setRsButton')

    reportTitle = PSE.getBundleItem('ops-switch-list')
    fileName = reportTitle + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    switchList = PSE.genericReadReport(targetPath)
    switchList = PSE.loadJson(switchList)

    moveRollingStock(switchList)

    return

def moveRollingStock(switchList):
    """
    Similar to:
    ViewEntities.merge
    """

    configFile = PSE.readConfigFile()

    ignoreTrackLength = configFile['Patterns']['PI']
    applySchedule = configFile['Patterns']['AS']
    allTracksAtLoc = ModelEntities.getTrackNamesByLocation(None)
    toLocation = PSE.LM.getLocationByName(unicode(switchList['locations'][0]['locationName'], PSE.ENCODING))

    setCount = 0
    i = -1
    locos = switchList['locations'][0]['tracks'][0]['locos']
    for loco in locos:
        i += 1
        rollingStock = PSE.EM.getByRoadAndNumber(loco['road'], loco['number'])
        if not rollingStock:
            _psLog.warning('Not found; ' + car['road'] + car['number'])
            continue

        setTo = loco['Set_To'][1:-1].split(']')[0]

        if not setTo in allTracksAtLoc:
            continue

        toTrack = toLocation.getTrackByName(setTo, None)

        setResult = rollingStock.setLocation(toLocation, toTrack)
        if ignoreTrackLength and toTrack.isTypeNameAccepted(loco['carType']):
            setResult = rollingStock.setLocation(toLocation, toTrack, True)

        if setResult == 'okay':
            setCount += 1
        
    cars = switchList['locations'][0]['tracks'][0]['cars']
    for car in cars:
        i += 1
        rollingStock = PSE.CM.getByRoadAndNumber(car['road'], car['number'])
        if not rollingStock:
            _psLog.warning('Not found; ' + car['road'] + car['number'])
            continue

        setTo = car['Set_To'][1:-1].split(']')[0]
        
        if not setTo in allTracksAtLoc:
            continue

        toTrack = toLocation.getTrackByName(setTo, None)

        setResult = rollingStock.setLocation(toLocation, toTrack)
        if ignoreTrackLength and toTrack.isTypeNameAccepted(car['carType']):
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

def makeTextSwitchList(switchList):
    """
    Formats and displays the Switch List report.
    Called by:
    ControllerSetCarsForm.CreateSetCarsForm.switchListButton
    """

    _psLog.debug('maksSwitchList')

    PSE.makeReportItemWidthMatrix()

    reportHeader = View.makeTextReportHeader(switchList)
    reportLocations = PSE.getBundleItem('Switch List') + '\n\n'
    
    reportLocations += View.makeTextReportLocations(switchList, trackTotals=False)

    return reportHeader + reportLocations

def switchListAsCsv(textBoxEntry):
    """
    Track Pattern Report json is written as a CSV file
    Called by:
    ControllerSetCarsForm.CreateSetCarsForm.switchListButton
    """

    _psLog.debug('switchListAsCsv')
#  Get json data
    fileName = PSE.getBundleItem('ops-work-list') + '.json'    
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    trackPattern = PSE.genericReadReport(targetPath)
    trackPattern = PSE.loadJson(trackPattern)
# Process json data into CSV
    userInputList = ModelEntities.makeUserInputList(textBoxEntry)
    trackPattern = ModelEntities.merge(trackPattern, userInputList)

    trackPattern = makeMergedForm(trackPattern, textBoxEntry)
    trackPatternCsv = View.makeTrackPatternCsv(trackPattern)
# Write CSV data
    fileName = PSE.getBundleItem('ops-switch-list') + '.csv'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'csvSwitchLists', fileName)
    PSE.genericWriteReport(targetPath, trackPatternCsv)

    return

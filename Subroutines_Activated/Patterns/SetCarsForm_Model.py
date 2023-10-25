# coding=utf-8
# © 2023 Greg Ritacco

"""
Methods for the Set Cars Form for Track X form
"""

from opsEntities import PSE
from Subroutines_Activated.Patterns import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.PT.ModelSetCarsForm')

def appendSwitchList(mergedForm):
    """
    Appends switch lists into one form to make the ops-Switch List file.
    Replaces an existing track.
    """

    fileName = PSE.getBundleItem('ops-Switch List') + '.json'    
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    currentWorkList = PSE.jsonLoadS(PSE.genericReadReport(targetPath))

    trackLookUp = []
    for i, trackName in enumerate(currentWorkList['locations']):
        trackLookUp.append((trackName['userName'], i))

    index = [x[1] for x in trackLookUp if mergedForm['locations'][0]['userName'] == x[0]]
    if index:
        currentWorkList['locations'].pop(index[0])

    currentWorkList['locations'].append(mergedForm['locations'][0])

    currentWorkList = PSE.dumpJson(currentWorkList)
    PSE.genericWriteReport(targetPath, currentWorkList)

    return

def getUserInputList(textBoxEntry):

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), PSE.ENCODING))

    return userInputList

def mergeSetCarsForm(setCarsForm, inputList):
    """
    Merge the values in textBoxEntry into the destination field of the set cars form data.
    """

    location = PSE.readConfigFile('Patterns')['PL']
    allTracksAtLoc = ModelEntities.getTrackNamesByLocation(None)
    currentTrack = setCarsForm['locations'][0]['userName']

    i = 0

    for loco in setCarsForm['locations'][0]['engines']['add']:
    # Skip locos that are assigned to a train
        if loco['trainName']:
            i += 1
            continue
        userInput = unicode(inputList[i], PSE.ENCODING)
        if userInput in allTracksAtLoc:
            loco['destination']['userName'] = location
            loco['destination']['track']['userName'] = userInput
        else:
            loco['destination']['userName'] = location
            loco['destination']['track']['userName'] = currentTrack

        i += 1

    for car in setCarsForm['locations'][0]['cars']['add']:
    # Skip cars that are assigned to a train
        if car['trainName']:
            i += 1
            continue

        userInput = unicode(inputList[i], PSE.ENCODING)
        if userInput in allTracksAtLoc:
            car['destination']['userName'] = location
            car['destination']['track']['userName'] = userInput
        else:
            car['destination']['userName'] = location
            car['destination']['track']['userName'] = currentTrack

        i += 1

    return setCarsForm

def moveRollingStock(switchList):
    """
    Set the rolling stock to the selected track.
    """

    configFile = PSE.readConfigFile()
    isSequence, sequenceHash = PSE.getSequenceHash()

    carSequence = 7001
    locoSequence = 7001

    ignoreTrackLength = configFile['Patterns']['PI']
    applySchedule = configFile['Patterns']['AS']
    allTracksAtLoc = ModelEntities.getTrackNamesByLocation(None)
    toLocation = PSE.LM.getLocationByName(configFile['Patterns']['PL'])

    setCount = 0
    i = -1
    locos = switchList['locations'][0]['engines']['add']
    for loco in locos:
        i += 1
        rollingStock = PSE.EM.getByRoadAndNumber(loco['road'], loco['number'])
        if not rollingStock:
            _psLog.warning('Not found; ' + car['road'] + car['number'])
            continue

        setTo = loco['destination']['track']['userName']
        toTrack = toLocation.getTrackByName(setTo, None)

        setResult = rollingStock.setLocation(toLocation, toTrack)
        if ignoreTrackLength and toTrack.isTypeNameAccepted(loco['carType']):
            setResult = rollingStock.setLocation(toLocation, toTrack, True)

        if setResult == 'okay':
            if sequenceHash:
                rsID = rollingStock.getRoadName() + ' ' + rollingStock.getNumber()
                sequenceHash['locos'].update({rsID:locoSequence})
                locoSequence += 1
            setCount += 1
        
    cars = switchList['locations'][0]['cars']['add']
    for car in cars:
        i += 1
        rollingStock = PSE.CM.getByRoadAndNumber(car['road'], car['number'])
        if not rollingStock:
            _psLog.warning('Not found; ' + car['road'] + car['number'])
            continue

        setTo = car['destination']['track']['userName']
        toTrack = toLocation.getTrackByName(setTo, None)

        setResult = rollingStock.setLocation(toLocation, toTrack)
        if ignoreTrackLength and toTrack.isTypeNameAccepted(car['carType']):
            setResult = rollingStock.setLocation(toLocation, toTrack, True)

        if setResult == 'okay':
            rsUpdate(toTrack, rollingStock)
            if applySchedule:
                scheduleUpdate(toTrack, rollingStock)
            if isSequence:
                rsID = rollingStock.getRoadName() + ' ' + rollingStock.getNumber()
                sequenceHash['cars'].update({rsID:carSequence})
                carSequence += 1

            setCount += 1

    if isSequence:
        sequenceFilePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'rsSequenceData.json')
        PSE.genericWriteReport(sequenceFilePath, PSE.dumpJson(sequenceHash))
        resequenceTracks()

    _psLog.info('Rolling stock count: ' + str(setCount) + ', processed.')

    return

def resequenceTracks():
    
    carHash = {}
    _, sequenceHash = PSE.getSequenceHash()
    allCars = PSE.CM.getList()
    for car in allCars:
        carID = car.getRoadName() + ' ' + car.getNumber()
        carTrack = car.getTrackName()
        try:
            carSequence = sequenceHash['cars'][carID]
        except:
            carSequence = 8888
        carHash[carID] = (carTrack, carSequence)

    allTracksAtLoc = ModelEntities.getTrackNamesByLocation(None)
    for track in allTracksAtLoc:
        trackHash = []
        for id, data in carHash.items():
            if track == data[0]:
                trackHash.append((id, data[1]))

        trackHash.sort(key=lambda row: row[1])
        sequence = 8001
        for tuple in trackHash:
            sequenceHash['cars'].update({tuple[0]:sequence})
            sequence += 1

    sequenceFilePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'rsSequenceData.json')
    PSE.genericWriteReport(sequenceFilePath, PSE.dumpJson(sequenceHash))

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

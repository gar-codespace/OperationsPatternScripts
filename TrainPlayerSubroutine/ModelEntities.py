# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.ModelEntities'
SCRIPT_REV = 20220101

def getLoadTypeRubric(xmlFile, target):

    loadTypeXml = PatternScriptEntities.xmlWrangler('OperationsCarRoster')

    loadList = loadTypeXml.getXml('./loads/load')
    if not loadList:
        return False

    loadTypeRubric = {}
    for item in loadList:
        for load in item:
            tempKey = item.attrib.get('type') + load.attrib.get('name')
            tempValue = load.attrib.get('loadType')
            loadTypeRubric[tempKey] = tempValue

    return loadTypeRubric


def parseJmriLocations(location, loadTypeRubric):
    """called from JmriTranslationToTp"""

    tpLocation = {}
    tpLocation['locationName'] = location['userName']
    tpLocation['tracks'] = []

    locoList = []
    carList = []
    for loco in location[u'engines'][u'add']:
        line = parseRollingStockAsDict(loco)
        line['PUSO'] = 'PL'
        line[PatternScriptEntities.SB.handleGetMessage('Load_Type')] = 'O'
        locoList.append(line)
    for loco in location[u'engines'][u'remove']:
        line = parseRollingStockAsDict(loco)
        line['PUSO'] = 'SL'
        line[PatternScriptEntities.SB.handleGetMessage('Load_Type')] = 'O'
        locoList.append(line)
    for car in location['cars']['add']:
        line = parseRollingStockAsDict(car)
        line['PUSO'] = 'PC'
        tempKey = car['carType'] + car['load']
        try:
            line[PatternScriptEntities.SB.handleGetMessage('Load_Type')] = loadTypeRubric[tempKey]
        except:
            line[PatternScriptEntities.SB.handleGetMessage('Load_Type')] = 'U'
        carList.append(line)
    for car in location['cars']['remove']:
        line = parseRollingStockAsDict(car)
        line['PUSO'] = 'SC'
        tempKey = car['carType'] + car['load']
        try:
            line[PatternScriptEntities.SB.handleGetMessage('Load_Type')] = loadTypeRubric[tempKey]
        except:
            line[PatternScriptEntities.SB.handleGetMessage('Load_Type')] = 'U'
        carList.append(line)

    locationTrack = {}
    locationTrack['locos'] = locoList
    locationTrack['cars'] = carList
    locationTrack['trackName'] = 'Track Name'
    locationTrack['length'] = 0

    tpLocation['tracks'].append(locationTrack)

    return tpLocation

def parseRollingStockAsDict(rS):

    rsDict = {}

    rsDict[PatternScriptEntities.SB.handleGetMessage('Road')] = unicode(rS[u'road'], PatternScriptEntities.ENCODING)
    rsDict[PatternScriptEntities.SB.handleGetMessage('Number')] = rS[u'number']

    try:
        rsDict[PatternScriptEntities.SB.handleGetMessage('Model')] = rS[u'model']
    except KeyError:
        rsDict[PatternScriptEntities.SB.handleGetMessage('Model')] = 'N/A'

    try:
        rsDict[PatternScriptEntities.SB.handleGetMessage('Type')] = rS[u'carType'] + "-" + rS[u'carSubType']
    except:
        rsDict[PatternScriptEntities.SB.handleGetMessage('Type')] = rS[u'carType']

    try:
        rsDict[PatternScriptEntities.SB.handleGetMessage('Load')] = rS['load']
    except:
        rsDict[PatternScriptEntities.SB.handleGetMessage('Load')] = 'O'

    rsDict[PatternScriptEntities.SB.handleGetMessage('Length')] = rS[u'length']
    rsDict[PatternScriptEntities.SB.handleGetMessage('Weight')] = rS[u'weightTons']
    rsDict[PatternScriptEntities.SB.handleGetMessage('Track')] = unicode(rS[u'location'][u'track'][u'userName'], PatternScriptEntities.ENCODING)
    rsDict[u'Set to'] = unicode(rS[u'destination'][u'userName'], PatternScriptEntities.ENCODING) \
        + u';' + unicode(rS[u'destination'][u'track'][u'userName'], PatternScriptEntities.ENCODING)

    try:
        jFinalDestination = unicode(rS[u'finalDestination'][u'userName'], PatternScriptEntities.ENCODING)
    except:
        jFinalDestination = PatternScriptEntities.BUNDLE['No final destination']

    try:
        jFinalTrack = unicode(rS[u'finalDestination'][u'track'][u'userName'], PatternScriptEntities.ENCODING)
    except:
        jFinalTrack = PatternScriptEntities.BUNDLE['No FD track']

    rsDict[PatternScriptEntities.SB.handleGetMessage('Final_Dest')] = jFinalDestination
    # rsDict[u'FD Track'] = jFinalTrack
    rsDict[PatternScriptEntities.SB.handleGetMessage('FD&Track')] = jFinalDestination + u';' + jFinalTrack
    return rsDict

def getTpInventory():

    tpInventoryPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() \
        + "AppData\Roaming\TrainPlayer\Reports\TrainPlayer Export - Inventory.txt"

    try: # Catch TrainPlayer not installed
        tpInventory = PatternScriptEntities.genericReadReport(tpInventoryPath).split('\n')

    except IOError:
        tpInventory = ''

    return tpInventory

def makeTpInventoryList(tpInventory):
    '''Returns (CarId,TrackLabel)'''

    tpInventoryList = []

    for item in tpInventory:
        lineItem = []
        carAttribs = item.split(':')

        carRoad, carNumber = parseCarId(carAttribs[0])
        lineItem.append(carRoad)
        lineItem.append(carNumber)

        lineItem.append(carAttribs[1]) # AAR

        locationTrack = carAttribs[2].split(';')
        lineItem.append(locationTrack[0]) # Location
        lineItem.append(locationTrack[1]) # Track

        lineItem.append(carAttribs[3]) # Loaded
        lineItem.append(carAttribs[4]) # Kernel

        tpInventoryList.append(lineItem)

    return tpInventoryList

def parseCarId(carId):

    carRoad = ''
    carNumber = ''

    for character in carId:
        if character.isdigit():
            carNumber += character
        else:
            carRoad += character

    return carRoad, carNumber

def updateEngine(lineItem):

    engine = PatternScriptEntities.EM.newRS(lineItem[0], lineItem[1])
    location = PatternScriptEntities.LM.getLocationByName(lineItem[3])
    track = location.getTrackByName(lineItem[4], None)
    engine.setLocation(location, track)

    return

def updateCar(lineItem):

    car = PatternScriptEntities.CM.newRS(lineItem[0], lineItem[1])
    location = PatternScriptEntities.LM.getLocationByName(lineItem[3])
    track = location.getTrackByName(lineItem[4], None)
    car.setLocation(location, track)
    print('Rolling Stock ', car.getRoadName(), ' set to: ' , location, track)

    return



# def makeJmriLocationHash():
#     '''Format: {TrackComment : (LocationName, TrackName)}'''
#
#     allLocations = PatternScriptEntities.getAllLocations()
#     locationHash = {}
#
#     for location in allLocations:
#         locationObject = PatternScriptEntities.LM.getLocationByName(location)
#         allTracks = locationObject.getTracksList()
#         for track in allTracks:
#             locationHash[track.getComment()] = (locationObject.getName(),track.getName())
#
#     return locationHash

def getSetToLocationAndTrack(jmriHashResult):
    '''jmriHashResult is a tuple (location, track) returned by looking up
    TrainPlayer track comment from makeJmriLocationHash
    '''

    try:
        locationTrack = jmriHashResult[0]
        jmriLocation = PatternScriptEntities.LM.getLocationByName(jmriHashResult[0])
        jmriTrack = jmriLocation.getTrackByName(jmriHashResult[1], None)
    except KeyError:
        return
    except AttributeError:
        return

    return jmriLocation, jmriTrack

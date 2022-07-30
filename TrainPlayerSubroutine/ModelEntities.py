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

# def getTpInventory():
#
#     tpInventoryPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() \
#         + "AppData\Roaming\TrainPlayer\Reports\TrainPlayer Export - Inventory.txt"
#
#     if PatternScriptEntities.JAVA_IO.File(tpInventoryPath).isFile():
#         tpInventory = PatternScriptEntities.genericReadReport(tpInventoryPath).split('\n')
#         return tpInventory
#     else:
#         return

def getTpExport(fileName):
    """Generic file getter"""

    fullPath = "AppData\\Roaming\\TrainPlayer\\Reports\\" + fileName
    tpExportPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() + fullPath

    if PatternScriptEntities.JAVA_IO.File(tpExportPath).isFile():
        tpExport = PatternScriptEntities.genericReadReport(tpExportPath).split('\n')
        return tpExport
    else:
        return
    return

def addNewRs(rsAttribs):
    """rsAttribs format: RoadNumber, AAR, Location, Track, Loaded, Kernel, Type
    Note: TrainPlayer AAR is used as JMRI type name
    Note: TrainPlayer Type is used as JMRI engine model
    """

    roadName, roadNumber = parseCarId(rsAttribs[0])

    if rsAttribs[1].startswith('E') and rsAttribs[1] != 'ET':
        PatternScriptEntities.EM.newRS(roadName, roadNumber)
        rs = PatternScriptEntities.EM.getByRoadAndNumber(roadName, roadNumber)
        rs.setModel(rsAttribs[6])

    else:
        PatternScriptEntities.CM.newRS(roadName, roadNumber)
        rs = PatternScriptEntities.CM.getByRoadAndNumber(roadName, roadNumber)

    rs.setTypeName(rsAttribs[1])
    rs.setLength("40")
    rs.setColor("Color")
    if rsAttribs[1] == '1':
        rs.setLoad('L')

    return

def parseCarId(carId):

    rsRoad = ''
    rsNumber = ''

    for character in carId:
        if character.isdigit():
            rsNumber += character
        else:
            rsRoad += character

    return rsRoad, rsNumber

def getSetToLocationAndTrack(location, track):

    locationObj = PatternScriptEntities.LM.getLocationByName(location)
    trackObj = locationObj.getTrackByName(track, None)

    return locationObj, trackObj

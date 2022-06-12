# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ModelEntities'
SCRIPT_REV = 20220101

def testSelectedItem(selectedItem):
    """Catches user edit of locations"""

    allLocations = PatternScriptEntities.getAllLocations() #List of strings
    if selectedItem in allLocations:
        return selectedItem
    else:
        return allLocations[0]

def getAllTracksForLocation(location):
    """Sets all tracks to false"""

    jmriTrackList = PatternScriptEntities.LM.getLocationByName(location).getTracksByNameList(None)
    trackDict = {}
    for track in jmriTrackList:
        trackDict[unicode(track.getName(), PatternScriptEntities.ENCODING)] = False

    return trackDict

def initializeConfigFile():
    """initialize or reinitialize the pattern tracks part of the config file
    on first use, reset, or edit of a location name
    """

    newConfigFile = PatternScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['PT']
    allLocations  = getAllLocations()
    subConfigfile.update({'AL': allLocations})
    subConfigfile.update({'PL': allLocations[0]})
    subConfigfile.update({'PT': makeInitialTrackList(allLocations[0])})
    newConfigFile.update({'PT': subConfigfile})

    return newConfigFile

def getTracksByLocation(trackType):

    patternLocation = PatternScriptEntities.readConfigFile('PT')['PL']
    allTracksList = []
    try: # Catch on the fly user edit of config file error
        for track in PatternScriptEntities.LM.getLocationByName(patternLocation).getTracksByNameList(trackType):
            allTracksList.append(unicode(track.getName(), PatternScriptEntities.ENCODING))
        return allTracksList
    except AttributeError:
        return allTracksList

def updateTrackCheckBoxes(trackCheckBoxes):
    """Returns a dictionary of track names and their check box status"""

    dict = {}
    for item in trackCheckBoxes:
        dict[unicode(item.text, PatternScriptEntities.ENCODING)] = item.selected

    return dict

def getGenericTrackDetails(locationName, trackName):
    """The loco and car lists are sorted at this level, used to make the JSON file"""

    genericTrackDetails = {}
    genericTrackDetails['trackName'] = trackName
    genericTrackDetails['length'] =  PatternScriptEntities.LM.getLocationByName(locationName).getTrackByName(trackName, None).getLength()
    genericTrackDetails['locos'] = sortLocoList(getLocoListForTrack(trackName))
    genericTrackDetails['cars'] = sortCarList(getCarListForTrack(trackName))

    return genericTrackDetails

def sortLocoList(locoList):
    """backupConfigFile() is a bit of user edit protection
    Sort order of PatternScriptEntities.readConfigFile('PT')['SL'] is top down
    """

    sortLocos = PatternScriptEntities.readConfigFile('PT')['SL']
    for sortKey in sortLocos:
        locoList.sort(key=lambda row: row[sortKey])

    PatternScriptEntities.backupConfigFile()
    return locoList

def getRsOnTrains():
    """Make a list of all rolling stock that are on built trains"""

    builtTrainList = []
    for train in PatternScriptEntities.TM.getTrainsByStatusList():
        if train.isBuilt():
            builtTrainList.append(train)

    listOfAssignedRs = []
    for train in builtTrainList:
        listOfAssignedRs += PatternScriptEntities.CM.getByTrainList(train)
        listOfAssignedRs += PatternScriptEntities.EM.getByTrainList(train)

    return listOfAssignedRs

def getLocoListForTrack(track):
    """Creates a generic locomotive list for a track, used to make the JSON file"""

    location = PatternScriptEntities.readConfigFile('PT')['PL']
    locoList = getLocoObjects(location, track)

    return [getDetailsForLocoAsDict(loco) for loco in locoList]

def getLocoObjects(location, track):

    locoList = []
    allLocos = PatternScriptEntities.EM.getByModelList()

    return [loco for loco in allLocos if loco.getLocationName() == location and loco.getTrackName() == track]

def getDetailsForLocoAsDict(locoObject):
    """backupConfigFile() is a bit of user edit protection
    Mimics jmri.jmrit.operations.setup.Setup.getEngineAttributes()
    [u'Road', u'Number', u'Type', u'Model', u'Length', u'Weight', u'Consist',
    u'Owner', u'Track', u'Location', u'Destination', u'Comment']
    """

    listOfAssignedRs = getRsOnTrains()
    locoDetailDict = {}

    lineKey = PatternScriptEntities.SB.handleGetMessage('Road')
    locoDetailDict[lineKey] = locoObject.getRoadName()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Number')
    locoDetailDict[lineKey] = locoObject.getNumber()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Type')
    locoDetailDict[lineKey] = locoObject.getTypeName()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Model')
    locoDetailDict[lineKey] = locoObject.getModel()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Length')
    locoDetailDict[lineKey] = locoObject.getLength()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Weight')
    locoDetailDict[lineKey] = locoObject.getWeightTons()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Consist')
    try:
        locoDetailDict[lineKey] = locoObject.getConsist().getName()
    except:
        locoDetailDict[lineKey] = PatternScriptEntities.BUNDLE['Single']

    lineKey = PatternScriptEntities.SB.handleGetMessage('Owner')
    locoDetailDict[lineKey] = str(locoObject.getOwner())

    lineKey = PatternScriptEntities.SB.handleGetMessage('Track')
    locoDetailDict[lineKey] = locoObject.getTrackName()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Location')
    locoDetailDict[lineKey] = locoObject.getLocation().getName()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Destination')
    locoDetailDict[lineKey] = locoObject.getDestinationName()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Comment')
    locoDetailDict[lineKey] = locoObject.getComment()

# Not part of JMRI engine attributes
    lineKey = PatternScriptEntities.SB.handleGetMessage('Load')
    locoDetailDict[lineKey] = u'O'

    lineKey = PatternScriptEntities.SB.handleGetMessage('FD&Track')
    locoDetailDict[lineKey] = PatternScriptEntities.readConfigFile('PT')['DS']

    lineKey = PatternScriptEntities.BUNDLE['On Train']
    if locoObject in listOfAssignedRs: # Flag to mark if RS is on a built train
        locoDetailDict[lineKey] = True
    else:
        locoDetailDict[lineKey] = False

    lineKey = PatternScriptEntities.BUNDLE['Set to']
    locoDetailDict[lineKey] = '[  ] '

    locoDetailDict[u'PUSO'] = u'SL'

    locoDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getDropEngineMessageFormat

    PatternScriptEntities.backupConfigFile()
    return locoDetailDict

def sortCarList(carList):
    """backupConfigFile() is a bit of user edit protection
    Sort order of PatternScriptEntities.readConfigFile('PT')['SC'] is top down"""

    sortCars = PatternScriptEntities.readConfigFile('PT')['SC']
    for sortKey in sortCars:
        carList.sort(key=lambda row: row[sortKey])

    PatternScriptEntities.backupConfigFile()
    return carList

def getCarListForTrack(track):
    """A list of car attributes as a dictionary"""

    location = PatternScriptEntities.readConfigFile('PT')['PL']
    carList = getCarObjects(location, track)

    return [getDetailsForCarAsDict(car) for car in carList]

def getCarObjects(location, track):

    allCars = PatternScriptEntities.CM.getByIdList()

    return [car for car in allCars if car.getLocationName() == location and car.getTrackName() == track]

def getDetailsForCarAsDict(carObject):
    """backupConfigFile() is a bit of user edit protection
    Mimics jmri.jmrit.operations.setup.Setup.getCarAttributes()
    [u'Road', u'Number', u'Type', u'Length', u'Weight', u'Load', u'Load Type',
    u'Hazardous', u'Color', u'Kernel', u'Kernel Size', u'Owner', u'Track',
    u'Location', u'Destination', u'Dest&Track', u'Final Dest', u'FD&Track',
    u'Comment', u'SetOut Msg', u'PickUp Msg', u'RWE']
    """

    fdStandIn = PatternScriptEntities.readConfigFile('PT')

    listOfAssignedRs = getRsOnTrains()
    carDetailDict = {}

    lineKey = PatternScriptEntities.SB.handleGetMessage('Road')
    carDetailDict[lineKey] = carObject.getRoadName()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Number')
    carDetailDict[lineKey] = carObject.getNumber()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Type')
    carDetailDict[lineKey] = carObject.getTypeName()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Length')
    carDetailDict[lineKey] = carObject.getLength()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Weight')
    carDetailDict[lineKey] = carObject.getWeightTons()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Load')
    if carObject.isCaboose() or carObject.isPassenger():
        carDetailDict[lineKey] = u'O'
    else:
        carDetailDict[lineKey] = carObject.getLoadName()

    # lineKey = PatternScriptEntities.CB.handleGetMessage('Load Type ')
    # x = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarLoads.Bundle().handleGetMessage('Load Type')
    carDetailDict[u'Load Type'] = carObject.getLoadType()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Hazardous')
    carDetailDict[lineKey] = carObject.isHazardous()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Color')
    carDetailDict[lineKey] = carObject.getColor()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Kernel')
    carDetailDict[lineKey] = carObject.getKernelName()

    allCarObjects =  PatternScriptEntities.CM.getByIdList()
    for car in allCarObjects:
        i = 0
        if (car.getKernelName() == carObject.getKernelName()):
            i += 1
    # lineKey = PatternScriptEntities.SB.handleGetMessage('Kernel Size')
    carDetailDict[u'Kernel Size'] = str(i)

    lineKey = PatternScriptEntities.SB.handleGetMessage('Owner')
    carDetailDict[lineKey] = carObject.getOwner()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Track')
    carDetailDict[lineKey] = carObject.getTrackName()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Location')
    carDetailDict[lineKey] = carObject.getLocationName()

    lineKey1 = PatternScriptEntities.SB.handleGetMessage('Destination')
    lineKey2 = PatternScriptEntities.SB.handleGetMessage('Dest&Track')
    if not (carObject.getDestinationName()):
        carDetailDict[lineKey1] = fdStandIn['DS']
        carDetailDict[lineKey2] = fdStandIn['DT']
    else:
        carDetailDict[lineKey1] = carObject.getDestinationName()
        carDetailDict[lineKey2] = carObject.getDestinationName() \
                                     + ', ' + carObject.getDestinationTrackName()

    # lineKey1 = PatternScriptEntities.SB.handleGetMessage('Final Dest')
    lineKey2 = PatternScriptEntities.SB.handleGetMessage('FD&Track')
    if not (carObject.getFinalDestinationName()):
        carDetailDict[u'Final Dest'] = fdStandIn['FD']
        carDetailDict[lineKey2] = fdStandIn['FT']
    else:
        carDetailDict[u'Final Dest'] = carObject.getFinalDestinationName()
        carDetailDict[lineKey2] = carObject.getFinalDestinationName() \
                                   + ', ' + carObject.getFinalDestinationTrackName()

    # lineKey = PatternScriptEntities.SB.handleGetMessage('FD Track')
    if not carObject.getFinalDestinationTrackName():
        carDetailDict[u'FD Track'] = fdStandIn['FT']
    else:
        carDetailDict[u'FD Track'] = carObject.getFinalDestinationTrackName()

    lineKey = PatternScriptEntities.SB.handleGetMessage('Comment')
    carDetailDict[lineKey] = carObject.getComment()

    trackId =  PatternScriptEntities.LM.getLocationByName(carObject.getLocationName()).getTrackById(carObject.getTrackId())
    # lineKey = PatternScriptEntities.SB.handleGetMessage('SetOut Msg')
    carDetailDict[u'SetOut Msg'] = trackId.getCommentSetout()
    # lineKey = PatternScriptEntities.SB.handleGetMessage('PickUp Msg')
    carDetailDict[u'PickUp Msg'] = trackId.getCommentPickup()


    lineKey = PatternScriptEntities.SB.handleGetMessage('RWE')
    carDetailDict[lineKey] = carObject.getReturnWhenEmptyDestinationName()
# Not part of JMRI car attributes
    lineKey = PatternScriptEntities.BUNDLE['On Train']
    if carObject in listOfAssignedRs: # Flag to mark if RS is on a built train
        carDetailDict[lineKey] = True
    else:
        carDetailDict[lineKey] = False

    lineKey = PatternScriptEntities.BUNDLE['Set to']
    carDetailDict[lineKey] = '[  ] '

    carDetailDict[u'PUSO'] = u'SC'
    carDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat

    PatternScriptEntities.backupConfigFile()
    return carDetailDict

def makeGenericHeader():
    """A generic header info for any switch list, used to make the JSON file"""

    listHeader = {}
    listHeader['railroad'] = unicode(PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getRailroadName(), PatternScriptEntities.ENCODING)
    listHeader['trainName'] = u'Train Name Placeholder'
    listHeader['trainDescription'] = u'Train Description Placeholder'
    listHeader['trainComment'] = u'Train Comment Placeholder'
    listHeader['date'] = unicode(PatternScriptEntities.timeStamp(), PatternScriptEntities.ENCODING)
    listHeader['locations'] = []

    return listHeader

def writeWorkEventListAsJson(switchList):
    """The generic switch list is written as a json"""

    switchListName = switchList['trainDescription']
    switchListPath = PatternScriptEntities.PROFILE_PATH \
               + 'operations\\jsonManifests\\' + switchListName + '.json'
    switchListReport = PatternScriptEntities.dumpJson(switchList)

    PatternScriptEntities.genericWriteReport(switchListPath, switchListReport)
    return switchListName

def readJsonWorkEventList(workEventName):

    reportPath = PatternScriptEntities.PROFILE_PATH \
                 + 'operations\\jsonManifests\\' + workEventName + '.json'

    jsonEventList = PatternScriptEntities.genericReadReport(reportPath)

    textWorkEventList = PatternScriptEntities.loadJson(jsonEventList)

    return textWorkEventList

def makeInitialTrackList(location):

    trackDict = {}
    for track in PatternScriptEntities.LM.getLocationByName(location).getTracksByNameList(None):
        trackDict[unicode(track, PatternScriptEntities.ENCODING)] = False

    return trackDict

def makeCsvSwitchlist(trackPattern):
    # CSV writer does not support utf-8

    csvSwitchList = u'Operator,Description,Parameters\n' \
                    u'RT,Report Type,' + trackPattern['trainDescription'] + '\n' \
                    u'RN,Railroad Name,' + trackPattern['railroad'] + '\n' \
                    u'LN,Location Name,' + trackPattern['locations'][0]['locationName'] + '\n' \
                    u'PRNTR,Printer Name,\n' \
                    u'YPC,Yard Pattern Comment,' + trackPattern['trainComment'] + '\n' \
                    u'VT,Valid,' + trackPattern['date'] + '\n'
    for track in trackPattern['locations'][0]['tracks']: # There is only one location
        csvSwitchList += u'TN,Track name,' + unicode(track['trackName'], PatternScriptEntities.ENCODING) + '\n'
        for loco in track['locos']:
            csvSwitchList +=  loco['Set to'] + ',' \
                            + loco['PUSO'] + ',' \
                            + loco['Road'] + ',' \
                            + loco['Number'] + ',' \
                            + loco['Type'] + ',' \
                            + loco['Model'] + ',' \
                            + loco['Length'] + ',' \
                            + loco['Weight'] + ',' \
                            + loco['Consist'] + ',' \
                            + loco['Owner'] + ',' \
                            + loco['Track'] + ',' \
                            + loco['Location'] + ',' \
                            + loco['Destination'] + ',' \
                            + loco['Comment'] + ',' \
                            + loco['Load'] + ',' \
                            + loco['FD&Track'] + ',' \
                            + '\n'
        for car in track['cars']:
            csvSwitchList +=  car['Set to'] + ',' \
                            + car['PUSO'] + ',' \
                            + car['Road'] + ',' \
                            + car['Number'] + ',' \
                            + car['Type'] + ',' \
                            + car['Length'] + ',' \
                            + car['Weight'] + ',' \
                            + car['Load'] + ',' \
                            + car['Track'] + ',' \
                            + car['FD&Track'] + ',' \
                            + car['Load Type'] + ',' \
                            + str(car['Hazardous']) + ',' \
                            + car['Color'] + ',' \
                            + car['Kernel'] + ',' \
                            + car['Kernel Size'] + ',' \
                            + car['Owner'] + ',' \
                            + car['Location'] + ',' \
                            + car['Destination'] + ',' \
                            + car['Dest&Track'] + ',' \
                            + car['Final Dest'] + ',' \
                            + car['Comment'] + ',' \
                            + car['SetOut Msg'] + ',' \
                            + car['PickUp Msg'] + ',' \
                            + car['RWE'] \
                            + '\n'

    return trackPattern['trainDescription'], csvSwitchList

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
        translatedkey = PatternScriptEntities.SB.handleGetMessage(sortKey)
        locoList.sort(key=lambda row: row[translatedkey])

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
    Dealers choice, either:
        PatternScriptEntities.J_BUNDLE.ROAD
        or
        PatternScriptEntities.SB.handleGetMessage('Road')
    """

    listOfAssignedRs = getRsOnTrains()
    locoDetailDict = {}

    locoDetailDict[PatternScriptEntities.J_BUNDLE.ROAD] = locoObject.getRoadName()
    locoDetailDict[PatternScriptEntities.J_BUNDLE.NUMBER] = locoObject.getNumber()
    locoDetailDict[PatternScriptEntities.J_BUNDLE.TYPE] = locoObject.getTypeName()
    locoDetailDict[PatternScriptEntities.J_BUNDLE.MODEL] = locoObject.getModel()
    locoDetailDict[PatternScriptEntities.J_BUNDLE.LENGTH] = locoObject.getLength()
    locoDetailDict[PatternScriptEntities.J_BUNDLE.WEIGHT] = locoObject.getWeightTons()

    try:
        locoDetailDict[PatternScriptEntities.J_BUNDLE.CONSIST] = locoObject.getConsist().getName()
    except:
        locoDetailDict[PatternScriptEntities.J_BUNDLE.CONSIST] = PatternScriptEntities.BUNDLE['Single']

    locoDetailDict[PatternScriptEntities.J_BUNDLE.OWNER] = str(locoObject.getOwner())
    locoDetailDict[PatternScriptEntities.J_BUNDLE.TRACK] = locoObject.getTrackName()
    locoDetailDict[PatternScriptEntities.J_BUNDLE.LOCATION] = locoObject.getLocation().getName()
    locoDetailDict[PatternScriptEntities.J_BUNDLE.DESTINATION] = locoObject.getDestinationName()
    locoDetailDict[PatternScriptEntities.J_BUNDLE.COMMENT] = locoObject.getComment()

# Not part of JMRI engine attributes
    locoDetailDict[PatternScriptEntities.J_BUNDLE.LOAD] = u'O'
    locoDetailDict[PatternScriptEntities.J_BUNDLE.FINAL_DEST_TRACK] = PatternScriptEntities.readConfigFile('PT')['DS']

    if locoObject in listOfAssignedRs: # Flag to mark if RS is on a built train
        locoDetailDict[PatternScriptEntities.BUNDLE['On Train']] = True
    else:
        locoDetailDict[PatternScriptEntities.BUNDLE['On Train']] = False

    locoDetailDict[PatternScriptEntities.BUNDLE['Set to']] = '[  ] '
    locoDetailDict[u'PUSO'] = u'SL'
    locoDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getDropEngineMessageFormat

    PatternScriptEntities.backupConfigFile()

    return locoDetailDict

def sortCarList(carList):
    """backupConfigFile() is a bit of user edit protection
    Sort order of PatternScriptEntities.readConfigFile('PT')['SC'] is top down"""

    sortCars = PatternScriptEntities.readConfigFile('PT')['SC']
    for sortKey in sortCars:
        translatedkey = PatternScriptEntities.SB.handleGetMessage(sortKey)
        carList.sort(key=lambda row: row[translatedkey])

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
    Dealers choice, either:
        PatternScriptEntities.J_BUNDLE.ROAD
        or
        PatternScriptEntities.SB.handleGetMessage('Road')
    """

    fdStandIn = PatternScriptEntities.readConfigFile('PT')

    listOfAssignedRs = getRsOnTrains()
    carDetailDict = {}

    carDetailDict[PatternScriptEntities.J_BUNDLE.ROAD] = carObject.getRoadName()
    carDetailDict[PatternScriptEntities.J_BUNDLE.NUMBER] = carObject.getNumber()
    carDetailDict[PatternScriptEntities.J_BUNDLE.TYPE] = carObject.getTypeName()
    carDetailDict[PatternScriptEntities.J_BUNDLE.LENGTH] = carObject.getLength()
    carDetailDict[PatternScriptEntities.J_BUNDLE.WEIGHT] = carObject.getWeightTons()
    if carObject.isCaboose() or carObject.isPassenger():
        carDetailDict[PatternScriptEntities.J_BUNDLE.LOAD] = u'O'
    else:
        carDetailDict[PatternScriptEntities.J_BUNDLE.LOAD] = carObject.getLoadName()
    carDetailDict[PatternScriptEntities.J_BUNDLE.LOAD_TYPE] = carObject.getLoadType()
    carDetailDict[PatternScriptEntities.J_BUNDLE.HAZARDOUS] = carObject.isHazardous()
    carDetailDict[PatternScriptEntities.J_BUNDLE.COLOR] = carObject.getColor()
    carDetailDict[PatternScriptEntities.J_BUNDLE.KERNEL] = carObject.getKernelName()



    carDetailDict[PatternScriptEntities.J_BUNDLE.KERNEL_SIZE] = '0'

    kernelTally = []
    for car in PatternScriptEntities.CM.getByIdList():
        kernelTally.append(car.getKernelName())
    #
    #
    #
    # if carObject.getKernelName():
    # i = 0
    #     if car.getKernelName() == carObject.getKernelName():
    #         i += 1
    # carDetailDict[PatternScriptEntities.J_BUNDLE.KERNEL_SIZE] = str(i)







    carDetailDict[PatternScriptEntities.J_BUNDLE.OWNER] = str(carObject.getOwner())
    carDetailDict[PatternScriptEntities.J_BUNDLE.TRACK] = carObject.getTrackName()
    carDetailDict[PatternScriptEntities.J_BUNDLE.LOCATION] = carObject.getLocationName()

    if not (carObject.getDestinationName()):
        carDetailDict[PatternScriptEntities.J_BUNDLE.DESTINATION] = fdStandIn['DS']
        carDetailDict[PatternScriptEntities.J_BUNDLE.DEST_TRACK] = fdStandIn['DT']
    else:
        carDetailDict[PatternScriptEntities.J_BUNDLE.DESTINATION] = carObject.getDestinationName()
        carDetailDict[PatternScriptEntities.J_BUNDLE.DEST_TRACK] = carObject.getDestinationName() \
                                     + ', ' + carObject.getDestinationTrackName()

    if not (carObject.getFinalDestinationName()):
        carDetailDict[PatternScriptEntities.J_BUNDLE.FINAL_DEST] = fdStandIn['FD']
        carDetailDict[PatternScriptEntities.J_BUNDLE.FINAL_DEST_TRACK] = fdStandIn['FT']
    else:
        carDetailDict[PatternScriptEntities.J_BUNDLE.FINAL_DEST] = carObject.getFinalDestinationName()
        carDetailDict[PatternScriptEntities.J_BUNDLE.FINAL_DEST_TRACK] = carObject.getFinalDestinationName() \
                                   + ', ' + carObject.getFinalDestinationTrackName()

    carDetailDict[PatternScriptEntities.J_BUNDLE.COMMENT] = carObject.getComment()

    trackId = PatternScriptEntities.LM.getLocationByName(carObject.getLocationName()).getTrackById(carObject.getTrackId())
    carDetailDict[PatternScriptEntities.J_BUNDLE.DROP_COMMENT] = trackId.getCommentSetout()
    carDetailDict[PatternScriptEntities.J_BUNDLE.PICKUP_COMMENT] = trackId.getCommentPickup()
    carDetailDict[PatternScriptEntities.J_BUNDLE.RWE] = carObject.getReturnWhenEmptyDestinationName()

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
            csvSwitchList +=  loco[PatternScriptEntities.BUNDLE['Set to']] + ',' \
                            + loco['PUSO'] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Road')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Number')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Type')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Model')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Length')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Weight')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Consist')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Owner')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Track')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Location')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Destination')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Comment')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('Load')] + ',' \
                            + loco[PatternScriptEntities.SB.handleGetMessage('FD&Track')] + ',' \
                            + '\n'
        for car in track['cars']:
            csvSwitchList +=  car[PatternScriptEntities.BUNDLE['Set to']] + ',' \
                            + car['PUSO'] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Road')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Number')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Type')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Length')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Weight')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Load')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Track')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('FD&Track')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Load_Type')] + ',' \
                            + str(car[PatternScriptEntities.SB.handleGetMessage('Hazardous')]) + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Color')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Kernel')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Kernel_Size')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Owner')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Location')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Destination')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Dest&Track')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Final_Dest')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('Comment')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('SetOut_Msg')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('PickUp_Msg')] + ',' \
                            + car[PatternScriptEntities.SB.handleGetMessage('RWE')] \
                            + '\n'

    return trackPattern['trainDescription'], csvSwitchList

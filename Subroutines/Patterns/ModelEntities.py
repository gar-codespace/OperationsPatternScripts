# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


def getTrackNamesByLocation(trackType):
    """
    Called by:
    Model.verifySelectedTracks
    ViewEntities.merge
    """

    patternLocation = PSE.readConfigFile('Patterns')['PL']
    allTracksAtLoc = []
    try: # Catch on the fly user edit of config file error
        for track in PSE.LM.getLocationByName(patternLocation).getTracksByNameList(trackType):
            allTracksAtLoc.append(unicode(track.getName(), PSE.ENCODING))
        return allTracksAtLoc
    except AttributeError:
        return allTracksAtLoc

def makeUserInputList(textBoxEntry):
    """
    Called by:
    ModelSetCarsForm.makeMergedForm
    """

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), PSE.ENCODING))

    return userInputList

def merge(switchList, userInputList):
    """
    Merge the values in textBoxEntry into the ['Set_To'] field of switchList.
    Called by:
    ModelSetCarsForm.makeMergedForm
    """

    longestTrackString = findLongestTrackString()
    allTracksAtLoc = getTrackNamesByLocation(None)

    i = 0
    locos = switchList['track']['locos']
    for loco in locos:
        userInput = unicode(userInputList[i], PSE.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PSE.formatText('[' + userInput + ']', longestTrackString + 2)
        else:
            setTrack = PSE.formatText('[' + PSE.getBundleItem('Hold') + ']', longestTrackString + 2)

        loco.update({'Set_To': setTrack})
        i += 1

    cars = switchList['track']['cars']
    for car in cars:
        userInput = unicode(userInputList[i], PSE.ENCODING)

        if userInput in allTracksAtLoc:
            setTrack = PSE.formatText('[' + userInput + ']', longestTrackString + 2)
        else:
            setTrack = PSE.formatText('[' + PSE.getBundleItem('Hold') + ']', longestTrackString + 2)

        car.update({'Set_To': setTrack})
        i += 1

    return switchList

def findLongestTrackString():
    """
    Called by:
    merge
    """

    longestTrackString = 6 # 6 is the length of [Hold]
    location = PSE.LM.getLocationByName(PSE.readConfigFile('Patterns')['PL'])
    for track in location.getTracksList():
        if len(track.getName()) > longestTrackString:
            longestTrackString = len(track.getName())

    return longestTrackString

def testSelectedDivision(selectedItem=None):
    """
    Catches user edit of divisions
    Called by:
    Model.jDivision
    """

    allDivisions = PSE.getAllDivisionNames()
    if selectedItem in allDivisions:
        return selectedItem
    else:
        return allDivisions[0]

def testSelectedLocation(selectedItem=None):
    """
    Catches user edit of locations
    Called by:
    Model.jLocation
    """

    allLocations = PSE.getAllLocationNames()
    if selectedItem in allLocations:
        return selectedItem
    else:
        return allLocations[0]

def getTrackDetails(locationName, trackName):
    """
    The loco and car lists are sorted at this level.
    Used to make the Track Pattern Report.json file
    Called by:
    makeTrackPattern
    """

    genericTrackDetails = {}
    genericTrackDetails['trackName'] = trackName
    genericTrackDetails['length'] =  PSE.LM.getLocationByName(locationName).getTrackByName(trackName, None).getLength()
    genericTrackDetails['locos'] = sortLocoList(getLocoListForTrack(trackName))
    genericTrackDetails['cars'] = sortCarList(getCarListForTrack(trackName))

    return genericTrackDetails

def sortLocoList(locoList):
    """
    Try/Except protects against bad edit of config file
    Sort order of PSE.readConfigFile('RM')['SL'] is top down
    Called by:
    getGenericTrackDetails
    """

    sortLocos = PSE.readConfigFile('Patterns')['RM']['SL']
    for sortKey in sortLocos:
        try:
            translatedkey = (sortKey)
            locoList.sort(key=lambda row: row[translatedkey])
        except:
            print('Exception at: Patterns.ModelEntities.sortLocoList')
            print('Loco list not sorted')

    return locoList

def getRsOnTrains():
    """
    Make a list of all rolling stock that are on built trains
    Called by:
    getDetailsForLoco
    getDetailsForCar
    """

    builtTrainList = []
    for train in PSE.TM.getTrainsByStatusList():
        if train.isBuilt():
            builtTrainList.append(train)

    listOfAssignedRs = []
    for train in builtTrainList:
        listOfAssignedRs += PSE.CM.getByTrainList(train)
        listOfAssignedRs += PSE.EM.getByTrainList(train)

    return listOfAssignedRs

def getLocoListForTrack(track):
    """
    Creates a generic locomotive list for a track
    Called by:
    getGenericTrackDetails
    """

    location = PSE.readConfigFile('Patterns')['PL']
    locoList = getLocoObjects(location, track)

    return [getDetailsForLoco(loco) for loco in locoList]

def getLocoObjects(location, track):
    """
    Called by:
    getLocoListForTrack
    """

    locoList = []
    allLocos = PSE.EM.getByModelList()

    return [loco for loco in allLocos if loco.getLocationName() == location and loco.getTrackName() == track]

def getDetailsForLoco(locoObject):
    """
    Mimics jmri.jmrit.operations.setup.Setup.getEngineAttributes()
    Called by:
    getLocoListForTrack
    """

    locoDetailDict = {}

    locoDetailDict['road'] = locoObject.getRoadName()
    locoDetailDict['number'] = locoObject.getNumber()
    locoDetailDict['carType'] = locoObject.getTypeName()
    locoDetailDict['model'] = locoObject.getModel()
    locoDetailDict['length'] = locoObject.getLength()
    locoDetailDict['weight'] = locoObject.getWeightTons()
    locoDetailDict['color'] = locoObject.getColor()
    # Depending on which version of JMRI Ops Pro
    try:
        locoDetailDict['owner'] = locoObject.getOwner()
    except:
        # print('Exception at: Patterns.ModelEntities.getDetailsForLoco')
        locoDetailDict['owner'] = locoObject.getOwnerName()
    locoDetailDict['comment'] = locoObject.getComment()
    locoDetailDict['division'] = locoObject.getDivisionName()
    locoDetailDict['location'] = locoObject.getLocationName()
    locoDetailDict['track'] = locoObject.getTrackName()
    locoDetailDict['destination'] = locoObject.getDestinationName()
    locoDetailDict['dccAddress'] = locoObject.getDccAddress()
# Modifications used by this plugin
    try:
        locoDetailDict['consist'] = locoObject.getConsist().getName()
    except:
        # print('Exception at: Patterns.ModelEntities.getDetailsForLoco')
        locoDetailDict['consist'] = PSE.getBundleItem('Single')
    locoDetailDict['setTo'] = u'[  ] '
    locoDetailDict[u'puso'] = u' '
    locoDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getDropEngineMessageFormat
    locoDetailDict['onTrain'] = False
    if locoObject in getRsOnTrains(): # Flag to mark if RS is on a built train
        locoDetailDict['onTrain'] = True

    return locoDetailDict

def sortCarList(carList):
    """
    Try/Except protects against bad edit of config file
    Sort order of PSE.readConfigFile('Patterns')['RM']['SC'] is top down
    Called by:
    getGenericTrackDetails
    """

    sortCars = PSE.readConfigFile('Patterns')['RM']['SC']
    for sortKey in sortCars:
        try:
            translatedkey = (sortKey)
            carList.sort(key=lambda row: row[translatedkey])
        except:
            print('Exception at: Patterns.ModelEntities.sortCarList')
            print('Car list not sorted')

    return carList

def getCarListForTrack(track):
    """
    A list of car attributes as a dictionary
    Called by:
    getGenericTrackDetails
    """

    location = PSE.readConfigFile('Patterns')['PL']
    carList = getCarObjects(location, track)
    kernelTally = getKernelTally()

    carDetails = [getDetailsForCar(car, kernelTally) for car in carList]

    return carDetails

def getCarObjects(location, track):
    """
    Called by:
    getCarListForTrack
    """

    allCars = PSE.CM.getByIdList()

    return [car for car in allCars if car.getLocationName() == location and car.getTrackName() == track]

def getKernelTally():
    """
    Called by:
    getCarListForTrack
    """

    tally = []
    for car in PSE.CM.getByIdList():
        kernelName = car.getKernelName()
        if kernelName:
            tally.append(kernelName)

    kernelTally = PSE.occuranceTally(tally)

    return kernelTally

def getDetailsForCar(carObject, kernelTally):
    """
    Mimics jmri.jmrit.operations.setup.Setup.getCarAttributes()
    Called by:
    getCarListForTrack
    """

    carDetailDict = {}
    trackId = PSE.LM.getLocationByName(carObject.getLocationName()).getTrackById(carObject.getTrackId())
    try:
        kernelSize = kernelTally[carObject.getKernelName()]
    except:
        kernelSize = 0

    carDetailDict['road'] = carObject.getRoadName()
    carDetailDict['number'] = carObject.getNumber()
    carDetailDict['carType'] = carObject.getTypeName()
    carDetailDict['length'] = carObject.getLength()
    carDetailDict['weight'] = carObject.getWeightTons()
    carDetailDict['loadType'] = carObject.getLoadType()
    carDetailDict['load'] = carObject.getLoadName()
    carDetailDict['hazardous'] = carObject.isHazardous()
    carDetailDict['color'] = carObject.getColor()
    carDetailDict['kernel'] = carObject.getKernelName()
    carDetailDict['kernelSize'] = str(kernelSize)
    # Depending on which version of JMRI Ops Pro
    try:
        carDetailDict['owner'] = carObject.getOwner()
    except:
        carDetailDict['owner'] = carObject.getOwnerName()
    carDetailDict['division'] = carObject.getDivisionName()
    carDetailDict['location'] = carObject.getLocationName()
    carDetailDict['track'] = carObject.getTrackName()
    carDetailDict['comment'] = carObject.getComment()
    carDetailDict['destination'] = carObject.getDestinationName()
    carDetailDict['dest&Track'] = carObject.getDestinationTrackName()
    carDetailDict['finalDest'] = carObject.getFinalDestinationName()
    carDetailDict['fd&Track'] = carObject.getFinalDestinationTrackName()
    carDetailDict['setOutMsg'] = trackId.getCommentSetout()
    carDetailDict['pickupMsg'] = trackId.getCommentPickup()
    carDetailDict['rwe'] = carObject.getReturnWhenEmptyDestinationName()
    carDetailDict['rwl'] = carObject.getReturnWhenLoadedDestinationName()
# Modifications used by this plugin
    carDetailDict['setTo'] = u'[  ] '
    carDetailDict[u'puso'] = u' '
    carDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat
    carDetailDict['onTrain'] = False
    if carObject in getRsOnTrains(): # Flag to mark if RS is on a built train
        carDetailDict['onTrain'] = True

    return carDetailDict

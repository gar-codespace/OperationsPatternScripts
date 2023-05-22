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
    locos = switchList['locations'][0]['tracks'][0]['locos']
    for loco in locos:
        setTrack = switchList['locations'][0]['tracks'][0]['trackName']
        setTrack = PSE.formatText('[' + setTrack + ']', longestTrackString + 2)
        loco.update({'Set_To': setTrack})

        userInput = unicode(userInputList[i], PSE.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PSE.formatText('[' + userInput + ']', longestTrackString + 2)
            loco.update({'Set_To': setTrack})
        i += 1

    cars = switchList['locations'][0]['tracks'][0]['cars']
    for car in cars:
        setTrack = switchList['locations'][0]['tracks'][0]['trackName']
        setTrack = PSE.formatText('[' + setTrack + ']', longestTrackString + 2)
        car.update({'Set_To': setTrack})

        userInput = unicode(userInputList[i], PSE.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PSE.formatText('[' + userInput + ']', longestTrackString + 2)
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

def getGenericTrackDetails(locationName, trackName):
    """
    The loco and car lists are sorted at this level, used to make the Track Pattern Report.json file
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

    locoDetailDict['Road'] = locoObject.getRoadName()
    locoDetailDict['Number'] = locoObject.getNumber()
    locoDetailDict['Type'] = locoObject.getTypeName()
    locoDetailDict['Model'] = locoObject.getModel()
    locoDetailDict['Length'] = locoObject.getLength()
    locoDetailDict['Weight'] = locoObject.getWeightTons()
    locoDetailDict['Color'] = locoObject.getColor()
    # Depending on which version of JMRI Ops Pro
    try:
        locoDetailDict['Owner'] = locoObject.getOwner()
    except:
        locoDetailDict['Owner'] = locoObject.getOwnerName()
    locoDetailDict['Comment'] = locoObject.getComment()
    locoDetailDict['Location'] = locoObject.getLocationName()
    locoDetailDict['Track'] = locoObject.getTrackName()
    locoDetailDict['Destination'] = locoObject.getDestinationName()
# Modifications used by this plugin
    try:
        locoDetailDict['Consist'] = locoObject.getConsist().getName()
    except:
        locoDetailDict['Consist'] = PSE.BUNDLE['Single']
    locoDetailDict['Set_To'] = u'[  ] '
    locoDetailDict[u'PUSO'] = u' '
    locoDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getDropEngineMessageFormat
    locoDetailDict['On_Train'] = False
    if locoObject in getRsOnTrains(): # Flag to mark if RS is on a built train
        locoDetailDict['On_Train'] = True

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

    carDetailDict['Road'] = carObject.getRoadName()
    carDetailDict['Number'] = carObject.getNumber()
    carDetailDict['Type'] = carObject.getTypeName()
    carDetailDict['Length'] = carObject.getLength()
    carDetailDict['Weight'] = carObject.getWeightTons()
    carDetailDict['Load Type'] = carObject.getLoadType()
    carDetailDict['Load'] = carObject.getLoadName()
    carDetailDict['Hazardous'] = carObject.isHazardous()
    carDetailDict['Color'] = carObject.getColor()
    carDetailDict['Kernel'] = carObject.getKernelName()
    carDetailDict['Kernel Size'] = str(kernelSize)
    # Depending on which version of JMRI Ops Pro
    try:
        carDetailDict['Owner'] = carObject.getOwner()
    except:
        carDetailDict['Owner'] = carObject.getOwnerName()
    carDetailDict['Track'] = carObject.getTrackName()
    carDetailDict['Location'] = carObject.getLocationName()
    carDetailDict['Comment'] = carObject.getComment()
    carDetailDict['Destination'] = carObject.getDestinationName()
    carDetailDict['Dest&Track'] = carObject.getDestinationTrackName()
    carDetailDict['Final Dest'] = carObject.getFinalDestinationName()
    carDetailDict['FD&Track'] = carObject.getFinalDestinationTrackName()
    carDetailDict['SetOut Msg'] = trackId.getCommentSetout()
    carDetailDict['PickUp Msg'] = trackId.getCommentPickup()
    carDetailDict['RWE'] = carObject.getReturnWhenEmptyDestinationName()
    carDetailDict['RWL'] = carObject.getReturnWhenLoadedDestinationName()
# Modifications used by this plugin
    carDetailDict['Set_To'] = u'[  ] '
    carDetailDict[u'PUSO'] = u' '
    carDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat
    carDetailDict['On_Train'] = False
    if carObject in getRsOnTrains(): # Flag to mark if RS is on a built train
        carDetailDict['On_Train'] = True

    return carDetailDict

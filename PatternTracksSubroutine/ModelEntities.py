# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ModelEntities'
SCRIPT_REV = 20221010


def makeUserInputList(textBoxEntry):
    """Used by:
        ModelSetCarsForm.makeMergedForm
        """

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), PSE.ENCODING))

    return userInputList

def merge(switchList, userInputList):
    """Merge the values in textBoxEntry into the ['Set_To'] field of switchList.
        Used by:
        ModelSetCarsForm.makeMergedForm
        """

    longestTrackString = findLongestTrackString()
    allTracksAtLoc = PSE.getTracksNamesByLocation(None)

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
    """Used by:
        merge
        """

    longestTrackString = 6 # 6 is the length of [Hold]
    for track in PSE.readConfigFile('PT')['PT']: # Pattern Tracks
        if len(track) > longestTrackString:
            longestTrackString = len(track)

    return longestTrackString

def modifyTrackPatternReport(trackPattern):
    """Make adjustments to the way the reports display here.
        The undeflying json is not changed.
        Replaces blank Dest and FD with standins.
        Replaces load type with short load type.
        Used by:
        View.trackPatternButton
        View.setRsButton
        ModelSetCarsForm.makeMergedForm
        """

    standins = PSE.readConfigFile('RM')

    tracks = trackPattern['locations'][0]['tracks']
    for track in tracks:
        for loco in track['locos']:
            destStandin, fdStandin = getStandins(loco, standins)
            loco.update({'Destination': destStandin})

        for car in track['cars']:
            destStandin, fdStandin = getStandins(car, standins)
            car.update({'Destination': destStandin})
            car.update({'Final Dest': fdStandin})
            shortLoadType = PSE.getShortLoadType(car)
            car.update({'Load Type': shortLoadType})

    return trackPattern

def getStandins(car, standins):
    """Replaces null destination and fd with the standin from the config file
        Used by:
        modifyTrackPatternReport
        """

    destStandin = car['Destination']
    if not car['Destination']:
        destStandin = standins['DS']

    try: # No FD for locos
        fdStandin = car['Final Dest']
        if not car['Final Dest']:
            fdStandin = standins['FD']
    except:
        fdStandin = ''

    return destStandin, fdStandin

def makeTrackPattern(trackList=None):
    """Used by:
        Model.trackPatternButton
        View.setRsButton
        """

    if not trackList:
        trackList = PSE.getSelectedTracks()

    detailsForTrack = []
    patternLocation = PSE.readConfigFile('PT')['PL']
    for trackName in trackList:
        detailsForTrack.append(getGenericTrackDetails(patternLocation, trackName))

    trackPattern = {}
    trackPattern['locationName'] = patternLocation
    trackPattern['tracks'] = detailsForTrack

    return trackPattern

def makeTrackPatternReport(trackPattern):
    """Used by:
        Model.trackPatternButton
        View.setRsButton
        """

    trackPatternReport = makeGenericHeader()
# put in as a list to maintain compatability with JSON File Format/JMRI manifest export.
    trackPatternReport['locations'] = [trackPattern]

    return trackPatternReport

def testSelectedItem(selectedItem=None):
    """Catches user edit of locations
        Used by:
        Model.updatePatternLocation
        """

    allLocations = PSE.getAllLocationNames() #List of strings
    if selectedItem in allLocations:
        return selectedItem
    else:
        return allLocations[0]

def getAllTracksForLocation(location):
    """Sets all tracks to false
        Used by:
        Model.updatePatternLocation
        """

    jmriTrackList = PSE.LM.getLocationByName(location).getTracksByNameList(None)
    trackDict = {}
    for track in jmriTrackList:
        trackDict[unicode(track.getName(), PSE.ENCODING)] = False

    return trackDict

def updateTrackCheckBoxes(trackCheckBoxes):
    """Returns a dictionary of track names and their check box status
        Used by:
        Model.updateConfigFile
        """

    dict = {}
    for item in trackCheckBoxes:
        dict[unicode(item.text, PSE.ENCODING)] = item.selected

    return dict

def getGenericTrackDetails(locationName, trackName):
    """The loco and car lists are sorted at this level, used to make the Track Pattern Report.json file
        Used by:
        makeTrackPattern
        """

    genericTrackDetails = {}
    genericTrackDetails['trackName'] = trackName
    genericTrackDetails['length'] =  PSE.LM.getLocationByName(locationName).getTrackByName(trackName, None).getLength()
    genericTrackDetails['locos'] = sortLocoList(getLocoListForTrack(trackName))
    genericTrackDetails['cars'] = sortCarList(getCarListForTrack(trackName))

    return genericTrackDetails

def sortLocoList(locoList):
    """Try/Except protects against bad edit of config file
        Sort order of PSE.readConfigFile('RM')['SL'] is top down
        Used by:
        getGenericTrackDetails
        """

    sortLocos = PSE.readConfigFile('RM')['SL']
    for sortKey in sortLocos:
        try:
            translatedkey = (sortKey)
            locoList.sort(key=lambda row: row[translatedkey])
        except:
            print('Loco lst not sorted')

    return locoList

def getRsOnTrains():
    """Make a list of all rolling stock that are on built trains
        Used by:
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
    """Creates a generic locomotive list for a track
        Used by:
        getGenericTrackDetails
        """

    location = PSE.readConfigFile('PT')['PL']
    locoList = getLocoObjects(location, track)

    return [getDetailsForLoco(loco) for loco in locoList]

def getLocoObjects(location, track):
    """Used by:
        getLocoListForTrack
        """

    locoList = []
    allLocos = PSE.EM.getByModelList()

    return [loco for loco in allLocos if loco.getLocationName() == location and loco.getTrackName() == track]

def getDetailsForLoco(locoObject):
    """Mimics jmri.jmrit.operations.setup.Setup.getEngineAttributes()
        Used by:
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
    locoDetailDict['Owner'] = str(locoObject.getOwner())
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
    """Try/Except protects against bad edit of config file
        Sort order of PSE.readConfigFile('RM')['SC'] is top down
        Used by:
        getGenericTrackDetails
        """

    sortCars = PSE.readConfigFile('RM')['SC']
    for sortKey in sortCars:
        try:
            translatedkey = (sortKey)
            carList.sort(key=lambda row: row[translatedkey])
        except:
            print('Car list not sorted')

    return carList

def getCarListForTrack(track):
    """A list of car attributes as a dictionary
        Used by:
        getGenericTrackDetails
        """

    location = PSE.readConfigFile('PT')['PL']
    carList = getCarObjects(location, track)
    kernelTally = getKernelTally()

    carDetails = [getDetailsForCar(car, kernelTally) for car in carList]

    return carDetails

def getCarObjects(location, track):
    """Used by:
        getCarListForTrack
        """

    allCars = PSE.CM.getByIdList()

    return [car for car in allCars if car.getLocationName() == location and car.getTrackName() == track]

def getKernelTally():
    """Used by:
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
    """Mimics jmri.jmrit.operations.setup.Setup.getCarAttributes()
        Used by:
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
    carDetailDict['Owner'] = str(carObject.getOwner())
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

def makeGenericHeader():
    """Used by:
        makeTrackPatternReport
        Controller.StartUp.setRsButton
        """

    OSU = PSE.JMRI.jmrit.operations.setup
    configFile = PSE.readConfigFile()

    listHeader = {}
    if configFile['CP']['jPlusSubroutine']: # Replace with Railroad Details Subroutine
        listHeader['railroadName'] = makeDetailedHeader(configFile['JP'])
    else:
        listHeader['railroadName'] = unicode(OSU.Setup.getRailroadName(), PSE.ENCODING)

    listHeader['date'] = unicode(PSE.timeStamp(), PSE.ENCODING)
    listHeader['locations'] = [{'locationName': configFile['PT']['PL'], 'tracks': [{'cars': [], 'locos': []}]}]

    return listHeader

def makeDetailedHeader(railroadDetails):
    """Used by:
        makeGenericHeader
        """

    detailedHeader = ''
    if railroadDetails['OR']:
        detailedHeader += railroadDetails['OR']

    if railroadDetails['TR']:
        detailedHeader += '\n' + railroadDetails['TR']

    if railroadDetails['LO']:
        detailedHeader += '\n' + railroadDetails['LO']

    return detailedHeader

def makeInitialTrackList(location):
    """Used by:
        updateLocations
        """

    trackDict = {}
    for track in PSE.LM.getLocationByName(location).getTracksByNameList(None):
        trackDict[unicode(track, PSE.ENCODING)] = False

    return trackDict

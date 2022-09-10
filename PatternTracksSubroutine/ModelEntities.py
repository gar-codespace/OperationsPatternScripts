# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ModelEntities'
SCRIPT_REV = 20220101

def makeTrackPattern(trackList=None):
    """Used by:
        Model.trackPatternButton
        View.setRsButton
        """

    if not trackList:
        trackList = PatternScriptEntities.getSelectedTracks()

    detailsForTrack = []
    patternLocation = PatternScriptEntities.readConfigFile('PT')['PL']
    for trackName in trackList:
        detailsForTrack.append(getGenericTrackDetails(patternLocation, trackName))

    locationDict = {}
    locationDict['locationName'] = patternLocation
    locationDict['tracks'] = detailsForTrack

    return locationDict

def makeTrackPatternReport(trackPattern):
    """Used by:
        Model.trackPatternButton
        View.setRsButton
        """

    trackPatternReport = makeGenericHeader()
# put in as a list to maintain compatability with JSON File Format/JMRI manifest export.
    trackPatternReport['locations'] = [trackPattern]

    return trackPatternReport

def testSelectedItem(selectedItem):
    """Catches user edit of locations
        Used by:
        Model.updatePatternLocation
        """

    allLocations = PatternScriptEntities.getAllLocations() #List of strings
    if selectedItem in allLocations:
        return selectedItem
    else:
        return allLocations[0]

def getAllTracksForLocation(location):
    """Sets all tracks to false
        Used by:
        Model.updatePatternLocation
        """

    jmriTrackList = PatternScriptEntities.LM.getLocationByName(location).getTracksByNameList(None)
    trackDict = {}
    for track in jmriTrackList:
        trackDict[unicode(track.getName(), PatternScriptEntities.ENCODING)] = False

    return trackDict

def getTracksByLocation(trackType):
    """Used by:
        Model.verifySelectedTracks
        Model.makeTrackList
        """

    patternLocation = PatternScriptEntities.readConfigFile('PT')['PL']
    allTracksList = []
    try: # Catch on the fly user edit of config file error
        for track in PatternScriptEntities.LM.getLocationByName(patternLocation).getTracksByNameList(trackType):
            allTracksList.append(unicode(track.getName(), PatternScriptEntities.ENCODING))
        return allTracksList
    except AttributeError:
        return allTracksList

def updateTrackCheckBoxes(trackCheckBoxes):
    """Returns a dictionary of track names and their check box status
        Used by:
        Model.updateConfigFile
        """

    dict = {}
    for item in trackCheckBoxes:
        dict[unicode(item.text, PatternScriptEntities.ENCODING)] = item.selected

    return dict

def getGenericTrackDetails(locationName, trackName):
    """The loco and car lists are sorted at this level, used to make the Track Pattern Report.json file
        Used by:
        makeTrackPattern
        """

    genericTrackDetails = {}
    genericTrackDetails['trackName'] = trackName
    genericTrackDetails['length'] =  PatternScriptEntities.LM.getLocationByName(locationName).getTrackByName(trackName, None).getLength()
    genericTrackDetails['locos'] = sortLocoList(getLocoListForTrack(trackName))
    genericTrackDetails['cars'] = sortCarList(getCarListForTrack(trackName))

    return genericTrackDetails

def sortLocoList(locoList):
    """Try/Except protects against bad edit of config file
        Sort order of PatternScriptEntities.readConfigFile('RM')['SL'] is top down
        Used by:
        getGenericTrackDetails
        """

    sortLocos = PatternScriptEntities.readConfigFile('RM')['SL']
    for sortKey in sortLocos:
        try:
            translatedkey = (sortKey)
            locoList.sort(key=lambda row: row[translatedkey])
        except:
            pass

    return locoList

def getRsOnTrains():
    """Make a list of all rolling stock that are on built trains
        Used by:
        getDetailsForLoco
        getDetailsForCar
        """

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
    """Creates a generic locomotive list for a track
        Used by:
        getGenericTrackDetails
        """

    location = PatternScriptEntities.readConfigFile('PT')['PL']
    locoList = getLocoObjects(location, track)

    return [getDetailsForLoco(loco) for loco in locoList]

def getLocoObjects(location, track):
    """Used by:
        getLocoListForTrack
        """

    locoList = []
    allLocos = PatternScriptEntities.EM.getByModelList()

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
        locoDetailDict['Consist'] = PatternScriptEntities.BUNDLE['Single']
    locoDetailDict['Set_To'] = u'[  ] '
    locoDetailDict[u'PUSO'] = u' '
    locoDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getDropEngineMessageFormat
    locoDetailDict['On_Train'] = False
    if locoObject in getRsOnTrains(): # Flag to mark if RS is on a built train
        locoDetailDict['On_Train'] = True

    return locoDetailDict

def sortCarList(carList):
    """Try/Except protects against bad edit of config file
        Sort order of PatternScriptEntities.readConfigFile('RM')['SC'] is top down
        Used by:
        getGenericTrackDetails
        """

    sortCars = PatternScriptEntities.readConfigFile('RM')['SC']
    for sortKey in sortCars:
        try:
            translatedkey = (sortKey)
            carList.sort(key=lambda row: row[translatedkey])
        except:
            pass

    return carList

def getCarListForTrack(track):
    """A list of car attributes as a dictionary
        Used by:
        getGenericTrackDetails
        """

    location = PatternScriptEntities.readConfigFile('PT')['PL']
    carList = getCarObjects(location, track)
    kernelTally = getKernelTally()

    carDetails = [getDetailsForCar(car, kernelTally) for car in carList]

    return carDetails

def getCarObjects(location, track):
    """Used by:
        getCarListForTrack
        """

    allCars = PatternScriptEntities.CM.getByIdList()

    return [car for car in allCars if car.getLocationName() == location and car.getTrackName() == track]

def getKernelTally():
    """Used by:
        getCarListForTrack
        """

    tally = []
    for car in PatternScriptEntities.CM.getByIdList():
        kernelName = car.getKernelName()
        if kernelName:
            tally.append(kernelName)

    kernelTally = PatternScriptEntities.occuranceTally(tally)

    return kernelTally

def getDetailsForCar(carObject, kernelTally):
    """Mimics jmri.jmrit.operations.setup.Setup.getCarAttributes()
        Used by:
        getCarListForTrack
        """

    carDetailDict = {}
    trackId = PatternScriptEntities.LM.getLocationByName(carObject.getLocationName()).getTrackById(carObject.getTrackId())
    try:
        kernelSize = kernelTally[carObject.getKernelName()]
    except:
        kernelSize = 0
    shortLoadType = getShortLoadType(carObject)

    carDetailDict['Road'] = carObject.getRoadName()
    carDetailDict['Number'] = carObject.getNumber()
    carDetailDict['Type'] = carObject.getTypeName()
    carDetailDict['Length'] = carObject.getLength()
    carDetailDict['Weight'] = carObject.getWeightTons()
    carDetailDict['Load Type'] = shortLoadType
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

def getShortLoadType(car):
    """Used by:
        getDetailsForCar
        """

    lt = 'U'
    if car.getLoadType() == 'empty':
        lt = 'E'
    if car.getLoadType() == 'load':
        lt = 'L'
    if car.isCaboose() or car.isPassenger():
        lt = 'O'

    return lt

def makeGenericHeader():
    """Used by:
        Model.makeTrackPatternReport
        Controller.StartUp.setRsButton
        """

    OSU = PatternScriptEntities.JMRI.jmrit.operations.setup
    patternLocation = PatternScriptEntities.readConfigFile('PT')['PL']
    location = PatternScriptEntities.LM.getLocationByName(patternLocation)

    listHeader = {}
    listHeader['railroad'] = unicode(OSU.Setup.getRailroadName(), PatternScriptEntities.ENCODING)
    listHeader['trainName'] = unicode(OSU.Setup.getComment(), PatternScriptEntities.ENCODING)
    listHeader['trainDescription'] = PatternScriptEntities.BUNDLE['Pattern Report for Tracks']
    listHeader['trainComment'] = location.getComment()
    listHeader['date'] = unicode(PatternScriptEntities.timeStamp(), PatternScriptEntities.ENCODING)
    listHeader['locations'] = [{'tracks': [{'cars': [], 'locos': []}]}]

    return listHeader

def writeWorkEventListAsJson(workEvent, workEventName):
    """Any generic switch list is written as a json file.
        Used By:
        Model.trackPatternButton
        ModelSetCarsForm.mergeForms
        """

    workEventPath = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + workEventName + '.json'
    workEventReport = PatternScriptEntities.dumpJson(workEvent)

    PatternScriptEntities.genericWriteReport(workEventPath, workEventReport)

    return

def makeInitialTrackList(location):
    """Used by:
        updateLocations
        """

    trackDict = {}
    for track in PatternScriptEntities.LM.getLocationByName(location).getTracksByNameList(None):
        trackDict[unicode(track, PatternScriptEntities.ENCODING)] = False

    return trackDict

def makeTrackPatternCsv(trackPattern):
    """CSV writer does not support utf-8
        Used by:
        Model.writeTrackPatternCsv
        """

    trackPatternCsv = u'Operator,Description,Parameters\n' \
                    u'RT,Report Type,' + trackPattern['trainDescription'] + '\n' \
                    u'RN,Railroad Name,' + trackPattern['railroad'] + '\n' \
                    u'LN,Location Name,' + trackPattern['locations'][0]['locationName'] + '\n' \
                    u'PRNTR,Printer Name,\n' \
                    u'YPC,Yard Pattern Comment,' + trackPattern['trainComment'] + '\n' \
                    u'VT,Valid,' + trackPattern['date'] + '\n'
    for track in trackPattern['locations'][0]['tracks']: # There is only one location
        trackPatternCsv += u'TN,Track name,' + unicode(track['trackName'], PatternScriptEntities.ENCODING) + '\n'
        trackPatternCsv += u'Set_To,PUSO,Road,Number,Type,Model,Length,Weight,Consist,Owner,Track,Location,Destination,Comment\n'
        for loco in track['locos']:
            trackPatternCsv +=  loco['Set_To'] + ',' \
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
                            + '\n'
        trackPatternCsv += u'Set_To,PUSO,Road,Number,Type,Length,Weight,Load,Load_Type,Hazardous,Color,Kernel,Kernel_Size,Owner,Track,Location,Destination,Dest&Track,Final_Dest,FD&Track,Comment,Drop_Comment,Pickup_Comment,RWE\n'
        for car in track['cars']:
            trackPatternCsv +=  car['Set_To'] + ',' \
                            + car['PUSO'] + ',' \
                            + car['Road'] + ',' \
                            + car['Number'] + ',' \
                            + car['Type'] + ',' \
                            + car['Length'] + ',' \
                            + car['Weight'] + ',' \
                            + car['Load'] + ',' \
                            + car['Load Type'] + ',' \
                            + str(car['Hazardous']) + ',' \
                            + car['Color'] + ',' \
                            + car['Kernel'] + ',' \
                            + car['Kernel Size'] + ',' \
                            + car['Owner'] + ',' \
                            + car['Track'] + ',' \
                            + car['Location'] + ',' \
                            + car['Destination'] + ',' \
                            + car['Dest&Track'] + ',' \
                            + car['Final Dest'] + ',' \
                            + car['FD&Track'] + ',' \
                            + car['Comment'] + ',' \
                            + car['SetOut Msg'] + ',' \
                            + car['PickUp Msg'] + ',' \
                            + car['RWE'] \
                            + '\n'

    return trackPatternCsv

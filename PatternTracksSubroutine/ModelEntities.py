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
    """Try/Except protects against bad edit of config file
    Sort order of PatternScriptEntities.readConfigFile('RM')['SL'] is top down
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
    """Creates a generic locomotive list for a track, used to make the **** WHICH JSON??****  JSON file"""

    location = PatternScriptEntities.readConfigFile('PT')['PL']
    locoList = getLocoObjects(location, track)

    return [getDetailsForLoco(loco) for loco in locoList]

def getLocoObjects(location, track):

    locoList = []
    allLocos = PatternScriptEntities.EM.getByModelList()

    return [loco for loco in allLocos if loco.getLocationName() == location and loco.getTrackName() == track]

def getDetailsForLoco(locoObject):
    """Mimics jmri.jmrit.operations.setup.Setup.getEngineAttributes()"""

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
    Sort order of PatternScriptEntities.readConfigFile('RM')['SC'] is top down"""

    sortCars = PatternScriptEntities.readConfigFile('RM')['SC']
    for sortKey in sortCars:
        try:
            translatedkey = (sortKey)
            carList.sort(key=lambda row: row[translatedkey])
        except:
            pass

    return carList

def getCarListForTrack(track):
    """A list of car attributes as a dictionary"""

    location = PatternScriptEntities.readConfigFile('PT')['PL']
    carList = getCarObjects(location, track)
    kernelTally = getKernelTally()

    carDetails = [getDetailsForCar(car, kernelTally) for car in carList]

    return carDetails

def getCarObjects(location, track):

    allCars = PatternScriptEntities.CM.getByIdList()

    return [car for car in allCars if car.getLocationName() == location and car.getTrackName() == track]

def getKernelTally(kernelName=None):

    if not kernelName:
        return '0'

    tally = []
    for car in PatternScriptEntities.CM.getByIdList():
        kernelName = car.getKernelName()
        if kernelName:
            tally.append(kernelName)

    kernelTally = PatternScriptEntities.occuranceTally(tally)

    return str(kernelTally)

def getDetailsForCar(carObject, kernelTally):
    """Mimics jmri.jmrit.operations.setup.Setup.getCarAttributes()"""

    carDetailDict = {}
    trackId = PatternScriptEntities.LM.getLocationByName(carObject.getLocationName()).getTrackById(carObject.getTrackId())

    carDetailDict['Road'] = carObject.getRoadName()
    carDetailDict['Number'] = carObject.getNumber()
    carDetailDict['Type'] = carObject.getTypeName()
    carDetailDict['Length'] = carObject.getLength()
    carDetailDict['Weight'] = carObject.getWeightTons()
    carDetailDict['Load_Type'] = carObject.getLoadType()
    carDetailDict['Load'] = carObject.getLoadName()
    carDetailDict['Hazardous'] = carObject.isHazardous()
    carDetailDict['Color'] = carObject.getColor()
    carDetailDict['Kernel'] = carObject.getKernelName()
    carDetailDict['Kernel_Size'] = getKernelTally(carObject.getKernelName())
    carDetailDict['Owner'] = str(carObject.getOwner())
    carDetailDict['Track'] = carObject.getTrackName()
    carDetailDict['Location'] = carObject.getLocationName()
    carDetailDict['Comment'] = carObject.getComment()
    carDetailDict['Destination'] = carObject.getDestinationName()
    carDetailDict['Dest&Track'] = carObject.getDestinationTrackName()
    carDetailDict['Final_Dest'] = carObject.getFinalDestinationName()
    carDetailDict['FD&Track'] = carObject.getFinalDestinationTrackName()
    carDetailDict['Drop_Comment'] = trackId.getCommentSetout()
    carDetailDict['Pickup_Comment'] = trackId.getCommentPickup()
    carDetailDict['RWE'] = carObject.getReturnWhenEmptyDestinationName()
    carDetailDict['RWL'] = carObject.getReturnWhenLoadedDestinationName()
# Modifications used by this plugin
    if carObject.isCaboose() or carObject.isPassenger():
        carDetailDict['Load_Type'] = u'O' # Occupied

    carDetailDict['On_Train'] = False
    if carObject in getRsOnTrains(): # Flag to mark if RS is on a built train
        carDetailDict['On_Train'] = True

    carDetailDict['Set_To'] = u'[  ] '
    carDetailDict[u'PUSO'] = u' '
    carDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat

    return carDetailDict

def makeGenericHeader():
    """Called by: Model.makeReport"""

    listHeader = {}
    listHeader['railroad'] = unicode(PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getRailroadName(), PatternScriptEntities.ENCODING)
    listHeader['trainName'] = u'Train Name Placeholder'
    listHeader['trainDescription'] = u'Train Description Placeholder'
    listHeader['trainComment'] = u'Train Comment Placeholder'
    listHeader['date'] = unicode(PatternScriptEntities.timeStamp(), PatternScriptEntities.ENCODING)
    listHeader['locations'] = []

    return listHeader

def writeWorkEventListAsJson(switchList):
    """The generic switch list is written as a ???????????? json
        redo this, thats a wierd way to pick a name
        """

    switchListName = switchList['trainDescription']
    switchListPath = PatternScriptEntities.PROFILE_PATH \
               + 'operations\\jsonManifests\\' + switchListName + '.json'
    switchListReport = PatternScriptEntities.dumpJson(switchList)

    PatternScriptEntities.genericWriteReport(switchListPath, switchListReport)
    return switchListName



def makeInitialTrackList(location):

    trackDict = {}
    for track in PatternScriptEntities.LM.getLocationByName(location).getTracksByNameList(None):
        trackDict[unicode(track, PatternScriptEntities.ENCODING)] = False

    return trackDict

def makeWorkEventsCsv(workEvents):
    """CSV writer does not support utf-8"""

    workEventsCsv = u'Operator,Description,Parameters\n' \
                    u'RT,Report Type,' + workEvents['trainDescription'] + '\n' \
                    u'RN,Railroad Name,' + workEvents['railroad'] + '\n' \
                    u'LN,Location Name,' + workEvents['locations'][0]['locationName'] + '\n' \
                    u'PRNTR,Printer Name,\n' \
                    u'YPC,Yard Pattern Comment,' + workEvents['trainComment'] + '\n' \
                    u'VT,Valid,' + workEvents['date'] + '\n'
    for track in workEvents['locations'][0]['tracks']: # There is only one location
        workEventsCsv += u'TN,Track name,' + unicode(track['trackName'], PatternScriptEntities.ENCODING) + '\n'
        workEventsCsv += u'Set_To,PUSO,Road,Number,Type,Model,Length,Weight,Consist,Owner,Track,Location,Destination,Comment\n'
        for loco in track['locos']:
            workEventsCsv +=  loco['Set_To'] + ',' \
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
        workEventsCsv += u'Set_To,PUSO,Road,Number,Type,Length,Weight,Load,Load_Type,Hazardous,Color,Kernel,Kernel_Size,Owner,Track,Location,Destination,Dest&Track,Final_Dest,FD&Track,Comment,Drop_Comment,Pickup_Comment,RWE\n'
        for car in track['cars']:
            workEventsCsv +=  car['Set_To'] + ',' \
                            + car['PUSO'] + ',' \
                            + car['Road'] + ',' \
                            + car['Number'] + ',' \
                            + car['Type'] + ',' \
                            + car['Length'] + ',' \
                            + car['Weight'] + ',' \
                            + car['Load'] + ',' \
                            + car['Load_Type'] + ',' \
                            + str(car['Hazardous']) + ',' \
                            + car['Color'] + ',' \
                            + car['Kernel'] + ',' \
                            + car['Kernel_Size'] + ',' \
                            + car['Owner'] + ',' \
                            + car['Track'] + ',' \
                            + car['Location'] + ',' \
                            + car['Destination'] + ',' \
                            + car['Dest&Track'] + ',' \
                            + car['Final_Dest'] + ',' \
                            + car['FD&Track'] + ',' \
                            + car['Comment'] + ',' \
                            + car['Drop_Comment'] + ',' \
                            + car['Pickup_Comment'] + ',' \
                            + car['RWE'] \
                            + '\n'

    return workEventsCsv

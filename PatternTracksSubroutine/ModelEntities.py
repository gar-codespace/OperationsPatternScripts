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
            translatedkey = PatternScriptEntities.SB.handleGetMessage(sortKey)
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
    # locoDetailDict['Dest Track'] = locoObject.getDestinationTrackName()
# Modifications used by this plugin
    try:
        locoDetailDict['Consist'] = locoObject.getConsist().getName()
    except:
        locoDetailDict['Consist'] = PatternScriptEntities.BUNDLE['Single']
    locoDetailDict['Set_To'] = u'[  ] '
    locoDetailDict[u'PUSO'] = u'XX'
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
            translatedkey = PatternScriptEntities.SB.handleGetMessage(sortKey)
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

    # carDetailDict[PatternScriptEntities.BUNDLE['Set to']] = '[  ] '
    carDetailDict['Set_To'] = u'[  ] '
    carDetailDict[u'PUSO'] = u'XX'
    carDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat

    return carDetailDict

def makeTextReportHeader(textWorkEventList):
    """Makes the header for generic text reports"""

    headerNames = PatternScriptEntities.readConfigFile('PT')

    textReportHeader    = textWorkEventList['railroad'] + '\n' \
                        + textWorkEventList['trainName'] + '\n' \
                        + textWorkEventList['date'] + '\n\n' \
                        + PatternScriptEntities.BUNDLE['Work Location:'] + ' ' + headerNames['PL'] + '\n\n'

    return textReportHeader

def makeTextReportLocations(textWorkEventList, trackTotals):

    reportWidth = PatternScriptEntities.REPORT_ITEM_WIDTH_MATRIX
    locoItems = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    carItems = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    reportSwitchList = ''
    reportTally = [] # running total for all tracks
    for track in textWorkEventList['locations'][0]['tracks']:
        lengthOfLocos = 0
        lengthOfCars = 0
        trackTally = []
        trackName = track['trackName']
        trackLength = track['length']
        reportSwitchList += PatternScriptEntities.BUNDLE['Track:'] + ' ' + trackName + '\n'
        switchListRow = ''

        for loco in track['locos']:
            lengthOfLocos += int(loco['Length']) + 4
            loco = addStandIns(loco)
            reportSwitchList += loco['Set_To'] + loopThroughRs('loco', loco) + '\n'

        for car in track['cars']:
            lengthOfCars += int(car['Length']) + 4
            car = addStandIns(car)
            reportSwitchList += car['Set_To'] + loopThroughRs('car', car) + '\n'
            trackTally.append(car['Final_Dest'])
            reportTally.append(car['Final_Dest'])

        if trackTotals:
            totalLength = lengthOfLocos + lengthOfCars
            reportSwitchList += PatternScriptEntities.BUNDLE['Total Cars:'] + ' ' \
                + str(len(track['cars'])) + ' ' + PatternScriptEntities.BUNDLE['Track Length:']  + ' ' \
                + str(trackLength) +  ' ' + PatternScriptEntities.BUNDLE['Eqpt. Length:']  + ' ' \
                + str(totalLength) + ' ' +  PatternScriptEntities.BUNDLE['Available:']  + ' '  \
                + str(trackLength - totalLength) \
                + '\n\n'
            reportSwitchList += PatternScriptEntities.BUNDLE['Track Totals for Cars:'] + '\n'
            for track, count in sorted(PatternScriptEntities.occuranceTally(trackTally).items()):
                reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
        reportSwitchList += '\n'

    if trackTotals:
        reportSwitchList += '\n' + PatternScriptEntities.BUNDLE['Report Totals for Cars:'] + '\n'
        for track, count in sorted(PatternScriptEntities.occuranceTally(reportTally).items()):
            reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'

    return reportSwitchList

def addStandIns(rs):
    """Make adjustments to the display version of textWorkEventList"""

    try:
        lt = rs['Load_Type']
        if lt == 'Load':
            lt = 'L'
        if lt == 'Empty':
            lt = 'E'
        rs.update({'Load_Type': lt})
    except:
        pass

    reportModifiers = PatternScriptEntities.readConfigFile('RM')

    try:
        if rs['Final_Dest'] == '':
            rs.update({'Final_Dest': reportModifiers['FD']})
            rs.update({'FD&Track': reportModifiers['FD']})
    except:
        pass

    if rs['Destination'] == '':
        rs.update({'Destination': reportModifiers['DS']})
        rs.update({'Dest&Track': reportModifiers['DS']})


    return rs


def loopThroughRs(type, rsAttribs):
    """Creates a line containing the attrs in get * MessageFormat"""

    reportWidth = PatternScriptEntities.REPORT_ITEM_WIDTH_MATRIX
    switchListRow = ''
    rosetta = PatternScriptEntities.translateMessageFormat()

    if type == 'loco':
        messageFormat = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    if type == 'car':
        messageFormat = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    for lookup in messageFormat:
        item = rosetta[lookup]

        if 'Tab' in item:
            continue

        itemWidth = reportWidth[item]
        switchListRow += PatternScriptEntities.formatText(rsAttribs[item], itemWidth)

    return switchListRow

def makeGenericHeader():
    """A generic header info for any switch list, used to make the ??????????????? JSON file"""

    listHeader = {}
    listHeader['railroad'] = unicode(PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getRailroadName(), PatternScriptEntities.ENCODING)
    listHeader['trainName'] = u'Train Name Placeholder'
    listHeader['trainDescription'] = u'Train Description Placeholder'
    listHeader['trainComment'] = u'Train Comment Placeholder'
    listHeader['date'] = unicode(PatternScriptEntities.timeStamp(), PatternScriptEntities.ENCODING)
    listHeader['locations'] = []

    return listHeader

def writeWorkEventListAsJson(switchList):
    """The generic switch list is written as a ???????????? json"""

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
    """CSV writer does not support utf-8"""

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

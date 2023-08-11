# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

def makeTextReportHeader(patternReport):
    """
    Makes the header for generic text reports
    Called by:
    View.ManageGui.trackPatternButton'
    ViewSetCarsForm.switchListButton
    """

    patternLocation = PSE.readConfigFile('Patterns')['PL']
    divisionName = patternReport['division']
    workLocation = ''
    if divisionName:
        workLocation = divisionName + ' - ' + patternLocation
    else:
        workLocation = patternLocation

    textReportHeader    = patternReport['railroadName'] + '\n\n' + PSE.getBundleItem('Work Location:') + ' ' + workLocation + '\n' + patternReport['date'] + '\n\n'
    
    return textReportHeader


def makeTextReportTracks(trackList, trackTotals):
    """
    Makes the body for generic text reports
    Called by:
    View.ManageGui.trackPatternButton'
    ViewSetCarsForm.switchListButton
    """

    reportSwitchList = ''
    reportTally = [] # running total for all tracks
    for track in trackList:
        lengthOfLocos = 0
        lengthOfCars = 0
        trackTally = []
        trackName = track['trackName']
        trackLength = track['length']
        reportSwitchList += PSE.getBundleItem('Track:') + ' ' + trackName + '\n'

        for loco in track['locos']:
            lengthOfLocos += int(loco['length']) + 4
            reportSwitchList += loco['setTo'] + loopThroughRs('loco', loco) + '\n'

        for car in track['cars']:
            lengthOfCars += int(car['length']) + 4
            reportSwitchList += car['setTo'] + loopThroughRs('car', car) + '\n'
            trackTally.append(car['finalDest'])
            reportTally.append(car['finalDest'])

        if trackTotals:
            totalLength = lengthOfLocos + lengthOfCars
            reportSwitchList += PSE.getBundleItem('Total Cars:') + ' ' \
                + str(len(track['cars'])) + ' ' + PSE.getBundleItem('Track Length:')  + ' ' \
                + str(trackLength) +  ' ' + PSE.getBundleItem('Eqpt. Length:')  + ' ' \
                + str(totalLength) + ' ' +  PSE.getBundleItem('Available:') + ' '  \
                + str(trackLength - totalLength) \
                + '\n\n'
            reportSwitchList += PSE.getBundleItem('Track Totals for Cars:') + '\n'
            for track, count in sorted(PSE.occuranceTally(trackTally).items()):
                reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
        reportSwitchList += '\n'

    if trackTotals:
        reportSwitchList += '\n' + PSE.getBundleItem('Report Totals for Cars:') + '\n'
        for track, count in sorted(PSE.occuranceTally(reportTally).items()):
            reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'

    return reportSwitchList

def loopThroughRs(type, rsAttribs):
    """
    Creates a line containing the attrs in get * MessageFormat
    Called by:
    makeTextReportTracks
    """

    reportWidth = PSE.REPORT_ITEM_WIDTH_MATRIX
    switchListRow = ''
    rosetta = PSE.translateMessageFormat()

    if type == 'loco':
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    if type == 'car':
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    for lookup in messageFormat:
        item = rosetta[lookup]

        if 'tab' in item:
            continue

        itemWidth = reportWidth[item]
        switchListRow += PSE.formatText(rsAttribs[item], itemWidth)

    return switchListRow

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
    Merge the values in textBoxEntry into the ['setTo'] field of switchList.
    Called by:
    ModelSetCarsForm.makeMergedForm
    """

    longestTrackString = findLongestTrackString()
    allTracksAtLoc = getTrackNamesByLocation(None)

    i = 0
    locos = switchList['tracks'][0]['locos']
    for loco in locos:
        userInput = unicode(userInputList[i], PSE.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PSE.formatText('[' + userInput + ']', longestTrackString + 2)
        else:
            setTrack = PSE.formatText('[' + PSE.getBundleItem('Hold') + ']', longestTrackString + 2)

        loco.update({'setTo': setTrack})
        i += 1

    cars = switchList['tracks'][0]['cars']
    for car in cars:
        userInput = unicode(userInputList[i], PSE.ENCODING)

        if userInput in allTracksAtLoc:
            setTrack = PSE.formatText('[' + userInput + ']', longestTrackString + 2)
        else:
            setTrack = PSE.formatText('[' + PSE.getBundleItem('Hold') + ']', longestTrackString + 2)

        car.update({'setTo': setTrack})
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

def getDetailsForTracks(selectedTracks):
    """
    Returns a list of dictionaries.
    """

    detailsForTracks = []
    parseRollingStock = RollingStockParser()

    locationName = PSE.readConfigFile('Patterns')['PL']
    for track in selectedTracks:
        genericTrackDetails = {}
        genericTrackDetails['trackName'] = track
        genericTrackDetails['length'] =  PSE.LM.getLocationByName(locationName).getTrackByName(track, None).getLength()
        genericTrackDetails['locos'] = parseRollingStock.getLocoDetails(track)
        genericTrackDetails['cars'] = parseRollingStock.getCarDetails(track)

        detailsForTracks.append(genericTrackDetails)

    return detailsForTracks


class RollingStockParser:

    def __init__(self):

        self.configFile = PSE.readConfigFile()
        self.locationName = self.configFile['Patterns']['PL']
        self.location = PSE.LM.getLocationByName(self.locationName)

        self.rsOnTrain = self.getRsOnTrains()
        self.kernelTally = self.getKernelTally()

        self.trackName = ''
        self.locoDetails = []
        self.carDetails = []

        return
    
    def getRsOnTrains(self):
        """
        Make a list of all rolling stock that are on built trains.
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

    def getKernelTally(self):
        """
        Makes a hash table of kernel names and kernel sizes.
        """

        tally = []
        for car in PSE.CM.getByIdList():
            kernelName = car.getKernelName()
            if kernelName:
                tally.append(kernelName)

        kernelTally = PSE.occuranceTally(tally)

        return kernelTally
    
    def getLocoDetails(self, trackName):
        """
        Mini controller.
        Gets the details for all engines at the selected track.
        """

        self.locoDetails = []

        self.trackName = trackName
        track = self.location.getTrackByName(trackName, None)

        locos = PSE.EM.getList(track)
        for loco in locos:
            locoDetails = self.getDetailsForLoco(loco)
            locoDetails.update(self.getDetailsForRollingStock(loco))
            self.locoDetails.append(locoDetails)

        self.sortLocoList()

        return self.locoDetails

    def getCarDetails(self, trackName):
        """
        Mini controller.
        Gets the details for all cars at the selected track.
        """

        self.carDetails = []

        self.trackName = trackName
        track = self.location.getTrackByName(trackName, None)

        cars = PSE.CM.getList(track)
        for car in cars:
            carDetails = self.getDetailsForCar(car)
            carDetails.update(self.getDetailsForRollingStock(car))
            self.carDetails.append(carDetails)

        self.sortCarList()

        return self.carDetails
    
    def getDetailsForRollingStock(self, rs):

        rsDetailDict = {}

    # Common items for all JMRI RS
        rsDetailDict['road'] = rs.getRoadName()
        rsDetailDict['number'] = rs.getNumber()
        rsDetailDict['carType'] = rs.getTypeName()
        rsDetailDict['length'] = rs.getLength()
        rsDetailDict['color'] = rs.getColor()
        rsDetailDict['weight'] = rs.getWeightTons()
        rsDetailDict['comment'] = rs.getComment()
        rsDetailDict['division'] = rs.getDivisionName()
        rsDetailDict['location'] = rs.getLocationName()
        rsDetailDict['track'] = rs.getTrackName()
        rsDetailDict['destination'] = rs.getDestinationName()
        try: # Depending on which version of JMRI Ops Pro
            rsDetailDict['owner'] = rs.getOwner()
        except:
            # print('Exception at: Patterns.ModelEntities.getDetailsForLoco')
            rsDetailDict['owner'] = rs.getOwnerName()
    # Common items for all OPS RS
        rsDetailDict['setTo'] = u'[  ] '
        rsDetailDict[u'puso'] = u' '
        rsDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat
        rsDetailDict['onTrain'] = False
        if rs in self.rsOnTrain: # Flag to mark if RS is on a built train
            rsDetailDict['onTrain'] = True

        return rsDetailDict
     
    def getDetailsForLoco(self, locoObject):
        """
        Mimics jmri.jmrit.operations.setup.Setup.getEngineAttributes()
        """

        locoDetailDict = {}

        locoDetailDict['model'] = locoObject.getModel()
        locoDetailDict['dccAddress'] = locoObject.getDccAddress()
    # Modifications used by this plugin
        try:
            locoDetailDict['consist'] = locoObject.getConsist().getName()
        except:
            locoDetailDict['consist'] = PSE.getBundleItem('Single')

        return locoDetailDict

    def getDetailsForCar(self, carObject):
        """
        Mimics jmri.jmrit.operations.setup.Setup.getCarAttributes()
        """

        track = self.location.getTrackByName(carObject.getTrackName(), None)
        try:
            kernelSize = self.kernelTally[carObject.getKernelName()]
        except:
            kernelSize = 0

        carDetailDict = {}

        carDetailDict['loadType'] = carObject.getLoadType()
        carDetailDict['load'] = carObject.getLoadName()
        carDetailDict['hazardous'] = carObject.isHazardous()
        carDetailDict['kernel'] = carObject.getKernelName()
        carDetailDict['kernelSize'] = str(kernelSize)
        carDetailDict['dest&Track'] = carObject.getDestinationTrackName()
        carDetailDict['finalDest'] = carObject.getFinalDestinationName()
        carDetailDict['fd&Track'] = carObject.getFinalDestinationTrackName()
        carDetailDict['setOutMsg'] = track.getCommentSetout()
        carDetailDict['pickupMsg'] = track.getCommentPickup()
        carDetailDict['rwe'] = carObject.getReturnWhenEmptyDestinationName()
        carDetailDict['rwl'] = carObject.getReturnWhenLoadedDestinationName()

        return carDetailDict

    def sortLocoList(self):
        """
        Try/Except protects against bad edit of config file
        Sort order of PSE.readConfigFile('RM')['SL'] is top down
        """

        sortLocos = self.configFile['Patterns']['RM']['SL']
        for sortKey in sortLocos:
            try:
                translatedkey = (sortKey)
                self.locoDetails.sort(key=lambda row: row[translatedkey])
            except:
                print('No engines or list not sorted')

        return


    def sortCarList(self):
        """
        Try/Except protects against bad edit of config file
        Sort order of PSE.readConfigFile('Patterns')['RM']['SC'] is top down
        """

        sortCars = self.configFile['Patterns']['RM']['SC']
        for sortKey in sortCars:
            try:
                translatedkey = (sortKey)
                self.carDetails.sort(key=lambda row: row[translatedkey])
            except:
                print('No cars or list not sorted')

        return

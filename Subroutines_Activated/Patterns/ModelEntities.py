# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

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
    if divisionName and patternLocation:
        workLocation = divisionName + ' - ' + patternLocation
    elif patternLocation:
        workLocation = patternLocation

    textReportHeader = patternReport['railroadName'] + '\n\n' + PSE.getBundleItem('Work Location:') + ' ' + workLocation + '\n' + patternReport['date'] + '\n\n'
    
    return textReportHeader

def makeTextReportTracks(trackList, trackTotals):
    """
    trackList is a list
    trackTotals is a bool
    Makes the body for generic text reports
    Called by:
    View.ManageGui.trackPatternButton'
    ViewSetCarsForm.switchListButton
    """

    reportSwitchList = ''
    reportTally = [] # running total for all tracks
    isSequenceHash, sequenceHash = PSE.getSequenceHash()

    for track in trackList:
        lengthOfLocos = 0
        lengthOfCars = 0
        trackTally = []
        trackName = track['trackName']
        trackLength = track['length']
        reportSwitchList += PSE.getBundleItem('Track:') + ' ' + trackName + '\n'

        for loco in track['locos']:
            lengthOfLocos += int(loco[PSE.SB.handleGetMessage('Length')]) + 4

            seqStandIn = ''
            if loco['setTo'] == '[  ] ' and isSequenceHash:
                seqStandIn = sequenceHash['locos'][loco['Id']]
                seqStandIn = seqStandIn - 8000
                seqStandIn = str(seqStandIn).rjust(3, '0') + '  '
            else:
                seqStandIn = loco['setTo']

            reportSwitchList += seqStandIn + loopThroughRs('loco', loco) + '\n'

        for car in track['cars']:
            lengthOfCars += int(car[PSE.SB.handleGetMessage('Length')]) + 4

            seqStandIn = ''
            if car['setTo'] == '[  ] ' and isSequenceHash:
                seqStandIn = sequenceHash['cars'][car['Id']]
                # print(sequenceHash['cars'][car['Id']])
                seqStandIn = seqStandIn - 8000
                # print(seqStandIn)
                seqStandIn = str(seqStandIn).rjust(3, '0') + '  '
            else:
                seqStandIn = car['setTo']

            reportSwitchList += seqStandIn + loopThroughRs('car', car) + '\n'

            trackTally.append(car[PSE.SB.handleGetMessage('Final_Dest')])
            reportTally.append(car[PSE.SB.handleGetMessage('Final_Dest')])

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
    The message format is in the locales language.
    Called by:
    makeTextReportTracks
    """

    reportWidth = PSE.REPORT_ITEM_WIDTH_MATRIX
    switchListRow = ''

    if type == 'loco':
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    if type == 'car':
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    for item in messageFormat:
        if 'Tab' in item:
            continue
    # Special case handling for the hazardous flag
        if item == PSE.SB.handleGetMessage('Hazardous') and rsAttribs[item]:
            labelName = item
        elif item == PSE.SB.handleGetMessage('Hazardous') and not rsAttribs[item]:
            labelName = ' '
        else:
            labelName = rsAttribs[item]

        itemWidth = reportWidth[item]
        rowItem = PSE.formatText(labelName, itemWidth)
        switchListRow += rowItem

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

    prefix = ['[' + PSE.getBundleItem('Hold') + ']']
    location = PSE.LM.getLocationByName(PSE.readConfigFile('Patterns')['PL'])
    for track in location.getTracksByNameList(None):
        prefix.append(track.toString())
    longestTrackString = PSE.findLongestStringLength(prefix)

    allTracksAtLoc = getTrackNamesByLocation(None)

    currentTrack = switchList['tracks'][0]['trackName']

    i = 0
    locos = switchList['tracks'][0]['locos']
    for loco in locos:
        userInput = unicode(userInputList[i], PSE.ENCODING)
        if userInput in allTracksAtLoc and userInput != currentTrack:
            setTrack = PSE.formatText('[' + userInput + ']', longestTrackString + 2)
        else:
            setTrack = PSE.formatText('[' + PSE.getBundleItem('Hold') + ']', longestTrackString + 2)

        loco.update({'setTo': setTrack})
        i += 1

    cars = switchList['tracks'][0]['cars']
    for car in cars:
        userInput = unicode(userInputList[i], PSE.ENCODING)

        if userInput in allTracksAtLoc and userInput != currentTrack:
            setTrack = PSE.formatText('[' + userInput + ']', longestTrackString + 2)
        else:
            setTrack = PSE.formatText('[' + PSE.getBundleItem('Hold') + ']', longestTrackString + 2)

        car.update({'setTo': setTrack})
        i += 1

    return switchList

# def findLongestTrackString():
#     """
#     Called by:
#     merge
#     """

#     hold = '[' + PSE.getBundleItem('Hold') + ']'
#     longestTrackString = len(hold)

#     location = PSE.LM.getLocationByName(PSE.readConfigFile('Patterns')['PL'])
#     for track in location.getTracksList():
#         longestTrackString = max(longestTrackString, len(track.getName()))

#     return longestTrackString









def getDetailsByTrack(selectedTracks):
    """
    Returns a list of dictionaries.
    Copies structure of JMRI manifest.
    """

    locationName = PSE.readConfigFile('Patterns')['PL']

    parseRollingStock = ParseRollingStock()

    detailsByTracks = []

    for track in selectedTracks:
        genericTrackDetails = {}
        genericTrackDetails['userName'] = track
        genericTrackDetails['trainDirection'] = 1
        trackLength = PSE.LM.getLocationByName(locationName).getTrackByName(track, None).getLength()
        trackUnit = PSE.JMRI.jmrit.operations.setup.Setup.getLengthUnit()
        genericTrackDetails['length'] = {'length':trackLength, 'unit':trackUnit}

        

        genericTrackDetails['engines'] = {'add':parseRollingStock.getLocoDetails(track), 'remove':[]}
        genericTrackDetails['cars'] = {'add':parseRollingStock.getCarDetails(track), 'remove':[]}

        detailsByTracks.append(genericTrackDetails)

    return detailsByTracks


class ParseRollingStock:

    def __init__(self):

        self.configFile = PSE.readConfigFile()
        self.isSequence, self.sequenceHash = PSE.getSequenceHash()

        self.locationName = self.configFile['Patterns']['PL']
        self.location = PSE.LM.getLocationByName(self.locationName)

        self.rsOnTrain = self.getRsOnTrains()
        self.kernelTally = self.getKernelTally()

        self.trackName = ''
        self.locoDetails = []
        self.carDetails = []

        return
    
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

    def getDetailsForLoco(self, locoObject):
        """
        Gets JSON file attribs specific to engines.
        """

        locoDetailDict = {}

    # Necessary JMRI attributes
        locoDetailDict['carType'] = locoObject.getTypeName()
        locoDetailDict['model'] = locoObject.getModel()
    # Modifications used by this plugin
        try:
            locoDetailDict['consist'] = locoObject.getConsist().getName()
        except:
            locoDetailDict['consist'] = PSE.getBundleItem('Single')
    # Additional OPS attributes for locos
        locoDetailDict['dccAddress'] = locoObject.getDccAddress()
        locoDetailDict['sequence'] = self.getSequence('locos', locoObject)

        return locoDetailDict
    
    def getDetailsForCar(self, carObject):
        """
        Gets JSON file attribs specific to cars.
        """

        carDetailDict = {}

        try:
            kernelSize = self.kernelTally[carObject.getKernelName()]
        except:
            kernelSize = 0

    # Necessary JMRI attributes
        carDetailDict['carType'] = carObject.getTypeName()
        carDetailDict['load'] = carObject.getLoadName()
        carDetailDict['loadType'] = carObject.getLoadType()
        carDetailDict['hazardous'] = carObject.isHazardous()
        carDetailDict['kernel'] = carObject.getKernelName()
        carDetailDict['kernelSize'] = kernelSize
        carDetailDict['finalDestination'] = carObject.getFinalDestinationName()
        carDetailDict['fdTrack'] = carObject.getFinalDestinationTrackName()
        carDetailDict['removeComment'] = carObject.getDropComment()
        carDetailDict['addComment'] = carObject.getPickupComment()
        carDetailDict['returnWhenEmpty'] = carObject.getReturnWhenEmptyDestinationName()
    # Additional OPS attributes for cars
        carDetailDict['isLocal'] = True
        carDetailDict['caboose'] = carObject.isCaboose()
        carDetailDict['passenger'] = carObject.isPassenger()
        carDetailDict['fred'] = carObject.hasFred()
        if self.isSequence:
            carDetailDict['sequence'] = self.getSequence('cars', carObject)
        else:
            carDetailDict['sequence'] = 8000

        return carDetailDict

    def getDetailsForRollingStock(self, rs):
        """
        Gets JSON file attribs common to engines and cars.
        """

        rsDetailDict = {}

    # Common attribs for all JMRI RS
        rsDetailDict['road'] = rs.getRoadName()
        rsDetailDict['number'] = rs.getNumber()
        rsDetailDict['length'] = rs.getLength()
        rsDetailDict['weightTons'] = rs.getAdjustedWeightTons()
        rsDetailDict['color'] = rs.getColor()
        rsDetailDict['owner'] = rs.getOwnerName()
        rsDetailDict['division'] = rs.getDivisionName()
        rsDetailDict['location'] = {'userName':rs.getLocationName(), 'track':{'userName':rs.getTrackName()}}
        rsDetailDict['destination'] = {'userName':rs.getDestinationName(), 'track':{'userName':rs.getDestinationTrackName()}}
        rsDetailDict['comment'] = rs.getComment()
    # Additional attribs for OPS
        rsDetailDict['Id'] = rs.getRoadName() + ' ' + rs.getNumber()
        rsDetailDict[' '] = ' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat
        rsDetailDict['onTrain'] = False
        if rs in self.rsOnTrain: # Flag to mark if RS is on a built train
            rsDetailDict['onTrain'] = True

        # try: # Depending on which version of JMRI Ops Pro
        #     rsDetailDict[PSE.SB.handleGetMessage('Owner')] = rs.getOwner()
        # except:
        return rsDetailDict
 
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

    def getSequence(self, rs, object):
        """
        rs is either cars or locos to choose the subset of the hash.
        """

        dataHash = self.sequenceHash[rs]
        rsID = object.getRoadName() + ' ' + object.getNumber()

        return dataHash[rsID]

    def sortLocoList(self):
        """
        Try/Except protects against bad edit of config file
        Sort order of PSE.readConfigFile('US')['SL'] is top down
        """
        if self.isSequence:
            self.locoDetails.sort(key=lambda row: row['sequence'])
        else:
            sortLocos = self.configFile['Patterns']['US']['SL']
            for sortKey in sortLocos:
                try:
                    translatedkey = (PSE.SB.handleGetMessage(sortKey))
                    self.locoDetails.sort(key=lambda row: row[translatedkey])
                except:
                    print('No engines or list not sorted')

        return

    def sortCarList(self):
        """
        Try/Except protects against bad edit of config file
        Sort order of PSE.readConfigFile('Patterns')['US']['SC'] is top down
        """

        if self.isSequence:
            self.carDetails.sort(key=lambda row: row['sequence'])
        else:
            sortCars = self.configFile['Patterns']['US']['SC']
            for sortKey in sortCars:
                try:
                    translatedkey = (PSE.SB.handleGetMessage(sortKey))
                    self.carDetails.sort(key=lambda row: row[translatedkey])
                except:
                    print('No cars or list not sorted')

        return















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
        self.isSequence, self.sequenceHash = PSE.getSequenceHash()

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
        rsDetailDict[PSE.SB.handleGetMessage('Road')] = rs.getRoadName()
        rsDetailDict[PSE.SB.handleGetMessage('Number')] = rs.getNumber()
        rsDetailDict[PSE.SB.handleGetMessage('Type')] = rs.getTypeName()
        rsDetailDict[PSE.SB.handleGetMessage('Length')] = rs.getLength()
        rsDetailDict[PSE.SB.handleGetMessage('Color')] = rs.getColor()
        rsDetailDict[PSE.SB.handleGetMessage('Weight')] = rs.getWeightTons()
        rsDetailDict[PSE.SB.handleGetMessage('Comment')] = rs.getComment()
        rsDetailDict[PSE.SB.handleGetMessage('Division')] = rs.getDivisionName()
        rsDetailDict[PSE.SB.handleGetMessage('Location')] = rs.getLocationName()
        rsDetailDict[PSE.SB.handleGetMessage('Track')] = rs.getTrackName()
        rsDetailDict[PSE.SB.handleGetMessage('Destination')] = rs.getDestinationName()
        try: # Depending on which version of JMRI Ops Pro
            rsDetailDict[PSE.SB.handleGetMessage('Owner')] = rs.getOwner()
        except:
            rsDetailDict[PSE.SB.handleGetMessage('Owner')] = rs.getOwnerName()
    # Common items for all OPS RS
        rsDetailDict['Id'] = rs.getRoadName() + ' ' + rs.getNumber()
        rsDetailDict['setTo'] = '[  ] '
        rsDetailDict['puso'] = ' '
        rsDetailDict[' '] = ' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat
        rsDetailDict['onTrain'] = False
        if rs in self.rsOnTrain: # Flag to mark if RS is on a built train
            rsDetailDict['onTrain'] = True

        return rsDetailDict
     
    def getDetailsForLoco(self, locoObject):
        """
        Mimics jmri.jmrit.operations.setup.Setup.getEngineAttributes()
        """

        locoDetailDict = {}

        locoDetailDict[PSE.SB.handleGetMessage('Model')] = locoObject.getModel()
        locoDetailDict[PSE.SB.handleGetMessage('DCC_Address')] = locoObject.getDccAddress()
    # Modifications used by this plugin
        try:
            locoDetailDict[PSE.SB.handleGetMessage('Consist')] = locoObject.getConsist().getName()
        except:
            locoDetailDict[PSE.SB.handleGetMessage('Consist')] = PSE.getBundleItem('Single')
    # OPS loco attributes
        locoDetailDict['isCaboose'] = False
        locoDetailDict['isPassenger'] = False
        locoDetailDict['isEngine'] = True
        locoDetailDict['sequence'] = 8000

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
    # JMRI car attributes
        carDetailDict[PSE.SB.handleGetMessage('Load_Type')] = carObject.getLoadType()
        carDetailDict[PSE.SB.handleGetMessage('Load')] = carObject.getLoadName()
        carDetailDict[PSE.SB.handleGetMessage('Hazardous')] = carObject.isHazardous()
        carDetailDict[PSE.SB.handleGetMessage('Kernel')] = carObject.getKernelName()
        carDetailDict[PSE.SB.handleGetMessage('Kernel_Size')] = str(kernelSize)
        carDetailDict[PSE.SB.handleGetMessage('Dest&Track')] = carObject.getDestinationTrackName()
        carDetailDict[PSE.SB.handleGetMessage('Final_Dest')] = carObject.getFinalDestinationName()
        carDetailDict[PSE.SB.handleGetMessage('FD&Track')] = carObject.getFinalDestinationTrackName()
        carDetailDict[PSE.SB.handleGetMessage('SetOut_Msg')] = track.getCommentSetout()
        carDetailDict[PSE.SB.handleGetMessage('PickUp_Msg')] = track.getCommentPickup()
        carDetailDict[PSE.SB.handleGetMessage('RWE')] = carObject.getReturnWhenEmptyDestinationName()
        try:
            carDetailDict[PSE.SB.handleGetMessage('RWL')] = carObject.getReturnWhenLoadedDestinationName()
        except:
            carDetailDict['RWL'] = carObject.getReturnWhenLoadedDestinationName()
    # OPS car attributes
        carDetailDict['isCaboose'] = carObject.isCaboose()
        carDetailDict['isPassenger'] = carObject.isPassenger()
        carDetailDict['isEngine'] = False
        if self.isSequence:
            carDetailDict['sequence'] = self.getSequence('cars', carObject)
        else:
            carDetailDict['sequence'] = 8000


        return carDetailDict

    def getSequence(self, rs, object):
        """
        rs is either cars or locos to choose the subset of the hash.
        """

        dataHash = self.sequenceHash[rs]
        rsID = object.getRoadName() + ' ' + object.getNumber()

        return dataHash[rsID]

    def sortLocoList(self):
        """
        Try/Except protects against bad edit of config file
        Sort order of PSE.readConfigFile('US')['SL'] is top down
        """
        if self.isSequence:
            self.locoDetails.sort(key=lambda row: row['sequence'])
        else:
            sortLocos = self.configFile['Patterns']['US']['SL']
            for sortKey in sortLocos:
                try:
                    translatedkey = (PSE.SB.handleGetMessage(sortKey))
                    self.locoDetails.sort(key=lambda row: row[translatedkey])
                except:
                    print('No engines or list not sorted')

        return

    def sortCarList(self):
        """
        Try/Except protects against bad edit of config file
        Sort order of PSE.readConfigFile('Patterns')['US']['SC'] is top down
        """

        if self.isSequence:
            self.carDetails.sort(key=lambda row: row['sequence'])
        else:
            sortCars = self.configFile['Patterns']['US']['SC']
            for sortKey in sortCars:
                try:
                    translatedkey = (PSE.SB.handleGetMessage(sortKey))
                    self.carDetails.sort(key=lambda row: row[translatedkey])
                except:
                    print('No cars or list not sorted')

        return

# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
Helper methods for any of the Model level modules.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

def getDetailsByTrack(selectedTracks):
    """
    Returns a list of dictionaries.
    Copies structure of JMRI manifest.
    Big difference:
    JMRI ['locations'] lists locations
    OPS ['locations'] lists tracks
    """

    locationName = PSE.readConfigFile('Patterns')['PL']

    parseRollingStock = ParseRollingStock()

    detailsByTracks = []

    for trackName in selectedTracks:
        track = PSE.LM.getLocationByName(locationName).getTrackByName(trackName, None)
        genericTrackDetails = {}
        genericTrackDetails['userName'] = trackName
        genericTrackDetails['trainDirection'] = track.getTrainDirections()
        genericTrackDetails['loads'] = 0
        genericTrackDetails['empties'] = 0
        trackLength = track.getLength()
        trackUnit = PSE.JMRI.jmrit.operations.setup.Setup.getLengthUnit()
        genericTrackDetails['length'] = {'length':trackLength, 'unit':trackUnit}

        genericTrackDetails['engines'] = {'add':parseRollingStock.getLocoDetails(trackName), 'remove':[]}
        genericTrackDetails['cars'] = {'add':parseRollingStock.getCarDetails(trackName), 'remove':[]}

        detailsByTracks.append(genericTrackDetails)

    return detailsByTracks


class ParseRollingStock:

    def __init__(self):

        self.configFile = PSE.readConfigFile()
        # self.isSequence, self.sequenceHash = PSE.getSequenceHash()

        self.locationName = self.configFile['Patterns']['PL']
        self.location = PSE.LM.getLocationByName(self.locationName)

        # self.rsOnTrain = self.getRsOnTrains()

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

        consistName = locoObject.getConsist().getName()
        eConsist = PSE.getBundleItem('Single')
        if consistName:
            eConsist = consistName

    # JMRI attributes
        locoDetailDict['carType'] = locoObject.getTypeName()
        locoDetailDict['model'] = locoObject.getModel()
        locoDetailDict['dccAddress'] = locoObject.getDccAddress()
        locoDetailDict['consist'] = eConsist

        return locoDetailDict
    
    def getDetailsForCar(self, carObject):
        """
        Gets JSON file attribs specific to cars.
        """

        carDetailDict = {}
        kernelName = carObject.getKernelName()
        kSize = 0
        if kernelName:
            kSize = PSE.KM.getKernelByName(kernelName).getSize()

    # JMRI attributes
        carDetailDict['carType'] = carObject.getTypeName()
        carDetailDict['load'] = carObject.getLoadName()
        carDetailDict['loadType'] = carObject.getLoadType()
        carDetailDict['hazardous'] = carObject.isHazardous()
        carDetailDict['kernel'] = carObject.getKernelName()
        carDetailDict['kernelSize'] = str(kSize)
        carDetailDict['finalDestination'] = {'userName':carObject.getFinalDestinationName(), 'track':{'userName':carObject.getFinalDestinationTrackName()}}
        carDetailDict['removeComment'] = carObject.getDropComment()
        carDetailDict['addComment'] = carObject.getPickupComment()
        carDetailDict['returnWhenEmpty'] = carObject.getReturnWhenEmptyDestinationName()
        carDetailDict['isLocal'] = True
        carDetailDict['caboose'] = carObject.isCaboose()
        carDetailDict['passenger'] = carObject.isPassenger()
        carDetailDict['fred'] = carObject.hasFred()

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
        rsDetailDict['weight'] = rs.getWeight()
        rsDetailDict['weightTons'] = rs.getAdjustedWeightTons()
        rsDetailDict['color'] = rs.getColor()
        rsDetailDict['owner'] = rs.getOwnerName()
        rsDetailDict['division'] = rs.getDivisionName()
        rsDetailDict['location'] = {'userName':rs.getLocationName(), 'track':{'userName':rs.getTrackName()}}
        rsDetailDict['destination'] = {'userName':rs.getDestinationName(), 'track':{'userName':rs.getDestinationTrackName()}}
        rsDetailDict['comment'] = rs.getComment()
    # Additional attribs for OPS
        rsDetailDict['id'] = '{} {}'.format(rs.getRoadName(), rs.getNumber())
        rsDetailDict[' '] = ' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat
        rsDetailDict['trainName'] = rs.getTrainName()

        return rsDetailDict
 
    # def getRsOnTrains(self):
    #     """
    #     Make a list of all rolling stock that are on built trains.
    #     """

    #     builtTrainList = []
    #     for train in PSE.TM.getTrainsByStatusList():
    #         if train.isBuilt():
    #             builtTrainList.append(train)

    #     listOfAssignedRs = []
    #     for train in builtTrainList:
    #         listOfAssignedRs += PSE.CM.getByTrainList(train)
    #         listOfAssignedRs += PSE.EM.getByTrainList(train)

    #     return listOfAssignedRs

    # def getSequence(self, rs, object):
    #     """
    #     rs is either cars or locos to choose the subset of the hash.
    #     """

    #     dataHash = self.sequenceHash[rs]
    #     rsID = object.getRoadName() + ' ' + object.getNumber()

    #     return dataHash[rsID]

    def sortLocoList(self):
        """
        Try/Except protects against bad edit of config file
        Sort order of PSE.readConfigFile('US')['SL'] is top down
        """

    # Process the sort list
        try:
            sortRS = self.configFile['Patterns']['US']['SL']
            sortRS.items().sort(key=lambda row: row[1])
        except:
            print('No engines were sorted')
            return
        
        sortList = []
        for sortKey, include in sortRS.items():
            if include != 0:
                sortList.append(sortKey)

        if not sortList:
            print('No engines were sorted')
            return

    # Sort the loco list
        for sortKey in sortList:
            sortKey = sortKey.split()
            try:
                self.locoDetails.sort(key=lambda row: row[sortKey[0]][sortKey[1]])
            except:
                self.locoDetails.sort(key=lambda row: row[sortKey[0]])

        print('{} engines were sorted'.format(str(len(self.locoDetails))))

        return

    def sortCarList(self):
        """
        Sorts the car list by value in self.configFile['Patterns']['US']['SC']
        A value of 0 in self.configFile['Patterns']['US']['SC'] means the item is excluded
        """

    # Process the sort list
        try:
            sortRS = self.configFile['Patterns']['US']['SC']
            sortRS.items().sort(key=lambda row: row[1])
        except:
            print('No cars were sorted')
            return
        
        sortList = []
        for sortKey, include in sortRS.items():
            if include != 0:
                sortList.append(sortKey)

        if not sortList:
            print('No cars were sorted')
            return

    # Sort the car list
        for sortKey in sortList:
            sortKey = sortKey.split()
            try:
                self.carDetails.sort(key=lambda row: row[sortKey[0]][sortKey[1]])
            except:
                self.carDetails.sort(key=lambda row: row[sortKey[0]])
                
        print('{} cars were sorted'.format(str(len(self.carDetails))))

        return

def getTrackNamesByLocation(trackType):

    patternLocation = PSE.readConfigFile('Patterns')['PL']
    allTracksAtLoc = []
    try: # Catch on the fly user edit of config file error
        for track in PSE.LM.getLocationByName(patternLocation).getTracksByNameList(trackType):
            allTracksAtLoc.append(unicode(track.getName(), PSE.ENCODING))
        return allTracksAtLoc
    except AttributeError:
        return allTracksAtLoc

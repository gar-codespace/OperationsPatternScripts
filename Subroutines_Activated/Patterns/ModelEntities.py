# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
Helper methods for any of the Model level modules.
"""

from opsEntities import PSE

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

def getLocationNamesByDivision(divisionName):
    """
    Returned list is sorted.
    """

    locationsByDivision = []

    if divisionName == None:
        for location in PSE.LM.getList():
            if not location.getDivisionName():
                locationsByDivision.append(location.getName())
    else:
        for location in PSE.LM.getList():
            if location.getDivisionName() == divisionName:
                locationsByDivision.append(location.getName())

    return sorted(locationsByDivision)

def getDetailsByTrack(selectedTracks, reportToggle):
    """
    Returns a list of dictionaries.
    Copies structure of JMRI manifest.
    Big difference:
    JMRI ['locations'] lists locations
    OPS ['locations'] lists tracks
    """

    locationName = PSE.readConfigFile('Patterns')['PL']
    location = PSE.LM.getLocationByName(locationName)

    parseRollingStock = ParseRollingStock(reportToggle)

    detailsByTracks = []

    for trackName in selectedTracks:
        track = location.getTrackByName(trackName, None)
        carCount = track.getNumberCars()
        loadCount = 0
        for car in PSE.CM.getList(track):
            if car.getLoadType() == 'load' or car.getLoadName() == 'L':
                loadCount += 1

        genericTrackDetails = {}
        genericTrackDetails['userName'] = trackName
        genericTrackDetails['trainDirection'] = track.getTrainDirections()
        genericTrackDetails['total'] = carCount
        genericTrackDetails['loads'] = loadCount
        genericTrackDetails['empties'] = carCount - loadCount
        trackLength = track.getLength()
        trackUnit = PSE.JMRI.jmrit.operations.setup.Setup.getLengthUnit()
        genericTrackDetails['length'] = {'length':trackLength, 'unit':trackUnit}

        genericTrackDetails['engines'] = {'add':parseRollingStock.getLocoDetails(trackName), 'remove':[]}
        genericTrackDetails['cars'] = {'add':parseRollingStock.getCarDetails(trackName), 'remove':[]}

        detailsByTracks.append(genericTrackDetails)

    return detailsByTracks


class ParseRollingStock:
    """
    Report toggle:
    true if the list data is for a OPS pattern report,
    false if the data is for a OPS switch list
    """

    def __init__(self, reportToggle):

        self.reportToggle = reportToggle # True = pattern report, False = switch list

        self.configFile = PSE.readConfigFile()

        self.locationName = self.configFile['Patterns']['PL']
        self.location = PSE.LM.getLocationByName(self.locationName)

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

        if self.reportToggle:
            self.sortLocosByAttribute()

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

        if self.reportToggle:
            self.sortCarsByAttribute()
        else:
            self.sortCarsBySequence()

        return self.carDetails

    def getDetailsForLoco(self, locoObject):
        """
        Gets JSON file attribs specific to engines.
        """

        locoDetailDict = {}

        try:
            consistName = locoObject.getConsist().getName()
        except:
            consistName = PSE.getBundleItem('Single')

    # JMRI attributes
        locoDetailDict['carType'] = locoObject.getTypeName()
        locoDetailDict['model'] = locoObject.getModel()
        locoDetailDict['dccAddress'] = locoObject.getDccAddress()
        locoDetailDict['consist'] = consistName

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
        try:
            rsDetailDict['owner'] = rs.getOwner() # JMRI v4
        except:
            rsDetailDict['owner'] = rs.getOwnerName() # JMRI v5
        rsDetailDict['division'] = rs.getDivisionName()
        rsDetailDict['location'] = {'userName':rs.getLocationName(), 'track':{'userName':rs.getTrackName()}}
        rsDetailDict['destination'] = {'userName':rs.getDestinationName(), 'track':{'userName':rs.getDestinationTrackName()}}
        rsDetailDict['comment'] = rs.getComment()
    # Additional attribs for OPS
        rsDetailDict['id'] = u'{} {}'.format(rs.getRoadName(), rs.getNumber())
        rsDetailDict[' '] = ' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat
        rsDetailDict['trainName'] = rs.getTrainName()

        return rsDetailDict

    def sortLocosByAttribute(self):
        """
        Try/Except protects against bad edit of config file
        Sort order of PSE.readConfigFile('US')['SL'] is top down
        """

        sortList = PSE.getSortList('SL')
        if not sortList:
            print('Car list not sorted')
            return

    # Sort the loco list
        for sortKey in PSE.getSortList('SL'):
            sortKey = sortKey.split()
            try:
                self.locoDetails.sort(key=lambda row: row[sortKey[0]][sortKey[1]])
            except:
                self.locoDetails.sort(key=lambda row: row[sortKey[0]])

        print('Sort engines by {}'.format(sortList))
        return

    def sortCarsByAttribute(self):
        """
        Sorts the car list by value in self.configFile['Patterns']['US']['SC']
        A value of 0 in self.configFile['Patterns']['US']['SC'] means the item is excluded
        """

        sortList = PSE.getSortList('SC')
        if not sortList:
            print('Car list not sorted')
            return

    # Sort the car list
        for sortKey in sortList:
            sortKey = sortKey.split()
            try:
                self.carDetails.sort(key=lambda row: row[sortKey[0]][sortKey[1]])
            except:
                self.carDetails.sort(key=lambda row: row[sortKey[0]])
                
        print('Sort cars by {}'.format(sortList))

        return

    def sortCarsBySequence(self):
        """
        If the sequence data is available.
        """

        for car in self.carDetails:
            carObj = PSE.CM.getByRoadAndNumber(car['road'], car['number'])
            try:
                car["sequence"] = carObj.getValue()
            except:
                car["sequence"] = 6000

        try:
            self.carDetails.sort(key=lambda row: row['sequence'])
            print('Sort cars by sequence number')
        except:
            print('Car list not sorted')

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

# coding=utf-8
# © 2021, 2022 Greg Ritacco

import jmri

from codecs import open as codecsOpen
import logging
import time

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.ModelEntities'
SCRIPT_REV = 20220101

def convertJmriDateToEpoch(jmriTime):
    """2022-02-26T17:16:17.807+0000"""

    epochTime = time.mktime(time.strptime(jmriTime, "%Y-%m-%dT%H:%M:%S.%f+0000"))

    if time.localtime(epochTime).tm_isdst and time.daylight: # If local dst and dst are both 1
        epochTime -= time.altzone
    else:
        epochTime -= time.timezone # in seconds

    return epochTime

def parseJmriLocations(location):

    tpLocation = {}
    tpLocation['locationName'] = location['userName']
    tpLocation['tracks'] = []

    locoList = []
    carList = []
    for loco in location[u'engines'][u'add']:
        line = parseRollingStockAsDict(loco)
        line['PUSO'] = 'PL'
        locoList.append(line)
    for loco in location[u'engines'][u'remove']:
        line = parseRollingStockAsDict(loco)
        line['PUSO'] = 'SL'
        locoList.append(line)
    for car in location['cars']['add']:
        line = parseRollingStockAsDict(car)
        line['PUSO'] = 'PC'
        carList.append(line)
    for car in location['cars']['remove']:
        line = parseRollingStockAsDict(car)
        line['PUSO'] = 'SC'
        carList.append(line)

    locationTrack = {}
    locationTrack['locos'] = locoList
    locationTrack['cars'] = carList
    locationTrack['trackName'] = 'Track Name'
    locationTrack['length'] = 0

    tpLocation['tracks'].append(locationTrack)

    return tpLocation

def parseRollingStockAsDict(rS):

    rsDict = {}
    rsDict['Road'] = unicode(rS[u'road'], PatternScriptEntities.ENCODING)
    rsDict['Number'] = rS[u'number']

    try:
        rsDict[u'Model'] = rS[u'model']
    except KeyError:
        rsDict[u'Model'] = 'N/A'
    try:
        rsDict[u'Type'] = rS[u'carType'] + "-" + rS[u'carSubType']
    except:
        rsDict[u'Type'] = rS[u'carType']
    try:
        rsDict[u'Load'] = rS['load']
    except:
        rsDict[u'Load'] = 'O'
    rsDict[u'Length'] = rS[u'length']
    rsDict[u'Weight'] = rS[u'weightTons']
    rsDict[u'Track'] = unicode(rS[u'location'][u'track'][u'userName'], PatternScriptEntities.ENCODING)
    rsDict[u'Set to'] = unicode(rS[u'destination'][u'userName'], PatternScriptEntities.ENCODING) \
        + u';' + unicode(rS[u'destination'][u'track'][u'userName'], PatternScriptEntities.ENCODING)
    try:
        jFinalDestination = unicode(rS[u'finalDestination'][u'userName'], PatternScriptEntities.ENCODING)
        try:
            jFinalTrack = unicode(rS[u'finalDestination'][u'track'][u'userName'], PatternScriptEntities.ENCODING)
        except KeyError:
            jFinalTrack = u'Any'
        rsDict[u'FD&Track'] = jFinalDestination + ';' + jFinalTrack
    except:
        rsDict[u'FD&Track'] = unicode(rS[u'destination'][u'userName'], PatternScriptEntities.ENCODING) \
            + u';' + unicode(rS[u'destination'][u'track'][u'userName'], PatternScriptEntities.ENCODING)

    return rsDict

def getTpInventory():

    tpInventoryPath = jmri.util.FileUtil.getHomePath() + "AppData\Roaming\TrainPlayer\Reports\TrainPlayer Export - Inventory.txt"
    tpInventory = ''

    try: # Catch TrainPlayer not installed
        with codecsOpen(tpInventoryPath, 'r', encoding=PatternScriptEntities.ENCODING) as csvWorkFile:
            tpInventory = [line.rstrip() for line in csvWorkFile]
            # tpInventory = csvWorkFile.read()

    except IOError:
        psLog.warning('TrainPlayer directory or file not found')

    return tpInventory

def makeTpInventoryList(tpInventory):
    '''Returns (CarId,TrackLabel)'''

    tpInventoryList = []
    for item in tpInventory:
        splitItem = tuple(item.split(','))
        tpInventoryList.append(splitItem)

    return tpInventoryList



class ProcessInventory:

    def __init__(self):

        self.locationHash = {}
        self.errorReport = []

        return

    def makeJmriLocationList(self):
        '''Format: {TrackComment : (LocationName, TrackName)}'''

        allLocations = PatternScriptEntities.getAllLocations()
        locDict = {}

        for location in allLocations:
            locationObject = PatternScriptEntities.LM.getLocationByName(location)
            allTracks = locationObject.getTracksList()
            for track in allTracks:
                self.locationHash[track.getComment()] = (locationObject.getName(),track.getName())

        return

    def getSetToLocation(self, tpTrackLabel):
        '''Returns the location and track objects'''

        errorReport = ''
        try:
            locationTrack = self.locationHash[tpTrackLabel]
            self.location = PatternScriptEntities.LM.getLocationByName(locationTrack[0])
            self.track = self.location.getTrackByName(locationTrack[1], None)
        except KeyError:
            self.errorReport.append(tpTrackLabel)

        return self.location, self.track

    def getErrorReport(self):

        return self.errorReport

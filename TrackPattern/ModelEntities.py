# coding=utf-8
# Extended ìÄÅÉî
# Data munipulation support methods for the track pattern subroutine
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import time
import java.awt
# import java.awt.event
import javax.swing
from os import system
from codecs import open as cOpen
from xml.etree import ElementTree as ET
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities

scriptRev = 'TrackPattern.ModelEntities v20211210'

def occuranceTally(listOfOccurances):
    '''Tally the occurances of a word in a list and return a dictionary'''

    dict = {}
    while len(listOfOccurances):
        occurance = listOfOccurances[-1]
        tally = 0
        for i in xrange(len(listOfOccurances) - 1, -1, -1): # run list from bottom up
            if (listOfOccurances[i] == occurance):
                tally += 1
                listOfOccurances.pop(i)
        dict[occurance] = tally

    return dict

def formatText(item, length):
    '''Left justify string to a specified length'''

    pad = '<' + str(length)

    return format(item, pad)


def getAllLocations():
    '''returns a list of all locations for this profile. JMRI sorts the list'''

    allLocs = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager).getLocationsByNameList()
    locList = []
    for item in allLocs:
        locList.append(unicode(item.getName(), MainScriptEntities.setEncoding()))

    return locList

def makeInitialTrackList(location):

    trackDict = {}
    for track in jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager).getLocationByName(location).getTracksByNameList(None):
        trackDict[unicode(track, MainScriptEntities.setEncoding())] = False

    return trackDict

def getTracksByLocation(location, trackType):
    ''' Make a list of all the tracks for a given location and track type'''

    allTracksList = []
    for x in jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager).getLocationByName(location).getTracksByNameList(trackType): # returns object
        allTracksList.append(unicode(x.getName(), MainScriptEntities.setEncoding())) # list of all yard tracks for the validated location

    return allTracksList

def getCarObjects(yard, track):
    '''Make a list of car objects at the specified yard and track'''

    carYardPattern = []
    allCars = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager).getByIdList() # a list of objects
    for car in allCars:
        if (car.getLocationName() == yard and car.getTrackName() == track):
            carYardPattern.append(car)

    return carYardPattern # a list of objects

def getDetailsForCarAsDict(carObject):
    '''makes a dictionary of attributes for one car based on the requirements of
    jmri.jmrit.operations.setup.Setup.getCarAttributes()'''

    cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
    lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)

    carDetailDict = {}
    carDetailDict[u'Set to'] = '[  ] '
    carDetailDict[u'Road'] = carObject.getRoadName()
    carDetailDict[u'Number'] = carObject.getNumber()
    carDetailDict[u'Type'] = carObject.getTypeName()
    carDetailDict[u'Length'] = carObject.getLength()
    carDetailDict[u'Weight'] = carObject.getWeightTons()
    carDetailDict[u'Load'] = carObject.getLoadName()
    carDetailDict[u'Load Type'] = carObject.getLoadType()
    carDetailDict[u'Hazardous'] = carObject.isHazardous()
    carDetailDict[u'Color'] = carObject.getColor()
    carDetailDict[u'Kernel'] = carObject.getKernelName()
    allCarObjects = cm.getByIdList()
    for car in allCarObjects:
        i = 0
        if (car.getKernelName() == carObject.getKernelName()):
            i += 1
        carDetailDict[u'Kernel Size'] = str(i)
    carDetailDict[u'Owner'] = carObject.getOwner()
    carDetailDict[u'Track'] = carObject.getTrackName()
    carDetailDict[u'Location'] = carObject.getLocationName()
    if not (carObject.getDestinationName()):
        carDetailDict[u'Destination'] = '*No Destination'
        carDetailDict[u'Dest&Track'] = '*No Destination'
    else:
        carDetailDict[u'Destination'] = carObject.getDestinationName()
        carDetailDict[u'Dest&Track'] = carObject.getDestinationName() + ', ' + carObject.getDestinationTrackName()
    if not (carObject.getFinalDestinationName()):
        carDetailDict[u'Final Dest'] = '*No Final Destination'
        carDetailDict[u'FD&Track'] = '*No Final Destination'
    else:
        carDetailDict[u'Final Dest'] = carObject.getFinalDestinationName()
        carDetailDict[u'FD&Track'] = carObject.getFinalDestinationName() + ', ' + carObject.getFinalDestinationTrackName()
    carDetailDict[u'Comment'] = carObject.getComment()
    trackId = lm.getLocationByName(carObject.getLocationName()).getTrackById(carObject.getTrackId())
    carDetailDict[u'SetOut Msg'] = trackId.getCommentSetout()
    carDetailDict[u'PickUp Msg'] = trackId.getCommentPickup()
    carDetailDict[u'RWE'] = carObject.getReturnWhenEmptyDestinationName()

    return carDetailDict

def sortCarList(carList):
    '''Returns a sorted car list of the one submitted
    Available sort keys in PatternConfig RW
    Selected key list in sort order in PatternConfig SL
    Key list can be any length'''

    subList = MainScriptEntities.readConfigFile('TP')
    sortList = subList['SL']
    for sortKey in sortList: # the list of sort keys in order is UZ
        carList.sort(key=lambda row: row[sortKey])

    return carList

def makeSwitchlist(trackPattern, bool):
    '''Makes a text switchlist using an input pattern, conforming to config values,
    bool is set to True to include report Totals'''
# Read in the config file
    configFile = MainScriptEntities.readConfigFile('TP')
    itemsList = jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()
# Make the switchlist
    switchList  = trackPattern['RT'] + '\n' \
                + trackPattern['RN'] + '\n' \
                + u'Valid time: ' + trackPattern['VT'] + '\n' \
                + u'Location: ' + trackPattern['YL'] + '\n\n'
    reportTally = [] # running total for all tracks
    for j in trackPattern['ZZ']:
        switchList = switchList + u'Track: ' + j['TN'] + '\n'
        trackRoster = j['TR']
        carLength = 0
        trackTally = []
        for car in trackRoster:
            switchListRow = car['Set to']
            for item in itemsList:
                if (item != ' '): # skips over null items
                    reportWidth = configFile['RW']
                    itemWidth = reportWidth[item]
                    switchListRow = switchListRow + formatText(car[item], itemWidth)
            switchList = switchList + switchListRow + '\n'
            carLength = carLength + int(car['Length']) + 4
            trackTally.append(car['Final Dest'])
            reportTally.append(car['Final Dest'])
        switchList = switchList + u'Total Cars: ' \
                                + str(len(trackRoster)) \
                                + u' Track Length: ' \
                                + str(j['TL']) \
                                + u' Car Length: ' \
                                + str(carLength) \
                                + u' Available: ' \
                                + str(j['TL'] - carLength) + '\n'
        if (bool):
            switchList = switchList + u'Track Totals:\n'
            tallySummary = occuranceTally(trackTally)
            for track, count in sorted(tallySummary.items()):
                switchList = switchList + ' ' + track + ' - ' + str(count) + '\n'
            switchList = switchList + '\n'
    if (bool):
        switchList = switchList + u'\nReport Totals:\n'
        for track, count in sorted(occuranceTally(reportTally).items()):
            switchList = switchList + ' ' + track + ' - ' + str(count) + '\n'

    return switchList

def makeCsvSwitchlist(trackPattern):
    '''Makes a CSV switchlist using an input pattern, conforming to config values.
    Generate CSV Switch list is selected from the Trains window, Tools/Options pull down'''

    csvSwitchList = u'Operator,Description,Parameters\n' \
                    u'RT,Report Type,' + trackPattern['RT'] + '\n' \
                    u'RN,Railroad Name,' + trackPattern['RN'] + '\n' \
                    u'LN,Location Name,' + trackPattern['YL'] + '\n' \
                    u'PRNTR,Printer Name,\n' \
                    u'YPC,Yard Pattern Comment,Yard inventory by Track and Destination\n' \
                    u'VT,Valid,' + trackPattern['VT'] + '\n'
    for j in trackPattern['ZZ']:
        csvSwitchList = csvSwitchList + u'TN,Track name,' + unicode(j['TN'], MainScriptEntities.setEncoding()) + '\n'
        for car in j['TR']:
            csvSwitchList   = csvSwitchList + car['Set to'] + ',' \
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
                                            + car['RWE'] + '\n'

    return csvSwitchList

def printSwitchList(trackData):
    '''Sends the TXT switch list to notepad and optionally creates the CSV switch list'''

    for track in trackData['ZZ']:
        trackName = track['TN']
# Print the switch list
    textSwitchList = makeSwitchlist(trackData, False)
    textCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\Switch list (' + trackData['YL'] + ') (' + trackName + ').txt'
    with cOpen(textCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as textWorkFile:
        textWorkFile.write(textSwitchList)
    system(MainScriptEntities.systemInfo() + textCopyTo)
# Print the CSV switch list
    if (jmri.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled()):
        csvSwitchList = makeCsvSwitchlist(trackData)
        csvCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists\\Switch list (' + trackData['YL'] + ') (' + trackName + ').csv'
        with cOpen(csvCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as csvWorkFile:
            csvWorkFile.write(csvSwitchList)
    return

def getcustomLoadForCarType():
    '''Returns the default empty designation and a dictionary of car types by custom empty name'''

    cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManagerXml)
    opsFileName = jmri.util.FileUtil.getProfilePath() + 'operations\\' + cm.getOperationsFileName()
    with cOpen(opsFileName, 'r', encoding=MainScriptEntities.setEncoding()) as opsWorkFile:
        carXml = ET.parse(opsWorkFile)
        defaultLoadLoad = carXml.getroot()[5][0].attrib['load']
        customLoadForCarTypes = {}
        for loadElement in carXml.getroot()[5]:
            carType = loadElement.attrib
            for loadDetail in loadElement:
                if (loadDetail.attrib['loadType'] == 'Load'):
                    customLoadForCarTypes[carType['type']] = loadDetail.attrib['name']
    return defaultLoadLoad, customLoadForCarTypes

def getcustomEmptyForCarType():
    '''Returns the default load designation and a dictionary of car types by custom load name'''

    cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManagerXml)
    opsFileName = jmri.util.FileUtil.getProfilePath() + 'operations\\' + cm.getOperationsFileName()
    with cOpen(opsFileName, 'r', encoding=MainScriptEntities.setEncoding()) as opsWorkFile:
        carXml = ET.parse(opsWorkFile)
        defaultLoadEmpty = carXml.getroot()[5][0].attrib['empty']
        customEmptyForCarTypes = {}
        for loadElement in carXml.getroot()[5]:
            carType = loadElement.attrib
            for loadDetail in loadElement:
                if (loadDetail.attrib['loadType'] == 'Empty'):
                    customEmptyForCarTypes[carType['type']] = loadDetail.attrib['name']
    return defaultLoadEmpty, customEmptyForCarTypes

def getSelectedTracks():
    '''Makes a list of just the selected tracks'''

    trackPattern = MainScriptEntities.readConfigFile('TP')
    trackList = []
    for track, bool in sorted(trackPattern['PT'].items()):
        if (bool):
            trackList.append(track)

    return trackList

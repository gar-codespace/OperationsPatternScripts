# coding=utf-8
# © 2021 Greg Ritacco

import jmri
# import java.awt
# import javax.swing
import time
from codecs import open as codecsOpen
from json import loads as jsonLoads, dumps as jsonDumps
from xml.etree import ElementTree as ET

from psEntities import MainScriptEntities

scriptName = 'OperationsPatternScripts.TrackPattern.ModelEntities'
scriptRev = 20220101

def makeGenericHeader():
    '''A generic header info for any switch list, used to make the JSON file'''

    listHeader = {}
    listHeader['railroad'] = unicode(jmri.jmrit.operations.setup.Setup.getRailroadName(), MainScriptEntities.setEncoding())
    listHeader['trainName'] = u'Report Type Placeholder'
    listHeader['trainDescription'] = u'Report Description'
    listHeader['trainComment'] = u'Train Comment Placeholder'
    listHeader['date'] = unicode(MainScriptEntities.timeStamp(), MainScriptEntities.setEncoding())
    listHeader['locations'] = []

    return listHeader

def getGenericTrackDetails(locationName, trackName):
    '''The loco and car lists are sorted at this level'''

    genericTrackDetails = {}
    genericTrackDetails['trackName'] = trackName
    genericTrackDetails['length'] =  MainScriptEntities._lm.getLocationByName(locationName).getTrackByName(trackName, None).getLength()

    genericTrackDetails['locos'] = sortLocoList(getLocoListForTrack(trackName))

    genericTrackDetails['cars'] = sortCarList(getCarListForTrack(trackName))

    return genericTrackDetails

def formatText(item, length):
    '''Truncate each item to its defined length in PatternConfig.json and add a space at the end'''
    # This version works with utf-8

    if len(item) < length:
        xItem = item.ljust(length)
    else:
        xItem = item[:length]

    return xItem + u' '

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

def getTrackDetails(track):

    location = MainScriptEntities.readConfigFile('TP')['PL']
    trackDetails = {}
    trackDetails['Name'] = track
    trackDetails['Length'] =  MainScriptEntities._lm.getLocationByName(location).getTrackByName(track, None).getLength()

    return trackDetails

def getLocoListForTrack(track):
    '''Creates a generic locomotive list for a track, used to make the JSON file'''

    trackLocoList = []
    location = MainScriptEntities.readConfigFile('TP')['PL']
    locoList = getLocoObjects(location, track)
    for loco in locoList:
        trackLocoList.append(getDetailsForLocoAsDict(loco))

    return trackLocoList

def getLocoObjects(location, track):

    locoList = []
    allLocos = MainScriptEntities._em.getByModelList()
    for loco in allLocos:
        if (loco.getLocationName() == location and loco.getTrackName() == track):
            locoList.append(loco)

    return locoList

def getDetailsForLocoAsDict(locoObject):
    '''A dictionary of locomotive attributes, hard coded selection'''
    # @Todo move this to the json config file
    locoDetailDict = {}
    locoDetailDict[u'Set to'] = '[  ] '
    locoDetailDict[u'Road'] = locoObject.getRoadName()
    locoDetailDict[u'Number'] = locoObject.getNumber()
    locoDetailDict[u'Type'] = locoObject.getTypeName()
    locoDetailDict[u'Length'] = locoObject.getLength()
    locoDetailDict[u'Weight'] = locoObject.getWeightTons()
    locoDetailDict[u'Model'] = locoObject.getModel()
    locoDetailDict[u'PUSO'] = u'SL'
    locoDetailDict[u'Load'] = u'O'
    locoDetailDict[u'FD&Track'] = MainScriptEntities.readConfigFile('TP')['DS']
    locoDetailDict[u'Track'] = locoObject.getTrackName()

    return locoDetailDict

def getCarListForTrack(track):
    '''A dictionary of car attributes'''

    trackCarList = []
    location = MainScriptEntities.readConfigFile('TP')['PL']
    carList = getCarObjects(location, track)
    for car in carList:
        trackCarList.append(getDetailsForCarAsDict(car))

    return trackCarList

def getCarObjects(location, track):

    carList = []
    allCars = MainScriptEntities._cm.getByIdList()
    for car in allCars:
        if (car.getLocationName() == location and car.getTrackName() == track):
            carList.append(car)

    return carList

def getDetailsForCarAsDict(carObject):
    '''makes a dictionary of attributes for one car that includes all the fields possible from:
    jmri.jmrit.operations.setup.Setup.getCarAttributes()'''

    fdStandIn = MainScriptEntities.readConfigFile('TP')

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
    allCarObjects =  MainScriptEntities._cm.getByIdList()
    for car in allCarObjects:
        i = 0
        if (car.getKernelName() == carObject.getKernelName()):
            i += 1
        carDetailDict[u'Kernel Size'] = str(i)
    carDetailDict[u'Owner'] = carObject.getOwner()
    carDetailDict[u'Track'] = carObject.getTrackName()
    carDetailDict[u'Location'] = carObject.getLocationName()
    if not (carObject.getDestinationName()):
        carDetailDict[u'Destination'] = fdStandIn['DS']
        carDetailDict[u'Dest&Track'] = fdStandIn['DT']
    else:
        carDetailDict[u'Destination'] = carObject.getDestinationName()
        carDetailDict[u'Dest&Track'] = carObject.getDestinationName() + ', ' + carObject.getDestinationTrackName()
    if not (carObject.getFinalDestinationName()):
        carDetailDict[u'Final Dest'] = fdStandIn['FD']
        carDetailDict[u'FD&Track'] = fdStandIn['FT']
    else:
        carDetailDict[u'Final Dest'] = carObject.getFinalDestinationName()
        carDetailDict[u'FD&Track'] = carObject.getFinalDestinationName() + ', ' + carObject.getFinalDestinationTrackName()
    carDetailDict[u'Comment'] = carObject.getComment()
    trackId =  MainScriptEntities._lm.getLocationByName(carObject.getLocationName()).getTrackById(carObject.getTrackId())
    carDetailDict[u'SetOut Msg'] = trackId.getCommentSetout()
    carDetailDict[u'PickUp Msg'] = trackId.getCommentPickup()
    carDetailDict[u'RWE'] = carObject.getReturnWhenEmptyDestinationName()
    carDetailDict[u'PUSO'] = u'SC'
    carDetailDict[u' '] = u' ' # Catches empty box added to getLocalSwitchListMessageFormat KeyError

    return carDetailDict

def appendJsonBody(trainPlayerSwitchList):
    '''TrainPlayer method'''

    jsonCopyFrom = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\TrainPlayerSwitchlist.json'
    with codecsOpen(jsonCopyFrom, 'r', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
        switchList = jsonWorkFile.read()
    jsonSwitchList = jsonLoads(switchList)
    jTemp = jsonSwitchList['locations']
    jTemp.append(trainPlayerSwitchList)
    jsonSwitchList['locations'] = jTemp

    jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\TrainPlayerSwitchlist.json'
    jsonObject = jsonDumps(jsonSwitchList, indent=2, sort_keys=True)
    with codecsOpen(jsonCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
        jsonWorkFile.write(jsonObject)

    return

def getAllLocations():
    '''JMRI sorts the list'''

    allLocations = MainScriptEntities._lm.getLocationsByNameList()
    locationList = []
    for item in allLocations:
        locationList.append(unicode(item.getName(), MainScriptEntities.setEncoding()))

    return locationList

def makeInitialTrackList(location):

    trackDict = {}
    for track in MainScriptEntities._lm.getLocationByName(location).getTracksByNameList(None):
        trackDict[unicode(track, MainScriptEntities.setEncoding())] = False

    return trackDict

def getTracksByLocation(location, trackType):

    allTracksList = []
    for x in MainScriptEntities._lm.getLocationByName(location).getTracksByNameList(trackType): # returns object
        allTracksList.append(unicode(x.getName(), MainScriptEntities.setEncoding())) # list of all yard tracks for the validated location

    return allTracksList

# def getSelectedTracks():
#
#     trackList = []
#     patternTracks = MainScriptEntities.readConfigFile('TP')['PT']
#     for track, include in sorted(patternTracks.items()):
#         if (include):
#             trackList.append(track)
#
#     return trackList

def makeTextReportHeader(textWorkEventList):

    textReportHeader    = textWorkEventList['railroad'] + '\n' \
                        + textWorkEventList['trainName'] + '\n' \
                        + textWorkEventList['trainDescription'] + '\n' \
                        + u'Comment: ' + textWorkEventList['trainComment'] + '\n' \
                        + u'Valid time: ' + textWorkEventList['date'] + '\n\n'

    return textReportHeader

def makeTextReportLocations(textWorkEventList, trackTotals):

    itemsList = jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()
    reportWidth = MainScriptEntities.readConfigFile('TP')['RW']
    # includeTotals = MainScriptEntities.readConfigFile('TP')['IT']

    reportSwitchList = ''
    reportTally = [] # running total for all tracks
    for location in textWorkEventList['locations']:
        reportSwitchList += 'Location: ' + location['locationName'] + '\n'
        for track in location['tracks']:
            lengthOfLocos = 0
            lengthOfCars = 0
            trackTally = []
            trackName = track['trackName']
            trackLength = track['length']
            reportSwitchList += 'Track: ' + trackName + '\n'

            for loco in track['locos']:
                lengthOfLocos += int(loco['Length']) + 4
                reportSwitchList += loco['Set to'] + formatText(loco['Road'], reportWidth['Road']) + formatText(loco['Number'],  reportWidth['Number']) + formatText(loco['Model'], reportWidth['Model']) + formatText(loco['Type'], reportWidth['Loco Type']) + '\n'

            for car in track['cars']:
                lengthOfCars += int(car['Length']) + 4
                switchListRow = car['Set to']
                trackTally.append(car['Final Dest'])
                reportTally.append(car['Final Dest'])
                for item in itemsList:
                    itemWidth = reportWidth[item]
                    switchListRow += formatText(car[item], itemWidth)
                reportSwitchList += switchListRow + '\n'

            if trackTotals:
                totalLength = lengthOfLocos + lengthOfCars
                reportSwitchList += 'Total Cars: ' + str(len(track['cars'])) + ' Track Length: ' + str(trackLength) + ' Eqpt. Length: ' + str(totalLength) + ' Available: ' + str(trackLength - totalLength) + '\n\n'
                reportSwitchList += u'Track Totals:\n'
                for track, count in sorted(occuranceTally(trackTally).items()):
                    reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
            reportSwitchList += '\n'

        if trackTotals:
            reportSwitchList += u'\nReport Totals:\n'
            for track, count in sorted(occuranceTally(reportTally).items()):
                reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'

    return reportSwitchList

def makeReportSwitchList(switchList, includeTotals=False):

    itemsList = jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()
    reportWidth = MainScriptEntities.readConfigFile('TP')['RW']

    reportSwitchList = ''
    reportTally = [] # running total for all tracks
    for track in switchList['locations']:
        lengthOfLocos = 0
        lengthOfCars = 0
        trackTally = []
        trackName = track['Name']
        trackLength = track['Length']
        reportSwitchList += 'Track: ' + trackName + '\n'

        sortedListOfLocos = sortLocoList(track['Locos'])
        for loco in sortedListOfLocos:
            lengthOfLocos += int(loco['Length']) + 4
            reportSwitchList += loco['Set to'] + formatText(loco['Road'], reportWidth['Road']) + formatText(loco['Number'],  reportWidth['Number']) + formatText(loco['Model'], reportWidth['Model']) + formatText(loco['Type'], reportWidth['Loco Type']) + '\n'
            # Loco Type is not as JMRI type, it is added by me

        sortedListOfCars = sortCarList(track['Cars'])
        for car in sortedListOfCars:
            lengthOfCars += int(car['Length']) + 4
            switchListRow = car['Set to']
            trackTally.append(car['Final Dest'])
            reportTally.append(car['Final Dest'])
            for item in itemsList:
                itemWidth = reportWidth[item]
                switchListRow += formatText(car[item], itemWidth)
            reportSwitchList += switchListRow + '\n'

        if (includeTotals):
            totalLength = lengthOfLocos + lengthOfCars
            reportSwitchList += 'Total Cars: ' + str(len(track['Cars'])) + ' Track Length: ' + str(trackLength) + ' Eqpt. Length: ' + str(totalLength) + ' Available: ' + str(trackLength - totalLength) + '\n\n'
            reportSwitchList += u'Track Totals:\n'
            for track, count in sorted(occuranceTally(trackTally).items()):
                reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
        reportSwitchList += '\n'

    if (includeTotals):
        reportSwitchList += u'\nReport Totals:\n'
        for track, count in sorted(occuranceTally(reportTally).items()):
            reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'

    return reportSwitchList

def sortLocoList(locoList):

    sortLocos = MainScriptEntities.readConfigFile('TP')['SL']
    for sortKey in sortLocos:
        locoList.sort(key=lambda row: row[sortKey])

    return locoList

def sortCarList(carList):

    sortCars = MainScriptEntities.readConfigFile('TP')['SC']
    for sortKey in sortCars:
        carList.sort(key=lambda row: row[sortKey])

    return carList

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

def getCustomLoadForCarType():
    '''Returns the default load designation and a dictionary of custon loads by car type'''

    opsFileName = jmri.util.FileUtil.getProfilePath() + 'operations\\' + MainScriptEntities._cmx.getOperationsFileName()
    with codecsOpen(opsFileName, 'r', encoding=MainScriptEntities.setEncoding()) as opsWorkFile:
        carXml = ET.parse(opsWorkFile)
        defaultLoadLoad = carXml.getroot()[5][0].attrib['load']
        customLoadForCarTypes = {}
        for loadElement in carXml.getroot()[5]:
            carType = loadElement.attrib
            for loadDetail in loadElement:
                if (loadDetail.attrib['loadType'] == 'Load'):
                    customLoadForCarTypes[carType['type']] = loadDetail.attrib['name']
    return defaultLoadLoad, customLoadForCarTypes

def getCustomEmptyForCarType():
    '''Returns the default empty designation and a dictionary of custon empties by car type'''

    opsFileName = jmri.util.FileUtil.getProfilePath() + 'operations\\' + MainScriptEntities._cmx.getOperationsFileName()
    with codecsOpen(opsFileName, 'r', encoding=MainScriptEntities.setEncoding()) as opsWorkFile:
        carXml = ET.parse(opsWorkFile)
        defaultLoadEmpty = carXml.getroot()[5][0].attrib['empty']
        customEmptyForCarTypes = {}
        for loadElement in carXml.getroot()[5]:
            carType = loadElement.attrib
            for loadDetail in loadElement:
                if (loadDetail.attrib['loadType'] == 'Empty'):
                    customEmptyForCarTypes[carType['type']] = loadDetail.attrib['name']
    return defaultLoadEmpty, customEmptyForCarTypes

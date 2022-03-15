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
    '''The loco and car lists are sorted at this level, used to make the JSON file'''

    genericTrackDetails = {}
    genericTrackDetails['trackName'] = trackName
    genericTrackDetails['length'] =  MainScriptEntities._lm.getLocationByName(locationName).getTrackByName(trackName, None).getLength()
    genericTrackDetails['locos'] = sortLocoList(getLocoListForTrack(trackName))
    genericTrackDetails['cars'] = sortCarList(getCarListForTrack(trackName))

    return genericTrackDetails

def sortLocoList(locoList):
    '''Sort order of MainScriptEntities.readConfigFile('TP')['SL'] is top down'''

    sortLocos = MainScriptEntities.readConfigFile('TP')['SL']
    for sortKey in sortLocos:
        locoList.sort(key=lambda row: row[sortKey])

    return locoList

def getLocoListForTrack(track):
    '''Creates a generic locomotive list for a track, used to make the JSON file'''

    location = MainScriptEntities.readConfigFile('TP')['PL']
    locoList = getLocoObjects(location, track)

    return [getDetailsForLocoAsDict(loco) for loco in locoList]

def getLocoObjects(location, track):

    locoList = []
    allLocos = MainScriptEntities._em.getByModelList()

    return [loco for loco in allLocos if loco.getLocationName() == location and loco.getTrackName() == track]

def getDetailsForLocoAsDict(locoObject):
    '''Mimics jmri.jmrit.operations.setup.Setup.getEngineAttributes()
    [u'Road', u'Number', u'Type', u'Model', u'Length', u'Weight', u'Consist', u'Owner', u'Track', u'Location', u'Destination', u'Comment']'''

    locoDetailDict = {}

    locoDetailDict[u'Road'] = locoObject.getRoadName()
    locoDetailDict[u'Number'] = locoObject.getNumber()
    locoDetailDict[u'Type'] = locoObject.getTypeName()
    locoDetailDict[u'Model'] = locoObject.getModel()
    locoDetailDict[u'Length'] = locoObject.getLength()
    locoDetailDict[u'Weight'] = locoObject.getWeightTons()
    try:
        locoDetailDict[u'Consist'] = locoObject.getConsist().getName()
    except:
        locoDetailDict[u'Consist'] = 'Single'
    locoDetailDict[u'Owner'] = str(locoObject.getOwner())
    locoDetailDict[u'Track'] = locoObject.getTrackName()
    locoDetailDict[u'Location'] = locoObject.getLocation().getName()
    locoDetailDict[u'Destination'] = locoObject.getDestinationName()
    locoDetailDict[u'Comment'] = locoObject.getComment()
# Not part of JMRI engine attributes
    locoDetailDict[u'Set to'] = '[  ] '
    locoDetailDict[u'PUSO'] = u'SL'
    locoDetailDict[u'Load'] = u'O'
    locoDetailDict[u'FD&Track'] = MainScriptEntities.readConfigFile('TP')['DS']
    locoDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getDropEngineMessageFormat

    return locoDetailDict

def sortCarList(carList):
    '''Sort order of MainScriptEntities.readConfigFile('TP')['SC'] is top down'''

    sortCars = MainScriptEntities.readConfigFile('TP')['SC']
    for sortKey in sortCars:
        carList.sort(key=lambda row: row[sortKey])

    return carList

def getCarListForTrack(track):
    '''A list of car attributes as a dictionary'''

    location = MainScriptEntities.readConfigFile('TP')['PL']
    carList = getCarObjects(location, track)

    return [getDetailsForCarAsDict(car) for car in carList]

def getCarObjects(location, track):

    allCars = MainScriptEntities._cm.getByIdList()

    return [car for car in allCars if car.getLocationName() == location and car.getTrackName() == track]

def getDetailsForCarAsDict(carObject):
    '''Mimics jmri.jmrit.operations.setup.Setup.getCarAttributes()
    [u'Road', u'Number', u'Type', u'Length', u'Weight', u'Load', u'Load Type', u'Hazardous', u'Color', u'Kernel', u'Kernel Size', u'Owner', u'Track', u'Location', u'Destination', u'Dest&Track', u'Final Dest', u'FD&Track', u'Comment', u'SetOut Msg', u'PickUp Msg', u'RWE']'''

    fdStandIn = MainScriptEntities.readConfigFile('TP')

    carDetailDict = {}

    carDetailDict[u'Road'] = carObject.getRoadName()
    carDetailDict[u'Number'] = carObject.getNumber()
    carDetailDict[u'Type'] = carObject.getTypeName()
    carDetailDict[u'Length'] = carObject.getLength()
    carDetailDict[u'Weight'] = carObject.getWeightTons()
    if carObject.isCaboose() or carObject.isPassenger():
        carDetailDict[u'Load'] = u'O'
    else:
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
# Not part of JMRI car attributes
    carDetailDict[u'Set to'] = '[  ] '
    carDetailDict[u'PUSO'] = u'SC'
    carDetailDict[u' '] = u' ' # Catches KeyError - empty box added to getLocalSwitchListMessageFormat

    return carDetailDict

def appendJsonBody(trainPlayerSwitchList):

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
    for x in MainScriptEntities._lm.getLocationByName(location).getTracksByNameList(trackType):
        allTracksList.append(unicode(x.getName(), MainScriptEntities.setEncoding())) # list of all yard tracks for the validated location

    return allTracksList

def makeTextReportHeader(textWorkEventList):

    textReportHeader    = textWorkEventList['railroad'] + '\n' \
                        + textWorkEventList['trainName'] + '\n' \
                        + textWorkEventList['trainDescription'] + '\n' \
                        + u'Comment: ' + textWorkEventList['trainComment'] + '\n' \
                        + u'Valid time: ' + textWorkEventList['date'] + '\n\n'

    return textReportHeader

def makeTextReportLocations(textWorkEventList, trackTotals):

    reportWidth = MainScriptEntities.readConfigFile('TP')['RW']
    locoItems = jmri.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    carItems = jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

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
                switchListRow = loco['Set to']
                for item in locoItems:
                    itemWidth = reportWidth[item]
                    switchListRow += formatText(loco[item], itemWidth)
                reportSwitchList += switchListRow + '\n'

            for car in track['cars']:
                lengthOfCars += int(car['Length']) + 4
                switchListRow = car['Set to']
                for item in carItems:
                    itemWidth = reportWidth[item]
                    switchListRow += formatText(car[item], itemWidth)
                reportSwitchList += switchListRow + '\n'
                trackTally.append(car['Final Dest'])
                reportTally.append(car['Final Dest'])

            if trackTotals:
                totalLength = lengthOfLocos + lengthOfCars
                reportSwitchList += 'Total Cars: ' + str(len(track['cars'])) + ' Track Length: ' + str(trackLength) + ' Eqpt. Length: ' + str(totalLength) + ' Available: ' + str(trackLength - totalLength) + '\n\n'
                reportSwitchList += u'Track Totals for Cars:\n'
                for track, count in sorted(occuranceTally(trackTally).items()):
                    reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
            reportSwitchList += '\n'

        if trackTotals:
            reportSwitchList += u'\nReport Totals for Cars:\n'
            for track, count in sorted(occuranceTally(reportTally).items()):
                reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'

    return reportSwitchList

def makeCsvSwitchlist(trackPattern):
    # CSV writer does not support utf-8

    csvSwitchList = u'Operator,Description,Parameters\n' \
                    u'RT,Report Type,' + trackPattern['trainDescription'] + '\n' \
                    u'RN,Railroad Name,' + trackPattern['railroad'] + '\n' \
                    u'LN,Location Name,' + trackPattern['locations'][0]['locationName'] + '\n' \
                    u'PRNTR,Printer Name,\n' \
                    u'YPC,Yard Pattern Comment,' + trackPattern['trainComment'] + '\n' \
                    u'VT,Valid,' + trackPattern['date'] + '\n'
    for track in trackPattern['locations'][0]['tracks']: # There is only one location
        csvSwitchList += u'TN,Track name,' + unicode(track['trackName'], MainScriptEntities.setEncoding()) + '\n'
        for loco in track['locos']:
            csvSwitchList +=  loco['Set to'] + ',' \
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
                            + loco['Load'] + ',' \
                            + loco['FD&Track'] + ',' \
                            + '\n'
        for car in track['cars']:
            csvSwitchList +=  car['Set to'] + ',' \
                            + car['PUSO'] + ',' \
                            + car['Road'] + ',' \
                            + car['Number'] + ',' \
                            + car['Type'] + ',' \
                            + car['Length'] + ',' \
                            + car['Weight'] + ',' \
                            + car['Load'] + ',' \
                            + car['Track'] + ',' \
                            + car['FD&Track'] + ',' \
                            + car['Load Type'] + ',' \
                            + str(car['Hazardous']) + ',' \
                            + car['Color'] + ',' \
                            + car['Kernel'] + ',' \
                            + car['Kernel Size'] + ',' \
                            + car['Owner'] + ',' \
                            + car['Location'] + ',' \
                            + car['Destination'] + ',' \
                            + car['Dest&Track'] + ',' \
                            + car['Final Dest'] + ',' \
                            + car['Comment'] + ',' \
                            + car['SetOut Msg'] + ',' \
                            + car['PickUp Msg'] + ',' \
                            + car['RWE'] \
                            + '\n'

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

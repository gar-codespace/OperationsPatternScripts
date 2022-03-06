# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import logging
from os import path as osPath
from os import system as osSystem
from json import loads as jsonLoads, dumps as jsonDumps
from codecs import open as codecsOpen

from psEntities import MainScriptEntities
from TrackPattern import ModelEntities
from TrackPattern import ControllerSetCarsForm

'''Data munipulation for the track pattern subroutine'''

scriptName = 'OperationsPatternScripts.TrackPattern.Model'
scriptRev = 20220101
psLog = logging.getLogger('PS.TP.Model')

def makeLocationDict():
    ''' '''

    psLog.debug('makeLocationDict')

    detailsForTrack = []
    patternLocation = MainScriptEntities.readConfigFile('TP')['PL']
    trackList = getSelectedTracks()
    for trackName in trackList:
        detailsForTrack.append(ModelEntities.getGenericTrackDetails(patternLocation, trackName))

    locationDict = {}
    locationDict['locationName'] = patternLocation
    locationDict['tracks'] = detailsForTrack

    return locationDict




def modifyReport(locationDict, reportType):

    psLog.debug('modifyReport')

    headerNames = MainScriptEntities.readConfigFile('TP')
    modifiedReport = makePatternHeader()
    modifiedReport['trainDescription'] = headerNames['TD'][reportType]
    modifiedReport['trainName'] = headerNames['TN'][reportType]
    modifiedReport['trainComment'] = headerNames['TC'][reportType]
    modifiedReport['locations'] = [locationDict] # put in as a dictionary to maintain compatability with JSON File Format/JMRI manifest export. See help web page

    return modifiedReport

def printWorkEventList(patternListForJson, trackTotals):

    psLog.debug('printWorkEventList')

    workEventName = writeWorkEventListAsJson(patternListForJson)
    textWorkEventList = readJsonWorkEventList(workEventName)
    textListForPrint = makeTextListForPrint(textWorkEventList, trackTotals)
    writeTextSwitchList(workEventName, textListForPrint)

    switchListFile = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\' + workEventName + '.txt'
    osSystem(MainScriptEntities.openEditorByComputerType(switchListFile))

    return

def getSelectedTracks():

    trackList = []
    patternTracks = MainScriptEntities.readConfigFile('TP')['PT']
    for track, include in sorted(patternTracks.items()):
        if (include):
            trackList.append(track)

    return trackList

# def makePatternLocations():
#     '''Simplified since there is only one location for the pattern buton'''
#
#     psLog.debug('makePatternLocations')
#
#     tracks = []
#     locationName = MainScriptEntities.readConfigFile('TP')['PL']
#     trackList = ModelEntities.getSelectedTracks()
#     for trackName in trackList:
#         tracks.append(ModelEntities.getGenericTrackDetails(locationName, trackName))
#
#     locationDict = {}
#     locationDict['locationName'] = locationName
#     locationDict['tracks'] = tracks
#
#     locations = [locationDict]
#
#     return locations # locations is a list of dictionaries

def onScButtonPress():
    '''"Set Cars" button opens a window for each selected track'''

    psLog.debug('onScButtonPress')

    locationName = MainScriptEntities.readConfigFile('TP')['PL']
    selectedTracks = getSelectedTracks()
    windowOffset = 200
    if selectedTracks:
        i = 0
        for trackName in selectedTracks:
            setCarsForm = ModelEntities.makeGenericHeader()
            locationDict = {}
            locationDict['locationName'] = locationName
            locationDict['tracks'] = [ModelEntities.getGenericTrackDetails(locationName, trackName)]
            setCarsForm['locations'] = [locationDict]
            # The above two lines are sent in as lists to maintain consistancy with the generic JSON file format
            newFrame = ControllerSetCarsForm.CreatePatternReportGui(setCarsForm)
            newWindow = newFrame.makeFrame()
            newWindow.setTitle(u'Pattern Report for track ' + trackName)
            newWindow.setLocation(windowOffset, 180)
            newWindow.pack()
            newWindow.setVisible(True)

            psLog.info(u'Set Cars Window created for track ' + trackName)
            windowOffset += 50
            i += 1
        psLog.info(str(i) + ' Set Cars windows for ' + locationName + ' created')
    else:
        psLog.warning('No tracks were selected for the Set Cars button')

    return

def makePatternHeader():

    psLog.debug('makePatternHeader')

    return ModelEntities.makeGenericHeader()

def makeSwitchList(fileName=u'test'): ##

    psLog.debug('makeSwitchList')
    switchList = TrackPattern.Model.makeSwitchListHeader()
    switchList['description'] = fileName

    trackList = getSelectedTracks()
    if not trackList:
        return

    tracks = []
    locoRoster = []
    carRoster = []
    for track in trackList:
        trackDetails = ModelEntities.getTrackDetails(track)

        locoList = ModelEntities.getLocoListForTrack(track)
        trackDetails['Locos'] = ModelEntities.sortLocoList(locoList)

        carList = ModelEntities.getCarListForTrack(track)
        trackDetails['Cars'] = ModelEntities.sortCarList(carList)
        tracks.append(trackDetails)

    switchList['locations'] = tracks

    return switchList

def writeWorkEventListAsJson(switchList):
    '''The generic switch list is written as a JSON'''

    psLog.debug('writeWorkEventListAsJson')

    switchListName = switchList['trainDescription']
    jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + switchListName + '.json'
    jsonObject = jsonDumps(switchList, indent=2, sort_keys=True)
    with codecsOpen(jsonCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
        jsonWorkFile.write(jsonObject)

    return switchListName

def readJsonWorkEventList(workEventName):

    psLog.debug('readJsonWorkEventList')

    jsonCopyFrom = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + workEventName + '.json'
    with codecsOpen(jsonCopyFrom, 'r', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
        jsonEventList = jsonWorkFile.read()
    textWorkEventList = jsonLoads(jsonEventList)

    return textWorkEventList

def makeTextListForPrint(textWorkEventList, trackTotals=False):

    psLog.debug('makeTextListForPrint')

    reportHeader = ModelEntities.makeTextReportHeader(textWorkEventList)
    reportLocations = ModelEntities.makeTextReportLocations(textWorkEventList, trackTotals)

    return reportHeader + reportLocations

def makeSwitchListHeader():
    '''The header info for any switch list, used to make the JSON file'''

    switchListHeader = {}
    switchListHeader['railroad'] = unicode(jmri.jmrit.operations.setup.Setup.getRailroadName(), MainScriptEntities.setEncoding())
    switchListHeader['userName'] = u'Report Type Placeholder'
    switchListHeader['description'] = u'Report Description'
    switchListHeader['location'] = MainScriptEntities.readConfigFile('TP')['PL']
    switchListHeader['date'] = unicode(MainScriptEntities.timeStamp(), MainScriptEntities.setEncoding())
    # switchListHeader['tracks'] = []

    return switchListHeader

def makeTextSwitchListHeader(switchListName):
    '''The JSON switch list is read in and processed'''

    jsonCopyFrom = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + switchListName + '.json'
    with codecsOpen(jsonCopyFrom, 'r', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
        jsonSwitchList = jsonWorkFile.read()
    switchList = jsonLoads(jsonSwitchList)

    reportHeader = ModelEntities.makeReportHeader(switchList)

    return reportHeader

def makeTextSwitchListBody(switchListName, includeTotals=False):
    '''The JSON switch list is read in and processed'''

    jsonCopyFrom = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\' + switchListName + '.json'
    with codecsOpen(jsonCopyFrom, 'r', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
        jsonSwitchList = jsonWorkFile.read()
    switchList = jsonLoads(jsonSwitchList)

    reportSwitchList = ModelEntities.makeReportSwitchList(switchList, includeTotals)

    return reportSwitchList

def writeTextSwitchList(fileName, textSwitchList):

    psLog.debug('writeTextSwitchList')

    textCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\' + fileName + '.txt'
    with codecsOpen(textCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as textWorkFile:
        textWorkFile.write(textSwitchList)

    return

def resetTrainPlayerSwitchlist():
    '''Overwrites the existing file with the header info for the next switch list'''

    psLog.debug('resetTrainPlayerSwitchlist')

    genericHeader = ModelEntities.makeGenericHeader()

    headerNames = MainScriptEntities.readConfigFile('TP')
    genericHeader['trainDescription'] = headerNames['TD']['TP']
    genericHeader['trainName'] = headerNames['TN']['TP']
    genericHeader['trainComment'] = headerNames['TC']['TP']

    genericHeader['locations'] = [{'locationName':'Location Name', 'tracks':[{'trackName':'Track Name', 'length': 1, 'locos':[], 'cars':[]}]}]

    writeWorkEventListAsJson(genericHeader)

    return

def updateLocations():
    '''Updates the config file with a list of all locations for this profile'''

    psLog.debug('updateLocations')
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    allLocations  = ModelEntities.getAllLocations()
    if not (subConfigfile['AL']): # when this sub is used for the first tims
        subConfigfile.update({'PL': allLocations[0]})
        subConfigfile.update({'PT': ModelEntities.makeInitialTrackList(allLocations[0])})
    subConfigfile.update({'AL': allLocations})
    newConfigFile.update({'TP': subConfigfile})
    MainScriptEntities.writeConfigFile(newConfigFile)

    return newConfigFile

def initializeConfigFile():
    '''initialize or reinitialize the track pattern part of the config file on first use, reset, or edit of a location name'''

    psLog.debug('initializeConfigFile')
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    allLocations  = ModelEntities.getAllLocations()
    subConfigfile.update({'AL': allLocations})
    subConfigfile.update({'PL': allLocations[0]})
    subConfigfile.update({'PT': ModelEntities.makeInitialTrackList(allLocations[0])})
    newConfigFile.update({'TP': subConfigfile})

    return newConfigFile

def updatePatternLocation(selectedItem):
    '''Catches user edits of locations, sets yard track only to false'''

    psLog.debug('updatePatternLocation')

    newConfigFile = MainScriptEntities.readConfigFile()

    allLocations = ModelEntities.getAllLocations()
    if not (selectedItem in allLocations):
        newConfigFile = initializeConfigFile()
        psLog.warning('Location list changed, config file updated')
        return newConfigFile

    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PA': False})
    subConfigfile.update({'PL': selectedItem})
    newConfigFile.update({'TP': subConfigfile})
    psLog.debug('The current location for this profile has been set to ' + selectedItem)

    return newConfigFile

def updateTrackCheckBoxes(trackCheckBoxes):
    '''Returns a dictionary of track names and their check box status'''

    psLog.debug('updateTrackCheckBoxes')
    dict = {}
    for item in trackCheckBoxes:
        dict[unicode(item.text, MainScriptEntities.setEncoding())] = item.selected

    return dict

def updatePatternTracks(trackList):
    '''Updates list of yard tracks as the yard track only flag is toggled'''

    psLog.debug('updatePatternTracks')
    trackDict = {}
    for track in trackList:
        trackDict[track] = False
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PT': trackDict})
    newConfigFile.update({'TP': subConfigfile})
    if (trackDict):
        psLog.warning('The track list for this location has changed')
    else:
        psLog.warning('There are no yard tracks for this location')

    return newConfigFile

def makePatternLog():
    '''creates a pattern log for display based on the log level, as set by the getBuildReportLevel'''

    outputPatternLog = ''
    buildReportLevel = int(jmri.jmrit.operations.setup.Setup.getBuildReportLevel())
    configLoggingIndex = MainScriptEntities.readConfigFile('LI')
    logLevel = configLoggingIndex[jmri.jmrit.operations.setup.Setup.getBuildReportLevel()]
    logFileLocation = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog.txt'
    with codecsOpen(logFileLocation, 'r', encoding=MainScriptEntities.setEncoding()) as patternLogFile:
        while True:
            thisLine = patternLogFile.readline()
            if not (thisLine):
                break
            if (configLoggingIndex['9'] in thisLine and buildReportLevel > 0): # critical
                outputPatternLog = outputPatternLog + thisLine
            if (configLoggingIndex['7'] in thisLine and buildReportLevel > 0): # error
                outputPatternLog = outputPatternLog + thisLine
            if (configLoggingIndex['5'] in thisLine and buildReportLevel > 0): # warning
                outputPatternLog = outputPatternLog + thisLine
            if (configLoggingIndex['3'] in thisLine and buildReportLevel > 2): # info
                outputPatternLog = outputPatternLog + thisLine
            if (configLoggingIndex['1'] in thisLine and buildReportLevel > 4): # debug
                outputPatternLog = outputPatternLog + thisLine

    tempLogFileLocation = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog_temp.txt'
    with codecsOpen(tempLogFileLocation, 'w', encoding=MainScriptEntities.setEncoding()) as tempPatternLogFile:
        tempPatternLogFile.write(outputPatternLog)
    return

def makeNewPatternTracks(location):
    '''Makes a new list of all tracks for a location'''

    psLog.debug('makeNewPatternTracks')
    allTracks = ModelEntities.getTracksByLocation(location, None)
    trackDict = {}
    for track in allTracks:
        trackDict[track] = False
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PT': trackDict})
    newConfigFile.update({'TP': subConfigfile})

    return newConfigFile

def updateCheckBoxStatus(all, ignore):
    '''Updates the config file with the checked status of Yard Tracks Only and Ignore Track Length check boxes'''

    psLog.debug('updateCheckBoxStatus')
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PA': all})
    subConfigfile.update({'PI': ignore})
    newConfigFile.update({'TP': subConfigfile})

    return newConfigFile

def updateConfigFile(controls):
    '''Updates the track pattern part of the config file'''

    psLog.debug('updateConfigFile')
    focusOn = MainScriptEntities.readConfigFile('TP')
    focusOn.update({"PL": controls[0].getSelectedItem()})
    focusOn.update({"PA": controls[1].selected})
    focusOn.update({"PI": controls[2].selected})
    focusOn.update({"PT": updateTrackCheckBoxes(controls[3])})
    newConfigFile = MainScriptEntities.readConfigFile('all')
    newConfigFile.update({"TP": focusOn})
    MainScriptEntities.writeConfigFile(newConfigFile)

    return controls

def makeLoadEmptyDesignationsDicts():
    '''Stores the custom car load for Load and Empty by type designations and the default load and empty designation as global variables'''

    psLog.debug('makeLoadEmptyDesignationsDicts')
    defaultLoadEmpty, customEmptyForCarTypes = ModelEntities.getCustomEmptyForCarType()
    defaultLoadLoad, customLoadForCarTypes = ModelEntities.getCustomLoadForCarType()
    # Set the default L/E
    try:
        _defaultLoadEmpty = defaultLoadEmpty
        _defaultLoadLoad = defaultLoadLoad
        psLog.info('Default load and empty designations saved')
    except:
        psLog.critical('Default empty designation not saved')
        _defaultLoadEmpty = 'E'
        _defaultLoadLoad = 'L'
    # Set custom L/E
    try:
        _carTypeByEmptyDict = customEmptyForCarTypes
        _carTypeByLoadDict = customLoadForCarTypes
        psLog.info('Default custon loads for (empty) and (load) by car type designations saved')
    except:
        psLog.critical('Custom car empty designations not saved')
        _carTypeByEmptyDict = {}
        _carTypeByLoadDict = {}

    return

def makeTrackList(location, type):
    '''Returns a list of tracks by type for a location'''
    psLog.debug('makeTrackList')

    return ModelEntities.getTracksByLocation(location, type)

# def writePatternJson(location, trackPatternDict):
#     '''Write the track pattern dictionary as a JSON file'''
#
#     psLog.debug('writePatternJson')
#     jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\Track Pattern (' + location + ').json'
#     jsonObject = jsonDumps(trackPatternDict, indent=2, sort_keys=True) #trackPatternDict
#     with codecsOpen(jsonCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
#         jsonWorkFile.write(jsonObject)
#
#     return

def writeCsvSwitchList(location, trackPatternDict):
    '''Rewrite this to write from the JSON file'''

    psLog.debug('writeCsvSwitchList')
    csvSwitchlistPath = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists'
    if not (osPath.isdir(csvSwitchlistPath)):
        mkdir(csvSwitchlistPath)
    csvCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists\\Track Pattern (' + location + ').csv'
    csvObject = ModelEntities.makeCsvSwitchlist(trackPatternDict)
    with codecsOpen(csvCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as csvWorkFile:
        csvWorkFile.write(csvObject)

    return

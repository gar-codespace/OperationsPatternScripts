# coding=utf-8
# © 2021, 2022 Greg Ritacco

import jmri

import logging
from os import path as osPath
from os import system as osSystem
from json import loads as jsonLoads, dumps as jsonDumps
from codecs import open as codecsOpen

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ModelEntities
from PatternTracksSubroutine import ControllerSetCarsForm

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.Model'
SCRIPT_REV = 20220101
psLog = logging.getLogger('PS.PT.Model')

def updatePatternLocation(selectedItem=None):
    '''Catches user edits of locations'''

    psLog.debug('updatePatternLocation')

    configFile = PatternScriptEntities.readConfigFile()
    newLocation = ModelEntities.testSelectedItem(selectedItem)
    newLocationList = ModelEntities.getAllLocations()
    newLocationTrackDict = ModelEntities.getAllTracksForLocation(newLocation)
    configFile['PT'].update({'PA': False})
    configFile['PT'].update({'PI': False})
    configFile['PT'].update({'PL': newLocation})
    configFile['PT'].update({'AL': newLocationList})
    configFile['PT'].update({'PT': newLocationTrackDict})
    PatternScriptEntities.writeConfigFile(configFile)

    psLog.info('The track list for location ' + newLocation + ' has been created')

    return newLocation

def makeNewPatternTracks(location):
    '''Makes a new list of all tracks for a location'''

    psLog.debug('makeNewPatternTracks')
    allTracks = ModelEntities.getTracksByLocation(None)
    trackDict = {}
    for track in allTracks:
        trackDict[track] = False
    newConfigFile = PatternScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['PT']
    subConfigfile.update({'PT': trackDict})
    newConfigFile.update({'PT': subConfigfile})

    return newConfigFile

def makeTrackList(location, type):
    '''Returns a list of tracks by type for a location'''
    psLog.debug('makeTrackList')

    return ModelEntities.getTracksByLocation(type)

def updatePatternTracks(trackList):
    '''Creates a new list of tracks and their default include flag'''

    psLog.debug('updatePatternTracks')
    trackDict = {}
    for track in trackList:
        trackDict[track] = False

    if (trackDict):
        psLog.warning('The track list for this location has changed')
    else:
        psLog.warning('There are no yard tracks for this location')

    return trackDict

def updateCheckBoxStatus(all, ignore):
    '''Updates the config file with the checked status of Yard Tracks Only and Ignore Track Length check boxes'''

    psLog.debug('updateCheckBoxStatus')
    newConfigFile = PatternScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['PT']
    subConfigfile.update({'PA': all})
    subConfigfile.update({'PI': ignore})
    newConfigFile.update({'PT': subConfigfile})

    return newConfigFile

def updateConfigFile(controls):
    '''Updates the pattern tracks part of the config file'''

    psLog.debug('updateConfigFile')

    focusOn = PatternScriptEntities.readConfigFile('PT')
    focusOn.update({"PL": controls[0].getSelectedItem()})
    focusOn.update({"PA": controls[1].selected})
    focusOn.update({"PI": controls[2].selected})
    focusOn.update({"PT": ModelEntities.updateTrackCheckBoxes(controls[3])})
    newConfigFile = PatternScriptEntities.readConfigFile()
    newConfigFile.update({"PT": focusOn})
    PatternScriptEntities.writeConfigFile(newConfigFile)
    psLog.info('Controls settings for configuration file updated')

    return controls

def getSelectedTracks():

    patternTracks = PatternScriptEntities.readConfigFile('PT')['PT']

    return [track for track, include in sorted(patternTracks.items()) if include]

def verifySelectedTracks():
    '''Catches on the fly user edit of JMRI track names'''

    validStatus = True
    allTracksList = ModelEntities.getTracksByLocation(None)
    if not allTracksList:
        psLog.warning('PatternConfig.JSON corrupted, new file written.')
        return False
    patternTracks = PatternScriptEntities.readConfigFile('PT')['PT']
    for track in patternTracks:
        if not track in allTracksList:
            validStatus = False

    return validStatus

def makeLocationDict(trackList=None):
    '''Returns the details for the tracks sent in formatted for the JSON file '''

    psLog.debug('makeLocationDict')

    if not trackList:
        trackList = getSelectedTracks()

    detailsForTrack = []
    patternLocation = PatternScriptEntities.readConfigFile('PT')['PL']
    for trackName in trackList:
        detailsForTrack.append(ModelEntities.getGenericTrackDetails(patternLocation, trackName))

    locationDict = {}
    locationDict['locationName'] = patternLocation
    locationDict['tracks'] = detailsForTrack

    return locationDict

def makeReport(locationDict, reportType):

    psLog.debug('makeReport')

    headerNames = PatternScriptEntities.readConfigFile('PT')
    modifiedReport = ModelEntities.makeGenericHeader()
    modifiedReport['trainDescription'] = headerNames['TD'][reportType]
    modifiedReport['trainName'] = headerNames['TN'][reportType]
    modifiedReport['trainComment'] = headerNames['TC'][reportType]
    modifiedReport['locations'] = [locationDict] # put in as a list to maintain compatability with JSON File Format/JMRI manifest export. See help web page

    return modifiedReport

def printWorkEventList(patternListForJson, trackTotals):

    psLog.debug('printWorkEventList')

    workEventName = ModelEntities.writeWorkEventListAsJson(patternListForJson)
    textWorkEventList = ModelEntities.readJsonWorkEventList(workEventName)
    textListForPrint = ModelEntities.makeTextListForPrint(textWorkEventList, trackTotals)
    ModelEntities.writeTextSwitchList(workEventName, textListForPrint)

    switchListFile = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\' + workEventName + '.txt'
    osSystem(PatternScriptEntities.openEditorByComputerType(switchListFile))

    return

def onScButtonPress():
    '''"Set Cars" button opens a window for each selected track'''

    psLog.debug('onScButtonPress')

    selectedTracks = getSelectedTracks()
    if not selectedTracks:
        psLog.warning('No tracks were selected for the Set Cars button')

        return

    locationName = PatternScriptEntities.readConfigFile('PT')['PL']
    windowOffset = 200
    for i, trackName in enumerate(selectedTracks, start=1):
        locationDict = makeLocationDict([trackName]) # makeLocationDict takes a track list
        setCarsForm = makeReport(locationDict, 'SC')
        newFrame = ControllerSetCarsForm.CreatePatternReportGui(setCarsForm)
        newWindow = newFrame.makeFrame()
        newWindow.setTitle(u'Set Cars Form for track ' + trackName)
        newWindow.setName('setCarsWindow')
        newWindow.setLocation(windowOffset, 180)
        newWindow.pack()
        newWindow.setVisible(True)

        psLog.info(u'Set Cars Window created for track ' + trackName)
        windowOffset += 50
    psLog.info(str(i) + ' Set Cars windows for ' + locationName + ' created')

    return

def resetTrainPlayerSwitchlist():
    '''Overwrites the existing file with the header info for the next switch list'''

    psLog.debug('resetTrainPlayerSwitchlist')

    locationDict = {'locationName':'Location Name', 'tracks':[{'trackName':'Track Name', 'length': 1, 'locos':[], 'cars':[]}]}
    setCarsForm = makeReport(locationDict, 'TP')
    ModelEntities.writeWorkEventListAsJson(setCarsForm)

    return

def makePatternLog():
    '''creates a pattern log for display based on the log level, as set by getBuildReportLevel'''

    outputPatternLog = ''
    buildReportLevel = int(jmri.jmrit.operations.setup.Setup.getBuildReportLevel())
    configLoggingIndex = PatternScriptEntities.readConfigFile('LI')
    logLevel = configLoggingIndex[jmri.jmrit.operations.setup.Setup.getBuildReportLevel()]
    logFileLocation = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog.txt'
    with codecsOpen(logFileLocation, 'r', encoding=PatternScriptEntities.setEncoding()) as patternLogFile:
        while True:
            thisLine = patternLogFile.readline()
            if not (thisLine):
                break
            if (configLoggingIndex['9'] in thisLine and buildReportLevel > 0): # critical
                outputPatternLog += thisLine
            if (configLoggingIndex['7'] in thisLine and buildReportLevel > 0): # error
                outputPatternLog += thisLine
            if (configLoggingIndex['5'] in thisLine and buildReportLevel > 0): # warning
                outputPatternLog += thisLine
            if (configLoggingIndex['3'] in thisLine and buildReportLevel > 2): # info
                outputPatternLog += thisLine
            if (configLoggingIndex['1'] in thisLine and buildReportLevel > 4): # debug
                outputPatternLog += thisLine

    tempLogFileLocation = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog_temp.txt'
    with codecsOpen(tempLogFileLocation, 'w', encoding=PatternScriptEntities.setEncoding()) as tempPatternLogFile:
        tempPatternLogFile.write(outputPatternLog)

    return

def updateLocations():
    '''Updates the config file with a list of all locations for this profile'''

    psLog.debug('updateLocations')
    newConfigFile = PatternScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['PT']
    allLocations  = ModelEntities.getAllLocations()
    if not (subConfigfile['AL']): # when this sub is used for the first tims
        subConfigfile.update({'PL': allLocations[0]})
        subConfigfile.update({'PT': ModelEntities.makeInitialTrackList(allLocations[0])})
    subConfigfile.update({'AL': allLocations})
    newConfigFile.update({'PT': subConfigfile})
    PatternScriptEntities.writeConfigFile(newConfigFile)

    return newConfigFile

def writeCsvSwitchList(trackPattern, type):
    '''Rewrite this to write from the JSON file'''

    psLog.debug('writeCsvSwitchList')
    trainDescription = PatternScriptEntities.readConfigFile('PT')['TD']
    csvCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists\\' + trainDescription[type]  + '.csv'
    csvObject = ModelEntities.makeCsvSwitchlist(trackPattern)
    with codecsOpen(csvCopyTo, 'wb', encoding=PatternScriptEntities.setEncoding()) as csvWorkFile:
        csvWorkFile.write(csvObject)

    return

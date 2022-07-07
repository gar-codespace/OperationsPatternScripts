# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ModelEntities
from PatternTracksSubroutine import ViewEntities
from PatternTracksSubroutine import ControllerSetCarsForm

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.Model'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.Model')

def updatePatternLocation(selectedItem=None):
    """Catches user edits of locations"""

    _psLog.debug('Model.updatePatternLocation')

    configFile = PatternScriptEntities.readConfigFile()
    newLocation = ModelEntities.testSelectedItem(selectedItem)
    newLocationList = PatternScriptEntities.getAllLocations()
    newLocationTrackDict = ModelEntities.getAllTracksForLocation(newLocation)
    configFile['PT'].update({'PA': False})
    configFile['PT'].update({'PI': False})
    configFile['PT'].update({'PL': newLocation})
    configFile['PT'].update({'AL': newLocationList})
    configFile['PT'].update({'PT': newLocationTrackDict})

    PatternScriptEntities.writeConfigFile(configFile)
    _psLog.info('The track list for location ' + newLocation + ' has been created')

    return newLocation

def makeNewPatternTracks(location):
    """Makes a new list of all tracks for a location"""

    _psLog.debug('Model.makeNewPatternTracks')
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
    """Returns a list of tracks by type for a location"""
    _psLog.debug('Model.makeTrackList')

    return ModelEntities.getTracksByLocation(type)

def updatePatternTracks(trackList):
    """Creates a new list of tracks and their default include flag"""

    _psLog.debug('Model.updatePatternTracks')
    trackDict = {}
    for track in trackList:
        trackDict[track] = False

    if (trackDict):
        _psLog.warning('The track list for this location has changed')
    else:
        _psLog.warning('There are no yard tracks for this location')

    return trackDict

def updateCheckBoxStatus(all, ignore):
    """Updates the config file with the checked status of Yard Tracks Only
    and Ignore Track Length check boxes
    """

    _psLog.debug('Model.updateCheckBoxStatus')
    newConfigFile = PatternScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['PT']
    subConfigfile.update({'PA': all})
    subConfigfile.update({'PI': ignore})
    newConfigFile.update({'PT': subConfigfile})

    return newConfigFile

def updateConfigFile(controls):
    """Updates the pattern tracks part of the config file"""

    _psLog.debug('Model.updateConfigFile')

    focusOn = PatternScriptEntities.readConfigFile('PT')
    focusOn.update({"PL": controls[0].getSelectedItem()})
    focusOn.update({"PA": controls[1].selected})
    focusOn.update({"PI": controls[2].selected})
    focusOn.update({"PT": ModelEntities.updateTrackCheckBoxes(controls[3])})
    newConfigFile = PatternScriptEntities.readConfigFile()
    newConfigFile.update({"PT": focusOn})
    PatternScriptEntities.writeConfigFile(newConfigFile)
    _psLog.info('Controls settings for configuration file updated')

    return controls

def getSelectedTracks():

    patternTracks = PatternScriptEntities.readConfigFile('PT')['PT']

    return [track for track, include in sorted(patternTracks.items()) if include]

def verifySelectedTracks():
    """Catches on the fly user edit of JMRI track names"""

    validStatus = True
    allTracksList = ModelEntities.getTracksByLocation(None)
    if not allTracksList:
        _psLog.warning('PatternConfig.JSON corrupted, new file written.')
        return False
    patternTracks = PatternScriptEntities.readConfigFile('PT')['PT']
    for track in patternTracks:
        if not track in allTracksList:
            validStatus = False

    return validStatus

def makeLocationDict(trackList=None):
    """Returns the details for the tracks sent in formatted for the json file """

    _psLog.debug('Model.makeLocationDict')

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

    _psLog.debug('Model.makeReport')

    if reportType == 'PR':
        reportTitle = PatternScriptEntities.BUNDLE['Track Pattern Report']

    if reportType == 'SC':
        reportTitle = PatternScriptEntities.BUNDLE['Switch List for Track']

    if reportType == 'TP':
        reportTitle = PatternScriptEntities.BUNDLE[u'Work Event List for TrainPlayer©']

    modifiedReport = ModelEntities.makeGenericHeader()
    modifiedReport.update({'trainDescription' : reportTitle})
    modifiedReport.update({'trainName' : reportTitle})
    modifiedReport['locations'] = [locationDict]
    # put in as a list to maintain compatability with JSON File Format/JMRI manifest export.

    return modifiedReport

def makeWorkEventList(patternListForJson, trackTotals):

    _psLog.debug('Model.makeWorkEventList')

    workEventName = ModelEntities.writeWorkEventListAsJson(patternListForJson)
    textWorkEventList = ModelEntities.readJsonWorkEventList(workEventName)

    textListForPrint = ViewEntities.makeTextListForPrint(textWorkEventList, trackTotals)

    return workEventName, textListForPrint

def onScButtonPress():
    """"Set Cars" button opens a window for each selected track"""

    _psLog.debug('Model.onScButtonPress')

    selectedTracks = getSelectedTracks()
    if not selectedTracks:
        _psLog.warning('No tracks were selected for the Set Cars button')

        return

    locationName = PatternScriptEntities.readConfigFile('PT')['PL']
    windowOffset = 200
    for i, trackName in enumerate(selectedTracks, start=1):
        locationDict = makeLocationDict([trackName]) # makeLocationDict takes a track list
        setCarsForm = makeReport(locationDict, 'SC')
        newFrame = ControllerSetCarsForm.CreatePatternReportGui(setCarsForm)
        newWindow = newFrame.makeFrame()
        newWindow.setTitle(PatternScriptEntities.BUNDLE['Set Cars Form for track:'] + ' ' + trackName)
        newWindow.setName('setCarsWindow')
        newWindow.setLocation(windowOffset, 180)
        newWindow.pack()
        newWindow.setVisible(True)

        _psLog.info(u'Set Cars Window created for track ' + trackName)
        windowOffset += 50
    _psLog.info(str(i) + ' Set Cars windows for ' + locationName + ' created')

    return

def resetTrainPlayerSwitchlist():
    """Overwrites the existing file with the header info for the next switch list"""

    _psLog.debug('Model.resetTrainPlayerSwitchlist')

    locationName = PatternScriptEntities.readConfigFile()['PT']['PL']
    locationDict = {'locationName':locationName, \
                    'tracks':[{'trackName':'Track Name', 'length': 1, 'locos':[], 'cars':[]}]}
    setCarsForm = makeReport(locationDict, 'TP')
    ModelEntities.writeWorkEventListAsJson(setCarsForm)

    return

def updateLocations():
    """Updates the config file with a list of all locations for this profile"""

    _psLog.debug('Model.updateLocations')
    newConfigFile = PatternScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['PT']
    allLocations  = PatternScriptEntities.getAllLocations()
    if not (subConfigfile['AL']): # when this sub is used for the first tims
        subConfigfile.update({'PL': allLocations[0]})
        subConfigfile.update({'PT': ModelEntities.makeInitialTrackList(allLocations[0])})
    subConfigfile.update({'AL': allLocations})
    newConfigFile.update({'PT': subConfigfile})
    PatternScriptEntities.writeConfigFile(newConfigFile)

    return newConfigFile

def writeCsvSwitchList(trackPattern):
    """Rewrite this to write from the json file"""

    _psLog.debug('Model.writeCsvSwitchList')

    csvName, csvReport = ModelEntities.makeCsvSwitchlist(trackPattern)
    csvPath = PatternScriptEntities.PROFILE_PATH + 'operations\\csvSwitchLists\\' + csvName + '.csv'
    PatternScriptEntities.genericWriteReport(csvPath, csvReport)

    return

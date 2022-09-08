# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.Model'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.Model')

def trackPatternButton():
    """Mini controller when the Track Pattern Report button is pressed
        Creates the Track Pattern data
        Used by:
        Controller.StartUp.trackPatternButton
        """

    locationDict = ModelEntities.makeLocationDict()
    modifiedReport = ModelEntities.makeReport(locationDict, 'PR')
    workEventName = ModelEntities.writeWorkEventListAsJson(modifiedReport)

    return

def updatePatternLocation(selectedItem=None):
    """Catches user edits of locations
        Used by:
        Controller.LocationComboBox.actionPerformed
        """

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

def makeTrackList(location, type):
    """Returns a list of tracks by type for a location
        Used by:
        Controller.StartUp.yardTrackOnlyCheckBox
        """
    _psLog.debug('Model.makeTrackList')

    return ModelEntities.getTracksByLocation(type)

def updatePatternTracks(trackList):
    """Creates a new list of tracks and their default include flag
        Used by:
        Controller.StartUp.yardTrackOnlyCheckBox
        """

    _psLog.debug('Model.updatePatternTracks')
    trackDict = {}
    for track in trackList:
        trackDict[track] = False

    if (trackDict):
        _psLog.warning('The track list for this location has changed')
    else:
        _psLog.warning('There are no yard tracks for this location')

    return trackDict

def updateConfigFile(controls):
    """Updates the pattern tracks part of the config file
        Used by:
        Controller.StartUp.trackPatternButton
        Controller.StartUp.setCarsButton
        """

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

def verifySelectedTracks():
    """Catches on the fly user edit of JMRI track names
        Used by:
        Controller.StartUp.trackPatternButton
        Controller.StartUp.setCarsButton
        """

    _psLog.debug('Model.verifySelectedTracks')

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

def updateLocations():
    """Updates the config file with a list of all locations for this profile
        Used by:
        Controller.StartUp.makeSubroutinePanel
        """

    _psLog.debug('Model.updateLocations')
    newConfigFile = PatternScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['PT']
    allLocations = PatternScriptEntities.getAllLocations()
    if not allLocations:
        _psLog.warning('There are no locations for this profile')
        return
    if not (subConfigfile['AL']): # when this sub is used for the first time
        subConfigfile.update({'PL': allLocations[0]})
        subConfigfile.update({'PT': ModelEntities.makeInitialTrackList(allLocations[0])})
    subConfigfile.update({'AL': allLocations})
    newConfigFile.update({'PT': subConfigfile})
    PatternScriptEntities.writeConfigFile(newConfigFile)

    return newConfigFile

def writeTrackPatternCsv(workEventName):
    """Track Pattern Report json is written as a CSV file
        Used by:
        Controller.StartUp.trackPatternButton
        """

    _psLog.debug('Model.writeTrackPatternCsv')
#  Get json data
    workEvents = PatternScriptEntities.readJsonWorkEventList(workEventName)
# Process json data into CSV
    csvReport = ModelEntities.makeWorkEventsCsv(workEvents)
# Write CSV data
    csvPath = PatternScriptEntities.PROFILE_PATH + 'operations\\csvSwitchLists\\' + workEventName + '.csv'
    PatternScriptEntities.genericWriteReport(csvPath, csvReport)

    return

# def resetTrainPlayerSwitchlist():
#     """Not used"""
#
#     _psLog.debug('Model.resetTrainPlayerSwitchlist')
#
#     locationName = PatternScriptEntities.readConfigFile()['PT']['PL']
#     locationDict = {'locationName':locationName, \
#                     'tracks':[{'trackName':'Track Name', 'length': 1, 'locos':[], 'cars':[]}]}
#     setCarsForm = makeReport(locationDict, 'TP')
#     ModelEntities.writeWorkEventListAsJson(setCarsForm)
#
#     return

# def makeNewPatternTracks(location):
#     """Makes a new list of all tracks for a location
#         Used by:
#         """
#
#     _psLog.debug('Model.makeNewPatternTracks')
#     allTracks = ModelEntities.getTracksByLocation(None)
#     trackDict = {}
#     for track in allTracks:
#         trackDict[track] = False
#     newConfigFile = PatternScriptEntities.readConfigFile()
#     subConfigfile = newConfigFile['PT']
#     subConfigfile.update({'PT': trackDict})
#     newConfigFile.update({'PT': subConfigfile})
#
#     return newConfigFile

# def updateCheckBoxStatus(all, ignore):
#     """Updates the config file with the checked status of Yard Tracks Only
#         and Ignore Track Length check boxes
#         """
#
#     _psLog.debug('Model.updateCheckBoxStatus')
#     newConfigFile = PatternScriptEntities.readConfigFile()
#     subConfigfile = newConfigFile['PT']
#     subConfigfile.update({'PA': all})
#     subConfigfile.update({'PI': ignore})
#     newConfigFile.update({'PT': subConfigfile})
#
#     return newConfigFile

# def makeLocationDict(trackList=None):
#     """Called by: Model.trackPatternButton, View.setCarsButton"""
#
#     _psLog.debug('Model.makeLocationDict')
#
#     if not trackList:
#         trackList = PatternScriptEntities.getSelectedTracks()
#
#     detailsForTrack = []
#     patternLocation = PatternScriptEntities.readConfigFile('PT')['PL']
#     for trackName in trackList:
#         detailsForTrack.append(ModelEntities.getGenericTrackDetails(patternLocation, trackName))
#
#     locationDict = {}
#     locationDict['locationName'] = patternLocation
#     locationDict['tracks'] = detailsForTrack
#
#     return locationDict

# def makeReport(locationDict, reportType):
#
#     _psLog.debug('Model.makeReport')
#
#     if reportType == 'PR':
#         reportTitle = PatternScriptEntities.BUNDLE['Track Pattern Report']
#
#     if reportType == 'SC':
#         reportTitle = PatternScriptEntities.BUNDLE['Switch List for Track']
#
#     if reportType == 'TP':
#         reportTitle = PatternScriptEntities.BUNDLE[u'Work Event List for TrainPlayer©']
#
#     modifiedReport = ModelEntities.makeGenericHeader()
#     modifiedReport.update({'trainDescription' : reportTitle})
#     modifiedReport.update({'trainName' : reportTitle})
#     modifiedReport['locations'] = [locationDict]
#     # put in as a list to maintain compatability with JSON File Format/JMRI manifest export.
#
#     return modifiedReport

# def getSelectedTracks():
#
#     patternTracks = PatternScriptEntities.readConfigFile('PT')['PT']
#
#     return [track for track, include in sorted(patternTracks.items()) if include]

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

    reportTitle = PatternScriptEntities.BUNDLE['Track Pattern Report']
    trackPatternPath = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + reportTitle + '.json'

    trackPattern = ModelEntities.makeTrackPattern()
    trackPatternReport = ModelEntities.makeTrackPatternReport(trackPattern)
    trackPatternReport = PatternScriptEntities.dumpJson(trackPatternReport)
    PatternScriptEntities.genericWriteReport(trackPatternPath, trackPatternReport)

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
    allTracksList = PatternScriptEntities.getTracksByLocation(None)

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

def writeTrackPatternCsv(trackPatternName):
    """Track Pattern Report json is written as a CSV file
        Used by:
        Controller.StartUp.trackPatternButton
        """

    _psLog.debug('Model.writeTrackPatternCsv')
#  Get json data
    trackPatternPath = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + trackPatternName + '.json'
    trackPattern = PatternScriptEntities.genericReadReport(trackPatternPath)
    trackPattern = PatternScriptEntities.loadJson(trackPattern)
# Process json data into CSV
    trackPatternCsv = ModelEntities.makeTrackPatternCsv(trackPattern)
# Write CSV data
    csvPath = PatternScriptEntities.PROFILE_PATH + 'operations\\csvSwitchLists\\' + trackPatternName + '.csv'
    PatternScriptEntities.genericWriteReport(csvPath, trackPatternCsv)

    return

# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PSE
from PatternTracksSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.Model'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('PS.PT.Model')

def trackPatternButton():
    """Mini controller when the Track Pattern Report button is pressed
        Creates the Track Pattern data
        Used by:
        Controller.StartUp.trackPatternButton
        """

    reportTitle = PSE.BUNDLE['Track Pattern Report']
    fileName = reportTitle + '.json'
    targetDir = PSE.PROFILE_PATH + 'operations\\jsonManifests'
    targetPath = PSE.OS_Path.join(targetDir, fileName)

    trackPattern = ModelEntities.makeTrackPattern()
    trackPatternReport = ModelEntities.makeTrackPatternReport(trackPattern)
    trackPatternReport = PSE.dumpJson(trackPatternReport)
    PSE.genericWriteReport(targetPath, trackPatternReport)

    return

def setRsButton():
    """Mini controller when the Set cars button is pressed
        Creates a new o2o Work Events.json file
        Used by:
        Controller.StartUp.setRsButton
        """

    reportTitle = PSE.BUNDLE['o2o Work Events']
    fileName = reportTitle + '.json'
    targetDir = PSE.PROFILE_PATH + 'operations\\jsonManifests'
    targetPath = PSE.OS_Path.join(targetDir, fileName)

    newHeader = ModelEntities.makeGenericHeader()
    newHeaderReport = PSE.dumpJson(newHeader)
    PSE.genericWriteReport(targetPath, newHeaderReport)

    return

def updatePatternLocation(selectedItem=None):
    """Catches user edits of locations
        Used by:
        PTSub.Controller.LocationComboBox.actionPerformed
        o2oSub.Model.updatePatternTracksSubroutine
        """

    _psLog.debug('Model.updatePatternLocation')

    configFile = PSE.readConfigFile()
    newLocation = ModelEntities.testSelectedItem(selectedItem)
    newLocationList = PSE.getAllLocationNames()
    newLocationTrackDict = ModelEntities.getAllTracksForLocation(newLocation)
    configFile['PT'].update({'PA': False})
    configFile['PT'].update({'PI': False})
    configFile['PT'].update({'PL': newLocation})
    configFile['PT'].update({'AL': newLocationList})
    configFile['PT'].update({'PT': newLocationTrackDict})

    PSE.writeConfigFile(configFile)
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

    if trackDict:
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

    focusOn = PSE.readConfigFile('PT')
    focusOn.update({"PL": controls[0].getSelectedItem()})
    focusOn.update({"PA": controls[1].selected})
    focusOn.update({"PI": controls[2].selected})
    focusOn.update({"PT": ModelEntities.updateTrackCheckBoxes(controls[3])})

    newConfigFile = PSE.readConfigFile()
    newConfigFile.update({"PT": focusOn})
    PSE.writeConfigFile(newConfigFile)

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
    allTracksList = PSE.getTracksByLocation(None)

    if not allTracksList:
        _psLog.warning('PatternConfig.JSON corrupted, new file written.')
        return False

    patternTracks = PSE.readConfigFile('PT')['PT']
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

    newConfigFile = PSE.readConfigFile()
    subConfigfile = newConfigFile['PT']

    allLocations = PSE.getAllLocationNames()
    if not allLocations:
        _psLog.warning('There are no locations for this profile')
        return

    if not (subConfigfile['AL']): # when this sub is used for the first time
        subConfigfile.update({'PL': allLocations[0]})
        subConfigfile.update({'PT': ModelEntities.makeInitialTrackList(allLocations[0])})

    subConfigfile.update({'AL': allLocations})
    newConfigFile.update({'PT': subConfigfile})
    PSE.writeConfigFile(newConfigFile)

    return newConfigFile

def writeTrackPatternCsv(trackPatternName):
    """Track Pattern Report json is written as a CSV file
        Used by:
        Controller.StartUp.trackPatternButton
        """

    _psLog.debug('Model.writeTrackPatternCsv')
#  Get json data
    targetDir = PSE.PROFILE_PATH + 'operations\\jsonManifests'
    fileName = trackPatternName + '.json'
    targetPath = PSE.OS_Path.join(targetDir, fileName)
    trackPattern = PSE.genericReadReport(targetPath)
    trackPattern = PSE.loadJson(trackPattern)
# Process json data into CSV
    trackPatternCsv = ModelEntities.makeTrackPatternCsv(trackPattern)
# Write CSV data
    targetDir = PSE.PROFILE_PATH + 'operations\\csvSwitchLists\\'
    fileName = trackPatternName + '.csv'
    targetPath = PSE.OS_Path.join(targetDir, fileName)
    PSE.genericWriteReport(targetPath, trackPatternCsv)

    return

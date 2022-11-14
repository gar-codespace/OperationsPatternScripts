# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE
from PatternTracksSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.Model'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.PT.Model')

def trackPatternButton():
    """Mini controller when the Track Pattern Report button is pressed
        Creates the Track Pattern data
        Used by:
        Controller.StartUp.trackPatternButton
        """

    fileName = PSE.BUNDLE['Track Pattern Report'] + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    trackPattern = ModelEntities.makeTrackPattern()
    trackPatternReport = ModelEntities.makeTrackPatternReport(trackPattern)
    trackPatternReport = PSE.dumpJson(trackPatternReport)
    PSE.genericWriteReport(targetPath, trackPatternReport)

    return

def updatePatternLocation(comboBox):
    """Catches user edits of locations
        A method is defined for each comboBox, the method name is the comboBox name.
        Used by:
        PTSub.Controller.LocationComboBox.actionPerformed
        o2oSub.Model.updatePatternTracksSubroutine
        """

    _psLog.debug('updatePatternLocation')



    getattr(PSE.sys.modules[__name__], comboBox.getName())(comboBox)


    # newLocation = ModelEntities.testSelectedItem(selectedItem)
    # newDivisionList = PSE.getAllDivisionNames()
    # newLocationList = PSE.getAllLocationNames()
    # newLocationTrackDict = ModelEntities.getAllTracksForLocation(newLocation)
    # configFile['PT'].update({'PA': False})
    # configFile['PT'].update({'PI': False})
    # configFile['PT'].update({'PL': newLocation})
    # configFile['PT'].update({'AD': newDivisionList})
    # configFile['PT'].update({'AL': newLocationList})
    # configFile['PT'].update({'PT': newLocationTrackDict})


    # _psLog.info('The track list for location ' + newLocation + ' has been created')

    return

def jDivision(comboBox):

    configFile = PSE.readConfigFile()
    newDivisionList = PSE.getAllDivisionNames()
    configFile['PT'].update({'AD': newDivisionList})
    configFile['PT'].update({'PD': comboBox.getSelectedItem()})
    PSE.writeConfigFile(configFile)

    return

def jLocations(comboBox):

    return

# def updatePatternLocation(selectedItem=None):
#     """Catches user edits of locations
#         Used by:
#         PTSub.Controller.LocationComboBox.actionPerformed
#         o2oSub.Model.updatePatternTracksSubroutine
#         """
#
#     _psLog.debug('updatePatternLocation')
#
#     configFile = PSE.readConfigFile()
#     newLocation = ModelEntities.testSelectedItem(selectedItem)
#     newDivisionList = PSE.getAllDivisionNames()
#     newLocationList = PSE.getAllLocationNames()
#     newLocationTrackDict = ModelEntities.getAllTracksForLocation(newLocation)
#     configFile['PT'].update({'PA': False})
#     configFile['PT'].update({'PI': False})
#     configFile['PT'].update({'PL': newLocation})
#     configFile['PT'].update({'AD': newDivisionList})
#     configFile['PT'].update({'AL': newLocationList})
#     configFile['PT'].update({'PT': newLocationTrackDict})
#
#     PSE.writeConfigFile(configFile)
#     _psLog.info('The track list for location ' + newLocation + ' has been created')
#
#     return newLocation


def updatePatternTracks(trackList):
    """Creates a new list of tracks and their default include flag
        Used by:
        Controller.StartUp.yardTrackOnlyCheckBox
        """

    _psLog.debug('updatePatternTracks')
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

    _psLog.debug('updateConfigFile')

    focusOn = PSE.readConfigFile('PT')
    focusOn.update({"PL": controls[1].getSelectedItem()})
    focusOn.update({"PA": controls[2].selected})
    focusOn.update({"PI": controls[3].selected})
    focusOn.update({"PT": ModelEntities.updateTrackCheckBoxes(controls[4])})

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

    _psLog.debug('verifySelectedTracks')

    validStatus = True
    allTracksAtLoc = PSE.getTracksNamesByLocation(None)

    if not allTracksAtLoc:
        _psLog.warning('PatternConfig.JSON corrupted, new file written.')
        return False

    patternTracks = PSE.readConfigFile('PT')['PT']
    for track in patternTracks:
        if not track in allTracksAtLoc:
            validStatus = False

    return validStatus

def updateLocations():
    """Updates the config file with a list of all locations for this profile
        Used by:
        Controller.StartUp.makeSubroutinePanel
        """

    _psLog.debug('updateLocations')

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

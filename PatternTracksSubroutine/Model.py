# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE
from PatternTracksSubroutine import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.PT.Model')

def trackPatternButton():
    """Mini controller when the Track Pattern Report button is pressed
        Creates the Track Pattern data
        Called by:
        Controller.StartUp.trackPatternButton
        """

    fileName = PSE.BUNDLE['Track Pattern Report'] + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    trackPattern = ModelEntities.makeTrackPattern()
    trackPatternReport = ModelEntities.makeTrackPatternReport(trackPattern)
    trackPatternReport = PSE.dumpJson(trackPatternReport)
    PSE.genericWriteReport(targetPath, trackPatternReport)

    return

def resetPatternLocation():
    """Called by:
        Controller.updatePatternTracksSubroutine
        """

    selectedItem = PSE.getAllDivisionNames()
    try:
        jDivision(selectedItem[0])
    except:
        jDivision(selectedItem)

    return

def updatePatternLocation(comboBox):
    """Clearinghouse that routes the combo box action to the appropriate method.
        Catches user edits of locations
        A method is defined for each comboBox, the method name is the comboBox name.
        Called by:
        PTSub.Controller.LocationComboBox.actionPerformed
        o2oSub.Model.updatePatternTracksSubroutine
        """

    selectedItem = comboBox.getSelectedItem()
    getattr(PSE.SYS.modules[__name__], comboBox.getName())(selectedItem)

    return

def jDivision(selectedItem):
    """Updates the Division: combo box and ripples the changes."""

    _psLog.debug('jDivision')

    configFile = PSE.readConfigFile()
    newDivisionList = PSE.getAllDivisionNames()

    newLocationList = PSE.getLocationNamesByDivision(selectedItem)
    
    if not newLocationList:
        newLocationList = PSE.getAllLocationNames()

    newLocationTrackDict = ModelEntities.getAllTracksForLocation(newLocationList[0])

    configFile['PT'].update({'AD': newDivisionList})
    configFile['PT'].update({'PD': selectedItem})

    configFile['PT'].update({'AL': newLocationList})
    configFile['PT'].update({'PL': newLocationList[0]})
    configFile['PT'].update({'PT': newLocationTrackDict})

    configFile['PT'].update({'PA': False})
    configFile['PT'].update({'PI': False})

    PSE.writeConfigFile(configFile)

    _psLog.info('The track list for division ' + str(selectedItem) + ' has been created')

    return

def jLocations(selectedItem):
    """Updates the Locations: combobox and ripples the changes."""

    _psLog.debug('jLocations')

    configFile = PSE.readConfigFile()
    newLocation = ModelEntities.testSelectedItem(selectedItem)
    newLocationList = PSE.getAllLocationNames()
    newLocationTrackDict = ModelEntities.getAllTracksForLocation(newLocation)

    configFile['PT'].update({'PL': newLocation})
    configFile['PT'].update({'PT': newLocationTrackDict})

    configFile['PT'].update({'PA': False})
    configFile['PT'].update({'PI': False})

    PSE.writeConfigFile(configFile)

    return

def updatePatternTracks(trackList):
    """Creates a new list of tracks and their default include flag
        Called by:
        Controller.StartUp.yardTrackOnlyCheckBox
        """

    _psLog.debug('updatePatternTracks')
    trackDict = {}
    for track in trackList:
        trackDict[track] = False

    if trackDict:
        _psLog.warning('The track list for this location has changed')
    else:
        _psLog.warning('There are no tracks for this selection')

    return trackDict

def updateConfigFile(controls):
    """Updates the pattern tracks part of the config file
        Called by:
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
        Called by:
        Controller.StartUp.trackPatternButton
        Controller.StartUp.setCarsButton
        """

    _psLog.debug('verifySelectedTracks')

    validStatus = True
    allTracksAtLoc = PSE.getTrackNamesByLocation(None)

    if not allTracksAtLoc:
        _psLog.warning('PatternConfig.JSON corrupted, new file written.')
        return False

    patternTracks = PSE.readConfigFile('PT')['PT']
    for track in patternTracks:
        if not track in allTracksAtLoc:
            validStatus = False

    return validStatus

def updateLocations():
    """Updates the PT section of the configFile..
        If entries are missing, makes new PT entries using initial values.
        The configFile is updated if initial values are used.
        Called by:
        Controller.StartUp.makeSubroutinePanel
        """

    _psLog.debug('updateLocations')

    configfile = PSE.readConfigFile()
    allDivisions = PSE.getAllDivisionNames()
    locations = []

    configfile['PT'].update({'AD': allDivisions})

    if len(allDivisions) != 0 and not configfile['PT']['PD']: # when this sub is initialized
        configfile['PT'].update({'PD': allDivisions[0]})

        _psLog.info('Set initial division in config file')

    if not configfile['PT']['PL']: # when this sub is initialised

        division = configfile['PT']['PD']
        locations = PSE.getLocationNamesByDivision(division)
        if not locations:
            locations = PSE.getAllLocationNames()

        try:
            configfile['PT'].update({'PL': locations[0]})
            configfile['PT'].update({'AL': locations})
            configfile['PT'].update({'PT': ModelEntities.makeInitialTrackDict(locations[0])})
        except:
            _psLog.warning('Initial location and tracks not set in config file')

        _psLog.info('Set initial location and tracks in config file')

    PSE.writeConfigFile(configfile)

    return

# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE
from Subroutines.Patterns import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.PT.Model')


def createFolder():
    """Creates a 'patterns' folder in operations."""

    targetDirectory = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'patterns')

    if not PSE.JAVA_IO.File(targetDirectory).isDirectory():
        PSE.JAVA_IO.File(targetDirectory).mkdirs()

        _psLog.info('Directory created: ' + targetDirectory)

    return

def verifySelectedTracks():
    """Catches on the fly user edit of JMRI track names
        Called by:
        Controller.StartUp.trackPatternButton
        Controller.StartUp.setCarsButton
        """

    _psLog.debug('verifySelectedTracks')

    validStatus = True
    allTracksAtLoc = ModelEntities.getTrackNamesByLocation(None)

    if not allTracksAtLoc:
        _psLog.warning('configFile.json corrupted, new file written.')
        return False

    patternTracks = PSE.readConfigFile('Patterns')['PT']
    for track in patternTracks:
        if not track in allTracksAtLoc:
            validStatus = False

    return validStatus

def getSelectedTracks():
    """Gets the track objects checked in the Track Pattern Subroutine."""

    patternTracks = PSE.readConfigFile('Patterns')['PT']

    return [track for track, include in sorted(patternTracks.items()) if include]

def patternReport():
    """Mini controller when the Track Pattern Report button is pressed
        Creates the Track Pattern data
        Called by:
        Controller.StartUp.patternReportButton
        """

    fileName = PSE.BUNDLE['Pattern Report'] + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'patterns', fileName)

    trackPattern = makeTrackPattern()
    trackPatternReport = makeTrackPatternReport(trackPattern)
    trackPatternReport = PSE.dumpJson(trackPatternReport)
    PSE.genericWriteReport(targetPath, trackPatternReport)

    return

def updateConfigFile(controls):
    """Updates the pattern tracks part of the config file
        Called by:
        Controller.StartUp.trackPatternButton
        Controller.StartUp.setCarsButton
        """

    _psLog.debug('updateConfigFile')

    configFile = PSE.readConfigFile()
    configFile['Patterns'].update({"PL": controls[1].getSelectedItem()})
    configFile['Patterns'].update({"PA": controls[2].selected})
    configFile['Patterns'].update({"PT": ModelEntities.updateTrackCheckBoxes(controls[3])})

    PSE.writeConfigFile(configFile)

    _psLog.info('Controls settings for configuration file updated')

    return controls



    


















def makeTrackPattern(trackList=None):
    """Called by:
        Model.trackPatternButton
        View.setRsButton
        """

    if not trackList:
        trackList = getSelectedTracks()

    detailsForTrack = []
    patternLocation = PSE.readConfigFile('Patterns')['PL']
    for trackName in trackList:
        detailsForTrack.append(ModelEntities.getGenericTrackDetails(patternLocation, trackName))

    trackPattern = {}
    trackPattern['locationName'] = patternLocation
    trackPattern['tracks'] = detailsForTrack

    return trackPattern

def makeTrackPatternReport(trackPattern):
    """Called by:
        Model.trackPatternButton
        View.setRsButton
        """

    trackPatternReport = initializeReportHeader()
    parseName = trackPatternReport['railroadName'].replace(';', '\n')
    trackPatternReport.update({'railroadName':parseName})

    division = PSE.getDivisionForLocation(trackPatternReport['locations'][0]['locationName'])
    trackPatternReport.update({'division':division})

# put in as a list to maintain compatability with JSON File Format/JMRI manifest export.
    trackPatternReport['locations'] = [trackPattern]

    return trackPatternReport



def initializeReportHeader():
    """Called by:
        makeTrackPatternReport
        Controller.StartUp.setRsButton
        """

    OSU = PSE.JMRI.jmrit.operations.setup
    configFile = PSE.readConfigFile()

    listHeader = {}
    listHeader['railroadName'] = unicode(OSU.Setup.getRailroadName(), PSE.ENCODING)

    listHeader['railroadDescription'] = ''
    listHeader['trainName'] = ''
    listHeader['trainDescription'] = ''
    listHeader['trainComment'] = ''
    listHeader['division'] = ''
    listHeader['date'] = unicode(PSE.validTime(), PSE.ENCODING)
    listHeader['locations'] = [{'locationName': configFile['Patterns']['PL'], 'tracks': [{'cars': [], 'locos': []}]}]

    return listHeader

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

    configFile['Patterns'].update({'AD': newDivisionList})
    configFile['Patterns'].update({'PD': selectedItem})

    configFile['Patterns'].update({'AL': newLocationList})
    configFile['Patterns'].update({'PL': newLocationList[0]})
    configFile['Patterns'].update({'PT': newLocationTrackDict})

    configFile['Patterns'].update({'PA': False})
    configFile['Patterns'].update({'PI': False})

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

    configFile['Patterns'].update({'PL': newLocation})
    configFile['Patterns'].update({'PT': newLocationTrackDict})

    configFile['Patterns'].update({'PA': False})
    configFile['Patterns'].update({'PI': False})

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





def updateLocations():
    """Updates the PT section of the configFile..
        If entries are missing, makes new PT entries using initial values.
        The configFile is updated if initial values are used.
        Called by:
        Controller.StartUp.makeSubroutinePanel
        """

    _psLog.debug('updateLocations')

    configFile = PSE.readConfigFile()

    allDivisions = PSE.getAllDivisionNames()
    locations = []

    configFile['Patterns'].update({'AD': allDivisions})

    if len(allDivisions) != 0 and not configFile['Patterns']['PD']: # when this sub is initialized
        configFile['Patterns'].update({'PD': allDivisions[0]})

        _psLog.info('Set initial division in config file')

    if not configFile['Patterns']['PL']: # when this sub is initialised

        division = configFile['Patterns']['PD']
        locations = PSE.getLocationNamesByDivision(division)
        if not locations:
            locations = PSE.getAllLocationNames()

        try:
            configFile['Patterns'].update({'PL': locations[0]})
            configFile['Patterns'].update({'AL': locations})
            configFile['Patterns'].update({'PT': ModelEntities.makeInitialTrackDict(locations[0])})
        except:
            _psLog.warning('Initial location and tracks not set in config file')

        _psLog.info('Set initial location and tracks in config file')

    PSE.writeConfigFile(configFile)

    return




# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from opsEntities import PSE
from Subroutines.Patterns import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.PT.Model')

def resetConfigFileItems():
    """Called from PSE.remoteCalls('resetCalls')"""

    configFile = PSE.readConfigFile()
    configFile['Patterns'].update({'PD':''})
    configFile['Patterns'].update({'PL':''})
    configFile['Patterns'].update({'PT':{}})
    configFile['Patterns'].update({'PA':False})
    configFile['Patterns'].update({'AL':[]})

    PSE.writeConfigFile(configFile)

    return

def initializeComboBoxes():
    """
    Initializes the Patterns section of the configFile when used for the first time.
    Called by:
    Controller.StartUp.makeSubroutinePanel
    """

    _psLog.debug('initializeComboBoxes')

    configFile = PSE.readConfigFile()

    print(PSE.DM.getNumberOfdivisions())


    if PSE.DM.getNumberOfdivisions() == 0:
        configFile['Patterns'].update({'AD': []})
        configFile['Patterns'].update({'PD': ''})
        locations = PSE.getAllLocationNames()
        configFile['Patterns'].update({'AL': locations})

        if configFile['Patterns']['PL'] == '':
            configFile['Patterns'].update({'PL': locations[0]})



    if PSE.DM.getNumberOfdivisions() > 0:
        allDivisions = PSE.getAllDivisionNames()

        configFile['Patterns'].update({'AD': allDivisions})
        locations = PSE.getLocationNamesByDivision(configFile['Patterns']['PD'])
        configFile['Patterns'].update({'AL': locations})
        if configFile['Patterns']['PD'] == '':
            configFile['Patterns'].update({'PD': allDivisions[0]})
            try:
                configFile['Patterns'].update({'PL': locations[0]})
            except:
                configFile['Patterns'].update({'PL': ''})

    _psLog.info('Set initial location and tracks in config file')

    PSE.writeConfigFile(configFile)

    return

def updateConfigFile(controls):
    """
    Updates the Patterns part of the config file
    Called by:
    Controller.StartUp.trackPatternButton
    Controller.StartUp.setCarsButton
    """

    _psLog.debug('updateConfigFile')

    configFile = PSE.readConfigFile()
    configFile['Patterns'].update({"PL": controls[1].getSelectedItem()})
    configFile['Patterns'].update({"PA": controls[2].selected})

    PSE.writeConfigFile(configFile)

    return controls

def validSelection(trackCheckBoxes):
    """
    Catches on the fly user edit of JMRI location and tracknames.
    patternTracks and allTracksAtLoc should be the same.
    Called by:
    Controller.StartUp.trackPatternButton
    Controller.StartUp.setCarsButton
    """

    _psLog.debug('validSelection')
    configFile = PSE.readConfigFile()
    patternLocation = configFile['Patterns']['PL']

    if not PSE.LM.getLocationByName(patternLocation): # test if location was changed.
        return False

    allTracksAtLoc = ModelEntities.getTrackNamesByLocation(None)
    subTracksAtLoc = [widget.text for widget in trackCheckBoxes]
    if list(set(allTracksAtLoc).difference(set(subTracksAtLoc))): # Test if track names were changed.
        return False

    return True

def makeTrackPatternBody(trackCheckBoxes):
    """Makes the body of a track pattern report."""

    patternLocation = PSE.readConfigFile('Patterns')['PL']

    detailsForTrack = []
    for widget in sorted(trackCheckBoxes):
        if widget.selected:
            detailsForTrack.append(ModelEntities.getGenericTrackDetails(patternLocation, widget.text))

    trackPatternBody = {}
    trackPatternBody['locationName'] = patternLocation
    trackPatternBody['tracks'] = detailsForTrack

    return trackPatternBody

def makeTrackPatternReport(trackPattern):
    """Combine header and body into a complete report."""

    trackPatternReport = initializeReportHeader()
    parseName = trackPatternReport['railroadName'].replace(';', '\n')
    trackPatternReport.update({'railroadName':parseName})

    division = PSE.getDivisionForLocation(trackPatternReport['locations'][0]['locationName'])
    trackPatternReport.update({'division':division})

# put in as a list to maintain compatability with JSON File Format/JMRI manifest export.
    trackPatternReport['locations'] = [trackPattern]

    return trackPatternReport

def writePatternReport(trackPattern):
    """
    Writes the track pattern report as a json file.
    Called by:
    Controller.StartUp.patternReportButton
    """

    fileName = PSE.BUNDLE['ops-pattern-report'] + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    
    trackPatternReport = PSE.dumpJson(trackPattern)
    PSE.genericWriteReport(targetPath, trackPatternReport)

    return

def appendWorkList(mergedForm):

    tracks = mergedForm['locations'][0]['tracks'][0]

    fileName = PSE.BUNDLE['ops-work-list'] + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    currentWorkList = PSE.jsonLoadS(PSE.genericReadReport(targetPath))

    currentWorkList['locations'][0]['tracks'].append(tracks)
    currentWorkList = PSE.dumpJson(currentWorkList)

    PSE.genericWriteReport(targetPath, currentWorkList)

    return

def newWorkList():
    """
    The work list is all the switchlists combined.
    Reset when the Set Cars button is pressed.
    """

    workList = initializeReportHeader()

    fileName = PSE.BUNDLE['ops-work-list'] + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    workList = PSE.dumpJson(workList)
    PSE.genericWriteReport(targetPath, workList)

    return

def initializeReportHeader():

    OSU = PSE.JMRI.jmrit.operations.setup
    configFile = PSE.readConfigFile()

    listHeader = {}
    listHeader['railroadName'] = getRailroadName()

    listHeader['railroadDescription'] = configFile['Patterns']['RD']
    listHeader['trainName'] = configFile['Patterns']['TN']
    listHeader['trainDescription'] = configFile['Patterns']['TD']
    listHeader['trainComment'] = configFile['Patterns']['TC']
    listHeader['division'] = configFile['Patterns']['PD']
    listHeader['date'] = unicode(PSE.validTime(), PSE.ENCODING)
    listHeader['locations'] = [{'locationName': configFile['Patterns']['PL'], 'tracks': [{'cars': [], 'locos': [], 'length': '', 'trackname': ''}]}]

    return listHeader

def getRailroadName():
    """
    Returns either a standard or extended railroad name.
    """

    configFile = PSE.readConfigFile()

    if not configFile['Main Script']['CP']['EH']:
        OSU = PSE.JMRI.jmrit.operations.setup
        return unicode(OSU.Setup.getRailroadName(), PSE.ENCODING)

    rrName = ''
    if configFile['Main Script']['LD']['OR']:
        rrName += configFile['Main Script']['LD']['OR'] + '\n'

    if configFile['Main Script']['LD']['TR']:
        rrName += configFile['Main Script']['LD']['TR'] + '\n'

    if configFile['Main Script']['LD']['LO']:
        rrName += configFile['Main Script']['LD']['LO'] + '\n'

    return rrName[:-1]

def jDivision(selectedItem):
    """Updates the Division: combo box and ripples the changes.
        jDivisions is also the name of the combobox.
        """

    _psLog.debug('jDivision')

    configFile = PSE.readConfigFile()
    newDivision = ModelEntities.testSelectedDivision(selectedItem)
    newDivisionList = PSE.getAllDivisionNames()
    newLocationList = PSE.getLocationNamesByDivision(selectedItem)

    if not newLocationList:
        # newLocationList = PSE.getAllLocationNames()
        configFile['Patterns'].update({'PL': ''})
    else:
        configFile['Patterns'].update({'PL': newLocationList[0]})

    configFile['Patterns'].update({'PD': newDivision})
    configFile['Patterns'].update({'AD': newDivisionList})
    configFile['Patterns'].update({'AL': newLocationList})

    PSE.writeConfigFile(configFile)
    PSE.restartSubroutineByName(__package__)

    return

def jLocations(selectedItem):
    """Updates the Locations: combobox and ripples the changes.
        jLocations is also the name of the combobox.
        """

    _psLog.debug('jLocations')

    configFile = PSE.readConfigFile()
    newLocation = ModelEntities.testSelectedLocation(selectedItem)






    if PSE.DM.getNumberOfdivisions() == 0:
        newLocationList = PSE.getAllLocationNames()
    else:
        newLocationList = PSE.getLocationNamesByDivision(configFile['Patterns']['PD'])






    configFile['Patterns'].update({'PL': newLocation})
    configFile['Patterns'].update({'AL': newLocationList})

    PSE.writeConfigFile(configFile)
    PSE.restartSubroutineByName(__package__)

    return

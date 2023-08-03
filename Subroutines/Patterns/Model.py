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
    """
    Called from PSE.remoteCalls('resetCalls')
    """

    configFile = PSE.readConfigFile()

    configFile['Patterns'].update({'AD':[]})
    configFile['Patterns'].update({'PD':''})

    configFile['Patterns'].update({'AL':[]})
    configFile['Patterns'].update({'PL':''})

    configFile['Patterns'].update({'PT':{}})
    configFile['Patterns'].update({'PA':False})

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

    if PSE.DM.getNumberOfdivisions() == 0:
        configFile['Patterns'].update({'AD': []})
        configFile['Patterns'].update({'PD': ''})
        locations = PSE.getAllLocationNames()
        configFile['Patterns'].update({'AL': locations})

        if configFile['Patterns']['PL'] == '':
            try:
                configFile['Patterns'].update({'PL': locations[0]})
            except:
                print('Exception at: Patterns.Model.initializeComboBoxes')
                configFile['Patterns'].update({'PL': ''})



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
                print('Exception at: Patterns.Model.initializeComboBoxes')
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

def validateSelection(selectedTracks):
    """
    Catches on the fly user edit of JMRI location and tracknames.
    patternTracks and allTracksAtLoc should be the same.
    Called by:
    Controller.StartUp.trackPatternButton
    Controller.StartUp.setCarsButton
    """

    _psLog.debug('validateSelection')
    configFile = PSE.readConfigFile()
    patternLocation = configFile['Patterns']['PL']

    if not PSE.LM.getLocationByName(patternLocation): # test if location was changed.
        return False

    allTracksAtLoc = ModelEntities.getTrackNamesByLocation(None)
    for track in selectedTracks:
        if track not in allTracksAtLoc:
            return False

    return True

def makeTrackPattern(selectedTracks):
    """
    Mini controller.
    """

    patternReport = makeReportHeader()
    patternReport['tracks'] = makeReportTracks(selectedTracks)

    return patternReport

def makeReportHeader():

    configFile = PSE.readConfigFile()

    reportHeader = {}
    reportHeader['railroadName'] = PSE.getRailroadName()

    reportHeader['railroadDescription'] = configFile['Patterns']['RD']
    reportHeader['trainName'] = configFile['Patterns']['TN']
    reportHeader['trainDescription'] = configFile['Patterns']['TD']
    reportHeader['trainComment'] = configFile['Patterns']['TC']
    reportHeader['division'] = configFile['Patterns']['PD']
    reportHeader['date'] = unicode(PSE.validTime(), PSE.ENCODING)
    reportHeader['location'] =configFile['Patterns']['PL']

    return reportHeader

def makeReportTracks(selectedTracks):

    configFile =  PSE.readConfigFile()
    tracks = []
    for trackName in sorted(selectedTracks):
        trackDetails = ModelEntities.getTrackDetails(configFile['Patterns']['PL'], trackName)
        tracks.append(trackDetails)

    return tracks

def writePatternReport(trackPattern):
    """
    Writes the track pattern report as a json file.
    Called by:
    Controller.StartUp.patternReportButton
    """

    fileName = PSE.getBundleItem('ops-pattern-report') + '.json'    
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)

    trackPatternReport = PSE.dumpJson(trackPattern)
    PSE.genericWriteReport(targetPath, trackPatternReport)

    return

def resetWorkList():
    """
    The worklist is reset when the Set Cars button is pressed.
    """

    workList = makeReportHeader()

    fileName = PSE.getBundleItem('ops-work-list') + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    workList = PSE.dumpJson(workList)
    PSE.genericWriteReport(targetPath, workList)

    return

def appendWorkList(mergedForm):

    tracks = mergedForm['tracks'][0]

    fileName = PSE.getBundleItem('ops-work-list') + '.json'    
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    currentWorkList = PSE.jsonLoadS(PSE.genericReadReport(targetPath))

    currentWorkList['locations'][0]['tracks'].append(tracks)
    currentWorkList = PSE.dumpJson(currentWorkList)

    PSE.genericWriteReport(targetPath, currentWorkList)

    return

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

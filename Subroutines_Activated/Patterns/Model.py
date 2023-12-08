# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from copy import deepcopy

from opsEntities import PSE
from opsEntities import TextReports
from Subroutines_Activated.Patterns import ModelEntities

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.PT.Model')


""" Routines called by the plugin listeners """


def resetConfigFileItems():

    return

def initializeSubroutine():

    divComboUpdater()
    locComboUpdater()
    makeTrackRows()
        
    return

def resetSubroutine():

    divComboUpdater()
    locComboUpdater()
    makeTrackRows()

    return

def refreshSubroutine():

    return

def addSubroutineListeners():
    """
    Add any listeners specific to this subroutine.
    """

    return

def removeSubroutineListeners():
    """
    Removes any listeners specific to this subroutine.
    """

    return


""" Routines specific to this subroutine """


def divComboUpdater():
    """
    Updates the contents of the divisions combo box when the listerers detect a change.
    """

    _psLog.debug('divComboUpdater')
    configFile = PSE.readConfigFile()

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
    component = PSE.getComponentByName(frame, 'jDivisions')

    component.removeAllItems()
    component.addItem(None)
    for divisionName in PSE.getAllDivisionNames():
        component.addItem(divisionName)

    configFile['Patterns'].update({'PD':None})
    PSE.writeConfigFile(configFile)

    return component

def locComboUpdater():
    """
    Updates the contents of the locations combo box when the listerers detect a change.
    """

    _psLog.debug('locComboUpdater')
    configFile = PSE.readConfigFile()
    divisionName = configFile['Patterns']['PD']

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    component = PSE.getComponentByName(frame, 'jLocations')
    component.removeAllItems()
    component.addItem(None)
    for locationName in ModelEntities.getLocationNamesByDivision(divisionName):
        component.addItem(locationName)

    configFile['Patterns'].update({'PL':None})
    PSE.writeConfigFile(configFile)

    return component

def divComboSelected(EVENT):
    """
    """

    _psLog.debug('divComboSelected')

    configFile = PSE.readConfigFile()

    itemSelected = EVENT.getSource().getSelectedItem()
    if not itemSelected:
        itemSelected = None

    configFile['Patterns'].update({'PD': itemSelected})
    PSE.writeConfigFile(configFile)

    return

def locComboSelected(EVENT):
    """
    """

    _psLog.debug('locComboSelected')

    configFile = PSE.readConfigFile()

    itemSelected = EVENT.getSource().getSelectedItem()
    if not itemSelected:
        itemSelected = None

    configFile['Patterns'].update({'PL': itemSelected})
    PSE.writeConfigFile(configFile)

    return


""" Routines specific to this subroutine """


def makeJsonTrackPattern(selectedTracks):
    """
    This track pattern json file mimics the JMRI manifest json.
    """
    
    jsonTrackPattern = makeReportHeader()
    jsonTrackPattern['locations'] = ModelEntities.getDetailsByTrack(selectedTracks, True)

    reportName = PSE.readConfigFile()['Main Script']['US']['OPR'].format('OPS', 'json')
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    PSE.genericWriteReport(targetPath, PSE.dumpJson(jsonTrackPattern))

    return jsonTrackPattern

def makeReportHeader():
    """
    Makes the header for:
    OPS Pattern Report
    OPS Set Cars frame
    OPS Switch List.
    """

    configFile = PSE.readConfigFile()
    OSU = PSE.JMRI.jmrit.operations.setup
    
    locationName = configFile['Patterns']['PL']
    divisionName = PSE.LM.getLocationByName(locationName).getDivisionName()
    reportHeader = {}

    reportHeader['date'] = PSE.isoTimeStamp()
    reportHeader['description'] = configFile['Patterns']['TD']
    reportHeader['railroad'] = OSU.Setup.getRailroadName()
    reportHeader['userName'] = configFile['Patterns']['PL']
    reportHeader['location'] = {'userName':locationName}
    reportHeader['division'] = {'userName':divisionName}

    return reportHeader

def makeTrackRows():
    """
    For the plugin GUI.
    Creates a row of check boxes, one for each track.
    If no tracks for the selected location, displays a message.
    """

    _psLog.debug('makeTrackRows')

    configFile = PSE.readConfigFile()

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
    component = PSE.getComponentByName(frame, 'jTracksPanel')
    
    label = PSE.getComponentByName(frame, 'jTracksPanelLabel')
    checkBox = PSE.getComponentByName(frame, 'jTrackCheckBox')

    component.removeAll()
    trackDict = getTrackDict()
    if trackDict:
        for track, flag in sorted(trackDict.items()):
            trackCheckBox = deepcopy(checkBox)
            trackCheckBox.actionPerformed = trackCheckBoxAction
            trackCheckBox.setText(track)
            trackCheckBox.setSelected(flag)
            trackCheckBox.setVisible(True)
            component.add(trackCheckBox)
    else:
        trackLabel = deepcopy(label)
        trackLabel.setText(PSE.getBundleItem('There are no tracks for this selection'))
        trackLabel.setVisible(True)
        component.add(trackLabel)

    configFile['Patterns'].update({'PT':trackDict})
    PSE.writeConfigFile(configFile)

    frame.validate()
    frame.repaint()

    return

def trackCheckBoxAction(EVENT):
    """
    Action listener attached to each track check box.
    """

    _psLog.debug(EVENT)

    configFile = PSE.readConfigFile() 
    configFile['Patterns']['PT'].update({EVENT.getSource().text:EVENT.getSource().selected})

    PSE.writeConfigFile(configFile)
    
    return
    
def getTrackDict():
    """
    Returns a dictionary of 'Track Name':False pairs.
    Used to create the row of track check boxes.
    """

    configFile = PSE.readConfigFile()

    trackDict = {}

    yardTracksOnlyFlag = None
    if configFile['Patterns']['PA']:
        # yardTracksOnlyFlag = 'Yard'
        yardTracksOnlyFlag = 'Spur'

    try:
        trackList = PSE.LM.getLocationByName(configFile['Patterns']['PL']).getTracksByNameList(yardTracksOnlyFlag)
    except:
        trackList = []

    for track in trackList:
        trackDict[unicode(track, PSE.ENCODING)] = False

    return trackDict


def getSetCarsData(selectedTrack):
    """
    Gets the data for:
    OPS Set Cars frame.
    OPS set cars switch list.
    """

    setCarsData = makeReportHeader()
    setCarsData['locations'] = ModelEntities.getDetailsByTrack([selectedTrack], False)

    return setCarsData


def writePatternReport(textPatternReport, flag):
    """
    Writes the track pattern report as a text file.
    """

    if flag: # Report is a track pattern
        reportName = PSE.readConfigFile()['Main Script']['US']['OPR'].format('OPS', 'txt')
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', reportName)
    else: # Report is a switch list
        reportName = PSE.readConfigFile()['Main Script']['US']['OSL'].format('OPS', 'txt')
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchLists', reportName)  

    PSE.genericWriteReport(targetPath, textPatternReport)

    return targetPath

def resetSwitchList():
    """
    The worklist is reset when the Set Cars button is pressed.
    """

    workList = makeReportHeader()
    workList['locations'] = []

    reportName = PSE.readConfigFile()['Main Script']['US']['OSL'].format('OPS', 'json')
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    workList = PSE.dumpJson(workList)
    PSE.genericWriteReport(targetPath, workList)

    return targetPath

def patternReportAsCsv():
    """
    pattern report-OPS.json is written as a CSV file
    """

    _psLog.debug('patternReportAsCsv')

    if not PSE.JMRI.jmrit.operations.setup.Setup.isGenerateCsvManifestEnabled():
        return
#  Get json data
    reportName = PSE.readConfigFile()['Main Script']['US']['OPR'].format('OPS', 'json')
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    patternReport = PSE.loadJson(PSE.genericReadReport(targetPath))
# Process json data into CSV
    patternReportCsv = TextReports.opsCsvGenericReport(patternReport)
# Write CSV data
    reportName = PSE.readConfigFile()['Main Script']['US']['OPR'].format('OPS', 'csv')
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'csvManifests', reportName)
    PSE.genericWriteReport(targetPath, patternReportCsv)

    return

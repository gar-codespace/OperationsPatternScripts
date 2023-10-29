# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from copy import deepcopy

from opsEntities import PSE
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
    for locationName in PSE.getLocationNamesByDivision(divisionName):
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

    fileName = PSE.getBundleItem('ops-Pattern Report') + '.json'    
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
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
    
    reportHeader = {}

    reportHeader['date'] = PSE.isoTimeStamp()
    reportHeader['description'] = configFile['Patterns']['TD']
    reportHeader['railroad'] = OSU.Setup.getRailroadName()
    reportHeader['userName'] = configFile['Patterns']['PL']

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
        yardTracksOnlyFlag = 'Yard'

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
        fileName = PSE.getBundleItem('ops-Pattern Report') + '.txt'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', fileName)
    else: # Report is a switch list
        fileName = PSE.getBundleItem('ops-Switch List') + '.txt'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchLists', fileName)  

    PSE.genericWriteReport(targetPath, textPatternReport)

    return targetPath

def resetSwitchList():
    """
    The worklist is reset when the Set Cars button is pressed.
    """

    workList = makeReportHeader()
    workList['locations'] = []

    fileName = PSE.getBundleItem('ops-Switch List') + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    workList = PSE.dumpJson(workList)
    PSE.genericWriteReport(targetPath, workList)

    return targetPath

def getReport(reportName):
    
    fileName = reportName + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    report = PSE.genericReadReport(targetPath)

    return PSE.loadJson(report)

def trackPatternAsCsv(reportName):
    """
    ops-pattern-report.json is written as a CSV file
    Called by:
    Controller.StartUp.trackPatternButton
    """

    _psLog.debug('trackPatternAsCsv')

    if not PSE.JMRI.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled():
        return
#  Get json data
    fileName = reportName + '.json'    

    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    trackPatternCsv = PSE.genericReadReport(targetPath)
    trackPatternCsv = PSE.loadJson(trackPatternCsv)
# Process json data into CSV
    trackPatternCsv = makeTrackPatternCsv(trackPatternCsv)
# Write CSV data
    fileName = reportName + '.csv'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'csvSwitchLists', fileName)
    PSE.genericWriteReport(targetPath, trackPatternCsv)

    return

def makeTrackPatternCsv(trackPattern):
    """
    The double quote for the railroadName entry is added to keep the j Pluse extended data intact.
    CSV writer does not support utf-8.
    Called by:
    Model.writeTrackPatternCsv
    """

    trackPatternCsv = 'Operator,Description,Parameters\n'
    trackPatternCsv += 'RT,Report Type,' + trackPattern['trainDescription'] + '\n'
    trackPatternCsv += 'RD,Railroad Division,' + str(trackPattern['division']) + '\n'
    trackPatternCsv += 'LN,Location Name,' + trackPattern['location'] + '\n'
    trackPatternCsv += 'PRNTR,Printer Name,\n'
    trackPatternCsv += 'YPC,Yard Pattern Comment,' + trackPattern['trainComment'] + '\n'
    trackPatternCsv += 'VT,Valid,' + trackPattern['date'] + '\n'
    trackPatternCsv += 'SE,Set Engines\n'
    trackPatternCsv += 'setTo,Road,Number,Type,Model,Length,Weight,Consist,Owner,Track,Location,Destination,Comment\n'
    for track in trackPattern['tracks']:
        try:
            trackPatternCsv += 'TN,Track name,' + unicode(track['trackName'], PSE.ENCODING) + '\n'
        except:
            print('Exception at: Patterns.View.makeTrackPatternCsv')
            
        for loco in track['locos']:
            trackPatternCsv +=  loco['setTo'] + ',' \
                            + loco[PSE.SB.handleGetMessage('Road')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Number')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Type')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Model')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Length')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Division')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Weight')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Consist')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Color')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Owner')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Track')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Location')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Destination')] + ',' \
                            + loco[PSE.SB.handleGetMessage('Comment')] + ',' \
                            + '\n'
    trackPatternCsv += 'SC,Set Cars\n'
    trackPatternCsv += 'setTo,Road,Number,Type,Length,Weight,Load,Load_Type,Hazardous,Color,Kernel,Kernel_Size,Owner,Track,Location,Destination,dest&Track,Final_Dest,fd&Track,Comment,Drop_Comment,Pickup_Comment,RWE\n'
    for track in trackPattern['tracks']:
        try:
            trackPatternCsv += 'TN,Track name,' + unicode(track['trackName'], PSE.ENCODING) + '\n'
        except:
            print('Exception at: Patterns.View.makeTrackPatternCsv')

        for car in track['cars']:
            trackPatternCsv +=  car['setTo'] + ',' \
                            + car[PSE.SB.handleGetMessage('Road')] + ',' \
                            + car[PSE.SB.handleGetMessage('Number')] + ',' \
                            + car[PSE.SB.handleGetMessage('Type')] + ',' \
                            + car[PSE.SB.handleGetMessage('Length')] + ',' \
                            + car[PSE.SB.handleGetMessage('Weight')] + ',' \
                            + car[PSE.SB.handleGetMessage('Load')] + ',' \
                            + car[PSE.SB.handleGetMessage('Load_Type')] + ',' \
                            + str(car[PSE.SB.handleGetMessage('Hazardous')]) + ',' \
                            + car[PSE.SB.handleGetMessage('Color')] + ',' \
                            + car[PSE.SB.handleGetMessage('Kernel')] + ',' \
                            + car[PSE.SB.handleGetMessage('Kernel_Size')] + ',' \
                            + car[PSE.SB.handleGetMessage('Owner')] + ',' \
                            + car[PSE.SB.handleGetMessage('Track')] + ',' \
                            + car[PSE.SB.handleGetMessage('Division')] + ',' \
                            + car[PSE.SB.handleGetMessage('Location')] + ',' \
                            + car[PSE.SB.handleGetMessage('Destination')] + ',' \
                            + car[PSE.SB.handleGetMessage('Dest&Track')] + ',' \
                            + car[PSE.SB.handleGetMessage('Final_Dest')] + ',' \
                            + car[PSE.SB.handleGetMessage('FD&Track')] + ',' \
                            + car[PSE.SB.handleGetMessage('Comment')] + ',' \
                            + car[PSE.SB.handleGetMessage('SetOut_Msg')] + ',' \
                            + car[PSE.SB.handleGetMessage('PickUp_Msg')] + ',' \
                            + car[PSE.SB.handleGetMessage('RWE')] \
                            + '\n'

    return trackPatternCsv

# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from copy import deepcopy

from opsEntities import PSE
from Subroutines.Patterns import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.PT.Model')

def initializeSubroutine():
    """
    After the subroutine is built, set it to its' initial values.
    """

    configFile = PSE.readConfigFile()

    divComboBox = divComboUpdater()
    divComboBox.setSelectedItem(configFile['Patterns']['PD'])

    locComboBox = locComboUpdater()
    locComboBox.setSelectedItem(configFile['Patterns']['PL'])

    trackRowManager()

    return
    
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

def refreshSubroutine():
    """
    Called from PSE.remoteCalls('refreshCalls')
    """

    return

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

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    component = PSE.getComponentByName(frame, 'jLocations')
    component.removeAllItems()
    component.addItem(None)
    for locationName in PSE.getLocationNamesByDivision():
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

def trackRowManager():
    """
    Creates a row of check boxes, one for each track.
    If no tracks for the selected location, displays a message.
    """

    _psLog.debug('trackRowManager')

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
    
def insertStandins(trackPattern):
    """
    Substitutes in standins from the config file.
    """

    standins = PSE.readConfigFile('Patterns')['RM']

    tracks = trackPattern['tracks']
    for track in tracks:
        for loco in track['locos']:
            destStandin, fdStandin = getStandins(loco, standins)
            loco.update({'destination': destStandin})

        for car in track['cars']:
            destStandin, fdStandin = getStandins(car, standins)
            car.update({'destination': destStandin})
            car.update({'finalDest': fdStandin})
            shortLoadType = PSE.getShortLoadType(car)
            car.update({'loadType': shortLoadType})

    return trackPattern

def getStandins(rs, standins):
    """
    Replaces null destination and fd with the standin from the configFile
    Called by:
    insertStandins
    """

    destStandin = rs['destination']
    if not rs['destination']:
        destStandin = standins['DS']

    try: # No FD for locos
        fdStandin = rs['finalDest']
        if not rs['finalDest']:
            fdStandin = standins['FD']
    except:
        fdStandin = standins['FD']

    return destStandin, fdStandin

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
    reportHeader['railroadName'] = PSE.getExtendedRailroadName()
    reportHeader['railroadDescription'] = configFile['Patterns']['RD']
    reportHeader['trainName'] = configFile['Patterns']['TN']
    reportHeader['trainDescription'] = configFile['Patterns']['TD']
    reportHeader['trainComment'] = configFile['Patterns']['TC']
    reportHeader['division'] = configFile['Patterns']['PD']
    reportHeader['date'] = unicode(PSE.validTime(), PSE.ENCODING)
    reportHeader['location'] = configFile['Patterns']['PL']

    return reportHeader

def makeReportTracks(selectedTracks):
    """
    Tracks is a list of dictionaries.
    """

    return ModelEntities.getDetailsForTracks(selectedTracks)

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
    workList['tracks'] = []

    fileName = PSE.getBundleItem('ops-switch-list') + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    workList = PSE.dumpJson(workList)
    PSE.genericWriteReport(targetPath, workList)

    return

def getReportForPrint(reportName):
    """
    Mini controller.
    Formats and displays the Track Pattern or Switch List report.
    Called by:
    Controller.StartUp.patternReportButton
    ControllerSetCarsForm.CreateSetCarsFrame.switchListButton
    """

    _psLog.debug('getReportForPrint')

    report = getReport(reportName)

    reportForPrint = makePatternReportForPrint(report)

    targetPath = writeReportForPrint(reportName, reportForPrint)

    PSE.genericDisplayReport(targetPath)

    return

def getReport(reportName):
    
    fileName = reportName + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    report = PSE.genericReadReport(targetPath)

    return PSE.loadJson(report)

def makePatternReportForPrint(trackPattern):

    trackPattern = insertStandins(trackPattern)
    reportHeader = ModelEntities.makeTextReportHeader(trackPattern)
    reportLocations = PSE.getBundleItem('Pattern Report for Tracks') + '\n\n'
    reportLocations += ModelEntities.makeTextReportTracks(trackPattern['tracks'], trackTotals=True)

    return reportHeader + reportLocations

def writeReportForPrint(reportName, report):

    fileName = reportName + '.txt'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', fileName)
    PSE.genericWriteReport(targetPath, report)

    return targetPath

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

    trackPatternCsv = u'Operator,Description,Parameters\n'
    trackPatternCsv += u'RT,Report Type,' + trackPattern['trainDescription'] + '\n'
    trackPatternCsv += u'RD,Railroad Division,' + str(trackPattern['division']) + '\n'
    trackPatternCsv += u'LN,Location Name,' + trackPattern['location'] + '\n'
    trackPatternCsv += u'PRNTR,Printer Name,\n'
    trackPatternCsv += u'YPC,Yard Pattern Comment,' + trackPattern['trainComment'] + '\n'
    trackPatternCsv += u'VT,Valid,' + trackPattern['date'] + '\n'
    trackPatternCsv += 'SE,Set Engines\n'
    trackPatternCsv += u'setTo,Road,Number,Type,Model,Length,Weight,Consist,Owner,Track,Location,Destination,Comment\n'
    for track in trackPattern['tracks']:
        try:
            trackPatternCsv += u'TN,Track name,' + unicode(track['trackName'], PSE.ENCODING) + '\n'
        except:
            print('Exception at: Patterns.View.makeTrackPatternCsv')
            pass
        for loco in track['locos']:
            trackPatternCsv +=  loco['setTo'] + ',' \
                            + loco['road'] + ',' \
                            + loco['number'] + ',' \
                            + loco['carType'] + ',' \
                            + loco['model'] + ',' \
                            + loco['length'] + ',' \
                            + loco['weight'] + ',' \
                            + loco['consist'] + ',' \
                            + loco['owner'] + ',' \
                            + loco['track'] + ',' \
                            + loco['location'] + ',' \
                            + loco['destination'] + ',' \
                            + loco['comment'] + ',' \
                            + '\n'
    trackPatternCsv += 'SC,Set Cars\n'
    trackPatternCsv += u'setTo,Road,Number,Type,Length,Weight,Load,Load_Type,Hazardous,Color,Kernel,Kernel_Size,Owner,Track,Location,Destination,dest&Track,Final_Dest,fd&Track,Comment,Drop_Comment,Pickup_Comment,RWE\n'
    for track in trackPattern['tracks']:
        try:
            trackPatternCsv += u'TN,Track name,' + unicode(track['trackName'], PSE.ENCODING) + '\n'
        except:
            print('Exception at: Patterns.View.makeTrackPatternCsv')
            pass
        for car in track['cars']:
            trackPatternCsv +=  car['setTo'] + ',' \
                            + car['road'] + ',' \
                            + car['number'] + ',' \
                            + car['carType'] + ',' \
                            + car['length'] + ',' \
                            + car['weight'] + ',' \
                            + car['load'] + ',' \
                            + car['loadType'] + ',' \
                            + str(car['hazardous']) + ',' \
                            + car['color'] + ',' \
                            + car['kernel'] + ',' \
                            + car['kernelSize'] + ',' \
                            + car['owner'] + ',' \
                            + car['track'] + ',' \
                            + car['location'] + ',' \
                            + car['destination'] + ',' \
                            + car['dest&Track'] + ',' \
                            + car['finalDest'] + ',' \
                            + car['fd&Track'] + ',' \
                            + car['comment'] + ',' \
                            + car['setOutMsg'] + ',' \
                            + car['pickupMsg'] + ',' \
                            + car['rwe'] \
                            + '\n'

    return trackPatternCsv

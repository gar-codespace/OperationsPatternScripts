# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from copy import deepcopy

from opsEntities import PSE
from Subroutines.Patterns import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

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
    """

    return

def refreshSubroutine():
    """
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

    standins = PSE.readConfigFile('Patterns')['US']

    tracks = trackPattern['tracks']
    for track in tracks:
        for loco in track['locos']:
            destination = loco[PSE.SB.handleGetMessage('Destination')]
            if not destination:
                destination = extendedDestionationHandling(loco, standins)

            loco.update({PSE.SB.handleGetMessage('Destination'): destination})

        for car in track['cars']:
            destination = car[PSE.SB.handleGetMessage('Destination')]
            finalDestination = car[PSE.SB.handleGetMessage('Final_Dest')]

            if not destination:
                destination = extendedDestionationHandling(car, standins)

            if not finalDestination:
                finalDestination = extendedFinalDestionationHandling(car, standins)

            shortLoadType = PSE.getShortLoadType(car)

            car.update({PSE.SB.handleGetMessage('Destination'): destination})
            car.update({PSE.SB.handleGetMessage('Final_Dest'): finalDestination})
            car.update({PSE.SB.handleGetMessage('Load_Type'): shortLoadType})

    return trackPattern

def extendedDestionationHandling(rs, standins):
    """
    Special case handling foe Engine, Caboose, and Passenger.
    """

    destination = standins['DS']
    if rs['isEngine']:
        destination = standins['EH']

    if rs['isCaboose']:
        destination = standins['EH']

    if rs['isPassenger']:
        destination = standins['EH']

    return destination

def extendedFinalDestionationHandling(rs, standins):
    """
    Special case handling foe Engine, Caboose, and Passenger.
    """

    finalDestination = standins['DS']
    if rs['isEngine']:
        pass

    if rs['isCaboose']:
        finalDestination = standins['EH']

    if rs['isPassenger']:
        finalDestination = standins['EH']

    return finalDestination

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
    trackPatternCsv += u'setTo,Road,Number,Type,Length,Weight,Load,Load_Type,Hazardous,Color,Kernel,Kernel_Size,Owner,Track,Location,Destination,dest&Track,Final_Dest,fd&Track,Comment,Drop_Comment,Pickup_Comment,RWE\n'
    for track in trackPattern['tracks']:
        try:
            trackPatternCsv += u'TN,Track name,' + unicode(track['trackName'], PSE.ENCODING) + '\n'
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

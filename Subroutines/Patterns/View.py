# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from opsEntities import PSE
from Subroutines.Patterns import Model
from Subroutines.Patterns import SetCarsForm_Controller
from Subroutines.Patterns import GUI

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.PT.View')

class ManageGui:

    def __init__(self):

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the Track Pattern controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the Track Pattern panel
        subroutineFrame.setName(__package__)
        subroutineFrame.setLayout(PSE.JAVX_SWING.BoxLayout(
                subroutineFrame, PSE.JAVX_SWING.BoxLayout.Y_AXIS))
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Patterns Subroutine'))

        return subroutineFrame

    def makeSubroutineGui(self):
        """Make the Patterns GUI."""

        _psLog.debug('PatternTracksSubroutine.View.makeSubroutineGui')

        subroutineGui = GUI.subroutineGui()
        gui = subroutineGui.guiMaker()
        widgets = subroutineGui.guiWidgetGetter()

        return gui, widgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))
    

def patternReport():
    """
    Mini controller when the Track Pattern Report button is pressed.
    Reformats and displays the Track Pattern Report.
    Called by:
    Controller.StartUp.patternReportButton
    """

    _psLog.debug('trackPatternButton')

# Get the report
    reportName = PSE.getBundleItem('ops-pattern-report')    
    fileName = reportName + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    trackPattern = PSE.genericReadReport(targetPath)
    trackPattern = PSE.loadJson(trackPattern)
# Modify the report for display
    PSE.makeReportItemWidthMatrix()
    trackPattern = modifyTrackPatternReport(trackPattern)
    reportHeader = makeTextReportHeader(trackPattern)
    reportLocations = PSE.getBundleItem('Pattern Report for Tracks') + '\n\n'

    reportLocations += makeTextReportLocations(trackPattern, trackTotals=True)
# Save the modified report
    fileName = reportName + '.txt'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', fileName)
    PSE.genericWriteReport(targetPath, reportHeader + reportLocations)
# Display the modified report
    PSE.genericDisplayReport(targetPath)

    return

def trackPatternAsCsv():
    """
    ops-pattern-report.json is written as a CSV file
    Called by:
    Controller.StartUp.trackPatternButton
    """

    _psLog.debug('trackPatternAsCsv')

    if not PSE.JMRI.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled():
        return
#  Get json data
    fileName = PSE.getBundleItem('ops-pattern-report')+ '.json'    

    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    trackPatternCsv = PSE.genericReadReport(targetPath)
    trackPatternCsv = PSE.loadJson(trackPatternCsv)
# Process json data into CSV
    trackPatternCsv = makeTrackPatternCsv(trackPatternCsv)
# Write CSV data
    fileName = PSE.getBundleItem('ops-pattern-report') + '.csv'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'csvSwitchLists', fileName)
    PSE.genericWriteReport(targetPath, trackPatternCsv)

    return
    
def setCarsToTrack(trackCheckBoxes):
    """"Set Cars to Track button opens a window for each selected track."""

    _psLog.debug('setCarsToTrack')

    patternLocation = PSE.readConfigFile('Patterns')['PL']
    PSE.makeReportItemWidthMatrix()

    selectedTracks = [trackCheckBox for trackCheckBox in trackCheckBoxes if trackCheckBox.selected]
    windowOffset = 200
    i = 0
    for trackCheckBox in selectedTracks:
        trackPatternBody = Model.makeTrackPatternBody([trackCheckBox])
        setCarsForm = Model.makeTrackPatternReport(trackPatternBody)
    # Apply common formatting to report
        setCarsForm = modifyTrackPatternReport(setCarsForm)

        newFrame = SetCarsForm_Controller.CreateSetCarsForm(setCarsForm)
        newWindow = newFrame.makeFrame()
        newWindow.setTitle(PSE.getBundleItem('Set Rolling Stock for track:') + ' ' + trackCheckBox.text)
        newWindow.setName('setCarsWindow')
        newWindow.pack()

        newWidth = newWindow.getWidth()
        if newWidth > 800:
            newWidth = 800

        newHeight = newWindow.getHeight()
        if newHeight > 800:
            newHeight = 800

        newDimension = PSE.JAVA_AWT.Dimension(newWidth, newHeight)
        newWindow.setSize(newDimension)
        newWindow.setLocation(windowOffset, 100)
        newWindow.setVisible(True)

        windowOffset += 50
        i += 1

        _psLog.info(u'Set Rolling Stock Window created for track ' + trackCheckBox.text)

    _psLog.info(str(i) + ' Set Rolling Stock windows for ' + patternLocation + ' created')

    return

def modifyTrackPatternReport(trackPattern):
    """Modifies the track pattern report for the Set Cars window."""

    standins = PSE.readConfigFile('Patterns')['RM']

    tracks = trackPattern['locations'][0]['tracks']
    for track in tracks:
        for loco in track['locos']:
            destStandin, fdStandin = getStandins(loco, standins)
            loco.update({'Destination': destStandin})

        for car in track['cars']:
            destStandin, fdStandin = getStandins(car, standins)
            car.update({'Destination': destStandin})
            car.update({'Final Dest': fdStandin})
            shortLoadType = PSE.getShortLoadType(car)
            car.update({'Load Type': shortLoadType})

    return trackPattern

def getStandins(car, standins):
    """
    Replaces null destination and fd with the standin from the configFile
    Called by:
    modifyTrackPatternReport
    """

    destStandin = car['Destination']
    if not car['Destination']:
        destStandin = standins['DS']

    try: # No FD for locos
        fdStandin = car['Final Dest']
        if not car['Final Dest']:
            fdStandin = standins['FD']
    except:
        print('Exception at: Patterns.View.getStandins')
        fdStandin = ''

    return destStandin, fdStandin
    
def makeTextReportHeader(textWorkEventList):
    """
    Makes the header for generic text reports
    Called by:
    View.ManageGui.trackPatternButton'
    ViewSetCarsForm.switchListButton
    """

    patternLocation = PSE.readConfigFile('Patterns')['PL']
    divisionName = textWorkEventList['division']
    workLocation = ''
    if divisionName:
        workLocation = divisionName + ' - ' + patternLocation
    else:
        workLocation = patternLocation

    textReportHeader    = textWorkEventList['railroadName'] + '\n\n' + PSE.getBundleItem('Work Location:') + ' ' + workLocation + '\n' + textWorkEventList['date'] + '\n\n'
    
    return textReportHeader

def makeTextReportLocations(textWorkEventList, trackTotals):
    """
    Makes the body for generic text reports
    Called by:
    View.ManageGui.trackPatternButton'
    ViewSetCarsForm.switchListButton
    """

    reportSwitchList = ''
    reportTally = [] # running total for all tracks
    for track in textWorkEventList['locations'][0]['tracks']:
        lengthOfLocos = 0
        lengthOfCars = 0
        trackTally = []
        trackName = track['trackName']
        trackLength = track['length']
        reportSwitchList += PSE.getBundleItem('Track:') + ' ' + trackName + '\n'

        for loco in track['locos']:
            lengthOfLocos += int(loco['Length']) + 4
            reportSwitchList += loco['Set_To'] + loopThroughRs('loco', loco) + '\n'

        for car in track['cars']:
            lengthOfCars += int(car['Length']) + 4
            reportSwitchList += car['Set_To'] + loopThroughRs('car', car) + '\n'
            trackTally.append(car['Final Dest'])
            reportTally.append(car['Final Dest'])

        if trackTotals:
            totalLength = lengthOfLocos + lengthOfCars
            reportSwitchList += PSE.getBundleItem('Total Cars:') + ' ' \
                + str(len(track['cars'])) + ' ' + PSE.getBundleItem('Track Length:')  + ' ' \
                + str(trackLength) +  ' ' + PSE.getBundleItem('Eqpt. Length:')  + ' ' \
                + str(totalLength) + ' ' +  PSE.getBundleItem('Available:') + ' '  \
                + str(trackLength - totalLength) \
                + '\n\n'
            reportSwitchList += PSE.getBundleItem('Track Totals for Cars:') + '\n'
            for track, count in sorted(PSE.occuranceTally(trackTally).items()):
                reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
        reportSwitchList += '\n'

    if trackTotals:
        reportSwitchList += '\n' + PSE.getBundleItem('Report Totals for Cars:') + '\n'
        for track, count in sorted(PSE.occuranceTally(reportTally).items()):
            reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'

    return reportSwitchList

def loopThroughRs(type, rsAttribs):
    """
    Creates a line containing the attrs in get * MessageFormat
    Called by:
    makeTextReportLocations
    """

    reportWidth = PSE.REPORT_ITEM_WIDTH_MATRIX
    switchListRow = ''
    rosetta = PSE.translateMessageFormat()

    if type == 'loco':
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    if type == 'car':
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    for lookup in messageFormat:
        item = rosetta[lookup]

        if 'Tab' in item:
            continue

        itemWidth = reportWidth[item]
        switchListRow += PSE.formatText(rsAttribs[item], itemWidth)

    return switchListRow

def makeTrackPatternCsv(trackPattern):
    """
    The double quote for the railroadName entry is added to keep the j Pluse extended data intact.
    CSV writer does not support utf-8.
    Called by:
    Model.writeTrackPatternCsv
    """

    trackPatternCsv = u'Operator,Description,Parameters\n' \
                    u'RT,Report Type,' + trackPattern['trainDescription'] + '\n' \
                    u'RN,Railroad Name,"' + trackPattern['railroadName'] + '"\n' \
                    u'RD,Railroad Division,"' + trackPattern['division'] + '"\n' \
                    u'LN,Location Name,' + trackPattern['locations'][0]['locationName'] + '\n' \
                    u'PRNTR,Printer Name,\n' \
                    u'YPC,Yard Pattern Comment,' + trackPattern['trainComment'] + '\n' \
                    u'VT,Valid,' + trackPattern['date'] + '\n'
    trackPatternCsv += 'SE,Set Engines\n'
    trackPatternCsv += u'Set_To,Road,Number,Type,Model,Length,Weight,Consist,Owner,Track,Location,Destination,Comment\n'
    for track in trackPattern['locations'][0]['tracks']: # There is only one location
        try:
            trackPatternCsv += u'TN,Track name,' + unicode(track['trackName'], PSE.ENCODING) + '\n'
        except:
            print('Exception at: Patterns.View.makeTrackPatternCsv')
            pass
        for loco in track['locos']:
            trackPatternCsv +=  loco['Set_To'] + ',' \
                            + loco['Road'] + ',' \
                            + loco['Number'] + ',' \
                            + loco['Type'] + ',' \
                            + loco['Model'] + ',' \
                            + loco['Length'] + ',' \
                            + loco['Weight'] + ',' \
                            + loco['Consist'] + ',' \
                            + loco['Owner'] + ',' \
                            + loco['Track'] + ',' \
                            + loco['Location'] + ',' \
                            + loco['Destination'] + ',' \
                            + loco['Comment'] + ',' \
                            + '\n'
    trackPatternCsv += 'SC,Set Cars\n'
    trackPatternCsv += u'Set_To,Road,Number,Type,Length,Weight,Load,Load_Type,Hazardous,Color,Kernel,Kernel_Size,Owner,Track,Location,Destination,Dest&Track,Final_Dest,FD&Track,Comment,Drop_Comment,Pickup_Comment,RWE\n'
    for track in trackPattern['locations'][0]['tracks']: # There is only one location
        try:
            trackPatternCsv += u'TN,Track name,' + unicode(track['trackName'], PSE.ENCODING) + '\n'
        except:
            print('Exception at: Patterns.View.makeTrackPatternCsv')
            pass
        for car in track['cars']:
            trackPatternCsv +=  car['Set_To'] + ',' \
                            + car['Road'] + ',' \
                            + car['Number'] + ',' \
                            + car['Type'] + ',' \
                            + car['Length'] + ',' \
                            + car['Weight'] + ',' \
                            + car['Load'] + ',' \
                            + car['Load Type'] + ',' \
                            + str(car['Hazardous']) + ',' \
                            + car['Color'] + ',' \
                            + car['Kernel'] + ',' \
                            + car['Kernel Size'] + ',' \
                            + car['Owner'] + ',' \
                            + car['Track'] + ',' \
                            + car['Location'] + ',' \
                            + car['Destination'] + ',' \
                            + car['Dest&Track'] + ',' \
                            + car['Final Dest'] + ',' \
                            + car['FD&Track'] + ',' \
                            + car['Comment'] + ',' \
                            + car['SetOut Msg'] + ',' \
                            + car['PickUp Msg'] + ',' \
                            + car['RWE'] \
                            + '\n'

    return trackPatternCsv

# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE
from PatternTracksSubroutine import ModelEntities
from PatternTracksSubroutine import ViewEntities
from PatternTracksSubroutine import ControllerSetCarsForm

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.View'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.PT.View')

class ManageGui:

    def __init__(self):

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the Track Pattern controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the Track Pattern panel
        subroutineFrame.setName(u'PatternTracksSubroutine')
        subroutineFrame.setLayout(PSE.JAVX_SWING.BoxLayout(
                subroutineFrame, PSE.JAVX_SWING.BoxLayout.Y_AXIS))
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder( \
                PSE.BUNDLE['Track Pattern Subroutine'] \
                )

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the Track Pattern controls"""

        _psLog.debug('makeSubroutinePanel')

        trackPatternPanel = ViewEntities.TrackPatternPanel()
        subroutinesPanel = trackPatternPanel.makeTrackPatternPanel()
        subroutinePanelWidgets = trackPatternPanel.getPanelWidgets()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

def trackPatternButton():
    """Mini controller when the Track Pattern Report button is pressed.
        Reformats and displays the Track Pattern Report.
        Used by:
        Controller.StartUp.trackPatternButton
        """

    _psLog.debug('trackPatternButton')
# Boilerplate
    reportName = PSE.BUNDLE['Track Pattern Report']
    fileName = reportName + '.json'
    # targetDir = PSE.PROFILE_PATH + 'operations\\jsonManifests'
    targetPath = PSE.OS_Path.join(PSE.PROFILE_PATH, 'operations\\jsonManifests', fileName)
# Get the report
    trackPattern = PSE.genericReadReport(targetPath)
    trackPattern = PSE.loadJson(trackPattern)
# Modify the report for display
    trackPattern = ViewEntities.modifyTrackPatternReport(trackPattern)
    reportHeader = ViewEntities.makeTextReportHeader(trackPattern)
    reportLocations = ViewEntities.makeTextReportLocations(trackPattern, trackTotals=True)
# Save the modified report
    fileName = reportName + '.txt'
    # targetDir = PSE.PROFILE_PATH + 'operations\\patternReports'
    targetPath = PSE.OS_Path.join(PSE.PROFILE_PATH, 'operations\\patternReports', fileName)
    PSE.genericWriteReport(targetPath, reportHeader + reportLocations)
# Display the modified report
    PSE.genericDisplayReport(targetPath)

    return

def setRsButton():
    """"Set Cars to Track button opens a window for each selected track"""

    _psLog.debug('setRsButton')

    selectedTracks = PSE.getSelectedTracks()
    if not selectedTracks:
        _psLog.warning('No tracks were selected for the Set Cars button')

        return

    locationName = PSE.readConfigFile('PT')['PL']
    windowOffset = 200
    for i, trackName in enumerate(selectedTracks, start=1):
        trackPattern = ModelEntities.makeTrackPattern([trackName]) # makeTrackPattern takes a track list
        setCarsForm = ModelEntities.makeTrackPatternReport(trackPattern)
    # Apply common formatting to report
        setCarsForm = ViewEntities.modifyTrackPatternReport(setCarsForm)

        newFrame = ControllerSetCarsForm.CreateSetCarsFormGui(setCarsForm)
        newWindow = newFrame.makeFrame()
        newWindow.setTitle(PSE.BUNDLE['Set Rolling Stock for track:'] + ' ' + trackName)
        newWindow.setName('setCarsWindow')
        newWindow.setLocation(windowOffset, 180)
        newWindow.pack()
        newWindow.setVisible(True)

        _psLog.info(u'Set Rolling Stock Window created for track ' + trackName)
        windowOffset += 50
    _psLog.info(str(i) + ' Set Rolling Stock windows for ' + locationName + ' created')

    return

def trackPatternAsCsv():
    """Track Pattern Report json is written as a CSV file
        Used by:
        Controller.StartUp.trackPatternButton
        """

    _psLog.debug('trackPatternAsCsv')
#  Get json data
    fileName = PSE.BUNDLE['Track Pattern Report'] + '.json'
    targetPath = PSE.OS_Path.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    trackPatternCsv = PSE.genericReadReport(targetPath)
    trackPatternCsv = PSE.loadJson(trackPatternCsv)
# Process json data into CSV
    trackPatternCsv = ViewEntities.makeTrackPatternCsv(trackPatternCsv)
# Write CSV data
    fileName = PSE.BUNDLE['Track Pattern Report'] + '.csv'
    targetPath = PSE.OS_Path.join(PSE.PROFILE_PATH, 'operations', 'csvSwitchLists', fileName)
    PSE.genericWriteReport(targetPath, trackPatternCsv)

    return

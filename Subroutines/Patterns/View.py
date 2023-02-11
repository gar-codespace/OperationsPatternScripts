# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from opsEntities import PSE
from Subroutines.Patterns import Model
from Subroutines.Patterns import ViewEntities
from Subroutines.Patterns import ControllerSetCarsForm

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
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder( \
                PSE.BUNDLE['Patterns Subroutine'] \
                )

        return subroutineFrame

    def makeSubroutineGui(self):
        """Make the Patterns GUI."""

        _psLog.debug('PatternTracksSubroutine.View.makeSubroutineGui')

        subroutineGui = ViewEntities.subroutineGui()
        gui = subroutineGui.guiMaker()
        widgets = subroutineGui.guiWidgetGetter()

        return gui, widgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))


def patternReport():
    """Mini controller when the Track Pattern Report button is pressed.
        Reformats and displays the Track Pattern Report.
        Called by:
        Controller.StartUp.patternReportButton
        """

    _psLog.debug('trackPatternButton')

# Get the report
    reportName = PSE.BUNDLE['ops-pattern-report']
    fileName = reportName + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    trackPattern = PSE.genericReadReport(targetPath)
    trackPattern = PSE.loadJson(trackPattern)
# Modify the report for display
    PSE.REPORT_ITEM_WIDTH_MATRIX = ViewEntities.makeReportItemWidthMatrix()
    trackPattern = ViewEntities.modifyTrackPatternReport(trackPattern)
    reportHeader = ViewEntities.makeTextReportHeader(trackPattern)
    reportLocations = PSE.BUNDLE['Pattern Report for Tracks'] + '\n\n'
    reportLocations += ViewEntities.makeTextReportLocations(trackPattern, trackTotals=True)
# Save the modified report
    fileName = reportName + '.txt'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', fileName)
    PSE.genericWriteReport(targetPath, reportHeader + reportLocations)
# Display the modified report
    PSE.genericDisplayReport(targetPath)

    return

def setRollingStock():
    """"Set Cars to Track button opens a window for each selected track"""

    _psLog.debug('setRsButton')

    selectedTracks = Model.getSelectedTracks()
    if not selectedTracks:
        _psLog.warning('No tracks were selected for the Set Cars button')

        return

    PSE.REPORT_ITEM_WIDTH_MATRIX = ViewEntities.makeReportItemWidthMatrix()
    locationName = PSE.readConfigFile('Patterns')['PL']
    windowOffset = 200
    for i, trackName in enumerate(selectedTracks, start=1):
        trackPattern = Model.makeTrackPattern([trackName]) # makeTrackPattern takes a track list
        setCarsForm = Model.makeTrackPatternReport(trackPattern)
    # Apply common formatting to report
        setCarsForm = ViewEntities.modifyTrackPatternReport(setCarsForm)

        newFrame = ControllerSetCarsForm.CreateSetCarsFormGui(setCarsForm)
        newWindow = newFrame.makeFrame()
        newWindow.setTitle(PSE.BUNDLE['Set Rolling Stock for track:'] + ' ' + trackName)
        newWindow.setName('setCarsWindow')
        newWindow.setLocation(windowOffset, 180)
        newWindow.pack()
        newWindow.setVisible(True)
        windowOffset += 50

        _psLog.info(u'Set Rolling Stock Window created for track ' + trackName)

    _psLog.info(str(i) + ' Set Rolling Stock windows for ' + locationName + ' created')

    return

def trackPatternAsCsv():
    """Track Pattern Report json is written as a CSV file
        Called by:
        Controller.StartUp.trackPatternButton
        """

    _psLog.debug('trackPatternAsCsv')
#  Get json data
    fileName = PSE.BUNDLE['ops-pattern-report'] + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    trackPatternCsv = PSE.genericReadReport(targetPath)
    trackPatternCsv = PSE.loadJson(trackPatternCsv)
# Process json data into CSV
    trackPatternCsv = ViewEntities.makeTrackPatternCsv(trackPatternCsv)
# Write CSV data
    fileName = PSE.BUNDLE['ops-pattern-report'] + '.csv'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'csvSwitchLists', fileName)
    PSE.genericWriteReport(targetPath, trackPatternCsv)

    return

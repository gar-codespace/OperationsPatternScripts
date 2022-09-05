# coding=utf-8
# © 2021, 2022 Greg Ritacco

from PatternTracksSubroutine import Model
from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ModelEntities
from PatternTracksSubroutine import ViewEntities
from PatternTracksSubroutine import ControllerSetCarsForm

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.View'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.View')

class ManageGui:

    def __init__(self):

        # self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.View')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the Track Pattern controls are added to"""

        subroutineFrame = PatternScriptEntities.JAVX_SWING.JPanel() # the Track Pattern panel
        subroutineFrame.setLayout(PatternScriptEntities.JAVX_SWING.BoxLayout(
                subroutineFrame, PatternScriptEntities.JAVX_SWING.BoxLayout.Y_AXIS))
        subroutineFrame.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createTitledBorder( \
                PatternScriptEntities.BUNDLE['Track Pattern Subroutine'] \
                )

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the Track Pattern controls"""

        _psLog.debug('View.makeSubroutinePanel')

        trackPatternPanel = ViewEntities.TrackPatternPanel()
        subroutinesPanel = trackPatternPanel.makeTrackPatternPanel()
        subroutinePanelWidgets = trackPatternPanel.getPanelWidgets()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

def trackPatternButton():
    """Mini controller when the Track Pattern Report button is pressed
        Formats and displays the Track Pattern Report
        """

    _psLog.debug('View.trackPatternButton')

    workEventName = PatternScriptEntities.BUNDLE['Track Pattern Report']
# Apply formatting to data
    workEvents = PatternScriptEntities.readJsonWorkEventList(workEventName)
    reportHeader = ViewEntities.makeTextReportHeader(workEvents)
    reportLocations = ViewEntities.makeTextReportLocations(workEvents, trackTotals=True)
# Save formatted data
    workEventPath = PatternScriptEntities.PROFILE_PATH + 'operations\\patternReports\\' + workEventName + '.txt'
    PatternScriptEntities.genericWriteReport(workEventPath, reportHeader + reportLocations)
# Display formatted data
    PatternScriptEntities.genericDisplayReport(workEventPath)

    return

def setCarsButton():
    """"Set Cars to Track button opens a window for each selected track"""

    _psLog.debug('setCarsButton')

    selectedTracks = PatternScriptEntities.getSelectedTracks()
    if not selectedTracks:
        _psLog.warning('No tracks were selected for the Set Cars button')

        return

    locationName = PatternScriptEntities.readConfigFile('PT')['PL']
    windowOffset = 200
    for i, trackName in enumerate(selectedTracks, start=1):
        locationDict = ModelEntities.makeLocationDict([trackName]) # makeLocationDict takes a track list
        setCarsForm = ModelEntities.makeReport(locationDict, 'SC')
        
        newFrame = ControllerSetCarsForm.CreateSetCarsFormGui(setCarsForm)
        newWindow = newFrame.makeFrame()
        newWindow.setTitle(PatternScriptEntities.BUNDLE['Set Cars Form for track:'] + ' ' + trackName)
        newWindow.setName('setCarsWindow')
        newWindow.setLocation(windowOffset, 180)
        newWindow.pack()
        newWindow.setVisible(True)

        _psLog.info(u'Set Cars Window created for track ' + trackName)
        windowOffset += 50
    _psLog.info(str(i) + ' Set Cars windows for ' + locationName + ' created')

    return

# coding=utf-8
# © 2021, 2022 Greg Ritacco

import jmri
import java.awt

import logging
from os import system as osSystem

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import Model
from PatternTracksSubroutine import ModelSetCarsForm
from PatternTracksSubroutine import ViewSetCarsForm

"""Makes a 'Set Cars Form for Track X' form for each selected track"""

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ControllerSetCarsForm'
SCRIPT_REV = 20220101

_trackNameClickedOn = None

class TextBoxEntryListener(java.awt.event.MouseAdapter):
    """When any of the 'Set Cars Form for Track X' text inpou boxes is clicked on"""

    def __init__(self):
        self.psLog = logging.getLogger('PS.PT.TextBoxEntryListener')

        return

    def mouseClicked(self, MOUSE_CLICKED):

        if _trackNameClickedOn:
            MOUSE_CLICKED.getSource().setText(_trackNameClickedOn)
        else:
            self.psLog.warning('No track was selected')

        return

class CreatePatternReportGui:
    """Creates an instance of each 'Set Cars Form for Track X' window,
    [0] is used to avoid for-loops since there is only 1 location and track
    """

    def __init__(self, setCarsForm):

        self.psLog = logging.getLogger('PS.PT.CreatePatternReportGui')

        self.setCarsForm = setCarsForm
        self.locationName = setCarsForm['locations'][0]['locationName']
        self.trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
        self.buttonDict = {}

        return

    def makeFrame(self):
        """Create a JMRI jFrame window"""

        setCarsForTrackForm, self.buttonDict = ViewSetCarsForm.makeSetCarsForTrackForm(self.setCarsForm)
        setCarsForTrackWindow = ViewSetCarsForm.setCarsForTrackWindow(setCarsForTrackForm)
        self.activateButtons()

        return setCarsForTrackWindow

    def activateButtons(self):

        for track in self.buttonDict['trackButtons']:
            track.actionPerformed = self.trackRowButton

        for inputText in self.buttonDict['textBoxEntry']:
            inputText.addMouseListener(TextBoxEntryListener())

        try:
            self.buttonDict['scheduleButton'][0].actionPerformed = self.scheduleButton
        except IndexError:
            pass

        self.buttonDict['footerButtons'][0].actionPerformed = self.printButton
        self.buttonDict['footerButtons'][1].actionPerformed = self.setButton
        try:
            self.buttonDict['footerButtons'][2].actionPerformed = self.trainPlayerButton
        except IndexError:
            pass

        return

    def quickCheck(self):

        if not ModelSetCarsForm.testValidityOfForm(self.setCarsForm, self.buttonDict['textBoxEntry']):
            self.psLog.critical('FAIL - ModelSetCarsForm.testValidityOfForm')
            return False
        else:
            self.psLog.info('PASS - ModelSetCarsForm.testValidityOfForm')
            return True

    def trackRowButton(self, MOUSE_CLICKED):
        """Any button of the 'Set Cars Form for Track X' - row of track buttons"""

        _trackNameClickedOn = unicode(MOUSE_CLICKED.getSource().getText(), PatternScriptEntities.ENCODING)
        global _trackNameClickedOn

        return

    def scheduleButton(self, MOUSE_CLICKED):
        """The named schedule button if displayed on any 'Set Cars Form for Track X' window"""

        scheduleName = MOUSE_CLICKED.getSource().getText()
        schedule = PatternScriptEntities.SM.getScheduleByName(scheduleName)
        track = PatternScriptEntities.LM.getLocationByName(self.locationName).getTrackByName(self.trackName, None)
        jmri.jmrit.operations.locations.schedules.ScheduleEditFrame(schedule, track)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def printButton(self, MOUSE_CLICKED):
        """Makes a Set Cars (SC) switch list for the
        active 'Set Cars Form for Track X' window
        """

        if not self.quickCheck():
            return

        locationDict = ModelSetCarsForm.makeLocationDict( \
                self.setCarsForm, self.buttonDict['textBoxEntry'] \
                ) # Replaces [Hold] with a track name

        modifiedReport = Model.makeReport(locationDict, 'SC')

        workEventName, textListForPrint = Model.makeWorkEventList(modifiedReport, trackTotals=False)
        workEventPath = PatternScriptEntities.writeGenericReport(workEventName, textListForPrint)
        osSystem(PatternScriptEntities.openEditorByComputerType(workEventPath))

        if jmri.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled():
            Model.writeCsvSwitchList(modifiedReport, 'SC')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def setButton(self, MOUSE_CLICKED):
        """Event that moves cars to the tracks entered in the text box of
        the 'Set Cars Form for Track X' form
        """

        if not self.quickCheck():
            return

        ModelSetCarsForm.setRsToTrack(self.setCarsForm, self.buttonDict['textBoxEntry'])

        setCarsWindow = MOUSE_CLICKED.getSource().getTopLevelAncestor()
        setCarsWindow.setVisible(False)
        setCarsWindow.dispose()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def trainPlayerButton(self, MOUSE_CLICKED):
        """Accumulate switch lists into one TrainPlayer switch list"""

        if not self.quickCheck():
            return

        MOUSE_CLICKED.getSource().setBackground(java.awt.Color.GREEN)

        ModelSetCarsForm.exportSetCarsFormToTp(self.setCarsForm, self.buttonDict['textBoxEntry'])

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

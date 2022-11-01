# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Makes a 'Set Cars Form for Track X' form for each selected track"""

from opsEntities import PSE
from opsEntities import Listeners
from PatternTracksSubroutine import Model
from PatternTracksSubroutine import ModelSetCarsForm
from PatternTracksSubroutine import ViewSetCarsForm
from o2oSubroutine import Controller as o2oController

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ControllerSetCarsForm'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.PT.ControllerSetCarsForm')


class CreateSetCarsFormGui:
    """Creates an instance of each 'Set Cars Form for Track X' window,
        [0] is used to avoid for-loops since there is only 1 location and track
        """

    def __init__(self, setCarsForm):

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
            inputText.addMouseListener(Listeners.TextBoxEntry())

        try:
            self.buttonDict['scheduleButton'][0].actionPerformed = self.scheduleButton
        except IndexError:
            pass

        self.buttonDict['footerButtons'][0].actionPerformed = self.switchListButton
        self.buttonDict['footerButtons'][1].actionPerformed = self.setRsButton
        try:
            self.buttonDict['footerButtons'][2].actionPerformed = self.o2oButton
        except IndexError:
            pass

        return

    def quickCheck(self):

        if not ModelSetCarsForm.testValidityOfForm(self.setCarsForm, self.buttonDict['textBoxEntry']):
            _psLog.critical('FAIL - CreateSetCarsFormGui.quickCheck.testValidityOfForm')
            PSE.openOutputPanel(PSE.BUNDLE['FAIL: CreateSetCarsFormGui.quickCheck.testValidityOfForm'])
            return False
        else:
            _psLog.info('PASS - testValidityOfForm')
            return True

    def trackRowButton(self, MOUSE_CLICKED):
        """Any button of the 'Set Cars Form for Track X' - row of track buttons"""

        PSE.TRACK_NAME_CLICKED_ON = unicode(MOUSE_CLICKED.getSource().getText(), PSE.ENCODING)

        return

    def scheduleButton(self, MOUSE_CLICKED):
        """The named schedule button if displayed for the active 'Set Cars Form for Track X' window"""

        scheduleName = MOUSE_CLICKED.getSource().getText()
        schedule = PSE.SM.getScheduleByName(scheduleName)
        track = PSE.LM.getLocationByName(self.locationName).getTrackByName(self.trackName, None)
        PSE.JMRI.jmrit.operations.locations.schedules.ScheduleEditFrame(schedule, track)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def switchListButton(self, MOUSE_CLICKED):
        """Makes a Set Cars (SC) switch list for the active 'Set Rolling Stock for Track X' window"""

        _psLog.info(MOUSE_CLICKED)

        if not self.quickCheck():
            return

        PSE.REPORT_ITEM_WIDTH_MATRIX = PSE.makeReportItemWidthMatrix()

        ModelSetCarsForm.writeToJson(self.setCarsForm)
    # Modify and disply the set cars form
        ViewSetCarsForm.switchListButton(self.buttonDict['textBoxEntry'])

        if PSE.JMRI.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled():
            ViewSetCarsForm.switchListAsCsv(self.buttonDict['textBoxEntry'])

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def setRsButton(self, MOUSE_CLICKED):
        """Event that moves cars to the tracks entered in the text box of
            the 'Set Cars Form for Track X' form.
            """

        _psLog.debug(MOUSE_CLICKED)

        if not self.quickCheck():
            return

        PSE.REPORT_ITEM_WIDTH_MATRIX = PSE.makeReportItemWidthMatrix()

        ModelSetCarsForm.writeToJson(self.setCarsForm)
    # Set the cars to the selected tracks
        ModelSetCarsForm.setRsButton(self.buttonDict['textBoxEntry'])

        setCarsWindow = MOUSE_CLICKED.getSource().getTopLevelAncestor()
        setCarsWindow.setVisible(False)
        setCarsWindow.dispose()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def o2oButton(self, MOUSE_CLICKED):
        """Creates the o2oSetCarsForm data and sends it to o2o for processing."""

        _psLog.info(MOUSE_CLICKED)

        if not self.quickCheck():
            return

        MOUSE_CLICKED.getSource().setBackground(PSE.JAVA_AWT.Color.GREEN)

        o2oSetCarsForm = ModelSetCarsForm.makeMergedForm(self.setCarsForm, self.buttonDict['textBoxEntry'])

        o2oController.o2oSwitchList(o2oSetCarsForm)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

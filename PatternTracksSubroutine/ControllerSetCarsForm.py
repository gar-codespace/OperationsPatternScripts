# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Makes a 'Set Cars Form for Track X' form for each selected track"""

from opsEntities import PSE
from PatternTracksSubroutine import Model
from PatternTracksSubroutine import ModelSetCarsForm
from PatternTracksSubroutine import ViewSetCarsForm
from o2oSubroutine import ModelWorkEvents

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ControllerSetCarsForm'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.PT.ControllerSetCarsForm')

class TextBoxEntryListener(PSE.JAVA_AWT.event.MouseAdapter):
    """When any of the 'Set Cars Form for Track X' text inpou boxes is clicked on"""

    def __init__(self):

        return

    def mouseClicked(self, MOUSE_CLICKED):

        if PSE.TRACK_NAME_CLICKED_ON:
            MOUSE_CLICKED.getSource().setText(PSE.TRACK_NAME_CLICKED_ON)
        else:
            _psLog.warning('No track was selected')

        return

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
            inputText.addMouseListener(TextBoxEntryListener())

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
            _psLog.critical('FAIL - testValidityOfForm')
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
            workEventName = PSE.BUNDLE['Switch List for Track']
            Model.writeTrackPatternCsv(workEventName)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def setRsButton(self, MOUSE_CLICKED):
        """Event that moves cars to the tracks entered in the text box of
            the 'Set Cars Form for Track X' form
            """

        _psLog.info(MOUSE_CLICKED)

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
        """Accumulate switch lists into the o2o-Work-Events switch list
            List is reset when set cars button on Track Pattern Sub is pressed
            """

        _psLog.info(MOUSE_CLICKED)

        if not self.quickCheck():
            return

        MOUSE_CLICKED.getSource().setBackground(PSE.JAVA_AWT.Color.GREEN)

    # Format for display and replace Set_To for the setCarsForm
        ptSetCarsForm = ViewSetCarsForm.o2oButton(self.setCarsForm, self.buttonDict['textBoxEntry'])
    # Append the ptSetCarsForm to the o2oSwitchList
        ModelSetCarsForm.o2oButton(ptSetCarsForm)
    # Convert the o2o switch list to the format used by o2oSubroutine
        o2o = ModelWorkEvents.o2oSwitchListConversion()
        o2o.o2oSwitchListGetter()
        o2o.thinTheHerd()
        o2o.o2oSwitchListUpdater()
        o2oSwitchList = o2o.getO2oSwitchList()
    # Common post processor for o2oButton and BuiltTrainExport.o2oWorkEventsBuilder.handle
        o2o = ModelWorkEvents.o2oWorkEvents(o2oSwitchList)
        o2o.o2oHeader()
        o2o.o2oLocations()
        o2o.saveList()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

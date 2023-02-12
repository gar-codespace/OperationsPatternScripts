# coding=utf-8
# © 2023 Greg Ritacco

"""
Makes a 'Set Cars Form for Track X' form for each selected track.
"""

from opsEntities import PSE
from Subroutines.Patterns import Listeners
from Subroutines.Patterns import Model
from Subroutines.Patterns import ModelSetCarsForm
from Subroutines.Patterns import ViewSetCarsForm

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

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

        return

    def quickCheck(self):

        if not ModelSetCarsForm.testValidityOfForm(self.setCarsForm, self.buttonDict['textBoxEntry']):
            _psLog.critical('FAIL - CreateSetCarsFormGui.quickCheck.testValidityOfForm')
            PSE.openOutputFrame(PSE.BUNDLE['FAIL: CreateSetCarsFormGui.quickCheck.testValidityOfForm'])
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

        _psLog.debug(MOUSE_CLICKED)

        if not self.quickCheck():
            return

    # Make the json file
        mergedForm = ModelSetCarsForm.makeMergedForm(self.setCarsForm, self.buttonDict['textBoxEntry'])
        reportTitle = PSE.BUNDLE['ops-switch-list']
        fileName = reportTitle + '.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchLists', fileName)
        switchListReport = PSE.dumpJson(mergedForm)
        PSE.genericWriteReport(targetPath, switchListReport)

        switchList = ViewSetCarsForm.maksSwitchList()

        Model.appendWorkList(mergedForm)

        MOUSE_CLICKED.getSource().setBackground(PSE.JAVA_AWT.Color.GREEN)
        PSE.remoteCalls('specificCalls')
        
    # Save formatted data
        fileName = PSE.BUNDLE['ops-switch-list'] + '.txt'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchLists', fileName)
        PSE.genericWriteReport(targetPath, switchList)
    # Display formatted data
        PSE.genericDisplayReport(targetPath)

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
    # Make the json file
        mergedForm = ModelSetCarsForm.makeMergedForm(self.setCarsForm, self.buttonDict['textBoxEntry'])
        reportTitle = PSE.BUNDLE['ops-switch-list']
        fileName = reportTitle + '.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchLists', fileName)
        switchListReport = PSE.dumpJson(mergedForm)
        PSE.genericWriteReport(targetPath, switchListReport)
    # Open the pop up window
        PSE.closeOpsWindows('popupFrame')
        popupFrame, popupWidgets = ViewSetCarsForm.setCarsPopup()
        popupFrame.setLocation(MOUSE_CLICKED.getSource().getParent().getLocationOnScreen())
        popupFrame.setVisible(True)        

        for widget in popupWidgets:
            widget.actionPerformed = getattr(self, widget.getName())

        self.setCarsWindow = MOUSE_CLICKED.getSource().getTopLevelAncestor()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def asCheckBox(self, EVENT):
        """The Apply Schedule check box."""

        configFile = PSE.readConfigFile()

        if EVENT.getSource().selected:
            configFile['Patterns'].update({'AS':True})
        else:
            configFile['Patterns'].update({'AS':False})

        PSE.writeConfigFile(configFile)

        return

    def itlCheckBox(self,EVENT):
        """The Ignore Track Length checkbox."""

        configFile = PSE.readConfigFile()

        if EVENT.getSource().selected:
            configFile['Patterns'].update({'PI':True})
        else:
            configFile['Patterns'].update({'PI':False})

        PSE.writeConfigFile(configFile)

        return

    def setCarsButton(self, MOUSE_CLICKED):

        ModelSetCarsForm.setRsToTrack()

        popupWindow = MOUSE_CLICKED.getSource().getTopLevelAncestor()
        popupWindow.setVisible(False)
        popupWindow.dispose()

        self.setCarsWindow.setVisible(False)
        self.setCarsWindow.dispose()

        return

    def cancelButton(self, MOUSE_CLICKED):

        popupWindow = MOUSE_CLICKED.getSource().getTopLevelAncestor()
        popupWindow.setVisible(False)
        popupWindow.dispose()

        return


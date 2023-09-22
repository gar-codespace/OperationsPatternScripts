# coding=utf-8
# © 2023 Greg Ritacco

"""
Makes a 'Set Cars Form for Track X' form for each selected track.
"""

from opsEntities import PSE
from Subroutines_Activated.Patterns import Model
from Subroutines_Activated.Patterns import SetCarsForm_Model
from Subroutines_Activated.Patterns import SetCarsForm_View
from Subroutines_Activated.Patterns import Listeners

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.PT.ControllerSetCarsForm')


class CreateSetCarsFrame:
    """
    Creates an instance of each 'Set Cars Form for Track X' window.
    """

    def __init__(self, selectedTrack):

        self.header = Model.makeReportHeader()
        self.track = Model.makeReportTracks([selectedTrack])

        self.locationName = self.header['location']
        self.trackName = selectedTrack

        self.setCarsForm = {}
        self.setCarsTracks = {}
        self.buttonDict = {}
        self.mergedForm = {}

        self.makeForm()

        return

    def makeForm(self):

        self.setCarsForm = self.header

        self.setCarsForm['tracks'] = [self.track][0]
        self.setCarsForm = Model.insertStandins(self.setCarsForm)

        return
    
    def makeFrame(self):

        setCarsFrame = SetCarsForm_View.ManageSetCarsGui(self.setCarsForm)
        setCarsFrame.makeSetCarsFrame()

        setCarsForTrackWindow = setCarsFrame.getSetCarsForTrackWindow()

        setCarsForTrackWindow.setTitle(PSE.getBundleItem('Set Rolling Stock for track:') + ' ' + self.track[0]['trackName'])
        setCarsForTrackWindow.setName('setCarsWindow')
        setCarsForTrackWindow.pack()

        self.buttonDict = setCarsFrame.getButtonDict()

        self.activateButtons()

        return setCarsForTrackWindow

    def activateButtons(self):

        for track in self.buttonDict['trackButtons']:
            track.actionPerformed = self.trackRowButton

        for inputText in self.buttonDict['textBoxEntry']:
            inputText.addMouseListener(Listeners.TextBoxEntry())

        try:
            self.buttonDict['scheduleButton'].actionPerformed = self.scheduleButton
        except:
            print('No schedule or schedule not found for this track.')

        self.buttonDict['footerButtons'][0].actionPerformed = self.switchListButton
        self.buttonDict['footerButtons'][1].actionPerformed = self.setRsButton

        return

    def quickCheck(self):

        if SetCarsForm_Model.formIsValid(self.setCarsForm, self.buttonDict['textBoxEntry']):
            _psLog.info('PASS - form validated')
            return True
        else:
            _psLog.critical('FAIL - CreateSetCarsFrame.quickCheck.formIsValid')
            PSE.openOutputFrame(PSE.getBundleItem('FAIL: CreateSetCarsFrame.quickCheck.formIsValid'))            
            return False

    def trackRowButton(self, MOUSE_CLICKED):
        """Any button of the 'Set Cars Form for Track X' - row of track buttons"""

        PSE.TRACK_NAME_CLICKED_ON = unicode(MOUSE_CLICKED.getSource().getText(), PSE.ENCODING)

        return

    def scheduleButton(self, MOUSE_CLICKED):
        """The schedule button if displayed for the active 'Set Cars Form for Track X' window."""

        scheduleName = MOUSE_CLICKED.getSource().getText()
        schedule = PSE.SM.getScheduleByName(scheduleName)
        track = PSE.LM.getLocationByName(self.locationName).getTrackByName(self.trackName, None)
        scheduleEditFrame = PSE.JMRI.jmrit.operations.locations.schedules.ScheduleEditFrame(schedule, track)

        PSE.LM.addPropertyChangeListener(PSE.ListenToThePSWindow(scheduleEditFrame))

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def switchListButton(self, MOUSE_CLICKED):
        """Makes a Set Cars (SC) switch list for the active 'Set Rolling Stock for Track X' window."""

        _psLog.debug(MOUSE_CLICKED)

        if not self.quickCheck():
            return

        mergedForm = SetCarsForm_Model.makeMergedForm(self.setCarsForm, self.buttonDict['textBoxEntry'])

        SetCarsForm_Model.appendSwitchList(mergedForm)

        reportName = PSE.getBundleItem('ops-switch-list')
        Model.getReportForPrint(reportName)
        Model.trackPatternAsCsv(reportName)

        MOUSE_CLICKED.getSource().setBackground(PSE.JAVA_AWT.Color.GREEN)
    # Plays well with others
        PSE.TM.firePropertyChange('patternsSwitchList', False, True)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def setRsButton(self, MOUSE_CLICKED):
        """
        Event that moves cars to the tracks entered in the text box of
        the 'Set Cars Form for Track X' form.
        """

        _psLog.debug(MOUSE_CLICKED)

        if not self.quickCheck():
            return

        self.mergedForm = SetCarsForm_Model.makeMergedForm(self.setCarsForm, self.buttonDict['textBoxEntry'])

    # Open the pop up window
        PSE.closeWindowByName('popupFrame')

        popup = SetCarsForm_View.ManagePopUp()
        popupFrame = popup.getPopupFrame()
        popupFrame.setLocation(MOUSE_CLICKED.getSource().getParent().getLocationOnScreen())
        popupFrame.setVisible(True)        

        for widget in popup.getPopupWidgets():
            widget.actionPerformed = getattr(self, widget.getName())

        PSE.LM.addPropertyChangeListener(PSE.ListenToThePSWindow(popupFrame))

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

        SetCarsForm_Model.moveRollingStock(self.mergedForm)

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

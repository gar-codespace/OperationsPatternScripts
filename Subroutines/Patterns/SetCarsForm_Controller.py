# coding=utf-8
# © 2023 Greg Ritacco

"""
Makes a 'Set Cars Form for Track X' form for each selected track.
"""

from opsEntities import PSE
from Subroutines.Patterns import Model
from Subroutines.Patterns import SetCarsForm_Model
from Subroutines.Patterns import SetCarsForm_View
from Subroutines.Patterns import Listeners

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.PT.ControllerSetCarsForm')

class CreateSetCarsForm:
    """
    Creates an instance of each 'Set Cars Form for Track X' window,
    [0] is used to avoid for-loops since there is only 1 location and track
    """

    def __init__(self, setCarsForm):

        self.setCarsForm = setCarsForm
        self.locationName = setCarsForm['locations'][0]['locationName']
        self.trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
        self.buttonDict = {}

        return

    def makeFrame(self):

        setCarsFrame = SetCarsForm_View.ManageSetCarsGui(self.setCarsForm)
        setCarsFrame.makeSetCarsFrame()

        setCarsForTrackWindow = setCarsFrame.getSetCarsForTrackWindow()
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
            print('Exception at: Patterns.Controller.CreateSetCarsForm.activateButtons')
            pass

        self.buttonDict['footerButtons'][0].actionPerformed = self.switchListButton
        self.buttonDict['footerButtons'][1].actionPerformed = self.setRsButton

        return

    def quickCheck(self):

        if SetCarsForm_Model.formIsValid(self.setCarsForm, self.buttonDict['textBoxEntry']):
            _psLog.info('PASS - form validated')
            return True
        else:
            _psLog.critical('FAIL - CreateSetCarsForm.quickCheck.formIsValid')
            PSE.openOutputFrame(PSE.getBundleItem('FAIL: CreateSetCarsForm.quickCheck.formIsValid'))            
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
        PSE.JMRI.jmrit.operations.locations.schedules.ScheduleEditFrame(schedule, track)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def switchListButton(self, MOUSE_CLICKED):
        """Makes a Set Cars (SC) switch list for the active 'Set Rolling Stock for Track X' window."""

        _psLog.debug(MOUSE_CLICKED)

        if not self.quickCheck():
            return

        mergedForm = SetCarsForm_Model.makeMergedForm(self.setCarsForm, self.buttonDict['textBoxEntry'])
        self.jsonSaver(mergedForm)

    # Save the merged form as a text switch list
        switchList = SetCarsForm_Model.makeTextSwitchList(mergedForm)
        fileName = PSE.getBundleItem('ops-switch-list') + '.txt'        
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchLists', fileName)
        PSE.genericWriteReport(targetPath, switchList)
    # Display formatted data
        PSE.genericDisplayReport(targetPath)






        

    # o2o stuff
        Model.appendWorkList(mergedForm)
        PSE.remoteCalls('specificCalls')








        if PSE.JMRI.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled():
            SetCarsForm_Model.switchListAsCsv(self.buttonDict['textBoxEntry'])

        MOUSE_CLICKED.getSource().setBackground(PSE.JAVA_AWT.Color.GREEN)
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

        mergedForm = SetCarsForm_Model.makeMergedForm(self.setCarsForm, self.buttonDict['textBoxEntry'])
        self.jsonSaver(mergedForm)

    # Open the pop up window
        PSE.closeOpsWindows('popupFrame')

        popup = SetCarsForm_View.ManagePopUp()
        popupFrame = popup.getPopupFrame()
        popupWidgets = popup.getPopupWidgets()

        popupFrame.setLocation(MOUSE_CLICKED.getSource().getParent().getLocationOnScreen())
        popupFrame.setVisible(True)        

        for widget in popupWidgets:
            widget.actionPerformed = getattr(self, widget.getName())

        self.setCarsWindow = MOUSE_CLICKED.getSource().getTopLevelAncestor()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def jsonSaver(self, mergedForm):
        """Saves the merged form as a json."""

        reportTitle = PSE.getBundleItem('ops-switch-list')
        fileName = reportTitle + '.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
        switchListReport = PSE.dumpJson(mergedForm)
        PSE.genericWriteReport(targetPath, switchListReport)

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

        SetCarsForm_Model.setRsToTrack()

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

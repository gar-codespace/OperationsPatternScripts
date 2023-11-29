# coding=utf-8
# © 2023 Greg Ritacco

"""
Makes a 'Set Cars Form for Track X' frame for each selected track.
Developers Note:
The Set Cars frame data and switch list json follow the same format as the JMRI json manifest,
with one difference:
With the JMRI json manifest, manifest['locations'] is a list of location dictionaries, IE userName is the name of the location.
With the OPS Set Cars frame and switch list, self.setCarsData['locations'] is a list of track dictionaries, IE userName is the name of the track.
"""

from opsEntities import PSE
from opsEntities import TextReports
from Subroutines_Activated.Patterns import Model
from Subroutines_Activated.Patterns import SetCarsForm_Model
from Subroutines_Activated.Patterns import SetCarsForm_View
from Subroutines_Activated.Patterns import SubroutineListeners

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.PT.ControllerSetCarsForm')

def opsPreProcess(message=None):
    """
    Extends the json files.
    """

    return

def opsProcess(message=None):
    """
    Process the extended json files.
    """

    return

def opsPostProcess(message=None):
    """
    Writes the processed json files to text files.
    """

    textSwitchList = TextReports.opsTextSwitchList()
    targetPath = Model.writePatternReport(textSwitchList, False)
    PSE.genericDisplayReport(targetPath)
    SetCarsForm_Model.switchListAsCsv()

    return


class CreateSetCarsFrame:
    """
    Creates an instance of each 'Set Cars Form for Track X' window.
    self.setCarsForm follows the JMRI json manifest format.
    """

    def __init__(self, selectedTrack):

        self.selectedTrack = selectedTrack
        
        self.setCarsData = Model.getSetCarsData(selectedTrack)

        self.setCarsTracks = {}
        self.buttonDict = {}
        self.mergedForm = {}

        self.makeForm()

        return

    def makeForm(self):

        return
    
    def makeFrame(self):

        setCarsFrame = SetCarsForm_View.ManageSetCarsGui(self.setCarsData)
        setCarsFrame.makeSetCarsFrame()
        setCarsForTrackFrame = setCarsFrame.getSetCarsForTrackFrame()
        setCarsForTrackFrame.setTitle(PSE.getBundleItem('Set Rolling Stock for track: {}').format(self.selectedTrack))
        setCarsForTrackFrame.setName('setCarsWindow')
        setCarsForTrackFrame.pack()

        self.buttonDict = setCarsFrame.getButtonDict()
        self.activateButtons()

        return setCarsForTrackFrame

    def activateButtons(self):

        for track in self.buttonDict['trackButtons']:
            track.actionPerformed = self.trackRowButton

        for inputText in self.buttonDict['textBoxEntry']:
            inputText.addMouseListener(SubroutineListeners.TextBoxEntry())

        try:
            self.buttonDict['scheduleButton'].actionPerformed = self.scheduleButton
        except:
            print('No schedule or schedule not found for this track.')

        self.buttonDict['footerButtons'][0].actionPerformed = self.switchListButton
        self.buttonDict['footerButtons'][1].actionPerformed = self.setRsButton

        return

    def quickCheck(self):

        textBoxLength = len(self.buttonDict['textBoxEntry'])
        carRosterLength = len(self.setCarsData['locations'][0]['cars']['add'])
        locoRosterLength = len(self.setCarsData['locations'][0]['engines']['add'])

        if textBoxLength == locoRosterLength + carRosterLength:
            _psLog.info('PASS - form validated')

            return True
        else:
            _psLog.critical('FAIL - CreateSetCarsFrame.quickCheck.formIsValid')
            PSE.openOutputFrame(PSE.getBundleItem('FAIL: CreateSetCarsFrame.quickCheck.formIsValid'))  

            return False

    def trackRowButton(self, MOUSE_CLICKED):
        """
        Any button of the 'Set Cars Form for Track X' - row of track buttons
        """

        PSE.TRACK_NAME_CLICKED_ON = unicode(MOUSE_CLICKED.getSource().getText(), PSE.ENCODING)

        return

    def scheduleButton(self, MOUSE_CLICKED):
        """
        The schedule button if displayed for the active 'Set Cars Form for Track X' window.
        """

        scheduleName = MOUSE_CLICKED.getSource().getText()
        schedule = PSE.SM.getScheduleByName(scheduleName)

        locationName = PSE.readConfigFile('Patterns')['PL']
        trackName = self.setCarsData['locations'][0]['userName'] 
        track = PSE.LM.getLocationByName(locationName).getTrackByName(trackName, None)
        scheduleEditFrame = PSE.JMRI.jmrit.operations.locations.schedules.ScheduleEditFrame(schedule, track)

        PSE.LM.addPropertyChangeListener(PSE.ListenToThePSWindow(scheduleEditFrame))

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

    def switchListButton(self, MOUSE_CLICKED):
        """
        Makes a Set Cars (SC) switch list for the active 'Set Rolling Stock for Track X' window.
        """

        _psLog.debug(MOUSE_CLICKED)

        if not self.quickCheck():
            return
        
        userInputList = SetCarsForm_Model.getUserInputList(self.buttonDict['textBoxEntry'])
        mergedForm = SetCarsForm_Model.mergeSetCarsForm(self.setCarsData, userInputList)
        SetCarsForm_Model.appendSwitchList(mergedForm) # Write to a file

        # Make a CSV switch list

        PSE.TM.firePropertyChange('opsSwitchList', False, True)

        MOUSE_CLICKED.getSource().setBackground(PSE.JAVA_AWT.Color.GREEN)

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

    def setRsButton(self, MOUSE_CLICKED):
        """
        Event that moves cars to the tracks entered in the text box of
        the 'Set Cars Form for Track X' form.
        """

        _psLog.debug(MOUSE_CLICKED)

        if not self.quickCheck():
            return

        userInputList = SetCarsForm_Model.getUserInputList(self.buttonDict['textBoxEntry'])
        self.mergedForm = SetCarsForm_Model.mergeSetCarsForm(self.setCarsData, userInputList)
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

        return

    def asCheckBox(self, EVENT):
        """
        The Apply Schedule check box.
        """

        configFile = PSE.readConfigFile()

        if EVENT.getSource().selected:
            configFile['Patterns'].update({'AS':True})
        else:
            configFile['Patterns'].update({'AS':False})

        PSE.writeConfigFile(configFile)

        return

    def itlCheckBox(self,EVENT):
        """
        The Ignore Track Length checkbox.
        """

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

        _psLog.info('Set Cars to track')
        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

    def cancelButton(self, MOUSE_CLICKED):

        popupWindow = MOUSE_CLICKED.getSource().getTopLevelAncestor()
        popupWindow.setVisible(False)
        popupWindow.dispose()

        return

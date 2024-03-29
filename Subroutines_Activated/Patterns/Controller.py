# coding=utf-8
# © 2023 Greg Ritacco

"""
The Patterns subroutins is inventory control for any one JMRI location.
Track pattern reports can be run on tracks at the selected location.
Cars can be moved from track to track at the selected location.
This subroutine can be used in conjunction with o2o to create TrainPlayer switch lists.
"""

from opsEntities import PSE
from opsEntities import TextReports
from Subroutines_Activated.Patterns import SetCarsForm_Controller
from Subroutines_Activated.Patterns import Model
from Subroutines_Activated.Patterns import View
from Subroutines_Activated.Patterns import SubroutineListeners

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.PT.Controller')

def getSubroutineDropDownItem():
    """
    Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>
    """

    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    configFile = PSE.readConfigFile()
    if configFile[subroutineName]['SV']:
        menuText = u'{} {}'.format(PSE.getBundleItem('Hide'), __package__)
    else:
        menuText = u'{} {}'.format(PSE.getBundleItem('Show'), __package__)

    menuItem.setName(__package__)
    menuItem.setText(menuText)

    return menuItem


class TrainsPropertyParser:
    """
    What gets called when any of three listeners are fired:
    preProcess, process, postProcess
    """
    
    def __init__(self, pce):

        self.propertySource = pce.source
        self.propertyName = pce.propertyName
        self.oldValue = pce.oldValue
        self.newValue = pce.newValue

        return
    
    def preProcess(self):

        if self.propertyName == 'TrainBuilt' and self.newValue == True:
            if PSE.readConfigFile()['Main Script']['CP']['ER']:
                PSE.extendManifest(self.propertySource) # The train object is passed in

        return
    
    def process(self):

        return
    
    def postProcess(self):

        if self.propertyName == 'opsPatternReport':
            textPatternReport = TextReports.opsTextPatternReport()
            targetPath = Model.writePatternReport(textPatternReport, True)
            PSE.genericDisplayReport(targetPath)
            Model.patternReportAsCsv()

        if self.propertyName == 'opsSwitchList':
            SetCarsForm_Controller.opsPostProcess()

        return


class StartUp:
    """
    Start the Patterns subroutine.
    """

    def __init__(self):

        self.configFile = PSE.readConfigFile()

        return

    def getSubroutine(self):
        """
        Returns the subroutine and activates the widgets.
        """

        subroutine, self.widgets = View.ManageGui().makeSubroutine()
        subroutineName = __package__.split('.')[1]
        subroutine.setVisible(self.configFile[subroutineName]['SV'])
        self.activateWidgets()

        _psLog.info(__package__ + ' makeFrame completed')

        return subroutine

    def startUpTasks(self):
        
        return

    def activateWidgets(self):
        """
        Puts actions on all the widgets that need actions.
        """

        self.widgets[0].addActionListener(SubroutineListeners.DivisionAction())
        self.widgets[1].addActionListener(SubroutineListeners.LocationAction())
        self.widgets[2].actionPerformed = self.yardTrackOnlyCheckBox
        self.widgets[4].actionPerformed = self.patternReportButton
        self.widgets[5].actionPerformed = self.setRsButton

        return

    def yardTrackOnlyCheckBox(self, EVENT):

        _psLog.debug(EVENT)

        configFile = PSE.readConfigFile()     
        configFile['Patterns'].update({'PA': self.widgets[2].selected})
        PSE.writeConfigFile(configFile)

        Model.makeTrackRows()
        
        return

    def patternReportButton(self, EVENT):
        """
        Displays a Pattern Report in a note window.
        """

        _psLog.debug(EVENT)

        configFile = PSE.readConfigFile()
        selectedTracks = [track for track, flag in configFile['Patterns']['PT'].items() if flag]
        selectedTracks.sort()

        Model.makeJsonTrackPattern(selectedTracks) # Write to a file

        PSE.TM.firePropertyChange('opsPatternReport', False, True)

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

    def setRsButton(self, EVENT):
        """
        Opens a "Pattern Report for Track X" window for each checked track.
        """

        _psLog.debug(EVENT)

        configFile = PSE.readConfigFile()
        selectedTracks = [track for track, flag in configFile['Patterns']['PT'].items() if flag]
        selectedTracks.sort()
 
        Model.resetSwitchList()

        windowOffset = 200
        for track in selectedTracks:

            setCarsFrame = SetCarsForm_Controller.CreateSetCarsFrame(track).makeFrame()

            newWidth = min(800, setCarsFrame.getWidth())
            newHeight = min(800, setCarsFrame.getHeight())

            newDimension = PSE.JAVA_AWT.Dimension(newWidth, newHeight)
            setCarsFrame.setSize(newDimension)
            setCarsFrame.setLocation(windowOffset, 100)
            setCarsFrame.setVisible(True)
            
            PSE.LM.addPropertyChangeListener(PSE.ListenToThePSWindow(setCarsFrame))

            windowOffset += 50

            _psLog.info('Set Rolling Stock Window created for track ' + track)

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

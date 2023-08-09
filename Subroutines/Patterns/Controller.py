# coding=utf-8
# © 2023 Greg Ritacco

"""
The Patterns subroutins is inventory control for any one JMRI location.
Yard and track pattern reports can be run on tracks at the selected location.
Cars can be moved from track to track at the selected location.
This subroutine can be used in conjunction with o2o to create TrainPlayer switch lists.
"""

from opsEntities import PSE
from Subroutines.Patterns import Model
from Subroutines.Patterns import View
from Subroutines.Patterns import Listeners
from Subroutines.Patterns import SetCarsForm_Controller

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.PT.Controller')

def getSubroutineDropDownItem():
    """
    Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>
    """

    configFile = PSE.readConfigFile()
    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    if configFile[subroutineName]['SV']:
        menuText = PSE.getBundleItem('Hide') + ' ' + __package__
    else:
        menuText = PSE.getBundleItem('Show') + ' ' + __package__

    menuItem.setName(__package__)
    menuItem.setText(menuText)
    menuItem.removeActionListener(Listeners.actionListener)
    menuItem.addActionListener(Listeners.actionListener)

    return menuItem


class StartUp:
    """
    Start the Patterns subroutine.
    """

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def getSubroutineFrame(self):
        """
        Gets the title border frame.
        """

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutineGui = self.getSubroutineGui()
        self.subroutineFrame.add(subroutineGui)

        _psLog.info('Patterns makeFrame completed')

        return self.subroutineFrame

    def getSubroutineGui(self):
        """
        Gets the GUI for this subroutine.
        """

        # Model.initializeComboBoxes()

        subroutineGui, self.widgets = View.ManageGui().makeSubroutineGui()
        self.activateWidgets()

        return subroutineGui

    def startUpTasks(self):
        """
        Run these tasks when this subroutine is started.
        """

        return

    def activateWidgets(self):
        """
        Puts actions on all the widgets that need actions.
        """

        self.widgets[0].addActionListener(Listeners.DivisionAction()) # Divisions
        self.widgets[1].addActionListener(Listeners.LocationAction()) # Locations
        self.widgets[2].actionPerformed = self.yardTrackOnlyCheckBox
        self.widgets[4].actionPerformed = self.patternReportButton
        self.widgets[5].actionPerformed = self.setRsButton

        return

    def yardTrackOnlyCheckBox(self, EVENT):

        _psLog.debug(EVENT)

        configFile = PSE.readConfigFile()     
        configFile['Patterns'].update({'PA': self.widgets[2].selected})
        PSE.writeConfigFile(configFile)

        PSE.restartSubroutineByName(__package__)
        
        return

    def patternReportButton(self, EVENT):
        """
        Displays a Pattern Report in a note window.
        """

        _psLog.debug(EVENT)

        Model.updateConfigFile(self.widgets)
        selectedTracks = [trackCheckBox.text for trackCheckBox in self.widgets[3] if trackCheckBox.selected]
        selectedTracks.sort()

        PSE.makeReportItemWidthMatrix()

        trackPattern = Model.makeTrackPattern(selectedTracks)
        Model.writePatternReport(trackPattern)

        Model.patternReportForPrint()
        # Model.trackPatternAsCsv()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def setRsButton(self, EVENT):
        """
        Opens a "Pattern Report for Track X" window for each checked track.
        """

        _psLog.debug(EVENT)

        Model.updateConfigFile(self.widgets)
        selectedTracks = [trackCheckBox.text for trackCheckBox in self.widgets[3] if trackCheckBox.selected]
        selectedTracks.sort()
 
        PSE.makeReportItemWidthMatrix()

        Model.resetWorkList()

        windowOffset = 200
        for track in selectedTracks:

            setCarsFrame = SetCarsForm_Controller.CreateSetCarsFrame(track).makeFrame()

            newWidth = setCarsFrame.getWidth()
            if newWidth > 800:
                newWidth = 800

            newHeight = setCarsFrame.getHeight()
            if newHeight > 800:
                newHeight = 800

            newDimension = PSE.JAVA_AWT.Dimension(newWidth, newHeight)
            setCarsFrame.setSize(newDimension)
            setCarsFrame.setLocation(windowOffset, 100)
            setCarsFrame.setVisible(True)

            windowOffset += 50

            _psLog.info(u'Set Rolling Stock Window created for track ' + track)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

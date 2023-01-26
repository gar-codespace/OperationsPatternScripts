# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
The Patterns subroutins is inventory control for a single JMRI location.
Yard and track pattern reports can be run on tracks at one location.
Cars can be moved from track to track at a location.
This subroutine can be used in conjunction with o2o to create TrainPlayer switch lists.
"""

from opsEntities import PSE
from Subroutines.Patterns import Listeners
from Subroutines.Patterns import View
from Subroutines.Patterns import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.PT.Controller')


def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/Subroutines.<subroutine>"""

    patternConfig = PSE.readConfigFile()

    menuItem = PSE.JAVX_SWING.JMenuItem()

    if patternConfig['Main Script']['CP'][__package__]:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
    else:
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__

    menuItem.setName(__package__)
    menuItem.setText(menuText)
    menuItem.removeActionListener(Listeners.actionListener)
    menuItem.addActionListener(Listeners.actionListener)

    PSE.writeConfigFile(patternConfig)

    return menuItem


class StartUp:
    """Start the pattern tracks subroutine"""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        _psLog.info('pattern tracks makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame
            Change this to call widgets by name
            """

        Model.updateLocations()

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def startUpTasks(self):
        """Run these tasks when this subroutine is started."""

        return

    def activateWidgets(self):

        self.widgets[0].addActionListener(Listeners.PTComboBox())
        self.widgets[1].addActionListener(Listeners.PTComboBox())
        self.widgets[2].actionPerformed = self.yardTrackOnlyCheckBox
        self.widgets[4].actionPerformed = self.patternReportButton
        self.widgets[5].actionPerformed = self.setRsButton

        return

    def yardTrackOnlyCheckBox(self, EVENT):

        if self.widgets[2].selected:
            allTracksAtLoc = Model.getTrackNamesByLocation('Yard')
        else:
            allTracksAtLoc = Model.getTrackNamesByLocation(None)

        configFile = PSE.readConfigFile()
        trackDict = Model.updatePatternTracks(allTracksAtLoc)
        configFile['Patterns'].update({'PT': trackDict})
        configFile['Patterns'].update({'PA': self.widgets[2].selected})
        PSE.writeConfigFile(configFile)

        PSE.restartSubroutineByName(__package__)
        
        return

    def patternReportButton(self, EVENT):
        """Makes a pattern tracks report based on the config file (PR)"""

        _psLog.debug(EVENT)

        Model.updateConfigFile(self.widgets)

        if not Model.verifySelectedTracks():
            _psLog.warning('Track not found, re-select the location')
            return

        if not Model.getSelectedTracks():
            _psLog.warning('No tracks were selected for the pattern button')
            return

        Model.patternReport()
        View.patternReport()

        if PSE.JMRI.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled():
            View.trackPatternAsCsv()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def setRsButton(self, EVENT):
        """Opens a "Pattern Report for Track X" window for each checked track
            """

        _psLog.debug(EVENT)

        Model.updateConfigFile(self.widgets)

        Model.newWorkList()

        if not Model.verifySelectedTracks():
            _psLog.warning('Track not found, re-select the location')
            return

        View.setRollingStock()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

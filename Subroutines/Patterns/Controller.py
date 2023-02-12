# coding=utf-8
# © 2023 Greg Ritacco

"""
The Patterns subroutins is inventory control for a single JMRI location.
Yard and track pattern reports can be run on tracks at the selected location.
Cars can be moved from track to track at the selected location.
This subroutine can be used in conjunction with o2o to create TrainPlayer switch lists.
"""

from opsEntities import PSE
from Subroutines.Patterns import Listeners
from Subroutines.Patterns import View
from Subroutines.Patterns import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.PT.Controller')


def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/'Enable or disable' Subroutines.<subroutine>"""

    configFile = PSE.readConfigFile()

    menuItem = PSE.JAVX_SWING.JMenuItem()

    if configFile['Main Script']['CP'][__package__]:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
    else:
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__

    menuItem.setName(__package__)
    menuItem.setText(menuText)
    menuItem.removeActionListener(Listeners.actionListener)
    menuItem.addActionListener(Listeners.actionListener)

    return menuItem


class StartUp:
    """Start the Patterns subroutine"""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def getSubroutineFrame(self):
        """Gets the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutineGui = self.getSubroutineGui()
        self.subroutineFrame.add(subroutineGui)

        _psLog.info('Patterns makeFrame completed')

        return self.subroutineFrame

    def getSubroutineGui(self):
        """Gets the GUI for this subroutine."""

        Model.initializeLocations()

        subroutineGui, self.widgets = View.ManageGui().makeSubroutineGui()
        self.activateWidgets()

        return subroutineGui

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

        _psLog.debug(EVENT)

        configFile = PSE.readConfigFile()     
        configFile['Patterns'].update({'PA': self.widgets[2].selected})
        PSE.writeConfigFile(configFile)

        PSE.restartSubroutineByName(__package__)
        
        return

    def patternReportButton(self, EVENT):
        """Makes a Patterns report based on the config file (PR)"""

        _psLog.debug(EVENT)

        Model.updateConfigFile(self.widgets)

        if not Model.validSelection():
            print('ERROR: re-select the location')
            _psLog.warning('Error, re-select the location')
            return

        Model.patternReport()
        View.patternReport()
        View.trackPatternAsCsv()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def setRsButton(self, EVENT):
        """Opens a "Pattern Report for Track X" window for each checked track
            """

        _psLog.debug(EVENT)

        Model.updateConfigFile(self.widgets)
        Model.newWorkList()

        if not Model.validSelection():
            print('ERROR: re-select the location')
            _psLog.warning('Track not found, re-select the location')
            return

        View.setRollingStock()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

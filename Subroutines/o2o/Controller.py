# coding=utf-8
# © 2023 Greg Ritacco

"""
The o2o Subroutine creates a JMRI railroad from TrainPlayer data.
It also exports a JMRI train's manifest and switch lists from the Patterns subroutine.
On the TrainPlayer side, the Quick Keys suite of scripts is used to import and export the JMRI railroads' data.
"""

from opsEntities import PSE
from Subroutines.o2o import Listeners
from Subroutines.o2o import Model
from Subroutines.o2o import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Controller')


def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>"""

    configFile = PSE.readConfigFile()
    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    if configFile[subroutineName]['SV']:
        menuText = PSE.BUNDLE[u'Hide'] + ' ' + __package__
    else:
        menuText = PSE.BUNDLE[u'Show'] + ' ' + __package__

    menuItem.setName(__package__)
    menuItem.setText(menuText)
    menuItem.removeActionListener(Listeners.actionListener)
    menuItem.addActionListener(Listeners.actionListener)

    PSE.writeConfigFile(configFile)

    return menuItem


class StartUp:
    """Start the o2o subroutine"""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame
        self.configFile = PSE.readConfigFile()

        return

    def getSubroutineFrame(self):
        """Gets the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutineGui = self.getSubroutineGui()
        self.subroutineFrame.add(subroutineGui)

        _psLog.info('o2o makeFrame completed')

        return self.subroutineFrame

    def getSubroutineGui(self):
        """Gets the GUI for this subroutine."""

        subroutineGui, self.widgets = View.ManageGui().makeSubroutineGui()
        self.activateWidgets()

        return subroutineGui

    def startUpTasks(self):
        """Run these tasks when this subroutine is started."""

        return

    def activateWidgets(self):
        """
        The *.getName value is the name of the action for the widget.
        IE: initializeJmriRailroad, updateJmriLocations
        """

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def initializeJmriRailroad(self, EVENT):
        """Creates a new JMRI railroad from the tpRailroadData.json file"""

        _psLog.debug(EVENT)

        if not Model.getTrainPlayerRailroad():
            return
        
        PSE.closeSubordinateWindows(level=1)

        PSE.remoteCalls('resetCalls')
        
        Model.initializeJmriRailroad()

        PSE.restartAllSubroutines()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))
        return

    def updateJmriLocations(self, EVENT):
        """
        Applies changes made to the TrainPlayer/OC/Locations tab.
        """

        _psLog.debug(EVENT)

        if not Model.getTrainPlayerRailroad():
            return

        PSE.closeSubordinateWindows(level=2)

        Model.updateJmriLocations()

        PSE.remoteCalls('refreshCalls')

        PSE.restartAllSubroutines()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateJmriTracks(self, EVENT):
        """
        Applies changes made to the TrainPlayer/OC/Industries tab.
        """

        _psLog.debug(EVENT)

        if not Model.getTrainPlayerRailroad():
            return

        PSE.closeSubordinateWindows(level=2)

        Model.updateJmriTracks()

        PSE.remoteCalls('refreshCalls')

        PSE.restartAllSubroutines()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return
    
    def updateJmriRollingingStock(self, EVENT):
        """Writes new or updated car and engine data."""

        _psLog.debug(EVENT)

        if not Model.getTrainPlayerRailroad():
            return

        PSE.closeSubordinateWindows(level=2)
        
        Model.updateJmriRollingingStock()

        PSE.remoteCalls('refreshCalls')

        PSE.restartAllSubroutines()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

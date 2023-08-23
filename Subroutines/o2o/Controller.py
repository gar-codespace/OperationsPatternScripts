# coding=utf-8
# © 2023 Greg Ritacco

"""
The o2o Subroutine creates a JMRI railroad from TrainPlayer data.
It also exports a JMRI manifest and Patterns switch list into a Quick Keys work events list.
On the TrainPlayer side, the Quick Keys suite of scripts is used to import from and export to the JMRI railroad.
"""

from opsEntities import PSE
from Subroutines.o2o import Listeners
from Subroutines.o2o import Model
from Subroutines.o2o import ModelImport
from Subroutines.o2o import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Controller')

def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>"""

    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    configFile = PSE.readConfigFile()
    if configFile[subroutineName]['SV']:
        menuText = PSE.getBundleItem('Hide') + ' ' + __package__
    else:
        menuText = PSE.getBundleItem('Show') + ' ' + __package__

    menuItem.setName(__package__)
    menuItem.setText(menuText)
    menuItem.addActionListener(Listeners.actionListener)

    return menuItem


class StartUp:
    """Start the o2o subroutine"""

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
        """Run these tasks when this subroutine is started."""

        Listeners.addTrainsTableListener()

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
        """
        Creates a new JMRI railroad from the tpRailroadData.json file
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return
        
        PSE.closeSubordinateWindows(level=1)

        Model.resetBuiltTrains()

        PSE.remoteCalls('resetCalls')

        Model.initializeJmriRailroad()

        PSE.remoteCalls('refreshCalls')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))
        return

    def updateJmriLocations(self, EVENT):
        """
        Applies changes made to the TrainPlayer/OC/Locations tab.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return

        PSE.closeSubordinateWindows(level=2)

        Model.resetBuiltTrains()

        Model.updateJmriLocations()

        PSE.remoteCalls('refreshCalls')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateJmriTracks(self, EVENT):
        """
        Applies changes made to the TrainPlayer/OC/Industries tab.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return

        PSE.closeSubordinateWindows(level=2)

        Model.resetBuiltTrains()

        Model.updateJmriTracks()

        PSE.remoteCalls('refreshCalls')

        # PSE.refreshAllSubroutines()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return
    
    def updateJmriRollingingStock(self, EVENT):
        """
        Writes new or updated car and engine data.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return

        PSE.closeSubordinateWindows(level=2)

        Model.resetBuiltTrains()
        
        Model.updateJmriRollingingStock()

        PSE.remoteCalls('refreshCalls')

        # PSE.refreshAllSubroutines()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateJmriProperties(self, EVENT):
        """
        Writes new or updated extended railroad properties.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return
        
        Model.updateJmriProperties()
        
        PSE.remoteCalls('refreshCalls')

        # PSE.refreshAllSubroutines()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return
    
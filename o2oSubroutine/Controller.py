# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""The o2o Subroutine."""

from psEntities import PSE
from o2oSubroutine import Model
from o2oSubroutine import ModelImport
from o2oSubroutine import ModelUpdate
from o2oSubroutine import View

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.Controller'
SCRIPT_REV = 20220101

class StartUp:
    """Start the o2o subroutine"""

    def __init__(self, subroutineFrame=None):

        self.psLog = PSE.LOGGING.getLogger('PS.TP.Controller')
        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        self.psLog.info('o2o makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame"""

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def activateWidgets(self):
        '''The *.getName value is the name of the action for the widget.
            IE: importTpRailroad, newJmriRailroad, updateRollingStock, updateLocations
            '''

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def importTpRailroad(self, EVENT):
        '''Writes a tpRailroadData.json file from the 3 TrainPlayer report files'''

        ModelImport.importTpRailroad()

        self.psLog.debug(EVENT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def newJmriRailroad(self, EVENT):
        '''Creates a new JMRI railroad from the tpRailroadData.json file'''

        ModelImport.importTpRailroad()
        Model.newJmriRailroad()

        self.psLog.debug(EVENT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateRollingStock(self, EVENT):
        '''Writes a new car and engine xml'''

        ModelImport.importTpRailroad()
        Model.updateRollingStock()

        self.psLog.debug(EVENT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateLocations(self, EVENT):
        '''Writes a new locations xml'''

        ModelImport.importTpRailroad()
        print('updateLocations button pressed')

        self.psLog.debug(EVENT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

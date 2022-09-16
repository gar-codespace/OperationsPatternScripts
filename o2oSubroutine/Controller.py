# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""The o2o Subroutine."""

from psEntities import PSE
from o2oSubroutine import ModelImport
from o2oSubroutine import ModelNew
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
        '''Maybe get them by name?'''

        self.widgets[0].actionPerformed = self.importTpRailroad
        self.widgets[1].actionPerformed = self.newJmriRailroad
        self.widgets[2].actionPerformed = self.updateRollingStock

        return

    def importTpRailroad(self, EVENT):
        '''Writes a tpRailroadData.json file from the 3 TrainPlayer report files'''

        ModelImport.importTpRailroad()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def newJmriRailroad(self, EVENT):
        '''Creates a new JMRI railroad from the tpRailroadData.json file'''

        ModelNew.newJmriRailroad()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateRollingStock(self, EVENT):
        '''Updates JMRI railroad from the json file'''

        ModelUpdate.updateRollingStock()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

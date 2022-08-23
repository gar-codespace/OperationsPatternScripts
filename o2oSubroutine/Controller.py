# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""The TrainPlayer Subroutine will be implemented in V3, this is just the framework"""

from psEntities import PatternScriptEntities
from o2oSubroutine import ModelImport
from o2oSubroutine import ModelNew
from o2oSubroutine import ModelUpdate
from o2oSubroutine import View

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.Controller'
SCRIPT_REV = 20220101

class StartUp:
    """Start the TrainPlayer subroutine"""

    def __init__(self, subroutineFrame=None):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.Controller')
        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        self.psLog.info('TrainPlayer makeFrame completed')

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

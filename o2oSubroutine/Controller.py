# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""The o2o Subroutine."""

from opsEntities import PSE
from PatternTracksSubroutine import Controller
from o2oSubroutine import Model
from o2oSubroutine import ModelImport
from o2oSubroutine import View

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.Controller'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Controller')

class StartUp:
    """Start the o2o subroutine"""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        _psLog.info('o2o makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame"""

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def activateWidgets(self):
        """The *.getName value is the name of the action for the widget.
            IE: newJmriRailroad, updateJmriRailroad
            """

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def newJmriRailroad(self, EVENT):
        '''Creates a new JMRI railroad from the tpRailroadData.json file'''

        _psLog.debug(EVENT)

        if ModelImport.importTpRailroad():
            Model.newJmriRailroad()
        else:
            print('Railroad not imported')

        Controller.updatePatternTracksSubroutine(EVENT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateJmriRailroad(self, EVENT):
        '''Writes a new car and engine xml'''

        _psLog.debug(EVENT)

        if ModelImport.importTpRailroad():
            Model.updateJmriRailroad()
        else:
            print('Railroad not imported')
            
        Controller.updatePatternTracksSubroutine(EVENT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

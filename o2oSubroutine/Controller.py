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
        """Creates a new JMRI railroad from the tpRailroadData.json file"""

        _psLog.debug(EVENT)

        PSE.closeOutputPanel()

        if ModelImport.importTpRailroad():
            print('TrainPlayer railroad data imported OK')
            _psLog.info('TrainPlayer railroad data imported OK')
        else:
            print('TrainPlayer railroad not imported')
            _psLog.critical('TrainPlayer railroad not imported')
            return

        if Model.newJmriRailroad():
            Controller.updatePatternTracksSubroutine(EVENT)
            print('New JMRI railroad built from TrainPlayer data')
            _psLog.info('New JMRI railroad built from TrainPlayer data')
        else:
            print('New JMRI railroad not built')
            _psLog.critical('New JMRI railroad not built')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateJmriRailroad(self, EVENT):
        """Updates the locations data and writes new car and engine data."""

        _psLog.debug(EVENT)

        PSE.closeOutputPanel()

        if ModelImport.importTpRailroad():
            print('TrainPlayer railroad data imported OK')
            _psLog.info('TrainPlayer railroad data imported OK')
        else:
            print('TrainPlayer railroad not imported')
            _psLog.critical('TrainPlayer railroad not imported')
            return

        if Model.updateJmriRailroad():
            Controller.updatePatternTracksSubroutine(EVENT)
            print('JMRI railroad updated from TrainPlayer data')
            _psLog.info('JMRI railroad updated from TrainPlayer data')
        else:
            print('JMRI railroad not updated')
            _psLog.critical('JMRI railroad not updated')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateJmriRollingingStock(self, EVENT):
        """Writes new car and engine data."""

        _psLog.debug(EVENT)

        PSE.closeOutputPanel()

        if ModelImport.importTpRailroad():
            print('TrainPlayer railroad data imported OK')
            _psLog.info('TrainPlayer railroad data imported OK')
        else:
            print('TrainPlayer railroad not imported')
            _psLog.critical('TrainPlayer railroad not imported')
            return

        if Model.updateJmriRollingingStock():
            print('JMRI rolling stock updated')
            _psLog.info('JMRI rolling stock updated')
        else:
            print('JMRI rolling stock not updated')
            _psLog.critical('JMRI rolling stock not updated')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

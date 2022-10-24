# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""This template serves as the framework for additional subroutines."""

from opsEntities import PSE
from GenericSubroutine import Model
from GenericSubroutine import View

SCRIPT_NAME = 'OperationsPatternScripts.GenericSubroutine.Controller'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.GS.Controller')

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

        _psLog.info('GenericSubroutine makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame"""

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def activateWidgets(self):
        """The widget.getName() value is the name of the action for the widget.
            IE 'button'
            """

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def button(self, EVENT):
        '''Whatever it is this button does.'''

        _psLog.debug(EVENT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return
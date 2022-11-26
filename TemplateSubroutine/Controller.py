# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Template
"""

from opsEntities import PSE
from TemplateSubroutine import Model
from TemplateSubroutine import View

SCRIPT_NAME = 'OperationsPatternScripts.TemplateSubroutine.Controller'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.xxx.Controller')


def updateSubroutine(parent):
    """Allows other subroutines to update and restart the jPlus Sub.
        Not implemented.
        """

    if not parent:
        return

    for component in parent.getComponents():
        if component.getName() == 'TemplateSubroutine':
            restartSubroutine(component.getComponents()[0])

    return

def restartSubroutine(subroutineFrame):
    """Subroutine restarter.
        Used by:

        """

    subroutinePanel = StartUp(subroutineFrame).makeSubroutinePanel()
    subroutineFrame.removeAll()
    subroutineFrame.add(subroutinePanel)
    subroutineFrame.revalidate()

    return

def setDropDownText():
    """itemMethod - Set the drop down text per the config file PatternTracksSubroutine Include flag ['CP']['IJ']"""

    patternConfig = PSE.readConfigFile('CP')

    if patternConfig['TemplateSubroutine']:
        menuText = PSE.BUNDLE[u'Disable xxx subroutine']
    else:
        menuText = PSE.BUNDLE[u'Enable xxx subroutine']

    return menuText, 'xxxItemSelected'


class StartUp:
    """Start the xxx subroutine"""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        _psLog.info('xxxSubroutine makeFrame completed')

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

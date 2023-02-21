# coding=utf-8
# © 2023 Greg Ritacco

"""
Template to serve as scaffolding for additional subroutines.
Replace XX with a designator for this subroutines name.
Describe what this subroutine does.

https://stackoverflow.com/questions/301134/how-can-i-import-a-module-dynamically-given-its-name-as-string

"""

from opsEntities import PSE
from Subroutines.Template import Listeners
from Subroutines.Template import Model
from Subroutines.Template import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.XX.Controller')


def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/Subroutines.<subroutine>"""

    configFile = PSE.readConfigFile()

    menuItem = PSE.JAVX_SWING.JMenuItem()

    if configFile['Main Script']['CP'][__package__]:
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
    """Start the subroutine."""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        _psLog.info(__package__ + ' makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame"""

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutineGui()
        self.activateWidgets()

        return self.subroutinePanel

    def startUpTasks(self):
        """Run these tasks when this subroutine is started."""

        return
        
    def activateWidgets(self):
        """The widget.getName() value is the name of the action for the widget.
            IE 'button'
            """

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def button(self, EVENT):
        """Whatever it is this button does."""

        PSE.restartSubroutineByName(__package__)

        _psLog.debug(EVENT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

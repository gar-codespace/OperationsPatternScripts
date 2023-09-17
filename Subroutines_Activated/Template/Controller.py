# coding=utf-8
# © 2023 Greg Ritacco

"""
Template to serve as scaffolding for additional subroutines.
For all the files in this subroutine:
Replace XX with a designator for this subroutines' name.
Replace Template with the name of this subroutine.
Replace this text with a description of what this subroutine does.
"""

from opsEntities import PSE

from Subroutines_Activated.Template import Listeners
from Subroutines_Activated.Template import Model
from Subroutines_Activated.Template import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.XX.Controller')


def getSubroutineDropDownItem():
    """
    Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>
    """

    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    configFile = PSE.readConfigFile()
    if configFile[subroutineName]['SV']:
        menuText = PSE.getBundleItem('Hide') + ' ' + __package__
    else:
        menuText = PSE.getBundleItem('Show') + ' ' + __package__

    menuItem.setName(__package__)
    menuItem.setText(menuText)

    return menuItem


class StartUp:
    """
    Start the subroutine.
    """

    def __init__(self):

        self.configFile = PSE.readConfigFile()

        return

    def getSubroutine(self):
        """
        Gets the title border frame.
        """

        subroutine, self.widgets = View.ManageGui().makeSubroutine()
        subroutineName = __package__.split('.')[1]
        subroutine.setVisible(self.configFile[subroutineName]['SV'])
        self.activateWidgets()

        _psLog.info(__package__ + ' makeFrame completed')

        return subroutine

    def startUpTasks(self):
        """
        Run these tasks when this subroutine is started.
        No GUI items as the GUI is not built yet.
        """

        return
        
    def activateWidgets(self):
        """
        The widget.getName() value is the name of the action for the widget.
        IE 'button'
        """

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def button(self, EVENT):
        """
        Whatever it is this button does.
        """

        Model.refreshSubroutine()

        _psLog.debug(EVENT)

        return

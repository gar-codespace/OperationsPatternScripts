# coding=utf-8
# © 2023 Greg Ritacco

"""
Scanner subroutine
"""

from opsEntities import PSE

from Subroutines_Activated.Scanner import Listeners
from Subroutines_Activated.Scanner import Model
from Subroutines_Activated.Scanner import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.SC.Controller')


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

        # PSE.LM.addPropertyChangeListener(Listeners.ListenToThePSWindow())
        
        return
        
    def activateWidgets(self):
        """
        """

        self.widgets[0].addActionListener(Listeners.DivisionAction())
        self.widgets[1].addActionListener(Listeners.LocationAction())
        self.widgets[2].addActionListener(Listeners.ScannerAction())
        self.widgets[3].actionPerformed = self.scButton
        self.widgets[4].actionPerformed = self.qrButton

        return

    def scButton(self, EVENT):
        """
        """

        _psLog.debug(EVENT)

        return

    def qrButton(self, EVENT):
        """
        """

        _psLog.debug(EVENT)

        return

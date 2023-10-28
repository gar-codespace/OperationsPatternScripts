# coding=utf-8
# © 2023 Greg Ritacco

"""
Scanner subroutine.
Scanner adds a sequence attribute to the cars data set.
This subroutine causes a modified JMRI manifest and
a modified JMRI switch list set to be created.
"""

from opsEntities import PSE

from Subroutines_Activated.Scanner import SubroutineListeners
from Subroutines_Activated.Scanner import Model
from Subroutines_Activated.Scanner import View

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.SC.Controller')


def getSubroutineDropDownItem():
    """
    Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>
    """

    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    configFile = PSE.readConfigFile()
    if configFile[subroutineName]['SV']:
        menuText = '{} {}'.format(PSE.getBundleItem('Hide'), __package__)
    else:
        menuText = '{} {}'.format(PSE.getBundleItem('Show'), __package__)

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

        Model.validateSequenceData()
        
        return
        
    def activateWidgets(self):
        """
        """

        self.widgets[0].actionPerformed = self.qrButton
        self.widgets[1].addActionListener(SubroutineListeners.ScannerSelection())
        self.widgets[2].actionPerformed = self.scButton

        return

    def qrButton(self, EVENT):
        """
        The make QR codes button.
        """

        _psLog.debug(EVENT)

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

    def scButton(self, EVENT):
        """
        The Apply button.
        """

        scannerReportPath = Model.getScannerReportPath()
        if Model.validateScanReport(scannerReportPath):
            Model.applyScanReport(scannerReportPath)

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        _psLog.debug(EVENT)

        return

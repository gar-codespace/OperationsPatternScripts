# coding=utf-8
# © 2023 Greg Ritacco

"""
A simple subroutine to add extended info about a railroad to JMRI.
The info can be input directly or imported from TrainPlayer if using o2o.
This subroutine causes a modified JMRI manifest and
a modified JMRI switch list set to be created.
"""

from opsEntities import PSE

# from Subroutines_Activated.jPlus import SubroutineListeners
from Subroutines_Activated.jPlus import Model
from Subroutines_Activated.jPlus import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.JP.Controller')

def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>"""

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
    Start the jPlus subroutine
    """

    def __init__(self):

        self.configFile = PSE.readConfigFile()

        return

    def getSubroutine(self):
        """
        Returns the subroutine and activates the widgets.
        """

        subroutine, self.widgets = View.ManageGui().makeSubroutine()
        subroutineName = __package__.split('.')[1]
        subroutine.setVisible(self.configFile[subroutineName]['SV'])
        self.activateWidgets()

        _psLog.info(__package__ + ' makeFrame completed')

        return subroutine

    def startUpTasks(self):

        return

    def activateWidgets(self):

        widget = self.widgets['control']['UP']
        widget.actionPerformed = self.update

        widget = self.widgets['control']['UX']
        widget.actionPerformed = self.useExtended

        return

    def update(self, EVENT):
        """
        Update button.
        Writes the text box entries to the configFile.
        Updates JMRI year modeled.
        Sets the jPlus extended header.
        """

        _psLog.debug(EVENT)

        Model.updateRailroadDetails(self.widgets['panel'])
        Model.extendedRailroadDetails()
        Model.pushDetailsToJmri()
        Model.refreshOperationsSettingsFrame()
        Model.refreshSubroutine()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def useExtended(self, EVENT):
        """
        The Use Extended Header checkbox.
        """

        _psLog.debug(EVENT)

        configFile = PSE.readConfigFile()            
        configFile['Main Script']['CP'].update({'EH':EVENT.getSource().selected})
        PSE.writeConfigFile(configFile)

        return
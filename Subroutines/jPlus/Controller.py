# coding=utf-8
# © 2023 Greg Ritacco

"""
A simple subroutine to add extended info about a railroad to JMRI.
The info can be input directly or imported from TrainPlayer if using o2o.
"""

from opsEntities import PSE

from Subroutines.jPlus import Listeners
from Subroutines.jPlus import Model
from Subroutines.jPlus import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

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
    menuItem.removeActionListener(Listeners.actionListener)
    menuItem.addActionListener(Listeners.actionListener)

    return menuItem


class StartUp:
    """
    Start the jPlus subroutine
    """

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def getSubroutineFrame(self):
        """
        Gets the title border frame
        """

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutineGui = self.getSubroutineGui()
        self.subroutineFrame.add(subroutineGui)

        _psLog.info('jPlusSubroutine makeFrame completed')

        return self.subroutineFrame

    def getSubroutineGui(self):
        """
        Gets the GUI for this subroutine.
        """

        subroutineGui, self.widgets = View.ManageGui().makeSubroutineGui()

        self.activateWidgets()

        return subroutineGui

    def startUpTasks(self):
        """
        Run these tasks when this subroutine is started.
        """

        return

    def activateWidgets(self):
        """
        The widget.getName() value is the name of the action for the widget.
        IE 'update'
        """

        widget = self.widgets['control']['UP']
        name = widget.getName()

        widget.actionPerformed = getattr(self, name)

        widget = self.widgets['control']['UX']
        name = widget.getName()

        widget.actionPerformed = getattr(self, name)

        return

    def update(self, EVENT):
        """
        Update button.
        Writes the text box entries to the configFile.
        Updates JMRI year modeled.
        Sets the jPlus expanded header.
        """

        _psLog.debug(EVENT)

        configFile = PSE.readConfigFile()

        Model.updateRailroadDetails(self.widgets['panel'])
        Model.extendedRailroadDetails()

        OSU = PSE.JMRI.jmrit.operations.setup
        OSU.Setup.setYearModeled(configFile['Main Script']['LD']['YR'])

        PSE.remoteCalls('refreshCalls')
        PSE.restartSubroutineByName(__package__)

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

        PSE.remoteCalls('refreshCalls')
        PSE.restartSubroutineByName(__package__)

        return

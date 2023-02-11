# coding=utf-8
# © 2023 Greg Ritacco

"""
A simple subroutine to add extended info about a railroad to JMRI.
The info can be input directly or imported from TrainPlayer.
"""

from opsEntities import PSE

from Subroutines.jPlus import Listeners
from Subroutines.jPlus import Model
from Subroutines.jPlus import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.JP.Controller')

    
def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/'Enable or disable' Subroutines.<subroutine>"""

    configFile = PSE.readConfigFile()

    menuItem = PSE.JAVX_SWING.JMenuItem()

    if configFile['Main Script']['CP'][__package__]:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
    else:
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__

    menuItem.setName(__package__)
    menuItem.setText(menuText)
    menuItem.removeActionListener(Listeners.actionListener)
    menuItem.addActionListener(Listeners.actionListener)

    PSE.writeConfigFile(configFile)

    return menuItem


class StartUp:
    """Start the jPlus subroutine"""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def getSubroutineFrame(self):
        """Gets the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutineGui = self.getSubroutineGui()
        self.subroutineFrame.add(subroutineGui)

        _psLog.info('jPlusSubroutine makeFrame completed')

        return self.subroutineFrame

    def getSubroutineGui(self):
        """Gets the GUI for this subroutine."""

        Model.jPanelSetup()
        subroutineGui, self.widgets = View.ManageGui().makeSubroutineGui()

        self.activateWidgets()

        return subroutineGui

    def startUpTasks(self):
        """Run these tasks when this subroutine is started."""

    # When jPlus is started for the first time
        OSU = PSE.JMRI.jmrit.operations.setup
        configFile = PSE.readConfigFile()
        if configFile['Main Script']['LD']['LN'] == '':
            configFile['Main Script']['LD'].update({'LN':OSU.Setup.getRailroadName()})
            PSE.writeConfigFile(configFile)

        return

    def activateWidgets(self):
        """The widget.getName() value is the name of the action for the widget.
            IE 'update'
            """

        widget = self.widgets['control']['UP']
        name = widget.getName()

        widget.actionPerformed = getattr(self, name)

        return

    def update(self, EVENT):
        '''Update button.
            Writes the text box entries to the configFile.
            Updates JMRI year modeled.
            Sets the jPlus expanded header.
            '''

        _psLog.debug(EVENT)

        configFile = PSE.readConfigFile()
        for id, widget in self.widgets['panel'].items():
            configFile['Main Script']['LD'].update({id:widget.getText()})
        PSE.writeConfigFile(configFile)

        OSU = PSE.JMRI.jmrit.operations.setup
        OSU.Setup.setYearModeled(configFile['Main Script']['LD']['YR'])

        Model.setExpandedHeader()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

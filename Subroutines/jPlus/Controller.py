# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
A simple subroutine to add extra info about a railroad to JMRI.
The info can be input directly or imported from TrainPlayer.
"""

from opsEntities import PSE

from Subroutines.jPlus import Listeners
from Subroutines.jPlus import Model
from Subroutines.jPlus import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.JP.Controller')

    
def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/Subroutines.<subroutine>"""

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
    """Start the o2o subroutine"""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        _psLog.info('jPlusSubroutine makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame"""

        Model.jPanelSetup()
        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()

        try:
            self.activateWidgets()
        except:
            print('j Plus Update button not added')

        return self.subroutinePanel

    def startUpTasks(self):
        """Run these tasks when this subroutine is started."""

    # When jPlus is started for the first time
        OSU = PSE.JMRI.jmrit.operations.setup
        configFile = PSE.readConfigFile()
        if configFile['Main Script']['LD']['LN'] == '':
            configFile['Main Script']['LD'].update({'LN':OSU.Setup.getRailroadName()})


        # self.update('Restart: OperationsPatternScripts.jPlusSubroutine.Controller.StartUp')
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
            '''

        _psLog.debug(EVENT)

        configFile = PSE.readConfigFile()

        for id, widget in self.widgets['panel'].items():
            configFile['Main Script']['LD'].update({id:widget.getText()})

        OSU = PSE.JMRI.jmrit.operations.setup
        OSU.Setup.setYearModeled(configFile['Main Script']['LD']['YR'])

        PSE.writeConfigFile(configFile)

        jPlusHeader = PSE.expandedHeader().replace(';', '\n')
        OSU.Setup.setRailroadName(jPlusHeader)

        PSE.JMRI.jmrit.operations.setup.OperationsSettingsPanel().savePreferences()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

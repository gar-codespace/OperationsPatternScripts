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
    """Pattern Scripts/Tools/<subroutine>"""

    patternConfig = PSE.readConfigFile()

    menuItem = PSE.JAVX_SWING.JMenuItem()

    if patternConfig['Main Script']['CP'][__package__]:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
    else:
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__

    menuItem.setName(__package__)
    menuItem.setText(menuText)
    menuItem.removeActionListener(Listeners.actionListener)
    menuItem.addActionListener(Listeners.actionListener)

    PSE.writeConfigFile(patternConfig)

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

        self.update('Restart: OperationsPatternScripts.jPlusSubroutine.Controller.StartUp')

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
            configFile['jPlus']['LD'].update({id:widget.getText()})

        OSU = PSE.JMRI.jmrit.operations.setup
        OSU.Setup.setYearModeled(configFile['jPlus']['LD']['YR'])

        PSE.writeConfigFile(configFile)

        jPlusHeader = PSE.expandedHeader('jPlus').replace(';', '\n')
        OSU.Setup.setRailroadName(jPlusHeader)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

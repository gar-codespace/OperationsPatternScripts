# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
A simple subroutine to add extra info about a railroad to JMRI.
The info can be input directly or imported from TrainPlayer.
"""

from opsEntities import PSE
# from jPlusSubroutine import Listeners
from jPlusSubroutine import Model
from jPlusSubroutine import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.JP.Controller')


def startDaemons():
    """Methods called when this subroutine is initialized by the Main Script.
        These calls are not turned off.
        """

    return

def activatedCalls():
    """Methods called when this subroutine is activated."""

    return

def deActivatedCalls():
    """Methods called when this subroutine is deactivated."""

    return

def refreshCalls():
    """Methods called when the subroutine needs to be refreshed."""

    PSE.updateYearModeled()
    PSE.restartSubroutineByName('jPlusSubroutine')

    return
    
def setDropDownText():
    """Pattern Scripts/Tools/itemMethod - Set the drop down text per the config file PatternTracksSubroutine Include flag ['CP'][<subroutine name>]"""

    patternConfig = PSE.readConfigFile('CP')
    if patternConfig['jPlusSubroutine']:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
    else:
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__

    return menuText, 'jpItemSelected'


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
            configFile['JP'].update({id:widget.getText()})

        OSU = PSE.JMRI.jmrit.operations.setup
        OSU.Setup.setYearModeled(configFile['JP']['YR'])

        PSE.writeConfigFile(configFile)

        jPlusHeader = PSE.jPlusHeader().replace(';', '\n')
        OSU.Setup.setRailroadName(jPlusHeader)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

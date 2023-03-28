# coding=utf-8
# © 2023 Greg Ritacco

"""
The Throwback subroutine works sort of like version control software.
Commits take a snapshot of the JMRI XML files.
Any or all of the XML files can be 'thrown back' to any one of the commits.
"""

from opsEntities import PSE
from Subroutines.Throwback import Model
from Subroutines.Throwback import View
from Subroutines.Throwback import Listeners

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.TB.Controller')

    
def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>"""

    configFile = PSE.readConfigFile()
    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    if configFile[subroutineName]['SV']:
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
    """Start the Throwback subroutine."""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def getSubroutineFrame(self):
        """Gets the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutineGui = self.getSubroutineGui()
        self.subroutineFrame.add(subroutineGui)

        _psLog.info(__package__ + ' makeFrame completed')

        return self.subroutineFrame

    def getSubroutineGui(self):
        """Gets the GUI for this subroutine."""

        subroutineGui, self.widgets = View.ManageGui().makeSubroutineGui()
        self.activateWidgets()

        return subroutineGui

    def startUpTasks(self):
        """Run these tasks when this subroutine is started."""

        configFile = PSE.readConfigFile()
        if configFile['Main Script']['CP'][__package__]:
            Model.createFolder()
            
        Model.countCommits()

        return

    def activateWidgets(self):
        """
        The widget.getName() value is the name of the action for the widget.
        IE 'commit'
        """

        for widget in self.widgets['control']:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def commit(self, EVENT):
        """Makes a throwback set point."""

        _psLog.debug(EVENT)

        Model.makeCommit(self.widgets['display'])
        Model.countCommits()
        lastSS = PSE.readConfigFile('Throwback')['SS']

        for widget in self.widgets['display']:
            if widget.getName() == 'timeStamp':
                widget.setText(lastSS[-1][0])
            if widget.getName() == 'commitName':
                widget.setText(lastSS[-1][1])
    
        PSE.restartSubroutineByName(__package__)

        return

    def previous(self, EVENT):
        """Move to the previous commit."""

        _psLog.debug(EVENT)

        previousSS = Model.previousCommit()

        for widget in self.widgets['display']:
            if widget.getName() == 'timeStamp':
                widget.setText(previousSS[0])
            if widget.getName() == 'commitName':
                widget.setText(previousSS[1])

        return

    def next(self, EVENT):
        """Move to the next commit."""

        _psLog.debug(EVENT)

        nextSS = Model.nextCommit()

        for widget in self.widgets['display']:
            if widget.getName() == 'timeStamp':
                widget.setText(nextSS[0])
            if widget.getName() == 'commitName':
                widget.setText(nextSS[1])

        return

    def throwback(self, EVENT):
        """Execute a throwback."""

        _psLog.debug(EVENT)

        PSE.remoteCalls('resetCalls')

        Model.throwbackCommit(self.widgets['display'])

        PSE.restartAllSubroutines()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def reset(self, EVENT):
        """Reset throwback."""

        _psLog.debug(EVENT)
        
        Model.resetThrowBack()
        
        PSE.restartSubroutineByName(__package__)

        print('Reset Throwback')

        return

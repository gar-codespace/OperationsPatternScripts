# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
The Throwback subroutine works sort of like version control software.
Commits take a snapshot of the cars and engines XML files.
The cars and engines can be 'thrown back' to any one of the commits.
"""

from opsEntities import PSE
from Subroutines.Throwback import Model
from Subroutines.Throwback import View
from Subroutines.Throwback import Listeners

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.TB.Controller')

    
def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/Subroutines.<subroutine>"""

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
    """Start the subroutine."""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        _psLog.info(__package__ + ' makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame"""

        self.subroutinePanel, self.controlWidgets, self.displayWidgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def startUpTasks(self):
        """Run these tasks when this subroutine is started."""

        Model.countSnapShots()

        return

    def activateWidgets(self):
        """The widget.getName() value is the name of the action for the widget.
            IE 'snapShot'
            """

        for widget in self.controlWidgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def commit(self, EVENT):
        """Makes a throwback set point."""

        _psLog.debug(EVENT)


        Model.takeSnapShot(self.displayWidgets)
        Model.countSnapShots()
        lastSS = PSE.readConfigFile('Throwback')['SS']

        for widget in self.displayWidgets:
            if widget.getName() == 'timeStamp':
                widget.setText(lastSS[-1][0])
            if widget.getName() == 'tbText':
                widget.setText(lastSS[-1][1])
    
        PSE.restartSubroutineByName(__package__)

        return

    def previous(self, EVENT):
        """Move to the previous snapshot."""

        _psLog.debug(EVENT)

        previousSS = Model.previousSnapShot()

        for widget in self.displayWidgets:
            if widget.getName() == 'timeStamp':
                widget.setText(previousSS[0])
            if widget.getName() == 'tbText':
                widget.setText(previousSS[1])

        return

    def next(self, EVENT):
        """Move to the next snapshot."""

        _psLog.debug(EVENT)

        nextSS = Model.nextSnapShot()

        for widget in self.displayWidgets:
            if widget.getName() == 'timeStamp':
                widget.setText(nextSS[0])
            if widget.getName() == 'tbText':
                widget.setText(nextSS[1])

        return

    def throwback(self, EVENT):
        """Execute a throwback."""

        _psLog.debug(EVENT)

        Model.throwbackSnapShot(self.displayWidgets)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def reset(self, EVENT):
        """Reset throwback."""

        _psLog.debug(EVENT)
        
        Model.resetThrowBack()
        
        PSE.restartSubroutineByName(__package__)

        print('Reset Throwback')

        return

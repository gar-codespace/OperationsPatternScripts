# coding=utf-8
# © 2023 Greg Ritacco

"""
The Throwback subroutine works sort of like version control software.
Commits take a snapshot of the JMRI XML files.
Any or all of the XML files can be 'thrown back' to any one of the commits.
"""

from opsEntities import PSE
from Subroutines_Activated.Throwback import Model
from Subroutines_Activated.Throwback import View

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.TB.Controller')

def getSubroutineDropDownItem():
    """
    Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>
    """

    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    configFile = PSE.readConfigFile()
    if configFile[subroutineName]['SV']:
        menuText = u'{} {}'.format(PSE.getBundleItem('Hide'), __package__)
    else:
        menuText = u'{} {}'.format(PSE.getBundleItem('Show'), __package__)

    menuItem.setName(__package__)
    menuItem.setText(menuText)

    return menuItem


class TrainsPropertyParser:
    """
    What gets called when any of three listeners are fired:
    preProcess, process, postProcess
    """
    
    def __init__(self, pce):

        self.propertySource = pce.source
        self.propertyName = pce.propertyName
        # self.oldValue = pce.oldValue
        self.newValue = pce.newValue

        pass
    
    def preProcess(self):

        if self.propertyName == 'TrainBuilt' and self.newValue:
            if PSE.readConfigFile()['Main Script']['CP']['ER']:
                PSE.extendManifest(self.propertySource)

        return
    
    def process(self):

        return
    
    def postProcess(self):

        return


class StartUp:
    """
    Start the Throwback subroutine.
    """

    def __init__(self, subroutineFrame=None):

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
            
        Model.createFolder()
        Model.validateCommits()

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
        """
        Makes a throwback commit TC.
        """

        _psLog.debug(EVENT)

        commitName = self.widgets['display']['tbText'].getText()
        Model.makeCommit(commitName)

        Model.countCommits()
        lastTC = PSE.readConfigFile('Throwback')['TC'][-1]
        self.widgets['display']['timeStamp'].setText(lastTC[0])
        self.widgets['display']['commitName'].setText(lastTC[1])

        return

    def previous(self, EVENT):
        """
        Move to the previous commit.
        """

        _psLog.debug(EVENT)

        previousTC = Model.previousCommit()
        self.widgets['display']['timeStamp'].setText(previousTC[0])
        self.widgets['display']['commitName'].setText(previousTC[1])

        return

    def next(self, EVENT):
        """
        Move to the next commit.
        """

        _psLog.debug(EVENT)

        nextTC = Model.nextCommit()
        self.widgets['display']['timeStamp'].setText(nextTC[0])
        self.widgets['display']['commitName'].setText(nextTC[1])

        return

    def throwback(self, EVENT):
        """
        Execute a throwback.
        """

        _psLog.debug(EVENT)

        Model.throwbackCommit(self.widgets['checkBox'])

        PSE.LM.firePropertyChange('opsRefreshSubroutine', False, True)

        print('{} {}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

    def getWidget(self, name):

        for widget in self.widgets['control']:
            if widget.getName() == name:
                return widget

    def reset(self, EVENT):
        """
        Reset throwback commits.
        """

        firstPress = PSE.getBundleItem('Delete All Commits')
        secondPress = PSE.getBundleItem('Confirm')

        if EVENT.getSource().text == firstPress:
            EVENT.getSource().setText(secondPress)
            self.getWidget('cancel').setVisible(True)
        else:
            Model.resetThrowBack()
            Model.refreshSubroutine()
            EVENT.getSource().setText(firstPress)
            self.getWidget('cancel').setVisible(False)

            _psLog.info('Throwback subroutine reset')          
            print('Throwback subroutine reset')

        return
    
    def cancel(self, EVENT):
        """
        Cancel the reset.
        """

        EVENT.getSource().setVisible(False)
        self.getWidget('reset').setText(PSE.getBundleItem('Delete All Commits'))

        return

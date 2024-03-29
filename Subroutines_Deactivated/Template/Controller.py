# coding=utf-8
# © 2023 Greg Ritacco

"""
Template to serve as scaffolding for additional subroutines.
For all the files in this subroutine:
Replace XX with a designator for this subroutines' name.
Replace Template with the name of this subroutine.
Replace this text with a description of what this subroutine does.
"""

from opsEntities import PSE
from opsEntities import TextReports
from Subroutines_Activated.Template import Model
from Subroutines_Activated.Template import View

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.XX.Controller')


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

        return
    
    def preProcess(self):

        if self.propertyName == 'TrainBuilt' and self.newValue == True:
            if PSE.readConfigFile()['Main Script']['CP']['ER']:
                PSE.extendManifest(self.propertySource) # The train object is passed in

        return
    
    def process(self):

        return
    
    def postProcess(self):

        return
    
    
def opsPreProcess(message=None):
    """
    Extends the json files.
    """

    return

def opsProcess(message=None):
    """
    Process the extended json files.
    """

    return

def opsPostProcess(message=None):
    """
    Writes the processed json files to text files.
    """

    return


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
        
        return
        
    def activateWidgets(self):
        """
        The widget.getName() value is the name of the action for the widget.
        IE 'button'
        """

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def button(self, EVENT):
        """
        Whatever it is this button does.
        """

        print('button')

        _psLog.debug(EVENT)

        return

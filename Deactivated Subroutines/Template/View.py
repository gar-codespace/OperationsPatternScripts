# coding=utf-8
# © 2023 Greg Ritacco

"""
Template
"""

from opsEntities import PSE
from Subroutines.Template import GUI

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.XX.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('Template')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the template controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Template Subroutine'))

        return subroutineFrame

    def makeSubroutineGui(self):
        """Make the Template GUI."""

        _psLog.debug('Template.View.makeSubroutineGui')

        subroutineGui = GUI.subroutineGui()
        gui = subroutineGui.guiMaker()
        widgets = subroutineGui.guiWidgetGetter()

        return gui, widgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

# coding=utf-8
# © 2023 Greg Ritacco

"""
jPlus
"""

from opsEntities import PSE
from Subroutines.jPlus import GUI

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.JP.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile()

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the jPlus controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('jPlus Subroutine'))        

        return subroutineFrame

    def makeSubroutineGui(self):
        """Make the jPlus GUI."""

        _psLog.debug('jPlusSubroutine.View.makeSubroutineGui')

        subroutineGui = GUI.subroutineGui()
        gui = subroutineGui.guiMaker()
        widgets = subroutineGui.guiWidgetGetter()

        return gui, widgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

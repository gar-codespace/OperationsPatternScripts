# coding=utf-8
# © 2023 Greg Ritacco

"""
o2o
"""

from opsEntities import PSE
from Subroutines.o2o import GUI

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.o2o.View')

class ManageGui:

    def __init__(self):

        # self.configFile = PSE.readConfigFile('o2o')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the o2o controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('o2o Subroutine'))        

        return subroutineFrame

    def makeSubroutineGui(self):
        """Make the o2o GUI."""

        _psLog.debug('o2oSubroutine.View.makeSubroutineGui')

        subroutineGui = GUI.subroutineGui()
        gui = subroutineGui.guiMaker()
        widgets = subroutineGui.guiWidgetGetter()

        return gui, widgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

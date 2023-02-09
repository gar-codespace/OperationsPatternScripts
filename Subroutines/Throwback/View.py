# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Template
"""

from opsEntities import PSE
from Subroutines.Throwback import ViewEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.TB.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('Throwback')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the throwback controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE['Throwback Subroutine'])

        return subroutineFrame

    def makeSubroutineGui(self):
        """Make the throwback GUI."""

        _psLog.debug('ThrowbackSubroutine.View.makeSubroutineGui')

        tbSubroutinePanel = ViewEntities.tbSubroutinePanel()
        subroutinesPanel = tbSubroutinePanel.tbPanelMaker()
        subroutinePanelWidgets, subroutineDisplayWidgets = tbSubroutinePanel.tbWidgetGetter()

        return subroutinesPanel, subroutinePanelWidgets, subroutineDisplayWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

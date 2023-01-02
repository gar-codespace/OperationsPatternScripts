# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Template
"""

from opsEntities import PSE
from ThrowbackSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.ThrowbackSubroutine.View'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.TB.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('TB')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the throwback controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(u'throwbackSubroutine')
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE[u'Throwback Subroutine'])

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the throwback controls"""

        _psLog.debug('ThrowbackSubroutine.View.makeSubroutinePanel')

        tbSubroutinePanel = ViewEntities.tbSubroutinePanel()
        subroutinesPanel = tbSubroutinePanel.tbPanelMaker()
        subroutinePanelWidgets = tbSubroutinePanel.tbWidgetGetter()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Template."""

from opsEntities import PSE
from jPlusSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.jPlusSubroutine.View'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.GS.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('GS')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the o2o controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(u'jPlus')
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE[u'jPlus Subroutine'])

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the jPlus controls"""

        _psLog.debug('makeSubroutinePanel')

        jPlusSubroutinePanel = ViewEntities.jPlusSubroutinePanel()
        subroutinesPanel = jPlusSubroutinePanel.jPlusPanelMaker()
        subroutinePanelWidgets = jPlusSubroutinePanel.JPWidgetGetter()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

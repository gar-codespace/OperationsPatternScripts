# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Template."""

from opsEntities import PSE
from GenericSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.GenericSubroutine.View'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.GS.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('GS')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the o2o controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(u'generic')
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE[u'Generic Subroutine'])

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the generic controls"""

        _psLog.debug('makeSubroutinePanel')

        genericSubroutinePanel = ViewEntities.GenericSubroutinePanel()
        subroutinesPanel = genericSubroutinePanel.genericPanelMaker()
        subroutinePanelWidgets = genericSubroutinePanel.genericWidgetGetter()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

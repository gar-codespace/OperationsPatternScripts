# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Template
"""

from opsEntities import PSE
from TemplateSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.TemplateSubroutine.View'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.xxx.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('GS')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the o2o controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(u'xxx')
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE[u'xxx Subroutine'])

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the xxx controls"""

        _psLog.debug('makeSubroutinePanel')

        xxxSubroutinePanel = ViewEntities.xxxSubroutinePanel()
        subroutinesPanel = xxxSubroutinePanel.xxxPanelMaker()
        subroutinePanelWidgets = xxxSubroutinePanel.xxxWidgetGetter()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

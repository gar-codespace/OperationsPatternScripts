# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Implemented in v3"""

from psEntities import PatternScriptEntities
from o2oSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.View'
SCRIPT_REV = 20220101


class ManageGui:

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.o2oSubroutine.View')
        self.configFile = PatternScriptEntities.readConfigFile('o2o')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the o2o controls are added to"""

        subroutineFrame = PatternScriptEntities.JAVX_SWING.JPanel() # the track pattern panel
        encodedKey = unicode('o2o Subroutine', PatternScriptEntities.ENCODING)
        subroutineFrame.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createTitledBorder(
            PatternScriptEntities.BUNDLE[u'o2o Subroutine']
            )

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the o2o controls"""

        self.psLog.debug('View.makeSubroutinePanel')

        o2oSubroutinePanel = ViewEntities.O2oSubroutinePanel()
        subroutinesPanel = o2oSubroutinePanel.o2oPanelMaker()
        subroutinePanelWidgets = o2oSubroutinePanel.o2oWidgetGetter()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

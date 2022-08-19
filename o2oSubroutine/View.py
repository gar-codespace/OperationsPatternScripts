# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Implemented in v3"""

from psEntities import PatternScriptEntities
from o2oSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrianPlayerSubroutine.View'
SCRIPT_REV = 20220101


class ManageGui:

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TrainPlayer.View')
        self.configFile = PatternScriptEntities.readConfigFile('TP')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the TrainPlayer controls are added to"""

        subroutineFrame = PatternScriptEntities.JAVX_SWING.JPanel() # the track pattern panel
        encodedKey = unicode('o2o Subroutine', PatternScriptEntities.ENCODING)
        subroutineFrame.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createTitledBorder(
            PatternScriptEntities.BUNDLE[u'o2o Subroutine']
            )

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the TrainPlayer controls"""

        self.psLog.debug('View.makeSubroutinePanel')

        trainPlayerPanel = ViewEntities.TrainPlayerPanel()
        subroutinesPanel = trainPlayerPanel.makeTrainPlayerPanel()
        subroutinePanelWidgets = trainPlayerPanel.getPanelWidgets()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

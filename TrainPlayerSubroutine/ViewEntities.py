# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Creates the TrainPlayer panel, implemented in v3."""

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewEntities'
SCRIPT_REV = 20220101

class TrainPlayerPanel:

    def __init__(self):

        self.configFile = PatternScriptEntities.readConfigFile('TP')

        self.uiButton = PatternScriptEntities.JAVX_SWING.JButton()
        self.uiButton.setText(PatternScriptEntities.BUNDLE['Update Inventory'])
        self.uiButton.setName('uiButton')

        self.saButton = PatternScriptEntities.JAVX_SWING.JButton()
        self.saButton.setText(PatternScriptEntities.BUNDLE['Space Available'])
        self.saButton.setName('saButton')

        self.controlWidgets = []

        return

    def makeTrainPlayerPanel(self):

        tpPanel = PatternScriptEntities.JAVX_SWING.JPanel()

        tpPanel.add(self.uiButton)
        tpPanel.add(PatternScriptEntities.JAVX_SWING.Box.createRigidArea(PatternScriptEntities.JAVA_AWT.Dimension(20,0)))
        tpPanel.add(self.saButton)

        return tpPanel

    def getPanelWidgets(self):

        self.controlWidgets.append(self.uiButton)
        self.controlWidgets.append(self.saButton)

        return self.controlWidgets

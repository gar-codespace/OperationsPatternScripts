# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Creates the TrainPlayer panel, implemented in v3."""

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewEntities'
SCRIPT_REV = 20220101

class TrainPlayerPanel:

    def __init__(self):

        self.configFile = PatternScriptEntities.readConfigFile('TP')

        self.irButton = PatternScriptEntities.JAVX_SWING.JButton()
        self.irButton.setText(PatternScriptEntities.BUNDLE[u'Import TrainPlayer© Railroad'])
        self.irButton.setName('irButton')

        self.nrButton = PatternScriptEntities.JAVX_SWING.JButton()
        self.nrButton.setText(PatternScriptEntities.BUNDLE[u'New JMRI Railroad'])
        self.nrButton.setName('nrButton')

        self.urButton = PatternScriptEntities.JAVX_SWING.JButton()
        self.urButton.setText(PatternScriptEntities.BUNDLE[u'Update Rolling Stock'])
        self.urButton.setName('urButton')

        self.controlWidgets = []

        return

    def makeTrainPlayerPanel(self):

        tpPanel = PatternScriptEntities.JAVX_SWING.JPanel()

        tpPanel.add(self.irButton)
        tpPanel.add(PatternScriptEntities.JAVX_SWING.Box.createRigidArea(PatternScriptEntities.JAVA_AWT.Dimension(20,0)))
        tpPanel.add(self.nrButton)
        tpPanel.add(PatternScriptEntities.JAVX_SWING.Box.createRigidArea(PatternScriptEntities.JAVA_AWT.Dimension(20,0)))
        tpPanel.add(self.urButton)

        return tpPanel

    def getPanelWidgets(self):

        self.controlWidgets.append(self.irButton)
        self.controlWidgets.append(self.nrButton)
        self.controlWidgets.append(self.urButton)

        return self.controlWidgets

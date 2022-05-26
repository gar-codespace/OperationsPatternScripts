# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Creates the TrainPlayer panel"""

import jmri
import java.awt
import javax.swing

from psEntities import PatternScriptEntities
from psBundle import Bundle

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewEntities'
SCRIPT_REV = 20220101

class TrainPlayerPanel:

    def __init__(self):

        self.configFile = PatternScriptEntities.readConfigFile('TP')

        self.uiButton = javax.swing.JButton()
        self.uiButton.setText(PatternScriptEntities.BUNDLE['Update Inventory'])
        self.uiButton.setName('uiButton')

        self.saButton = javax.swing.JButton()
        self.saButton.setText(PatternScriptEntities.BUNDLE['Space Available'])
        self.saButton.setName('saButton')

        self.controlWidgets = []

        return

    def makeTrainPlayerPanel(self):

        tpPanel = javax.swing.JPanel()

        tpPanel.add(self.uiButton)
        tpPanel.add(javax.swing.Box.createRigidArea(java.awt.Dimension(20,0)))
        tpPanel.add(self.saButton)

        return tpPanel

    def getPanelWidgets(self):

        self.controlWidgets.append(self.uiButton)
        self.controlWidgets.append(self.saButton)

        return self.controlWidgets

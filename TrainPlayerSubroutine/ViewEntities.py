# coding=utf-8
# © 2021, 2022 Greg Ritacco

'''Creates the TrainPlayer panel'''

import jmri
import java.awt
import javax.swing

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewEntities'
SCRIPT_REV = 20220101

class TrainPlayerPanel:

    def __init__(self):

        self.configFile = PatternScriptEntities.readConfigFile('TP')

        self.aButton = javax.swing.JButton()
        self.aButton.setText(u'For Rent')
        self.aButton.setName('aButton')

        self.bButton = javax.swing.JButton()
        self.bButton.setText(u'Post No Bills')
        self.bButton.setName('bButton')

        self.controlWidgets = []

        return

    def makeTrainPlayerPanel(self):

        tpPanel = javax.swing.JPanel()

        tpPanel.add(self.aButton)
        tpPanel.add(javax.swing.Box.createRigidArea(java.awt.Dimension(20,0)))
        tpPanel.add(self.bButton)

        return tpPanel

    def getPanelWidgets(self):

        self.controlWidgets.append(self.aButton)
        self.controlWidgets.append(self.bButton)

        return self.controlWidgets

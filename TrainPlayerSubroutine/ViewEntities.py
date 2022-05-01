# coding=utf-8
# © 2021, 2022 Greg Ritacco

'''Creates the pattern tracks and its panel'''

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
        self.bButton.setText(u'Not Implemented')
        self.bButton.setName('bButton')

        self.controlObjects = []

        return

    def makeTrainPlayerPanel(self):

        tpPanel = javax.swing.JPanel()

        tpPanel.add(self.aButton)
        tpPanel.add(javax.swing.Box.createRigidArea(java.awt.Dimension(20,0)))
        tpPanel.add(self.bButton)

        return tpPanel

    def getPanelWidgets(self):
        '''A list of the widgets created by this class'''

        self.controlObjects.append(self.aButton)
        self.controlObjects.append(self.bButton)

        return self.controlObjects

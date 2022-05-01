# coding=utf-8
# © 2021, 2022 Greg Ritacco

'''View script for the TrainPlayer subroutine'''

import jmri
import javax.swing
import java.awt

import logging
from os import system as osSystem

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrianPlayerSubroutine.View'
SCRIPT_REV = 20220101
psLog = logging.getLogger('PS.TrainPlayer.View')

class ManageGui:

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.View')
        self.configFile = PatternScriptEntities.readConfigFile('TP')

        return

    def makeSubroutineFrame(self):
        '''Make the frame that all the TrainPlayer controls are added to'''

        subroutineFrame = javax.swing.JPanel() # the track pattern panel
        subroutineFrame.border = javax.swing.BorderFactory.createTitledBorder(u'TrainPlayer Support Subroutine')

        return subroutineFrame

    def makeSubroutinePanel(self):
        '''Make the TrainPlayer controls'''

        self.psLog.debug('makeSubroutinePanel')

        trainPlayerPanel = ViewEntities.TrainPlayerPanel()
        subroutinesPanel = trainPlayerPanel.makeTrainPlayerPanel()
        subroutinePanelWidgets = trainPlayerPanel.getPanelWidgets()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

# coding=utf-8
# © 2021, 2022 Greg Ritacco

'''View script for the TrainPlayer subroutine'''

import jmri
import javax.swing

import logging
from os import system as osSystem

from psEntities import MainScriptEntities
# from TrianPlayerSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrianPlayerSubroutine.View'
SCRIPT_REV = 20220101
psLog = logging.getLogger('PS.TrainPlayer.View')

class ManageGui:

    def __init__(self):

        self.psLog = logging.getLogger('PS.TrainPlayer.View')
        self.configFile = MainScriptEntities.readConfigFile('TP')

        return

    def makeSubroutineFrame(self):
        '''Make the frame that all the track pattern controls are added to'''

        subroutineFrame = javax.swing.JPanel() # the track pattern panel
        subroutineFrame.setLayout(javax.swing.BoxLayout(subroutineFrame, javax.swing.BoxLayout.Y_AXIS))
        subroutineFrame.border = javax.swing.BorderFactory.createTitledBorder(u'Track Pattern')

        return subroutineFrame

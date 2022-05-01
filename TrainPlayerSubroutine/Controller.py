# coding=utf-8
# © 2021, 2022 Greg Ritacco

'''The TrainPlayer Subroutine will be filled in in V3, this is just the framework'''

import jmri
import java.awt.event

import logging
from os import system as osSystem

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import Model
from TrainPlayerSubroutine import View

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.Controller'
SCRIPT_REV = 20220101

class StartUp:
    '''Start the Track Pattern subroutine'''

    def __init__(self, subroutineFrame=None):

        self.psLog = logging.getLogger('PS.TP.Controller')
        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        '''Makes the title border frame'''

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        self.psLog.info('TrainPlayer makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        '''Makes the control panel that sits inside the frame'''

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def validateSubroutineConfig(self):
        '''Put a test here that validates config file ["T"]'''

        if not PatternScriptEntities.readConfigFile('PT')['AL']:
            PatternScriptEntities.writeNewConfigFile()
            Model.updatePatternLocation()

        return

    def activateWidgets(self):
        '''Maybe get them by name?'''

        self.widgets[0].actionPerformed = self.aButtonAction
        self.widgets[1].actionPerformed = self.bButtonAction

        return


    def aButtonAction(self, EVENT):
        '''Whatever this button ends up doing'''

        print('This space for rent')

        return

    def bButtonAction(self, EVENT):
        '''Whatever this button ends up doing'''

        print('This button is not implemented')

        return

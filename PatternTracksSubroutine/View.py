# coding=utf-8
# © 2021, 2022 Greg Ritacco

'''View script for the pattern tracks subroutine'''

import jmri
import javax.swing

import logging
from os import system as osSystem

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.View'
SCRIPT_REV = 20220101
psLog = logging.getLogger('PS.PT.View')

class ManageGui:

    def __init__(self):

        self.psLog = logging.getLogger('PS.PT.View')
        self.configFile = PatternScriptEntities.readConfigFile('PT')

        return

    def makeSubroutineFrame(self):
        '''Make the frame that all the pattern tracks controls are added to'''

        subroutineFrame = javax.swing.JPanel() # the pattern tracks panel
        subroutineFrame.setLayout(javax.swing.BoxLayout(subroutineFrame, javax.swing.BoxLayout.Y_AXIS))
        subroutineFrame.border = javax.swing.BorderFactory.createTitledBorder(u'Pattern Tracks Subroutine')

        return subroutineFrame

    def makeSubroutinePanel(self):
        '''Make the pattern tracks controls'''

        self.psLog.debug('makeSubroutinePanel')
        
        trackPatternPanel = ViewEntities.TrackPatternPanel()
        subroutinesPanel = trackPatternPanel.makeTrackPatternPanel()
        subroutinePanelWidgets = trackPatternPanel.getPanelWidgets()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

def displayTextSwitchList(textSwitchList):
    '''Opens the text switchlist to Notepad or other'''

    psLog.debug('displayTextSwitchList')

    fileToDisplay = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\' + textSwitchList.splitlines()[0] + '.txt'

    return osSystem(PatternScriptEntities.openEditorByComputerType(fileToDisplay))

def printPatternLog():
    '''Opens the pattern log in notepad or other'''

    psLog.debug('displayPatternLog')

    tempPatternLog = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog_temp.txt'
    osSystem(PatternScriptEntities.openEditorByComputerType(tempPatternLog))

    return

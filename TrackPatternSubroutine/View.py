# coding=utf-8
# © 2021, 2022 Greg Ritacco

'''View script for the track pattern subroutine'''

import jmri
import logging
from os import system as osSystem

from psEntities import MainScriptEntities
from TrackPatternSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrackPatternSubroutine.View'
SCRIPT_REV = 20220101
psLog = logging.getLogger('PS.TP.View')

class ManageGui:

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.View')
        self.configFile = MainScriptEntities.readConfigFile('TP')

        return

    def makeFrame(self):
        '''Makes the title frame that all the track pattern controls go into'''

        self.psLog.debug('makeFrame')

        return ViewEntities.TrackPatternPanel().makePatternFrame()

    def makePanel(self):
        '''Make the track pattern controls'''

        self.psLog.debug('makePanel')
        trackPatternPanel = ViewEntities.TrackPatternPanel()
        patternPanel = trackPatternPanel.makeTrackPatternPanel()
        patternPanelWidgets = trackPatternPanel.getPanelWidgets()

        return patternPanel, patternPanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

def updatePanel(panel):
    ''' Replaces the current panel with an updated panel'''

    psLog.debug('updatePanel')

    trackPatternPanel = ViewEntities.TrackPatternPanel()
    patternPanel = trackPatternPanel.makeTrackPatternPanel()
    patternPanelWidgets = trackPatternPanel.getPanelWidgets()
    panel.removeAll()
    panel.add(patternPanel)
    panel.revalidate()

    return patternPanelWidgets

def displayTextSwitchList(textSwitchList):
    '''Opens the text switchlist to Notepad or other'''

    psLog.debug('displayTextSwitchList')

    fileToDisplay = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\' + textSwitchList.splitlines()[0] + '.txt'

    return osSystem(MainScriptEntities.openEditorByComputerType(fileToDisplay))

def printPatternLog():
    '''Opens the pattern log in notepad or other'''

    psLog.debug('displayPatternLog')

    tempPatternLog = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog_temp.txt'
    osSystem(MainScriptEntities.openEditorByComputerType(tempPatternLog))

    return

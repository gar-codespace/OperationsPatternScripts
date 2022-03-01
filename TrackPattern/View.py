# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import logging
from os import system as osSystem

import psEntities.MainScriptEntities
import TrackPattern.ViewEntities

'''View script for the track pattern subroutine'''

scriptName = 'OperationsPatternScripts.TrackPattern.View'
scriptRev = 20220101
psLog = logging.getLogger('PS.TP.View')

class ManageGui:
    '''Manages all the GUI elements for the Pattern Scripts subroutine'''

    def __init__(self, panel=None, controls=None):
        '''Track Pattern panel'''

        self.psLog = logging.getLogger('PS.TP.View')
        self.configFile = psEntities.MainScriptEntities.readConfigFile('TP')
        self.panel = panel
        self.controls = controls

        return

    def updatePanel(self, panel):
        ''' Replaces the current panel with a new updated panel'''

        self.psLog.debug('updatePanel')
        newView, newControls = TrackPattern.ViewEntities.TrackPatternPanel().makePatternControls()
        panel.removeAll()
        panel.add(newView)
        panel.revalidate()

        return newControls

    def makeFrame(self):
        '''Makes the title frame that all the track pattern controls go into'''

        self.psLog.debug('makeFrame')
        return TrackPattern.ViewEntities.TrackPatternPanel().makePatternFrame()

    def makePanel(self):
        '''Make the track pattern controls'''

        self.psLog.debug('makePanel')
        return TrackPattern.ViewEntities.TrackPatternPanel().makePatternControls()

    print(scriptName + ' ' + str(scriptRev))

def displayTextSwitchlist(location):
    '''Opens the text switchlist to Notepad or other'''

    psLog.debug('displayTextSwitchlist')

    textSwitchList = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\Track Pattern (' + location + ').txt'
    osSystem(psEntities.MainScriptEntities.openEditorByComputerType(textSwitchList))

    return

def displayTextSwitchList(textSwitchList):
    '''Opens the text switchlist to Notepad or other'''

    fileToDisplay = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\' + textSwitchList.splitlines()[0] + '.txt'

    return osSystem(psEntities.MainScriptEntities.openEditorByComputerType(fileToDisplay))

def printPatternLog():
    '''Opens the pattern log in notepad or other'''

    psLog.debug('displayPatternLog')
    
    tempPatternLog = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog_temp.txt'
    osSystem(psEntities.MainScriptEntities.openEditorByComputerType(tempPatternLog))

    return

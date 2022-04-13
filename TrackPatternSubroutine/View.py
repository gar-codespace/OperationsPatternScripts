# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import logging
from os import system as osSystem

from psEntities import MainScriptEntities
from TrackPatternSubroutine import ViewEntities

'''View script for the track pattern subroutine'''

SCRIPT_NAME = 'OperationsPatternScripts.TrackPatternSubroutine.View'
SCRIPT_REV = 20220101
psLog = logging.getLogger('PS.TP.View')

class ManageGui:
    '''Manages all the GUI elements for the Pattern Scripts subroutine'''

    def __init__(self, panel=None, controls=None):
        '''Track Pattern panel'''

        self.psLog = logging.getLogger('PS.TP.View')
        self.configFile = MainScriptEntities.readConfigFile('TP')
        self.panel = panel
        self.controls = controls

        return

    def updatePanel(self, panel):
        ''' Replaces the current panel with a new updated panel'''

        self.psLog.debug('updatePanel')
        newView, newControls = ViewEntities.TrackPatternPanel().makePatternControls()
        panel.removeAll()
        panel.add(newView)
        panel.revalidate()

        return newControls

    def makeFrame(self):
        '''Makes the title frame that all the track pattern controls go into'''

        self.psLog.debug('makeFrame')

        return ViewEntities.TrackPatternPanel().makePatternFrame()

    def makePanel(self):
        '''Make the track pattern controls'''

        self.psLog.debug('makePanel')

        return ViewEntities.TrackPatternPanel().makePatternControls()

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

def displayTextSwitchList(textSwitchList):
    '''Opens the text switchlist to Notepad or other'''

    fileToDisplay = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\' + textSwitchList.splitlines()[0] + '.txt'

    return osSystem(MainScriptEntities.openEditorByComputerType(fileToDisplay))

def printPatternLog():
    '''Opens the pattern log in notepad or other'''

    psLog.debug('displayPatternLog')

    tempPatternLog = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog_temp.txt'
    osSystem(MainScriptEntities.openEditorByComputerType(tempPatternLog))

    return

# coding=utf-8
# Extended ìÄÅÉî
# View script for the track pattern subroutine
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import logging
from os import system
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsTrackPattern')
import MainScriptEntities
import TrackPattern.ViewEntities

scriptRev = 'TrackPattern.View v20211210'
psLog = logging.getLogger('PS.TP.View')

class manageGui:
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
        newView, newControls = TrackPattern.ViewEntities.TrackPatternPanel().makePatternControls()
        panel.removeAll()
        panel.add(newView)
        panel.revalidate()
        # panel.repaint()

        return newControls

    def makeFrame(self):
        '''Makes the title frame that all the track pattern controls go into'''

        self.psLog.debug('makeFrame')
        return TrackPattern.ViewEntities.TrackPatternPanel().makePatternFrame()

    def makePanel(self):
        '''Make the track pattern controls'''

        self.psLog.debug('makePanel')
        return TrackPattern.ViewEntities.TrackPatternPanel().makePatternControls()

    print(scriptRev)

def displayTextSwitchlist(location):
    '''Opens the text switchlist to Notepad or other'''

    psLog.debug('displayTextSwitchlist')
    textSwitchList = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\Track Pattern (' + location + ').txt'
    system(MainScriptEntities.systemInfo() + textSwitchList)

    return

def displayPatternLog():
    '''Opens the pattern log in notepad or other'''

    psLog.debug('displayPatternLog')
    textPatternLog = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternLog.txt'
    system(MainScriptEntities.systemInfo() + textPatternLog)

    return

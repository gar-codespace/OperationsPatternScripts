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
import TrackPattern.ViewTrackPatternPanel

class manageGui:
    '''At startup create the GUI elements'''

    scriptRev = 'View/manageGui rev.20211015'

    def __init__(self, panel=None, controls=None):
        '''Track Pattern panel'''

        self.psLog = logging.getLogger('PS.View')
        self.configFile = MainScriptEntities.readConfigFile('TP')
        self.panel = panel
        self.controls = controls

        return

    def updatePanel(self, panel):
        ''' Makes a new panel from the config file and replaces the current panel with the new panel'''

        newView, newControls = TrackPattern.ViewTrackPatternPanel.TrackPatternPanel().makePatternControls()
        panel.removeAll()
        panel.add(newView)
        panel.revalidate()
        # panel.repaint()

        return newControls

    def makeFrame(self):
        '''Makes the title frame that all the track pattern controls go into'''

        return TrackPattern.ViewTrackPatternPanel.TrackPatternPanel().makePatternFrame()

    def makePanel(self):
        '''Make the track pattern controls'''

        return TrackPattern.ViewTrackPatternPanel.TrackPatternPanel().makePatternControls()

    print(scriptRev)

def displayTextSwitchlist(location):
    '''Opens the text switchlist to Notepad or other'''

    textSwitchList = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\Track Pattern (' + location + ').txt'
    system(MainScriptEntities.systemInfo() + textSwitchList)

    return

def displayPatternLog():
    '''Opens the pattern log in notepad or other'''

    textPatternLog = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternLog.txt'
    system(MainScriptEntities.systemInfo() + textPatternLog)

    return

# coding=utf-8
# © 2021, 2022 Greg Ritacco

'''View script for the track pattern subroutine'''

import jmri
import javax.swing

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

    def makeSubroutineFrame(self):
        '''Make the frame that all the track pattern controls are added to'''

        subroutineFrame = javax.swing.JPanel() # the track pattern panel
        subroutineFrame.setLayout(javax.swing.BoxLayout(subroutineFrame, javax.swing.BoxLayout.Y_AXIS))
        subroutineFrame.border = javax.swing.BorderFactory.createTitledBorder(u'Track Pattern')

        return subroutineFrame

    # def makeFrame(self):
    #     '''Makes the title frame that all the track pattern controls go into'''
    #
    #     self.psLog.debug('makeFrame')
    #
    #     return ViewEntities.TrackPatternPanel().makePatternFrame()

    def makeSubroutinePanel(self):
        '''Make the track pattern controls'''

        self.psLog.debug('makeSubroutinePanel')
        trackPatternPanel = ViewEntities.TrackPatternPanel()
        subroutinesPanel = trackPatternPanel.makeTrackPatternPanel()
        subroutinePanelWidgets = trackPatternPanel.getPanelWidgets()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

# def updatePanel(panel):
#     ''' Replaces the current panel with an updated panel'''
#
#     psLog.debug('updatePanel')
#
#     trackPatternPanel = ViewEntities.TrackPatternPanel()
#     patternPanel = trackPatternPanel.makeTrackPatternPanel()
#     patternPanelWidgets = trackPatternPanel.getPanelWidgets()
#     panel.removeAll()
#     panel.add(patternPanel)
#     panel.revalidate()
#
#     return patternPanelWidgets

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

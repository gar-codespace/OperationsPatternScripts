# coding=utf-8
# © 2021, 2022 Greg Ritacco

import jmri
import java.awt.event

import logging
from os import system as osSystem

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import Model
from PatternTracksSubroutine import View

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.Controller'
SCRIPT_REV = 20220101

class LocationComboBox(java.awt.event.ActionListener):
    '''Event triggered from location combobox selection'''

    def __init__(self, subroutineFrame):

        self.subroutineFrame = subroutineFrame
        self.psLog = logging.getLogger('PS.PT.ComboBox')

    def actionPerformed(self, EVENT):

        Model.updatePatternLocation(EVENT.getSource().getSelectedItem())
        subroutinePanel = StartUp(self.subroutineFrame).makeSubroutinePanel()
        self.subroutineFrame.removeAll()
        self.subroutineFrame.add(subroutinePanel)
        self.subroutineFrame.revalidate()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

class StartUp:
    '''Start the pattern tracks subroutine'''

    def __init__(self, subroutineFrame=None):

        self.psLog = logging.getLogger('PS.PT.Controller')
        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        '''Makes the title border frame'''

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        self.psLog.info('pattern tracks makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        '''Makes the control panel that sits inside the frame'''

        if not PatternScriptEntities.readConfigFile('PT')['AL']:
            Model.updateLocations()

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def activateWidgets(self):

        self.widgets[0].addActionListener(LocationComboBox(self.subroutineFrame))
        self.widgets[1].actionPerformed = self.yardTrackOnlyCheckBox
        self.widgets[4].actionPerformed = self.patternButton
        self.widgets[5].actionPerformed = self.setCarsButton
        # self.widgets[6].actionPerformed = self.viewLogButton

        return

    def yardTrackOnlyCheckBox(self, EVENT):

        if (self.widgets[1].selected):
            trackList = Model.makeTrackList(self.widgets[0].getSelectedItem(), 'Yard')
        else:
            trackList = Model.makeTrackList(self.widgets[0].getSelectedItem(), None)

        configFile = PatternScriptEntities.readConfigFile()
        trackDict = Model.updatePatternTracks(trackList)
        configFile['PT'].update({'PT': trackDict})
        configFile['PT'].update({'PA': self.widgets[1].selected})
        configFile['PT'].update({'PI': self.widgets[2].selected})

        subroutinePanel = StartUp(self.subroutineFrame).makeSubroutinePanel()
        self.subroutineFrame.removeAll()
        self.subroutineFrame.add(subroutinePanel)
        self.subroutineFrame.revalidate()

        PatternScriptEntities.writeConfigFile(configFile)
        # PatternScriptEntities.backupConfigFile()

        return

    def patternButton(self, EVENT):
        '''Makes a pattern tracks report based on the config file (PR)'''

        self.psLog.debug('Controller.patternButton')

        Model.updateConfigFile(self.widgets)

        if not Model.verifySelectedTracks():
            self.psLog.warning('Track not found, re-select the location')
            return

        if not Model.getSelectedTracks():
            self.psLog.warning('No tracks were selected for the pattern button')
            return

        locationDict = Model.makeLocationDict()
        modifiedReport = Model.makeReport(locationDict, 'PR')

        Model.printWorkEventList(modifiedReport, trackTotals=True)

        if jmri.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled():
            Model.writeCsvSwitchList(modifiedReport, 'PR')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def setCarsButton(self, EVENT):
        '''Opens a "Pattern Report for Track X" window for each checked track'''

        self.psLog.debug('Controller.setCarsButton')

        Model.updateConfigFile(self.widgets)

        if not Model.verifySelectedTracks():
            self.psLog.warning('Track not found, re-select the location')
            return

        Model.onScButtonPress()

        if PatternScriptEntities.readConfigFile('PT')['TI']: # TrainPlayer Include
            Model.resetTrainPlayerSwitchlist()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

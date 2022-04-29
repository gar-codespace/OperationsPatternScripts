# coding=utf-8
# © 2021, 2022 Greg Ritacco

import jmri
import java.awt.event

import logging
from os import system as osSystem

from psEntities import MainScriptEntities
from TrackPatternSubroutine import Model
from TrackPatternSubroutine import View

SCRIPT_NAME = 'OperationsPatternScripts.TrackPatternSubroutine.Controller'
SCRIPT_REV = 20220101

class LocationComboBox(java.awt.event.ActionListener):
    '''Event triggered from location combobox selection'''

    def __init__(self, subroutineFrame):

        self.subroutineFrame = subroutineFrame
        self.psLog = logging.getLogger('PS.TP.ComboBox')

    def actionPerformed(self, EVENT):

        Model.updatePatternLocation(EVENT.getSource().getSelectedItem())
        subroutinePanel = StartUp(self.subroutineFrame).makeSubroutinePanel()
        self.subroutineFrame.removeAll()
        self.subroutineFrame.add(subroutinePanel)
        self.subroutineFrame.revalidate()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

class StartUp:
    '''Start the Track Pattern subroutine'''

    def __init__(self, subroutineFrame=None):

        self.psLog = logging.getLogger('PS.TP.Control')
        self.subroutineFrame = subroutineFrame

        return

    def yardTrackOnlyCheckBox(self, EVENT):

        if (self.widgets[1].selected):
            trackList = Model.makeTrackList(self.widgets[0].getSelectedItem(), 'Yard')
        else:
            trackList = Model.makeTrackList(self.widgets[0].getSelectedItem(), None)

        configFile = MainScriptEntities.readConfigFile()
        trackDict = Model.updatePatternTracks(trackList)
        configFile['TP'].update({'PT': trackDict})
        configFile['TP'].update({'PA': self.widgets[1].selected})
        configFile['TP'].update({'PI': self.widgets[2].selected})
        MainScriptEntities.writeConfigFile(configFile)

        subroutinePanel = StartUp(self.subroutineFrame).makeSubroutinePanel()
        self.subroutineFrame.removeAll()
        self.subroutineFrame.add(subroutinePanel)
        self.subroutineFrame.revalidate()

        return

    def patternButton(self, EVENT):
        '''Makes a track pattern report (PR) based on the config file'''

        self.psLog.debug('patternButton')

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

        self.psLog.debug('setCarsButton')

        Model.updateConfigFile(self.widgets)

        if not Model.verifySelectedTracks():
            self.psLog.warning('Track not found, re-select the location')
            return

        Model.onScButtonPress()

        if MainScriptEntities.readConfigFile('TP')['TF']['TI']: # TrainPlayer Include
            Model.resetTrainPlayerSwitchlist()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def viewLogButton(self, EVENT):
        '''Displays the pattern report log file in a notepad window'''

        Model.makePatternLog()
        View.printPatternLog()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def activateWidgets(self):

        self.widgets[0].addActionListener(LocationComboBox(self.subroutineFrame))
        self.widgets[1].actionPerformed = self.yardTrackOnlyCheckBox
        self.widgets[4].actionPerformed = self.patternButton
        self.widgets[5].actionPerformed = self.setCarsButton
        self.widgets[6].actionPerformed = self.viewLogButton

        return

    def validateSubroutineConfig(self):

        if not MainScriptEntities.readConfigFile('TP')['AL']:
            MainScriptEntities.writeNewConfigFile()
            Model.updatePatternLocation()

        return

    def makeSubroutineFrame(self):
        '''Makes the title border frame'''

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        '''Makes the control panel that sits inside the frame'''

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        self.psLog.info('Track pattern makeFrame completed')

        return self.subroutinePanel

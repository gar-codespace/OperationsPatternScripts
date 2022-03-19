# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import java.awt.event
import logging
from os import system as osSystem

from psEntities import MainScriptEntities
from TrackPattern import Model
from TrackPattern import View

scriptName = 'OperationsPatternScripts.TrackPattern.Controller'
scriptRev = 20220101

class StartUp():
    '''Start the Track Pattern subroutine'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.Control')

        return

    class LocationComboBox(java.awt.event.ActionListener):
        '''Event triggered from location combobox selection'''

        def __init__(self, panel, controls):
            self.panel = panel
            self.controls = controls
            self.psLog = logging.getLogger('PS.TP.ComboBox')

        def actionPerformed(self, event):

            newConfigFile = Model.updatePatternLocation(event.getSource().getSelectedItem())
            MainScriptEntities.writeConfigFile(newConfigFile)
            newConfigFile = MainScriptEntities.readConfigFile('TP')
            newConfigFile = Model.makeNewPatternTracks(newConfigFile['PL'])
            MainScriptEntities.writeConfigFile(newConfigFile)
            self.psLog.info('The track list for location ' + newConfigFile['TP']['PL'] + ' has been created')
            self.controls = View.ManageGui().updatePanel(self.panel)
            StartUp().activateButtons(self.panel, self.controls)

            print(scriptName + ' ' + str(scriptRev))

            return

    def yardTrackOnlyCheckBox(self, event):

        if (self.controls[1].selected):
            trackList = Model.makeTrackList(self.controls[0].getSelectedItem(), 'Yard')
        else:
            trackList = Model.makeTrackList(self.controls[0].getSelectedItem(), None)

        newConfigFile = Model.updatePatternTracks(trackList)
        MainScriptEntities.writeConfigFile(newConfigFile)
        newConfigFile = Model.updateCheckBoxStatus(self.controls[1].selected, self.controls[2].selected)
        MainScriptEntities.writeConfigFile(newConfigFile)
        self.controls = View.ManageGui().updatePanel(self.panel)
        StartUp().activateButtons(self.panel, self.controls)

        return

    def patternButton(self, event):
        '''Makes a track pattern report (PR) based on the config file'''

        self.psLog.debug('patternButton')

        Model.updateConfigFile(self.controls)

        if not Model.getSelectedTracks():
            self.psLog.info('No tracks were selected')
            return

        locationDict = Model.makeLocationDict()
        modifiedReport = Model.makeReport(locationDict, 'PR')

        Model.printWorkEventList(modifiedReport, trackTotals=True)

        if jmri.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled():
            Model.writeCsvSwitchList(modifiedReport, 'PR')

        print(scriptName + ' ' + str(scriptRev))

        return

    def setCarsButton(self, event):
        '''Opens a "Pattern Report for Track X" window for each checked track'''

        self.psLog.debug('setCarsButton')

        Model.updateConfigFile(self.controls)

        # Model.makeLoadEmptyDesignationsDicts()
        # Model.makeCustomLoadEmptyByCarType()
        Model.onScButtonPress()

        if MainScriptEntities.readConfigFile('TP')['TI']: # TrainPlayer Include
            Model.resetTrainPlayerSwitchlist()

        print(scriptName + ' ' + str(scriptRev))

        return

    def viewLogButton(self, event):
        '''Displays the pattern report log file in a notepad window'''

        Model.makePatternLog()
        View.printPatternLog()

        print(scriptName + ' ' + str(scriptRev))

        return

    def activateButtons(self, panel, controls):
        '''Assigns actions to the subroutine widgets'''

        self.panel = panel
        self.controls = controls
        self.controls[0].addActionListener(self.LocationComboBox(panel, controls))
        self.controls[1].actionPerformed = self.yardTrackOnlyCheckBox
        self.controls[4].actionPerformed = self.patternButton
        self.controls[5].actionPerformed = self.setCarsButton
        self.controls[6].actionPerformed = self.viewLogButton

        return

    def makeSubroutineFrame(self):
        '''Makes the title border frame'''

        patternFrame = View.ManageGui().makeFrame()
        self.psLog.info('track pattern makeFrame completed')

        return patternFrame

    def makeSubroutinePanel(self):
        '''Make and activate the Track Pattern objects'''

        MainScriptEntities.writeConfigFile(Model.updateLocations())
        panel, controls = View.ManageGui().makePanel()
        self.activateButtons(panel, controls)
        self.psLog.info('track pattern makeSubroutinePanel completed')

        return panel

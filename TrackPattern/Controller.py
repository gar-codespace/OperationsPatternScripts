# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import java.awt.event
import logging

import psEntities.MainScriptEntities
import TrackPattern.Model
import TrackPattern.View

'''Controller script for the track pattern subroutine'''

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

            newConfigFile = TrackPattern.Model.updatePatternLocation(event.getSource().getSelectedItem())
            psEntities.MainScriptEntities.writeConfigFile(newConfigFile)
            newConfigFile = psEntities.MainScriptEntities.readConfigFile('TP')
            newConfigFile = TrackPattern.Model.makeNewPatternTracks(newConfigFile['PL'])
            psEntities.MainScriptEntities.writeConfigFile(newConfigFile)
            self.psLog.info('The track list for location ' + newConfigFile['TP']['PL'] + ' has been created')
            self.controls = TrackPattern.View.ManageGui().updatePanel(self.panel)
            StartUp().activateButtons(self.panel, self.controls)

            print(scriptName + ' ' + str(scriptRev))

            return

    def yardTrackOnlyCheckBox(self, event):

        if (self.controls[1].selected):
            trackList = TrackPattern.Model.makeTrackList(self.controls[0].getSelectedItem(), 'Yard')
        else:
            trackList = TrackPattern.Model.makeTrackList(self.controls[0].getSelectedItem(), None)

        newConfigFile = TrackPattern.Model.updatePatternTracks(trackList)
        psEntities.MainScriptEntities.writeConfigFile(newConfigFile)
        newConfigFile = TrackPattern.Model.updateCheckBoxStatus(self.controls[1].selected, self.controls[2].selected)
        psEntities.MainScriptEntities.writeConfigFile(newConfigFile)
        self.controls = TrackPattern.View.ManageGui().updatePanel(self.panel)
        StartUp().activateButtons(self.panel, self.controls)

        return

    def patternButton(self, event):
        '''Makes a track pattern report based on the config file'''

        self.psLog.info('Configuration file updated with new settings for controls')
        TrackPattern.Model.updateConfigFile(self.controls)

        listLocations = TrackPattern.Model.makePatternLocations()
        if not listLocations:
            self.psLog.info('No tracks were selected')
            return

        patternListForJson = TrackPattern.Model.makePatternHeader()
        patternListForJson['trainDescription'] = psEntities.MainScriptEntities.readConfigFile('TP')['RT']['PR']
        patternListForJson['locations'] = listLocations
        workEventName = TrackPattern.Model.writeWorkEventListAsJson(patternListForJson)
        textWorkEventList = TrackPattern.Model.readJsonWorkEventList(workEventName)
        textListForPrint = TrackPattern.Model.makeTextListForPrint(textWorkEventList, trackTotals=True)
        TrackPattern.Model.writeTextSwitchList(workEventName, textListForPrint)
        TrackPattern.View.displayTextSwitchList(workEventName)

        print(scriptName + ' ' + str(scriptRev))

        return

    def setCarsButton(self, event):
        '''Opens a "Pattern Report for Track X" window for each checked track'''

        self.controls = TrackPattern.Model.updateConfigFile(self.controls)
        self.psLog.info('Configuration file updated with new settings for controls')

        TrackPattern.Model.makeLoadEmptyDesignationsDicts()
        TrackPattern.Model.onScButtonPress()
        if psEntities.MainScriptEntities.readConfigFile('TP')['TI']: # TrainPlayer Include
            TrackPattern.Model.resetTrainPlayerSwitchlist()
        print(scriptName + ' ' + str(scriptRev))

        return

    def viewLogButton(self, event):
        '''Displays the pattern report log file in a notepad window'''

        TrackPattern.Model.makePatternLog()
        TrackPattern.View.printPatternLog()
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

        patternFrame = TrackPattern.View.ManageGui().makeFrame()
        self.psLog.info('track pattern makeFrame completed')

        return patternFrame

    def makeSubroutinePanel(self):
        '''Make and activate the Track Pattern objects'''

        psEntities.MainScriptEntities.writeConfigFile(TrackPattern.Model.updateLocations())
        panel, controls = TrackPattern.View.ManageGui().makePanel()
        self.activateButtons(panel, controls)
        self.psLog.info('track pattern makeSubroutinePanel completed')

        return panel

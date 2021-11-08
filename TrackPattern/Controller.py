# coding=utf-8
# Extended ìÄÅÉî
# Controller script for the track pattern subroutine
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import logging
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import TrackPattern.View
import TrackPattern.Model
import TrackPattern.MakeSetCarsForms

class StartUp:
    '''Start the the Track Pattern subroutine'''

    def __init__(self):

        self.psLog = logging.getLogger('Pattern Scripts.tpController')

        return

    def whenTPEnterPressed(self, event):
        '''When enter is pressed for Yard Pattern box'''

        updatedConfigTpValues = TrackPattern.Model.validateUserInput(self.controls)
        newConfigFile = MainScriptEntities.readConfigFile('all')
        newConfigFile.update({"TP": updatedConfigTpValues})
        MainScriptEntities.updateConfigFile(newConfigFile)
        self.panel, self.controls = TrackPattern.View.manageGui().updatePanel(self.panel)
        self.psLog.info('control panel refreshed')
        self.controls[0].actionPerformed = self.whenTPEnterPressed
        self.configFile = MainScriptEntities.readConfigFile('TP')
        if (self.configFile['PL'] != ''):
            self.controls[4].setEnabled(True)
            self.controls[5].setEnabled(True)
            self.controls[6].setEnabled(True)
            self.controls[4].actionPerformed = self.whenTPButtonPressed
            self.controls[5].actionPerformed = self.whenSCButtonPressed
            self.controls[6].actionPerformed = self.whenPRButtonPressed
            self.psLog.info('location ' + self.controls[0].text + ' validated, buttons activated')
        else:
            self.psLog.warning('invalid location entered')

        return

    def whenTPButtonPressed(self, event):
        '''Makes a track pattern based on the config file'''

    # Boilerplate
        trackPatternTracks = TrackPattern.Model.getAllTracks(self.controls[3])
        updatedConfigTpValues = TrackPattern.Model.updateTrackList(trackPatternTracks)
        newConfigFile = MainScriptEntities.readConfigFile('all')
        newConfigFile.update({"TP": updatedConfigTpValues})
        MainScriptEntities.updateConfigFile(newConfigFile)
        selectedTracks = TrackPattern.Model.getSelectedTracks()
        self.psLog.info('tp button boilerplate completed')
    # Button specific
        trackPatternDict = TrackPattern.Model.makeTrackPatternDict(selectedTracks)
        trackPatternDict.update({'RT': u'Track Pattern for Location'})
        location = trackPatternDict['YL']
        trackPatternJson = TrackPattern.Model.writePatternJson(location, trackPatternDict)
        self.psLog.info('Track Pattern for ' + location + ' JSON file written')
        textSwitchList = TrackPattern.Model.writeTextSwitchList(location, trackPatternDict)
        self.psLog.info('Track Pattern for ' + location + ' switch list file written')
        if (jmri.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled()):
            csvSwitchList = TrackPattern.Model.writeCsvSwitchList(location, trackPatternDict)
            self.psLog.info('Track Pattern for ' + location + ' CSV file written')
        TrackPattern.View.displayTextSwitchlist(location)

        return

    def whenSCButtonPressed(self, event):
        '''Opens a set cars window for each checked track'''

    # Boilerplate
        trackPatternTracks = TrackPattern.Model.getAllTracks(self.controls[3])
        updatedConfigTpValues = TrackPattern.Model.updateTrackList(trackPatternTracks)
        ignoreAllFlag = self.controls[2].selected # user input for ignore length flag
        updatedConfigTpValues.update({"PI": ignoreAllFlag})
        newConfigFile = MainScriptEntities.readConfigFile('all')
        newConfigFile.update({"TP": updatedConfigTpValues})
        MainScriptEntities.updateConfigFile(newConfigFile)
        selectedTracks = TrackPattern.Model.getSelectedTracks()
        self.psLog.info('sc button boilerplate completed')
    # Button specific
        TrackPattern.MakeSetCarsForms.MakeFormWindows(self.controls[0].text, selectedTracks).runScript()
        self.psLog.info('Set Cars windows for ' + location + ' created')

        return

    def whenPRButtonPressed(self, event):
        '''Displays the pattern report log file in a notepad window'''

        TrackPattern.View.displayPatternLog()

        return

    def makeFrame(self):
        '''Makes the title boarder frame'''

        self.patternFrame = TrackPattern.View.manageGui().makeFrame()
        self.psLog.info('track pattern makeFrame completed')

        return self.patternFrame

    def makePanel(self):
        '''Make and activate the Track Pattern objects'''

        self.panel, self.controls = TrackPattern.View.manageGui().makePanel()
        self.controls[0].actionPerformed = self.whenTPEnterPressed
        self.configFile = MainScriptEntities.readConfigFile('TP')
        if (self.configFile['PL'] != ''):
            self.controls[4].setEnabled(True)
            self.controls[5].setEnabled(True)
            self.controls[6].setEnabled(True)
            self.controls[4].actionPerformed = self.whenTPButtonPressed
            self.controls[5].actionPerformed = self.whenSCButtonPressed
            self.controls[6].actionPerformed = self.whenPRButtonPressed
            self.psLog.info('saved location validated, buttons activated')
        self.psLog.info('track pattern makePanel completed')

        return self.panel

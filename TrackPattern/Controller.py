# coding=utf-8
# Extended ìÄÅÉî
# Controller script for the track pattern subroutine
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import TrackPattern.View
import TrackPattern.Model
import TrackPattern.SetCars

class StartUp:
    '''Start the the Track Pattern subroutine'''

    def __init__(self):
        pass

        return

    def whenTPEnterPressed(self, event):
        '''When enter is pressed for Yard Pattern box'''

        updatedConfigTpValues = TrackPattern.Model.validateUserInput(self.controls)
        newConfigFile = MainScriptEntities.readConfigFile('all')
        newConfigFile.update({"TP": updatedConfigTpValues})
        MainScriptEntities.updateConfigFile(newConfigFile)
        self.panel, self.controls = TrackPattern.View.manageGui().updatePanel(self.panel)
        self.controls[0].actionPerformed = self.whenTPEnterPressed
        self.configFile = MainScriptEntities.readConfigFile('TP')
        if (self.configFile['PL'] != ''):
            self.controls[4].setEnabled(True)
            self.controls[5].setEnabled(True)
            self.controls[4].actionPerformed = self.whenTPButtonPressed
            self.controls[5].actionPerformed = self.whenSCButtonPressed

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
    # Button specific
        trackPatternDict = TrackPattern.Model.makeTrackPatternDict(selectedTracks)
        trackPatternDict.update({'RT': u'Track Pattern for Location'})
        location = trackPatternDict['YL']
        trackPatternJson = TrackPattern.Model.writePatternJson(location, trackPatternDict)
        textSwitchList = TrackPattern.Model.writeTextSwitchList(location, trackPatternDict)
        if (jmri.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled()):
            csvSwitchList = TrackPattern.Model.writeCsvSwitchList(location, trackPatternDict)
        TrackPattern.View.displayTextSwitchlist(location)

        return

    def whenSCButtonPressed(self, event):
        '''Opens a set cars window for each checked track'''

    # Boilerplate
        trackPatternTracks = TrackPattern.Model.getAllTracks(self.controls[3])
        updatedConfigTpValues = TrackPattern.Model.updateTrackList(trackPatternTracks)
        newConfigFile = MainScriptEntities.readConfigFile('all')
        newConfigFile.update({"TP": updatedConfigTpValues})
        MainScriptEntities.updateConfigFile(newConfigFile)
        selectedTracks = TrackPattern.Model.getSelectedTracks()
    # Button specific
        # destTrackList = []
        # for destTrack in self.trackBoxList:
        #     destTrackList.append(destTrack.text)
        # # pass in the location, valid tracks, selected tracks, ignore length flag
        # print(self.controls[0].text, selectedTracks)
        TrackPattern.SetCars.makeSetCarsForm(self.controls[0].text, selectedTracks).runScript()

        return

    def makeFrame(self):
        '''Makes the title boarder frame'''

        self.patternFrame = TrackPattern.View.manageGui().makeFrame()

        return self.patternFrame

    def makePanel(self):
        '''Make and activate the Track Pattern objects'''

        self.panel, self.controls = TrackPattern.View.manageGui().makePanel()
        self.controls[0].actionPerformed = self.whenTPEnterPressed
        self.configFile = MainScriptEntities.readConfigFile('TP')
        if (self.configFile['PL'] != ''):
            self.controls[4].setEnabled(True)
            self.controls[5].setEnabled(True)
            self.controls[4].actionPerformed = self.whenTPButtonPressed
            self.controls[5].actionPerformed = self.whenSCButtonPressed

        return self.panel

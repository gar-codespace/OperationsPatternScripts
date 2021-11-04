# Container to run the pattern scripts
# by Greg Ritacco
# use and abuse this as you see fit

import jmri
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import TrackPattern.View
import TrackPattern.Model

class StartUp:
    '''Start the the Track Pattern subroutine'''

    def __init__(self):
        pass

        return

    def whenTPEnterPressed(self, event):
        '''When enter is pressed for Yard Pattern box'''

        configFile = TrackPattern.Model.validateUserInput(self.controls)
        MainScriptEntities.updateConfigFile(configFile)
        self.panel, self.controls = TrackPattern.View.manageGui().updatePanel(self.panel)
        self.controls[0].actionPerformed = self.whenTPEnterPressed
        configFile = MainScriptEntities.readConfigFile()
        self.configFile = configFile['TP']
        if (self.configFile['PL'] != ''):
            self.controls[4].setEnabled(True)
            self.controls[5].setEnabled(True)
            self.controls[4].actionPerformed = self.whenTPButtonPressed
            self.controls[5].actionPerformed = self.whenSCButtonPressed

        return

    def whenTPButtonPressed(self, event):
        '''Makes a track pattern based on the config file'''

        trackPatternTracks = TrackPattern.Model.getAllTracks(self.controls[3])
        configFile = TrackPattern.Model.updateTrackList(trackPatternTracks)
        MainScriptEntities.updateConfigFile(configFile)
        selectedTracks = TrackPattern.Model.getSelectedTracks()
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
        '''When the Set button is pressed'''

        trackPatternTracks = TrackPattern.Model.getTracks(self.controls[3])
        configFile = TrackPattern.Model.updateTrackList(trackPatternTracks)
        MainScriptEntities.updateConfigFile(configFile)
        selectedTracks = TrackPattern.Model.getSelectedTracks()
        destTrackList = []
        for destTrack in self.trackBoxList:
            destTrackList.append(destTrack.text)
        # pass in the location, valid tracks, selected tracks, ignore length flag
        SC.setCars(self.patternInput.text, self.useTheseTracks()).runScript()
        return

    def makeFrame(self):
        '''Makes the title boarder frame'''

        self.patternFrame = TrackPattern.View.manageGui().makeFrame()

        return self.patternFrame

    def makePanel(self):
        '''Make and activate the Track Pattern objects'''

        self.panel, self.controls = TrackPattern.View.manageGui().makePanel()
        self.controls[0].actionPerformed = self.whenTPEnterPressed
        configFile = MainScriptEntities.readConfigFile()
        self.configFile = configFile['TP']
        if (self.configFile['PL'] != ''):
            self.controls[4].setEnabled(True)
            self.controls[5].setEnabled(True)
            self.controls[4].actionPerformed = self.whenTPButtonPressed
            self.controls[5].actionPerformed = self.whenSCButtonPressed

        return self.panel

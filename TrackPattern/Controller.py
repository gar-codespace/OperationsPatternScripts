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
import TrackPattern.ViewSetCarsForm

class StartUp:
    '''Start the the Track Pattern subroutine'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.Control')
        self.rev = 'TrackPattern.Controller v20211101'

        return

    def whenTPEnterPressed(self, event):
        '''When enter is pressed for Yard Pattern box'''

        self.clickOrEnter()

        return

    def whenPABoxClicked(self, event):
        '''When the Yard Tracks Only box is clicked'''

        self.clickOrEnter()

        return

    def whenTPButtonPressed(self, event):
        '''Makes a track pattern based on the config file'''

    # Boilerplate - update the config file
        self.buttonBoilerplate()
        self.psLog.info('Button boilerplate completed - config file updated')
    # Button specific
        selectedTracks = TrackPattern.Model.getSelectedTracks()
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
        print(self.rev)

        return

    def whenSCButtonPressed(self, event):
        '''Opens a set cars window for each checked track'''

    # Boilerplate - update the config file
        self.buttonBoilerplate()
        self.psLog.info('Button boilerplate completed - config file updated')
    # Button specific
        selectedTracks = TrackPattern.Model.getSelectedTracks()
        TrackPattern.ViewSetCarsForm.MakeFormWindows(self.controls[0].text, selectedTracks).runScript()
        self.psLog.info('Set Cars Windows for ' + self.controls[0].text + ' completed')
        print(self.rev)

        return

    def whenPRButtonPressed(self, event):
        '''Displays the pattern report log file in a notepad window'''

        TrackPattern.View.displayPatternLog()

        return

    def buttonBoilerplate(self):
        '''Boilerplate calls when a button is pressed'''

        focusOn = MainScriptEntities.readConfigFile('TP')
        focusOn.update({"PL": self.controls[0].text})
        focusOn.update({"PA": self.controls[1].selected})
        focusOn.update({"PI": self.controls[2].selected})
        focusOn.update({"PT": TrackPattern.Model.getAllTracks(self.controls[3])})
        newConfigFile = MainScriptEntities.readConfigFile('all')
        newConfigFile.update({"TP": focusOn})
        MainScriptEntities.updateConfigFile(newConfigFile)

        return

    def clickOrEnter(self):
        '''Bolierplate method for the text box and check box'''

        updatedConfigTpValues, validCombo = TrackPattern.Model.validateUserInput(self.controls)
        newConfigFile = MainScriptEntities.readConfigFile('all')
        newConfigFile.update({"TP": updatedConfigTpValues})
        MainScriptEntities.updateConfigFile(newConfigFile)
        self.panel, self.controls = TrackPattern.View.manageGui().updatePanel(self.panel)
        self.controls[0].actionPerformed = self.whenTPEnterPressed
        self.controls[1].actionPerformed = self.whenPABoxClicked
        self.controls[6].actionPerformed = self.whenPRButtonPressed # the log button is always active
        if (validCombo):
            self.controls[4].setEnabled(True)
            self.controls[5].setEnabled(True)
            self.controls[4].actionPerformed = self.whenTPButtonPressed
            self.controls[5].actionPerformed = self.whenSCButtonPressed
            self.psLog.info('location ' + self.controls[0].text + ' validated, buttons activated')
        print(self.rev)
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
        self.controls[1].actionPerformed = self.whenPABoxClicked
        self.controls[6].actionPerformed = self.whenPRButtonPressed
        self.configFile = MainScriptEntities.readConfigFile('TP')
        if (self.configFile['PL'] != ''):
            self.controls[4].setEnabled(True)
            self.controls[5].setEnabled(True)
            self.controls[4].actionPerformed = self.whenTPButtonPressed
            self.controls[5].actionPerformed = self.whenSCButtonPressed
            self.psLog.info('saved location validated, buttons activated')
        self.psLog.info('track pattern makePanel completed')

        return self.panel

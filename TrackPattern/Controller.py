# coding=utf-8
# Extended ìÄÅÉî
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import logging
import java.awt.event
from os import path as oPath

print(oPath.dirname(oPath.abspath(__file__)) + ' ***^^^^^^^^^^^^****')
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import TrackPattern.Model
import TrackPattern.View

'''Controller script for the track pattern subroutine'''

scriptRev = 'TrackPattern.Controller v20211210'

class StartUp():
    '''Start the the Track Pattern subroutine'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.Control')

        return

    class ComboBoxListener(java.awt.event.ActionListener):
        '''Event triggered from location combobox selection'''

        def __init__(self, panel, controls):
            self.panel = panel
            self.controls = controls
            self.psLog = logging.getLogger('PS.TP.ComboBox')

        def actionPerformed(self, event):
            try:
                newConfigFile = TrackPattern.Model.updatePatternLocation(event.getSource().getSelectedItem())
                MainScriptEntities.writeConfigFile(newConfigFile)
                newConfigFile = TrackPattern.Model.makeNewPatternTracks(event.getSource().getSelectedItem())
                self.psLog.info('The track list for location ' + event.getSource().getSelectedItem() + ' has been created')
                MainScriptEntities.writeConfigFile(newConfigFile)
                newConfigFile = TrackPattern.Model.updateCheckBoxStatus(False, self.controls[2].selected)
                MainScriptEntities.writeConfigFile(newConfigFile)
                self.controls = TrackPattern.View.ManageGui().updatePanel(self.panel)
                StartUp().activateButtons(self.panel, self.controls)
        # catch the error when the user edits the location name
            except AttributeError:
                newConfigFile = TrackPattern.Model.initializeConfigFile()
                MainScriptEntities.writeConfigFile(newConfigFile)
                self.controls = TrackPattern.View.ManageGui().updatePanel(self.panel)
                StartUp().activateButtons(self.panel, self.controls)
                self.psLog.warning('Location list changed, config file updated')

            print(scriptRev)

            return

    def whenPABoxClicked(self, event):
        '''When the Yard Tracks Only box is clicked'''

        if (self.controls[1].selected):
            trackList = TrackPattern.Model.makeTrackList(self.controls[0].getSelectedItem(), 'Yard')
        else:
            trackList = TrackPattern.Model.makeTrackList(self.controls[0].getSelectedItem(), None)
        newConfigFile = TrackPattern.Model.updatePatternLocation(self.controls[0].getSelectedItem())
        MainScriptEntities.writeConfigFile(newConfigFile)
        newConfigFile = TrackPattern.Model.updatePatternTracks(trackList)
        MainScriptEntities.writeConfigFile(newConfigFile)
        newConfigFile = TrackPattern.Model.updateCheckBoxStatus(self.controls[1].selected, self.controls[2].selected)
        MainScriptEntities.writeConfigFile(newConfigFile)
        self.controls = TrackPattern.View.ManageGui().updatePanel(self.panel)
        self.activateButtons(self.panel, self.controls)

        return

    def whenTPButtonPressed(self, event):
        '''Makes a track pattern report based on the config file'''

        TrackPattern.Model.updateConfigFile(self.controls)
        self.psLog.info('Configuration file updated with new settings for controls')
    # Button specific
        try:
            location = TrackPattern.Model.onTpButtonPress()
            TrackPattern.View.displayTextSwitchlist(location)
        except:
            # error handled in Model.onTpButtonPress()
            pass
        print(scriptRev)

        return

    def whenSCButtonPressed(self, event):
        '''Opens a set cars window for each checked track'''

        self.controls = TrackPattern.Model.updateConfigFile(self.controls)
        self.psLog.info('Configuration file updated with new settings for controls')

        TrackPattern.Model.makeLoadEmptyDesignationsDicts()
    # Button specific
        TrackPattern.Model.onScButtonPress()
        print(scriptRev)

        return

    def whenPRButtonPressed(self, event):
        '''Displays the pattern report log file in a notepad window'''

        TrackPattern.Model.makePatternLog()
        TrackPattern.View.printPatternLog()
        print(scriptRev)

        return

    def activateButtons(self, panel, controls):
        '''Assigns actions to the subroutine widgets'''

        self.panel = panel
        self.controls = controls
        self.controls[0].addActionListener(self.ComboBoxListener(panel, controls))
        self.controls[1].actionPerformed = self.whenPABoxClicked
        self.controls[4].actionPerformed = self.whenTPButtonPressed
        self.controls[5].actionPerformed = self.whenSCButtonPressed
        self.controls[6].actionPerformed = self.whenPRButtonPressed

        return

    def makeSubroutineFrame(self):
        '''Makes the title border frame'''

        patternFrame = TrackPattern.View.ManageGui().makeFrame()
        self.psLog.info('track pattern makeFrame completed')

        return patternFrame

    def makeSubroutinePanel(self):
        '''Make and activate the Track Pattern objects'''

        MainScriptEntities.writeConfigFile(TrackPattern.Model.updateLocations())
        panel, controls = TrackPattern.View.ManageGui().makePanel()
        self.activateButtons(panel, controls)
        self.psLog.info('track pattern makeSubroutinePanel completed')

        return panel

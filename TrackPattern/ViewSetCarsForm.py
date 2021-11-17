# coding=utf-8
# Extended ìÄÅÉî
# Makes a set cars form for each selected track
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
import javax.swing
import logging
import time
from codecs import open as cOpen
from os import system
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern')
import MainScriptEntities
import TrackPattern.ViewEntities
import TrackPattern.ModelEntities

class SetCarsWindowInstance():
    '''Manages an instance of each -Pattern Report for track- window'''

# Class variables
    scriptRev = 'SetCarsWindowInstance v20210901'

    def __init__(self, pattern, schedule):
        '''Initialization variables'''

        self.psLog = logging.getLogger('PS.CarsForm')
    # Boilerplate
        self.lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        self.cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
        self.profilePath = jmri.util.FileUtil.getProfilePath()
        self.configFile = MainScriptEntities.readConfigFile('TP')
    # Track variables
        self.trackData = pattern # all the data for the selected track, car roster is sorted
        self.trackSchedule = schedule
        self.allTracksAtLoc = [] # all the tracks for that location
        self.ignoreLength = False # initial setting, user changes this setting
    # Lists for reports
        self.jTextIn = [] # create a list jTextField objects
        self.carDataList = [] # list of sorted car objects

    def setCarsToTrack(self, event):
        '''Event that moves cars to the tracks entered in the pattern window'''

    # set the cars to a track
        self.ignoreLength = self.configFile['PI'] # flag to ignore track length
        patternCopy = self.trackData # all the data for just one track
        # self.allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(patternCopy['YL'], None)
        userInputList = [] # create a list of user inputs from the text input boxes
        for userInput in self.jTextIn: # Read in and check the user input
            userInputList.append(unicode(userInput.getText(), MainScriptEntities.setEncoding()))

        i = 0
        for z in patternCopy['ZZ']:
            if (len(userInputList) == len(z['TR'])): # check that the lengths of the -input list- and -car roster- match
                self.psLog.info('input list and car roster lengths match')
            else:
                self.psLog.critical('mismatched input list and car roster lengths')
            trackName = unicode(z['TN'], MainScriptEntities.setEncoding())
            setToLocation = self.lm.getLocationByName(unicode(patternCopy['YL'], MainScriptEntities.setEncoding()))
            j = 0
            for y in z['TR']:
                if (userInputList[i] in self.allTracksAtLoc and userInputList[i] != trackName):
                    setToTrack = setToLocation.getTrackByName(unicode(userInputList[i], MainScriptEntities.setEncoding()), None)
                    setCarId = self.cm.newRS(y['Road'], y['Number'])
                    setCarId.setLocation(setToLocation, setToTrack, self.ignoreLength)
                    j += 1
                i += 1
            self.psLog.info(str(j) + ' cars were set from track ' + trackName)
    # Wrap it up
        self.setCarsWindow.setVisible(False)
        return

    def printYP(self, event):
        '''Event that prints the yard pattern for the selected track'''

    # Make the switch list
        patternCopy = self.trackData
        userInputList = [] # create a list of user inputs for the set car destinations
        for userInput in self.jTextIn: # Read in the user input
            userInputList.append(unicode(userInput.getText(), MainScriptEntities.setEncoding()))
        i = 0
        for z in patternCopy['ZZ']:
            if (len(userInputList) == len(z['TR'])): # check that the lengths of the input list and car roster match
                self.psLog.info('input list and car roster lengths match')
            else:
                self.psLog.critical('mismatched input list and car roster lengths')
            trackName = unicode(z['TN'], MainScriptEntities.setEncoding())
            # self.allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(patternCopy['YL'], None)
            for y in z['TR']:
                setTrack = unicode('Hold', MainScriptEntities.setEncoding())
                if (userInputList[i] in self.allTracksAtLoc and userInputList[i] != trackName):
                    setTrack = unicode(userInputList[i], MainScriptEntities.setEncoding())
                setTrack = TrackPattern.ModelEntities.formatText(' [' + setTrack + '] ', 8)
                y.update({'Set to': setTrack}) # replaces empty brackets with the marked ones
                i += 1
    # Print the switch list
        textSwitchList = TrackPattern.ModelEntities.makeSwitchlist(patternCopy, False)
        textCopyTo = self.profilePath + 'operations\\switchLists\\Switch list (' + patternCopy['YL'] + ') (' + trackName + ').txt'
        with cOpen(textCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as textWorkFile:
            textWorkFile.write(textSwitchList)
        system(MainScriptEntities.systemInfo() + textCopyTo)
    # Print the CSV switch list
        if (jmri.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled()):
            csvSwitchList = TrackPattern.ModelEntities.makeCsvSwitchlist(patternCopy)
            csvCopyTo = self.profilePath + 'operations\\csvSwitchLists\\Switch list (' + patternCopy['YL'] + ') (' + trackName + ').csv'
            with cOpen(csvCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as csvWorkFile:
                csvWorkFile.write(csvSwitchList)

        return

    def trackButton(self, event):
        '''When any one of the track buttons is pressed'''

        thisButton = event.getSource().getText()
        print(thisButton)
        return

    def setCarsForTrackWindow(self, xOffset):
        ''' Creates and populates the -Pattern Report for Track- window'''

        configFile = MainScriptEntities.readConfigFile('TP')
    # Make a button for every track at the location
        self.allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(self.trackData['YL'], None)
        buttonPanel = javax.swing.JPanel()
        buttonPanel.setLayout(javax.swing.BoxLayout(buttonPanel, javax.swing.BoxLayout.X_AXIS))
        self.trackButtonList = []
        for track in self.allTracksAtLoc:
            selectTrackButton = javax.swing.JButton(track)
            selectTrackButton.setPreferredSize(java.awt.Dimension(0,18))
            buttonPanel.add(selectTrackButton)
            self.trackButtonList.append(selectTrackButton)
            selectTrackButton.actionPerformed = self.trackButton
    # Define the window
        trackName = self.trackData['ZZ']
        trackName = trackName[0]
        trackName = unicode(trackName['TN'], MainScriptEntities.setEncoding())
    # Define the form
        combinedForm = javax.swing.JPanel()
        combinedForm.setLayout(javax.swing.BoxLayout(combinedForm, javax.swing.BoxLayout.Y_AXIS))
        combinedForm.setAlignmentX(java.awt.Component.CENTER_ALIGNMENT)
        bodyHeader, headerWidth = TrackPattern.ViewEntities.setCarsFormBodyHeader()
        combinedForm.add(bodyHeader)
        formBody, self.jTextIn = TrackPattern.ViewEntities.setCarsFormBody(self.trackData)
        combinedForm.add(formBody)
        scrollPanel = javax.swing.JScrollPane(combinedForm)
        scrollPanel.border = javax.swing.BorderFactory.createEmptyBorder(2,2,2,2)
    # Make the footer
        combinedFooter, tpButton, scButton = TrackPattern.ViewEntities.setCarsFormFooter()
        tpButton.actionPerformed = self.printYP
        scButton.actionPerformed = self.setCarsToTrack
    # Construct the window
        self.setCarsWindow = TrackPattern.ViewEntities.makeWindow()
        self.setCarsWindow.setTitle(u'Pattern Report for track ' + trackName)
        self.setCarsWindow.setLocation(xOffset, 150)
        formHeader = TrackPattern.ViewEntities.setCarsFormHeader(self.trackData)
        formHeader.border = javax.swing.BorderFactory.createEmptyBorder(5,0,5,0)
        # formHeader.add(javax.swing.JLabel(u'Schedule: ' + deg.getName()))
        self.setCarsWindow.add(formHeader)
        self.setCarsWindow.add(javax.swing.JSeparator())
        self.setCarsWindow.add(buttonPanel)
        self.setCarsWindow.add(javax.swing.JSeparator())
        self.setCarsWindow.add(scrollPanel)
        self.setCarsWindow.add(javax.swing.JSeparator())
        if (self.trackSchedule):
            scheduleName = self.trackSchedule.getName()
            schedulePanel = javax.swing.JPanel()
            schedulePanel.setAlignmentX(java.awt.Component.CENTER_ALIGNMENT)
            schedulePanel.add(javax.swing.JLabel(u'Schedule: ' + scheduleName))
            self.setCarsWindow.add(schedulePanel)
            self.setCarsWindow.add(javax.swing.JSeparator())
        self.setCarsWindow.add(combinedFooter)
        self.setCarsWindow.pack()
        self.setCarsWindow.setVisible(True)
        # print(SetCarsWindowInstance.scriptRev)
        return

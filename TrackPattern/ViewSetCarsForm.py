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
    scriptRev = 'SetCarsWindowInstanceV1 rev.20210901'

    def __init__(self, pattern):
        '''Initialization variables'''

        self.psLog = logging.getLogger('PS.CarsForm')
    # Boilerplate
        self.lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        self.cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
        self.profilePath = jmri.util.FileUtil.getProfilePath()
        self.configFile = MainScriptEntities.readConfigFile('TP')
    # Track variables
        self.trackData = pattern # all the data for the selected track, car roster is sorted
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
        self.allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(patternCopy['YL'], None)
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
            self.allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(patternCopy['YL'], None)
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

    def setCarsForTrackWindow(self, xOffset):
        ''' Creates and populates the -Pattern Report for Track- window'''

    # Read in the config file
        configFile = MainScriptEntities.readConfigFile('TP')
    # Define the window
        trackName = self.trackData['ZZ']
        trackName = trackName[0]
        trackName = unicode(trackName['TN'], MainScriptEntities.setEncoding())
        self.setCarsWindow = TrackPattern.ViewEntities.makeWindow()
        self.setCarsWindow.setTitle(u'Pattern Report for track ' + trackName)
        self.setCarsWindow.setLocation(xOffset, 150)
        self.setCarsWindow.setSize(400,500)
        formSeparator = javax.swing.JSeparator()

    # Define the form
        combinedForm = javax.swing.JPanel()
        combinedForm.setLayout(javax.swing.BoxLayout(combinedForm, javax.swing.BoxLayout.Y_AXIS))
        combinedForm.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
        combinedForm.add(TrackPattern.ViewEntities.setCarsFormBodyHeader())
        formBody, self.jTextIn = TrackPattern.ViewEntities.setCarsFormBody(self.trackData)
        combinedForm.add(formBody)
    # Make the footer
        combinedFooter, tpButton, scButton = TrackPattern.ViewEntities.setCarsFormFooter()
        tpButton.actionPerformed = self.printYP
        scButton.actionPerformed = self.setCarsToTrack
    # Construct the window
        self.setCarsWindow.add(TrackPattern.ViewEntities.setCarsFormHeader(self.trackData))
        # self.setCarsWindow.add(formSeparator)
        self.setCarsWindow.add(combinedForm)
        self.setCarsWindow.add(formSeparator)
        self.setCarsWindow.add(combinedFooter)
        self.setCarsWindow.pack()
        self.setCarsWindow.setVisible(True)
        # print(SetCarsWindowInstance.scriptRev)
        return

class MakeFormWindows():
    '''Create and open a set cars window for each track selected'''

    scriptRev = 'TrackPattern.ViewSetCarsForm v20211101'

    def __init__(self, xYard, xTracks):
        '''Initialization variables'''

    # Script specific
        self.psLog = logging.getLogger('PS.CarsWindow')
        self.profilePath = jmri.util.FileUtil.getProfilePath()
        self.yardLoc = xYard
        self.selectedTracks = xTracks
        self.yardTrackType = None

        return

    def runScript(self):
        '''Run the program'''

    # Set initial variables
        yTimeNow = time.time()
        windowOffset = 200
    # create an instance for each track in its own window
        for track in self.selectedTracks:
            listForTrack = TrackPattern.ModelEntities.makeYardPattern([track], self.yardLoc) # track needs to be send in as a list
            listForTrack.update({'RT': u'Switch List for Track '})
            newWindow = SetCarsWindowInstance(listForTrack)
            newWindow.setCarsForTrackWindow(windowOffset)
            self.psLog.info(u'Set Cars Window created for track ' + track)
            windowOffset += 50
    # wrap up the script
        computeTime = u'Set Cars windows run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6]
        self.psLog.info(computeTime)
        print(self.scriptRev)
        return

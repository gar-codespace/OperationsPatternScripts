# coding=utf-8
# Extended ìÄÅÉî
# Makes a set cars form for each selected track
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
import java.awt.event
import javax.swing
import logging
from codecs import open as cOpen
from os import system
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern')
import MainScriptEntities
import TrackPattern.ViewEntities
import TrackPattern.ModelEntities

class AnyButtonPressedListener(java.awt.event.ActionListener):

    def __init__(self, scheduleObject=None, trackObject=None):

        self.scheduleObject = scheduleObject
        self.trackObject = trackObject

        return

    def trackButton(self, MOUSE_CLICKED):

        MainScriptEntities.trackNameClickedOn = unicode(MOUSE_CLICKED.getSource().getText(), MainScriptEntities.setEncoding())

        return

    def scheduleButton(self, MOUSE_CLICKED):

        jmri.jmrit.operations.locations.schedules.ScheduleEditFrame(self.scheduleObject, self.trackObject)

        return

class SetCarsWindowInstance():
    '''Manages an instance of each -Pattern Report for track- window'''

# Class variables
    scriptRev = 'TrackPattern.ViewSetCarsForm v20211125'

    def __init__(self, pattern):

        self.psLog = logging.getLogger('PS.TP.CarsForm')
    # Boilerplate
        self.lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        self.cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
        self.profilePath = jmri.util.FileUtil.getProfilePath()
        self.configFile = MainScriptEntities.readConfigFile('TP')
    # Track variables
        self.trackData = pattern # all the data for the selected track, car roster is sorted
        self.allTracksAtLoc = [] # all the tracks for this location
        self.ignoreLength = False # initial setting, user changes this
        self.isASpur = False
        self.hasASchedule = False
    # Lists for reports
        self.jTextIn = [] # create a list jTextField objects
        self.carDataList = [] # list of sorted car objects

        return

    def setCarsToTrack(self, MOUSE_CLICK):
        '''Event that moves cars to the tracks entered in the pattern window'''

    # set the cars to a track
        self.ignoreLength = self.configFile['PI'] # flag to ignore track length
        patternCopy = self.trackData # all the data for just one track
        userInputList = [] # create a list of user inputs from the text input boxes
        for userInput in self.jTextIn: # Read in and check the user input
            userInputList.append(unicode(userInput.getText(), MainScriptEntities.setEncoding()))
        i = 0
        for z in patternCopy['ZZ']:
            if (len(userInputList) == len(z['TR'])): # check that the lengths of the -input list- and -car roster- match
                self.psLog.info('input list and car roster lengths match')
                trackName = unicode(z['TN'], MainScriptEntities.setEncoding())
                setToLocation = self.lm.getLocationByName(unicode(patternCopy['YL'], MainScriptEntities.setEncoding()))
                scheduleObject, trackObject = TrackPattern.ModelEntities.getScheduleForTrack(patternCopy['YL'], trackName)
                j = 0
                for y in z['TR']:
                    if (userInputList[i] in self.allTracksAtLoc and userInputList[i] != trackName):
                        setToTrack = setToLocation.getTrackByName(unicode(userInputList[i], MainScriptEntities.setEncoding()), None)
                        setCarId = self.cm.newRS(y['Road'], y['Number'])
                        setResult = setCarId.setLocation(setToLocation, setToTrack, self.ignoreLength)
                        if (setResult == 'okay'):
                            if (self.isASpur):
                                TrackPattern.ModelEntities.applyShippingRubric(setCarId, scheduleObject)
                        else:
                            self.psLog.warning(setCarId.getRoadName() + ' ' + setCarId.getNumber() + ' not set exception: ' + setResult)
                        j += 1
                    i += 1
                self.psLog.info(str(j) + ' cars were processed from track ' + trackName)
                jmri.jmrit.operations.rollingstock.cars.CarManagerXml.save()
            else:
                self.psLog.critical('mismatched input list and car roster lengths')
    # Wrap it up
        self.setCarsWindow.setVisible(False)
        print(SetCarsWindowInstance.scriptRev)

        return

    def printYP(self, MOUSE_CLICK):
        '''Event that prints the yard pattern for the selected track'''

        TrackPattern.ModelEntities.makeCarTypeByEmptyDict()
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
        print(SetCarsWindowInstance.scriptRev)

        return

    def setCarsForTrackWindow(self, xOffset):
        ''' Creates and populates the -Pattern Report for Track- window'''

        configFile = MainScriptEntities.readConfigFile('TP')

    #Boilerplate
        trackName = self.trackData['ZZ']
        trackName = trackName[0]
        trackName = unicode(trackName['TN'], MainScriptEntities.setEncoding())
        trackLocation = unicode(self.trackData['YL'], MainScriptEntities.setEncoding())
        self.allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(trackLocation, None)
        self.isASpur, self.hasASchedule = TrackPattern.ModelEntities.makeSpurScheduleMatrix(trackLocation, trackName)
    # Create the forms header
        formHeader = TrackPattern.ViewEntities.setCarsFormHeader(self.trackData)
        formHeader.border = javax.swing.BorderFactory.createEmptyBorder(5,0,5,0)
    # create the row of track buttons
        buttonPanel = javax.swing.JPanel()
        buttonPanel.setLayout(javax.swing.BoxLayout(buttonPanel, javax.swing.BoxLayout.X_AXIS))
        for trackButton in TrackPattern.ViewEntities.makeTrackButtonRow(self.allTracksAtLoc):
            buttonPanel.add(trackButton)
            trackButton.actionPerformed = AnyButtonPressedListener().trackButton
    # Create the car list part of the form
        combinedForm = javax.swing.JPanel()
        combinedForm.setLayout(javax.swing.BoxLayout(combinedForm, javax.swing.BoxLayout.Y_AXIS))
        combinedForm.setAlignmentX(java.awt.Component.CENTER_ALIGNMENT)
        bodyHeader, headerWidth = TrackPattern.ViewEntities.setCarsFormBodyHeader()
        combinedForm.add(bodyHeader)
        formBody, self.jTextIn = TrackPattern.ModelEntities.setCarsFormBody(self.trackData)
        combinedForm.add(formBody)
        scrollPanel = javax.swing.JScrollPane(combinedForm)
        scrollPanel.border = javax.swing.BorderFactory.createEmptyBorder(2,2,2,2)
    # Create the schedule row
        scheduleObject, trackObject = TrackPattern.ModelEntities.getScheduleForTrack(trackLocation, trackName)
        if (scheduleObject):
            schedulePanel = javax.swing.JPanel()
            schedulePanel.setLayout(javax.swing.BoxLayout(schedulePanel, javax.swing.BoxLayout.X_AXIS))
            scheduleButton = javax.swing.JButton(scheduleObject.getName())
            scheduleButton.setPreferredSize(java.awt.Dimension(0,18))
            scheduleButton.actionPerformed = AnyButtonPressedListener(scheduleObject, trackObject).scheduleButton
            schedulePanel.add(javax.swing.JLabel(u'Schedule: '))
            schedulePanel.add(scheduleButton)
    # Create the footer
        combinedFooter, tpButton, scButton = TrackPattern.ViewEntities.setCarsFormFooter()
        tpButton.actionPerformed = self.printYP
        scButton.actionPerformed = self.setCarsToTrack
    # Put it all together
        self.setCarsWindow = TrackPattern.ViewEntities.makeWindow()
        self.setCarsWindow.setTitle(u'Pattern Report for track ' + trackName)
        self.setCarsWindow.setLocation(xOffset, 180)
        self.setCarsWindow.add(formHeader)
        self.setCarsWindow.add(javax.swing.JSeparator())
        self.setCarsWindow.add(buttonPanel)
        self.setCarsWindow.add(javax.swing.JSeparator())
        self.setCarsWindow.add(scrollPanel)
        self.setCarsWindow.add(javax.swing.JSeparator())
        if (scheduleObject):
            self.setCarsWindow.add(schedulePanel)
            self.setCarsWindow.add(javax.swing.JSeparator())
        self.setCarsWindow.add(combinedFooter)
        self.setCarsWindow.setVisible(True)
        self.setCarsWindow.pack()

        return

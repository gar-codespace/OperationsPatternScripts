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
# import TrackPattern.ModelSetCarsForm
import TrackPattern.ViewSetCarsForm
import MainScriptEntities

class AnyButtonPressedListener(java.awt.event.ActionListener):

    scriptRev = 'TrackPattern.ViewSetCarsForm v20211210'

    def __init__(self, scheduleObject=None, trackObject=None, trackData=None, jTextIn=None):

        self.scheduleObject = scheduleObject
        self.trackObject = trackObject
        self.trackData = trackData
        self.jTextIn = jTextIn

        return

    def trackRowButton(self, MOUSE_CLICKED):
        '''Any of the track buttons on the set cars window - row of track buttons'''

        MainScriptEntities.trackNameClickedOn = unicode(MOUSE_CLICKED.getSource().getText(), MainScriptEntities.setEncoding())

        return

    def scheduleButton(self, MOUSE_CLICKED):
        '''The named schedule button if displayed on any set cars window'''

        jmri.jmrit.operations.locations.schedules.ScheduleEditFrame(self.scheduleObject, self.trackObject)

        return

    def printYP(self, MOUSE_CLICK):
        '''Event that prints the yard pattern for the selected track'''

    # Set logging level
        # MainScriptEntities.setLoggingLevel(self.psLog)
        # self.psLog.setLevel(logLevel)
    # Make the switch list
        userInputList = [] # create a list of user inputs for the set car destinations
        for userInput in self.jTextIn: # Read in the user input
            userInputList.append(unicode(userInput.getText(), MainScriptEntities.setEncoding()))
        i = 0
        for z in self.trackData['ZZ']:
            if (len(userInputList) == len(z['TR'])): # check that the lengths of the input list and car roster match
                pass
                # self.psLog.debug('input list and car roster lengths match')
            else:
                pass
                # self.psLog.critical('mismatched input list and car roster lengths')
            trackLocation = self.trackData['YL']
            trackName = unicode(z['TN'], MainScriptEntities.setEncoding())
            allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(trackLocation, None)
            for y in z['TR']:
                setTrack = unicode('Hold', MainScriptEntities.setEncoding())
                if (userInputList[i] in allTracksAtLoc and userInputList[i] != trackName):
                    setTrack = unicode(userInputList[i], MainScriptEntities.setEncoding())
                setTrack = TrackPattern.ModelEntities.formatText(' [' + setTrack + '] ', 8)
                y.update({'Set to': setTrack}) # replaces empty brackets with the marked ones
                i += 1
        # print(self.trackData)
        TrackPattern.ModelEntities.printSwitchList(self.trackData)
        # print(ManageGui.scriptRev)

        return

    def setCarsToTrack(self, MOUSE_CLICK):
        '''Event that moves cars to the tracks entered in the pattern window'''

    # Set logging level
        MainScriptEntities.setLoggingLevel(self.psLog)

    # # set the cars to a track
    #     self.ignoreLength = self.configFile['PI'] # flag to ignore track length
    #     patternCopy = self.trackData # all the data for just one track
    #     userInputList = [] # create a list of user inputs from the text input boxes
    #     for userInput in self.jTextIn: # Read in and check the user input
    #         userInputList.append(unicode(userInput.getText(), MainScriptEntities.setEncoding()))
    #     i = 0
    #     for z in patternCopy['ZZ']:
    #         if (len(userInputList) == len(z['TR'])): # check that the lengths of the -input list- and -car roster- match
    #             self.psLog.debug('input list and car roster lengths match')
    #             trackName = unicode(z['TN'], MainScriptEntities.setEncoding())
    #             setToLocation = self.lm.getLocationByName(unicode(patternCopy['YL'], MainScriptEntities.setEncoding()))
    #             scheduleObject, trackObject = TrackPattern.ModelEntities.getScheduleForTrack(patternCopy['YL'], trackName)
    #             j = 0
    #             for y in z['TR']:
    #                 if (userInputList[i] in self.allTracksAtLoc and userInputList[i] != trackName):
    #                     setToTrack = setToLocation.getTrackByName(unicode(userInputList[i], MainScriptEntities.setEncoding()), None)
    #                     setCarId = self.cm.newRS(y['Road'], y['Number'])
    #                     testCarDestination = setCarId.testDestination(setToLocation, setToTrack)
    #                     if (testCarDestination == 'okay'):
    #                         setCarId.setLocation(setToLocation, setToTrack)
    #                         j += 1
    #                         continue
    #                     if (testCarDestination.startswith('track') and self.ignoreLength):
    #                         trackLength = setToTrack.getLength()
    #                         setToTrack.setLength(9999)
    #                         setCarId.setLocation(setToLocation, setToTrack)
    #                         setToTrack.setLength(trackLength)
    #                         self.psLog.warning('Track length exceeded for ' + setToTrack.getName())
    #                         j += 1
    #                     else:
    #                         self.psLog.warning(setCarId.getRoadName() + ' ' + setCarId.getNumber() + ' not set exception: ' + testCarDestination)
    #
    #                 i += 1
    #             self.psLog.info(str(j) + ' cars were processed from track ' + trackName)
    #             jmri.jmrit.operations.rollingstock.cars.CarManagerXml.save()
    #         else:
    #             self.psLog.critical('mismatched input list and car roster lengths')
    # # Wrap it up
    #     self.setCarsWindow.setVisible(False)
    #     print(ManageGui.scriptRev)

        return

class SetTrackBoxMouseListener(java.awt.event.MouseAdapter):
    '''When any of the Set Cars to Track text boxes is clicked on'''

    def __init__(self):
        pass

    def mouseClicked(self, MOUSE_CLICKED):

        try:
            MOUSE_CLICKED.getSource().setText(MainScriptEntities.trackNameClickedOn)
        except NameError:
            # add some loggong stuff
            print('No track was selected')
        return

class ManageGui():
    '''Manages an instance of each -Pattern Report for track- window'''

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

    def makeFrame(self, offSet):

        patternReportForTrackWindow = TrackPattern.ViewSetCarsForm.patternReportForTrackWindow(self.trackData, offSet)
        patternReportForTrackWindow.pack()
        patternReportForTrackWindow.setVisible(True)


        return

# coding=utf-8
# Extended ìÄÅÉî
# Makes a set cars form for each selected track
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
# import java.awt.event
import javax.swing
import logging
from codecs import open as cOpen
from os import system
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern')
import MainScriptEntities
import TrackPattern.ModelEntities


def setCarsToTrack(self, MOUSE_CLICK):
    '''Event that moves cars to the tracks entered in the pattern window'''

# Set logging level
    MainScriptEntities.setLoggingLevel(self.psLog)
# set the cars to a track
    self.ignoreLength = self.configFile['PI'] # flag to ignore track length
    patternCopy = self.trackData # all the data for just one track
    userInputList = [] # create a list of user inputs from the text input boxes
    for userInput in self.jTextIn: # Read in and check the user input
        userInputList.append(unicode(userInput.getText(), MainScriptEntities.setEncoding()))
    i = 0
    for z in patternCopy['ZZ']:
        if (len(userInputList) == len(z['TR'])): # check that the lengths of the -input list- and -car roster- match
            self.psLog.debug('input list and car roster lengths match')
            trackName = unicode(z['TN'], MainScriptEntities.setEncoding())
            setToLocation = self.lm.getLocationByName(unicode(patternCopy['YL'], MainScriptEntities.setEncoding()))
            scheduleObject, trackObject = TrackPattern.ModelEntities.getScheduleForTrack(patternCopy['YL'], trackName)
            j = 0
            for y in z['TR']:
                if (userInputList[i] in self.allTracksAtLoc and userInputList[i] != trackName):
                    setToTrack = setToLocation.getTrackByName(unicode(userInputList[i], MainScriptEntities.setEncoding()), None)
                    setCarId = self.cm.newRS(y['Road'], y['Number'])
                    testCarDestination = setCarId.testDestination(setToLocation, setToTrack)
                    if (testCarDestination == 'okay'):
                        setCarId.setLocation(setToLocation, setToTrack)
                        j += 1
                        continue
                    if (testCarDestination.startswith('track') and self.ignoreLength):
                        trackLength = setToTrack.getLength()
                        setToTrack.setLength(9999)
                        setCarId.setLocation(setToLocation, setToTrack)
                        setToTrack.setLength(trackLength)
                        self.psLog.warning('Track length exceeded for ' + setToTrack.getName())
                        j += 1
                    else:
                        self.psLog.warning(setCarId.getRoadName() + ' ' + setCarId.getNumber() + ' not set exception: ' + testCarDestination)

                i += 1
            self.psLog.info(str(j) + ' cars were processed from track ' + trackName)
            jmri.jmrit.operations.rollingstock.cars.CarManagerXml.save()
        else:
            self.psLog.critical('mismatched input list and car roster lengths')
# Wrap it up
    self.setCarsWindow.setVisible(False)
    print(SetCarsWindowInstance.scriptRev)

    return

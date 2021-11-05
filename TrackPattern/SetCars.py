# coding=utf-8
# Extended ìÄÅÉî
# Makes a set cars form for each selected track
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java
import java.awt
import javax.swing
import time
from codecs import open as cOpen
from os import system
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern')
import MainScriptEntities
import TrackPattern.ViewEntities
import TrackPattern.ModelEntities

class patternReportWindowManager():
    '''Manages an instance of each -Pattern Report for Track- window'''

# Class variables
    scriptRev = 'patternReportWindowManagerV1 rev.20210901'

    def __init__(self, pattern):
        '''Initialization variables'''

    # Boilerplate
        self.lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        self.cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
        self.profilePath = jmri.util.FileUtil.getProfilePath()
        self.configFile = MainScriptEntities.readConfigFile('TP')
    # Track variables
        self.trackData = pattern # all the data for the selected track, car roster is sorted
        self.allTracksAtLoc = [] # all the tracks for that location
        self.ignoreLength = False # force car to track regardless of track length
    # Lists for reports
        self.jTextIn = [] # create a list jTextField objects
        self.carDataList = [] # list of sorted car objects
    # Set up the logger
        # self.scLogPath = logPath # passed in
        self.scLog = 'scLog'
        self.slLog = 'slLog'
        self.logLevel = 10 # verbose
        self.logMode = 'a' # append to existing log

    def setCarsToTrack(self, event):
        '''Event that moves cars to the tracks entered in the pattern window
        Can ignore track length'''

    # Setup gplogging
        # gpLogPath = self.scLogPath
        # scLog = yUtil.gpLogging(self.scLog)
        # scHandle = scLog.gpStartLogFile(gpLogPath, self.logLevel, self.logMode)
    # set the cars to a track
        self.ignoreLength = self.configFile['PI'] # flag to ignore track length
        patternCopy = self.trackData # all the data for just one track
        self.allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(patternCopy['YL'], None)
        userInputList = [] # create a list of user inputs from the text input boxes
        for userInput in self.jTextIn: # Read in and check the user input
            userInputList.append(unicode(userInput.getText(), MainScriptEntities.setEncoding()))
        # scLog.gpInfo('*** Set cars to track')

        i = 0
        for z in patternCopy['ZZ']:
            if (len(userInputList) == len(z['TR'])): # check that the lengths of the -input list- and -car roster- match
                print(userInputList)
                # scLog.gpInfo('Number of input fields matches track roster length') # elaborate on this
            else:
                # something that happens if the lengths dont match
                pass
            trackName = unicode(z['TN'], MainScriptEntities.setEncoding())
            setToLocation = self.lm.getLocationByName(unicode(patternCopy['YL'], MainScriptEntities.setEncoding()))
            j = 0
            for y in z['TR']:
                if (userInputList[i] in self.allTracksAtLoc and userInputList[i] != trackName):
                    setToTrack = setToLocation.getTrackByName(unicode(userInputList[i], MainScriptEntities.setEncoding()), None)
                    setCarId = self.cm.newRS(y['Road'], y['Number'])
                    print(self.ignoreLength)
                    setCarId.setLocation(setToLocation, setToTrack, self.ignoreLength)
                    # scLog.gpInfo('Set car (' + unicode(setCarId, MainScriptEntities.setEncoding()) + ') to track (' + unicode(setToTrack, MainScriptEntities.setEncoding()) + ')')
                    j += 1
                i += 1
            # scLog.gpInfo(str(j) + ' cars were set')
    # Wrap it up
        self.setCarsWindow.setVisible(False)
        # scLog.gpInfo('Time run: ' + str(time.time()))
        # scLog.gpStopLogFile(scHandle)
        return

    def printYP(self, event):
        '''Event that prints the yard pattern for the selected track'''

    # Set up gpLogging
        # gpLogPath = self.scLogPath
        # slLog = yUtil.gpLogging(self.slLog)
        # scHandle = slLog.gpStartLogFile(gpLogPath, self.logLevel, self.logMode)
        # slLog.gpInfo('*** Switch List, create switch list for print')
    # Make the switch list
        patternCopy = self.trackData
        userInputList = [] # create a list of user inputs for the set car destinations
        for userInput in self.jTextIn: # Read in the user input
            userInputList.append(unicode(userInput.getText(), MainScriptEntities.setEncoding()))
        i = 0
        for z in patternCopy['ZZ']:
            if (len(userInputList) == len(z['TR'])): # check that the lengths of the input list and car roster match
                pass
                # slLog.gpInfo('Lengths of the input list and car roster match') # elaborate on this
            trackName = z['TN']
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
            # slLog.gpInfo('Write CSV switch list for track (' + trackName + ')')
    # Wrap it up
        # slLog.gpInfo('Make switch list for print - track (' + trackName + ')')
        # slLog.gpInfo('Time run: ' + str(time.time()))
        # slLog.gpStopLogFile(scHandle)
        return

    def patternReportForTrackWindow(self, xOffset):
        ''' Creates and populates the -Pattern Report for Track- window'''

    # Read in the config file
        configFile = MainScriptEntities.readConfigFile('TP')
    # Define the window
        self.setCarsWindow = TrackPattern.ViewEntities.makeWindow()
        self.setCarsWindow.setLocation(xOffset, 150)
        self.setCarsWindow.setSize(400,500)
        formSeparator = javax.swing.JSeparator()
    # Define the header
        combinedHeader = javax.swing.JPanel()
        combinedHeader.setLayout(javax.swing.BoxLayout(combinedHeader, javax.swing.BoxLayout.Y_AXIS))
        combinedHeader.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    # Populate the header
        headerRRLabel = javax.swing.JLabel(self.trackData['RN'])
        headerRRBox = TrackPattern.ViewEntities.makeSwingBox(100, configFile['PH'])
        headerRRBox.add(headerRRLabel)
        headerValidLabel = javax.swing.JLabel(self.trackData['VT'])
        headerValidBox = TrackPattern.ViewEntities.makeSwingBox(100, configFile['PH'])
        headerValidBox.add(headerValidLabel)
        headerYTLabel = javax.swing.JLabel()
        headerYTBox = TrackPattern.ViewEntities.makeSwingBox(100, configFile['PH'])
        headerYTBox.add(headerYTLabel)
    # Construct the header
        combinedHeader.add(headerRRBox)
        combinedHeader.add(headerValidBox)
        combinedHeader.add(headerYTBox)
        combinedHeader.add(javax.swing.JSeparator())
    # Define the form
        combinedForm = javax.swing.JPanel()
        combinedForm.setLayout(javax.swing.BoxLayout(combinedForm, javax.swing.BoxLayout.Y_AXIS))
        combinedForm.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    # Define the forms header
        combinedFormHeader = javax.swing.JPanel()
        combinedFormHeader.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
        reportWidth = configFile['RW']
    # Populate the forms header
        # Set to: input box
        label = javax.swing.JLabel(configFile['ST'])
        box = TrackPattern.ViewEntities.makeSwingBox(reportWidth['Input'] * configFile['RM'], configFile['PH'])
        box.add(label)
        combinedFormHeader.add(box)
        # Create rest of header from user settings
        for x in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
            if (x != ' '): # skips over null entries
                label = javax.swing.JLabel(x)
                box = TrackPattern.ViewEntities.makeSwingBox(reportWidth[x] * configFile['RM'], configFile['PH'])
                box.add(label)
                combinedFormHeader.add(box)
    # Define the forms body
        combinedFormBody = javax.swing.JPanel()
        combinedFormBody.setLayout(javax.swing.BoxLayout(combinedFormBody, javax.swing.BoxLayout.Y_AXIS))
        combinedFormBody.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    # Sort the cars
        for j in self.trackData['ZZ']:
            self.setCarsWindow.setTitle(u'Pattern Report for track ' + unicode(j['TN'], MainScriptEntities.setEncoding())) # have to do this here
            headerYTLabel.setText(self.trackData['RT'] + u' for (' + self.trackData['YL'] + u') track (' + j['TN'] + ')') #have to do this here
            carList = TrackPattern.ModelEntities.sortCarList(j['TR'])
    # Each line of the form
            for car in carList:
                carId = self.cm.newRS(car['Road'], car['Number']) # returns car object
                carDataDict = TrackPattern.ModelEntities.getCarDetailDict(carId)
                combinedInputLine = javax.swing.JPanel()
                combinedInputLine.setAlignmentX(0.0)
                # set car to input box
                inputText = javax.swing.JTextField(5)
                self.jTextIn.append(inputText) # making a list of jTextField boxes
                inputBox = TrackPattern.ViewEntities.makeSwingBox(reportWidth['Input'] * configFile['RM'], configFile['PH'])
                inputBox.add(inputText)
                combinedInputLine.add(inputBox)
                for x in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
                    if (x != ' '):
                        label = javax.swing.JLabel(carDataDict[x])
                        box = TrackPattern.ViewEntities.makeSwingBox(reportWidth[x] * configFile['RM'], configFile['PH'])
                        box.add(label)
                        combinedInputLine.add(box)
                combinedFormBody.add(combinedInputLine)
    # Define the footer
        combinedFooter = javax.swing.JPanel()
        combinedFooter.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    # Construct the footer
        setCarsButton = javax.swing.JButton(unicode('Set', MainScriptEntities.setEncoding()))
        setCarsButton.actionPerformed = self.setCarsToTrack
        ypButton = javax.swing.JButton(unicode('Print', MainScriptEntities.setEncoding()))
        ypButton.actionPerformed = self.printYP
    # Populate the footer
        combinedFooter.add(ypButton)
        combinedFooter.add(setCarsButton)
    # Construce the form
        combinedForm.add(combinedFormHeader)
        combinedForm.add(combinedFormBody)
    # Construct the window
        self.setCarsWindow.add(combinedHeader)
    #     # self.setCarsWindow.add(formSeparator)
        self.setCarsWindow.add(combinedForm)
        self.setCarsWindow.add(formSeparator)
        self.setCarsWindow.add(combinedFooter)
        self.setCarsWindow.pack()
        self.setCarsWindow.setVisible(True)
        print(patternReportWindowManager.scriptRev)
        return True


class makeSetCarsForm():
    '''Create and open a set cars window for each track selected'''

    scriptRev = 'setCars rev.20211101'

    def __init__(self, xYard, xTracks):
        '''Initialization variables'''

    # Script specific
        self.profilePath = jmri.util.FileUtil.getProfilePath()
        self.yardLoc = xYard
        # self.destTracks = dTracks
        self.selectedTracks = xTracks
        self.yardTrackType = None
    # File logger setup
        self.logName = 'mwLog'
        self.logLevel = 10
        self.logMode = 'w' # write over the old log
        return

    def runScript(self):
        '''Run the program'''

    # Set initial variables
        yTimeNow = time.time()
    # Setup gplogging
        # gpLogPath = self.profilePath + 'operations\\buildstatus\\SetCars (' + self.yardLoc + ').txt'
        # scLog = yUtil.gpLogging(self.logName)
        # scHandle = scLog.gpStartLogFile(gpLogPath, self.logLevel, self.logMode)
        # scLog.gpInfo('*** Make Window, set cars window')
        # scLog.gpInfo('Time run: ' + str(time.time()))
        windowOffset = 200
    # create an instance for each track in its own window
        # scLog.gpInfo(u'Open track windows for location ' + unicode(self.yardLoc, MainScriptEntities.setEncoding()))
        for track in self.selectedTracks:
            listForTrack = TrackPattern.ModelEntities.makeYardPattern([track], self.yardLoc) # track needs to be send in as a list
            listForTrack.update({'RT': u'Switch List for Track'})
            newWindow = patternReportWindowManager(listForTrack)
            newWindow.patternReportForTrackWindow(windowOffset)
            # scLog.gpInfo(u'Window created for track ' + track)
            windowOffset += 50
    # wrap up the script
        computeTime = 'Script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6]
        # scLog.gpInfo(computeTime)
        # scLog.gpStopLogFile(scHandle)
        print(makeSetCarsForm.scriptRev)
        print(computeTime)
        return

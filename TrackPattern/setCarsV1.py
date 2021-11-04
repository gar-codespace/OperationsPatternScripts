# coding=utf-8
# script to set cars to a yard track
# by Greg Ritacco
# use and abuse this as you see fit
# Extended ìÄÅÉî

import jmri
import java
import java.awt
import javax.swing
import time
from codecs import open as cOpen
from os import system
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern')
import utilsV1 as yUtil

class patternReportWindowManager():
    '''Manages an instance of each -Pattern Report for Track- window'''

# Class variables
    scriptRev = 'patternReportWindowManagerV1 rev.20210901'

    def __init__(self, pattern, logPath):
        '''Initialization variables'''

    # Boilerplate
        self.lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        self.cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
        self.profilePath = jmri.util.FileUtil.getProfilePath()
    # Track variables
        self.trackData = pattern # all the data for the selected track, car roster is sorted
        self.allTracksAtLoc = [] # all the tracks for that location
        self.ignoreLength = False # force car to track regardless of track length
    # Lists for reports
        self.jTextIn = [] # create a list jTextField objects
        self.carDataList = [] # list of sorted car objects
    # Set up the logger
        self.scLogPath = logPath # passed in
        self.scLog = 'scLog'
        self.slLog = 'slLog'
        self.logLevel = 10 # verbose
        self.logMode = 'a' # append to existing log

    def setCarsToTrack(self, event):
        '''Event that moves cars to the tracks entered in the pattern window
        Can ignore track length'''

    # Setup gplogging
        gpLogPath = self.scLogPath
        scLog = yUtil.gpLogging(self.scLog)
        scHandle = scLog.gpStartLogFile(gpLogPath, self.logLevel, self.logMode)
    # set the cars to a track
        self.ignoreLength = yUtil.readConfigFile()['MI'] # flag to ignore track length
        patternCopy = self.trackData # all the data for just one track
        self.allTracksAtLoc = yUtil.getTracks(patternCopy['YL'], None)
        userInputList = [] # create a list of user inputs from the text input boxes
        for userInput in self.jTextIn: # Read in and check the user input
            userInputList.append(unicode(userInput.getText(), yUtil.setEncoding()))
        scLog.gpInfo('*** Set cars to track')
        i = 0
        for z in patternCopy['ZZ']:
            if (len(userInputList) == len(z['TR'])): # check that the lengths of the -input list- and -car roster- match
                scLog.gpInfo('Number of input fields matches track roster length') # elaborate on this
            else:
                # something that happens if the lengths dont match
                pass
            trackName = unicode(z['TN'], yUtil.setEncoding())
            setToLocation = self.lm.getLocationByName(unicode(patternCopy['YL'], yUtil.setEncoding()))
            j = 0
            for y in z['TR']:
                if (userInputList[i] in self.allTracksAtLoc and userInputList[i] != trackName):
                    setToTrack = setToLocation.getTrackByName(unicode(userInputList[i], yUtil.setEncoding()), None)
                    setCarId = self.cm.newRS(y['Road'], y['Number'])
                    self.cm.newRS(y['Road'], y['Number']).setLocation(setToLocation, setToTrack, self.ignoreLength)
                    scLog.gpInfo('Set car (' + unicode(setCarId, yUtil.setEncoding()) + ') to track (' + unicode(setToTrack, yUtil.setEncoding()) + ')')
                    j += 1
                i += 1
            scLog.gpInfo(str(j) + ' cars were set')
    # Wrap it up
        self.setCarsWindow.setVisible(False)
        scLog.gpInfo('Time run: ' + str(time.time()))
        scLog.gpStopLogFile(scHandle)
        return

    def printYP(self, event):
        '''Event that prints the yard pattern for the selected track'''

    # Set up gpLogging
        gpLogPath = self.scLogPath
        slLog = yUtil.gpLogging(self.slLog)
        scHandle = slLog.gpStartLogFile(gpLogPath, self.logLevel, self.logMode)
        slLog.gpInfo('*** Switch List, create switch list for print')
    # Make the switch list
        patternCopy = self.trackData
        userInputList = [] # create a list of user inputs for the set car destinations
        for userInput in self.jTextIn: # Read in the user input
            userInputList.append(unicode(userInput.getText(), yUtil.setEncoding()))
        i = 0
        for z in patternCopy['ZZ']:
            if (len(userInputList) == len(z['TR'])): # check that the lengths of the input list and car roster match
                slLog.gpInfo('Lengths of the input list and car roster match') # elaborate on this
            trackName = z['TN']
            self.allTracksAtLoc = yUtil.getTracks(patternCopy['YL'], None)
            for y in z['TR']:
                setTrack = unicode('Hold', yUtil.setEncoding())
                if (userInputList[i] in self.allTracksAtLoc and userInputList[i] != trackName):
                    setTrack = unicode(userInputList[i], yUtil.setEncoding())
                setTrack = yUtil.formatText(' [' + setTrack + '] ', 8)
                y.update({'Set to': setTrack}) # replaces empty brackets with the marked ones
                i += 1
    # Print the switch list
        textSwitchList = yUtil.makeSwitchlist(patternCopy, False)
        textCopyTo = self.profilePath + 'operations\\switchLists\\Switch list (' + patternCopy['YL'] + ') (' + trackName + ').txt'
        with cOpen(textCopyTo, 'wb', encoding=yUtil.setEncoding()) as textWorkFile:
            textWorkFile.write(textSwitchList)
        system(yUtil.systemInfo() + textCopyTo)
    # Print the CSV switch list
        if (jmri.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled()):
            csvSwitchList = yUtil.makeCsvSwitchlist(patternCopy)
            csvCopyTo = self.profilePath + 'operations\\csvSwitchLists\\Switch list (' + patternCopy['YL'] + ') (' + trackName + ').csv'
            with cOpen(csvCopyTo, 'wb', encoding=yUtil.setEncoding()) as csvWorkFile:
                csvWorkFile.write(csvSwitchList)
            slLog.gpInfo('Write CSV switch list for track (' + trackName + ')')
    # Wrap it up
        slLog.gpInfo('Make switch list for print - track (' + trackName + ')')
        slLog.gpInfo('Time run: ' + str(time.time()))
        slLog.gpStopLogFile(scHandle)
        return

    def patternReportForTrackWindow(self, xOffset):
        ''' Creates and populates the -Pattern Report for Track- window'''

    # Read in the config file
        configFile = yUtil.readConfigFile()
    # Define the window
        self.setCarsWindow = yUtil.makeWindow()
        self.setCarsWindow.setLocation(xOffset, 200)
        self.setCarsWindow.setSize(400,500)
        formSeparator = javax.swing.JSeparator()
    # Define the header
        combinedHeader = javax.swing.JPanel()
        combinedHeader.setLayout(javax.swing.BoxLayout(combinedHeader, javax.swing.BoxLayout.Y_AXIS))
        combinedHeader.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    # Populate the header
        headerRRLabel = javax.swing.JLabel(self.trackData['RN'])
        headerRRBox = yUtil.makeSwingBox(100, configFile['RH'])
        headerRRBox.add(headerRRLabel)
        headerValidLabel = javax.swing.JLabel(self.trackData['VT'])
        headerValidBox = yUtil.makeSwingBox(100, configFile['RH'])
        headerValidBox.add(headerValidLabel)
        headerYTLabel = javax.swing.JLabel()
        headerYTBox = yUtil.makeSwingBox(100, configFile['RH'])
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
        box = yUtil.makeSwingBox(reportWidth['Input'] * configFile['RM'], configFile['RH'])
        box.add(label)
        combinedFormHeader.add(box)
        # Create rest of header from user settings
        for x in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
            if (x != ' '): # skips over null entries
                label = javax.swing.JLabel(x)
                box = yUtil.makeSwingBox(reportWidth[x] * configFile['RM'], configFile['RH'])
                box.add(label)
                combinedFormHeader.add(box)
    # Define the forms body
        combinedFormBody = javax.swing.JPanel()
        combinedFormBody.setLayout(javax.swing.BoxLayout(combinedFormBody, javax.swing.BoxLayout.Y_AXIS))
        combinedFormBody.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    # Sort the cars
        for j in self.trackData['ZZ']:
            self.setCarsWindow.setTitle(u'Pattern Report for track ' + unicode(j['TN'], yUtil.setEncoding())) # have to do this here
            headerYTLabel.setText(self.trackData['RT'] + u' for (' + self.trackData['YL'] + u') track (' + j['TN'] + ')') #have to do this here
            carList = yUtil.sortCarList(j['TR'])
    # Each line of the form
            for car in carList:
                carId = self.cm.newRS(car['Road'], car['Number']) # returns car object
                carDataDict = yUtil.getCarDetailDict(carId)
                combinedInputLine = javax.swing.JPanel()
                combinedInputLine.setAlignmentX(0.0)
                # set car to input box
                inputText = javax.swing.JTextField(5)
                self.jTextIn.append(inputText) # making a list of jTextField boxes
                inputBox = yUtil.makeSwingBox(reportWidth['Input'] * configFile['RM'], configFile['RH'])
                inputBox.add(inputText)
                combinedInputLine.add(inputBox)
                for x in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
                    if (x != ' '):
                        label = javax.swing.JLabel(carDataDict[x])
                        box = yUtil.makeSwingBox(reportWidth[x] * configFile['RM'], configFile['RH'])
                        box.add(label)
                        combinedInputLine.add(box)
                combinedFormBody.add(combinedInputLine)
    # Define the footer
        combinedFooter = javax.swing.JPanel()
        combinedFooter.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    # Construct the footer
        setCarsButton = javax.swing.JButton(unicode('Set', yUtil.setEncoding()))
        setCarsButton.actionPerformed = self.setCarsToTrack
        ypButton = javax.swing.JButton(unicode('Print', yUtil.setEncoding()))
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


class setCars():
    '''Create and open a set cars window for each track selected'''

    scriptRev = 'setCarsV1 rev.20210901'

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

        # print(jmri.jmrit.operations.setup.Setup.getCarAttributes())
        # for x in jmri.jmrit.operations.setup.Setup.getDropSwitchListMessageFormat():
        #     print(x)
    # Set initial variables
        yTimeNow = time.time()
    # Setup gplogging
        gpLogPath = self.profilePath + 'operations\\buildstatus\\SetCars (' + self.yardLoc + ').txt'
        scLog = yUtil.gpLogging(self.logName)
        scHandle = scLog.gpStartLogFile(gpLogPath, self.logLevel, self.logMode)
        scLog.gpInfo('*** Make Window, set cars window')
        scLog.gpInfo('Time run: ' + str(time.time()))
        windowOffset = 200
    # create an instance for each track in its own window
        scLog.gpInfo(u'Open track windows for location ' + unicode(self.yardLoc, yUtil.setEncoding()))
        for track in self.selectedTracks:
            listForTrack = yUtil.makeYardPattern([track], self.yardLoc) # track needs to be send in as a list
            listForTrack.update({'RT': u'Switch List for Track'})
            newWindow = patternReportWindowManager(listForTrack, gpLogPath)
            newWindow.patternReportForTrackWindow(windowOffset)
            scLog.gpInfo(u'Window created for track ' + track)
            windowOffset += 50
    # wrap up the script
        computeTime = 'Script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6]
        scLog.gpInfo(computeTime)
        scLog.gpStopLogFile(scHandle)
        print(setCars.scriptRev)
        print(computeTime)
        return

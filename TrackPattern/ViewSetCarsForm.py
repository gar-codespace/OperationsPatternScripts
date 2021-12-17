# coding=utf-8
# Extended ìÄÅÉî
# support methods for the view script
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import jmri.util
import java.awt
import javax.swing
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern')
import MainScriptEntities
import TrackPattern.ControllerSetCarsForm
import TrackPattern.ViewEntities
import TrackPattern.ModelEntities

scriptRev = 'TrackPattern.ViewSetCarsForm v20211210'

def patternReportForTrackWindow(trackPattern, offset):
    '''Creates and populates the -Pattern Report for Track- window'''

    configFile = MainScriptEntities.readConfigFile('TP')

#Boilerplate
    trackName = unicode(trackPattern['ZZ'][0]['TN'], MainScriptEntities.setEncoding())
    trackLocation = unicode(trackPattern['YL'], MainScriptEntities.setEncoding())
    allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(trackLocation, None)
    isASpur, hasASchedule = TrackPattern.ModelSetCarsForm.getTrackTypeAndSchedule(trackLocation, trackName)
# Define the window
    setCarsWindow = TrackPattern.ViewSetCarsForm.makeWindow()
# Create the forms header
    formHeader = setCarsFormHeader(trackPattern)
    formHeader.border = javax.swing.BorderFactory.createEmptyBorder(5,0,5,0)
# create the row of track buttons
    buttonPanel = javax.swing.JPanel()
    buttonPanel.setLayout(javax.swing.BoxLayout(buttonPanel, javax.swing.BoxLayout.X_AXIS))
    for trackButton in makeTrackButtonRow(allTracksAtLoc):
        buttonPanel.add(trackButton)
        trackButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(None, None, None, None).trackRowButton
# Create the car list part of the form
    combinedForm = javax.swing.JPanel()
    combinedForm.setLayout(javax.swing.BoxLayout(combinedForm, javax.swing.BoxLayout.Y_AXIS))
    combinedForm.setAlignmentX(java.awt.Component.CENTER_ALIGNMENT)
    bodyHeader, headerWidth = setCarsFormBodyHeader()
    combinedForm.add(bodyHeader)
    formBody, textBoxEntry = setCarsFormBody(trackPattern)
    combinedForm.add(formBody)
    scrollPanel = javax.swing.JScrollPane(combinedForm)
    scrollPanel.border = javax.swing.BorderFactory.createEmptyBorder(2,2,2,2)
# Create the schedule row
    scheduleObject, trackObject = TrackPattern.ModelSetCarsForm.getScheduleForTrack(trackLocation, trackName)
    if (scheduleObject):
        schedulePanel = javax.swing.JPanel()
        schedulePanel.setLayout(javax.swing.BoxLayout(schedulePanel, javax.swing.BoxLayout.X_AXIS))
        scheduleButton = javax.swing.JButton(scheduleObject.getName())
        scheduleButton.setPreferredSize(java.awt.Dimension(0,18))
        scheduleButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(scheduleObject, trackObject, None, None).scheduleButton
        schedulePanel.add(javax.swing.JLabel(u'Schedule: '))
        schedulePanel.add(scheduleButton)
# Create the footer
    combinedFooter, tpButton, scButton = TrackPattern.ViewSetCarsForm.setCarsFormFooter()
    tpButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(trackPattern, None, textBoxEntry, None).printPrButton
    scButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(trackPattern, trackObject, textBoxEntry, setCarsWindow).setPrButton
# Put it all together
    setCarsWindow.setTitle(u'Pattern Report for track ' + trackName)
    setCarsWindow.setLocation(offset, 180)
    setCarsWindow.add(formHeader)
    setCarsWindow.add(javax.swing.JSeparator())
    setCarsWindow.add(buttonPanel)
    setCarsWindow.add(javax.swing.JSeparator())
    setCarsWindow.add(scrollPanel)
    setCarsWindow.add(javax.swing.JSeparator())
    if (scheduleObject):
        setCarsWindow.add(schedulePanel)
        setCarsWindow.add(javax.swing.JSeparator())
    setCarsWindow.add(combinedFooter)

    return setCarsWindow

def makeSwingBox(xWidth, yHeight):
    '''Makes a swing box to the desired size'''

    xName = javax.swing.Box(javax.swing.BoxLayout.X_AXIS)
    xName.setPreferredSize(java.awt.Dimension(width=xWidth, height=yHeight))

    return xName

def makeWindow():
    '''Makes a JMRI style swing frame'''

    jFrame = jmri.util.JmriJFrame()
    jFrame.contentPane.setLayout(javax.swing.BoxLayout(jFrame.contentPane, javax.swing.BoxLayout.Y_AXIS))
    # jFrame.contentPane.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    # jFrame.contentPane.setAlignmentX(0.0)

    return jFrame

def makeTrackButtonRow(allTracksAtLoc):
    '''Makes a row of buttons, one for each track'''

    trackButtonRowList = []
    for track in allTracksAtLoc:
        selectTrackButton = javax.swing.JButton(track)
        selectTrackButton.setPreferredSize(java.awt.Dimension(0,18))
        trackButtonRowList.append(selectTrackButton)

    return trackButtonRowList

def setCarsFormHeader(trackData):
    '''Creates the Set Cars forms header'''

# Read in the config file
    configFile = MainScriptEntities.readConfigFile('TP')
# Define the header
    combinedHeader = javax.swing.JPanel()
    combinedHeader.setLayout(javax.swing.BoxLayout(combinedHeader, javax.swing.BoxLayout.Y_AXIS))
    # combinedHeader.setAlignmentX(java.awt.Component.CENTER_ALIGNMENT)
# Populate the header
    headerRRLabel = javax.swing.JLabel(trackData['RN'])
    headerRRBox = makeSwingBox(100, configFile['PH'])
    headerRRBox.add(headerRRLabel)

    headerValidLabel = javax.swing.JLabel(trackData['VT'])
    headerValidBox = makeSwingBox(100, configFile['PH'])
    headerValidBox.add(headerValidLabel)
    # Dig out the track name
    trackName = trackData['ZZ']
    trackName = trackName[0]
    trackName = unicode(trackName['TN'], MainScriptEntities.setEncoding())
    headerYTLabel = javax.swing.JLabel()
    headerYTLabel.setText(trackData['RT'] + trackName + ' at ' + trackData['YL'])
    headerYTBox = makeSwingBox(100, configFile['PH'])
    headerYTBox.add(headerYTLabel)
# Construct the header
    combinedHeader.add(headerRRBox)
    combinedHeader.add(headerValidBox)
    combinedHeader.add(headerYTBox)

    return combinedHeader

def setCarsFormBodyHeader():
    '''Creates the header for the Set Cars forms body'''

# Read in the config file
    configFile = MainScriptEntities.readConfigFile('TP')
    reportWidth = configFile['RW']
# Define the forms header
    bodyHeader = javax.swing.JPanel()
    bodyHeader.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)

# Populate the forms header
    label = javax.swing.JLabel(configFile['ST'])
    box = makeSwingBox(reportWidth['Input'] * configFile['RM'], configFile['PH'])
    box.add(label)
    bodyHeader.add(box)
# Create rest of header from user settings
    headerWidth = 0
    for x in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
        if (x != ' '): # skips over null entries
            label = javax.swing.JLabel(x)
            box = makeSwingBox(reportWidth[x] * configFile['RM'], configFile['PH'])
            box.add(label)
            bodyHeader.add(box)
            headerWidth = headerWidth + reportWidth[x]
    headerWidth = headerWidth * 10

    return bodyHeader, headerWidth

def setCarsFormBody(trackData):
    '''Creates the body of the Set cars form'''

# Set up
    cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
    configFile = MainScriptEntities.readConfigFile('TP')
    reportWidth = configFile['RW']
    textBoxEntry = []
# define the forms body
    formBody = javax.swing.JPanel()
    formBody.setLayout(javax.swing.BoxLayout(formBody, javax.swing.BoxLayout.Y_AXIS))
    formBody.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
# Sort the cars
    for j in trackData['ZZ']:
        carList = TrackPattern.ModelEntities.sortCarList(j['TR'])
# Each line of the form
        headerWidth = 0
        for car in carList:
            carId = cm.newRS(car['Road'], car['Number']) # returns car object
            carDataDict = TrackPattern.ModelEntities.getDetailsForCarAsDict(carId)
            combinedInputLine = javax.swing.JPanel()
            combinedInputLine.setAlignmentX(0.0)
        # set car to input box
            inputText = javax.swing.JTextField(5)
            inputText.addMouseListener(TrackPattern.ControllerSetCarsForm.textBoxEntryListener())
            textBoxEntry.append(inputText) # making a list of jTextField boxes
            inputBox = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth['Input'] * configFile['RM'], configFile['PH'])
            inputBox.add(inputText)
            combinedInputLine.add(inputBox)
            for x in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
                if (x != ' '):
                    label = javax.swing.JLabel(carDataDict[x])
                    box = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth[x] * configFile['RM'], configFile['PH'])
                    box.add(label)
                    combinedInputLine.add(box)
                    headerWidth = headerWidth + reportWidth[x]
            formBody.add(combinedInputLine)

    return formBody, textBoxEntry

def setCarsFormFooter():
    '''Creates the Set Cars forms footer'''

# Define the footer
    footer = javax.swing.JPanel()
# Construct the footer
    scButton = javax.swing.JButton(unicode('Set', MainScriptEntities.setEncoding()))
    tpButton = javax.swing.JButton(unicode('Print', MainScriptEntities.setEncoding()))
# Populate the footer
    footer.add(tpButton)
    footer.add(scButton)

    return footer, tpButton, scButton

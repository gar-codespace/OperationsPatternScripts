# coding=utf-8
# © 2021 Greg Ritacco

import jmri
# import jmri.util
import java.awt
import javax.swing

import psEntities.MainScriptEntities
import TrackPattern.ViewEntities
import TrackPattern.ModelEntities
import TrackPattern.ControllerSetCarsForm

'''Display methods for the Set Cars form'''

scriptName = 'OperationsPatternScripts.TrackPattern.ViewSetCarsForm'
scriptRev = 20220101

def patternReportForTrackForm(header, body):
    '''Creates and populates the "Pattern Report for Track X" form'''

    configFile = psEntities.MainScriptEntities.readConfigFile('TP')
# Boilerplate
    trackName = unicode(body['Name'], psEntities.MainScriptEntities.setEncoding())
    trackLocation = unicode(header['location'], psEntities.MainScriptEntities.setEncoding())
    allTracksAtLoc = TrackPattern.ModelEntities.getTracksByLocation(trackLocation, None)
# Define the form
    setCarsForm = javax.swing.JPanel()
    setCarsForm.setLayout(javax.swing.BoxLayout(setCarsForm, javax.swing.BoxLayout.Y_AXIS))
# Create the forms header
    formHeader = setCarsFormHeader(header, trackName)
    formHeader.border = javax.swing.BorderFactory.createEmptyBorder(5,0,5,0)
# create the row of track buttons
    buttonPanel = javax.swing.JPanel()
    buttonPanel.setLayout(javax.swing.BoxLayout(buttonPanel, javax.swing.BoxLayout.X_AXIS))
    for track in allTracksAtLoc:
        selectTrackButton = javax.swing.JButton(track)
        selectTrackButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener().trackRowButton
        buttonPanel.add(selectTrackButton)
# Create the car list part of the form
    combinedForm = javax.swing.JPanel()
    combinedForm.setLayout(javax.swing.BoxLayout(combinedForm, javax.swing.BoxLayout.Y_AXIS))
    combinedForm.setAlignmentX(java.awt.Component.CENTER_ALIGNMENT)
    bodyHeader, headerWidth = setCarsFormBodyHeader()
    combinedForm.add(bodyHeader)
    formBody, textBoxEntry = setCarsFormBody(body)
    combinedForm.add(formBody)
    scrollPanel = javax.swing.JScrollPane(combinedForm)
    scrollPanel.border = javax.swing.BorderFactory.createEmptyBorder(2,2,2,2)
# Create the schedule row
    trackObject = TrackPattern.ModelSetCarsForm.getTrackObject(trackLocation, trackName)
    scheduleObject = trackObject.getSchedule()
    if (scheduleObject):
        schedulePanel = javax.swing.JPanel()
        schedulePanel.setLayout(javax.swing.BoxLayout(schedulePanel, javax.swing.BoxLayout.X_AXIS))
        scheduleButton = javax.swing.JButton(scheduleObject.getName())
        # scheduleButton.setPreferredSize(java.awt.Dimension(0,20))
        scheduleButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(trackObject).scheduleButton
        schedulePanel.add(javax.swing.JLabel(u'Schedule: '))
        schedulePanel.add(scheduleButton)
# Create the footer
    combinedFooter = javax.swing.JPanel()

    printButton = javax.swing.JButton(unicode(u'Print', psEntities.MainScriptEntities.setEncoding()))
    printButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(body, textBoxEntry).printButton
    setButton = javax.swing.JButton(unicode(u'Set', psEntities.MainScriptEntities.setEncoding()))
    setButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(body, textBoxEntry).setButton

    combinedFooter.add(printButton)
    combinedFooter.add(setButton)
    if psEntities.MainScriptEntities.readConfigFile('TP')['TP']:
        trainPlayerButton = javax.swing.JButton(unicode(u'TrainPlayer', psEntities.MainScriptEntities.setEncoding()))
        combinedFooter.add(trainPlayerButton)
        trainPlayerButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(body, textBoxEntry).trainPlayerButton
# # Put it all together
    setCarsForm.add(formHeader)
    setCarsForm.add(javax.swing.JSeparator())
    setCarsForm.add(buttonPanel)
    setCarsForm.add(javax.swing.JSeparator())
    setCarsForm.add(scrollPanel)
    setCarsForm.add(javax.swing.JSeparator())
    if (scheduleObject):
        setCarsForm.add(schedulePanel)
        setCarsForm.add(javax.swing.JSeparator())
    setCarsForm.add(combinedFooter)

    return setCarsForm

def patternReportForTrackWindow(patternReportForTrackForm):

    setCarsWindow = TrackPattern.ViewSetCarsForm.makeWindow()
    setCarsWindow.add(patternReportForTrackForm)
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

    return jFrame

def setCarsFormHeader(header, trackName):
    '''Creates the "Pattern Report for Track X" forms header'''

# Read in the config file
    configFile = psEntities.MainScriptEntities.readConfigFile('TP')
# Define the header
    combinedHeader = javax.swing.JPanel()
    combinedHeader.setLayout(javax.swing.BoxLayout(combinedHeader, javax.swing.BoxLayout.Y_AXIS))
# Railroad name
    headerRRLabel = javax.swing.JLabel(header['railroad'])
    headerRRBox = makeSwingBox(100, configFile['PH'])
    headerRRBox.add(headerRRLabel)
# Valid time
    headerValidLabel = javax.swing.JLabel(header['date'])
    headerValidBox = makeSwingBox(100, configFile['PH'])
    headerValidBox.add(headerValidLabel)
# Track name and location
    # trackName = unicode(trackData['ZZ'][0]['TN'], psEntities.MainScriptEntities.setEncoding())
    headerYTLabel = javax.swing.JLabel()
    headerYTLabel.setText('Pattern report for track: ' + trackName + ' at ' + header['location'])
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
    configFile = psEntities.MainScriptEntities.readConfigFile('TP')
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

def setCarsFormBody(body):
    '''Creates the body of the Set cars form'''

    cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
    configFile = psEntities.MainScriptEntities.readConfigFile('TP')
    reportWidth = configFile['RW']
    textBoxEntry = []

    formBody = javax.swing.JPanel()
    formBody.setLayout(javax.swing.BoxLayout(formBody, javax.swing.BoxLayout.Y_AXIS))
    formBody.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)

    sortedCarList = TrackPattern.ModelEntities.sortCarList(body['Cars'])

    headerWidth = 0
    for car in sortedCarList:
        carId = cm.newRS(car['Road'], car['Number']) # returns car object
        combinedInputLine = javax.swing.JPanel()
        combinedInputLine.setAlignmentX(0.0)

        inputText = javax.swing.JTextField(5)
        inputText.addMouseListener(TrackPattern.ControllerSetCarsForm.TextBoxEntryListener())
        textBoxEntry.append(inputText) # making a list of jTextField boxes
        inputBox = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth['Input'] * configFile['RM'], configFile['PH'])
        inputBox.add(inputText)
        combinedInputLine.add(inputBox)
        for item in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
            label = javax.swing.JLabel(car[item])
            box = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth[item] * configFile['RM'], configFile['PH'])
            box.add(label)
            combinedInputLine.add(box)
            headerWidth = headerWidth + reportWidth[item]
        formBody.add(combinedInputLine)

    return formBody, textBoxEntry

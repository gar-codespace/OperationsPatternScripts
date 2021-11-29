# coding=utf-8
# Extended ìÄÅÉî
# support methods for the view script
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
import javax.swing
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern')
import MainScriptEntities
import TrackPattern.ModelEntities
import TrackPattern.ViewSetCarsForm

scriptRev = 'TrackPattern.ViewEntities v20211125'

def makeSwingBox(xWidth, xHeight):
    ''' Makes a swing box to the desired size'''

    xName = javax.swing.Box(javax.swing.BoxLayout.X_AXIS)
    xName.setPreferredSize(java.awt.Dimension(width=xWidth, height=xHeight))

    return xName

def makeWindow():
    '''Makes a swing frame with the desired name'''

    pFrame = javax.swing.JFrame()
    pFrame.contentPane.setLayout(javax.swing.BoxLayout(pFrame.contentPane, javax.swing.BoxLayout.Y_AXIS))
    pFrame.contentPane.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    pFrame.contentPane.setAlignmentX(0.0)
    iconPath = jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts\\decpro5.png'
    icon = java.awt.Toolkit.getDefaultToolkit().getImage(iconPath)
    pFrame.setIconImage(icon)

    return pFrame

def setCarsFormHeader(trackData):
    ''' Creates the Set Cars forms header'''

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
    # Set to: input box
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
    jTextIn = []
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
            carDataDict = TrackPattern.ModelEntities.makeCarDetailDict(carId)
            combinedInputLine = javax.swing.JPanel()
            combinedInputLine.setAlignmentX(0.0)
        # set car to input box
            inputText = javax.swing.JTextField(5)
            inputText.addMouseListener(TrackPattern.ControllerSetCarsForm.SetTrackBoxMouseListener())
            jTextIn.append(inputText) # making a list of jTextField boxes
            inputBox = makeSwingBox(reportWidth['Input'] * configFile['RM'], configFile['PH'])
            inputBox.add(inputText)
            combinedInputLine.add(inputBox)
            for x in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
                if (x != ' '):
                    label = javax.swing.JLabel(carDataDict[x])
                    box = makeSwingBox(reportWidth[x] * configFile['RM'], configFile['PH'])
                    box.add(label)
                    combinedInputLine.add(box)
                    headerWidth = headerWidth + reportWidth[x]
            formBody.add(combinedInputLine)

    return formBody, jTextIn

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

def makeFrame():
    '''Makes the title boarder frame'''

    patternFrame = TrackPattern.View.manageGui().makeFrame()

    return patternFrame

def makePanel(self):
    '''Make and activate the Track Pattern objects'''

    panel, controls = TrackPattern.View.manageGui().makePanel()
    controls[0].actionPerformed = whenTPEnterPressed
    controls[1].actionPerformed = whenPABoxClicked
    self.controls[6].actionPerformed = self.whenPRButtonPressed
    self.configFile = MainScriptEntities.readConfigFile('TP')
    if (self.configFile['PL'] != ''):
        self.controls[4].setEnabled(True)
        self.controls[5].setEnabled(True)
        self.controls[4].actionPerformed = self.whenTPButtonPressed
        self.controls[5].actionPerformed = self.whenSCButtonPressed
        self.psLog.info('saved location validated, buttons activated')
    self.psLog.info('track pattern makePanel completed')

    return self.panel

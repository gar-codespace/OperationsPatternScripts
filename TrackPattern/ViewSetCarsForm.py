# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import java.awt
import javax.swing
import javax.swing.GroupLayout

import psEntities.MainScriptEntities
import TrackPattern.ViewEntities
import TrackPattern.ControllerSetCarsForm

'''Display methods for the Pattern Report for Track X form'''

scriptName = 'OperationsPatternScripts.TrackPattern.ViewSetCarsForm'
scriptRev = 20220101

def patternReportForTrackWindow(patternReportForTrackForm):

    setCarsWindow = TrackPattern.ViewSetCarsForm.makeWindow()
    setCarsWindow.add(patternReportForTrackForm)

    return setCarsWindow

def patternReportForTrackForm(header, body):
    '''Creates and populates the "Pattern Report for Track X" form'''

    configFile = psEntities.MainScriptEntities.readConfigFile('TP')

    patternReportForm = javax.swing.JPanel()
    patternReportForm.setLayout(javax.swing.BoxLayout(patternReportForm, javax.swing.BoxLayout.PAGE_AXIS))

    trackName = unicode(body['Name'], psEntities.MainScriptEntities.setEncoding())
    patternReportFormHeader = TrackPattern.ViewSetCarsForm.patternReportFormHeader(header, trackName)
    patternReportForm.add(patternReportFormHeader)
    patternReportForm.add(javax.swing.JSeparator())

    trackLocation = unicode(header['location'], psEntities.MainScriptEntities.setEncoding())
    lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
    allTracksAtLoc = lm.getLocationByName(trackLocation).getTracksByNameList(None)
    patternReportRowOfTracks = TrackPattern.ViewSetCarsForm.patternReportRowOfTracks(allTracksAtLoc)
    patternReportForm.add(patternReportRowOfTracks)
    patternReportForm.add(javax.swing.JSeparator())

    patternReportFormBody = javax.swing.JPanel()
    patternReportFormBody.setLayout(javax.swing.BoxLayout(patternReportFormBody, javax.swing.BoxLayout.PAGE_AXIS))

    listOfLocoRows, textBoxEntry = TrackPattern.ViewSetCarsForm.patternReportLocosBody(body)
    for loco in listOfLocoRows:
        # loco.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
        patternReportFormBody.add(loco)

    listOfCarRows, carBoxEntry = TrackPattern.ViewSetCarsForm.patternReportCarsBody(body)
    for car in listOfCarRows:
        # car.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
        patternReportFormBody.add(car)

    for item in carBoxEntry:
        textBoxEntry.append(item)

    patternReportForm.add(patternReportFormBody)
    patternReportForm.add(javax.swing.JSeparator())

    patternReportSchedule = TrackPattern.ViewSetCarsForm.patternReportScheduleRow(trackLocation, trackName)
    if (patternReportSchedule):
        patternReportForm.add(patternReportSchedule)
        patternReportForm.add(javax.swing.JSeparator())

    patternReportFooter = TrackPattern.ViewSetCarsForm.patternReportFooter()
    buttonList = patternReportFooter.getComponents()
    buttonList[0].actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(body, textBoxEntry).printButton
    buttonList[1].actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(body, textBoxEntry).setButton
    buttonList[2].actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(body, textBoxEntry).trainPlayerButton
    patternReportForm.add(patternReportFooter)

    return patternReportForm

def makeSwingBox(xWidth, yHeight):
    '''Makes a swing box to the desired size'''

    xName = javax.swing.Box(javax.swing.BoxLayout.X_AXIS)
    xName.setPreferredSize(java.awt.Dimension(width=xWidth, height=yHeight))

    return xName

def makeWindow():
    '''Makes a JMRI style swing frame'''

    jFrame = jmri.util.JmriJFrame()
    # jFrame.contentPane.setLayout(javax.swing.BoxLayout(jFrame.contentPane, javax.swing.BoxLayout.PAGE_AXIS))

    return jFrame

def patternReportFormHeader(header, trackName):
    '''Creates the "Pattern Report for Track X" forms header'''


    configFile = psEntities.MainScriptEntities.readConfigFile('TP')

    combinedHeader = javax.swing.JPanel()
    combinedHeader.setLayout(javax.swing.BoxLayout(combinedHeader, javax.swing.BoxLayout.PAGE_AXIS))

    headerRRLabel = javax.swing.JLabel(header['railroad'])
    headerRRBox = makeSwingBox(100, configFile['PH'])
    headerRRBox.add(headerRRLabel)

    headerValidLabel = javax.swing.JLabel(header['date'])
    headerValidBox = makeSwingBox(100, configFile['PH'])
    headerValidBox.add(headerValidLabel)

    headerYTLabel = javax.swing.JLabel()
    headerYTLabel.setText('Pattern report for track: ' + trackName + ' at ' + header['location'])
    headerYTBox = makeSwingBox(100, configFile['PH'])
    headerYTBox.add(headerYTLabel)

    combinedHeader.add(headerRRBox)
    combinedHeader.add(headerValidBox)
    combinedHeader.add(headerYTBox)
    combinedHeader.border = javax.swing.BorderFactory.createEmptyBorder(5,0,5,0)

    return combinedHeader

def patternReportRowOfTracks(allTracksAtLoc):

    buttonPanel = javax.swing.JPanel()
    for track in allTracksAtLoc:
        selectTrackButton = javax.swing.JButton(track.getName())
        selectTrackButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener().trackRowButton
        buttonPanel.add(selectTrackButton)

    return buttonPanel

def patternReportLocosBody(body):
    '''Creates the locomotive lines of the pattern report form'''

    configFile = psEntities.MainScriptEntities.readConfigFile('TP')
    reportWidth = configFile['RW']

    listOfLocoRows = []
    textBoxEntry = []

    for loco in body['Locos']:
        combinedInputLine = javax.swing.JPanel()
        combinedInputLine.setBackground(psEntities.FADED)
        # combinedInputLine.setAlignmentX(java.awt.BorderLayout.WEST)

        inputText = javax.swing.JTextField(5)
        inputText.addMouseListener(TrackPattern.ControllerSetCarsForm.TextBoxEntryListener())
        textBoxEntry.append(inputText)
        inputBox = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth['Input'] * configFile['RM'], configFile['PH'])
        inputBox.add(inputText)
        combinedInputLine.add(inputBox)

        label = javax.swing.JLabel(loco['Road'])
        box = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth['Road'] * configFile['RM'], configFile['PH'])
        box.add(label)
        combinedInputLine.add(box)

        label = javax.swing.JLabel(loco['Number'])
        box = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth['Number'] * configFile['RM'], configFile['PH'])
        box.add(label)
        combinedInputLine.add(box)

        label = javax.swing.JLabel(loco['Model'])
        box = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth['Model'] * configFile['RM'], configFile['PH'])
        box.add(label)
        combinedInputLine.add(box)

        label = javax.swing.JLabel(loco['Type'])
        box = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth['Loco Type'] * configFile['RM'], configFile['PH'])
        box.add(label)
        combinedInputLine.add(box)
        combinedInputLine.add(javax.swing.Box.createHorizontalGlue())

        listOfLocoRows.append(combinedInputLine)

    return listOfLocoRows, textBoxEntry

def patternReportCarsBody(body):
    '''Creates the car lines of the pattern report form'''

    configFile = psEntities.MainScriptEntities.readConfigFile('TP')
    reportWidth = configFile['RW']

    listOfCarRows = []
    textBoxEntry = []

    for car in body['Cars']:
        combinedInputLine = javax.swing.JPanel()
        combinedInputLine.setBackground(psEntities.DUST)
        # combinedInputLine.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
        inputText = javax.swing.JTextField(5)
        inputText.addMouseListener(TrackPattern.ControllerSetCarsForm.TextBoxEntryListener())
        textBoxEntry.append(inputText)
        inputBox = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth['Input'] * configFile['RM'], configFile['PH'])
        inputBox.add(inputText)
        combinedInputLine.add(inputBox)

        for item in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
            label = javax.swing.JLabel(car[item])
            box = TrackPattern.ViewSetCarsForm.makeSwingBox(reportWidth[item] * configFile['RM'], configFile['PH'])
            box.add(label)
            combinedInputLine.add(box)
        combinedInputLine.add(javax.swing.Box.createHorizontalGlue())
        listOfCarRows.append(combinedInputLine)

    return listOfCarRows, textBoxEntry

def patternReportScheduleRow(trackLocation, trackName):

    trackObject = TrackPattern.ModelSetCarsForm.getTrackObject(trackLocation, trackName)
    scheduleObject = trackObject.getSchedule()
    schedulePanel = None
    if (scheduleObject):
        schedulePanel = javax.swing.JPanel()
        scheduleButton = javax.swing.JButton(scheduleObject.getName())
        scheduleButton.actionPerformed = TrackPattern.ControllerSetCarsForm.AnyButtonPressedListener(trackObject).scheduleButton
        schedulePanel.add(javax.swing.JLabel(u'Schedule: '))
        schedulePanel.add(scheduleButton)

    return schedulePanel

def patternReportFooter():

    combinedFooter = javax.swing.JPanel()

    printButton = javax.swing.JButton(unicode(u'Print', psEntities.MainScriptEntities.setEncoding()))
    combinedFooter.add(printButton)

    setButton = javax.swing.JButton(unicode(u'Set', psEntities.MainScriptEntities.setEncoding()))
    combinedFooter.add(setButton)

    if psEntities.MainScriptEntities.readConfigFile('TP')['TP']:
        trainPlayerButton = javax.swing.JButton(unicode(u'TrainPlayer', psEntities.MainScriptEntities.setEncoding()))
        combinedFooter.add(trainPlayerButton)

    return combinedFooter

# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import java.awt
import javax.swing

from psEntities import MainScriptEntities
from TrackPattern import ViewEntities

'''Display methods for the Pattern Report for Track X form'''

scriptName = 'OperationsPatternScripts.ViewSetCarsForm'
scriptRev = 20220101

def patternReportForTrackWindow(patternReportForTrackForm):

    setCarsWindow = jmri.util.JmriJFrame()
    setCarsWindow.add(patternReportForTrackForm)

    return setCarsWindow

def makePatternReportForTrackForm(setCarsForm):
    '''Creates and populates the "Pattern Report for Track X" form'''

    configFile = MainScriptEntities.readConfigFile('TP')

    buttonDict = {}

    patternReportForm = javax.swing.JPanel()
    patternReportForm.setLayout(javax.swing.BoxLayout(patternReportForm, javax.swing.BoxLayout.PAGE_AXIS))

    patternReportFormHeader = makePatternReportFormHeader(setCarsForm)
    patternReportForm.add(patternReportFormHeader)
    patternReportForm.add(javax.swing.JSeparator())

    trackLocation = unicode(setCarsForm['locations'][0]['locationName'], MainScriptEntities.setEncoding())
    allTracksAtLoc =  MainScriptEntities._lm.getLocationByName(trackLocation).getTracksByNameList(None)
    patternReportRowOfTracks, buttonList = makePatternReportRowOfTracks(allTracksAtLoc)
    buttonDict['trackButtons'] = buttonList
    patternReportForm.add(patternReportRowOfTracks)
    patternReportForm.add(javax.swing.JSeparator())

    patternReportFormBody = javax.swing.JPanel()
    patternReportFormBody.setLayout(javax.swing.BoxLayout(patternReportFormBody, javax.swing.BoxLayout.PAGE_AXIS))

    setCarsEqptRows = MakeSetCarsEqptRows(setCarsForm)

    rollingStockRows, textBoxEntry = setCarsEqptRows.makeSetCarsRsRows()
    for rollingStock in rollingStockRows:
        patternReportFormBody.add(rollingStock)

    # listOfLocoRows, textBoxEntry = setCarsEqptRows.makeSetCarsLocoRows()
    # for loco in listOfLocoRows:
    #     patternReportFormBody.add(loco)
    # listOfCarRows, carBoxEntry = setCarsEqptRows.makeSetCarsCarRows()
    # for car in listOfCarRows:
    #     patternReportFormBody.add(car)
    # for item in carBoxEntry:
    #     textBoxEntry.append(item)
    buttonDict['textBoxEntry'] = textBoxEntry


    patternReportFormPane = javax.swing.JScrollPane(patternReportFormBody)
    patternReportForm.add(patternReportFormPane)
    patternReportForm.add(javax.swing.JSeparator())

    setCarsSchedule, scheduleButton = makeSetCarsScheduleRow(setCarsForm)
    buttonDict['scheduleButton'] = []
    if (setCarsSchedule):
        patternReportForm.add(setCarsSchedule)
        buttonDict['scheduleButton'] = scheduleButton
        patternReportForm.add(javax.swing.JSeparator())

    setCarsFooter = MakeSetCarsFooter()
    buttonDict['footerButtons'] = setCarsFooter.getComponents()
    patternReportForm.add(setCarsFooter)

    return patternReportForm, buttonDict

def makeSwingBox(xWidth, yHeight):
    '''Makes a swing box to the desired size'''

    xName = javax.swing.Box(javax.swing.BoxLayout.X_AXIS)
    xName.setPreferredSize(java.awt.Dimension(width=xWidth, height=yHeight))

    return xName

def makePatternReportFormHeader(setCarsForm):
    '''Creates the "Pattern Report for Track X" forms header'''

    configFile = MainScriptEntities.readConfigFile('TP')

    combinedHeader = javax.swing.JPanel()
    combinedHeader.setLayout(javax.swing.BoxLayout(combinedHeader, javax.swing.BoxLayout.PAGE_AXIS))

    headerRRLabel = javax.swing.JLabel(setCarsForm['railroad'])
    headerRRBox = makeSwingBox(100, configFile['PH'])
    headerRRBox.add(headerRRLabel)

    headerValidLabel = javax.swing.JLabel(setCarsForm['date'])
    headerValidBox = makeSwingBox(100, configFile['PH'])
    headerValidBox.add(headerValidLabel)

    headerYTLabel = javax.swing.JLabel()
    trackName = setCarsForm['locations'][0]['tracks'][0]['trackName'] # There's only one track
    locationName = setCarsForm['locations'][0]['locationName'] # There's only one location
    headerYTLabel.setText('Pattern report for track: ' + trackName + ' at ' + locationName)
    headerYTBox = makeSwingBox(100, configFile['PH'])
    headerYTBox.add(headerYTLabel)

    combinedHeader.add(headerRRBox)
    combinedHeader.add(headerYTBox)
    combinedHeader.add(headerValidBox)
    combinedHeader.border = javax.swing.BorderFactory.createEmptyBorder(5,0,5,0)

    return combinedHeader

def makePatternReportRowOfTracks(allTracksAtLoc):

    buttonPanel = javax.swing.JPanel()
    buttonList = []
    for track in allTracksAtLoc:
        selectTrackButton = javax.swing.JButton(track.getName())
        buttonList.append(selectTrackButton)
        buttonPanel.add(selectTrackButton)

    return buttonPanel, buttonList

class MakeSetCarsEqptRows():

    def __init__(self, setCarsForm):

        self.scriptName = 'OperationsPatternScripts.MakeSetCarsEqptRows'
        self.scriptRev = 20220101

        self.reportWidth = MainScriptEntities.readConfigFile('TP')['RW']
        fontSize = MainScriptEntities._pm.getFontSize()
        self.panelHeight = fontSize + 4
        self.panelWidth = fontSize - 2

        self.setCarsForm = setCarsForm
        self.locoRowLength = 0
        self.carRowLength = 0

        return

    def makeRsRowAdjustment(self):
        '''I can't figure out how to left justify JAVAX so I'm doing this BS work around'''

        for item in jmri.jmrit.operations.setup.Setup.getDropEngineMessageFormat():
            self.locoRowLength += self.reportWidth[item]

        for item in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
            self.carRowLength += self.reportWidth[item]

        rowAdjustment = 0 # catches rows of the samelength
        shorterRow = ''
        if self.locoRowLength < self.carRowLength:
            rowAdjustment = (self.carRowLength - self.locoRowLength) * self.panelWidth
            shorterRow = 'loco'

        if self.locoRowLength > self.carRowLength:
            rowAdjustment = (self.locoRowLength - self.carRowLength + 1) * self.panelWidth
            shorterRow = 'car'

        return rowAdjustment, shorterRow

    def makeSetCarsRsRows(self):

        rowAdjustment, shorterRow = self.makeRsRowAdjustment()
        # rowAdjustment += self.panelWidth * 6

        listOfEqptRows = []
        textBoxEntry = []

        locos = self.setCarsForm['locations'][0]['tracks'][0]['locos']
        for loco in locos:
            combinedInputLine = javax.swing.JPanel()
            # combinedInputLine.setPreferredSize(java.awt.Dimension(width=rowAdjustment, height=self.panelHeight + 8))
            # combinedInputLine = makeSwingBox(rowAdjustment, self.panelHeight + 1)
            combinedInputLine.setBackground(MainScriptEntities.FADED)
            inputText = javax.swing.JTextField(5)
            textBoxEntry.append(inputText)
            inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
            inputBox.add(inputText)
            combinedInputLine.add(inputBox)
            for item in jmri.jmrit.operations.setup.Setup.getDropEngineMessageFormat():
                label = javax.swing.JLabel(loco[item])
                box = makeSwingBox(self.reportWidth[item] * self.panelWidth, self.panelHeight)
                box.add(label)
                combinedInputLine.add(box)
            if shorterRow == 'loco':
                combinedInputLine.add(makeSwingBox(rowAdjustment, self.panelHeight))
            listOfEqptRows.append(combinedInputLine)

        cars = self.setCarsForm['locations'][0]['tracks'][0]['cars']
        for car in cars:
            combinedInputLine = javax.swing.JPanel()
            # combinedInputLine.setPreferredSize(java.awt.Dimension(width=rowAdjustment, height=self.panelHeight + 8))
            # combinedInputLine = makeSwingBox(rowAdjustment, self.panelHeight + 1)
            combinedInputLine.setBackground(MainScriptEntities.DUST)
            # combinedInputLine.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
            inputText = javax.swing.JTextField(5)
            textBoxEntry.append(inputText)
            inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
            inputBox.add(inputText)
            combinedInputLine.add(inputBox)
            for item in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
                label = javax.swing.JLabel(car[item])
                box = makeSwingBox(self.reportWidth[item] * self.panelWidth, self.panelHeight)
                box.add(label)
                combinedInputLine.add(box)
            if shorterRow == 'car':
                combinedInputLine.add(makeSwingBox(rowAdjustment, self.panelHeight))
            listOfEqptRows.append(combinedInputLine)

        return listOfEqptRows, textBoxEntry

    # def makeSetCarsLocoRows(self):
    #     '''Creates the locomotive lines of the pattern report form'''
    #
    #     listOfLocoRows = []
    #     textBoxEntry = []
    #     locos = self.setCarsForm['locations'][0]['tracks'][0]['locos']
    #
    #     for loco in locos:
    #         combinedInputLine = javax.swing.JPanel()
    #         combinedInputLine.setBackground(MainScriptEntities.FADED)
    #         inputText = javax.swing.JTextField(5)
    #         textBoxEntry.append(inputText)
    #         inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
    #         inputBox.add(inputText)
    #         combinedInputLine.add(inputBox)
    #
    #         for item in jmri.jmrit.operations.setup.Setup.getDropEngineMessageFormat():
    #             label = javax.swing.JLabel(loco[item])
    #             box = makeSwingBox(self.reportWidth[item] * self.panelWidth, self.panelHeight)
    #             box.add(label)
    #             combinedInputLine.add(box)
    #
    #         combinedInputLine.add(javax.swing.Box.createHorizontalGlue())
    #
    #         listOfLocoRows.append(combinedInputLine)
    #
    #     return listOfLocoRows, textBoxEntry
    #
    # def makeSetCarsCarRows(self):
    #     '''Creates the car lines of the pattern report form'''
    #
    #     listOfCarRows = []
    #     textBoxEntry = []
    #     cars = self.setCarsForm['locations'][0]['tracks'][0]['cars']
    #
    #     for car in cars:
    #         combinedInputLine = javax.swing.JPanel()
    #         combinedInputLine.setBackground(MainScriptEntities.DUST)
    #         inputText = javax.swing.JTextField(5)
    #         textBoxEntry.append(inputText)
    #         inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
    #         inputBox.add(inputText)
    #         combinedInputLine.add(inputBox)
    #
    #         for item in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
    #             label = javax.swing.JLabel(car[item])
    #             box = makeSwingBox(self.reportWidth[item] * self.panelWidth, self.panelHeight)
    #             box.add(label)
    #             combinedInputLine.add(box)
    #         combinedInputLine.add(javax.swing.Box.createHorizontalGlue())
    #         listOfCarRows.append(combinedInputLine)
    #
    #     return listOfCarRows, textBoxEntry

def makeSetCarsScheduleRow(setCarsForm):
    '''Using [0] to avoid for loop since there is only 1 location and track'''

    trackLocation = setCarsForm['locations'][0]['locationName']
    trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
    trackObject = MainScriptEntities._lm.getLocationByName(trackLocation).getTrackByName(trackName, None)
    scheduleObject = trackObject.getSchedule()
    schedulePanel = None
    scheduleList = []
    if (scheduleObject):
        schedulePanel = javax.swing.JPanel()
        scheduleButton = javax.swing.JButton(scheduleObject.getName())
        scheduleList.append(scheduleButton)
        schedulePanel.add(javax.swing.JLabel(u'Schedule: '))
        schedulePanel.add(scheduleButton)

    return schedulePanel, scheduleList

def MakeSetCarsFooter():

    combinedFooter = javax.swing.JPanel()

    printButton = javax.swing.JButton(unicode(u'Print', MainScriptEntities.setEncoding()))
    combinedFooter.add(printButton)

    setButton = javax.swing.JButton(unicode(u'Set', MainScriptEntities.setEncoding()))
    combinedFooter.add(setButton)

    if MainScriptEntities.readConfigFile('TP')['TI']:
        trainPlayerButton = javax.swing.JButton(unicode(u'TrainPlayer', MainScriptEntities.setEncoding()))
        combinedFooter.add(trainPlayerButton)

    return combinedFooter

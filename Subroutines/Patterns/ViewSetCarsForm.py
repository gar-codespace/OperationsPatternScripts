# coding=utf-8
# © 2023 Greg Ritacco

"""Display methods for the Set Cars Form for Track X form"""

from opsEntities import PSE
from Subroutines.Patterns import ViewEntities
from Subroutines.Patterns import ModelSetCarsForm
from Subroutines.Patterns import ModelEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.PT.ViewSetCarsForm')


def switchListAsCsv(textBoxEntry):
    """Track Pattern Report json is written as a CSV file
        Called by:
        ControllerSetCarsForm.CreateSetCarsFormGui.switchListButton
        """

    _psLog.debug('switchListAsCsv')
#  Get json data
    fileName = PSE.BUNDLE['ops-work-list'] + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', fileName)
    trackPattern = PSE.genericReadReport(targetPath)
    trackPattern = PSE.loadJson(trackPattern)
# Process json data into CSV
    userInputList = ModelEntities.makeUserInputList(textBoxEntry)
    trackPattern = ModelEntities.merge(trackPattern, userInputList)

    trackPattern = ModelSetCarsForm.makeMergedForm(trackPattern, textBoxEntry)
    trackPatternCsv = ViewEntities.makeTrackPatternCsv(trackPattern)
# Write CSV data
    fileName = PSE.BUNDLE['Switch List'] + '.csv'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'csvSwitchLists', fileName)
    PSE.genericWriteReport(targetPath, trackPatternCsv)

    return

def maksSwitchList():
    """Formats and displays the Switch List report.
        Called by:
        ControllerSetCarsForm.CreateSetCarsFormGui.switchListButton
        """

    _psLog.debug('maksSwitchList')

    PSE.REPORT_ITEM_WIDTH_MATRIX = ViewEntities.makeReportItemWidthMatrix()

# Get the switch list
    fileName = PSE.BUNDLE['ops-switch-list'] + '.json'
    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchLists', fileName)
    switchList = PSE.genericReadReport(targetPath)
    switchList = PSE.loadJson(switchList)

    reportHeader = ViewEntities.makeTextReportHeader(switchList)
    reportLocations = PSE.BUNDLE['Switch List'] + '\n\n'
    reportLocations += ViewEntities.makeTextReportLocations(switchList, trackTotals=False)

    return reportHeader + reportLocations

def setCarsPopup():
    """When the Set Rollingstock For Track: Window/Set Rollingstock to Track button is pressed
        this popup is displayed to select apply schedule and ignore track length
        on a per track basis.
        """

    configFile = PSE.readConfigFile('Patterns')
    widgets = []

    popupFrame = PSE.JMRI.util.JmriJFrame()
    popupFrame.setName('popupFrame')
    popupFrame.setTitle(PSE.BUNDLE['Additional Choices'])
    
    popupPanel = PSE.JAVX_SWING.JPanel()
    popupPanel.setName('popupPanel')
    popupPanel.setLayout(PSE.JAVX_SWING.BoxLayout(popupPanel, PSE.JAVX_SWING.BoxLayout.Y_AXIS))
    # popupPanel.setAlignmentY(PSE.JAVX_SWING.JPanel.CENTER_ALIGNMENT)
# Check box items
    checkBoxPanel = PSE.JAVX_SWING.JPanel()
    checkBoxPanel.setLayout(PSE.JAVX_SWING.BoxLayout(checkBoxPanel, PSE.JAVX_SWING.BoxLayout.Y_AXIS))
    checkBoxPanel.setAlignmentX(PSE.JAVX_SWING.JPanel.CENTER_ALIGNMENT)
    checkBoxPanel.setName('checkBoxPanel')

    applySchedule = PSE.JAVX_SWING.JCheckBox()
    applySchedule.setText(PSE.BUNDLE['Apply the destination tracks schedule'])
    applySchedule.setSelected(configFile['AS'])
    applySchedule.setName('asCheckBox')
    widgets.append(applySchedule)
    
    ignoreTrackLength = PSE.JAVX_SWING.JCheckBox()
    ignoreTrackLength.setText(PSE.BUNDLE['Ignore track length'])
    ignoreTrackLength.setSelected(configFile['PI'])
    ignoreTrackLength.setName('itlCheckBox')
    widgets.append(ignoreTrackLength)

    checkBoxPanel.add(applySchedule)
    checkBoxPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
    checkBoxPanel.add(ignoreTrackLength)
# Buttons
    buttonRow = PSE.JAVX_SWING.JPanel()
    buttonRow.setName('buttonRow')

    setCarsButton = PSE.JAVX_SWING.JButton()
    setCarsButton.setText(PSE.BUNDLE['Set Cars'])
    setCarsButton.setName('setCarsButton')
    widgets.append(setCarsButton)

    cancelButton = PSE.JAVX_SWING.JButton()
    cancelButton.setText(PSE.BUNDLE['Cancel'])
    cancelButton.setName('cancelButton')
    widgets.append(cancelButton)

    buttonRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
    buttonRow.add(setCarsButton)
    buttonRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
    buttonRow.add(cancelButton)
    buttonRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
# Build the panel
    popupPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,20)))
    popupPanel.add(checkBoxPanel)
    popupPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,20)))
    popupPanel.add(PSE.JAVX_SWING.JSeparator())
    popupPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,20)))
    popupPanel.add(buttonRow)
    popupPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,20)))

    popupFrame.add(popupPanel)
    popupFrame.pack()

    return popupFrame, widgets

def setCarsForTrackWindow(setCarsForTrackForm):
    """Called by:
        ControllerSetCarsForm.CreateSetCarsFormGui.makeFrame
        """

    setCarsWindow = PSE.JMRI.util.JmriJFrame()
    setCarsWindow.add(setCarsForTrackForm)

    return setCarsWindow

def makeSetCarsForTrackForm(setCarsFormData):
    """Creates and populates the 'Set Cars Form for Track X' form
        Called by:
        ControllerSetCarsForm.CreateSetCarsFormGui.makeFrame
        """

    _psLog.debug('makeSetCarsForTrackForm')

    buttonDict = {}

    setCarsForm = PSE.JAVX_SWING.JPanel()
    setCarsForm.setLayout(PSE.JAVX_SWING.BoxLayout(
        setCarsForm, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)
        )

    setCarsFormHeader = makeSetCarsFormHeader(setCarsFormData)
    setCarsForm.add(setCarsFormHeader)
    setCarsForm.add(PSE.JAVX_SWING.JSeparator())

    setCarsRowOfTracks, buttonList = makeSetCarsTrackButtons()
    buttonDict['trackButtons'] = buttonList
    setCarsForm.add(setCarsRowOfTracks)
    setCarsForm.add(PSE.JAVX_SWING.JSeparator())

    setCarsFormBody = PSE.JAVX_SWING.JPanel()
    setCarsFormBody.setLayout(PSE.JAVX_SWING.BoxLayout(
        setCarsFormBody, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)
        )

    setCarsEqptRows = MakeSetCarsEqptRows(setCarsFormData)

    if setCarsFormData['locations'][0]['tracks'][0]['locos']:
        locoFormBody = PSE.JAVX_SWING.JPanel()
        locoFormBody.setLayout(PSE.JAVX_SWING.BoxLayout(
            locoFormBody, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)
            )
        locoFormBody.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder( \
                PSE.BUNDLE['Locomotives at'] \
                +  ' ' + setCarsFormData['locations'][0]['tracks'][0]['trackName'] \
                )

        setCarsLocoRows = setCarsEqptRows.makeSetCarsLocoRows()
        for loco in setCarsLocoRows:
            locoFormBody.add(loco)
        setCarsFormBody.add(locoFormBody)

    if setCarsFormData['locations'][0]['tracks'][0]['cars']:
        carFormBody = PSE.JAVX_SWING.JPanel()
        carFormBody.setLayout(PSE.JAVX_SWING.BoxLayout(
            carFormBody, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)
            )
        carFormBody.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder( \
                PSE.BUNDLE['Cars at'] \
                +  ' ' + setCarsFormData['locations'][0]['tracks'][0]['trackName'] \
                )

        setCarsCarRows = setCarsEqptRows.makeSetCarsCarRows()
        for car in setCarsCarRows:
            carFormBody.add(car)
        setCarsFormBody.add(carFormBody)

    buttonDict['textBoxEntry'] = setCarsEqptRows.textBoxEntryList()

    setCarsFormPane = PSE.JAVX_SWING.JScrollPane(setCarsFormBody)
    setCarsForm.add(setCarsFormPane)
    setCarsForm.add(PSE.JAVX_SWING.JSeparator())

    setCarsSchedule, scheduleButton = makeSetCarsScheduleRow(setCarsFormData)
    buttonDict['scheduleButton'] = []
    if setCarsSchedule:
        setCarsForm.add(setCarsSchedule)
        buttonDict['scheduleButton'] = scheduleButton
        setCarsForm.add(PSE.JAVX_SWING.JSeparator())

    setCarsFooter, footerButtons = MakeSetCarsFooter()
    buttonDict['footerButtons'] = footerButtons
    setCarsForm.add(setCarsFooter)

    return setCarsForm, buttonDict

def makeSwingBox(xWidth, yHeight):
    """Makes a swing box to the desired size
        Called by:
        makeSetCarsFormHeader
        makeSetCarsCarRows
        makeSetCarsLocoRows
        """

    xName = PSE.JAVX_SWING.Box(PSE.JAVX_SWING.BoxLayout.X_AXIS)
    xName.setPreferredSize(PSE.JAVA_AWT.Dimension(width=xWidth, height=yHeight))

    return xName

def makeSetCarsFormHeader(setCarsFormData):
    """Creates the 'Set Cars Form for Track X' forms header
        Called by:
        makeSetCarsForTrackForm
        """

    _psLog.debug('makeSetCarsFormHeader')

    splitName = setCarsFormData['railroadName'].split('\n')
    trackName = setCarsFormData['locations'][0]['tracks'][0]['trackName'] # There's only one track
    locationName = setCarsFormData['locations'][0]['locationName'] # There's only one location
    validDate = setCarsFormData['date']

    headerTrackLabel = PSE.JAVX_SWING.JLabel()
    headerTrackLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
    headerTrackLabel.setText(PSE.BUNDLE['Set Rolling Stock for track:'] + ' ' + trackName + ' ' + PSE.BUNDLE['at'] + ' ' + locationName)

    headerValidLabel = PSE.JAVX_SWING.JLabel()
    headerValidLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
    headerValidLabel.setText(validDate)

    combinedHeader = PSE.JAVX_SWING.JPanel()
    combinedHeader.setLayout(PSE.JAVX_SWING.BoxLayout(combinedHeader, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
    combinedHeader.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
    combinedHeader.border = PSE.JAVX_SWING.BorderFactory.createEmptyBorder(10,0,10,0)

    for item in splitName:
        headerDetailLabel = PSE.JAVX_SWING.JLabel()
        headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
        headerDetailLabel.setText(item)
        combinedHeader.add(headerDetailLabel)
    combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,10)))
    combinedHeader.add(headerTrackLabel)
    combinedHeader.add(headerValidLabel)

    return combinedHeader

def makeSetCarsTrackButtons():
    """Called by:
        makeSetCarsForTrackForm
        """

    location =  PSE.readConfigFile('Patterns')['PL']
    allTracksAtLoc =  PSE.LM.getLocationByName(location).getTracksByNameList(None)

    buttonPanel = PSE.JAVX_SWING.JPanel()
    buttonPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder( \
            PSE.BUNDLE['Tracks at'] \
            +  ' ' + location \
            )
    buttonList = []
    for track in allTracksAtLoc:
        selectTrackButton = PSE.JAVX_SWING.JButton(track.getName())
        buttonList.append(selectTrackButton)
        buttonPanel.add(selectTrackButton)

    return buttonPanel, buttonList


class MakeSetCarsEqptRows():
    """Called by:
        makeSetCarsForTrackForm
        """

    def __init__(self, setCarsFormData):

        self.SCRIPT_NAME = 'OperationsPatternScripts.MakeSetCarsEqptRows'

        PSE.REPORT_ITEM_WIDTH_MATRIX = ViewEntities.makeReportItemWidthMatrix()

        self.reportWidth = PSE.REPORT_ITEM_WIDTH_MATRIX
        fontSize = PSE.PM.getFontSize()
        self.panelHeight = fontSize + 4
        self.panelWidth = fontSize - 2

        self.setCarsFormData = setCarsFormData
        self.textBoxEntry = []

        self.rosetta = PSE.translateMessageFormat()
        self.carColor = PSE.getColorA()
        self.locoColor = PSE.getColorB()
        self.alertColor = PSE.getColorC()

        return

    def makeSetCarsLocoRows(self):
        """Creates the locomotive lines of the pattern report form"""

        listOfLocoRows = []
        locos = self.setCarsFormData['locations'][0]['tracks'][0]['locos']

        for loco in locos:
            combinedInputLine = PSE.JAVX_SWING.JPanel()
            combinedInputLine.setBackground(self.locoColor)
            if loco['On_Train']:
                combinedInputLine.setBackground(self.alertColor)
            inputText = PSE.JAVX_SWING.JTextField(5)
            self.textBoxEntry.append(inputText)
            inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
            inputBox.add(inputText)
            combinedInputLine.add(inputBox)

            for item in PSE.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat():
                if 'Tab' in item:
                    continue
                translatedItem = self.rosetta[item]
                label = PSE.JAVX_SWING.JLabel(loco[translatedItem])
                box = makeSwingBox(self.reportWidth[translatedItem] * self.panelWidth, self.panelHeight)
                box.add(label)
                combinedInputLine.add(box)

            combinedInputLine.add(PSE.JAVX_SWING.Box.createHorizontalGlue())

            listOfLocoRows.append(combinedInputLine)

        return listOfLocoRows

    def makeSetCarsCarRows(self):
        """Creates the car lines of the pattern report form"""

        listOfCarRows = []
        cars = self.setCarsFormData['locations'][0]['tracks'][0]['cars']

        for car in cars:
            combinedInputLine = PSE.JAVX_SWING.JPanel()
            combinedInputLine.setBackground(self.carColor)
            if car['On_Train']:
                combinedInputLine.setBackground(self.alertColor)
            inputText = PSE.JAVX_SWING.JTextField(5)
            self.textBoxEntry.append(inputText)
            inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
            inputBox.add(inputText)
            combinedInputLine.add(inputBox)

            for item in PSE.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
                if 'Tab' in item:
                    continue
                translatedItem = self.rosetta[item]
                try:
                    label = PSE.JAVX_SWING.JLabel(car[translatedItem])
                except: # The hazardous field is a boolean so work around it
                    label = PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Hazardous'])
                box = makeSwingBox(self.reportWidth[translatedItem] * self.panelWidth, self.panelHeight)
                box.add(label)
                combinedInputLine.add(box)
            combinedInputLine.add(PSE.JAVX_SWING.Box.createHorizontalGlue())
            listOfCarRows.append(combinedInputLine)

        return listOfCarRows

    def textBoxEntryList(self):

        return self.textBoxEntry


def makeSetCarsScheduleRow(setCarsFormData):
    """Using [0] to avoid for loop since there is only 1 location and track
        Used By:
        makeSetCarsForTrackForm
        """

    _psLog.debug('makeSetCarsScheduleRow')

    trackLocation = setCarsFormData['locations'][0]['locationName']
    trackName = setCarsFormData['locations'][0]['tracks'][0]['trackName']
    trackObject = PSE.LM.getLocationByName(trackLocation).getTrackByName(trackName, None)
    scheduleObject = trackObject.getSchedule()
    schedulePanel = None
    scheduleList = []
    if scheduleObject:
        schedulePanel = PSE.JAVX_SWING.JPanel()
        schedulePanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(
            PSE.BUNDLE['Schedule for'] + ' ' + trackName
            )
        scheduleButton = PSE.JAVX_SWING.JButton(scheduleObject.getName())
        scheduleList.append(scheduleButton)
        schedulePanel.add(PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Schedule:'] + ' '))
        schedulePanel.add(scheduleButton)

    return schedulePanel, scheduleList

def MakeSetCarsFooter():
    """Makes 2 panels, Make Work and Report Work, and adds buttons to the panels
        Used By:
        makeSetCarsForTrackForm
        """

    _psLog.debug('MakeSetCarsFooter')

    makeWorkPanel = PSE.JAVX_SWING.JPanel()
    makeWorkPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(
        unicode(PSE.BUNDLE['Make Work'], PSE.ENCODING)
        )

    printButton = PSE.JAVX_SWING.JButton(
        unicode(PSE.BUNDLE['Switch List'], PSE.ENCODING)
        )


    makeWorkPanel.add(PSE.JAVX_SWING.Box.createRigidArea(
        PSE.JAVA_AWT.Dimension(20,0))
        )
    makeWorkPanel.add(printButton)
    makeWorkPanel.add(PSE.JAVX_SWING.Box.createRigidArea(
        PSE.JAVA_AWT.Dimension(20,0))
        )

    reportWorkPanel = PSE.JAVX_SWING.JPanel()
    reportWorkPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(
        unicode(PSE.BUNDLE['Report Work'], PSE.ENCODING)
        )

    setButton = PSE.JAVX_SWING.JButton(
        unicode(PSE.BUNDLE['Set Rolling Stock to Track'], PSE.ENCODING)
        )

    reportWorkPanel.add(PSE.JAVX_SWING.Box.createRigidArea(
        PSE.JAVA_AWT.Dimension(20,0))
        )
    reportWorkPanel.add(setButton)
    reportWorkPanel.add(PSE.JAVX_SWING.Box.createRigidArea(
        PSE.JAVA_AWT.Dimension(20,0))
        )

    combinedFooter = PSE.JAVX_SWING.JPanel()
    combinedFooter.add(makeWorkPanel)
    combinedFooter.add(reportWorkPanel)

    footerButtons = []
    footerButtons.append(printButton)
    footerButtons.append(setButton)

    return combinedFooter, footerButtons

# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Display methods for the Set Cars Form for Track X form"""

from psEntities import PSE
from PatternTracksSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewSetCarsForm'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.PT.ViewSetCarsForm')

def switchListButton(textBoxEntry):
    """Mini controller when the Switch List button is pressed.
        Formats and displays the Switch List for Track report.
        Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.switchListButton
        """

    _psLog.debug('switchListButton')

# Boilerplate
    reportName = PSE.BUNDLE['Switch List for Track']
    fileName = reportName + '.json'
    targetDir = PSE.PROFILE_PATH + '\\operations\\jsonManifests'
    targetPath = PSE.OS_Path.join(targetDir, fileName)
# Get the switch list
    switchList = PSE.genericReadReport(targetPath)
    switchList = PSE.loadJson(switchList)
# Replace Set To with a track name, reformat for display
    userInputList = ViewEntities.makeUserInputList(textBoxEntry)
    switchList = ViewEntities.merge(switchList, userInputList)
    switchList = ViewEntities.modifyTrackPatternReport(switchList)
# Make switch list for print
    reportHeader = ViewEntities.makeTextReportHeader(switchList)
    reportLocations = ViewEntities.makeTextReportLocations(switchList, trackTotals=False)
# Save formatted data
    targetDir = PSE.PROFILE_PATH + '\\operations\\patternReports'
    fileName = reportName + '.txt'
    targetPath = PSE.OS_Path.join(targetDir, fileName)
    PSE.genericWriteReport(targetPath, reportHeader + reportLocations)
# Display formatted data
    PSE.genericDisplayReport(targetPath)

    return

def o2oButton(ptSetCarsForm, textBoxEntry):

# Replace Set To with a track name, reformat for display
    userInputList = ViewEntities.makeUserInputList(textBoxEntry)
    o2oSwitchList = ViewEntities.merge(ptSetCarsForm, userInputList)
    o2oSwitchList = ViewEntities.modifyTrackPatternReport(o2oSwitchList)

    return o2oSwitchList

def setCarsForTrackWindow(setCarsForTrackForm):
    """Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.makeFrame
        """

    setCarsWindow = PSE.JMRI.util.JmriJFrame()
    setCarsWindow.add(setCarsForTrackForm)

    return setCarsWindow

def makeSetCarsForTrackForm(setCarsFormData):
    """Creates and populates the 'Set Cars Form for Track X' form
        Used by:
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
    if setCarsSchedule and PSE.readConfigFile('PT')['AS']:
        setCarsForm.add(setCarsSchedule)
        buttonDict['scheduleButton'] = scheduleButton
        setCarsForm.add(PSE.JAVX_SWING.JSeparator())

    setCarsFooter, footerButtons = MakeSetCarsFooter()
    buttonDict['footerButtons'] = footerButtons
    setCarsForm.add(setCarsFooter)

    return setCarsForm, buttonDict

def makeSwingBox(xWidth, yHeight):
    """Makes a swing box to the desired size
        Used by:
        makeSetCarsFormHeader
        makeSetCarsCarRows
        makeSetCarsLocoRows
        """

    xName = PSE.JAVX_SWING.Box(PSE.JAVX_SWING.BoxLayout.X_AXIS)
    xName.setPreferredSize(PSE.JAVA_AWT.Dimension(width=xWidth, height=yHeight))

    return xName

def makeSetCarsFormHeader(setCarsFormData):
    """Creates the 'Set Cars Form for Track X' forms header
        Used by:
        makeSetCarsForTrackForm
        """

    _psLog.debug('makeSetCarsFormHeader')

    configFile = PSE.readConfigFile('PT')

    combinedHeader = PSE.JAVX_SWING.JPanel()
    combinedHeader.setLayout(PSE.JAVX_SWING.BoxLayout(
        combinedHeader, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)
        )
    combinedHeader.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
    combinedHeader.border = PSE.JAVX_SWING.BorderFactory.createEmptyBorder(10,0,10,0)

    headerRRLabel = PSE.JAVX_SWING.JLabel(setCarsFormData['railroad'])
    headerRRLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
    headerRRBox = makeSwingBox(100, configFile['PH'])
    headerRRBox.add(headerRRLabel)

    headerYTLabel = PSE.JAVX_SWING.JLabel()
    headerYTLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
    trackName = setCarsFormData['locations'][0]['tracks'][0]['trackName'] # There's only one track
    locationName = setCarsFormData['locations'][0]['locationName'] # There's only one location
    headerYTLabel.setText(PSE.BUNDLE['Set Rolling Stock for track:'] \
                + ' ' + trackName + ' ' + PSE.BUNDLE['at'] + ' ' + locationName)

    headerYTBox = makeSwingBox(100, configFile['PH'])
    headerYTBox.add(headerYTLabel)

    headerValidLabel = PSE.JAVX_SWING.JLabel(setCarsFormData['date'])
    headerValidLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
    headerValidBox = makeSwingBox(100, configFile['PH'])
    headerValidBox.add(headerValidLabel)

    combinedHeader.add(headerRRLabel)
    combinedHeader.add(headerYTLabel)
    combinedHeader.add(headerValidLabel)

    return combinedHeader

def makeSetCarsTrackButtons():
    """Used by:
        makeSetCarsForTrackForm
        """

    location =  PSE.readConfigFile('PT')['PL']
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
    """Used by:
        makeSetCarsForTrackForm
        """

    # _psLog.debug('MakeSetCarsEqptRows')

    def __init__(self, setCarsFormData):

        self.SCRIPT_NAME = 'OperationsPatternScripts.MakeSetCarsEqptRows'
        self.SCRIPT_REV = 20220101

        self.reportWidth = PSE.REPORT_ITEM_WIDTH_MATRIX
        fontSize = PSE.PM.getFontSize()
        self.panelHeight = fontSize + 4
        self.panelWidth = fontSize - 2

        self.setCarsFormData = setCarsFormData
        self.textBoxEntry = []

        self.rosetta = PSE.translateMessageFormat()
        self.carColor = PSE.getCarColor()
        self.locoColor = PSE.getLocoColor()
        self.alertColor = PSE.getAlertColor()

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

    o2oButton = PSE.JAVX_SWING.JButton(
        unicode(PSE.BUNDLE['o2o Work Events'], PSE.ENCODING)
        )
    if not PSE.readConfigFile()['CP']['SI'][1]['o2oSubroutine']:
        o2oButton.setVisible(False)

    makeWorkPanel.add(PSE.JAVX_SWING.Box.createRigidArea(
        PSE.JAVA_AWT.Dimension(20,0))
        )
    makeWorkPanel.add(printButton)
    makeWorkPanel.add(o2oButton)
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
    footerButtons.append(o2oButton)

    return combinedFooter, footerButtons

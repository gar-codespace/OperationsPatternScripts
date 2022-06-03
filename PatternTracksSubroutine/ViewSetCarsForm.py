# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Display methods for the Set Cars Form for Track X form"""

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewSetCarsForm'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.ViewSetCarsForm')

def setCarsForTrackWindow(setCarsForTrackForm):

    setCarsWindow = PatternScriptEntities.JMRI.util.JmriJFrame()
    setCarsWindow.add(setCarsForTrackForm)

    return setCarsWindow

def makeSetCarsForTrackForm(setCarsFormData):
    """Creates and populates the 'Set Cars Form for Track X' form"""

    _psLog.debug('makeSetCarsForTrackForm')

    buttonDict = {}

    setCarsForm = PatternScriptEntities.JAVX_SWING.JPanel()
    setCarsForm.setLayout(PatternScriptEntities.JAVX_SWING.BoxLayout(
        setCarsForm, PatternScriptEntities.JAVX_SWING.BoxLayout.PAGE_AXIS)
        )

    setCarsFormHeader = makeSetCarsFormHeader(setCarsFormData)
    setCarsForm.add(setCarsFormHeader)
    setCarsForm.add(PatternScriptEntities.JAVX_SWING.JSeparator())

    setCarsRowOfTracks, buttonList = makeSetCarsTrackButtons()
    buttonDict['trackButtons'] = buttonList
    setCarsForm.add(setCarsRowOfTracks)
    setCarsForm.add(PatternScriptEntities.JAVX_SWING.JSeparator())

    setCarsFormBody = PatternScriptEntities.JAVX_SWING.JPanel()
    setCarsFormBody.setLayout(PatternScriptEntities.JAVX_SWING.BoxLayout(
        setCarsFormBody, PatternScriptEntities.JAVX_SWING.BoxLayout.PAGE_AXIS)
        )

    setCarsEqptRows = MakeSetCarsEqptRows(setCarsFormData)

    if setCarsFormData['locations'][0]['tracks'][0]['locos']:
        locoFormBody = PatternScriptEntities.JAVX_SWING.JPanel()
        locoFormBody.setLayout(PatternScriptEntities.JAVX_SWING.BoxLayout(
            locoFormBody, PatternScriptEntities.JAVX_SWING.BoxLayout.PAGE_AXIS)
            )
        locoFormBody.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createTitledBorder( \
                PatternScriptEntities.BUNDLE['Locomotives at '] \
                + setCarsFormData['locations'][0]['tracks'][0]['trackName'] \
                )

        setCarsLocoRows = setCarsEqptRows.makeSetCarsLocoRows()
        for loco in setCarsLocoRows:
            locoFormBody.add(loco)
        setCarsFormBody.add(locoFormBody)

    if setCarsFormData['locations'][0]['tracks'][0]['cars']:
        carFormBody = PatternScriptEntities.JAVX_SWING.JPanel()
        carFormBody.setLayout(PatternScriptEntities.JAVX_SWING.BoxLayout(
            carFormBody, PatternScriptEntities.JAVX_SWING.BoxLayout.PAGE_AXIS)
            )
        carFormBody.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createTitledBorder( \
                PatternScriptEntities.BUNDLE['Cars at '] \
                + setCarsFormData['locations'][0]['tracks'][0]['trackName'] \
                )

        setCarsCarRows = setCarsEqptRows.makeSetCarsCarRows()
        for car in setCarsCarRows:
            carFormBody.add(car)
        setCarsFormBody.add(carFormBody)

    buttonDict['textBoxEntry'] = setCarsEqptRows.textBoxEntryList()

    setCarsFormPane = PatternScriptEntities.JAVX_SWING.JScrollPane(setCarsFormBody)
    setCarsForm.add(setCarsFormPane)
    setCarsForm.add(PatternScriptEntities.JAVX_SWING.JSeparator())

    setCarsSchedule, scheduleButton = makeSetCarsScheduleRow(setCarsFormData)
    buttonDict['scheduleButton'] = []
    if setCarsSchedule and PatternScriptEntities.readConfigFile('PT')['AS']:
        setCarsForm.add(setCarsSchedule)
        buttonDict['scheduleButton'] = scheduleButton
        setCarsForm.add(PatternScriptEntities.JAVX_SWING.JSeparator())

    setCarsFooter = MakeSetCarsFooter()
    buttonDict['footerButtons'] = setCarsFooter.getComponents()
    setCarsForm.add(setCarsFooter)

    return setCarsForm, buttonDict

def makeSwingBox(xWidth, yHeight):
    """Makes a swing box to the desired size"""

    xName = PatternScriptEntities.JAVX_SWING.Box(PatternScriptEntities.JAVX_SWING.BoxLayout.X_AXIS)
    xName.setPreferredSize(PatternScriptEntities.JAVA_AWT.Dimension(width=xWidth, height=yHeight))

    return xName

def makeSetCarsFormHeader(setCarsFormData):
    """Creates the 'Set Cars Form for Track X' forms header"""

    _psLog.debug('makeSetCarsFormHeader')

    configFile = PatternScriptEntities.readConfigFile('PT')

    combinedHeader = PatternScriptEntities.JAVX_SWING.JPanel()
    combinedHeader.setLayout(PatternScriptEntities.JAVX_SWING.BoxLayout(
        combinedHeader, PatternScriptEntities.JAVX_SWING.BoxLayout.PAGE_AXIS)
        )
    combinedHeader.setAlignmentX(PatternScriptEntities.JAVA_AWT.Component.CENTER_ALIGNMENT)
    combinedHeader.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createEmptyBorder(10,0,10,0)

    headerRRLabel = PatternScriptEntities.JAVX_SWING.JLabel(setCarsFormData['railroad'])
    headerRRLabel.setAlignmentX(PatternScriptEntities.JAVA_AWT.Component.CENTER_ALIGNMENT)
    headerRRBox = makeSwingBox(100, configFile['PH'])
    headerRRBox.add(headerRRLabel)

    headerYTLabel = PatternScriptEntities.JAVX_SWING.JLabel()
    headerYTLabel.setAlignmentX(PatternScriptEntities.JAVA_AWT.Component.CENTER_ALIGNMENT)
    trackName = setCarsFormData['locations'][0]['tracks'][0]['trackName'] # There's only one track
    locationName = setCarsFormData['locations'][0]['locationName'] # There's only one location
    headerYTLabel.setText(PatternScriptEntities.BUNDLE['Set Cars Form for track: '] \
            + trackName + PatternScriptEntities.BUNDLE[' at '] \
            + locationName)
    headerYTBox = makeSwingBox(100, configFile['PH'])
    headerYTBox.add(headerYTLabel)

    headerValidLabel = PatternScriptEntities.JAVX_SWING.JLabel(setCarsFormData['date'])
    headerValidLabel.setAlignmentX(PatternScriptEntities.JAVA_AWT.Component.CENTER_ALIGNMENT)
    headerValidBox = makeSwingBox(100, configFile['PH'])
    headerValidBox.add(headerValidLabel)

    combinedHeader.add(headerRRLabel)
    combinedHeader.add(headerYTLabel)
    combinedHeader.add(headerValidLabel)

    return combinedHeader

def makeSetCarsTrackButtons():

    location =  PatternScriptEntities.readConfigFile('PT')['PL']
    allTracksAtLoc =  PatternScriptEntities.LM.getLocationByName(location).getTracksByNameList(None)

    buttonPanel = PatternScriptEntities.JAVX_SWING.JPanel()
    buttonPanel.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createTitledBorder( \
            PatternScriptEntities.BUNDLE['Tracks at '] \
            + location \
            )
    buttonList = []
    for track in allTracksAtLoc:
        selectTrackButton = PatternScriptEntities.JAVX_SWING.JButton(track.getName())
        buttonList.append(selectTrackButton)
        buttonPanel.add(selectTrackButton)

    return buttonPanel, buttonList

class MakeSetCarsEqptRows():

    _psLog.debug('MakeSetCarsEqptRows')

    def __init__(self, setCarsFormData):

        self.SCRIPT_NAME = 'OperationsPatternScripts.MakeSetCarsEqptRows'
        self.SCRIPT_REV = 20220101

        self.reportWidth = PatternScriptEntities.readConfigFile('PT')['RW']
        fontSize = PatternScriptEntities.PM.getFontSize()
        self.panelHeight = fontSize + 4
        self.panelWidth = fontSize - 2

        self.setCarsFormData = setCarsFormData
        self.textBoxEntry = []

        return

    def makeSetCarsLocoRows(self):
        """Creates the locomotive lines of the pattern report form"""

        listOfLocoRows = []
        locos = self.setCarsFormData['locations'][0]['tracks'][0]['locos']

        for loco in locos:
            combinedInputLine = PatternScriptEntities.JAVX_SWING.JPanel()
            combinedInputLine.setBackground(PatternScriptEntities.getLocoColor())
            if loco['On Train']:
                combinedInputLine.setBackground(PatternScriptEntities.getAlertColor())
            inputText = PatternScriptEntities.JAVX_SWING.JTextField(5)
            self.textBoxEntry.append(inputText)
            inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
            inputBox.add(inputText)
            combinedInputLine.add(inputBox)

            for item in PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat():
                label = PatternScriptEntities.JAVX_SWING.JLabel(loco[PatternScriptEntities.BUNDLE[item]])
                box = makeSwingBox(self.reportWidth[PatternScriptEntities.BUNDLE[item]] \
                        * self.panelWidth, self.panelHeight \
                        )
                box.add(label)
                combinedInputLine.add(box)

            combinedInputLine.add(PatternScriptEntities.JAVX_SWING.Box.createHorizontalGlue())

            listOfLocoRows.append(combinedInputLine)

        PatternScriptEntities.backupConfigFile()
        return listOfLocoRows

    def makeSetCarsCarRows(self):
        """Creates the car lines of the pattern report form"""

        listOfCarRows = []
        cars = self.setCarsFormData['locations'][0]['tracks'][0]['cars']

        for car in cars:
            combinedInputLine = PatternScriptEntities.JAVX_SWING.JPanel()
            combinedInputLine.setBackground(PatternScriptEntities.getCarColor())
            if car['On Train']:
                combinedInputLine.setBackground(PatternScriptEntities.getAlertColor())
            inputText = PatternScriptEntities.JAVX_SWING.JTextField(5)
            self.textBoxEntry.append(inputText)
            inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
            inputBox.add(inputText)
            combinedInputLine.add(inputBox)

            for item in PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
                label = PatternScriptEntities.JAVX_SWING.JLabel(car[PatternScriptEntities.BUNDLE[item]])
                box = makeSwingBox(self.reportWidth[PatternScriptEntities.BUNDLE[item]] \
                        * self.panelWidth, self.panelHeight \
                        )
                box.add(label)
                combinedInputLine.add(box)
            combinedInputLine.add(PatternScriptEntities.JAVX_SWING.Box.createHorizontalGlue())
            listOfCarRows.append(combinedInputLine)

        PatternScriptEntities.backupConfigFile()
        return listOfCarRows

    def textBoxEntryList(self):

        return self.textBoxEntry

def makeSetCarsScheduleRow(setCarsFormData):
    """Using [0] to avoid for loop since there is only 1 location and track"""

    _psLog.debug('makeSetCarsScheduleRow')

    trackLocation = setCarsFormData['locations'][0]['locationName']
    trackName = setCarsFormData['locations'][0]['tracks'][0]['trackName']
    trackObject = PatternScriptEntities.LM.getLocationByName(trackLocation).getTrackByName(trackName, None)
    scheduleObject = trackObject.getSchedule()
    schedulePanel = None
    scheduleList = []
    if (scheduleObject):
        schedulePanel = PatternScriptEntities.JAVX_SWING.JPanel()
        schedulePanel.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createTitledBorder(
            PatternScriptEntities.BUNDLE['Schedule for '] + trackName
            )
        scheduleButton = PatternScriptEntities.JAVX_SWING.JButton(scheduleObject.getName())
        scheduleList.append(scheduleButton)
        schedulePanel.add(PatternScriptEntities.JAVX_SWING.JLabel(PatternScriptEntities.BUNDLE['Schedule: ']))
        schedulePanel.add(scheduleButton)

    return schedulePanel, scheduleList

def MakeSetCarsFooter():

    _psLog.debug('MakeSetCarsFooter')

    combinedFooter = PatternScriptEntities.JAVX_SWING.JPanel()
    combinedFooter.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createTitledBorder(
        PatternScriptEntities.BUNDLE['Action']
        )

    printButton = PatternScriptEntities.JAVX_SWING.JButton(unicode(
        PatternScriptEntities.BUNDLE['Switch List'], PatternScriptEntities.ENCODING)
        )
    combinedFooter.add(printButton)

    setButton = PatternScriptEntities.JAVX_SWING.JButton(
        unicode(PatternScriptEntities.BUNDLE['Set to Track'], PatternScriptEntities.ENCODING)
        )
    combinedFooter.add(setButton)

    if PatternScriptEntities.readConfigFile('PT')['TI']:
        trainPlayerButton = PatternScriptEntities.JAVX_SWING.JButton(
            unicode(u'TrainPlayer', PatternScriptEntities.ENCODING)
            )
        combinedFooter.add(trainPlayerButton)

    return combinedFooter

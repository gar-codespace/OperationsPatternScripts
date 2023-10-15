# coding=utf-8
# © 2023 Greg Ritacco

"""
All the GUI items are made here.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.PT.GUI')

def makeSwingBox(xWidth, yHeight):
    """Makes a swing box to the desired size."""

    swingBox = PSE.JAVX_SWING.Box(PSE.JAVX_SWING.BoxLayout.X_AXIS)
    swingBox.setPreferredSize(PSE.JAVA_AWT.Dimension(width=xWidth, height=yHeight))

    return swingBox
    

class subroutineGui:
    """
    Makes the Patterns subroutine panel.
    The Controller manages the combo boxes.
    Called by:
    View.ManageGui.makeSubroutinePanel
    """

    def __init__(self):

        self.patternsConfigFile = PSE.readConfigFile('Patterns')

    # The Divisions combo box content is managed by the Controller
        self.divisionComboBox = PSE.JAVX_SWING.JComboBox()
        self.divisionComboBox.setName('jDivisions')

    # The Locations combo box content is managed by the Controller
        self.locationComboBox = PSE.JAVX_SWING.JComboBox()
        self.locationComboBox.setName('jLocations')

        self.yardTracksOnly = PSE.JAVX_SWING.JCheckBox()
        self.yardTracksOnly.setText(PSE.getBundleItem('Yard tracks only') + ' ')
        self.yardTracksOnly.setSelected(self.patternsConfigFile['PA'])
        self.yardTracksOnly.setName('ytoCheckBox')

        self.ypButton = PSE.JAVX_SWING.JButton()
        self.ypButton.setText(PSE.getBundleItem('Track Inquiry'))
        self.ypButton.setName('ypButton')

        self.scButton = PSE.JAVX_SWING.JButton()
        self.scButton.setText(PSE.getBundleItem('Set Rolling Stock to Track'))
        self.scButton.setName('scButton')

        self.trackCheckBoxes = []

        return

    def getGuiFrame(self):
        """
        The title border panel the whole GUI is set into.
        """

        subroutineFrame = PSE.JAVX_SWING.JPanel()
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Patterns Subroutine'))

        return subroutineFrame
    
    def guiMaker(self):
        """Make the subroutine GUI here."""

        tpPanel = PSE.JAVX_SWING.JPanel() # the Patterns panel
        tpPanel.setLayout(PSE.JAVX_SWING.BoxLayout(tpPanel, PSE.JAVX_SWING.BoxLayout.Y_AXIS))

        rowLabel = PSE.JAVX_SWING.JLabel()
        rowLabel.setName('jTracksPanelLabel')
        # rowLabel.setVisible(False)

        checkBox = PSE.JAVX_SWING.JCheckBox('test')
        checkBox.setName('jTrackCheckBox')
        checkBox.setVisible(False)

        tpPanel.add(self.makeLocaleRow())
        tpPanel.add(self.makeTracksRow())
        tpPanel.add(self.makeButtonsRow())
        tpPanel.add(rowLabel)
        tpPanel.add(checkBox)

        guiFrame = self.getGuiFrame()
        guiFrame.add(tpPanel)
        
        return guiFrame

    def makeLocaleRow(self):
        """
        Make widget row containing: 'Division:', combo box, 'Loaction:', combo box, 'Yard Tracks Only', check box.
        Since the Locations combo box needs to be custom, it became moot to use DM.getComboBox().
        """

        localeRow = PSE.JAVX_SWING.JPanel()
        localeRow.setAlignmentX(PSE.JAVX_SWING.JPanel.CENTER_ALIGNMENT)

        divisionLabel = PSE.JAVX_SWING.JLabel(PSE.getBundleItem('Division:'))
        locationLabel = PSE.JAVX_SWING.JLabel(PSE.getBundleItem('Location:'))

        localeRow.add(divisionLabel)
        localeRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        localeRow.add(self.divisionComboBox)
        localeRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        localeRow.add(locationLabel)
        localeRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        localeRow.add(self.locationComboBox)
        localeRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        localeRow.add(self.yardTracksOnly)

        return localeRow

    def makeTracksRow(self):
        """
        The track row is populated by Model.trackRowManager()
        """

        tracksPanel = PSE.JAVX_SWING.JPanel()
        tracksPanel.setName('jTracksPanel')            

        return tracksPanel
        
    def makeButtonsRow(self):
        """
        Make the row of action buttons: 'Track Pattern', 'Set Rolling Stock.'
        """

        trackButtonsPanel = PSE.JAVX_SWING.JPanel()
        trackButtonsPanel.setAlignmentX(PSE.JAVX_SWING.JPanel.CENTER_ALIGNMENT)
        trackButtonsPanel.add(self.ypButton)
        trackButtonsPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
        trackButtonsPanel.add(self.scButton)

        return trackButtonsPanel

    def guiWidgetGetter(self):

        widgets = []

        widgets.append(self.divisionComboBox)
        widgets.append(self.locationComboBox)
        widgets.append(self.yardTracksOnly)
        widgets.append(self.trackCheckBoxes)
        widgets.append(self.ypButton)
        widgets.append(self.scButton)

        return widgets

def makeSetCarsForTrackForm(setCarsFormData):
    """
    Creates and populates the 'Set Cars Form for Track X' form
    Called by:
    ControllerSetCarsForm.CreateSetCarsForm.makeFrame
    """

    _psLog.debug('makeSetCarsForTrackForm')

    allSetCarsWidgets = {}

    setCarsForm = PSE.JAVX_SWING.JPanel()
    setCarsForm.setLayout(PSE.JAVX_SWING.BoxLayout(setCarsForm, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))

    headerPanel = makeSetCarsFormHeader(setCarsFormData)
    setCarsForm.add(headerPanel)
    
    trackButtonsPanel, buttonList = makeSetCarsTrackButtons()
    allSetCarsWidgets['trackButtons'] = buttonList
    setCarsForm.add(trackButtonsPanel)

    inventoryPanel, textBoxList = makeSetCarsListOfInventory(setCarsFormData)
    allSetCarsWidgets['textBoxEntry'] = textBoxList
    setCarsForm.add(inventoryPanel)
    setCarsForm.add(PSE.JAVX_SWING.JSeparator())

    schedulePanel, scheduleButton = makeSetCarsScheduleRow(setCarsFormData)
    allSetCarsWidgets['scheduleButton'] = None
    if schedulePanel:
        setCarsForm.add(schedulePanel)
        allSetCarsWidgets['scheduleButton'] = scheduleButton

    footerPanel, footerButtons = MakeSetCarsFooter()
    allSetCarsWidgets['footerButtons'] = footerButtons
    setCarsForm.add(footerPanel)

    return setCarsForm, allSetCarsWidgets

def makeSetCarsFormHeader(setCarsFormData):
    """
    Creates the 'Set Cars Form for Track X' forms header
    Called by:
    makeSetCarsForTrackForm
    """

    _psLog.debug('makeSetCarsFormHeader')

    splitName = setCarsFormData['railroad'].split('\n')
    trackName = setCarsFormData['locations'][0]['userName'] # There's only one track
    locationName = PSE.readConfigFile('Patterns')['PL'] # There's only one location
    validDate = PSE.isoValidTime(setCarsFormData['date'])

    headerTrackLabel = PSE.JAVX_SWING.JLabel()
    headerTrackLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
    headerTrackLabel.setText(PSE.getBundleItem('Set Rolling Stock for track: {} at {}').format(trackName, locationName))

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

    # combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,10)))
    combinedHeader.add(headerTrackLabel)
    combinedHeader.add(headerValidLabel)

    return combinedHeader

def makeSetCarsTrackButtons():
    """
    Makes a scrollable row of buttons, one for each track
    Called by:
    makeSetCarsForTrackForm
    """

    buttonList = []
    location =  PSE.readConfigFile('Patterns')['PL']
    allTracksAtLoc =  PSE.LM.getLocationByName(location).getTracksByNameList(None)
    paneHeight = PSE.PM.getFontSize() * 4 + 20

    trackButtonsPanel = PSE.JAVX_SWING.JPanel()
    for track in allTracksAtLoc:
        selectTrackButton = PSE.JAVX_SWING.JButton(track.getName())
        buttonList.append(selectTrackButton)
        trackButtonsPanel.add(selectTrackButton)

    VSN = PSE.JAVX_SWING.ScrollPaneConstants.VERTICAL_SCROLLBAR_NEVER
    HSA = PSE.JAVX_SWING.ScrollPaneConstants.HORIZONTAL_SCROLLBAR_ALWAYS
    trackButtonsPane = PSE.JAVX_SWING.JScrollPane(trackButtonsPanel, VSN, HSA)

    trackButtonsWrapper = PSE.JAVX_SWING.JPanel()
    trackButtonsWrapper.setLayout(PSE.JAVX_SWING.BoxLayout(trackButtonsWrapper, PSE.JAVX_SWING.BoxLayout.Y_AXIS))
    trackButtonsWrapper.setMinimumSize(PSE.JAVA_AWT.Dimension(paneHeight, paneHeight))
    trackButtonsWrapper.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Tracks at {}').format(location))

    trackButtonsWrapper.add(trackButtonsPane)

    return trackButtonsWrapper, buttonList

def makeSetCarsListOfInventory(setCarsFormData):
    """
    Creates the 'Set Cars Form for Track X' forms list of rolling stock
    Called by:
    makeSetCarsForTrackForm
    """

    inventoryFormBody = PSE.JAVX_SWING.JPanel()
    inventoryFormBody.setLayout(PSE.JAVX_SWING.BoxLayout(inventoryFormBody, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))

    setCarsEqptRows = MakeSetCarsEqptRows(setCarsFormData)
    trackName = setCarsFormData['locations'][0]['userName']

    if setCarsFormData['locations'][0]['engines']['add']:
        locoFormBody = PSE.JAVX_SWING.JPanel()
        locoFormBody.setLayout(PSE.JAVX_SWING.BoxLayout(locoFormBody, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        locoFormBody.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Locomotives at {}').format(trackName))

        # setCarsLocoRows = setCarsEqptRows.makeSetCarsLocoRows()
        # for loco in setCarsLocoRows:
        #     locoFormBody.add(loco)
        inventoryFormBody.add(locoFormBody)

    if setCarsFormData['locations'][0]['cars']['add']:
        carFormBody = PSE.JAVX_SWING.JPanel()
        carFormBody.setLayout(PSE.JAVX_SWING.BoxLayout(carFormBody, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        carFormBody.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Cars at {}').format(trackName))

        setCarsCarRows = setCarsEqptRows.makeSetCarsCarRows()
        for car in setCarsCarRows:
            carFormBody.add(car)
        inventoryFormBody.add(carFormBody)

    inventoryPane = PSE.JAVX_SWING.JScrollPane(inventoryFormBody)

    inventoryWrapper = PSE.JAVX_SWING.JPanel()
    inventoryWrapper.setLayout(PSE.JAVX_SWING.BoxLayout(inventoryWrapper, PSE.JAVX_SWING.BoxLayout.Y_AXIS))
    inventoryWrapper.add(inventoryPane)

    textBoxList = setCarsEqptRows.getTextBoxEntryList()
    
    return inventoryWrapper, textBoxList

def makeSetCarsScheduleRow(setCarsFormData):
    """
    Used By:
    makeSetCarsForTrackForm
    """

    _psLog.debug('makeSetCarsScheduleRow')

    trackLocation = PSE.readConfigFile('Patterns')['PL']
    trackName = setCarsFormData['locations'][0]['userName']
    trackObject = PSE.LM.getLocationByName(trackLocation).getTrackByName(trackName, None)
    scheduleObject = trackObject.getSchedule()
    if scheduleObject:
        schedulePanel = PSE.JAVX_SWING.JPanel()
        schedulePanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Schedule for {}').format(trackName))
        scheduleButton = PSE.JAVX_SWING.JButton(scheduleObject.getName())
        schedulePanel.add(PSE.JAVX_SWING.JLabel(PSE.getBundleItem('Schedule:')))
        schedulePanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(5,0)))
        schedulePanel.add(scheduleButton)

        return schedulePanel, scheduleButton
    
    else:
        return None, None

def MakeSetCarsFooter():
    """
    Makes 2 panels, Make Work and Report Work, and adds buttons to the panels
    Used By:
    makeSetCarsForTrackForm
    """

    _psLog.debug('MakeSetCarsFooter')

    makeWorkPanel = PSE.JAVX_SWING.JPanel()
    makeWorkPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Make Work'))
# Switch List button
    slButton = PSE.JAVX_SWING.JButton(PSE.getBundleItem('+ Switch List'))

    makeWorkPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
    makeWorkPanel.add(slButton)
    makeWorkPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))

    reportWorkPanel = PSE.JAVX_SWING.JPanel()
    reportWorkPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Report Work'))
# Set cars button
    scButton = PSE.JAVX_SWING.JButton(PSE.getBundleItem('Set Rolling Stock to Track'))

    reportWorkPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
    reportWorkPanel.add(scButton)
    reportWorkPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))

    combinedFooter = PSE.JAVX_SWING.JPanel()
    combinedFooter.add(makeWorkPanel)
    combinedFooter.add(reportWorkPanel)

    footerButtons = []
    footerButtons.append(slButton)
    footerButtons.append(scButton)

    return combinedFooter, footerButtons

def setCarsForTrackWindow(setCarsForTrackForm):
    """
    Called by:
    ControllerSetCarsForm.CreateSetCarsForm.makeFrame
    """

    setCarsWindow = PSE.JMRI.util.JmriJFrame()
    setCarsWindow.add(setCarsForTrackForm)

    return setCarsWindow


class MakeSetCarsEqptRows():
    """
    Called by:
    makeSetCarsForTrackForm
    """

    def __init__(self, setCarsFormData):

        self.SCRIPT_NAME = 'OperationsPatternScripts.MakeSetCarsEqptRows'

        PSE.makeReportItemWidthMatrix()
        PSE.translateMessageFormat()

        self.reportWidth = PSE.REPORT_ITEM_WIDTH_MATRIX
        fontSize = PSE.PM.getFontSize()
        self.panelHeight = fontSize + 4
        self.panelWidth = fontSize - 2

        self.setCarsFormData = setCarsFormData
        self.textBoxEntry = []

        self.carColor = PSE.getColorA()
        self.locoColor = PSE.getColorB()
        self.alertColor = PSE.getColorC()

        return

    def makeSetCarsLocoRows(self):
        """
        Creates the locomotive lines of the pattern report form
        """

        listOfLocoRows = []
        locos = self.setCarsFormData['locations'][0]['engines']['add']

        for loco in locos:
            locoItems = PSE.translateCarFormat(loco)
            combinedInputLine = PSE.JAVX_SWING.JPanel()
            combinedInputLine.setBackground(self.locoColor)
            if loco['onTrain']:
                combinedInputLine.setBackground(self.alertColor)

            inputText = PSE.JAVX_SWING.JTextField(5)
            self.textBoxEntry.append(inputText)
            inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
            inputBox.add(inputText)
            combinedInputLine.add(inputBox)

            messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
            for messageItem in messageFormat:
                if 'Tab' in item:
                    continue
                labelName = locoItems[PSE.ROSETTA[messageItem]]
                lineWidth = PSE.REPORT_ITEM_WIDTH_MATRIX[messageItem] + 1

                rowItem = labelName.ljust(lineWidth)
                label = PSE.JAVX_SWING.JLabel(rowItem)
                box = makeSwingBox(lineWidth * self.panelWidth, self.panelHeight)
                box.add(label)
                combinedInputLine.add(box)

            combinedInputLine.add(PSE.JAVX_SWING.Box.createHorizontalGlue())
            listOfLocoRows.append(combinedInputLine)

        return listOfLocoRows

    def makeSetCarsCarRows(self):
        """
        Creates the car lines of the Set Cars frame.
        """

        listOfCarRows = []
        cars = self.setCarsFormData['locations'][0]['cars']['add']

        for car in cars:
            carItems = PSE.translateCarFormat(car)
            combinedInputLine = PSE.JAVX_SWING.JPanel()
            combinedInputLine.setBackground(self.carColor)
            if car['onTrain']:
                combinedInputLine.setBackground(self.alertColor)

            inputText = PSE.JAVX_SWING.JTextField(5)
            self.textBoxEntry.append(inputText)
            inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
            inputBox.add(inputText)
            combinedInputLine.add(inputBox)

            messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()
            for messageItem in messageFormat:
                if 'Tab' in messageItem:
                    continue
                labelName = carItems[PSE.ROSETTA[messageItem]]
                lineWidth = PSE.REPORT_ITEM_WIDTH_MATRIX[messageItem] + 1

            # Special case handling for car load type
                if PSE.ROSETTA[messageItem] == 'Load_Type':
                    labelName = PSE.getShortLoadType(car).ljust(1)
                    lineWidth = 2
            # Special case handling for car number
                if PSE.ROSETTA[messageItem] == 'Number':
                    labelName = labelName.rjust(lineWidth)
            # Special case handling for the hazardous flag
                if PSE.ROSETTA[messageItem] == 'Hazardous' and car['hazardous']:
                    labelName = messageItem[0].upper()
                    lineWidth = 2
                elif PSE.ROSETTA[messageItem] == 'Hazardous' and not car['hazardous']:
                    labelName = ' '
                    lineWidth = 2

                rowItem = labelName.ljust(lineWidth)
                label = PSE.JAVX_SWING.JLabel(rowItem)
                box = makeSwingBox(lineWidth * self.panelWidth, self.panelHeight)
                box.add(label)
                combinedInputLine.add(box)

            combinedInputLine.add(PSE.JAVX_SWING.Box.createHorizontalGlue())
            listOfCarRows.append(combinedInputLine)

        return listOfCarRows

    def getTextBoxEntryList(self):

        return self.textBoxEntry


def setCarsPopup():
    """
    When the Set Rollingstock For Track: Window/Set Rollingstock to Track button is pressed
    this popup is displayed to select apply schedule and ignore track length on a per track basis.
    """

    configFile = PSE.readConfigFile('Patterns')
    widgets = []

    popupFrame = PSE.JMRI.util.JmriJFrame()
    popupFrame.setName('popupFrame')
    popupFrame.setTitle(PSE.getBundleItem('Additional Choices'))
    
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
    applySchedule.setText(PSE.getBundleItem('Apply the destination tracks schedule'))
    applySchedule.setSelected(configFile['AS'])
    applySchedule.setName('asCheckBox')
    widgets.append(applySchedule)
    
    ignoreTrackLength = PSE.JAVX_SWING.JCheckBox()
    ignoreTrackLength.setText(PSE.getBundleItem('Ignore track length'))
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
    setCarsButton.setText(PSE.getBundleItem('Set Cars'))
    setCarsButton.setName('setCarsButton')
    widgets.append(setCarsButton)

    cancelButton = PSE.JAVX_SWING.JButton()
    cancelButton.setText(PSE.getBundleItem('Cancel'))
    cancelButton.setName('cancelButton')
    widgets.append(cancelButton)

    buttonRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
    buttonRow.add(setCarsButton)
    buttonRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
    buttonRow.add(cancelButton)
    buttonRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
# Build the panel
    # popupPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,20)))
    popupPanel.add(checkBoxPanel)
    # popupPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,20)))
    popupPanel.add(PSE.JAVX_SWING.JSeparator())
    # popupPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,20)))
    popupPanel.add(buttonRow)
    # popupPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,20)))

    popupFrame.add(popupPanel)
    popupFrame.pack()

    return popupFrame, widgets

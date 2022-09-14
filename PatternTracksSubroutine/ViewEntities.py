# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewEntities'
SCRIPT_REV = 20220101

class TrackPatternPanel:
    """Makes the pattern tracks subroutine panel
        Used by:
        View.ManageGui.makeSubroutinePanel"""

    def __init__(self):

        self.configFile = PatternScriptEntities.readConfigFile('PT')
        self.yardTracksOnly = PatternScriptEntities.JAVX_SWING.JCheckBox()
        self.yardTracksOnly.setText(PatternScriptEntities.BUNDLE['Yard tracks only'] + ' ')
        self.yardTracksOnly.setSelected(self.configFile['PA'])
        self.yardTracksOnly.setName('ytoCheckBox')

        self.ignoreTrackLength = PatternScriptEntities.JAVX_SWING.JCheckBox()
        self.ignoreTrackLength.setText(PatternScriptEntities.BUNDLE['Ignore track length'] + ' ')
        self.ignoreTrackLength.setSelected(self.configFile['PI'])
        self.ignoreTrackLength.setName('itlCheckBox')

        self.ypButton = PatternScriptEntities.JAVX_SWING.JButton()
        self.ypButton.setText(PatternScriptEntities.BUNDLE['Track Pattern Report'])
        self.ypButton.setName('ypButton')

        self.scButton = PatternScriptEntities.JAVX_SWING.JButton()
        self.scButton.setText(PatternScriptEntities.BUNDLE['Set Rolling Stock to Track'])
        self.scButton.setName('scButton')

        self.trackCheckBoxes = []
        self.controlObjects = []

        return

    def makeLocationComboBox(self):
        """Make the combo box of user selectable locations"""

        patternLabel = PatternScriptEntities.JAVX_SWING.JLabel(PatternScriptEntities.BUNDLE['Location:'])
        locationList = self.configFile['AL']
        self.locationComboBox = PatternScriptEntities.JAVX_SWING.JComboBox(locationList)
        self.locationComboBox.setName('locationComboBox')
        self.locationComboBox.setSelectedItem(self.configFile['PL'])
        patternComboBox = PatternScriptEntities.JAVX_SWING.Box(PatternScriptEntities.JAVX_SWING.BoxLayout.X_AXIS)
        patternComboBox.add(patternLabel)
        patternComboBox.add(PatternScriptEntities.JAVX_SWING.Box.createRigidArea(PatternScriptEntities.JAVA_AWT.Dimension(8,0)))
        patternComboBox.add(self.locationComboBox)

        return patternComboBox

    def makeLocationCheckBoxes(self):
        """Any track type and ignore length flags"""

        flagInputBox = PatternScriptEntities.JAVX_SWING.Box(PatternScriptEntities.JAVX_SWING.BoxLayout.X_AXIS) # make a box for the label and input box
        flagInputBox.add(self.yardTracksOnly)
        flagInputBox.add(self.ignoreTrackLength)

        return flagInputBox

    def makeTrackCheckBoxes(self):
        """Make a panel of check boxes, one for each track"""

        rowLabel = PatternScriptEntities.JAVX_SWING.JLabel()
        tracksPanel = PatternScriptEntities.JAVX_SWING.JPanel()
        tracksPanel.setAlignmentX(PatternScriptEntities.JAVX_SWING.JPanel.CENTER_ALIGNMENT)
        tracksPanel.add(rowLabel)
        trackDict = self.configFile['PT'] # pattern tracks
        if (trackDict):
            rowLabel.text = PatternScriptEntities.BUNDLE['Track List:'] + ' '
            for track, flag in sorted(trackDict.items()):
                trackCheckBox = tracksPanel.add(PatternScriptEntities.JAVX_SWING.JCheckBox(track, flag))
                self.trackCheckBoxes.append(trackCheckBox)
            self.ypButton.setEnabled(True)
            self.scButton.setEnabled(True)
        else:
            self.ypButton.setEnabled(False)
            self.scButton.setEnabled(False)
            rowLabel.text = PatternScriptEntities.BUNDLE['There are no yard tracks for this location']

        return tracksPanel

    def makeButtonPanel(self):
        """Button panel added to makeTrackPatternPanel"""

        buttonPanel = PatternScriptEntities.JAVX_SWING.JPanel()
        buttonPanel.setAlignmentX(PatternScriptEntities.JAVX_SWING.JPanel.CENTER_ALIGNMENT)
        buttonPanel.add(self.ypButton)
        buttonPanel.add(self.scButton)

        return buttonPanel

    def getPanelWidgets(self):
        """A list of the widgets created by this class"""

        self.controlObjects.append(self.locationComboBox)
        self.controlObjects.append(self.yardTracksOnly)
        self.controlObjects.append(self.ignoreTrackLength)
        self.controlObjects.append(self.trackCheckBoxes)
        self.controlObjects.append(self.ypButton)
        self.controlObjects.append(self.scButton)

        return self.controlObjects

    def makeTrackPatternPanel(self):
        """Make the pattern tracks panel object"""

        tpPanel = PatternScriptEntities.JAVX_SWING.JPanel() # the pattern tracks panel
        tpPanel.setLayout(PatternScriptEntities.JAVX_SWING.BoxLayout(tpPanel, PatternScriptEntities.JAVX_SWING.BoxLayout.Y_AXIS))
        inputRow = PatternScriptEntities.JAVX_SWING.JPanel()
        inputRow.setLayout(PatternScriptEntities.JAVX_SWING.BoxLayout(inputRow, PatternScriptEntities.JAVX_SWING.BoxLayout.X_AXIS))
        inputRow.add(PatternScriptEntities.JAVX_SWING.Box.createRigidArea(PatternScriptEntities.JAVA_AWT.Dimension(12,0)))
        inputRow.add(self.makeLocationComboBox())
        inputRow.add(PatternScriptEntities.JAVX_SWING.Box.createRigidArea(PatternScriptEntities.JAVA_AWT.Dimension(8,0)))
        inputRow.add(self.makeLocationCheckBoxes())
        trackCheckBoxes = self.makeTrackCheckBoxes()
        buttonPanel = self.makeButtonPanel()
        tpPanel.add(inputRow)
        tpPanel.add(trackCheckBoxes)
        tpPanel.add(buttonPanel)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return tpPanel

def modifyTrackPattern(trackPattern):
    """Make adjustments to the way the reports display here.
        Replaces blank Dest and FD with standins.
        Replaces load type with short load type.
        Used by:
        View.trackPatternButton
        View.setRsButton
        ViewSetCarsForm.switchListButton
        """

    standins = PatternScriptEntities.readConfigFile('RM')

    tracks = trackPattern['locations'][0]['tracks']
    for track in tracks:
        for loco in track['locos']:
            destStandin, fdStandin = getStandins(loco, standins)
            loco.update({'Destination': destStandin})

        for car in track['cars']:
            destStandin, fdStandin = getStandins(car, standins)
            car.update({'Destination': destStandin})
            car.update({'Final Dest': fdStandin})
            shortLoadType = PatternScriptEntities.getShortLoadType(car)
            car.update({'Load Type': shortLoadType})

    return trackPattern

def makeTextReportHeader(textWorkEventList):
    """Makes the header for generic text reports
        Used by:
        View.ManageGui.trackPatternButton'
        ViewSetCarsForm.switchListButton
        """

    headerNames = PatternScriptEntities.readConfigFile('PT')

    textReportHeader    = textWorkEventList['railroad'] + '\n' \
                        + textWorkEventList['trainName'] + '\n' \
                        + textWorkEventList['trainDescription'] + '\n' \
                        + textWorkEventList['date'] + '\n\n' \
                        + PatternScriptEntities.BUNDLE['Work Location:'] + ' ' + headerNames['PL'] + '\n\n'

    return textReportHeader

def makeTextReportLocations(textWorkEventList, trackTotals):
    """Makes the body for generic text reports
        Used by:
        View.ManageGui.trackPatternButton'
        ViewSetCarsForm.switchListButton
        """

    locoItems = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    carItems = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    reportSwitchList = ''
    reportTally = [] # running total for all tracks
    for track in textWorkEventList['locations'][0]['tracks']:
        lengthOfLocos = 0
        lengthOfCars = 0
        trackTally = []
        trackName = track['trackName']
        trackLength = track['length']
        reportSwitchList += PatternScriptEntities.BUNDLE['Track:'] + ' ' + trackName + '\n'
        switchListRow = ''

        for loco in track['locos']:
            lengthOfLocos += int(loco['Length']) + 4
            reportSwitchList += loco['Set_To'] + loopThroughRs('loco', loco) + '\n'

        for car in track['cars']:
            lengthOfCars += int(car['Length']) + 4
            reportSwitchList += car['Set_To'] + loopThroughRs('car', car) + '\n'
            trackTally.append(car['Final Dest'])
            reportTally.append(car['Final Dest'])

        if trackTotals:
            totalLength = lengthOfLocos + lengthOfCars
            reportSwitchList += PatternScriptEntities.BUNDLE['Total Cars:'] + ' ' \
                + str(len(track['cars'])) + ' ' + PatternScriptEntities.BUNDLE['Track Length:']  + ' ' \
                + str(trackLength) +  ' ' + PatternScriptEntities.BUNDLE['Eqpt. Length:']  + ' ' \
                + str(totalLength) + ' ' +  PatternScriptEntities.BUNDLE['Available:']  + ' '  \
                + str(trackLength - totalLength) \
                + '\n\n'
            reportSwitchList += PatternScriptEntities.BUNDLE['Track Totals for Cars:'] + '\n'
            for track, count in sorted(PatternScriptEntities.occuranceTally(trackTally).items()):
                reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
        reportSwitchList += '\n'

    if trackTotals:
        reportSwitchList += '\n' + PatternScriptEntities.BUNDLE['Report Totals for Cars:'] + '\n'
        for track, count in sorted(PatternScriptEntities.occuranceTally(reportTally).items()):
            reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'

    return reportSwitchList

def makeUserInputList(textBoxEntry):
    """Used by:
        ViewSetCarsForm.switchListButton
        """

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), PatternScriptEntities.ENCODING))

    return userInputList

def merge(switchList, userInputList):
    """Merge the values in textBoxEntry into the ['Set_To'] field of switchList.
        Used by:
        ViewSetCarsForm.switchListButton
        """

    longestTrackString = findLongestTrackString()
    allTracksAtLoc = PatternScriptEntities.getTracksByLocation(None)

    i = 0
    locos = switchList['locations'][0]['tracks'][0]['locos']
    for loco in locos:
        setTrack = switchList['locations'][0]['tracks'][0]['trackName']
        setTrack = PatternScriptEntities.formatText('[' + setTrack + ']', longestTrackString + 2)
        loco.update({'Set_To': setTrack})

        userInput = unicode(userInputList[i], PatternScriptEntities.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PatternScriptEntities.formatText('[' + userInput + ']', longestTrackString + 2)
            loco.update({'Set_To': setTrack})
        i += 1

    cars = switchList['locations'][0]['tracks'][0]['cars']
    for car in cars:
        setTrack = switchList['locations'][0]['tracks'][0]['trackName']
        setTrack = PatternScriptEntities.formatText('[' + setTrack + ']', longestTrackString + 2)
        car.update({'Set_To': setTrack})

        userInput = unicode(userInputList[i], PatternScriptEntities.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PatternScriptEntities.formatText('[' + userInput + ']', longestTrackString + 2)
            car.update({'Set_To': setTrack})

        i += 1

    return switchList

def findLongestTrackString():
    """Used by:
        merge
        """

    longestTrackString = 6 # 6 is the length of [Hold]
    for track in PatternScriptEntities.readConfigFile('PT')['PT']: # Pattern Tracks
        if len(track) > longestTrackString:
            longestTrackString = len(track)

    return longestTrackString

def loopThroughRs(type, rsAttribs):
    """Creates a line containing the attrs in get * MessageFormat
        Used by:
        makeTextReportLocations
        """

    reportWidth = PatternScriptEntities.REPORT_ITEM_WIDTH_MATRIX
    switchListRow = ''
    rosetta = PatternScriptEntities.translateMessageFormat()

    if type == 'loco':
        messageFormat = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    if type == 'car':
        messageFormat = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    for lookup in messageFormat:
        item = rosetta[lookup]

        if 'Tab' in item:
            continue

        itemWidth = reportWidth[item]
        switchListRow += PatternScriptEntities.formatText(rsAttribs[item], itemWidth)

    return switchListRow

def getStandins(car, standins):
    """Replaces null destination and fd with the standin from the config file
        Used by:
        ModelSetCarsForm.merge
        """

    destStandin = car['Destination']
    if not car['Destination']:
        destStandin = standins['DS']

    try: # No FD for locos
        fdStandin = car['Final Dest']
        if not car['Final Dest']:
            fdStandin = standins['FD']
    except:
        fdStandin = ''

    return destStandin, fdStandin

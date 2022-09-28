# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewEntities'
SCRIPT_REV = 20220101

class TrackPatternPanel:
    """Makes the pattern tracks subroutine panel
        Used by:
        View.ManageGui.makeSubroutinePanel"""

    def __init__(self):

        self.configFile = PSE.readConfigFile('PT')

        self.yardTracksOnly = PSE.JAVX_SWING.JCheckBox()
        self.yardTracksOnly.setText(PSE.BUNDLE['Yard tracks only'] + ' ')
        self.yardTracksOnly.setSelected(self.configFile['PA'])
        self.yardTracksOnly.setName('ytoCheckBox')

        self.ignoreTrackLength = PSE.JAVX_SWING.JCheckBox()
        self.ignoreTrackLength.setText(PSE.BUNDLE['Ignore track length'] + ' ')
        self.ignoreTrackLength.setSelected(self.configFile['PI'])
        self.ignoreTrackLength.setName('itlCheckBox')

        self.ypButton = PSE.JAVX_SWING.JButton()
        self.ypButton.setText(PSE.BUNDLE['Track Pattern Report'])
        self.ypButton.setName('ypButton')

        self.scButton = PSE.JAVX_SWING.JButton()
        self.scButton.setText(PSE.BUNDLE['Set Rolling Stock to Track'])
        self.scButton.setName('scButton')

        self.trackCheckBoxes = []

        return

    def makeLocationRow(self):
        """Make widget row containing: 'Loaction:', combo box, 'Yard Tracks Only', 'Ignore Track Length'.
            PSE.LM.getComboBox() includes box.addItem(null); which is unwanted
            """

        patternLabel = PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Location:'])
        locationList = self.configFile['AL']

        self.locationComboBox = PSE.JAVX_SWING.JComboBox(locationList)
        self.locationComboBox.setName('locationComboBox')
        self.locationComboBox.setSelectedItem(self.configFile['PL'])

        patternComboBox = PSE.JAVX_SWING.JPanel()
        patternComboBox.setAlignmentX(PSE.JAVX_SWING.JPanel.CENTER_ALIGNMENT)

        patternComboBox.add(patternLabel)
        patternComboBox.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        patternComboBox.add(self.locationComboBox)
        patternComboBox.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        patternComboBox.add(self.yardTracksOnly)
        patternComboBox.add(self.ignoreTrackLength)

        return patternComboBox

    def makeTracksRow(self):
        """Make the row of check boxes, one for each track"""

        tracksPanel = PSE.JAVX_SWING.JPanel()
        tracksPanel.setAlignmentX(PSE.JAVX_SWING.JPanel.CENTER_ALIGNMENT)

        rowLabel = PSE.JAVX_SWING.JLabel()
        tracksPanel.add(rowLabel)
        trackDict = self.configFile['PT'] # pattern tracks
        if trackDict:
            rowLabel.text = PSE.BUNDLE['Track List:'] + ' '
            for track, flag in sorted(trackDict.items()):
                trackCheckBox = tracksPanel.add(PSE.JAVX_SWING.JCheckBox(track, flag))
                self.trackCheckBoxes.append(trackCheckBox)
            self.ypButton.setEnabled(True)
            self.scButton.setEnabled(True)
        else:
            self.ypButton.setEnabled(False)
            self.scButton.setEnabled(False)
            rowLabel.text = PSE.BUNDLE['There are no yard tracks for this location']

        return tracksPanel

    def makeButtonsRow(self):
        """Make the row of action buttons: 'Track Pattern', 'Set Rolling Stock.' """

        buttonPanel = PSE.JAVX_SWING.JPanel()
        buttonPanel.setAlignmentX(PSE.JAVX_SWING.JPanel.CENTER_ALIGNMENT)
        buttonPanel.add(self.ypButton)
        buttonPanel.add(self.scButton)

        return buttonPanel

    def getPanelWidgets(self):
        """A list of the widgets created by this class"""

        panelWidgets = []
        panelWidgets.append(self.locationComboBox)
        panelWidgets.append(self.yardTracksOnly)
        panelWidgets.append(self.ignoreTrackLength)
        panelWidgets.append(self.trackCheckBoxes)
        panelWidgets.append(self.ypButton)
        panelWidgets.append(self.scButton)

        return panelWidgets

    def makeTrackPatternPanel(self):
        """Make the pattern tracks panel object"""

        tpPanel = PSE.JAVX_SWING.JPanel() # the pattern tracks panel
        tpPanel.setLayout(PSE.JAVX_SWING.BoxLayout(tpPanel, PSE.JAVX_SWING.BoxLayout.Y_AXIS))

        tpPanel.add(self.makeLocationRow())
        tpPanel.add(self.makeTracksRow())
        tpPanel.add(self.makeButtonsRow())

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return tpPanel

def modifyTrackPatternReport(trackPattern):
    """Make adjustments to the way the reports display here.
        The undeflying json is not changed.
        Replaces blank Dest and FD with standins.
        Replaces load type with short load type.
        Used by:
        View.trackPatternButton
        View.setRsButton
        ViewSetCarsForm.switchListButton
        """

    standins = PSE.readConfigFile('RM')

    tracks = trackPattern['locations'][0]['tracks']
    for track in tracks:
        for loco in track['locos']:
            destStandin, fdStandin = getStandins(loco, standins)
            loco.update({'Destination': destStandin})

        for car in track['cars']:
            destStandin, fdStandin = getStandins(car, standins)
            car.update({'Destination': destStandin})
            car.update({'Final Dest': fdStandin})
            shortLoadType = PSE.getShortLoadType(car)
            car.update({'Load Type': shortLoadType})

    return trackPattern

def getStandins(car, standins):
    """Replaces null destination and fd with the standin from the config file
        Used by:
        modifyTrackPatternReport
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

def makeTextReportHeader(textWorkEventList):
    """Makes the header for generic text reports
        Used by:
        View.ManageGui.trackPatternButton'
        ViewSetCarsForm.switchListButton
        """

    headerNames = PSE.readConfigFile('PT')

    textReportHeader    = textWorkEventList['railroad'] + '\n' \
                        + textWorkEventList['trainName'] + '\n' \
                        + textWorkEventList['trainDescription'] + '\n' \
                        + textWorkEventList['date'] + '\n\n' \
                        + PSE.BUNDLE['Work Location:'] + ' ' + headerNames['PL'] + '\n\n'

    return textReportHeader

def makeTextReportLocations(textWorkEventList, trackTotals):
    """Makes the body for generic text reports
        Used by:
        View.ManageGui.trackPatternButton'
        ViewSetCarsForm.switchListButton
        """

    locoItems = PSE.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    carItems = PSE.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    reportSwitchList = ''
    reportTally = [] # running total for all tracks
    for track in textWorkEventList['locations'][0]['tracks']:
        lengthOfLocos = 0
        lengthOfCars = 0
        trackTally = []
        trackName = track['trackName']
        trackLength = track['length']
        reportSwitchList += PSE.BUNDLE['Track:'] + ' ' + trackName + '\n'
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
            reportSwitchList += PSE.BUNDLE['Total Cars:'] + ' ' \
                + str(len(track['cars'])) + ' ' + PSE.BUNDLE['Track Length:']  + ' ' \
                + str(trackLength) +  ' ' + PSE.BUNDLE['Eqpt. Length:']  + ' ' \
                + str(totalLength) + ' ' +  PSE.BUNDLE['Available:']  + ' '  \
                + str(trackLength - totalLength) \
                + '\n\n'
            reportSwitchList += PSE.BUNDLE['Track Totals for Cars:'] + '\n'
            for track, count in sorted(PSE.occuranceTally(trackTally).items()):
                reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
        reportSwitchList += '\n'

    if trackTotals:
        reportSwitchList += '\n' + PSE.BUNDLE['Report Totals for Cars:'] + '\n'
        for track, count in sorted(PSE.occuranceTally(reportTally).items()):
            reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'

    return reportSwitchList

def makeUserInputList(textBoxEntry):
    """Used by:
        ViewSetCarsForm.switchListButton
        """

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), PSE.ENCODING))

    return userInputList

def merge(switchList, userInputList):
    """Merge the values in textBoxEntry into the ['Set_To'] field of switchList.
        Used by:
        ViewSetCarsForm.switchListButton
        """

    longestTrackString = findLongestTrackString()
    allTracksAtLoc = PSE.getTracksNamesByLocation(None)

    i = 0
    locos = switchList['locations'][0]['tracks'][0]['locos']
    for loco in locos:
        setTrack = switchList['locations'][0]['tracks'][0]['trackName']
        setTrack = PSE.formatText('[' + setTrack + ']', longestTrackString + 2)
        loco.update({'Set_To': setTrack})

        userInput = unicode(userInputList[i], PSE.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PSE.formatText('[' + userInput + ']', longestTrackString + 2)
            loco.update({'Set_To': setTrack})
        i += 1

    cars = switchList['locations'][0]['tracks'][0]['cars']
    for car in cars:
        setTrack = switchList['locations'][0]['tracks'][0]['trackName']
        setTrack = PSE.formatText('[' + setTrack + ']', longestTrackString + 2)
        car.update({'Set_To': setTrack})

        userInput = unicode(userInputList[i], PSE.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PSE.formatText('[' + userInput + ']', longestTrackString + 2)
            car.update({'Set_To': setTrack})

        i += 1

    return switchList

def findLongestTrackString():
    """Used by:
        merge
        """

    longestTrackString = 6 # 6 is the length of [Hold]
    for track in PSE.readConfigFile('PT')['PT']: # Pattern Tracks
        if len(track) > longestTrackString:
            longestTrackString = len(track)

    return longestTrackString

def loopThroughRs(type, rsAttribs):
    """Creates a line containing the attrs in get * MessageFormat
        Used by:
        makeTextReportLocations
        """

    reportWidth = PSE.REPORT_ITEM_WIDTH_MATRIX
    switchListRow = ''
    rosetta = PSE.translateMessageFormat()

    if type == 'loco':
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    if type == 'car':
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    for lookup in messageFormat:
        item = rosetta[lookup]

        if 'Tab' in item:
            continue

        itemWidth = reportWidth[item]
        switchListRow += PSE.formatText(rsAttribs[item], itemWidth)

    return switchListRow

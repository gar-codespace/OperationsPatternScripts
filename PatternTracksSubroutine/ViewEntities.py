# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewEntities'
SCRIPT_REV = 20220101

class TrackPatternPanel:
    """Makes the pattern tracks subroutine panel"""

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
        self.scButton.setText(PatternScriptEntities.BUNDLE['Set Cars to Track'])
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

# def makeTextListForPrint(textWorkEventList, trackTotals=False):
#
#     reportHeader = makeTextReportHeader(textWorkEventList)
#     reportLocations = makeTextReportLocations(textWorkEventList, trackTotals)
#
#     return reportHeader + reportLocations

# def makeTextReportHeader(textWorkEventList):
#
#     headerNames = PatternScriptEntities.readConfigFile('PT')
#
#     textReportHeader    = textWorkEventList['railroad'] + '\n' \
#                         + textWorkEventList['trainName'] + '\n' \
#                         + textWorkEventList['date'] + '\n\n' \
#                         + PatternScriptEntities.BUNDLE['Work Location:'] + ' ' + headerNames['PL'] + '\n\n'
#
#     return textReportHeader

# def makeTextReportLocations(textWorkEventList, trackTotals):
#
#     reportWidth = PatternScriptEntities.REPORT_ITEM_WIDTH_MATRIX
#     locoItems = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
#     carItems = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()
#
#     reportSwitchList = ''
#     reportTally = [] # running total for all tracks
#     for track in textWorkEventList['locations'][0]['tracks']:
#         lengthOfLocos = 0
#         lengthOfCars = 0
#         trackTally = []
#         trackName = track['trackName']
#         trackLength = track['length']
#         reportSwitchList += PatternScriptEntities.BUNDLE['Track:'] + ' ' + trackName + '\n'
#         switchListRow = ''
#
#         for loco in track['locos']:
#             # lengthOfLocos += int(loco[PatternScriptEntities.SB.handleGetMessage('Length')]) + 4
#             # reportSwitchList += loco[PatternScriptEntities.BUNDLE['Set to']] + loopThroughRs('loco', loco) + '\n'
#             lengthOfLocos += int(loco['Length']) + 4
#             reportSwitchList += loco['Set to'] + loopThroughRs('loco', loco) + '\n'
#
#         for car in track['cars']:
#             lengthOfCars += int(car['Length']) + 4
#             reportSwitchList += car['Set to'] + loopThroughRs('car', car) + '\n'
#             trackTally.append(car['Final Dest'])
#             reportTally.append(car['Final Dest'])
#
#
#             # lengthOfCars += int(car[PatternScriptEntities.SB.handleGetMessage('Length')]) + 4
#             # reportSwitchList += car[PatternScriptEntities.BUNDLE['Set to']] + loopThroughRs('car', car) + '\n'
#             # trackTally.append(car[PatternScriptEntities.SB.handleGetMessage('Final_Dest')])
#             # reportTally.append(car[PatternScriptEntities.SB.handleGetMessage('Final_Dest')])
#
#         if trackTotals:
#             totalLength = lengthOfLocos + lengthOfCars
#             reportSwitchList += PatternScriptEntities.BUNDLE['Total Cars:'] + ' ' \
#                 + str(len(track['cars'])) + ' ' + PatternScriptEntities.BUNDLE['Track Length:']  + ' ' \
#                 + str(trackLength) +  ' ' + PatternScriptEntities.BUNDLE['Eqpt. Length:']  + ' ' \
#                 + str(totalLength) + ' ' +  PatternScriptEntities.BUNDLE['Available:']  + ' '  \
#                 + str(trackLength - totalLength) \
#                 + '\n\n'
#             reportSwitchList += PatternScriptEntities.BUNDLE['Track Totals for Cars:'] + '\n'
#             for track, count in sorted(PatternScriptEntities.occuranceTally(trackTally).items()):
#                 reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
#         reportSwitchList += '\n'
#
#     if trackTotals:
#         reportSwitchList += '\n' + PatternScriptEntities.BUNDLE['Report Totals for Cars:'] + '\n'
#         for track, count in sorted(PatternScriptEntities.occuranceTally(reportTally).items()):
#             reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
#
#     return reportSwitchList
#
# def loopThroughRs(type, rsAttribs):
#
#     reportWidth = PatternScriptEntities.REPORT_ITEM_WIDTH_MATRIX
#     switchListRow = ''
#     rosetta = translateMessageFormat()
#
#     if type == 'loco':
#         messageFormat = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
#     if type == 'car':
#         messageFormat = PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()
#
#     for lookup in messageFormat:
#         item = rosetta[lookup]
#
#         if 'Tab' in item:
#             continue
#
#         itemWidth = reportWidth[item]
#         switchListRow += PatternScriptEntities.formatText(rsAttribs[item], itemWidth)
#
#     return switchListRow

# def translateMessageFormat():
#     """The messageFormat is in the locale's language, it has to be hashed to the plugin fields."""
#
#     rosetta = {}
# #Common
#     rosetta[PatternScriptEntities.J_BUNDLE.ROAD] = 'Road'
#     rosetta[PatternScriptEntities.J_BUNDLE.NUMBER] = 'Number'
#     rosetta[PatternScriptEntities.J_BUNDLE.TYPE] = 'Type'
#     rosetta[PatternScriptEntities.J_BUNDLE.LENGTH] = 'Length'
#     rosetta[PatternScriptEntities.J_BUNDLE.WEIGHT] = 'Weight'
#     rosetta[PatternScriptEntities.J_BUNDLE.COLOR] = 'Color'
#     rosetta[PatternScriptEntities.J_BUNDLE.OWNER] = 'Owner'
#     rosetta[PatternScriptEntities.J_BUNDLE.TRACK] = 'Track'
#     rosetta[PatternScriptEntities.J_BUNDLE.LOCATION] = 'Location'
#     rosetta[PatternScriptEntities.J_BUNDLE.COMMENT] = 'Comment'
#     rosetta[PatternScriptEntities.J_BUNDLE.DESTINATION] = 'Destination'
#     rosetta[PatternScriptEntities.J_BUNDLE.DEST_TRACK] = 'Dest&Track'
#     rosetta[PatternScriptEntities.J_BUNDLE.TAB] = 'Tab'
#     rosetta[PatternScriptEntities.J_BUNDLE.TAB2] = 'Tab2'
#     rosetta[PatternScriptEntities.J_BUNDLE.TAB3] = 'Tab3'
# # Cars
#     rosetta[PatternScriptEntities.J_BUNDLE.LOAD] = 'Load'
#     rosetta[PatternScriptEntities.J_BUNDLE.LOAD_TYPE] = 'Load_Type'
#     rosetta[PatternScriptEntities.J_BUNDLE.HAZARDOUS] = 'Hazardous'
#     rosetta[PatternScriptEntities.J_BUNDLE.KERNEL] = 'Kernel'
#     rosetta[PatternScriptEntities.J_BUNDLE.KERNEL_SIZE] = 'Kernel_Size'
#     rosetta[PatternScriptEntities.J_BUNDLE.FINAL_DEST] = 'Final_Dest'
#     rosetta[PatternScriptEntities.J_BUNDLE.FINAL_DEST_TRACK] = 'FD&Track'
#     rosetta[PatternScriptEntities.J_BUNDLE.DROP_COMMENT] = 'SetOut_Msg'
#     rosetta[PatternScriptEntities.J_BUNDLE.PICKUP_COMMENT] = 'PickUp_Msg'
#     rosetta[PatternScriptEntities.J_BUNDLE.RWE] = 'RWE'
#     # rosetta[PatternScriptEntities.J_BUNDLE.RWL] = 'RWL'
# # Locos
#     rosetta[PatternScriptEntities.J_BUNDLE.MODEL] = 'Model'
#     rosetta[PatternScriptEntities.J_BUNDLE.CONSIST] = 'Consist'
# # Unique to this plugin
#     rosetta['On Train'] = 'On Train'
#     rosetta['Set to'] = 'Set to'
#     rosetta['PUSO'] = 'PUSO'
#     rosetta[' '] = ' '
#
#     return rosetta

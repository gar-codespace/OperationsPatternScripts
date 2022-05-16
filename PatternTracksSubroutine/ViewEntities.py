# coding=utf-8
# © 2021, 2022 Greg Ritacco

'''Creates the pattern tracks and its panel'''

import jmri
import java.awt
import javax.swing

from psEntities import PatternScriptEntities
from psBundle import Bundle

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewEntities'
SCRIPT_REV = 20220101

bundle = Bundle.getBundleForLocale(PatternScriptEntities.SCRIPT_ROOT)

class TrackPatternPanel:
    '''Makes the pattern tracks subroutine panel'''

    def __init__(self):

        # self.bundle = Bundle.getBundleForLocale(PatternScriptEntities.SCRIPT_ROOT)

        self.configFile = PatternScriptEntities.readConfigFile('PT')
        self.yardTracksOnly = javax.swing.JCheckBox() #self.configFile['PA']
        self.yardTracksOnly.setText(PatternScriptEntities.BUNDLE['Yard tracks only '])
        self.yardTracksOnly.setSelected(self.configFile['PA'])
        self.yardTracksOnly.setName('ytoCheckBox')

        self.ignoreTrackLength = javax.swing.JCheckBox() # u'Ignore track length ', self.configFile['PI']
        self.ignoreTrackLength.setText(PatternScriptEntities.BUNDLE['Ignore track length '])
        self.ignoreTrackLength.setSelected(self.configFile['PI'])
        self.ignoreTrackLength.setName('itlCheckBox')

        self.ypButton = javax.swing.JButton()
        self.ypButton.setText(PatternScriptEntities.BUNDLE['Pattern'])
        self.ypButton.setName('ypButton')

        self.scButton = javax.swing.JButton()
        self.scButton.setText(PatternScriptEntities.BUNDLE['Set Cars'])
        self.scButton.setName('scButton')

        self.trackCheckBoxes = []
        self.controlObjects = []

        return

    def makeLocationComboBox(self):
        '''Make the combo box of user selectable locations'''

        patternLabel = javax.swing.JLabel(PatternScriptEntities.BUNDLE['Location:'])
        locationList = self.configFile['AL']
        self.locationComboBox = javax.swing.JComboBox(locationList)
        self.locationComboBox.setName('locationComboBox')
        self.locationComboBox.setSelectedItem(self.configFile['PL'])
        patternComboBox = javax.swing.Box(javax.swing.BoxLayout.X_AXIS)
        patternComboBox.add(patternLabel)
        patternComboBox.add(javax.swing.Box.createRigidArea(java.awt.Dimension(8,0)))
        patternComboBox.add(self.locationComboBox)

        return patternComboBox

    def makeLocationCheckBoxes(self):
        '''Any track type and ignore length flags'''

        flagInputBox = javax.swing.Box(javax.swing.BoxLayout.X_AXIS) # make a box for the label and input box
        # flagInputBox.setPreferredSize(java.awt.Dimension(self.configFile['PW'], self.configFile['PH']))
        flagInputBox.add(self.yardTracksOnly)
        flagInputBox.add(self.ignoreTrackLength)

        return flagInputBox

    def makeTrackCheckBoxes(self):
        '''Make a panel of check boxes, one for each track'''

        rowLabel = javax.swing.JLabel()
        tracksPanel = javax.swing.JPanel()
        tracksPanel.setAlignmentX(javax.swing.JPanel.CENTER_ALIGNMENT)
        tracksPanel.add(rowLabel)
        trackDict = self.configFile['PT'] # pattern tracks
        if (trackDict):
            rowLabel.text = PatternScriptEntities.BUNDLE['Track List: ']
            for track, flag in sorted(trackDict.items()):
                trackCheckBox = tracksPanel.add(javax.swing.JCheckBox(track, flag))
                self.trackCheckBoxes.append(trackCheckBox)
            self.ypButton.setEnabled(True)
            self.scButton.setEnabled(True)
        else:
            self.ypButton.setEnabled(False)
            self.scButton.setEnabled(False)
            rowLabel.text = PatternScriptEntities.BUNDLE['There are no yard tracks for this location']

        return tracksPanel

    def makeButtonPanel(self):
        '''Button panel added to makeTrackPatternPanel'''

        buttonPanel = javax.swing.JPanel()
        buttonPanel.setAlignmentX(javax.swing.JPanel.CENTER_ALIGNMENT)
        buttonPanel.add(self.ypButton)
        buttonPanel.add(self.scButton)
        # buttonPanel.add(self.vlButton)

        return buttonPanel

    def getPanelWidgets(self):
        '''A list of the widgets created by this class'''

        self.controlObjects.append(self.locationComboBox)
        self.controlObjects.append(self.yardTracksOnly)
        self.controlObjects.append(self.ignoreTrackLength)
        self.controlObjects.append(self.trackCheckBoxes)
        self.controlObjects.append(self.ypButton)
        self.controlObjects.append(self.scButton)
        # self.controlObjects.append(self.vlButton)

        return self.controlObjects

    def makeTrackPatternPanel(self):
        '''Make the pattern tracks panel object'''

        tpPanel = javax.swing.JPanel() # the pattern tracks panel
        tpPanel.setLayout(javax.swing.BoxLayout(tpPanel, javax.swing.BoxLayout.Y_AXIS))
        inputRow = javax.swing.JPanel()
        inputRow.setLayout(javax.swing.BoxLayout(inputRow, javax.swing.BoxLayout.X_AXIS))
        inputRow.add(javax.swing.Box.createRigidArea(java.awt.Dimension(12,0)))
        inputRow.add(self.makeLocationComboBox())
        inputRow.add(javax.swing.Box.createRigidArea(java.awt.Dimension(8,0)))
        inputRow.add(self.makeLocationCheckBoxes())
        trackCheckBoxes = self.makeTrackCheckBoxes()
        buttonPanel = self.makeButtonPanel()
        tpPanel.add(inputRow)
        tpPanel.add(trackCheckBoxes)
        tpPanel.add(buttonPanel)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return tpPanel

def makeTextListForPrint(textWorkEventList, trackTotals=False):

    reportHeader = makeTextReportHeader(textWorkEventList)
    reportLocations = makeTextReportLocations(textWorkEventList, trackTotals)

    return reportHeader + reportLocations

def makeTextReportHeader(textWorkEventList):

    textReportHeader    = textWorkEventList['railroad'] + '\n' \
                        + textWorkEventList['trainName'] + '\n' \
                        + textWorkEventList['trainDescription'] + '\n' \
                        + bundle['Comment: '] + textWorkEventList['trainComment'] + '\n' \
                        + bundle['Valid time: '] + textWorkEventList['date'] + '\n\n'

    return textReportHeader

def makeTextReportLocations(textWorkEventList, trackTotals):

    reportWidth = PatternScriptEntities.readConfigFile('PT')['RW']
    locoItems = jmri.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    carItems = jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    reportSwitchList = ''
    reportTally = [] # running total for all tracks
    reportSwitchList += bundle['Location: '] + textWorkEventList['locations'][0]['locationName'] + '\n'
    for track in textWorkEventList['locations'][0]['tracks']:
        lengthOfLocos = 0
        lengthOfCars = 0
        trackTally = []
        trackName = track['trackName']
        trackLength = track['length']
        reportSwitchList += bundle['Track: '] + trackName + '\n'
        switchListRow = ''

        for loco in track['locos']:
            lengthOfLocos += int(loco['Length']) + 4
            reportSwitchList += loco['Set to'] + loopThroughRs('loco', loco) + '\n'

        for car in track['cars']:
            lengthOfCars += int(car['Length']) + 4
            reportSwitchList += car['Set to'] + loopThroughRs('car', car) + '\n'
            trackTally.append(car['Final Dest'])
            reportTally.append(car['Final Dest'])

        if trackTotals:
            totalLength = lengthOfLocos + lengthOfCars
            reportSwitchList += bundle['Total Cars: '] + str(len(track['cars'])) + bundle[' Track Length: '] + str(trackLength) + bundle[' Eqpt. Length: '] + str(totalLength) + bundle[' Available: '] + str(trackLength - totalLength) + '\n\n'
            reportSwitchList += bundle['Track Totals for Cars:'] + '\n'
            for track, count in sorted(PatternScriptEntities.occuranceTally(trackTally).items()):
                reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
        reportSwitchList += '\n'

    if trackTotals:
        reportSwitchList += '\n' + bundle['Report Totals for Cars:'] + '\n'
        for track, count in sorted(PatternScriptEntities.occuranceTally(reportTally).items()):
            reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'

    return reportSwitchList

def loopThroughRs(type, rsAttribs):

    reportWidth = PatternScriptEntities.readConfigFile('PT')['RW']
    switchListRow = ''

    if type == 'loco':
        messageFormat = jmri.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    if type == 'car':
        messageFormat = jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    for item in messageFormat:
        itemWidth = reportWidth[bundle[item]]
        switchListRow += PatternScriptEntities.formatText(rsAttribs[bundle[item]], itemWidth)

    return switchListRow

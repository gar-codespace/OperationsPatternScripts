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

class TrackPatternPanel:
    '''Makes the pattern tracks subroutine panel'''

    def __init__(self):

        self.bundle = Bundle.getBundleForLocale(PatternScriptEntities.SCRIPT_ROOT)

        self.configFile = PatternScriptEntities.readConfigFile('PT')
        self.yardTracksOnly = javax.swing.JCheckBox() #self.configFile['PA']
        self.yardTracksOnly.setText(self.bundle['Yard tracks only '])
        self.yardTracksOnly.setSelected(self.configFile['PA'])
        self.yardTracksOnly.setName('ytoCheckBox')

        self.ignoreTrackLength = javax.swing.JCheckBox() # u'Ignore track length ', self.configFile['PI']
        self.ignoreTrackLength.setText(self.bundle['Ignore track length '])
        self.ignoreTrackLength.setSelected(self.configFile['PI'])
        self.ignoreTrackLength.setName('itlCheckBox')

        self.ypButton = javax.swing.JButton()
        self.ypButton.setText(self.bundle['Pattern'])
        self.ypButton.setName('ypButton')

        self.scButton = javax.swing.JButton()
        self.scButton.setText(self.bundle['Set Cars'])
        self.scButton.setName('scButton')

        self.trackCheckBoxes = []
        self.controlObjects = []

        return

    def makeLocationComboBox(self):
        '''Make the combo box of user selectable locations'''

        patternLabel = javax.swing.JLabel(self.bundle['Location:'])
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
            rowLabel.text = self.bundle['Track List: ']
            for track, flag in sorted(trackDict.items()):
                trackCheckBox = tracksPanel.add(javax.swing.JCheckBox(track, flag))
                self.trackCheckBoxes.append(trackCheckBox)
            self.ypButton.setEnabled(True)
            self.scButton.setEnabled(True)
        else:
            self.ypButton.setEnabled(False)
            self.scButton.setEnabled(False)
            rowLabel.text = self.bundle['There are no yard tracks for this location']

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

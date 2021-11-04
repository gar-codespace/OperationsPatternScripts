


    def whenYPEnterPressed(self, event):
        '''When enter is pressed for Yard Pattern box'''

    # Validate the yard location
        if (self.rowLabel.text == ''):
            self.rowLabel.text = u'Type in a location and press enter'
        useAllFlag = None
        if (self.useYardTracks.selected):
            useAllFlag = 'Yard'
        if (yUtil.checkYard(self.patternInput.text, useAllFlag)):
            self.rowLabel.text = u'Track List: '
            yUtil.updateConfigFile(self.patternInput.text, self.useYardTracks.selected, self.ignoreLength.selected)
            self.removeTrackCheckBoxes()
            self.makeTrackCheckBoxes(yUtil.getTracks(self.patternInput.text, useAllFlag))
        else:
            self.removeTrackCheckBoxes()
            self.rowLabel.text = u'Not a valid Location or location has no yard tracks'
        self.trainsFrame.revalidate()
        return

    def whenYPButtonPressed(self, event):
        '''When the Pattern button is pressed'''

        yUtil.updateConfigFile(self.patternInput.text, self.useYardTracks.selected, self.ignoreLength.selected)
        YP.yardPattern(self.patternInput.text, self.useTheseTracks()).runScript()
        return

    def whenSCButtonPressed(self, event):
        '''When the Set button is pressed'''

        # from utilsV1 import updateConfigFile as yUpdate
        yUtil.updateConfigFile(self.patternInput.text, self.useYardTracks.selected, self.ignoreLength.selected)
        destTrackList = []
        for destTrack in self.trackBoxList:
            destTrackList.append(destTrack.text)
        # pass in the location, valid tracks, selected tracks, ignore length flag
        SC.setCars(self.patternInput.text, self.useTheseTracks()).runScript()
        return

    def whenASButtonPressed(self, event):
        '''When the Schedule button is pressed NOT USED'''

        from utilsV1 import updateConfigFile as yUpdate
        print(yUpdate(self.patternInput.text, self.useYardTracks.selected, self.ignoreLength.selected))
        return

    def useTheseTracks(self):
        '''Reads which of the track check boxes are actually checked off'''

        selectedTracks = []
        for x in self.trackBoxList:
            if x.selected:
                selectedTracks.append(x.text)
        return selectedTracks

    def removeTrackCheckBoxes(self):
        '''Removes the track check box row'''

        for x in self.trackBoxList:
            self.tracksPanel.remove(x)
        self.trackBoxList = []
        self.trainsFrame.revalidate()
        return

    def makeTrackCheckBoxes(self, trackList):
        '''Make a panel of check boxes, one for each track'''

        for track in trackList:
            x = javax.swing.JCheckBox(track, True)
            self.tracksPanel.add(x)
            self.trackBoxList.append(x)
        return self.tracksPanel

    def makeHomeLayout(self):
        '''Create the frame that the whole program goes into'''

    # set vars from config file
        self.configFile = yUtil.readConfigFile()
        self.boxWidth = self.configFile['MW']
        self.boxHeight = self.configFile['MH']
        self.useYardTracks.selected = self.configFile['MA']
        self.ignoreLength.selected = self.configFile['MI']

    # Check Box Row
        checkBoxRow = javax.swing.Box(javax.swing.BoxLayout.X_AXIS)
        # checkBoxRow.setAlignmentX(javax.swing.Box.RIGHT_ALIGNMENT)
        checkBoxRow.setPreferredSize(java.awt.Dimension(self.boxWidth, self.boxHeight))
        checkBoxRow.add(self.useYardTracks) # Add the check box
        checkBoxRow.add(self.ignoreLength) # Add the check box
    # Panel that the data form sits in.
        formPanel = javax.swing.JPanel()
        formPanel.setAlignmentX(javax.swing.JPanel.CENTER_ALIGNMENT)
        formPanel.setAlignmentY(javax.swing.JPanel.TOP_ALIGNMENT)
        formPanelWidth = 3 * self.boxWidth + 20
        formPanel.setPreferredSize(java.awt.Dimension(formPanelWidth, self.boxHeight))
        # formPanel.setMaximumSize(formPanel.getPreferredSize())
        formPanel.add(patternInputBox)
        formPanel.add(checkBoxRow)
    # Panel the locations track check boxes are in
        self.tracksPanel.setAlignmentX(javax.swing.JPanel.CENTER_ALIGNMENT)
        self.tracksPanel.add(self.rowLabel)
        xLoc = unicode(self.configFile['ML'], yUtil.setEncoding())
        xTrackType = None
        if (self.configFile['MA']):
            xTrackType = 'Yard'
        self.trackList = yUtil.getTracks(xLoc, xTrackType)
    # Panel the buttons are added to
        buttonPanel = javax.swing.JPanel()
        buttonPanel.setAlignmentX(javax.swing.JPanel.CENTER_ALIGNMENT)
        buttonPanel.add(self.ypButton)
        buttonPanel.add(self.scButton)
        # buttonPanel.add(self.asButton)
    # YP scripts panel

        self.ypPanel.add(formPanel)
        self.ypPanel.add(self.makeTrackCheckBoxes(self.trackList))
        self.ypPanel.add(buttonPanel)
    # Overall panel for all the future panels
        self.wholePanel.border = javax.swing.BorderFactory.createLineBorder(java.awt.Color.GRAY)
        wholePanelHight = 7 * self.boxHeight
        self.wholePanel.setPreferredSize(java.awt.Dimension(2000, wholePanelHight))
        self.wholePanel.setMaximumSize(self.wholePanel.getPreferredSize())
        return

    def handle(self):
        '''Run the program and wait for a keyboard return or button press'''

    # Define the actions and add the home panel
        self.makeHomeLayout()
        self.patternInput.actionPerformed = self.whenYPEnterPressed
        self.ypButton.actionPerformed = self.whenYPButtonPressed
        self.scButton.actionPerformed = self.whenSCButtonPressed
        self.asButton.actionPerformed = self.whenASButtonPressed
        self.trainsFrame.add(self.wholePanel)
        # self.trainsFrame.initComponents()
        # trainsFrame.pack()
        self.trainsFrame.revalidate()
        print(addTextToMain.scriptRev)
        # print(dir(self.trainsFrame))
        # z = javax.swing.JCheckBox('xyzzy', True)
        # xyz = jmri.jmrit.operations.setup.OptionFrame()
        # xyz.add(z)
        # xyz.revalidate()
        # print(dir(xyz))
        # print(xyz.getListeners())

        return False

validateConfigFile().start()
addTextToMain().start()

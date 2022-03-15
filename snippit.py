def makeSetCarsRsRows(self):

    rowAdjustment, shorterRow = self.makeRsRowAdjustment()
    rowWidth = self.makeRowWidth()

    listOfEqptRows = []
    textBoxEntry = []

    locos = self.setCarsForm['locations'][0]['tracks'][0]['locos']
    for loco in locos:

        newInputLine = makeSwingBox(rowWidth + 200, self.panelHeight + 4)
        # newInputLine.setLayout(javax.swing.BoxLayout(newInputLine, javax.swing.BoxLayout.X_AXIS))
        newInputLine.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
        newInputLine.setBackground(MainScriptEntities.FADED)

        inputText = javax.swing.JTextField(5)
        textBoxEntry.append(inputText)
        inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
        inputBox.add(inputText)
        newInputLine.add(inputBox)

        rowText = ''
        for item in jmri.jmrit.operations.setup.Setup.getDropEngineMessageFormat():
            rowText += self.formatText(loco[item], self.reportWidth[item])
        rowLabel = javax.swing.JLabel()
        rowLabel.text = rowText
        newInputLine.add(rowLabel)
        listOfEqptRows.append(newInputLine)



        # combinedInputLine = javax.swing.JPanel()
        # combinedInputLine.setBackground(MainScriptEntities.FADED)
        # inputText = javax.swing.JTextField(5)
        # textBoxEntry.append(inputText)
        # inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
        # inputBox.add(inputText)
        # combinedInputLine.add(inputBox)
        # for item in jmri.jmrit.operations.setup.Setup.getDropEngineMessageFormat():
        #     label = javax.swing.JLabel(loco[item])
        #     box = makeSwingBox(self.reportWidth[item] * self.panelWidth, self.panelHeight)
        #     box.add(label)
        #     combinedInputLine.add(box)
        # if shorterRow == 'loco':
        #     combinedInputLine.add(makeSwingBox(rowAdjustment, self.panelHeight))
        # listOfEqptRows.append(combinedInputLine)

    cars = self.setCarsForm['locations'][0]['tracks'][0]['cars']
    for car in cars:
        combinedInputLine = javax.swing.JPanel()
        # combinedInputLine.setPreferredSize(java.awt.Dimension(width=rowAdjustment, height=self.panelHeight + 8))
        # combinedInputLine = makeSwingBox(rowAdjustment, self.panelHeight + 1)
        combinedInputLine.setBackground(MainScriptEntities.DUST)
        # combinedInputLine.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
        inputText = javax.swing.JTextField(5)
        textBoxEntry.append(inputText)
        inputBox = makeSwingBox(self.panelWidth * 6, self.panelHeight)
        inputBox.add(inputText)
        combinedInputLine.add(inputBox)
        for item in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
            label = javax.swing.JLabel(car[item])
            box = makeSwingBox(self.reportWidth[item] * self.panelWidth, self.panelHeight)
            box.add(label)
            combinedInputLine.add(box)
        if shorterRow == 'car':
            combinedInputLine.add(makeSwingBox(rowAdjustment, self.panelHeight))
        listOfEqptRows.append(combinedInputLine)

    return listOfEqptRows, textBoxEntry

    def findLongestRow(self):
        '''The length of the locos row is compared to the length of the cars row, the longer is used for all items in the set cars form'''

        locoRowLength = 0
        for item in jmri.jmrit.operations.setup.Setup.getDropEngineMessageFormat():
            locoRowLength += self.reportWidth[item]

        carRowLength = 0
        for item in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
            carRowLength += self.reportWidth[item]

        if locoRowLength >= carRowLength:
            return locoRowLength
        else:
            return carRowLength

    def makeRsRowAdjustment(self):
        '''I can't figure out how to left justify JAVAX so I'm doing this BS work around'''

        for item in jmri.jmrit.operations.setup.Setup.getDropEngineMessageFormat():
            self.locoRowLength += self.reportWidth[item]

        for item in jmri.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat():
            self.carRowLength += self.reportWidth[item]

        locoAdjustment = 0
        if self.locoRowLength < self.carRowLength:
            locoAdjustment = ((self.carRowLength - self.locoRowLength) * self.panelWidth) + 4
            rowAdjustment = (self.carRowLength - self.locoRowLength) * self.panelWidth
            shorterRow = 'loco'

        carAdjustment = 0
        if self.locoRowLength >= self.carRowLength:
            carAdjustment = (self.locoRowLength - self.carRowLength) * self.panelWidth
            rowAdjustment = (self.locoRowLength - self.carRowLength) * self.panelWidth
            shorterRow = 'car'

        # return rowAdjustment, shorterRow
        return locoAdjustment, carAdjustment

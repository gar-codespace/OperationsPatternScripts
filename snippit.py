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

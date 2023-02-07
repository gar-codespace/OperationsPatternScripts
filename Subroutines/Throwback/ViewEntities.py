# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Build the GUI here.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

class tbSubroutinePanel:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.controlWidgets = []
        self.displayWidgets = []
        self.configFile = PSE.readConfigFile()

        return

    def tbPanelMaker(self):

        snapShot = self.configFile['Throwback']['SS']

        lastSnapShot = snapShot[-1]

        tpPanel = PSE.JAVX_SWING.JPanel()
        tpPanel.setLayout(PSE.JAVX_SWING.BoxLayout(tpPanel, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))

    # Selection
        selectionFrame = PSE.JAVX_SWING.JPanel()
        selectionFrame.setName('selectionFrame')
        selectionFrame.setLayout(PSE.JAVX_SWING.BoxLayout(selectionFrame, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        selectionFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE[u'Total Commits'] + u' - ' + str(len(snapShot) - 1))

        inputRow = PSE.JAVX_SWING.JPanel()
        inputRow.setName('inputRow')

        pvButton = PSE.JAVX_SWING.JButton()
        pvButton.setText(PSE.BUNDLE[u'Previous'])
        pvButton.setName('previous')
        self.controlWidgets.append(pvButton)

        timeStampLabel = PSE.JAVX_SWING.JLabel(lastSnapShot[0])
        timeStampLabel.setName('timeStamp')
        self.displayWidgets.append(timeStampLabel)

        tbText = PSE.JAVX_SWING.JTextField(20)
        tbText.setText(lastSnapShot[1])
        tbText.setName('tbText')
        self.displayWidgets.append(tbText)

        nxButton = PSE.JAVX_SWING.JButton()
        nxButton.setText(PSE.BUNDLE[u'Next'])
        nxButton.setName('next')
        self.controlWidgets.append(nxButton)

        inputRow.add(pvButton)
        inputRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        inputRow.add(timeStampLabel)
        inputRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        inputRow.add(tbText)
        inputRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        inputRow.add(nxButton)

        buttonRow = PSE.JAVX_SWING.JPanel()
        buttonRow.setName('buttonRow')

        ssButton = PSE.JAVX_SWING.JButton()
        ssButton.setText(PSE.BUNDLE[u'Add New Commit'])
        ssButton.setName('commit')
        self.controlWidgets.append(ssButton)

        rsButton = PSE.JAVX_SWING.JButton()
        rsButton.setText(PSE.BUNDLE[u'Reset All Commits'])
        rsButton.setName('reset')
        self.controlWidgets.append(rsButton)

        buttonRow.add(ssButton)
        buttonRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
        buttonRow.add(rsButton)

        selectionFrame.add(inputRow)
        selectionFrame.add(buttonRow)
    # Action
        actionFrame = PSE.JAVX_SWING.JPanel()
        actionFrame.setName('actionFrame')
        actionFrame.setLayout(PSE.JAVX_SWING.BoxLayout(actionFrame, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        actionFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE[u'Action'])

        checkboxRow = PSE.JAVX_SWING.JPanel()
        checkboxRow.setName('checkboxRow')

        carsCheckBox = PSE.JAVX_SWING.JCheckBox()
        carsCheckBox.setText(PSE.BUNDLE['Cars'])
        carsCheckBox.setSelected(True)
        carsCheckBox.setName('cCheckBox')
        self.displayWidgets.append(carsCheckBox)

        locosCheckBox = PSE.JAVX_SWING.JCheckBox()
        locosCheckBox.setText(PSE.BUNDLE['Engines'])
        locosCheckBox.setSelected(True)
        locosCheckBox.setName('eCheckBox')
        self.displayWidgets.append(locosCheckBox)

        locationsCheckBox = PSE.JAVX_SWING.JCheckBox()
        locationsCheckBox.setText(PSE.BUNDLE['Locations'])
        locationsCheckBox.setSelected(True)
        locationsCheckBox.setName('lCheckBox')
        self.displayWidgets.append(locationsCheckBox)

        routesCheckBox = PSE.JAVX_SWING.JCheckBox()
        routesCheckBox.setText(PSE.BUNDLE['Routes'])
        routesCheckBox.setSelected(True)
        routesCheckBox.setName('rCheckBox')
        self.displayWidgets.append(routesCheckBox)

        trainsCheckBox = PSE.JAVX_SWING.JCheckBox()
        trainsCheckBox.setText(PSE.BUNDLE['Trains'])
        trainsCheckBox.setSelected(True)
        trainsCheckBox.setName('tCheckBox')
        self.displayWidgets.append(trainsCheckBox)

        checkboxRow.add(carsCheckBox)
        checkboxRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        checkboxRow.add(locosCheckBox)
        checkboxRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        checkboxRow.add(locationsCheckBox)
        checkboxRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        checkboxRow.add(routesCheckBox)
        checkboxRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        checkboxRow.add(trainsCheckBox)

        actionRow = PSE.JAVX_SWING.JPanel()
        actionRow.setName('actionRow')

        tbButton = PSE.JAVX_SWING.JButton()
        tbButton.setText(PSE.BUNDLE[u'Throwback'])
        tbButton.setName('throwback')
        self.controlWidgets.append(tbButton)

        actionRow.add(tbButton)

        actionFrame.add(checkboxRow)
        actionFrame.add(actionRow)

        tpPanel.add(selectionFrame)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,10)))
        tpPanel.add(actionFrame)

        return tpPanel

    def tbWidgetGetter(self):

        return self.controlWidgets, self.displayWidgets

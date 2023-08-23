# coding=utf-8
# © 2023 Greg Ritacco

"""
All the GUI items are made here.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


class subroutineGui:

    def __init__(self):

        self.controlWidgets = []
        self.displayWidgets = []
        self.configFile = PSE.readConfigFile()

        return

    def guiMaker(self):
        """
        Make the GUI here.
        """

        snapShot = self.configFile['Throwback']['SS']

        lastSnapShot = snapShot[-1]

    # Selection
        selectionFrame = PSE.JAVX_SWING.JPanel()
        selectionFrame.setName('selectionFrame')
        selectionFrame.setLayout(PSE.JAVX_SWING.BoxLayout(selectionFrame, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        selectionFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Total Commits') + u' - ' + str(len(snapShot) - 1))

        tbText = PSE.JAVX_SWING.JTextField(20)
        tbText.setText(lastSnapShot[1])
        tbText.setName('tbText')
        self.displayWidgets.append(tbText)

        inputRow = PSE.JAVX_SWING.JPanel()
        inputRow.setName('inputRow')
        inputRow.add(tbText)

        ssButton = PSE.JAVX_SWING.JButton()
        ssButton.setText(PSE.getBundleItem('Add New Commit'))
        ssButton.setName('commit')
        self.controlWidgets.append(ssButton)

        commitRow = PSE.JAVX_SWING.JPanel()
        commitRow.setName('commitRow')
        commitRow.add(ssButton)

        rsButton = PSE.JAVX_SWING.JButton()
        rsButton.setText(PSE.getBundleItem('Delete All Commits'))
        rsButton.setName('reset')
        self.controlWidgets.append(rsButton)

        resetRow = PSE.JAVX_SWING.JPanel()
        resetRow.setName('resetRow')
        resetRow.add(rsButton)

        selectionFrame.add(inputRow)
        selectionFrame.add(commitRow)
        # selectionFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))
        selectionFrame.add(PSE.JAVX_SWING.JSeparator())
        # selectionFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))
        selectionFrame.add(resetRow)
        # selectionFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))

    # Action
        actionFrame = PSE.JAVX_SWING.JPanel()
        actionFrame.setName('actionFrame')
        actionFrame.setLayout(PSE.JAVX_SWING.BoxLayout(actionFrame, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        actionFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Action'))

        commitRow = PSE.JAVX_SWING.JPanel()
        commitRow.setName('commitRow')

        pvButton = PSE.JAVX_SWING.JButton()
        pvButton.setText(PSE.getBundleItem('Previous'))
        pvButton.setName('previous')
        self.controlWidgets.append(pvButton)

        timeStamp = PSE.JAVX_SWING.JLabel(lastSnapShot[0])
        timeStamp.setName('timeStamp')
        self.displayWidgets.append(timeStamp)

        commitName = PSE.JAVX_SWING.JLabel(lastSnapShot[1])
        commitName.setName('commitName')
        self.displayWidgets.append(commitName)

        nxButton = PSE.JAVX_SWING.JButton()
        nxButton.setText(PSE.getBundleItem('Next'))
        nxButton.setName('next')
        self.controlWidgets.append(nxButton)

        commitRow.add(pvButton)
        commitRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        commitRow.add(timeStamp)
        commitRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        commitRow.add(commitName)
        commitRow.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        commitRow.add(nxButton)

        checkboxRow = PSE.JAVX_SWING.JPanel()
        checkboxRow.setName('checkboxRow')

        carsCheckBox = PSE.JAVX_SWING.JCheckBox()
        carsCheckBox.setText(PSE.getBundleItem('Cars'))
        carsCheckBox.setSelected(False)
        carsCheckBox.setName('cCheckBox')
        self.displayWidgets.append(carsCheckBox)

        locosCheckBox = PSE.JAVX_SWING.JCheckBox()
        locosCheckBox.setText(PSE.getBundleItem('Engines'))
        locosCheckBox.setSelected(False)
        locosCheckBox.setName('eCheckBox')
        self.displayWidgets.append(locosCheckBox)

        locationsCheckBox = PSE.JAVX_SWING.JCheckBox()
        locationsCheckBox.setText(PSE.getBundleItem('Locations'))
        locationsCheckBox.setSelected(False)
        locationsCheckBox.setName('lCheckBox')
        self.displayWidgets.append(locationsCheckBox)

        routesCheckBox = PSE.JAVX_SWING.JCheckBox()
        routesCheckBox.setText(PSE.getBundleItem('Routes'))
        routesCheckBox.setSelected(False)
        routesCheckBox.setName('rCheckBox')
        self.displayWidgets.append(routesCheckBox)

        trainsCheckBox = PSE.JAVX_SWING.JCheckBox()
        trainsCheckBox.setText(PSE.getBundleItem('Trains'))
        trainsCheckBox.setSelected(False)
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
        tbButton.setText(PSE.getBundleItem('Throwback'))
        tbButton.setName('throwback')
        self.controlWidgets.append(tbButton)

        actionRow.add(tbButton)

        actionFrame.add(commitRow)
        actionFrame.add(checkboxRow)
        # actionFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))
        actionFrame.add(PSE.JAVX_SWING.JSeparator())
        # actionFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))
        actionFrame.add(actionRow)

        tpPanel = PSE.JAVX_SWING.JPanel()
        tpPanel.add(selectionFrame)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        tpPanel.add(actionFrame)
        
        return tpPanel

    def guiWidgetGetter(self):

        widgets = {}
        widgets['control'] = self.controlWidgets
        widgets['display'] = self.displayWidgets

        return widgets

# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Creates either version of the j Plus panel."""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

class jPlusSubroutinePanel:

    def __init__(self):

        self.configFile = PSE.readConfigFile()

        self.controlWidgets = {}
        self.panelWidgets = {}

        return

    def updateButton(self):
        """The *.setName value is the name of the action for the widget"""

        upButton = PSE.JAVX_SWING.JButton()
        upButton.setText(PSE.BUNDLE[u'Update'])
        upButton.setName('update')

        return upButton

    def jPlusPanelEditable(self):
        """User can edit the railroad details."""

        jPlusPanel = PSE.JAVX_SWING.JPanel()
        jPlusPanel.setName('jPlusPanel')
        jPlusPanel.setLayout(PSE.JAVX_SWING.BoxLayout(jPlusPanel, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        jPlusPanel.border = PSE.JAVX_SWING.BorderFactory.createEmptyBorder(5,0,5,0)

        inputGrid = PSE.JAVX_SWING.JPanel()
        inputGrid.setLayout(PSE.JAVA_AWT.GridLayout(4, 2, 10, 4))

        a1 = PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Operating Railroad Name'], PSE.JAVX_SWING.JLabel.RIGHT)

        a3 = PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Operational Territory'], PSE.JAVX_SWING.JLabel.RIGHT)
        
        a5 = PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Location'], PSE.JAVX_SWING.JLabel.RIGHT)

        a7 = PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Year Modeled'], PSE.JAVX_SWING.JLabel.RIGHT)

        a2 = PSE.JAVX_SWING.JTextField(self.configFile['JP']['OR'])
        a2.setColumns(25) # sets the width for all text fields
        self.panelWidgets['OR'] = a2

        a4 = PSE.JAVX_SWING.JTextField(self.configFile['JP']['TR'])
        self.panelWidgets['TR'] = a4

        a6 = PSE.JAVX_SWING.JTextField(self.configFile['JP']['LO'])
        self.panelWidgets['LO'] = a6

        # a8 = PSE.JAVX_SWING.JTextField(self.configFile['JP']['YR'])
        a8 = PSE.JAVX_SWING.JTextField(PSE.JMRI.jmrit.operations.setup.Setup.getYearModeled())
        # a8.setText(self.configFile['JP']['YR'])
        # print(self.configFile['JP']['YR'])

        self.panelWidgets['YR'] = a8

        inputGrid.add(a1)
        inputGrid.add(a2)
        inputGrid.add(a3)
        inputGrid.add(a4)
        inputGrid.add(a5)
        inputGrid.add(a6)
        inputGrid.add(a7)
        inputGrid.add(a8)

        jPlusPanel.add(inputGrid)
        jPlusPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,20)))
        
        upButton = self.updateButton()
        self.controlWidgets['UP'] = upButton
        jPlusPanel.add(upButton)

        return jPlusPanel

    def jPlusPanelFixed(self):
        """If using o2o, the railroad details are added from tpRailroadData.json."""

        jPlusPanel = PSE.JAVX_SWING.JPanel()
        jPlusPanel.setLayout(PSE.JAVX_SWING.BoxLayout(jPlusPanel, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        jPlusPanel.border = PSE.JAVX_SWING.BorderFactory.createEmptyBorder(5,0,5,0)

        tpRailroadData = PSE.getTpRailroadJson('tpRailroadData')

        if not tpRailroadData:
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(PSE.BUNDLE[u'Not found: incomplete o2o import'])
            jPlusPanel.add(headerDetailLabel)
            jPlusPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))

            return jPlusPanel

        if self.configFile['JP']['OR']:
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(self.configFile['JP']['OR'])
            jPlusPanel.add(headerDetailLabel)
            jPlusPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))

        if self.configFile['JP']['TR']:
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(self.configFile['JP']['TR'])
            jPlusPanel.add(headerDetailLabel)
            jPlusPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))

        if self.configFile['JP']['LO']:
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(self.configFile['JP']['LO'])
            jPlusPanel.add(headerDetailLabel)
            jPlusPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))

        if self.configFile['JP']['YR']:
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(self.configFile['JP']['YR'])
            jPlusPanel.add(headerDetailLabel)

        self.controlWidgets['UP'] = self.updateButton()

        return jPlusPanel

    def jPlusWidgets(self):

        allWidgets = {}
        allWidgets['control'] = self.controlWidgets
        allWidgets['panel'] = self.panelWidgets

        return allWidgets

# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Creates either version of the j Plus panel."""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.jPlusSubroutine.ViewEntities'
SCRIPT_REV = 20221010

class jPlusSubroutinePanel:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.configFile = PSE.readConfigFile()

        self.upButton = PSE.JAVX_SWING.JButton()
        self.upButton.setText(PSE.BUNDLE[u'Update'])
        self.upButton.setName('update')

        self.controlWidgets = {}
        self.controlWidgets['UP'] = self.upButton
        self.panelWidgets = {}

        return

    def jPlusPanelEditable(self):
        """User can edit the railroad details."""

        jPlusPanel = PSE.JAVX_SWING.JPanel()
        jPlusPanel.setLayout(PSE.JAVX_SWING.BoxLayout(jPlusPanel, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        jPlusPanel.border = PSE.JAVX_SWING.BorderFactory.createEmptyBorder(10,0,10,0)

        inputGrid = PSE.JAVX_SWING.JPanel()
        inputGrid.setLayout(PSE.JAVA_AWT.GridLayout(4, 2, 10, 4))

        a1 = PSE.JAVA_AWT.Label(PSE.BUNDLE['Operating Railroad Name'], PSE.JAVA_AWT.Label.RIGHT)

        a3 = PSE.JAVA_AWT.Label(PSE.BUNDLE['Operational Territory'], PSE.JAVA_AWT.Label.RIGHT)

        a5 = PSE.JAVA_AWT.Label(PSE.BUNDLE['Location'], PSE.JAVA_AWT.Label.RIGHT)

        a7 = PSE.JAVA_AWT.Label(PSE.BUNDLE['Year Modeled'], PSE.JAVA_AWT.Label.RIGHT)

        a2 = PSE.JAVX_SWING.JTextField(self.configFile['JP']['OR'], PSE.JAVA_AWT.Label.LEFT)
        a2.setColumns(25)
        self.panelWidgets['OR'] = a2

        a4 = PSE.JAVX_SWING.JTextField(self.configFile['JP']['TR'], PSE.JAVA_AWT.Label.LEFT)
        a4.setColumns(25)
        self.panelWidgets['TR'] = a4

        a6 = PSE.JAVX_SWING.JTextField(self.configFile['JP']['LO'], PSE.JAVA_AWT.Label.LEFT)
        a6.setColumns(25)
        self.panelWidgets['LO'] = a6

        a8 = PSE.JAVX_SWING.JTextField(self.configFile['JP']['YR'], PSE.JAVA_AWT.Label.LEFT)
        a8.setColumns(25)
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
        jPlusPanel.add(self.upButton)

        return jPlusPanel

    def jPlusPanelFixed(self):
        """If using o2o, the railroad details are added from tpRailroadData.json."""

        jPlusPanel = PSE.JAVX_SWING.JPanel()
        jPlusPanel.setLayout(PSE.JAVX_SWING.BoxLayout(jPlusPanel, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        jPlusPanel.border = PSE.JAVX_SWING.BorderFactory.createEmptyBorder(10,0,10,0)

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

        return jPlusPanel

    def jPlusWidgets(self):

        allWidgets = {}
        allWidgets['control'] = self.controlWidgets
        allWidgets['panel'] = self.panelWidgets

        return allWidgets

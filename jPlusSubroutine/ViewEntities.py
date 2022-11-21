# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Template."""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.jPlusSubroutine.ViewEntities'
SCRIPT_REV = 20221010

class jPlusSubroutinePanel:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.configFile = PSE.readConfigFile()

        self.upButton = PSE.JAVX_SWING.JButton()
        # self.upButton.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
        self.upButton.setText(PSE.BUNDLE[u'Update'])
        self.upButton.setName('update')

        self.controlWidgets = {}
        self.controlWidgets['UP'] = self.upButton
        self.panelWidgets = {}

        return

    def jPlusPanelEditable(self):
        """User can edit the rr details."""

        configFile = PSE.readConfigFile()

        combinedHeader = PSE.JAVX_SWING.JPanel()
        combinedHeader.setLayout(PSE.JAVX_SWING.BoxLayout(combinedHeader, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        combinedHeader.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
        # combinedHeader.border = PSE.JAVX_SWING.BorderFactory.createEmptyBorder(10,0,10,0)

        panel = PSE.JAVX_SWING.JPanel()
        # panel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
        panel.add(PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Operating Railroad Name']))
        panel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8 ,0)))
        inputText = PSE.JAVX_SWING.JTextField(configFile['JP']['OR'])
        inputText.setColumns(40)
        panel.add(inputText)
        self.panelWidgets['OR'] = inputText
        combinedHeader.add(panel)

        combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0 ,3)))

        panel = PSE.JAVX_SWING.JPanel()
        panel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
        panel.add(PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Operational Territory']))
        panel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8 ,0)))
        inputText = PSE.JAVX_SWING.JTextField(configFile['JP']['TR'])
        inputText.setColumns(40)
        panel.add(inputText)
        self.panelWidgets['TR'] = inputText
        combinedHeader.add(panel)

        combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0 ,3)))

        panel = PSE.JAVX_SWING.JPanel()
        panel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
        panel.add(PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Location']))
        panel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8 ,0)))
        inputText = PSE.JAVX_SWING.JTextField(configFile['JP']['LO'])
        inputText.setColumns(40)
        panel.add(inputText)
        self.panelWidgets['LO'] = inputText
        combinedHeader.add(panel)

        combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0 ,3)))

        panel = PSE.JAVX_SWING.JPanel()
        panel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
        panel.add(PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Year Modeled']))
        panel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(5 ,0)))
        inputText = PSE.JAVX_SWING.JTextField(configFile['JP']['YR'])
        inputText.setColumns(5)
        panel.add(inputText)
        self.panelWidgets['YR'] = inputText
        combinedHeader.add(panel)

        combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,15)))
        combinedHeader.add(self.upButton)

        return combinedHeader

    def jPlusPanelFixed(self):
        """If using o2o, the rr details are adde from TrainPlayer.
            This is a duplicate of o2o.ModelEntities.getTpRailroadData():"""


        combinedHeader = PSE.JAVX_SWING.JPanel()
        combinedHeader.setLayout(PSE.JAVX_SWING.BoxLayout(combinedHeader, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        combinedHeader.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
        # combinedHeader.border = PSE.JAVX_SWING.BorderFactory.createEmptyBorder(10,0,10,0)

        reportName = 'tpRailroadData'
        fileName = reportName + '.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        if not PSE.JAVA_IO.File(targetPath).isFile():
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(PSE.BUNDLE[u'Not found: incomplete o2o import'])
            combinedHeader.add(headerDetailLabel)
            combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))
            return combinedHeader

        report = PSE.genericReadReport(targetPath)
        tpRailroad = PSE.loadJson(report)

        if tpRailroad['operatingRoad']:
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(tpRailroad['operatingRoad'])
            combinedHeader.add(headerDetailLabel)
            combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))

        if tpRailroad['territory']:
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(tpRailroad['territory'])
            combinedHeader.add(headerDetailLabel)
            combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))

        if tpRailroad['location']:
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(tpRailroad['location'])
            combinedHeader.add(headerDetailLabel)
            combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))

        if tpRailroad['year']:
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(tpRailroad['year'])
            combinedHeader.add(headerDetailLabel)

        return combinedHeader

    def jPlusWidgets(self):

        allWidgets = {}
        allWidgets['control'] = self.controlWidgets
        allWidgets['panel'] = self.panelWidgets

        return allWidgets

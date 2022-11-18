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

        self.nrButton = PSE.JAVX_SWING.JButton()
        self.nrButton.setText(PSE.BUNDLE[u'Update'])
        self.nrButton.setName('update')

        self.controlWidgets = []

        return

    def jPlusPanelEditable(self):
        """User can edit the rr details."""

        tpPanel = PSE.JAVX_SWING.JPanel()


        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        tpPanel.add(self.nrButton)

        return tpPanel

    def jPlusPanelFixed(self):
        """If using o2o, the rr details are adde from TrainPlayer.
            This is a duplicate of o2o.ModelEntities.getTpRailroadData():"""


        combinedHeader = PSE.JAVX_SWING.JPanel()
        combinedHeader.setLayout(PSE.JAVX_SWING.BoxLayout(combinedHeader, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        combinedHeader.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
        combinedHeader.border = PSE.JAVX_SWING.BorderFactory.createEmptyBorder(10,0,10,0)

        reportName = 'tpRailroadData'
        fileName = reportName + '.json'
        targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

        try:
            PSE.JAVA_IO.File(targetPath).isFile()
        except:
            headerDetailLabel = PSE.JAVX_SWING.JLabel()
            headerDetailLabel.setAlignmentX(PSE.JAVA_AWT.Component.CENTER_ALIGNMENT)
            headerDetailLabel.setText(PSE.BUNDLE[u'Not found: incomplete o2o import'])
            combinedHeader.add(headerDetailLabel)
            combinedHeader.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))
            return

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

    def JPWidgetGetter(self):


        self.controlWidgets.append(self.nrButton)

        return self.controlWidgets

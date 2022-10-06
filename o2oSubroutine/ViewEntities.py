# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Creates the TrainPlayer panel."""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ViewEntities'
SCRIPT_REV = 20220101

class O2oSubroutinePanel:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.nrButton = PSE.JAVX_SWING.JButton()
        self.nrButton.setText(PSE.BUNDLE[u'New JMRI Railroad'])
        self.nrButton.setName('newJmriRailroad')

        self.urButton = PSE.JAVX_SWING.JButton()
        self.urButton.setText(PSE.BUNDLE[u'Update JMRI Railroad'])
        self.urButton.setName('updateJmriRailroad')

        self.controlWidgets = []

        return

    def o2oPanelMaker(self):

        tpPanel = PSE.JAVX_SWING.JPanel()

        tpPanel.add(self.nrButton)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        tpPanel.add(self.urButton)

        return tpPanel

    def o2oWidgetGetter(self):

        self.controlWidgets.append(self.nrButton)
        self.controlWidgets.append(self.urButton)

        return self.controlWidgets

# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Creates the TrainPlayer panel, implemented in v3."""

from psEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ViewEntities'
SCRIPT_REV = 20220101

class O2oSubroutinePanel:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.irButton = PSE.JAVX_SWING.JButton()
        self.irButton.setText(PSE.BUNDLE[u'Import TrainPlayer© Railroad'])
        self.irButton.setName('importTpRailroad')

        self.nrButton = PSE.JAVX_SWING.JButton()
        self.nrButton.setText(PSE.BUNDLE[u'New JMRI Railroad'])
        self.nrButton.setName('newJmriRailroad')

        self.urButton = PSE.JAVX_SWING.JButton()
        self.urButton.setText(PSE.BUNDLE[u'Update Rolling Stock'])
        self.urButton.setName('updateRollingStock')

        self.ulButton = PSE.JAVX_SWING.JButton()
        self.ulButton.setText(PSE.BUNDLE[u'Update Locations'])
        self.ulButton.setName('updateLocations')

        self.controlWidgets = []

        return

    def o2oPanelMaker(self):

        tpPanel = PSE.JAVX_SWING.JPanel()

        # tpPanel.add(self.irButton)
        # tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        tpPanel.add(self.nrButton)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        tpPanel.add(self.urButton)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        tpPanel.add(self.ulButton)

        return tpPanel

    def o2oWidgetGetter(self):

        self.controlWidgets.append(self.irButton)
        self.controlWidgets.append(self.nrButton)
        self.controlWidgets.append(self.urButton)
        self.controlWidgets.append(self.ulButton)

        return self.controlWidgets

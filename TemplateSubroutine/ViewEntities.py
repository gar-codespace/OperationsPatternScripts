# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Template
"""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.xxxSubroutine.ViewEntities'
SCRIPT_REV = 20221010

class xxxSubroutinePanel:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.controlWidgets = []

        return

    def xxxPanelMaker(self):
        """Build the GUI here."""

        tpPanel = PSE.JAVX_SWING.JPanel()

        nrButton = PSE.JAVX_SWING.JButton()
        nrButton.setText(PSE.BUNDLE[u'Button'])
        nrButton.setName('button')
        self.controlWidgets.append(self.nrButton)

        tpPanel.add(nrButton)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))

        return tpPanel

    def xxxWidgetGetter(self):
        """Returns all the widgets."""

        return self.controlWidgets

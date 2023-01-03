# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Template
"""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.' + __package__ + '.ViewEntities'
SCRIPT_REV = 20221010

class xxSubroutinePanel:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.controlWidgets = []

        return

    def xxPanelMaker(self):
        """Build the GUI here."""

        tpPanel = PSE.JAVX_SWING.JPanel()

        nrButton = PSE.JAVX_SWING.JButton()
        nrButton.setText(PSE.BUNDLE['xyzzy'])
        nrButton.setName('button')
        self.controlWidgets.append(nrButton)

        tpPanel.add(nrButton)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))

        return tpPanel

    def xxWidgetGetter(self):
        """Returns all the widgets."""

        return self.controlWidgets

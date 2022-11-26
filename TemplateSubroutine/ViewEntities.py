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

        self.nrButton = PSE.JAVX_SWING.JButton()
        self.nrButton.setText(PSE.BUNDLE[u'Button'])
        self.nrButton.setName('button')

        self.controlWidgets = []

        return

    def xxxPanelMaker(self):

        tpPanel = PSE.JAVX_SWING.JPanel()

        tpPanel.add(self.nrButton)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        tpPanel.add(self.nrButton)

        return tpPanel

    def xxxWidgetGetter(self):

        self.controlWidgets.append(self.nrButton)
        self.controlWidgets.append(self.nrButton)

        return self.controlWidgets

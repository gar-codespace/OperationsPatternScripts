# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Template subroutine.
Build the GUI here.
Replace XX with a designator for this subroutines' name.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

class templateSubroutinePanel:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.controlWidgets = []

        return

    def templatePanelMaker(self):
        """Build the GUI here."""

        tpPanel = PSE.JAVX_SWING.JPanel()

        nrButton = PSE.JAVX_SWING.JButton()
        nrButton.setText(PSE.BUNDLE['xyzzy'])
        nrButton.setName('button')
        self.controlWidgets.append(nrButton)

        tpPanel.add(nrButton)
        # tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))

        return tpPanel

    def templateWidgetGetter(self):
        """Returns all the widgets."""

        return self.controlWidgets

# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
o2o
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

class subroutineGui:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.nrButton = PSE.JAVX_SWING.JButton()
        self.nrButton.setText(PSE.BUNDLE['New JMRI Railroad'])
        self.nrButton.setName('newJmriRailroad')

        self.urButton = PSE.JAVX_SWING.JButton()
        self.urButton.setText(PSE.BUNDLE['Update JMRI Railroad'])
        self.urButton.setName('updateJmriRailroad')

        self.rsButton = PSE.JAVX_SWING.JButton()
        self.rsButton.setText('Update Rolling Stock')
        self.rsButton.setName('updateJmriRollingingStock')

        return

    def guiMaker(self):
        """Make the GUI here."""

        tpPanel = PSE.JAVX_SWING.JPanel()
        newRrPanel = PSE.JAVX_SWING.JPanel()
        updateRrPanel = PSE.JAVX_SWING.JPanel()

        newRrPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE['Create New Railroad'])
        newRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(50,0)))
        newRrPanel.add(self.nrButton)
        newRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(50,0)))

        updateRrPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE['Update Current Railroad'])
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(50,0)))
        updateRrPanel.add(self.urButton)
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
        updateRrPanel.add(self.rsButton)
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(50,0)))

        tpPanel.add(newRrPanel)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
        tpPanel.add(updateRrPanel)

        return tpPanel

    def guiWidgetGetter(self):

        widgets = []

        widgets.append(self.nrButton)
        widgets.append(self.urButton)
        widgets.append(self.rsButton)

        return widgets

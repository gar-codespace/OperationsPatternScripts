# coding=utf-8
# © 2023 Greg Ritacco

"""
All the GUI items are made here.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

class subroutineGui:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.nrButton = PSE.JAVX_SWING.JButton()
        self.nrButton.setText(PSE.BUNDLE['Initialize'])
        self.nrButton.setName('newJmriRailroad')

        self.ulButton = PSE.JAVX_SWING.JButton()
        self.ulButton.setText(PSE.BUNDLE['Locations'])
        self.ulButton.setName('updateJmriLocations')

        self.uiButton = PSE.JAVX_SWING.JButton()
        self.uiButton.setText(PSE.BUNDLE['Industries'])
        self.uiButton.setName('updateJmriTracks')

        self.ursButton = PSE.JAVX_SWING.JButton()
        self.ursButton.setText('Cars')
        self.ursButton.setName('updateJmriRollingingStock')
        return

    def guiMaker(self):
        """Make the GUI here."""

        tpPanel = PSE.JAVX_SWING.JPanel()
        newRrPanel = PSE.JAVX_SWING.JPanel()
        updateRrPanel = PSE.JAVX_SWING.JPanel()

        newRrPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE['Import preperation'])
        newRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(50,0)))
        newRrPanel.add(self.nrButton)
        newRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(50,0)))

        updateRrPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE['Import from TrainPlayer'])
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(50,0)))
        updateRrPanel.add(self.ulButton)
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
        updateRrPanel.add(self.uiButton)
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
        updateRrPanel.add(self.ursButton)
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(50,0)))

        tpPanel.add(updateRrPanel)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
        tpPanel.add(newRrPanel)

        return tpPanel

    def guiWidgetGetter(self):

        widgets = []

        widgets.append(self.nrButton)
        widgets.append(self.ulButton)
        widgets.append(self.uiButton)
        widgets.append(self.ursButton)

        return widgets

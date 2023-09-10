# coding=utf-8
# © 2023 Greg Ritacco

"""
All the GUI items are made here.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901


class subroutineGui:

    def __init__(self):
        """
        The *.setName value is the name of the action for the widget.
        """

        self.nrButton = PSE.JAVX_SWING.JButton()
        self.nrButton.setText(PSE.getBundleItem('Initialize Railroad'))
        self.nrButton.setName('initializeJmriRailroad')

        self.ulButton = PSE.JAVX_SWING.JButton()
        self.ulButton.setText(PSE.getBundleItem('Locations'))
        self.ulButton.setName('updateJmriLocations')

        self.uiButton = PSE.JAVX_SWING.JButton()
        self.uiButton.setText(PSE.getBundleItem('Industries'))
        self.uiButton.setName('updateJmriTracks')

        self.ursButton = PSE.JAVX_SWING.JButton()
        self.ursButton.setText(PSE.getBundleItem('Cars'))
        self.ursButton.setName('updateJmriRollingingStock')

        self.lpButton = PSE.JAVX_SWING.JButton()
        self.lpButton.setText(PSE.getBundleItem('Extended Header'))
        self.lpButton.setName('updateJmriProperties')

        return

    def getGuiFrame(self):
        """
        The title border panel the whole GUI is set into.
        """

        subroutineFrame = PSE.JAVX_SWING.JPanel()
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('o2o Subroutine'))

        return subroutineFrame
    
    def guiMaker(self):
        """
        Make the GUI here.
        """

        tpPanel = PSE.JAVX_SWING.JPanel()
        newRrPanel = PSE.JAVX_SWING.JPanel()
        updateRrPanel = PSE.JAVX_SWING.JPanel()
        extendedRrPanel = PSE.JAVX_SWING.JPanel()

        newRrPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Import Preperation'))
        newRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(40,0)))
        newRrPanel.add(self.nrButton)
        newRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(40,0)))

        updateRrPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem("Import TrainPlayer's Advanced Ops"))
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(40,0)))
        updateRrPanel.add(self.ulButton)
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        updateRrPanel.add(self.uiButton)
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        updateRrPanel.add(self.ursButton)
        updateRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(40,0)))

        extendedRrPanel.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Import Personalized Settings'))
        extendedRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(40,0)))
        extendedRrPanel.add(self.lpButton)
        extendedRrPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(40,0)))

        tpPanel.add(updateRrPanel)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
        tpPanel.add(extendedRrPanel)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
        tpPanel.add(newRrPanel)

        guiFrame = self.getGuiFrame()
        guiFrame.add(tpPanel)
        
        return guiFrame

    def guiWidgetGetter(self):

        widgets = []

        widgets.append(self.nrButton)
        widgets.append(self.ulButton)
        widgets.append(self.uiButton)
        widgets.append(self.ursButton)
        widgets.append(self.lpButton)

        return widgets

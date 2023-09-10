# coding=utf-8
# © 2023 Greg Ritacco

"""
All the GUI items are made here.
Replace XX with a designator for this subroutines' name.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

class subroutineGui:

    def __init__(self):
        """
        The *.setName value is the name of the action for the widget.
        """

        self.controlWidgets = []

        return

    def getGuiFrame(self):
        """
        The title border panel the whole GUI is set into.
        """

        subroutineFrame = PSE.JAVX_SWING.JPanel()
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Template Subroutine'))

        return subroutineFrame
    
    def guiMaker(self):
        """
        Make the GUI here.
        """

        tpPanel = PSE.JAVX_SWING.JPanel()

        nrButton = PSE.JAVX_SWING.JButton()
        
        nrButton.setText(PSE.getBundleItem('xyzzy'))
        
        nrButton.setName('button')
        self.controlWidgets.append(nrButton)

        tpPanel.add(nrButton)
        # tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))

        guiFrame = self.getGuiFrame()
        guiFrame.add(tpPanel)
        
        return guiFrame

    def guiWidgetGetter(self):
        """
        Returns all the widgets.
        Can return a list or dict.
        """

        return self.controlWidgets

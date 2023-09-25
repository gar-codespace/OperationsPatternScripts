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

    # The Divisions combo box content is managed by the Controller
        self.divisionComboBox = PSE.JAVX_SWING.JComboBox()
        self.divisionComboBox.setName('sDivisions')

    # The Locations combo box content is managed by the Controller
        self.locationComboBox = PSE.JAVX_SWING.JComboBox()
        self.locationComboBox.setName('sLocations')

    # The Scanner combo box content is managed by the Controller
        self.scannerComboBox = PSE.JAVX_SWING.JComboBox()
        self.scannerComboBox.setName('sScanner')

        self.qrButton = PSE.JAVX_SWING.JButton()
        self.qrButton.setText(PSE.getBundleItem('Generate'))
        self.qrButton.setName('self.qrButton')



        return

    def getGuiFrame(self):
        """
        The title border panel the whole GUI is set into.
        """

        subroutineFrame = PSE.JAVX_SWING.JPanel()
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Scanner Subroutine'))

        return subroutineFrame
    
    def guiMaker(self):
        """
        Make the GUI here.
        """

        tpPanel = PSE.JAVX_SWING.JPanel()
    # Scan QR code
        qrFrame = PSE.JAVX_SWING.JPanel()
        qrFrame.setName('qrFrame')
        qrFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Generate QR codes'))

        qrFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        qrFrame.add(self.qrButton)
        qrFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
    # Apply scanner
        scFrame = PSE.JAVX_SWING.JPanel()
        scFrame.setName('scFrame')
        scFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Apply scanner data'))

        divisionLabel = PSE.JAVX_SWING.JLabel(PSE.getBundleItem('Division:'))
        locationLabel = PSE.JAVX_SWING.JLabel(PSE.getBundleItem('Location:'))
        fileLabel = PSE.JAVX_SWING.JLabel(PSE.getBundleItem('Scanner:'))
        
        self.scButton = PSE.JAVX_SWING.JButton()
        self.scButton.setText(PSE.getBundleItem('Apply'))
        self.scButton.setName('scButton')     

        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        scFrame.add(divisionLabel)
        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        scFrame.add(self.divisionComboBox)
        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        scFrame.add(locationLabel)
        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        scFrame.add(self.locationComboBox)
        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        scFrame.add(fileLabel)
        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        scFrame.add(self.scannerComboBox)
        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        scFrame.add(self.scButton)
        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        
        tpPanel.add(qrFrame)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        tpPanel.add(scFrame)

        guiFrame = self.getGuiFrame()
        guiFrame.add(tpPanel)
        
        return guiFrame

    def guiWidgetGetter(self):
        """
        Returns all the widgets.
        Can return a list or dict.
        """

        widgets = []

        widgets.append(self.divisionComboBox)
        widgets.append(self.locationComboBox)
        widgets.append(self.scannerComboBox)
        widgets.append(self.qrButton)
        widgets.append(self.scButton)

        return widgets

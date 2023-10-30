# coding=utf-8
# © 2023 Greg Ritacco

"""
All the GUI items are made here.
"""

from opsEntities import PSE

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001


class subroutineGui:

    def __init__(self):
        """
        The *.setName value is the name of the action for the widget.
        """

        self.qrCodeButton = PSE.JAVX_SWING.JButton()
        self.qrCodeButton.setText(PSE.getBundleItem('Generate'))
        self.qrCodeButton.setName('self.qrCodeButton')

    # The Scanner combo box content is managed by the Controller
        self.scannerComboBox = PSE.JAVX_SWING.JComboBox()
        self.scannerComboBox.setName('sScanner')

        self.applyButton = PSE.JAVX_SWING.JButton()
        self.applyButton.setText(PSE.getBundleItem('Apply'))
        self.applyButton.setName('applyButton')

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
        qrFrame.add(self.qrCodeButton)
        qrFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
    # Apply scanner
        scFrame = PSE.JAVX_SWING.JPanel()
        scFrame.setName('scFrame')
        scFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Apply scanner data'))

        fileLabel = PSE.JAVX_SWING.JLabel(PSE.getBundleItem('Scanner:'))
        
        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        scFrame.add(fileLabel)
        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        scFrame.add(self.scannerComboBox)
        scFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        scFrame.add(self.applyButton)
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

        widgets.append(self.qrCodeButton)
        widgets.append(self.scannerComboBox)
        widgets.append(self.applyButton)

        return widgets

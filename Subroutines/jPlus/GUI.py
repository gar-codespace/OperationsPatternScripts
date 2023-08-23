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

        self.configFile = PSE.readConfigFile()

        self.controlWidgets = {}
        self.panelWidgets = {}

        return

    def getGuiFrame(self):
        """
        The title border panel the whole GUI is set into.
        """

        subroutineFrame = PSE.JAVX_SWING.JPanel()
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('jPlus Subroutine'))

        return subroutineFrame
    
    def guiMaker(self):
        """
        Make the GUI here.
        """

        jPlusPanel = PSE.JAVX_SWING.JPanel()
        jPlusPanel.setName('jPlus')
        jPlusPanel.setLayout(PSE.JAVX_SWING.BoxLayout(jPlusPanel, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        jPlusPanel.border = PSE.JAVX_SWING.BorderFactory.createEmptyBorder(5,0,5,0)

        inputGrid = PSE.JAVX_SWING.JPanel()
        inputGrid.setLayout(PSE.JAVA_AWT.GridLayout(4, 2, 10, 4))

        a1 = PSE.JAVX_SWING.JLabel(PSE.getBundleItem('Operating Railroad Name'), PSE.JAVX_SWING.JLabel.RIGHT)

        a3 = PSE.JAVX_SWING.JLabel(PSE.getBundleItem('Operational Territory'), PSE.JAVX_SWING.JLabel.RIGHT)
        
        a5 = PSE.JAVX_SWING.JLabel(PSE.getBundleItem('location'), PSE.JAVX_SWING.JLabel.RIGHT)

        a7 = PSE.JAVX_SWING.JLabel(PSE.getBundleItem('Year Modeled'), PSE.JAVX_SWING.JLabel.RIGHT)

        a2 = PSE.JAVX_SWING.JTextField(self.configFile['Main Script']['LD']['OR'])
        a2.setName('operatingRoad')
        a2.setColumns(25) # sets the width for all text fields
        self.panelWidgets['OR'] = a2

        a4 = PSE.JAVX_SWING.JTextField(self.configFile['Main Script']['LD']['TR'])
        a4.setName('territory')
        self.panelWidgets['TR'] = a4

        a6 = PSE.JAVX_SWING.JTextField(self.configFile['Main Script']['LD']['LO'])
        a6.setName('location')
        self.panelWidgets['LO'] = a6

        # a8 = PSE.JAVX_SWING.JTextField(self.configFile['Main Script']['LD']['YR'])
        a8 = PSE.JAVX_SWING.JTextField(PSE.JMRI.jmrit.operations.setup.Setup.getYearModeled())
        a8.setName('yearModeled')
        self.panelWidgets['YR'] = a8

        inputGrid.add(a1)
        inputGrid.add(a2)
        inputGrid.add(a3)
        inputGrid.add(a4)
        inputGrid.add(a5)
        inputGrid.add(a6)
        inputGrid.add(a7)
        inputGrid.add(a8)

        jPlusPanel.add(inputGrid)
        jPlusPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,5)))

        updatePanel = PSE.JAVX_SWING.JPanel()
        
        upButton = self.updateButton()
        self.controlWidgets['UP'] = upButton

        flag = self.configFile['Main Script']['CP']['EH']
        message = PSE.getBundleItem('Use Extended Header')
        useExtended = PSE.JAVX_SWING.JCheckBox(message, flag)
        useExtended.setName('useExtended')
        self.controlWidgets['UX'] = useExtended

        updatePanel.add(upButton)
        updatePanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        updatePanel.add(useExtended)

        jPlusPanel.add(updatePanel)

        guiFrame = self.getGuiFrame()
        guiFrame.add(jPlusPanel)
        
        return guiFrame

    def updateButton(self):
        """
        The *.setName value is the name of the action for the widget.
        """

        upButton = PSE.JAVX_SWING.JButton()
        upButton.setText(PSE.getBundleItem('Update'))
        upButton.setName('update')

        return upButton

    def guiWidgetGetter(self):

        allWidgets = {}
        allWidgets['control'] = self.controlWidgets
        allWidgets['panel'] = self.panelWidgets

        return allWidgets

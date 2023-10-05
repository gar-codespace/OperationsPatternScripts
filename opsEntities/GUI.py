# coding=utf-8
# © 2023 Greg Ritacco

"""
All the OPS GUI items are made here.
"""

from opsEntities import PSE
from opsBundle import Bundle

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901


class PluginGUI:
    """
    All the GUI elements.
    """

    def __init__(self):

        self.psLog = PSE.LOGGING.getLogger('OPS.Main.View')

        self.configFile = PSE.readConfigFile()

        self.psFrame = PSE.JMRI.util.JmriJFrame()

        """Dealers choice, jPanel or Box."""
        # self.subroutinePanel = PSE.JAVX_SWING.JPanel()
        # self.subroutinePanel.setLayout(PSE.JAVX_SWING.BoxLayout( self.subroutinePanel, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        self.subroutinePanel = PSE.JAVX_SWING.Box(PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)
        self.subroutinePanel.setName('subroutinePanel')

        self.itemText = ''
        self.itemName = ''
        self.subroutineName = ''
        self.psPluginMenuItems = []
        self.psPluginSubroutineMenuItems = []

        self._makeSubroutinesPanel()
        self._makeScrollPanel()
        self._makePatternScriptsGUI()

        return

    def _makeSubroutinesPanel(self):
        """
        The subroutines are added to self.subroutinePanel.
        """

        for subroutine in PSE.getSubroutineDirs():

            subroutineName = PSE.SUBROUTINE_DIR + '.' + subroutine + '.Controller'
            package = PSE.IM(subroutineName)
            startUp = package.StartUp()
            startUp.startUpTasks()
            self.subroutinePanel.add(startUp.getSubroutine())

        return    

    def _makeScrollPanel(self):
        """
        The subroutinePanel is set into a scroll panel.
        """

        self.scrollPanel = PSE.JAVX_SWING.JScrollPane(self.subroutinePanel)
        self.scrollPanel.border = PSE.JAVX_SWING.BorderFactory.createLineBorder(PSE.JAVA_AWT.Color.GRAY)
        self.scrollPanel.setName('scrollPanel')

        return

    def _makePatternScriptsGUI(self):
        """
        This is the Pattern Scripts jFrame.
        """

        self.psLog.debug('_makePatternScriptsGUI')
    # Tools menu item drop-down items
        toolsMenu = PSE.JAVX_SWING.JMenu(PSE.getBundleItem('Tools'))

        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.OptionAction())
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.PrintOptionAction())
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.BuildReportOptionAction())

        for self.subroutineName in PSE.getSubroutineDirs():
            menuItem = self._getSubroutineDropDownItem()
            self.psPluginSubroutineMenuItems.append(menuItem)
            # menuItem.addActionListener(Listeners.dropDownMneuItem)
            toolsMenu.add(menuItem)

        self.itemText = PSE.getBundleItem('Translate Plugin')
        self.itemName =  'ptItemSelected'
        ptMenuItem = self._makeMenuItem()
        self.psPluginMenuItems.append(ptMenuItem)
        toolsMenu.add(ptMenuItem)
        if not Bundle.validateKeyFile():
            ptMenuItem.setEnabled(False)

        self.itemText = PSE.getBundleItem('Edit Config File')
        self.itemName = 'ecItemSelected'
        editConfigMenuItem = self._makeMenuItem()
        self.psPluginMenuItems.append(editConfigMenuItem)
        toolsMenu.add(editConfigMenuItem)

        self.itemText = PSE.getBundleItem('Restart From Default')
        self.itemName = 'rsItemSelected'
        rsMenuItem = self._makeMenuItem()
        self.psPluginMenuItems.append(rsMenuItem)
        toolsMenu.add(rsMenuItem)
    # Help menu item drop-down items
        helpMenu = PSE.JAVX_SWING.JMenu(PSE.getBundleItem('Help'))        

        self.itemText = PSE.getBundleItem('Window Help...')
        self.itemName = 'helpItemSelected'
        helpMenuItem = self._makeMenuItem()
        self.psPluginMenuItems.append(helpMenuItem)
        helpMenu.add(helpMenuItem)

        self.itemText = PSE.getBundleItem('GitHub Web Page')
        self.itemName = 'ghItemSelected'
        gitHubMenuItem = self._makeMenuItem()
        self.psPluginMenuItems.append(gitHubMenuItem)
        helpMenu.add(gitHubMenuItem)

        self.itemText = PSE.getBundleItem('Operations Folder')
        self.itemName = 'ofItemSelected'
        opsFolderMenuItem = self._makeMenuItem()
        self.psPluginMenuItems.append(opsFolderMenuItem)
        helpMenu.add(opsFolderMenuItem)

        self.itemText = PSE.getBundleItem('View Log File')
        self.itemName = 'logItemSelected'
        logMenuItem = self._makeMenuItem()
        self.psPluginMenuItems.append(logMenuItem)
        helpMenu.add(logMenuItem)
    # The jFrame menu bar
        psMenuBar = PSE.JAVX_SWING.JMenuBar()
        psMenuBar.add(toolsMenu)
        psMenuBar.add(PSE.JMRI.jmrit.operations.OperationsMenu())
        psMenuBar.add(PSE.JMRI.util.WindowMenu(self.psFrame))
        psMenuBar.add(helpMenu)
    # Put it all together
        self.psFrame.setName('PatternScriptsFrame')
        self.psFrame.setTitle(PSE.getBundleItem('Pattern Scripts'))
        self.psFrame.setJMenuBar(psMenuBar)
        # self.psFrame.add(self.subroutinePanel)
        self.psFrame.add(self.scrollPanel)
        # self.psFrame.pack()

        return

    def _getSubroutineDropDownItem(self):
        """
        Pattern Scripts/Tools/'Show or Hide <subroutine>'
        """

        menuItem = PSE.JAVX_SWING.JMenuItem()

        if self.configFile[self.subroutineName]['SV']:
            menuText = PSE.getBundleItem('Hide') + ' ' + self.subroutineName        
        else:
            menuText = PSE.getBundleItem('Show') + ' ' + self.subroutineName

        menuItem.setName(self.subroutineName)
        menuItem.setText(menuText)

        return menuItem

    def _makeMenuItem(self):
        """
        Makes all the items for the custom drop-down menus.
        """

        menuItem = PSE.JAVX_SWING.JMenuItem(self.itemText)
        menuItem.setName(self.itemName)

        return menuItem

    def getPsFrame(self):

        return self.psFrame

    def getPsPluginMenuItems(self):

        return self.psPluginMenuItems

    def getSubroutineMenuItems(self):

        return self.psPluginSubroutineMenuItems
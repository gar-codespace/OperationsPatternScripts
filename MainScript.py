"""
Pattern Scripts plugin for JMRI Operations Pro
OPS = Operations Pattern Scripts
Copyright 2021, 2022, 2023 Greg Ritacco
No restrictions on use, but I would appreciate the reference.
"""

import jmri
import sys
from os import path as OS_PATH
# from importlib import import_module as IM

SCRIPT_NAME = 'OperationsPatternScripts.MainScript'
SCRIPT_REV = 20230901
SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b3'

PLUGIN_ROOT = OS_PATH.join(jmri.util.FileUtil.getPreferencesPath(), SCRIPT_DIR)
sys.path.append(PLUGIN_ROOT)
from opsEntities import PSE

PSE.PLUGIN_ROOT = PLUGIN_ROOT
PSE.SCRIPT_DIR = SCRIPT_DIR
PSE.SUBROUTINE_DIR = 'Subroutines_Activated'
PSE.JMRI = jmri
PSE.SYS = sys
PSE.OS_PATH = OS_PATH
# PSE.IM = IM

from opsEntities import Listeners
from opsBundle import Bundle

PSE.validateConfigFile()

configFile = PSE.readConfigFile()
encodingSelection = configFile['Main Script']['CP']['ES']
PSE.ENCODING = configFile['Main Script']['CP']['EO'][encodingSelection] # ['EO'] is encoding options

def buildThePlugin(view):
    """
    Mini controller.
    Build and display the PS Plugin Window.
    Called by:
    patternScriptsButtonAction
    restartThePlugin
    """

    view.makeSubroutinesPanel()
    view.makeScrollPanel()
    view.makePatternScriptsGUI()

    for menuItem in view.getPsPluginMenuItems():
        menuItem.addActionListener(getattr(Listeners, menuItem.getName()))

    view.OpenPatternScriptsWindow()

    return

def restartThePlugin():

    _psLog = PSE.LOGGING.getLogger('OPS.Main.restartThePlugin')
    
    PSE.closeWindowByName('patternScriptsWindow')

    buildThePlugin(View())

    _psLog.info('Pattern Scripts plugin restarted')

    return

class View:
    """
    Includes all the GUI elements.
    """

    def __init__(self):

        self.psLog = PSE.LOGGING.getLogger('OPS.Main.View')

        self.configFile = PSE.readConfigFile()

        self.psWindow = PSE.JMRI.util.JmriJFrame()

        """Dealers choice, jPanel or Box."""
        # self.subroutinePanel = PSE.JAVX_SWING.JPanel()
        # self.subroutinePanel.setLayout(PSE.JAVX_SWING.BoxLayout( self.subroutinePanel, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        self.subroutinePanel = PSE.JAVX_SWING.Box(PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)
        self.subroutinePanel.setName('subroutinePanel')

        self.itemText = ''
        self.itemName = ''
        self.subroutineName = ''
        self.psPluginMenuItems = []

        return

    def makeSubroutinesPanel(self):
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

    def makeScrollPanel(self):
        """
        The subroutinePanel is set into a scroll panel.
        """

        self.scrollPanel = PSE.JAVX_SWING.JScrollPane(self.subroutinePanel)
        self.scrollPanel.border = PSE.JAVX_SWING.BorderFactory.createLineBorder(PSE.JAVA_AWT.Color.GRAY)
        self.scrollPanel.setName('scrollPanel')

        return

    def getSubroutineDropDownItem(self):
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

    def makePatternScriptsGUI(self):
        """
        This is the Pattern Scripts jFrame.
        """

        self.psLog.debug('makePatternScriptsGUI')
    # Tools menu item drop-down items
        toolsMenu = PSE.JAVX_SWING.JMenu(PSE.getBundleItem('Tools'))

        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.OptionAction())
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.PrintOptionAction())
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.BuildReportOptionAction())

        for self.subroutineName in PSE.getSubroutineDirs():
            menuItem = self.getSubroutineDropDownItem()
            menuItem.addActionListener(Listeners.dropDownMenuItem)
            toolsMenu.add(menuItem)

        self.itemText = PSE.getBundleItem('Translate Plugin')
        self.itemName =  'ptItemSelected'
        ptMenuItem = self.makeMenuItem()
        self.psPluginMenuItems.append(ptMenuItem)
        toolsMenu.add(ptMenuItem)
        if not Bundle.validateKeyFile():
            ptMenuItem.setEnabled(False)

        self.itemText = PSE.getBundleItem('Edit Config File')
        self.itemName = 'ecItemSelected'
        editConfigMenuItem = self.makeMenuItem()
        self.psPluginMenuItems.append(editConfigMenuItem)
        toolsMenu.add(editConfigMenuItem)

        self.itemText = PSE.getBundleItem('Restart From Default')
        self.itemName = 'rsItemSelected'
        rsMenuItem = self.makeMenuItem()
        self.psPluginMenuItems.append(rsMenuItem)
        toolsMenu.add(rsMenuItem)
    # Help menu item drop-down items
        helpMenu = PSE.JAVX_SWING.JMenu(PSE.getBundleItem('Help'))        

        self.itemText = PSE.getBundleItem('Window Help...')
        self.itemName = 'helpItemSelected'
        helpMenuItem = self.makeMenuItem()
        self.psPluginMenuItems.append(helpMenuItem)
        helpMenu.add(helpMenuItem)

        self.itemText = PSE.getBundleItem('GitHub Web Page')
        self.itemName = 'ghItemSelected'
        gitHubMenuItem = self.makeMenuItem()
        self.psPluginMenuItems.append(gitHubMenuItem)
        helpMenu.add(gitHubMenuItem)

        self.itemText = PSE.getBundleItem('Operations Folder')
        self.itemName = 'ofItemSelected'
        opsFolderMenuItem = self.makeMenuItem()
        self.psPluginMenuItems.append(opsFolderMenuItem)
        helpMenu.add(opsFolderMenuItem)

        self.itemText = PSE.getBundleItem('View Log File')
        self.itemName = 'logItemSelected'
        logMenuItem = self.makeMenuItem()
        self.psPluginMenuItems.append(logMenuItem)
        helpMenu.add(logMenuItem)
    # The jFrame menu bar
        psMenuBar = PSE.JAVX_SWING.JMenuBar()
        psMenuBar.add(toolsMenu)
        psMenuBar.add(PSE.JMRI.jmrit.operations.OperationsMenu())
        psMenuBar.add(PSE.JMRI.util.WindowMenu(self.psWindow))
        psMenuBar.add(helpMenu)
    # Put it all together
        self.psWindow.setName('patternScriptsWindow')
        self.psWindow.setTitle(PSE.getBundleItem('Pattern Scripts'))
        self.psWindow.setJMenuBar(psMenuBar)
        # self.psWindow.add(self.subroutinePanel)
        self.psWindow.add(self.scrollPanel)
        # self.psWindow.pack()
        configPanel = PSE.readConfigFile('Main Script')['CP']
        self.psWindow.setSize(configPanel['PW'], configPanel['PH'])
        self.psWindow.setLocation(configPanel['PX'], configPanel['PY'])

        return

    def OpenPatternScriptsWindow(self):

        self.psWindow.addWindowListener(Listeners.PatternScriptsWindow())
        self.psWindow.setVisible(True)

        return

    def getPsPluginMenuItems(self):

        return self.psPluginMenuItems

    def makeMenuItem(self):
        """
        Makes all the items for the custom drop-down menus.
        """

        menuItem = PSE.JAVX_SWING.JMenuItem(self.itemText)
        menuItem.setName(self.itemName)

        return menuItem
    

class Controller(PSE.JMRI.jmrit.automat.AbstractAutomaton):

    def init(self):

        PSE.makeReportFolders()

        logFileTarget = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'buildstatus', 'PatternScriptsLog.txt')

        self.logger = PSE.Logger(logFileTarget)
        self.logger.startLogger('OPS')

        self.menuItemList = []

        return

    def addPatternScriptsButton(self):
        """
        The Pattern Scripts button on the PanelPro frame.
        """

        psButton = PSE.JAVX_SWING.JButton()
        psButton.setName('psButton')
        psButton.setText(PSE.getBundleItem('Pattern Scripts'))
        psButton.actionPerformed = self.patternScriptsButtonAction
        
        PSE.APPS.Apps.buttonSpace().add(psButton)
        PSE.APPS.Apps.buttonSpace().revalidate()

        return

    def patternScriptsButtonAction(self, MOUSE_CLICKED):

        self.psLog.debug(MOUSE_CLICKED)

        buildThePlugin(View())

        return

    def handle(self):

        startTime = PSE.TIME.time()
        self.psLog = PSE.LOGGING.getLogger('OPS.Main.Controller')
        self.logger.initialLogMessage(self.psLog)

        Bundle.setupBundle()

        self.addPatternScriptsButton()

        PSE.openSystemConsole()

        self.psLog.info('Current Pattern Scripts directory: ' + PLUGIN_ROOT)
        print('Current Pattern Scripts directory: ' + PLUGIN_ROOT)

        runTime = PSE.TIME.time() - startTime
        self.psLog.info('Main script run time (sec): ' + str(round(runTime, 4)))
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return False

if __name__ == "__builtin__":
    Controller().start()
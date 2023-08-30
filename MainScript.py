"""
Pattern Scripts plugin for JMRI Operations Pro
OPS = Operations Pattern Scripts
Copyright 2021, 2022, 2023 Greg Ritacco
No restrictions on use, but I would appreciate the reference.
"""

import jmri
import sys
from os import path as OS_PATH

SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b1'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b2'

PLUGIN_ROOT = OS_PATH.join(jmri.util.FileUtil.getPreferencesPath(), SCRIPT_DIR)
sys.path.append(PLUGIN_ROOT)
from opsEntities import PSE

PSE.PLUGIN_ROOT = PLUGIN_ROOT
PSE.SCRIPT_DIR = SCRIPT_DIR
PSE.JMRI = jmri
PSE.SYS = sys
PSE.OS_PATH = OS_PATH

from opsEntities import Listeners
from opsBundle import Bundle

SCRIPT_NAME = 'OperationsPatternScripts.MainScript'
SCRIPT_REV = 20230201

PSE.validateConfigFile()

configFile = PSE.readConfigFile()
encodingSelection = configFile['Main Script']['CP']['ES']
PSE.ENCODING = configFile['Main Script']['CP']['EO'][encodingSelection]
# ['EO'] is encoding options

def buildThePlugin(view):
    """
    Mini controller to build and display the PS Plugin Window.
    Called by:
    patternScriptsButtonAction
    """

    view.makeSubroutinesPanel()
    # view.makeScrollPanel()
    view.makePatternScriptsWindow()

    for menuItem in view.getPsPluginMenuItems():
        menuItem.removeActionListener(getattr(Listeners, menuItem.getName()))
        menuItem.addActionListener(getattr(Listeners, menuItem.getName()))

    view.OpenPatternScriptsWindow()

    return

def restartThePlugin():

    _psLog = PSE.LOGGING.getLogger('OPS.Main.restartThePlugin')
    
    PSE.closeWindowByName('patternScriptsWindow')

    Bundle.setupBundle()

    buildThePlugin(View())

    psButton = PSE.getPsButton()

    psButton.setText(PSE.getBundleItem('Pattern Scripts'))

    PSE.APPS.Apps.buttonSpace().revalidate()

    _psLog.info('Pattern Scripts plugin restarted')

    return

class View:

    def __init__(self):

        self.psLog = PSE.LOGGING.getLogger('OPS.Main.View')

        self.configFile = PSE.readConfigFile()

        self.psWindow = PSE.JMRI.util.JmriJFrame()

        """Dealers choice, jPanel or Box."""
        # self.subroutinePanel = PSE.JAVX_SWING.JPanel()
        # self.subroutinePanel.setLayout(PSE.JAVX_SWING.BoxLayout( self.subroutinePanel, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        self.subroutinePanel = PSE.JAVX_SWING.Box(PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)
        self.subroutinePanel.setName('subroutinePanel')

        self.psPluginMenuItems = []
        self.subroutineMenuItems = []

        return

    def makeSubroutinesPanel(self):
        """
        The subroutines are added to self.subroutinePanel.
        """

        for subroutine in PSE.getSubroutineDirs():
            subroutineName = 'Subroutines.' + subroutine
            package = __import__(subroutineName, fromlist=['Controller'], level=-1)
            startUp = package.Controller.StartUp()
            startUp.startUpTasks()
            self.subroutinePanel.add(startUp.getSubroutine())
            # if self.configFile[subroutine]['SV']:
            #     self.subroutinePanel.add(startUp.getSubroutineFrame())

        return    

    def makeScrollPanel(self):
        """
        Currently not implemented.
        """

        self.scrollPanel = PSE.JAVX_SWING.JScrollPane(self.subroutinePanel)
        self.scrollPanel.border = PSE.JAVX_SWING.BorderFactory.createLineBorder(PSE.JAVA_AWT.Color.GRAY)
        self.scrollPanel.setName('scrollPanel')

        return

    def makePatternScriptsWindow(self):

        self.psLog.debug('makePatternScriptsWindow')

        toolsMenu = PSE.JAVX_SWING.JMenu(PSE.getBundleItem('Tools'))

        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.OptionAction())
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.PrintOptionAction())
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.BuildReportOptionAction())

        for subroutine in PSE.getSubroutineDirs():
            xModule = 'Subroutines.' + subroutine
            package = __import__(xModule, fromlist=['Controller'], level=-1)
            menuItem = package.Controller.getSubroutineDropDownItem()
            toolsMenu.add(menuItem)

        itemText, itemName = self.setPtDropDownText()
        ptMenuItem = self.makeMenuItem(itemText, itemName)
        self.psPluginMenuItems.append(ptMenuItem)
        toolsMenu.add(ptMenuItem)
        if not Bundle.validateKeyFile():
            ptMenuItem.setEnabled(False)

        itemText, itemName = self.setEcDropDownText()
        editConfigMenuItem = self.makeMenuItem(itemText, itemName)
        self.psPluginMenuItems.append(editConfigMenuItem)
        toolsMenu.add(editConfigMenuItem)

        itemText, itemName = self.setRsDropDownText()
        rsMenuItem = self.makeMenuItem(itemText, itemName)
        self.psPluginMenuItems.append(rsMenuItem)
        toolsMenu.add(rsMenuItem)

        helpMenu = PSE.JAVX_SWING.JMenu(PSE.getBundleItem('Help'))        

        itemText, itemName = self.setHmDropDownText()
        helpMenuItem = self.makeMenuItem(itemText, itemName)
        self.psPluginMenuItems.append(helpMenuItem)
        helpMenu.add(helpMenuItem)

        itemText, itemName = self.setGhDropDownText()
        gitHubMenuItem = self.makeMenuItem(itemText, itemName)
        self.psPluginMenuItems.append(gitHubMenuItem)
        helpMenu.add(gitHubMenuItem)

        itemText, itemName = self.setOfDropDownText()
        opsFolderMenuItem = self.makeMenuItem(itemText, itemName)
        self.psPluginMenuItems.append(opsFolderMenuItem)
        helpMenu.add(opsFolderMenuItem)

        itemText, itemName = self.setLmDropDownText()
        logMenuItem = self.makeMenuItem(itemText, itemName)
        self.psPluginMenuItems.append(logMenuItem)
        helpMenu.add(logMenuItem)

        psMenuBar = PSE.JAVX_SWING.JMenuBar()
        psMenuBar.add(toolsMenu)
        psMenuBar.add(PSE.JMRI.jmrit.operations.OperationsMenu())
        psMenuBar.add(PSE.JMRI.util.WindowMenu(self.psWindow))
        psMenuBar.add(helpMenu)

        configPanel = PSE.readConfigFile('Main Script')['CP']
        self.psWindow.setName('patternScriptsWindow')
        self.psWindow.setTitle(PSE.getBundleItem('Pattern Scripts'))

        self.psWindow.addWindowListener(Listeners.PatternScriptsWindow())
        self.psWindow.setJMenuBar(psMenuBar)
        # self.psWindow.add(self.scrollPanel)
        self.psWindow.add(self.subroutinePanel)
        # self.psWindow.pack()
        self.psWindow.setSize(configPanel['PW'], configPanel['PH'])
        self.psWindow.setLocation(configPanel['PX'], configPanel['PY'])

        return

    def OpenPatternScriptsWindow(self):

        self.psWindow.setVisible(True)

        return

    def getPsPluginMenuItems(self):

        return self.psPluginMenuItems

    def makeMenuItem(self, itemText, itemName):
        """
        Makes all the items for the custom drop down menus.
        """

        menuItem = PSE.JAVX_SWING.JMenuItem(itemText)
        menuItem.setName(itemName)

        return menuItem

    def setPtDropDownText(self):
        """
        itemMethod - Set the drop down text for the Translate Plugin item.
        """

        menuText = PSE.getBundleItem('Translate Plugin')        

        return menuText, 'ptItemSelected'

    def setRsDropDownText(self):
        """
        itemMethod - Set the drop down text for the Restart From Default item.
        """

        menuText = PSE.getBundleItem('Restart From Default') 
        return menuText, 'rsItemSelected'

    def setHmDropDownText(self):
        """
        itemMethod - Set the drop down text for the Log menu item.
        """

        menuText = PSE.getBundleItem('Window Help...') 

        return menuText, 'helpItemSelected'

    def setLmDropDownText(self):
        """
        itemMethod - Set the drop down text for the Log menu item.
        """

        menuText = PSE.getBundleItem('View Log File')

        return menuText, 'logItemSelected'

    def setGhDropDownText(self):
        """
        itemMethod - Set the drop down text for the gitHub page item.
        """

        menuText = PSE.getBundleItem('GitHub Web Page')

        return menuText, 'ghItemSelected'

    def setEcDropDownText(self):
        """
        itemMethod - Set the drop down text for the edit config file item.
        """

        menuText = PSE.getBundleItem('Edit Config File')

        return menuText, 'ecItemSelected'

    def setOfDropDownText(self):
        """
        itemMethod - Set the drop down text for the operations folder item.
        """

        menuText = PSE.getBundleItem('Operations Folder')

        return menuText, 'ofItemSelected'


class Controller(PSE.JMRI.jmrit.automat.AbstractAutomaton):

    def init(self):
        """
        """

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
        psButton.actionPerformed = self.patternScriptsButtonAction
        psButton.setName('psButton')
        psButton.setText(PSE.getBundleItem('Pattern Scripts'))
        
        PSE.APPS.Apps.buttonSpace().add(psButton)
        PSE.APPS.Apps.buttonSpace().revalidate()

        return

    def patternScriptsButtonAction(self, MOUSE_CLICKED):

        self.psLog.debug(MOUSE_CLICKED)

        PSE.validateConfigFile()

        Bundle.setupBundle()

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
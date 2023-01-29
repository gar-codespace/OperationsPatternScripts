"""
Pattern Scripts plugin for JMRI Operations Pro
OPS = Operations Pattern Scripts
Copyright 2021, 2022 Greg Ritacco
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

import java.awt
import javax.swing
import time
PSE.JAVA_AWT = java.awt
PSE.JAVX_SWING = javax.swing
PSE.TIME = time

from opsEntities import Listeners
from opsBundle import Bundle

SCRIPT_NAME = 'OperationsPatternScripts.MainScript'
SCRIPT_REV = 20230101

PSE.validateConfigFile()
PSE.ENCODING = PSE.readConfigFile('Main Script')['CP']['SE']

Bundle.BUNDLE_DIR = OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle')


def buildThePlugin(view):
    """Mini controller to build and display the PS Plugin Window.
        Called by:
        restartThePlugin
        patternScriptsButtonAction
        """

    view.makeSubroutinePanel()
    view.makeScrollPanel()
    view.makePatternScriptsWindow()

    for menuItem in view.getPsPluginMenuItems():
        menuItem.removeActionListener(getattr(Listeners, menuItem.getName()))
        menuItem.addActionListener(getattr(Listeners, menuItem.getName()))

    view.OpenPatternScriptsWindow()

    return

def restartThePlugin():
    """ """

    _psLog = PSE.LOGGING.getLogger('OPS.Main.restartThePlugin')
    
    PSE.closeOpsWindows('patternScriptsWindow')

    Bundle.setupBundle()

    buildThePlugin(View())

    psButton = PSE.getPsButton()
    psButton.setText(PSE.BUNDLE[u'Pattern Scripts'])
    PSE.APPS.Apps.buttonSpace().revalidate()

    _psLog.info('Pattern Scripts plugin restarted')

    return

class View:

    def __init__(self):

        self.psLog = PSE.LOGGING.getLogger('OPS.Main.View')

        self.cpConfig = PSE.readConfigFile('Main Script')['CP']

        self.psWindow = PSE.JMRI.util.JmriJFrame()

        """Dealers choice, jPanel or Box."""
        # self.subroutinePanel = PSE.JAVX_SWING.JPanel()
        # self.subroutinePanel.setLayout(PSE.JAVX_SWING.BoxLayout( self.subroutinePanel, PSE.JAVX_SWING.BoxLayout.PAGE_AXIS))
        self.subroutinePanel = PSE.JAVX_SWING.Box(PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)

        self.psPluginMenuItems = []
        self.subroutineMenuItems = []

        return

    def makeSubroutinePanel(self):
        """Add the subroutines to this."""

        self.subroutinePanel.setName('subroutinePanel')

        self.subroutinePanel = PSE.addActiveSubroutines(self.subroutinePanel)

        return

    # def makeSubroutineMenuItems(self):
    #     """ """

    #     menuItemList = []

    #     for subroutine in PSE.getSubroutineDirs():
    #         xModule = 'Subroutines.' + subroutine
    #         package = __import__(xModule, fromlist=['Controller', 'Listeners'], level=-1)
    #         menuText, itemName = package.Controller.setDropDownText()
    #         menuItem = self.makeMenuItem(menuText, itemName)
    #         menuItem.addActionListener(package.Listeners.actionListener)

    #         menuItemList.append(menuItem)








        # for include in self.cpConfig['IL']:
        #     package = __import__(include, fromlist=['Listeners'])

        #     menuText, itemName = package.Controller.setDropDownText()
        #     menuItem = self.makeMenuItem(menuText, itemName)
        #     menuItem.addActionListener(package.Listeners.actionListener)

        #     menuItemList.append(menuItem)

        return menuItemList

    def makeScrollPanel(self):

        self.scrollPanel = PSE.JAVX_SWING.JScrollPane(self.subroutinePanel)
        self.scrollPanel.border = PSE.JAVX_SWING.BorderFactory.createLineBorder(PSE.JAVA_AWT.Color.GRAY)
        self.scrollPanel.setName('scrollPanel')

        return

    def makePatternScriptsWindow(self):

        self.psLog.debug('makePatternScriptsWindow')

        toolsMenu = PSE.JAVX_SWING.JMenu(PSE.BUNDLE[u'Tools'])
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

        helpMenu = PSE.JAVX_SWING.JMenu(PSE.BUNDLE[u'Help'])

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
        self.psWindow.setTitle(PSE.BUNDLE[u'Pattern Scripts'])
        self.psWindow.addWindowListener(Listeners.PatternScriptsWindow())
        self.psWindow.setJMenuBar(psMenuBar)
        self.psWindow.add(self.scrollPanel)
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
        """Makes all the items for the custom drop down menus."""

        menuItem = PSE.JAVX_SWING.JMenuItem(itemText)
        menuItem.setName(itemName)

        return menuItem

    def setPtDropDownText(self):
        """itemMethod - Set the drop down text for the Translate Plugin item."""

        menuText = PSE.BUNDLE[u'Translate Plugin']

        return menuText, 'ptItemSelected'

    def setRsDropDownText(self):
        """itemMethod - Set the drop down text for the Restart From Default item."""

        menuText = PSE.BUNDLE[u'Restart From Default']

        return menuText, 'rsItemSelected'

    def setHmDropDownText(self):
        """itemMethod - Set the drop down text for the Log menu item."""

        menuText = PSE.BUNDLE[u'Window Help...']

        return menuText, 'helpItemSelected'

    def setLmDropDownText(self):
        """itemMethod - Set the drop down text for the Log menu item."""

        menuText = PSE.BUNDLE[u'View Log File']

        return menuText, 'logItemSelected'

    def setGhDropDownText(self):
        """itemMethod - Set the drop down text for the gitHub page item."""

        menuText = PSE.BUNDLE[u'GitHub Web Page']

        return menuText, 'ghItemSelected'

    def setEcDropDownText(self):
        """itemMethod - Set the drop down text for the edit config file item."""

        menuText = PSE.BUNDLE[u'Edit Config File']

        return menuText, 'ecItemSelected'

    def setOfDropDownText(self):
        """itemMethod - Set the drop down text for the operations folder item."""

        menuText = PSE.BUNDLE[u'Operations Folder']

        return menuText, 'ofItemSelected'


class Controller(PSE.JMRI.jmrit.automat.AbstractAutomaton):

    def init(self):
        """ """

        PSE.makeBuildStatusFolder()


        logFileTarget = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'buildstatus', 'PatternScriptsLog.txt')

        self.logger = PSE.Logger(logFileTarget)
        self.logger.startLogger('OPS')


        # self.configFile = PSE.readConfigFile()

        self.menuItemList = []

        return

    def addPatternScriptsButton(self):
        """The Pattern Scripts button on the PanelPro frame."""

        psButton = PSE.JAVX_SWING.JButton()
        psButton.actionPerformed = self.patternScriptsButtonAction
        psButton.setName('psButton')
        PSE.APPS.Apps.buttonSpace().add(psButton)

        psButton.setText(PSE.BUNDLE[u'Pattern Scripts'])
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

        PSE.makeReportFolders()

        Bundle.setupBundle()

        PSE.validateSubroutines()

        PSE.remoteCalls('startupCalls')

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
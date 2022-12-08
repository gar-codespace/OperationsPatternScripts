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
SCRIPT_REV = 20221010

PSE.ENCODING = PSE.readConfigFile('CP')['SE']

Bundle.BUNDLE_DIR = OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle')


class View:

    def __init__(self):

        self.psLog = PSE.LOGGING.getLogger('OPS.Main.View')

        self.cpSettings = PSE.readConfigFile('CP')

        self.psPluginMenuItems = []
        self.subroutineMenuItems = []

        return

    def makePluginPanel(self):
        """Dealers choice, jPanel or Box."""

        # pluginPanel = PSE.JAVX_SWING.JPanel()
        pluginPanel = PSE.JAVX_SWING.Box(PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)

        return pluginPanel

    def makePatternScriptsPanel(self, pluginPanel):

        pluginPanel.setName('OPS Plugin Panel')

        for subroutine in self.makeSubroutineList():
            pluginPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,10)))
            pluginPanel.add(subroutine)

        return pluginPanel

    def makeSubroutineList(self):
        """Add all the subroutines in ['CP']['IL'], activate if ['CP']['*Subroutine'] is true."""

        subroutineList = []
        controlPanelConfig = PSE.readConfigFile('CP')
        for include in controlPanelConfig['IL']:
            xModule = __import__(include, fromlist=['Controller', 'Listeners'])
            menuText, itemName = xModule.Controller.setDropDownText()
            menuItem = self.makeMenuItem(menuText, itemName)
            menuItem.addActionListener(xModule.Listeners.actionListener)
            self.subroutineMenuItems.append(menuItem)
            if controlPanelConfig[include]:
                startUp = xModule.Controller.StartUp()
                subroutineFrame = startUp.makeSubroutineFrame()
                subroutineList.append(subroutineFrame)
                self.psLog.info(include + ' subroutine added to control panel')

        return subroutineList

    def makeScrollPanel(self, pluginPanel):

        scrollPanel = PSE.JAVX_SWING.JScrollPane(pluginPanel)
        scrollPanel.border = PSE.JAVX_SWING.BorderFactory.createLineBorder(PSE.JAVA_AWT.Color.GRAY)

        return scrollPanel

    def getPsPluginMenuItems(self):

        return self.psPluginMenuItems

    def makePatternScriptsWindow(self, scrollPanel):

        self.psLog.debug('makePatternScriptsWindow')

        uniqueWindow = PSE.JMRI.util.JmriJFrame()

        toolsMenu = PSE.JAVX_SWING.JMenu(PSE.BUNDLE[u'Tools'])
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.OptionAction())
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.PrintOptionAction())
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.BuildReportOptionAction())

        for menuItem in self.subroutineMenuItems:
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
        psMenuBar.add(PSE.JMRI.util.WindowMenu(uniqueWindow))
        psMenuBar.add(helpMenu)

        configPanel = PSE.readConfigFile('CP')
        uniqueWindow.setName('patternScriptsWindow')
        uniqueWindow.setTitle(PSE.BUNDLE[u'Pattern Scripts'])
        uniqueWindow.addWindowListener(Listeners.PatternScriptsWindow())
        uniqueWindow.setJMenuBar(psMenuBar)
        uniqueWindow.add(scrollPanel)
        # uniqueWindow.pack()
        uniqueWindow.setSize(configPanel['PW'], configPanel['PH'])
        uniqueWindow.setLocation(configPanel['PX'], configPanel['PY'])
        uniqueWindow.setVisible(True)

        return

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

        self.menuItemList = []

        return

    def validatePatternConfig(self):
        """To be reworked when mergeConfigFiles() is implemented."""

        if not PSE.validateConfigFileVersion():
            PSE.mergeConfigFiles()
            # self.psLog.info('Previous PatternConfig.json merged with new')
            PSE.writeNewConfigFile()
            self.psLog.warning('New PatternConfig.json file created for this profile')

        return

    def addPatternScriptsButton(self):
        """The Pattern Scripts button on the PanelPro frame."""

        psButton = PSE.JAVX_SWING.JButton()
        psButton.setText(PSE.BUNDLE[u'Pattern Scripts'])
        psButton.setName('psButton')

        psButton.actionPerformed = Listeners.patternScriptsButtonAction
        PSE.APPS.Apps.buttonSpace().add(psButton)
        PSE.APPS.Apps.buttonSpace().revalidate()

        return

    def handle(self):

        startTime = PSE.TIME.time()
        self.psLog = PSE.LOGGING.getLogger('OPS.Main.Controller')
        self.logger.initialLogMessage(self.psLog)

        self.validatePatternConfig()

        Bundle.validatePluginBundle()
        PSE.BUNDLE = Bundle.getBundleForLocale()
        Bundle.validateHelpBundle()
        PSE.CreateStubFile().make()
        Bundle.makeHelpPage()

        PSE.makeReportFolders()
        # PSE.CreateStubFile().make()

        if PSE.readConfigFile()['CP']['AP']:
            self.addPatternScriptsButton()

        PSE.openSystemConsole()

        self.psLog.info('Current Pattern Scripts directory: ' + PLUGIN_ROOT)
        runTime = PSE.TIME.time() - startTime
        self.psLog.info('Main script run time (sec): ' + str(round(runTime, 4)))
        print('Current Pattern Scripts directory: ' + PLUGIN_ROOT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return False

if __name__ == "__builtin__":
    Controller().start()

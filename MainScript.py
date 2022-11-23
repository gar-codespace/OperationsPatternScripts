# © 2021, 2022 Greg Ritacco

"""
Pattern Scripts plugin for JMRI Operations Pro
OPS = Operations Pattern Scripts
© 2021, 2022 Greg Ritacco
No restrictions on use, but I would appreciate the reference.
"""

import jmri
import java.awt
import javax.swing
import time

import sys
from os import path as OS_PATH

SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b1'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b2'

PLUGIN_ROOT = OS_PATH.join(jmri.util.FileUtil.getPreferencesPath(), SCRIPT_DIR)

sys.path.append(PLUGIN_ROOT)
from opsEntities import PSE

PSE.JMRI = jmri
PSE.JAVA_AWT = java.awt
PSE.JAVX_SWING = javax.swing
PSE.TIME = time
PSE.SYS = sys
PSE.PLUGIN_ROOT = PLUGIN_ROOT

from opsEntities import Listeners
from opsBundle import Bundle

SCRIPT_NAME = 'OperationsPatternScripts.MainScript'
SCRIPT_REV = 20221010

PSE.ENCODING = PSE.readConfigFile('CP')['SE']

Bundle.BUNDLE_DIR = OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle')
# Bundle.validatePluginBundle()
# PSE.BUNDLE = Bundle.getBundleForLocale()
PSE.BUNDLE = {}


def validatePatternConfig():
    """To be reworked when mergeConfigFiles() is implemented."""

    if not PSE.validateConfigFileVersion():
        PSE.mergeConfigFiles()
        self.psLog.info('Previous PatternConfig.json merged with new')
        PSE.writeNewConfigFile()
        self.psLog.warning('New PatternConfig.json file created for this profile')

    return


class View:

    def __init__(self):

        self.psLog = PSE.LOGGING.getLogger('OPS.Main.View')

        self.cpSettings = PSE.readConfigFile('CP')

        self.psPluginMenuItems = []
        self.subroutineMenuItems = []

        return

    def makePsButton(self):

        psButton = PSE.JAVX_SWING.JButton()
        psButton.setText(PSE.BUNDLE[u'Pattern Scripts'])
        psButton.setName('psButton')

        return psButton

    def makePluginPanel(self):
        """Dealers choice, jPanel or Box."""

        # pluginPanel = PSE.JAVX_SWING.JPanel()
        pluginPanel = PSE.JAVX_SWING.Box(PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)

        return pluginPanel

    def makePatternScriptsPanel(self, pluginPanel):

        for subroutine in self.makeSubroutineList():
            pluginPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,10)))
            pluginPanel.add(subroutine)
            pluginPanel.setName('OPS Plugin Panel')
        return pluginPanel

    def makeSubroutineList(self):
        """Add all the subroutines in ['CP']['IL'], activate if ['CP']['*Subroutine'] is true."""

        subroutineList = []
        controlPanelConfig = PSE.readConfigFile('CP')
        for include in controlPanelConfig['IL']:
            xModule = __import__(include, fromlist=['Controller'])
            menuText, itemName = xModule.Controller.setDropDownText()
            menuItem = self.makeMenuItem(menuText, itemName)
            menuItem.addActionListener(xModule.Controller.actionListener)
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

        self.trainsTableModel = PSE.JMRI.jmrit.operations.trains.TrainsTableModel()
        self.builtTrainListener = Listeners.BuiltTrain()
        self.trainsTableListener = Listeners.TrainsTable(self.builtTrainListener)

        self.menuItemList = []

        return

    def addPatternScriptsButton(self):
        """The Pattern Scripts button on the PanelPro frame."""

        self.patternScriptsButton = View().makePsButton()
        self.patternScriptsButton.actionPerformed = self.patternScriptsButtonAction
        PSE.APPS.buttonSpace().add(self.patternScriptsButton)
        PSE.APPS.buttonSpace().revalidate()

        return

    def addTrainsTableListener(self):

        self.trainsTableModel.addTableModelListener(self.trainsTableListener)

        return

    def removeTrainsTableListener(self):

        self.trainsTableModel.removeTableModelListener(self.trainsTableListener)

        return

    def addBuiltTrainListener(self):

        trainList = PSE.TM.getTrainsByIdList()
        for train in trainList:
            train.addPropertyChangeListener(self.builtTrainListener)

        return

    def removeBuiltTrainListener(self):

        trainList = PSE.TM.getTrainsByIdList()
        for train in trainList:
            train.removePropertyChangeListener(self.builtTrainListener)

        return

    def patternScriptsButtonAction(self, MOUSE_CLICKED):

        self.psLog.debug(MOUSE_CLICKED)

        self.buildThePlugin()

        return

    def closePsWindow(self):
        """Used by:
            tpItemSelected
            shutdownPlugin
            """

        for frame in PSE.JMRI.util.JmriJFrame.getFrameList():
            if frame.getName() == 'patternScriptsWindow':
                PSE.updateWindowParams(frame)
                PSE.closeSetCarsWindows()

                frame.setVisible(False)
                frame.dispose()

        return

    def buildThePlugin(self):
        """Used by:
            tpItemSelected
            startupPlugin
            patternScriptsButtonAction
            """

        view = View()
        emptyPluginPanel = view.makePluginPanel()
        populatedPluginPanel = view.makePatternScriptsPanel(emptyPluginPanel)
        scrollPanel = view.makeScrollPanel(populatedPluginPanel)
        view.makePatternScriptsWindow(scrollPanel)
        self.menuItemList = view.getPsPluginMenuItems()

        self.addMenuItemListeners()

        return

    def o2oSubroutineListeners(self):

        self.addTrainsTableListener()
        self.addBuiltTrainListener()

        return

    def addMenuItemListeners(self):
        """Use the pull down item names as the attribute to set the
            listener: ptItemSelected, rsItemSelected, logItemSelected, helpItemSelected, Etc.
            Used by:
            buildThePlugin
            """

        for menuItem in self.menuItemList:
            menuItem.addActionListener(getattr(self, menuItem.getName()))

        return

    def ptItemSelected(self, TRANSLATE_PLUGIN_EVENT):
        """menu item-Tools/Translate Plugin"""

        self.psLog.debug(TRANSLATE_PLUGIN_EVENT)

        textBundles = Bundle.getAllTextBundles()
        Bundle.makePluginBundle(textBundles)

        Bundle.makeHelpBundle()
        Bundle.makeHelpPage()

        self.shutdownPlugin()
        self.startupPlugin()

        self.psLog.info('Pattern Scripts plugin translated')
        self.psLog.info('Pattern Scripts plugin restarted')

        return

    def rsItemSelected(self, RESTART_PLUGIN_EVENT):
        """menu item-Tools/Restart Plugin"""

        self.psLog.debug(RESTART_PLUGIN_EVENT)

        PSE.deleteConfigFile()

        self.shutdownPlugin()
        self.startupPlugin()

        self.psLog.info('Pattern Scripts plugin restarted')

        return

    def helpItemSelected(self, OPEN_HELP_EVENT):
        """menu item-Help/Window help..."""

        self.psLog.debug(OPEN_HELP_EVENT)

        stubFileTarget = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getPreferencesPath(), 'jmrihelp', PSE.psLocale()[:2], 'psStub.html')
        stubUri = PSE.JAVA_IO.File(stubFileTarget).toURI()
        if PSE.JAVA_IO.File(stubUri).isFile():
            PSE.JAVA_AWT.Desktop.getDesktop().browse(stubUri)
        else:
            self.psLog.warning('Help file not found')

        return

    def logItemSelected(self, OPEN_LOG_EVENT):
        """menu item-Help/View Log"""

        self.psLog.debug(OPEN_LOG_EVENT)

        patternLog = PSE.makePatternLog()

        logFileTarget = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'buildstatus', 'PatternScriptsLog_temp.txt')

        PSE.genericWriteReport(logFileTarget, patternLog)
        PSE.genericDisplayReport(logFileTarget)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def ghItemSelected(self, OPEN_GH_EVENT):
        """menu item-Help/GitHub Page"""

        self.psLog.debug(OPEN_GH_EVENT)

        ghURL = 'https://github.com/gar-codespace/OperationsPatternScripts'
        PSE.JMRI.util.HelpUtil.openWebPage(ghURL)

        return

    def ecItemSelected(self, OPEN_EC_EVENT):
        """menu item-Help/Edit Config File"""

        self.psLog.debug(OPEN_EC_EVENT)

        configTarget = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'PatternConfig.json')

        if PSE.JAVA_IO.File(configTarget).isFile():
            PSE.genericDisplayReport(configTarget)
        else:
            self.psLog.warning('Not found: ' + configTarget)

        return

    def ofItemSelected(self, OPEN_OF_EVENT):
        """menu item-Help/Operations Folder"""

        self.psLog.debug(OPEN_OF_EVENT)

        opsFolderPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations')

        opsFolder = PSE.JAVA_IO.File(opsFolderPath)
        if opsFolder.exists():
            PSE.JAVA_AWT.Desktop.getDesktop().open(opsFolder)
        else:
            self.psLog.warning('Not found: ' + opsFolderPath)

        return

    def shutdownPlugin(self):
        """Used by:
            ptItemSelected
            rsItemSelected
            ooItemSelected
            """

        self.closePsWindow()

        return

    def startupPlugin(self):
        """Used by:
            ptItemSelected
            rsItemSelected
            ooItemSelected
            """

        PSE.BUNDLE = Bundle.getBundleForLocale()
        PSE.CreateStubFile().make()
        Bundle.makeHelpPage()

        self.buildThePlugin()

        return

    def handle(self):

        startTime = PSE.TIME.time()
        self.psLog = PSE.LOGGING.getLogger('OPS.Main.Controller')
        self.logger.initialLogMessage(self.psLog)

        validatePatternConfig()

        Bundle.validatePluginBundle()
        PSE.BUNDLE = Bundle.getBundleForLocale()
        Bundle.validateHelpBundle()
        PSE.CreateStubFile().make()
        Bundle.makeHelpPage()

        PSE.closeOutputPanel()
        PSE.makeReportFolders()
        PSE.CreateStubFile().make()
        if PSE.readConfigFile()['CP']['o2oSubroutine']:
            self.o2oSubroutineListeners()
        if PSE.readConfigFile()['CP']['AP']:
            self.addPatternScriptsButton()

        PSE.openSystemConsole()

        self.psLog.info('Current Pattern Scripts directory: ' + PLUGIN_ROOT)
        runTime = PSE.TIME.time() - startTime
        self.psLog.info('Main script run time (sec): ' + str(round(runTime, 4)))
        print('Current Pattern Scripts directory: ' + PLUGIN_ROOT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return False

Controller().start()

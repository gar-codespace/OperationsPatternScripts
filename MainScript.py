# © 2021, 2022 Greg Ritacco

"""Pattern Scripts plugin for JMRI Operations Pro"""

import jmri
import java.awt
import javax.swing
import time

from sys import path as sysPath
from os import path as OS_Path
from java.beans import PropertyChangeListener
from apps import Apps

SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b1'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b2'

PLUGIN_ROOT = OS_Path.join(jmri.util.FileUtil.getPreferencesPath(), SCRIPT_DIR)

sysPath.append(PLUGIN_ROOT)
from opsEntities import PSE

PSE.JMRI = jmri
PSE.JAVA_AWT = java.awt
PSE.JAVX_SWING = javax.swing
PSE.TIME = time
PSE.PLUGIN_ROOT = PLUGIN_ROOT

from opsEntities import Listeners
from opsBundle import Bundle
# from o2oSubroutine import BuiltTrainExport

SCRIPT_NAME = 'OperationsPatternScripts.MainScript'
SCRIPT_REV = 20220101

PSE.ENCODING = PSE.readConfigFile('CP')['SE']

Bundle.BUNDLE_DIR = OS_Path.join(PSE.PLUGIN_ROOT, 'opsBundle')
PSE.BUNDLE = Bundle.getBundleForLocale()


# class TrainsTableListener(PSE.JAVX_SWING.event.TableModelListener):
#     """Catches user add or remove train while o2oSubroutine is enabled"""
#
#     def __init__(self, builtTrainListener):
#
#         self.builtTrainListener = builtTrainListener
#
#         return
#
#     def tableChanged(self, TABLE_CHANGE):
#
#         trainList = PSE.TM.getTrainsByIdList()
#         for train in trainList:
#             train.removePropertyChangeListener(self.builtTrainListener)
#     # Does not throw error if there is no listener to remove :)
#             train.addPropertyChangeListener(self.builtTrainListener)
#
#         return

# class BuiltTrainListener(java.beans.PropertyChangeListener):
#     """Starts o2oWorkEventsBuilder on trainBuilt"""
#
#     def propertyChange(self, TRAIN_BUILT):
#
#         if TRAIN_BUILT.propertyName == 'TrainBuilt' and TRAIN_BUILT.newValue:
#
#             o2oWorkEvents = BuiltTrainExport.o2oWorkEventsBuilder()
#             o2oWorkEvents.passInTrain(TRAIN_BUILT.getSource())
#             o2oWorkEvents.start()
#
#         return

# class PatternScriptsWindowListener(PSE.JAVA_AWT.event.WindowListener):
#     """Listener to respond to the plugin window operations.
#         May be expanded in v3.
#         """
#
#     def __init__(self):
#
#         return
#
#     def closeSetCarsWindows(self):
#         """Close all the Set Cars windows when the Pattern Scripts window is closed"""
#
#         for frame in PSE.JMRI.util.JmriJFrame.getFrameList():
#             # frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
#             if frame.getName() == 'setCarsWindow':
#                 frame.setVisible(False)
#                 frame.dispose()
#
#         return
#
#     def getPsButton(self):
#         """Gets the Pattern Scripts button on the PanelPro frame"""
#
#         buttonSpaceComponents = Apps.buttonSpace().getComponents()
#         for component in buttonSpaceComponents:
#             if component.getName() == 'psButton':
#                 return component
#
#     def windowClosed(self, WINDOW_CLOSED):
#
#         # self.closeSetCarsWindows()
#         button = self.getPsButton()
#         button.setEnabled(True)
#         WINDOW_CLOSED.getSource().dispose()
#
#         return
#
#     def windowClosing(self, WINDOW_CLOSING):
#
#         # self.closeSetCarsWindows()
#         updateWindowParams(WINDOW_CLOSING.getSource())
#
#
#         # print(dir(frame))
#         # print(frame.HIDE_ON_CLOSE)
#         WINDOW_CLOSING.getSource().firePropertyChange('windowStateChanged', False, True)
#         WINDOW_CLOSING.getSource().firePropertyChange('windowClosing', False, True)
#         print('windowClosing')
#
#         return
#
#     def windowOpened(self, WINDOW_OPENED):
#
#         button = self.getPsButton()
#         button.setEnabled(False)
#
#         return
#
#     def windowIconified(self, WINDOW_ICONIFIED):
#         return
#     def windowDeiconified(self, WINDOW_DEICONIFIED):
#         return
#     def windowActivated(self, WINDOW_ACTIVATED):
#         return
#     def windowDeactivated(self, WINDOW_DEACTIVATED):
#         return
#
# def updateWindowParams(window):
#
#     configPanel = PSE.readConfigFile()
#     configPanel['CP'].update({'PH': window.getHeight()})
#     configPanel['CP'].update({'PW': window.getWidth()})
#     configPanel['CP'].update({'PX': window.getX()})
#     configPanel['CP'].update({'PY': window.getY()})
#     PSE.writeConfigFile(configPanel)
#
#     return

class Model:

    def __init__(self):

        self.psLog = PSE.LOGGING.getLogger('OPS.Main.Model')

        return

    def validatePatternConfig(self):
        """To be reworked in v3"""

        if not PSE.validateConfigFileVersion():
            PSE.mergeConfigFiles()
            self.psLog.info('Previous PatternConfig.json merged with new')
            PSE.writeNewConfigFile()
            self.psLog.warning('New PatternConfig.json file created for this profile')

        return

    def makePatternScriptsPanel(self, pluginPanel):

        for subroutine in self.makeSubroutineList():
            pluginPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(0,10)))
            pluginPanel.add(subroutine)
        return pluginPanel

    def makeSubroutineList(self):
        """for x, y in *.items() sorts the list, this oddball way does not sort the list"""

        subroutineList = []
        controlPanelConfig = PSE.readConfigFile('CP')
        for item in controlPanelConfig['SI']:
            for subroutine, include in item.items(): # The list is sorted, but there is only 1 item
                if include:
                    xModule = __import__(subroutine, fromlist=['Controller'])
                    startUp = xModule.Controller.StartUp()
                    subroutineFrame = startUp.makeSubroutineFrame()
                    subroutineList.append(subroutineFrame)
                    self.psLog.info(subroutine + ' subroutine added to control panel')

        return subroutineList

class View:

    def __init__(self, scrollPanel):

        self.psLog = PSE.LOGGING.getLogger('OPS.Main.View')

        self.cpSettings = PSE.readConfigFile('CP')

        self.controlPanel = scrollPanel
        self.psPluginMenuItems = []
        self.isKeyFile = Bundle.validateKeyFile()

        return

    def makePsButton(self):

        psButton = PSE.JAVX_SWING.JButton()
        psButton.setText(PSE.BUNDLE[u'Pattern Scripts'])
        psButton.setName('psButton')

        return psButton

    def makePluginPanel(self):
        """Dealers choice, jPanel or Box"""

        # pluginPanel = PSE.JAVX_SWING.JPanel()
        pluginPanel = PSE.JAVX_SWING.Box(PSE.JAVX_SWING.BoxLayout.PAGE_AXIS)

        return pluginPanel

    def makeScrollPanel(self, pluginPanel):

        scrollPanel = PSE.JAVX_SWING.JScrollPane(pluginPanel)
        scrollPanel.border = PSE.JAVX_SWING.BorderFactory.createLineBorder(PSE.JAVA_AWT.Color.GRAY)

        return scrollPanel

    def getPsPluginMenuItems(self):

        return self.psPluginMenuItems

    def makePatternScriptsWindow(self):

        uniqueWindow = PSE.JMRI.util.JmriJFrame()

        asMenuItem = self.makeMenuItem(self.setAsDropDownText())
        tpMenuItem = self.makeMenuItem(self.setTpDropDownText())
        o2oMenuItem = self.makeMenuItem(self.setOoDropDownText())
        ptMenuItem = self.makeMenuItem(self.setPtDropDownText())
        if not self.isKeyFile:
            ptMenuItem.setEnabled(False)
        rsMenuItem = self.makeMenuItem(self.setRsDropDownText())
        helpMenuItem = self.makeMenuItem(self.setHmDropDownText())
        gitHubMenuItem = self.makeMenuItem(self.setGhDropDownText())
        opsFolderMenuItem = self.makeMenuItem(self.setOfDropDownText())
        logMenuItem = self.makeMenuItem(self.setLmDropDownText())
        editConfigMenuItem = self.makeMenuItem(self.setEcDropDownText())

        toolsMenu = PSE.JAVX_SWING.JMenu(PSE.BUNDLE[u'Tools'])
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.OptionAction())
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.PrintOptionAction())
        toolsMenu.add(PSE.JMRI.jmrit.operations.setup.BuildReportOptionAction())
        toolsMenu.add(asMenuItem)
        toolsMenu.add(tpMenuItem)
        toolsMenu.add(o2oMenuItem)
        toolsMenu.add(editConfigMenuItem)
        toolsMenu.add(ptMenuItem)
        toolsMenu.add(rsMenuItem)

        helpMenu = PSE.JAVX_SWING.JMenu(PSE.BUNDLE[u'Help'])
        helpMenu.add(helpMenuItem)
        helpMenu.add(gitHubMenuItem)
        helpMenu.add(opsFolderMenuItem)
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
        uniqueWindow.add(self.controlPanel)
        uniqueWindow.pack()
        uniqueWindow.setSize(configPanel['PW'], configPanel['PH'])
        uniqueWindow.setLocation(configPanel['PX'], configPanel['PY'])
        uniqueWindow.setVisible(True)

        return

    def makeMenuItem(self, itemMethod):

        itemText, itemName = itemMethod

        menuItem = PSE.JAVX_SWING.JMenuItem(itemText)
        menuItem.setName(itemName)
        self.psPluginMenuItems.append(menuItem)

        return menuItem

    def setAsDropDownText(self):
        """itemMethod - Set the drop down text per the Apply Schedule flag"""

        patternConfig = PSE.readConfigFile('PT')
        if patternConfig['AS']:
            menuText = PSE.BUNDLE[u'Do Not Apply Schedule']
        else:
            menuText = PSE.BUNDLE[u'Apply Schedule']

        return menuText, 'asItemSelected'

    def setTpDropDownText(self):
        """itemMethod - Set the drop down text per the config file PatternTracksSubroutine Include flag"""

        patternConfig = PSE.readConfigFile('CP')
        if patternConfig['SI'][0]['PatternTracksSubroutine']:
            menuText = PSE.BUNDLE[u'Disable Track Pattern subroutine']
        else:
            menuText = PSE.BUNDLE[u'Enable Track Pattern subroutine']

        return menuText, 'tpItemSelected'

    def setOoDropDownText(self):
        """itemMethod - Set the drop down text per the config file o2oSubroutine Include flag"""

        patternConfig = PSE.readConfigFile('CP')
        if patternConfig['SI'][1]['o2oSubroutine']:
            menuText = PSE.BUNDLE[u'Disable o2o subroutine']
        else:
            menuText = PSE.BUNDLE[u'Enable o2o subroutine']

        return menuText, 'ooItemSelected'

    def setPtDropDownText(self):
        """itemMethod - Set the drop down text for the Translate Plugin item"""

        menuText = PSE.BUNDLE[u'Translate Plugin']

        return menuText, 'ptItemSelected'

    def setRsDropDownText(self):
        """itemMethod - Set the drop down text for the Restart From Default item"""

        menuText = PSE.BUNDLE[u'Restart From Default']

        return menuText, 'rsItemSelected'

    def setHmDropDownText(self):
        """itemMethod - Set the drop down text for the Log menu item"""

        menuText = PSE.BUNDLE[u'Window Help...']

        return menuText, 'helpItemSelected'

    def setLmDropDownText(self):
        """itemMethod - Set the drop down text for the Log menu item"""

        menuText = PSE.BUNDLE[u'View Log File']

        return menuText, 'logItemSelected'

    def setGhDropDownText(self):
        """itemMethod - Set the drop down text for the gitHub page item"""

        menuText = PSE.BUNDLE[u'GitHub Web Page']

        return menuText, 'ghItemSelected'

    def setEcDropDownText(self):
        """itemMethod - Set the drop down text for the edit config file item"""

        menuText = PSE.BUNDLE[u'Edit Config File']

        return menuText, 'ecItemSelected'

    def setOfDropDownText(self):
        """itemMethod - Set the drop down text for the edit config file item"""

        menuText = PSE.BUNDLE[u'Operations Folder']

        return menuText, 'ofItemSelected'

class Controller(PSE.JMRI.jmrit.automat.AbstractAutomaton):

    def init(self):
        """ """

        PSE.makeBuildStatusFolder()

        logFileTarget = PSE.OS_Path.join(PSE.PROFILE_PATH, 'operations', 'buildstatus', 'PatternScriptsLog.txt')

        self.logger = PSE.Logger(logFileTarget)
        self.logger.startLogger('OPS')

        self.model = Model()

        self.trainsTableModel = PSE.JMRI.jmrit.operations.trains.TrainsTableModel()
        self.builtTrainListener = Listeners.BuiltTrain()
        self.trainsTableListener = Listeners.TrainsTable(self.builtTrainListener)

        self.menuItemList = []

        return

    def addPatternScriptsButton(self):
        """The Pattern Scripts button on the PanelPro frame"""

        self.patternScriptsButton = View(None).makePsButton()
        self.patternScriptsButton.actionPerformed = self.patternScriptsButtonAction
        Apps.buttonSpace().add(self.patternScriptsButton)
        Apps.buttonSpace().revalidate()

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
        """Invoked by Restart From Defaults pulldown"""

        for frame in PSE.JMRI.util.JmriJFrame.getFrameList():
            # frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
            if frame.getName() == 'patternScriptsWindow':
                PSE.updateWindowParams(frame)
                PSE.closeSetCarsWindows()

                frame.setVisible(False)
                frame.dispose()

        return

    def buildThePlugin(self):

        # PSE.BUNDLE = Bundle.getBundleForLocale()

        view = View(None)
        emptyPluginPanel = view.makePluginPanel()
        populatedPluginPanel = self.model.makePatternScriptsPanel(emptyPluginPanel)

        scrollPanel = view.makeScrollPanel(populatedPluginPanel)
        patternScriptsWindow = View(scrollPanel)
        patternScriptsWindow.makePatternScriptsWindow()
        self.menuItemList = patternScriptsWindow.getPsPluginMenuItems()

        self.addMenuItemListeners()

        return

    def o2oSubroutineListeners(self):

        self.addTrainsTableListener()
        self.addBuiltTrainListener()

        return

    def addMenuItemListeners(self):
        """Use the pull down item names as the attribute to set the
        listener: asItemSelected, tpItemSelected, ooItemSelected, logItemSelected, helpItemSelected, Etc.
        """

        for menuItem in self.menuItemList:
            menuItem.addActionListener(getattr(self, menuItem.getName()))

        return

    def asItemSelected(self, AS_ACTIVATE_EVENT):
        """menu item-Tools/Apply Schedule"""

        self.psLog.debug(AS_ACTIVATE_EVENT)
        patternConfig = PSE.readConfigFile()

        if patternConfig['PT']['AS']:
            patternConfig['PT'].update({'AS': False})
            AS_ACTIVATE_EVENT.getSource().setText(PSE.BUNDLE[u'Apply Schedule'])
            self.psLog.info('Apply Schedule turned off')
            print('Apply Schedule turned off')
        else:
            patternConfig['PT'].update({'AS': True})
            AS_ACTIVATE_EVENT.getSource().setText(PSE.BUNDLE[u'Do Not Apply Schedule'])
            self.psLog.info('Apply Schedule turned on')
            print('Apply Schedule turned on')

        PSE.writeConfigFile(patternConfig)

        return

    def tpItemSelected(self, TP_ACTIVATE_EVENT):
        """menu item-Tools/Enable Track Pattern subroutine"""

        self.psLog.debug(TP_ACTIVATE_EVENT)
        patternConfig = PSE.readConfigFile()

        if patternConfig['CP']['SI'][0]['PatternTracksSubroutine']: # If enabled, turn it off
            patternConfig['CP']['SI'][0].update({'PatternTracksSubroutine': False})
            TP_ACTIVATE_EVENT.getSource().setText(PSE.BUNDLE[u'Enable Track Pattern subroutine'])

            self.psLog.info('Track Pattern support deactivated')
            print('Track Pattern support deactivated')
        else:
            patternConfig['CP']['SI'][0].update({'PatternTracksSubroutine': True})
            TP_ACTIVATE_EVENT.getSource().setText(PSE.BUNDLE[u'Disable Track Pattern subroutine'])

            self.psLog.info('Track Pattern support activated')
            print('Track Pattern support activated')

        PSE.writeConfigFile(patternConfig)
        self.closePsWindow()
        self.buildThePlugin()

        return

    def ooItemSelected(self, TP_ACTIVATE_EVENT):
        """menu item-Tools/Enable o2o subroutine"""

        self.psLog.debug(TP_ACTIVATE_EVENT)
        patternConfig = PSE.readConfigFile()

        if patternConfig['CP']['SI'][1]['o2oSubroutine']: # If enabled, turn it off
            patternConfig['CP']['SI'][1].update({'o2oSubroutine': False})
            TP_ACTIVATE_EVENT.getSource().setText(PSE.BUNDLE[u'Enable o2o subroutine'])

            self.trainsTableModel.removeTableModelListener(self.trainsTableListener)
            self.removeBuiltTrainListener()

            self.psLog.info('o2o subroutine deactivated')
            print('o2o subroutine deactivated')
        else:
            patternConfig['CP']['SI'][1].update({'o2oSubroutine': True})
            TP_ACTIVATE_EVENT.getSource().setText(PSE.BUNDLE[u'Disable o2o subroutine'])

            self.trainsTableModel.addTableModelListener(self.trainsTableListener)
            self.addBuiltTrainListener()

            self.psLog.info('o2o subroutine activated')
            print('o2o subroutine activated')

        PSE.writeConfigFile(patternConfig)
        self.shutdownPlugin()
        self.startupPlugin()

        return

    def ptItemSelected(self, TRANSLATE_PLUGIN_EVENT):
        """menu item-Tools/Translate Plugin"""

        self.psLog.debug(TRANSLATE_PLUGIN_EVENT)

        Bundle.makeBundles()
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
        RESTART_PLUGIN_EVENT.getSource().firePropertyChange('psWindowClosing', False, True)

        self.psLog.info('Pattern Scripts plugin restarted')

        return

    def shutdownPlugin(self):

        self.removeTrainsTableListener()
        self.removeBuiltTrainListener()
        self.closePsWindow()

        return

    def startupPlugin(self):

        PSE.BUNDLE = Bundle.getBundleForLocale()
        PSE.CreateStubFile().make()
        Bundle.makeHelpPage()

        self.buildThePlugin()

        return

    def helpItemSelected(self, OPEN_HELP_EVENT):
        """menu item-Help/Window help..."""

        self.psLog.debug(OPEN_HELP_EVENT)

        stubFileTarget = PSE.OS_Path.join(PSE.JMRI.util.FileUtil.getPreferencesPath(), 'jmrihelp', 'psStub.html')
        stubUri = PSE.JAVA_IO.File(stubFileTarget).toURI()
        # stubUri = JAVA_NET.URI(str(stubFileTarget)).create()
        if PSE.JAVA_IO.File(stubUri).isFile():
            PSE.JAVA_AWT.Desktop.getDesktop().browse(stubUri)
        else:
            self.psLog.warning('Help file not found')

        return

    def logItemSelected(self, OPEN_LOG_EVENT):
        """menu item-Help/View Log"""

        self.psLog.debug(OPEN_LOG_EVENT)

        patternLog = PSE.makePatternLog()

        logFileTarget = PSE.OS_Path.join(PSE.PROFILE_PATH, 'operations', 'buildstatus', 'PatternScriptsLog_temp.txt')

        PSE.genericWriteReport(logFileTarget, patternLog)
        PSE.genericDisplayReport(logFileTarget)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def ghItemSelected(self, OPEN_GH_EVENT):
        """menu item-Help/GitHub Page"""

        self.psLog.debug(OPEN_GH_EVENT)

        ghURL = 'https://github.com//GregRitacco//OperationsPatternScripts'
        PSE.JMRI.util.HelpUtil.openWebPage(ghURL)

        return

    def ecItemSelected(self, OPEN_EC_EVENT):
        """menu item-Help/Edit Config File"""

        self.psLog.debug(OPEN_EC_EVENT)

        configTarget = PSE.OS_Path.join(PSE.PROFILE_PATH, 'operations', 'PatternConfig.json')

        if PSE.JAVA_IO.File(configTarget).isFile():
            PSE.genericDisplayReport(configTarget)
        else:
            self.psLog.warning('Not found: ' + configTarget)

        return

    def ofItemSelected(self, OPEN_OF_EVENT):
        """menu item-Help/Operations Folder"""

        self.psLog.debug(OPEN_OF_EVENT)

        opsFolderPath = PSE.OS_Path.join(PSE.PROFILE_PATH, 'operations')

        opsFolder = PSE.JAVA_IO.File(opsFolderPath)
        if opsFolder.exists():
            PSE.JAVA_AWT.Desktop.getDesktop().open(opsFolder)
        else:
            self.psLog.warning('Not found: ' + opsFolderPath)

        return

    def handle(self):

        startTime = PSE.TIME.time()
        self.psLog = PSE.LOGGING.getLogger('OPS.Main.Controller')
        self.logger.initialLogMessage(self.psLog)

        PSE.makeReportFolders()
        self.model.validatePatternConfig()
        PSE.CreateStubFile().make()
        if PSE.readConfigFile()['CP']['SI'][1]['o2oSubroutine']:
            self.o2oSubroutineListeners()
        if PSE.readConfigFile()['CP']['AP']:
            self.addPatternScriptsButton()

        self.psLog.info('Current Pattern Scripts directory: ' + PLUGIN_ROOT)
        runTime = PSE.TIME.time() - startTime
        self.psLog.info('Main script run time (sec): ' + str(round(runTime, 4)))
        print('Current Pattern Scripts directory: ' + PLUGIN_ROOT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return False

Controller().start()

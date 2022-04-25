# No restrictions on use
# © 2021 Greg Ritacco

'''Pattern Scripts plugin for JMRI Operations Pro'''

import jmri
from apps import Apps

import java
import java.beans
import java.awt
import javax.swing

import logging
import time
from sys import path as sysPath

SCRIPT_NAME = 'OperationsPatternScripts.MainScript'
SCRIPT_REV = 20220101

SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b2'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b3'

SCRIPT_ROOT = jmri.util.FileUtil.getPreferencesPath() + SCRIPT_DIR

sysPath.append(SCRIPT_ROOT)
from psEntities import MainScriptEntities
from TrainPlayerSubroutine import ExportToTrainPlayer
MainScriptEntities.SCRIPT_ROOT = SCRIPT_ROOT

class Logger():

    def __init__(self):

        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog.txt'
        logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.psFileHandler = logging.FileHandler(logPath, mode='w', encoding='utf-8')
        self.psFileHandler.setFormatter(logFileFormat)

        return

    def startLogger(self):

        psLog = logging.getLogger('PS')
        psLog.setLevel(10)
        psLog.addHandler(self.psFileHandler)

        return

    def stopLogger(self):

        psLog = logging.getLogger('PS')
        psLog.removeHandler(self.psFileHandler)

        return

class TrainsTableListener(javax.swing.event.TableModelListener):
    '''Catches user add or remove train while TP support is enabled'''

    def __init__(self, builtTrainListener):

        self.builtTrainListener = builtTrainListener

        return

    def tableChanged(self, TABLE_CHANGE):

        trainList = MainScriptEntities.TM.getTrainsByIdList()
        for train in trainList:
            train.removePropertyChangeListener(self.builtTrainListener) # Does not throw error if there is no listener to remove
            train.addPropertyChangeListener(self.builtTrainListener)

        return

class BuiltTrainListener(java.beans.PropertyChangeListener):
    '''Starts TrainPlayer manifest export on trainBuilt'''

    def propertyChange(self, TRAIN_BUILT):

        if TRAIN_BUILT.propertyName == 'TrainBuilt' and TRAIN_BUILT.newValue:
            tpManifest = ExportToTrainPlayer.ManifestForTrainPlayer()
            tpManifest.passInTrain(TRAIN_BUILT.getSource())
            tpManifest.start()

        return

class PatternScriptsWindowListener(java.awt.event.WindowListener):
    '''Listener to respond to the plugin window operations. A bit verbose because of intended expansion in v3'''

    def __init__(self):

        return

    def closeSetCarsWindows(self):
        '''Close all the Set Cars windows when the Pattern Scripts window is closed'''

        for frameName in jmri.util.JmriJFrame.getFrameList():
            frame = jmri.util.JmriJFrame.getFrame(frameName)
            if frame.getName() == 'setCarsWindow':
                frame.dispose()
                frame.setVisible(False)

        return

    def windowClosed(self, WINDOW_CLOSED):

        self.closeSetCarsWindows()
        WINDOW_CLOSED.getSource().dispose()

        return

    def windowOpened(self, WINDOW_OPENED):
        return
    def windowClosing(self, WINDOW_CLOSING):
        return
    def windowActivated(self, WINDOW_ACTIVATED):
        return
    def windowDeactivated(self, WINDOW_DEACTIVATED):
        return

class View_PsWindow:
    '''Makes a JMRI JFrame that the control panel is set into'''

    def __init__(self, scrollPanel):

        self.controlPanel = scrollPanel
        self.uniqueWindow = jmri.util.JmriJFrame(u'Pattern Scripts')
        self.uniqueWindow.setName('patternScripts')
        self.menuItemList = []

        return

    def makePsButton(self):

        psButton = javax.swing.JButton(name='psButton')

        return psButton

    def makePatternScriptWindow(self):

        menuItemList = []

        asMenuItem = javax.swing.JMenuItem(self.setAsDropDown())
        asMenuItem.setName('asItemSelected')
        self.menuItemList.append(asMenuItem)
        tpMenuItem = javax.swing.JMenuItem(self.setTiDropDown())
        tpMenuItem.setName('tpItemSelected')
        self.menuItemList.append(tpMenuItem)
        toolsMenu = javax.swing.JMenu(u'Tools')
        toolsMenu.add(jmri.jmrit.operations.setup.OptionAction())
        toolsMenu.add(jmri.jmrit.operations.setup.PrintOptionAction())
        toolsMenu.add(jmri.jmrit.operations.setup.BuildReportOptionAction())
        toolsMenu.add(asMenuItem)
        toolsMenu.add(tpMenuItem)

        helpMenuItem = javax.swing.JMenuItem(u'Window Help...')
        helpMenuItem.setName('helpItemSelected')
        self.menuItemList.append(helpMenuItem)
        helpMenu = javax.swing.JMenu(u'Help')
        helpMenu.add(helpMenuItem)

        psMenuBar = javax.swing.JMenuBar()
        psMenuBar.add(toolsMenu)
        psMenuBar.add(jmri.jmrit.operations.OperationsMenu())
        psMenuBar.add(jmri.util.WindowMenu(self.uniqueWindow))
        psMenuBar.add(helpMenu)

        self.uniqueWindow.addWindowListener(PatternScriptsWindowListener())
        self.uniqueWindow.setJMenuBar(psMenuBar)
        self.uniqueWindow.add(self.controlPanel)
        self.uniqueWindow.pack()
        self.uniqueWindow.setVisible(True)

        return

    def getMenuItemList(self):

        return self.menuItemList

    def setAsDropDown(self):
        '''Set the drop down text per the Apply Schedule flag'''

        asFlag = patternConfig = MainScriptEntities.readConfigFile('TP')['AS']
        if asFlag:
            menuText = "Don't Apply Schedules"
        else:
            menuText = "Apply Schedules"

        return menuText

    def setTiDropDown(self):
        '''Set the drop down text per the TrainPlayer Include flag'''

        tiFlag = patternConfig = MainScriptEntities.readConfigFile('TP')['TI']
        if tiFlag:
            menuText = "Disable TrainPlayer"
        else:
            menuText = "Enable TrainPlayer"

        return menuText

# class MakeControlPanel:
#
#     def makePluginPanel(self):
#
#         self.pluginPanel = javax.swing.JPanel()
#
#         return self.pluginPanel
#
#     def makeScrollPanel(self):
#
#         configPanel = MainScriptEntities.readConfigFile('CP')
#         scrollPanel = javax.swing.JScrollPane(self.pluginPanel)
#         scrollPanel.border = javax.swing.BorderFactory.createLineBorder(java.awt.Color.GRAY)
#         scrollPanel.setPreferredSize(java.awt.Dimension(configPanel['PW'], configPanel['PH']))
#         scrollPanel.setMaximumSize(scrollPanel.getPreferredSize())
#
#         return scrollPanel

class PatternScriptsPlugin:
    '''Make the the Pattern Scripts plugin from selected subroutines'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.Plugin')

        return

    def makePluginPanel(self):

        pluginPanel = javax.swing.JPanel()

        return pluginPanel

    def makeScrollPanel(self, subroutinePanel):

        configPanel = MainScriptEntities.readConfigFile('CP')
        scrollPanel = javax.swing.JScrollPane(subroutinePanel)
        scrollPanel.border = javax.swing.BorderFactory.createLineBorder(java.awt.Color.GRAY)
        scrollPanel.setPreferredSize(java.awt.Dimension(configPanel['PW'], configPanel['PH']))
        scrollPanel.setMaximumSize(scrollPanel.getPreferredSize())

        return scrollPanel

    def makeSubroutineList(self):

        subroutineList = []
        controlPanelConfig = MainScriptEntities.readConfigFile('CP')
        for subroutineIncludes, isIncluded in controlPanelConfig['SI'].items():
            if (isIncluded):
                xModule = __import__(subroutineIncludes, fromlist=['Controller'])
                subroutineFrame = xModule.Controller.StartUp().makeSubroutineFrame()
                subroutinePanel = xModule.Controller.StartUp().makeSubroutinePanel()
                subroutineFrame.add(subroutinePanel)
                subroutineList.append(subroutineFrame)
                self.psLog.info(subroutineIncludes + ' subroutine added to control panel')

        return subroutineList

    def makeSubroutineScrollPanel(self):

        subroutinePanel = self.makePluginPanel()
        scrollPanel = self.makeScrollPanel(subroutinePanel)
        subroutineList = self.makeSubroutineList()
        for subroutine in subroutineList:
            subroutinePanel.add(subroutine)

        return scrollPanel

class Controller_PsWindow(jmri.jmrit.automat.AbstractAutomaton):

    def init(self):

        self.logger = Logger()
        self.logger.startLogger()
        self.psLog = logging.getLogger('PS')
        self.psLog.debug('Log File for Pattern Scripts Plugin - DEBUG level test message')
        self.psLog.info('Log File for Pattern Scripts Plugin - INFO level test message')
        self.psLog.warning('Log File for Pattern Scripts Plugin - WARNING level test message')
        self.psLog.error('Log File for Pattern Scripts Plugin - ERROR level test message')
        self.psLog.critical('Log File for Pattern Scripts Plugin - CRITICAL level test message')

        self.trainsTableModel = jmri.jmrit.operations.trains.TrainsTableModel()
        self.builtTrainListener = BuiltTrainListener()
        self.trainsTableListener = TrainsTableListener(self.builtTrainListener)

        self.patternScriptsButton = javax.swing.JButton(text = 'Pattern Scripts', name = 'psButton')

        return

    def runValidations(self):

        MainScriptEntities.validateFileDestinationDirestories()
        MainScriptEntities.validateStubFile(SCRIPT_ROOT)
        MainScriptEntities.readConfigFile()
        if not MainScriptEntities.validateConfigFile(SCRIPT_ROOT):
            MainScriptEntities.backupConfigFile()
            self.psLog.warning('PatternConfig.json.bak file written')
            MainScriptEntities.writeNewConfigFile()
            self.psLog.warning('New PatternConfig.JSON file created for this profile')
        if MainScriptEntities.readConfigFile('TP')['TI']: # TrainPlayer Include
            ExportToTrainPlayer.CheckTpDestination().directoryExists()

        return

    def addTrainsTableListener(self):

        self.trainsTableModel.addTableModelListener(self.trainsTableListener)

        return

    def removeTrainsTableListener(self):

        self.trainsTableModel.removeTableModelListener(self.trainsTableListener)

        return

    def addBuiltTrainListener(self):

        trainList = MainScriptEntities.TM.getTrainsByIdList()
        for train in trainList:
            train.addPropertyChangeListener(self.builtTrainListener)

        return

    def removeBuiltTrainListener(self):

        trainList = MainScriptEntities.TM.getTrainsByIdList()
        for train in trainList:
            train.removePropertyChangeListener(self.builtTrainListener)

        return

    def addPatternScriptsButton(self):
        '''The Pattern Scripts button on the PanelPro frame'''

        self.patternScriptsButton = View_PsWindow(None).makePsButton()
        self.patternScriptsButton.setText('Pattern Scripts')
        self.patternScriptsButton.actionPerformed = self.patternScriptsButtonAction
        Apps.buttonSpace().add(self.patternScriptsButton)
        Apps.buttonSpace().revalidate()

        return

    def patternScriptsButtonAction(self, MOUSE_CLICKED):

        self.patternScriptsButton.setText('Restart Pattern Scripts')
        self.patternScriptsButton.actionPerformed = self.patternScriptsButtonRestartAction
        self.buildThePlugin()

        return

    def patternScriptsButtonRestartAction(self, MOUSE_CLICKED):

        self.removeTrainsTableListener()
        self.removeBuiltTrainListener()
        self.closePsWindow()
        self.logger.stopLogger()
        self.logger.startLogger()
        self.buildThePlugin()
        self.psLog.info('Pattern Scripts plugin restarted')

        return

    def closePsWindow(self):

        for frameName in jmri.util.JmriJFrame.getFrameList():
            frame = jmri.util.JmriJFrame.getFrame(frameName)
            if frame.getName() == 'patternScripts':
                frame.dispose()
                frame.setVisible(False)

        return

    def buildThePlugin(self):

        patternScriptsPlugin = PatternScriptsPlugin()
        subroutinePanel = patternScriptsPlugin.makeSubroutineScrollPanel()
        patternScriptsWindow = View_PsWindow(subroutinePanel)
        patternScriptsWindow.makePatternScriptWindow()
        menuItemList = patternScriptsWindow.getMenuItemList()
        self.parseMenuItemList(menuItemList)

        return

    def parseMenuItemList(self, menuItemList):
        '''Use the pull down item names as the attribute to set the listener: asItemSelected, tpItemSelected, helpItemSelected'''

        for menuItem in menuItemList:
            menuItem.addActionListener(getattr(self, menuItem.getName()))

        return

    def asItemSelected(self, AS_ACTIVATE_EVENT):
        '''menu item-Tools/Apply Schedule'''

        patternConfig = MainScriptEntities.readConfigFile()

        if patternConfig['TP']['AS']:
            patternConfig['TP'].update({'AS': False})
            AS_ACTIVATE_EVENT.getSource().setText(u"Apply Schedules")
            self.psLog.info('Apply Schedule turned off')
            print('Apply Schedule turned off')
        else:
            patternConfig['TP'].update({'AS': True})
            AS_ACTIVATE_EVENT.getSource().setText(u"Don't Apply Schedules")
            self.psLog.info('Apply Schedule turned on')
            print('Apply Schedule turned on')

        MainScriptEntities.writeConfigFile(patternConfig)

        return

    def tpItemSelected(self, TP_ACTIVATE_EVENT):
        '''menu item-Tools/Enable Trainplayer'''

        patternConfig = MainScriptEntities.readConfigFile()

        if patternConfig['TP']['TI']: # If enabled, turn it off
            patternConfig['TP'].update({'TI': False})
            TP_ACTIVATE_EVENT.getSource().setText(u'Enable TrainPlayer')

            self.trainsTableModel.removeTableModelListener(self.trainsTableListener)
            self.removeBuiltTrainListener()

            self.psLog.info('TrainPlayer support deactivated')
            print('TrainPlayer support deactivated')
        else:
            patternConfig['TP'].update({'TI': True})
            TP_ACTIVATE_EVENT.getSource().setText(u'Disable TrainPlayer')

            ExportToTrainPlayer.CheckTpDestination().directoryExists()
            self.trainsTableModel.addTableModelListener(self.trainsTableListener)
            self.addBuiltTrainListener()

            self.psLog.info('TrainPlayer support activated')
            print('TrainPlayer support activated')

        MainScriptEntities.writeConfigFile(patternConfig)

        return

    def helpItemSelected(self, OPEN_HELP_EVENT):
        '''menu item-Help/Window help...'''

        helpStubPath = MainScriptEntities.getStubPath()
        jmri.util.HelpUtil.openWebPage(helpStubPath)

        return

    def handle(self):

        yTimeNow = time.time()

        self.runValidations()
        self.addPatternScriptsButton()

        if MainScriptEntities.readConfigFile('TP')['TI']: # TrainPlayer Include
            self.addTrainsTableListener()
            self.addBuiltTrainListener()

        self.psLog.info('Current Pattern Scripts directory: ' + SCRIPT_ROOT)
        self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])
        print('Current Pattern Scripts directory: ' + SCRIPT_ROOT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))
        print('%s' % (SCRIPT_NAME))

        return False

Controller_PsWindow().start()

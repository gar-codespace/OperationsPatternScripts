# No restrictions on use
# © 2021 Greg Ritacco

import jmri
from apps import Apps
import java
import java.beans
import java.awt
import java.awt.event
import javax.swing
import logging
import time
from sys import path as sysPath
# import os.path

'''Pattern Scripts plugin for JMRI Operations Pro'''

SCRIPT_NAME = 'OperationsPatternScripts.MainScript'
SCRIPT_REV = 20220101

SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b2'

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
    '''Catches user add or remove train while TP support is active'''

    def tableChanged(self, TABLE_CHANGE):

        trainList = MainScriptEntities.TM.getTrainsByIdList()
        print('Yipee')

        for train in trainList:
            train.removePropertyChangeListener(BuiltTrainListener()) # Does not throw error if there is no listener to remove
            train.addPropertyChangeListener(BuiltTrainListener())

        return

class BuiltTrainListener(java.beans.PropertyChangeListener):

    def propertyChange(self, TRAIN_BUILT):
        '''Listens for a built train, starts TrainPlayer manifest export'''

        if TRAIN_BUILT.propertyName == 'TrainBuilt' and TRAIN_BUILT.newValue:
            tpManifest = ExportToTrainPlayer.ManifestForTrainPlayer()
            tpManifest.passInTrain(TRAIN_BUILT.getSource())
            tpManifest.start()

        return

class PatternScriptsWindowListener(java.awt.event.WindowListener):
    '''Listener to respond to the plugin window operations. More on this later.'''

    def __init__(self):

        # self.psLog = logging.getLogger('PS')
        return

    def closeSetCarsWindows(self):

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

class ControllerPsWindow(jmri.jmrit.automat.AbstractAutomaton):

    def init(self):

        self.logger = Logger()
        self.logger.startLogger()
        # self.psLog = logging.getLogger('PS')

        self.helpStubPath = MainScriptEntities.scrubPath()

        self.trainsTableModel = jmri.jmrit.operations.trains.TrainsTableModel()
        self.trainsTableListener = TrainsTableListener()
        self.builtTrainListener = BuiltTrainListener()

        self.trainList = MainScriptEntities.TM.getTrainsByIdList()


        # self.patternScriptsButton = javax.swing.JButton(text = 'Pattern Scripts', name = 'psButton')


        self.psPlugin = StartPsPlugin()
        return

    def patternButtonStart(self, MOUSE_CLICKED):

        # self.logger.startLogger()
        self.psPlugin.startPlugin()
        self.patternScriptsButton.setText('Restart Pattern Scripts')
        self.patternScriptsButton.actionPerformed = self.patternButtonRestart

        return

    def patternButtonRestart(self, MOUSE_CLICKED):

        self.closePsWindow()
        self.logger.stopLogger()
        self.logger.startLogger()
        self.psPlugin.startPlugin()

        return

    def helpItemSelected(self, ACTION_PERFORMED):
        '''Displays the help pge in a browser'''

        jmri.util.HelpUtil.openWebPage(self.helpStubPath)

        return

    def asItemSelected(self, EVENT):
        '''Optionally apply a spurs schedule'''

        patternConfig = MainScriptEntities.readConfigFile()

        if patternConfig['TP']['AS']:
            patternConfig['TP'].update({'AS': False})
            EVENT.getSource().setText(u"Apply Schedules")
        else:
            patternConfig['TP'].update({'AS': True})
            EVENT.getSource().setText(u"Don't Apply Schedules")

        MainScriptEntities.writeConfigFile(patternConfig)

        return

    def closePsWindow(self):

        for frameName in jmri.util.JmriJFrame.getFrameList():
            frame = jmri.util.JmriJFrame.getFrame(frameName)
            if frame.getName() == 'patternScripts':
                frame.dispose()
                frame.setVisible(False)

        return

    def tpItemSelected(self, TP_ACTIVATE_EVENT):
        '''Enable or disable the TrainPlayer subroutine'''

        patternConfig = MainScriptEntities.readConfigFile()

        if patternConfig['TP']['TI']: # If enabled, turn it off
            patternConfig['TP'].update({'TI': False})
            TP_ACTIVATE_EVENT.getSource().setText(u'Enable TrainPlayer')
            self.trainList = MainScriptEntities.TM.getTrainsByIdList()
            self.trainsTableModel.removeTableModelListener(self.trainsTableListener)
            print(self.trainList)
            # self.stopBuiltTrainListener()
            # self.stopTrainsTableListener()
            # self.psLog.info('TrainPlayer support deactivated')
            print('TrainPlayer support deactivated')
        else:
            patternConfig['TP'].update({'TI': True})
            TP_ACTIVATE_EVENT.getSource().setText(u'Disable TrainPlayer')
            ExportToTrainPlayer.CheckTpDestination().directoryExists()
            self.trainList = MainScriptEntities.TM.getTrainsByIdList()
            self.trainsTableModel.addTableModelListener(self.trainsTableListener)
            print(self.trainList)
            # self.startBuiltTrainListener()
            # self.startTrainsTableListener()
            # self.psLog.info('TrainPlayer support activated')
            print('TrainPlayer support activated')

        MainScriptEntities.writeConfigFile(patternConfig)

        return

    def getAsFlag(self):
        '''Set the drop down text per the Apply Schedule flag'''

        asFlag = patternConfig = MainScriptEntities.readConfigFile('TP')['AS']
        if asFlag:
            menuText = "Don't Apply Schedules"
        else:
            menuText = "Apply Schedules"

        return menuText

    def getTiFlag(self):
        '''Set the drop down text per the TrainPlayer Include flag'''

        tiFlag = patternConfig = MainScriptEntities.readConfigFile('TP')['TI']
        if tiFlag:
            menuText = "Disable TrainPlayer"
        else:
            menuText = "Enable TrainPlayer"

        return menuText

    def startTrainsTableListener(self):

        # trainsTableModel = jmri.jmrit.operations.trains.TrainsTableModel()

        self.trainsTableModel.addTableModelListener(self.trainsTableListener)
        # self.psLog.info('TrainsTableListener activated')

        return

    def stopTrainsTableListener(self):

        # print(self.trainsTableModel.getListeners())

        self.trainsTableModel.removeTableModelListener(self.trainsTableListener)
        # self.psLog.info('TrainsTableListener deactivated')

        return

    def startBuiltTrainListener(self):


        for train in self.trainList:
            train.addPropertyChangeListener(self.builtTrainListener)


        # self.psLog.info('BuiltTrainListener added to trains')

        return

    def stopBuiltTrainListener(self):

        # self.trainList = MainScriptEntities.TM.getTrainsByIdList()

        for train in self.trainList:
            train.removePropertyChangeListener(self.builtTrainListener)

        # self.psLog.info('BuiltTrainListener removed from trains')

        return

    def handle(self):

        self.psLog = logging.getLogger('PS')

        if MainScriptEntities.readConfigFile('TP')['TI']: # TrainPlayer Include
            ExportToTrainPlayer.CheckTpDestination().directoryExists()
            self.startTrainsTableListener()
            self.startBuiltTrainListener()

        self.patternScriptsButton = ViewPsWindow(None).makePsButton()
        self.patternScriptsButton.setText('Pattern Scripts')
        self.patternScriptsButton.actionPerformed = self.patternButtonStart
        Apps.buttonSpace().add(self.patternScriptsButton)
        Apps.buttonSpace().revalidate()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return False

class ViewPsWindow:
    '''Makes a JMRI JFrame that the control panel is set into'''

    def __init__(self, scrollPanel):

        # self.psLog = logging.getLogger('PS')

        self.controlPanel = scrollPanel
        self.uniqueWindow = jmri.util.JmriJFrame(u'Pattern Scripts')
        self.uniqueWindow.setName('patternScripts')

        return

    def makePsButton(self):

        psButton = javax.swing.JButton(name = 'psButton')

        return psButton

    def makeWindow(self):

        asMenuItem = javax.swing.JMenuItem(ControllerPsWindow().getAsFlag())
        asMenuItem.addActionListener(ControllerPsWindow().asItemSelected)
        tpMenuItem = javax.swing.JMenuItem(ControllerPsWindow().getTiFlag())
        tpMenuItem.addActionListener(ControllerPsWindow().tpItemSelected)
        toolsMenu = javax.swing.JMenu(u'Tools')
        toolsMenu.add(jmri.jmrit.operations.setup.OptionAction())
        toolsMenu.add(jmri.jmrit.operations.setup.PrintOptionAction())
        toolsMenu.add(jmri.jmrit.operations.setup.BuildReportOptionAction())
        toolsMenu.add(asMenuItem)
        toolsMenu.add(tpMenuItem)

        # self.helpStubPath = MainScriptEntities.scrubPath()
        helpMenuItem = javax.swing.JMenuItem(u'Window Help...')
        helpMenuItem.addActionListener(ControllerPsWindow().helpItemSelected)
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

class MakeControlPanel:
    '''This is the main panel for the plugin'''

    def makePluginPanel(self):

        self.pluginPanel = javax.swing.JPanel()

        return self.pluginPanel

    def makeScrollPanel(self):

        configPanel = MainScriptEntities.readConfigFile('CP')
        scrollPanel = javax.swing.JScrollPane(self.pluginPanel)
        scrollPanel.border = javax.swing.BorderFactory.createLineBorder(java.awt.Color.GRAY)
        scrollPanel.setPreferredSize(java.awt.Dimension(configPanel['PW'], configPanel['PH']))
        scrollPanel.setMaximumSize(scrollPanel.getPreferredSize())

        return scrollPanel

class StartPsPlugin():
    '''Start the the Pattern Scripts plugin and add selected subroutines'''

    def __init__(self):

        PM = jmri.InstanceManager.getDefault(jmri.util.gui.GuiLafPreferencesManager)

        self.psLog = logging.getLogger('PS')
        self.psLog.debug('Log File for Pattern Scripts Plugin - DEBUG level test message')
        self.psLog.info('Log File for Pattern Scripts Plugin - INFO level test message')
        self.psLog.warning('Log File for Pattern Scripts Plugin - WARNING level test message')
        self.psLog.error('Log File for Pattern Scripts Plugin - ERROR level test message')
        self.psLog.critical('Log File for Pattern Scripts Plugin - CRITICAL level test message')

        return

    def startPlugin(self):
        '''Make and populate the Pattern Scripts control panel'''

        yTimeNow = time.time()
        MainScriptEntities.validateFileDestinationDirestories()
        MainScriptEntities.validateStubFile(SCRIPT_ROOT)
        MainScriptEntities.readConfigFile()
        if not MainScriptEntities.validateConfigFile(SCRIPT_ROOT):
            MainScriptEntities.backupConfigFile()
            self.psLog.warning('PatternConfig.json.bak file written')
            MainScriptEntities.writeNewConfigFile()
            self.psLog.warning('New PatternConfig.JSON file created for this profile')
    # make a list of subroutines for the control panel
        subroutineList = []
        controlPanelConfig = MainScriptEntities.readConfigFile('CP')
        for subroutineIncludes, isIncluded in controlPanelConfig['SI'].items():
            if (isIncluded):
            # import selected subroutines and add them to a list
                xModule = __import__(subroutineIncludes, fromlist=['Controller'])
                subroutineFrame = xModule.Controller.StartUp().makeSubroutineFrame()
                subroutinePanel = xModule.Controller.StartUp().makeSubroutinePanel()
                subroutineFrame.add(subroutinePanel)
                subroutineList.append(subroutineFrame)
                self.psLog.info(subroutineIncludes + ' subroutine added to control panel')
    # plug in the subroutine list into the control panel
        controlPanel = MakeControlPanel()
        pluginPanel = controlPanel.makePluginPanel()
        scrollPanel = controlPanel.makeScrollPanel()
        for subroutine in subroutineList:
            pluginPanel.add(subroutine)

        psWindow = ViewPsWindow(scrollPanel)
        psWindow.makeWindow()

        print('Current Pattern Scripts directory: ' + SCRIPT_ROOT)
        self.psLog.info('Current Pattern Scripts directory: ' + SCRIPT_ROOT)
        self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])

        return False

ControllerPsWindow().start()

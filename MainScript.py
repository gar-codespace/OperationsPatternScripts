# © 2021, 2022 Greg Ritacco

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
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b4'

SCRIPT_ROOT = jmri.util.FileUtil.getPreferencesPath() + SCRIPT_DIR

sysPath.append(SCRIPT_ROOT)
from psEntities import PatternScriptEntities
from psBundle import Bundle
from TrainPlayerSubroutine import BuiltTrainExport

'''Global variables for now, this may change'''
PatternScriptEntities.SCRIPT_ROOT = SCRIPT_ROOT
PatternScriptEntities.ENCODING = PatternScriptEntities.readConfigFile('CP')['SE']
PatternScriptEntities.BUNDLE = Bundle.getBundleForLocale(SCRIPT_ROOT)

class TrainsTableListener(javax.swing.event.TableModelListener):
    '''Catches user add or remove train while TrainPlayer support is enabled'''

    def __init__(self, builtTrainListener):

        self.builtTrainListener = builtTrainListener

        return

    def tableChanged(self, TABLE_CHANGE):

        trainList = PatternScriptEntities.TM.getTrainsByIdList()
        for train in trainList:
            train.removePropertyChangeListener(self.builtTrainListener) # Does not throw error if there is no listener to remove
            train.addPropertyChangeListener(self.builtTrainListener)

        return

class BuiltTrainListener(java.beans.PropertyChangeListener):
    '''Starts TrainPlayer manifest export on trainBuilt'''

    def propertyChange(self, TRAIN_BUILT):

        if TRAIN_BUILT.propertyName == 'TrainBuilt' and TRAIN_BUILT.newValue:
            tpManifest = BuiltTrainExport.ManifestForTrainPlayer()
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
                frame.setVisible(False)
                frame.dispose()

        return

    def windowClosed(self, WINDOW_CLOSED):

        self.closeSetCarsWindows()
        WINDOW_CLOSED.getSource().dispose()

        return

    def windowClosing(self, WINDOW_CLOSING):

        updateWindowParams(WINDOW_CLOSING.getSource())

        return

    def windowIconified(self, WINDOW_ICONIFIED):
        return
    def windowDeiconified(self, WINDOW_DEICONIFIED):
        return
    def windowOpened(self, WINDOW_OPENED):
        return
    def windowActivated(self, WINDOW_ACTIVATED):
        return
    def windowDeactivated(self, WINDOW_DEACTIVATED):
        return

def updateWindowParams(window):

    configPanel = PatternScriptEntities.readConfigFile()
    configPanel['CP'].update({'PH': window.getHeight()})
    configPanel['CP'].update({'PW': window.getWidth()})
    configPanel['CP'].update({'PX': window.getX()})
    configPanel['CP'].update({'PY': window.getY()})
    PatternScriptEntities.writeConfigFile(configPanel)

    return

class Model:

    def __init__(self):

        self.psLog = logging.getLogger('PS.Model')

        return

    def validatePatternConfig(self):

        PatternScriptEntities.readConfigFile()
        if not PatternScriptEntities.validateConfigFile(SCRIPT_ROOT):
            PatternScriptEntities.backupConfigFile()
            self.psLog.warning('PatternConfig.json.bak file written')
            PatternScriptEntities.writeNewConfigFile()
            self.psLog.warning('New PatternConfig.JSON file created for this profile')

        return

    def runValidations(self):

        PatternScriptEntities.validateFileDestinationDirestories()
        PatternScriptEntities.validateStubFile(SCRIPT_ROOT)

        return

    def makePatternScriptsPanel(self, pluginPanel):

        for subroutine in self.makeSubroutineList():
            pluginPanel.add(javax.swing.Box.createRigidArea(java.awt.Dimension(0,10)))
            pluginPanel.add(subroutine)
        return pluginPanel

    def makeSubroutineList(self):

        subroutineList = []
        controlPanelConfig = PatternScriptEntities.readConfigFile('CP')
        for subroutineIncludes, isIncluded in controlPanelConfig['SI'].items():
            if (isIncluded):
                xModule = __import__(subroutineIncludes, fromlist=['Controller'])
                startUp = xModule.Controller.StartUp()
                subroutineFrame = startUp.makeSubroutineFrame()
                subroutineList.append(subroutineFrame)
                self.psLog.info(subroutineIncludes + ' subroutine added to control panel')

        return subroutineList

class View:

    def __init__(self, scrollPanel):

        self.psLog = logging.getLogger('PS.View')

        self.controlPanel = scrollPanel
        self.menuItemList = []

        return

    def makePsButton(self):

        psButton = javax.swing.JButton(name='psButton')
        psButton.setText(PatternScriptEntities.BUNDLE['Pattern Scripts'])

        return psButton

    def makePluginPanel(self):
        '''Still not sure if it should be a panel or box'''

        # pluginPanel = javax.swing.JPanel()
        pluginPanel = javax.swing.Box(javax.swing.BoxLayout.PAGE_AXIS)

        return pluginPanel

    def makeScrollPanel(self, pluginPanel):

        configPanel = PatternScriptEntities.readConfigFile('CP')
        scrollPanel = javax.swing.JScrollPane(pluginPanel)
        scrollPanel.border = javax.swing.BorderFactory.createLineBorder(java.awt.Color.GRAY)

        return scrollPanel

    def makePatternScriptsWindow(self):

        tally = -1 # Don't count the description in the tally
        menuIncludes = PatternScriptEntities.readConfigFile('CP')['MI']
        for name, menuItem in menuIncludes.items():
            tally += len(menuItem)
        self.psLog.info(''.join(menuIncludes['Description']) + str(tally))

        uniqueWindow = jmri.util.JmriJFrame()
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

        logMenuItem = javax.swing.JMenuItem(PatternScriptEntities.BUNDLE['View Log'])
        logMenuItem.setName('logItemSelected')
        helpMenuItem = javax.swing.JMenuItem(PatternScriptEntities.BUNDLE['Window Help...'])
        helpMenuItem.setName('helpItemSelected')
        self.menuItemList.append(logMenuItem)
        self.menuItemList.append(helpMenuItem)
        helpMenu = javax.swing.JMenu(PatternScriptEntities.BUNDLE['Help'])
        helpMenu.add(logMenuItem)
        helpMenu.add(helpMenuItem)

        psMenuBar = javax.swing.JMenuBar()
        psMenuBar.add(toolsMenu)
        psMenuBar.add(jmri.jmrit.operations.OperationsMenu())
        psMenuBar.add(jmri.util.WindowMenu(uniqueWindow))
        psMenuBar.add(helpMenu)

        uniqueWindow.setName('patternScripts')
        uniqueWindow.setTitle(PatternScriptEntities.BUNDLE['Pattern Scripts'])
        uniqueWindow.addWindowListener(PatternScriptsWindowListener())
        uniqueWindow.setJMenuBar(psMenuBar)
        uniqueWindow.add(self.controlPanel)
        uniqueWindow.pack()
        configPanel = PatternScriptEntities.readConfigFile('CP')
        uniqueWindow.setSize(configPanel['PW'], configPanel['PH'])
        uniqueWindow.setLocation(configPanel['PX'], configPanel['PY'])
        uniqueWindow.setVisible(True)

        return

    def getMenuItemList(self):

        return self.menuItemList

    def setAsDropDown(self):
        '''Set the drop down text per the Apply Schedule flag'''

        patternConfig = PatternScriptEntities.readConfigFile('PT')
        if patternConfig['AS']:
            menuText = PatternScriptEntities.BUNDLE['Do Not Apply Schedule']
        else:
            menuText = PatternScriptEntities.BUNDLE['Apply Schedule']

        return menuText

    def setTiDropDown(self):
        '''Set the drop down text per the TrainPlayer Include flag'''

        patternConfig = PatternScriptEntities.readConfigFile('PT')
        if patternConfig['TI']:
            menuText = PatternScriptEntities.BUNDLE['Disable TrainPlayer']
        else:
            menuText = PatternScriptEntities.BUNDLE['Enable TrainPlayer']

        return menuText

class Controller(jmri.jmrit.automat.AbstractAutomaton):

    def init(self):

        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog.txt'
        self.logger = PatternScriptEntities.Logger(logPath)
        self.logger.startLogger('PS')

        self.model = Model()

        self.trainsTableModel = jmri.jmrit.operations.trains.TrainsTableModel()
        self.builtTrainListener = BuiltTrainListener()
        self.trainsTableListener = TrainsTableListener(self.builtTrainListener)

        self.menuItemList = []

        return

    def handle(self):

        yTimeNow = time.time()
        self.psLog = logging.getLogger('PS.Controller')
        self.logger.initialLogMessage(self.psLog)

        self.model.validatePatternConfig()
        # PatternScriptEntities.ENCODING = PatternScriptEntities.readConfigFile()['CP']['SE']
        self.model.runValidations()
        PatternScriptEntities.validateStubFile(SCRIPT_ROOT)
        self.addTrainPlayerListeners()
        if PatternScriptEntities.readConfigFile()['CP']['AP']:
            self.addPatternScriptsButton()

        self.psLog.info('Current Pattern Scripts directory: ' + SCRIPT_ROOT)
        self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])
        print('Current Pattern Scripts directory: ' + SCRIPT_ROOT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return False

    def addPatternScriptsButton(self):
        '''The Pattern Scripts button on the PanelPro frame'''

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

        trainList = PatternScriptEntities.TM.getTrainsByIdList()
        for train in trainList:
            train.addPropertyChangeListener(self.builtTrainListener)

        return

    def removeBuiltTrainListener(self):

        trainList = PatternScriptEntities.TM.getTrainsByIdList()
        for train in trainList:
            train.removePropertyChangeListener(self.builtTrainListener)

        return

    def patternScriptsButtonAction(self, MOUSE_CLICKED):

        self.patternScriptsButton.setText(PatternScriptEntities.BUNDLE['Restart Pattern Scripts'])
        self.patternScriptsButton.actionPerformed = self.patternScriptsButtonRestartAction
        self.buildThePlugin()

        return

    def patternScriptsButtonRestartAction(self, MOUSE_CLICKED):

        self.removeTrainsTableListener()
        self.removeBuiltTrainListener()
        self.closePsWindow()
        self.logger.stopLogger('PS')
        self.logger.startLogger('PS')
        self.buildThePlugin()
        self.psLog.info('Pattern Scripts plugin restarted')

        return

    def closePsWindow(self):

        for frameName in jmri.util.JmriJFrame.getFrameList():
            frame = jmri.util.JmriJFrame.getFrame(frameName)
            if frame.getName() == 'patternScripts':
                updateWindowParams(frame)
                frame.setVisible(False)
                frame.dispose()

        return

    def buildThePlugin(self):

        view = View(None)
        emptyPluginPanel = view.makePluginPanel()
        populatedPluginPanel = self.model.makePatternScriptsPanel(emptyPluginPanel)

        scrollPanel = view.makeScrollPanel(populatedPluginPanel)
        patternScriptsWindow = View(scrollPanel)
        patternScriptsWindow.makePatternScriptsWindow()
        self.menuItemList = patternScriptsWindow.getMenuItemList()

        self.addMenuItemListeners()

        return

    def addTrainPlayerListeners(self):

        if PatternScriptEntities.readConfigFile('PT')['TI']:
            self.addTrainsTableListener()
            self.addBuiltTrainListener()

        return

    def addMenuItemListeners(self):
        '''Use the pull down item names as the attribute to set the listener: asItemSelected, tpItemSelected, logItemSelected, helpItemSelected'''

        for menuItem in self.menuItemList:
            menuItem.addActionListener(getattr(self, menuItem.getName()))

        return

    def asItemSelected(self, AS_ACTIVATE_EVENT):
        '''menu item-Tools/Apply Schedule'''

        patternConfig = PatternScriptEntities.readConfigFile()

        if patternConfig['PT']['AS']:
            patternConfig['PT'].update({'AS': False})
            AS_ACTIVATE_EVENT.getSource().setText(PatternScriptEntities.BUNDLE["Apply Schedule"])
            self.psLog.info('Apply Schedule turned off')
            print('Apply Schedule turned off')
        else:
            patternConfig['PT'].update({'AS': True})
            AS_ACTIVATE_EVENT.getSource().setText(PatternScriptEntities.BUNDLE["Do Not Apply Schedule"])
            self.psLog.info('Apply Schedule turned on')
            print('Apply Schedule turned on')

        PatternScriptEntities.writeConfigFile(patternConfig)

        return

    def tpItemSelected(self, TP_ACTIVATE_EVENT):
        '''menu item-Tools/Enable Trainplayer'''

        patternConfig = PatternScriptEntities.readConfigFile()

        if patternConfig['PT']['TI']: # If enabled, turn it off
            patternConfig['PT'].update({'TI': False})
            TP_ACTIVATE_EVENT.getSource().setText(PatternScriptEntities.BUNDLE["Enable TrainPlayer"])

            self.trainsTableModel.removeTableModelListener(self.trainsTableListener)
            self.removeBuiltTrainListener()

            self.psLog.info('TrainPlayer support deactivated')
            print('TrainPlayer support deactivated')
        else:
            patternConfig['PT'].update({'TI': True})
            TP_ACTIVATE_EVENT.getSource().setText(PatternScriptEntities.BUNDLE["Disable TrainPlayer"])

            PatternScriptEntities.CheckTpDestination().directoryExists()
            self.trainsTableModel.addTableModelListener(self.trainsTableListener)
            self.addBuiltTrainListener()

            self.psLog.info('TrainPlayer support activated')
            print('TrainPlayer support activated')

        PatternScriptEntities.writeConfigFile(patternConfig)

        return

    def logItemSelected(self, OPEN_LOG_EVENT):
        '''menu item-Help/View Log'''

        PatternScriptEntities.makePatternLog()
        PatternScriptEntities.printPatternLog()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def helpItemSelected(self, OPEN_HELP_EVENT):
        '''menu item-Help/Window help...'''

        helpStubPath = PatternScriptEntities.getStubPath()
        jmri.util.HelpUtil.openWebPage(helpStubPath)

        return

Controller().start()

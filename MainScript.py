"""
Pattern Scripts plugin for JMRI Operations Pro
OPS = Operations Pattern Scripts
Copyright 2021, 2022, 2023 Greg Ritacco
No restrictions on use, but I would appreciate the reference.
"""

import jmri
import sys
from os import path as OS_PATH

SCRIPT_NAME = 'OperationsPatternScripts.MainScript'
SCRIPT_REV = 20231001
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

from opsEntities import GUI
from opsEntities import MainScriptListeners
from opsEntities import PluginListeners
from opsBundle import Bundle

PSE.validateConfigFile()

configFile = PSE.readConfigFile()
encodingSelection = configFile['Main Script']['CP']['ES']
PSE.ENCODING = configFile['Main Script']['CP']['EO'][encodingSelection] # ['EO'] is encoding options


class View:

    def __init__(self):

        self.psLog = PSE.LOGGING.getLogger('OPS.Main.View')

        Bundle.setupBundle()

        self.plugin = GUI.PluginGUI()

        return

    def getThePlugin(self):

        return self.plugin.getPsFrame()
    
    def getMenuItems(self):

        return self.plugin.getPsPluginMenuItems()
    
    def getSubroutineMenuItems(self):

        return self.plugin.getSubroutineMenuItems()
    

def makePsPlugin():
    """
    Set outside the Controller because it's also called by reset plugin.
    Called by:
    Controller
    MainScriptListeners.rsItemSelected
    """

    configFile = PSE.readConfigFile()
    subroutineDirs = PSE.getSubroutineDirs()
    configFile['Main Script'].update({'SL':subroutineDirs})
    if len(subroutineDirs) == 0: # Catches all subroutines deactivated
        configFile['Main Script']['CP'].update({'ER':False})
    PSE.writeConfigFile(configFile)

    view = View()
    psFrame = view.getThePlugin()
    psFrame.setSize(configFile['Main Script']['CP']['PW'], configFile['Main Script']['CP']['PH'])
    psFrame.setLocation(configFile['Main Script']['CP']['PX'], configFile['Main Script']['CP']['PY'])

    for menuItem in view.getMenuItems():
        menuItem.addActionListener(getattr(MainScriptListeners, menuItem.getName()))
    for menuItem in view.getSubroutineMenuItems():
        menuItem.addActionListener(MainScriptListeners.dropDownMenuItem)

    psFrame.addWindowListener(PluginListeners.PatternScriptsFrameListener())  
    psFrame.setVisible(True)

    return


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

        makePsPlugin()

        PSE.getPsButton().setEnabled(False)

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
        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return False

if __name__ == "__builtin__":
    Controller().start()
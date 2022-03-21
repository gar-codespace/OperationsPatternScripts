# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java
import logging
import time
from sys import path as sysPath

def useThisVersion():
    '''Keep multiple versions of this plugin sorted out'''

    fileRoot = jmri.util.FileUtil.getPreferencesPath()
    currentFile = str(jmri.util.FileUtil.findFiles('MainScript2.0.0.b1.py', fileRoot).pop())
    currentDir = java.io.File(currentFile).getParent()

    return currentDir

_currentDir = useThisVersion()
sysPath.append(_currentDir)

from psEntities import MainScriptEntities
from psEntities import PluginLocations
MainScriptEntities._currentPath = _currentDir
print('Current Pattern Scripts directory: ' + MainScriptEntities._currentPath)

'''Pattern Scripts Version 2.0.0 Pre Release b1'''

scriptName = 'OperationsPatternScripts.MainScript'
scriptRev = 20220101

class StartUp(jmri.jmrit.automat.AbstractAutomaton):
    '''Start the the Pattern Scripts plugin and add selected subroutines'''

    def init(self):

    # fire up logging
        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog.txt'
        self.psLog = logging.getLogger('PS')
        self.psLog.setLevel(10)
        logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        psFileHandler = logging.FileHandler(logPath, mode='w', encoding='utf-8')
        psFileHandler.setFormatter(logFileFormat)
        self.psLog.addHandler(psFileHandler)
        self.psLog.debug('Log File for Pattern Scripts Plugin - DEBUG level test message')
        self.psLog.info('Log File for Pattern Scripts Plugin - INFO level test message')
        self.psLog.warning('Log File for Pattern Scripts Plugin - WARNING level test message')
        self.psLog.error('Log File for Pattern Scripts Plugin - ERROR level test message')
        self.psLog.critical('Log File for Pattern Scripts Plugin - CRITICAL level test message')

        return

    def handle(self):
        '''Make and populate the Pattern Scripts control panel'''

        yTimeNow = time.time()
        MainScriptEntities.validateStubFile()
        MainScriptEntities.validateFileDestinationDirestories()
        MainScriptEntities.validateConfigFile()

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
        controlPanel, scrollPanel = MainScriptEntities.makeControlPanel()
        for subroutine in subroutineList:
            controlPanel.add(subroutine)
    # plug in the control panel to a location
        locationMatrix = MainScriptEntities.readConfigFile('LM')
        panelLocation = locationMatrix['PL']
        locationOptions = locationMatrix['LO']
        if (locationOptions[panelLocation][1]):
            getattr(PluginLocations, locationOptions[panelLocation][1])(scrollPanel)
    # fire up the help File
        self.psLog.info(locationOptions[panelLocation][0])
        self.psLog.info('Current Pattern Scripts directory: ' + MainScriptEntities._currentPath)
        self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])

        return False

StartUp().start()

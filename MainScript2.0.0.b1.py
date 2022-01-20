# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java
import logging
import time
from sys import path as sysPath

def useCurrentVersion():
    '''Only use the modules in this package'''

    fileRoot = jmri.util.FileUtil.getPreferencesPath()
    currentFile = str(jmri.util.FileUtil.findFiles('MainScript2.0.0.b1.py', fileRoot).pop())
    currentDir = java.io.File(currentFile).getParent()
    return currentDir

sysPath.append(useCurrentVersion())
import psEntities
psEntities.MainScriptEntities._currentPath = useCurrentVersion()

'''Pattern Scripts Version 2.0.0 Pre Release b1'''

scriptName = 'OperationsPatternScripts.MainScript'
scriptRev = 20211210

class StartUp(jmri.jmrit.automat.AbstractAutomaton):
    '''Start the the Pattern Scripts plugin and add selected subroutines'''

    def init(self):

    # fire up logging
        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternLog.txt'
        self.psLog = logging.getLogger('PS')
        self.psLog.setLevel(10)
        logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        psFileHandler = logging.FileHandler(logPath, mode='w', encoding='utf-8')
        psFileHandler.setFormatter(logFileFormat)
        self.psLog.addHandler(psFileHandler)
        self.psLog.debug('Log File for Pattern Scripts Plugin - debug level initialized')
        self.psLog.info('Log File for Pattern Scripts Plugin - info level initialized')
        self.psLog.warning('Log File for Pattern Scripts Plugin - warning level initialized')
    # fire up the config file
        if not (psEntities.MainScriptEntities.validateConfigFile()):
            psEntities.MainScriptEntities.writeNewConfigFile() # No love, just start over
            self.psLog.warning('New PatternConfig.json file created')

        return

    def handle(self):
        '''Make and populate the Pattern Scripts control panel'''

        yTimeNow = time.time()
        psEntities.MainScriptEntities.validateFileDestinationDirestories()
    # make a list of subroutines for the control panel
        subroutineList = []
        controlPanelConfig = psEntities.MainScriptEntities.readConfigFile('CP')
        for subroutineIncludes, bool in controlPanelConfig['SI'].items():
            if (bool):
            # import selected subroutines and add them to a list
                xModule = __import__(subroutineIncludes, fromlist=['Controller'])
                subroutineFrame = xModule.Controller.StartUp().makeSubroutineFrame()
                subroutinePanel = xModule.Controller.StartUp().makeSubroutinePanel()
                subroutineFrame.add(subroutinePanel)
                subroutineList.append(subroutineFrame)
                self.psLog.info(subroutineIncludes + ' subroutine added to control panel')
    # plug in the subroutine list into the control panel
        controlPanel, scrollPanel = psEntities.MainScriptEntities.makeControlPanel()
        for subroutine in subroutineList:
            controlPanel.add(subroutine)
    # plug in the control panel to a location
        locationMatrix = psEntities.MainScriptEntities.readConfigFile('LM')
        panelLocation = locationMatrix['PL']
        locationOptions = locationMatrix['LO']
        if (locationOptions[panelLocation][1]):
            getattr(psEntities.PluginLocations, locationOptions[panelLocation][1])(scrollPanel)
    # fire up the help File
        psEntities.MainScriptEntities.validateStubFile(scrollPanel.getLocale())
        self.psLog.info(locationOptions[panelLocation][0])
        self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])

        return False

StartUp().start()

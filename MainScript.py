# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import logging
import time
import os
from sys import path as sysPath
# print(os.getcwd() + 'jjjjjjjjjjjjjj')
# print(oPath.dirname(oPath.abspath(__file__)) + ' *@@@@@@@@@@@@@@@@@@@@*****')

sysPath.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import PluginLocations

class verifyPath():
    def __init__(self):
        from os import path as oPath

        return

    def main(self):
        from os import path as oPath
        print(oPath.dirname(oPath.abspath(__main__)) + ' *@@@@@@@@@@@@@@@@@@@@*****')
        return
verifyPath().main()
# print(dir(MainScriptEntities))

'''Pattern Scripts Version 2.0.0'''

scriptRev = 'OperationsPatternScripts.MainScript v20211210'

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
        if not (MainScriptEntities.validateConfigFile()):
            MainScriptEntities.writeNewConfigFile() # No love, just start over
            self.psLog.warning('New PatternConfig.json file created')

        return

    def handle(self):
        '''Make and populate the Pattern Scripts control panel'''

        yTimeNow = time.time()
        MainScriptEntities.validateDestinationDirestories()
    # make a list of subroutines for the control panel
        subroutineList = []
        controlPanelConfig = MainScriptEntities.readConfigFile('CP')
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
        controlPanel, scrollPanel = MainScriptEntities.makeControlPanel()
    # fire up the help File
        MainScriptEntities.validateStubFile(scrollPanel.getLocale())
        for subroutine in subroutineList:
            controlPanel.add(subroutine)
    # plug in the control panel to a location
        locationMatrix = MainScriptEntities.readConfigFile('LM')
        panelLocation = locationMatrix['PL']
        locationOptions = locationMatrix['LO']
        if (locationOptions[panelLocation][1]):
            getattr(PluginLocations, locationOptions[panelLocation][1])(scrollPanel)

        self.psLog.info(locationOptions[panelLocation][0])
        self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])

        return False

StartUp().start()

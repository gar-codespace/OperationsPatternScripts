# Main script that starts the plugin
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import logging
import time
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import PluginLocations

class StartUp(jmri.jmrit.automat.AbstractAutomaton):
    '''Start the the Pattern Scripts plugin and add selected subroutines'''

    scriptRev = 'OperationsPatternScripts.MainScript v20211120'

    def init(self):

    # fire up logging
        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternLog.txt'
        self.psLog = logging.getLogger('PS')
        self.psLog.setLevel(10)
        logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        psFileHandler = logging.FileHandler(logPath, mode='w', encoding='utf-8')
        psFileHandler.setFormatter(logFileFormat)
        self.psLog.addHandler(psFileHandler)
        self.psLog.info('Log File for Pattern Scripts Plugin')
    # fire up the config file
        self.psLog.info(MainScriptEntities.validateConfigFile())
        self.configFile = MainScriptEntities.readConfigFile('ControlPanel')
    # add the subroutines
        for subroutine, bool in self.configFile['scriptIncludes'].items():
            if (bool):
                path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts\\' + subroutine)
                import Controller
                self.psLog.info(subroutine + ' subroutine imported')
        return

    def handle(self):
        '''Make and populate the Pattern Scripts control panel'''

        yTimeNow = time.time()
    # create the subroutines for the control panel
        subroutineList = []
        for subroutine, bool in self.configFile['scriptIncludes'].items():
            if (bool):
                subroutineFrame = __import__(subroutine).Controller.StartUp().makeSubroutineFrame()
                subroutinePanel = __import__(subroutine).Controller.StartUp().makeSubroutinePanel()
                subroutineFrame.add(subroutinePanel)
                subroutineList.append(subroutineFrame)
                self.psLog.info(subroutine + ' subroutine added to control panel')
    # plug in subroutines into the control panel
        controlPanel, scrollPanel = MainScriptEntities.makeControlPanel()
        for subroutine in subroutineList:
            controlPanel.add(subroutine)
    # plug in the control panel to a location
        location = MainScriptEntities.readConfigFile('PluginLocation')
        try:
            pluginLocation = getattr(PluginLocations, location)()
            pluginLocation.add(scrollPanel)
            # pluginLocation.revalidate()
            self.psLog.info('control panel added to ' + location)
            self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])
        except AttributeError:
            print('No valid location found, plugin terminated')

        return False

StartUp().start()

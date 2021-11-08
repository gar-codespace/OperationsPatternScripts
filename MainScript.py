# Main script that starts the plugin
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import logging
import time
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import GpLogger
import PluginLocations

class StartUp(jmri.jmrit.automat.AbstractAutomaton):
    '''Start the the Pattern Scripts plugin and add selected subroutines'''

    def init(self):

    # fire up logging
        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternLog.txt'
        self.psLog = logging.getLogger('Pattern Scripts')
        self.psLog.setLevel(10)
        logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        psfh = logging.FileHandler(logPath, mode='w', encoding='utf-8')
        psfh.setFormatter(logFileFormat)
        self.psLog.addHandler(psfh)
    # fire up the config file
        result = MainScriptEntities.validateConfigFile()
        self.psLog.info('Log File for Pattern Scripts Plugin')
        self.psLog.info('PatternConfig.json file validated')
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
    # plug in subroutines into the control panel
        frameList = []
        for subroutine, bool in self.configFile['scriptIncludes'].items():
            if (bool):
                xPatternFrame = __import__(subroutine).Controller.StartUp().makeFrame()
                xPatternPanel = __import__(subroutine).Controller.StartUp().makePanel()
                xPatternFrame.add(xPatternPanel)
                frameList.append(xPatternFrame)
                self.psLog.info(subroutine + ' subroutine added to control panel')
    # populate the control panel
        controlPanel, scrollPanel = MainScriptEntities.makeControlPanel()
        for panel in frameList:
            controlPanel.add(panel)
    # plug in the control panel to a location
        location = MainScriptEntities.readConfigFile('PluginLocation')
        pluginLocation = getattr(PluginLocations, location)()
        pluginLocation.add(scrollPanel)
        self.psLog.info('control panel added to ' + location)
        self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])
        return False

StartUp().start()

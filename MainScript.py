# Main script that starts the plugin
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
from apps import Apps
import logging
import time
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import PluginLocations

class StartUp(jmri.jmrit.automat.AbstractAutomaton):
    '''Start the the Pattern Scripts plugin and add selected subroutines'''

    scriptRev = 'OperationsPatternScripts.MainScript v20211125'

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
        if not (MainScriptEntities.validateConfigFile()):
            MainScriptEntities.writeNewConfigFile() # No love, just start over
            self.psLog.warning('PatternConfig.json missing or corrupt, new file created')
        self.configFile = MainScriptEntities.readConfigFile('ControlPanel')
    # import the subroutines
        for subroutine, bool in self.configFile['scriptIncludes'].items():
            if (bool):
                path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts\\' + subroutine)
                import Controller
                self.psLog.info(subroutine + ' subroutine imported')

        return

    def homeButtonClick(self, event):
        '''The Pattern Scripts button on the Panel Pro home screen'''

        piList = MainScriptEntities.readConfigFile('PluginLocation')
        piOptions = piList['locationOptions']
        piLocation = piList['PL']
        piWindowLocation = getattr(PluginLocations, piOptions[piLocation])()
        piWindowLocation.add(self.scrollPanel)
        piWindowLocation.setVisible(True)
        self.psLog.info('Subroutine control panel created on ' + piOptions[piLocation])
        print(StartUp.scriptRev)

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
        controlPanel, self.scrollPanel = MainScriptEntities.makeControlPanel()
        for subroutine in subroutineList:
            controlPanel.add(subroutine)
    # plug in the control panel to a location
        homePanelButton = MainScriptEntities.makeButton()
        homePanelButton.actionPerformed = self.homeButtonClick
        Apps.buttonSpace().add(homePanelButton)
        Apps.buttonSpace().revalidate()
        self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])

        return False

StartUp().start()

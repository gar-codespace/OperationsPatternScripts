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

    scriptRev = 'OperationsPatternScripts.MainScript v20211125'

    def init(self):

    # fire up logging
        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternLog.txt'
        self.psLog = logging.getLogger('PS')
        self.psLog.setLevel(20)
        print(jmri.jmrit.operations.setup.Setup.getBuildReportLevel()) # 1, 3, 5, 7
        logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        psFileHandler = logging.FileHandler(logPath, mode='w', encoding='utf-8')
        psFileHandler.setFormatter(logFileFormat)
        self.psLog.addHandler(psFileHandler)
        self.psLog.info('Log File for Pattern Scripts Plugin')
    # fire up the config file
        if not (MainScriptEntities.validateConfigFile()):
            MainScriptEntities.writeNewConfigFile() # No love, just start over
            self.psLog.warning('PatternConfig.json missing or corrupt, new file created')

        return

    def handle(self):
        '''Make and populate the Pattern Scripts control panel'''

        yTimeNow = time.time()
    # create the subroutines for the control panel
        subroutineList = []
        configFile = MainScriptEntities.readConfigFile('CP')
        for subroutine, bool in configFile['SI'].items():
            if (bool):
            # import selected subroutines and add them to a list
                xModule = __import__(subroutine, fromlist=['Controller'])
                subroutineFrame = xModule.Controller.StartUp().makeSubroutineFrame()
                subroutinePanel = xModule.Controller.StartUp().makeSubroutinePanel()
                subroutineFrame.add(subroutinePanel)
                subroutineList.append(subroutineFrame)
                self.psLog.info(subroutine + ' subroutine added to control panel')
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

        self.psLog.info(locationOptions[panelLocation][0])
        self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])

        return False

StartUp().start()

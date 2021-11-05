# Main script that starts the plugin
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import GpLogger
import PluginLocations

class StartUp(jmri.jmrit.automat.AbstractAutomaton):
    '''Start the the Pattern Scripts plugin and add selected modules'''

    def init(self):
        self.logger = GpLogger.gpLogging('TrackPattern')
        result = MainScriptEntities.validateConfigFile()
        # log the result
        self.configFile = MainScriptEntities.readConfigFile('ControlPanel')
        for subroutine, bool in self.configFile['scriptIncludes'].items():
            if (bool):
                path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts\\' + subroutine)
                import Controller
        return

    def handle(self):
        '''Make and populate the Pattern Scripts control panel'''

    # create the subroutines that go into the control panel
        frameList = []
        for subroutine, bool in self.configFile['scriptIncludes'].items():
            if (bool):
                xPatternFrame = __import__(subroutine).Controller.StartUp().makeFrame()
                xPatternPanel = __import__(subroutine).Controller.StartUp().makePanel()
                xPatternFrame.add(xPatternPanel)
                frameList.append(xPatternFrame)
    # populate the control panel
        controlPanel, scrollPanel = MainScriptEntities.makeControlPanel()
        for panel in frameList:
            controlPanel.add(panel)
    # add the control panel to a location
        location = MainScriptEntities.readConfigFile('PluginLocation')
        pluginLocation = getattr(PluginLocations, location)()
        pluginLocation.add(scrollPanel)
        return False

StartUp().start()

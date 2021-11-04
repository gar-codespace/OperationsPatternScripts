import jmri
import javax.swing
import java.awt
# import json
# from json import loads as jLoads, dumps as jDumps
# from apps import Apps
from os import path as oPath
from shutil import copy as sCopy
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import TrackPattern.Controller
import TrackPattern.View

class ValidateConfigFile:
    '''Checks for a config file and adds one if missing'''

    def __init__(self):
        self.profilePath = jmri.util.FileUtil.getProfilePath()
        return

    def validate(self):
        copyTo = self.profilePath + 'operations\\PatternConfig.json'
        if not (oPath.exists(copyTo)):
            copyFrom = jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts\\PatternConfig.json'
            sCopy(copyFrom, copyTo)
            print(u'Configuration file created')
        else:
            print(u'Configuration file found')
        return

class AddControlPanelToThisLocation():
    '''Add the whole panel to some place'''

    def __init__(self):
        pass
        return

    def trainsTable(self):

        return  jmri.jmrit.operations.trains.TrainsTableFrame()

class StartUp(jmri.jmrit.automat.AbstractAutomaton):
    '''Start the the Pattern Scripts program and add selected modules'''

    def init(self):
        ValidateConfigFile().validate()
        self.configFile = MainScriptEntities.readConfigFile()
        return

    def makeControlPanel(self):
        '''Create the control panel, with a scroll bar, that all sub panels go into
        This holds trackPatternPanel and future panels'''

        controlPanel = javax.swing.JPanel() # The whole panel that everything goes into
        scrollPanel = javax.swing.JScrollPane(controlPanel) # and that goes into a scroll pane
        scrollPanel.border = javax.swing.BorderFactory.createLineBorder(java.awt.Color.GRAY)
        scrollPanel.setPreferredSize(java.awt.Dimension(self.configFile['PW'], self.configFile['PH']))
        scrollPanel.setMaximumSize(scrollPanel.getPreferredSize())
        return controlPanel, scrollPanel

    def handle(self):
        '''Make and populate the track pattern panel'''

        self.configFile = self.configFile['ControlPanel']
    # create the sub panels that go into the control panel
        trackPatternFrame = TrackPattern.Controller.StartUp().makeFrame()
        trackPatternPanel = TrackPattern.Controller.StartUp().makePanel()
        trackPatternFrame.add(trackPatternPanel)
    # create and populate the control panel
        controlPanel, scrollPanel = self.makeControlPanel()
        controlPanel.add(trackPatternFrame)
        panelLocation = AddControlPanelToThisLocation().trainsTable()
        panelLocation.add(scrollPanel)
        return False

StartUp().start()

import jmri
# import javax.swing
# import java.awt
from os import system
# import system
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsTrackPattern')
import MainScriptEntities
import TrackPattern.MakeTrackPatternPanel

class manageGui:
    '''At startup create the GUI elements'''

    scriptRev = 'View/manageGui rev.20211015'

    def __init__(self, panel=None, controls=None):
        '''Track Pattern panel'''

        configFile = MainScriptEntities.readConfigFile()
        self.configFile = configFile['TP']
        self.panel = panel
        self.controls = controls

        return

    def updatePanel(self, panel):
        ''' Makes a new panel from the config file and replaces the currentpanel with the new panel'''

        newView, newControls = TrackPattern.MakeTrackPatternPanel.TrackPatternPanel().makePatternControls()
        panel.removeAll()
        panel.add(newView)
        panel.revalidate()
        # panel.repaint()

        return newView, newControls

    def makeFrame(self):
        '''Makes the title frame that allthe track pattern controls go into'''

        return TrackPattern.MakeTrackPatternPanel.TrackPatternPanel().makePatternFrame()

    def makePanel(self):
        '''Make the track pattern controls'''

        return TrackPattern.MakeTrackPatternPanel.TrackPatternPanel().makePatternControls()

    print(scriptRev)

def displayTextSwitchlist(location):
    '''Opens the text switchlist to Notepad or other'''

    textSwitchList = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\Track Pattern (' + location + ').txt'
    system(MainScriptEntities.systemInfo() + textSwitchList)

    return

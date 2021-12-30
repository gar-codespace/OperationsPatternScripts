# coding=utf-8
# Extended ìÄÅÉî
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import jmri.util
import jmri.util.HelpUtil
import java.awt
import java.awt.event
import javax.swing
from apps import Apps

'''Different locations for this plugin'''

scriptRev = 'OperationsPatternScripts.PluginLocations v20211125'

class PatternScriptsWindowListener(java.awt.event.WindowListener):
    '''Listener to respond to window operations'''

    def __init__(self, button):

        self.homePanelButton = button
        return

    def windowOpened(self, WINDOW_OPENED):
        for xFrame in jmri.util.JmriJFrame.getFrameList(): # tonsil
            pass
        return
    def windowActivated(self, WINDOW_ACTIVATED):
        return
    def windowDeactivated(self, WINDOW_DEACTIVATED):
        return
    def windowClosed(self, WINDOW_CLOSED):
        self.homePanelButton.setEnabled(True)
        return
    def windowClosing(self, WINDOW_CLOSING):
        return

def makeButton():

    return javax.swing.JButton(text = u'Pattern Scripts')

def panelPro(scrollPanel):
    '''Add the plugin to the Panel Pro home screen
NOTE: This location does not support DecoderPro'''

    Apps.buttonSpace().add(scrollPanel)
    Apps.buttonSpace().revalidate()
    print(scriptRev)

    return

def uniqueWindow(scrollPanel):
    '''makes a window to display the control panel'''

    def homeButtonClick(MOUSE_CLICKED):
        '''The Pattern Scripts button on the Panel Pro frame'''

        homePanelButton.setEnabled(False)
        uniqueWindow.setVisible(True)
        # print(jmri.util.JmriJFrame.getFrameList())
        # print(scrollPanel.getSize())
        return

    homePanelButton = makeButton()
    homePanelButton.actionPerformed = homeButtonClick
    Apps.buttonSpace().add(homePanelButton)
    Apps.buttonSpace().revalidate()

    # jmri.util.HelpUtil.createStubFile('ttt.rrr.sss', 'en')
    uniqueWindow = jmri.util.JmriJFrame(u'Pattern Scripts')
    uniqueWindow.addWindowListener(PatternScriptsWindowListener(homePanelButton))
    uniqueWindow.addHelpMenu('stub', False) # false means only window help
    uniqueWindow.add(scrollPanel)
    uniqueWindow.pack()



    print(scriptRev)

    return

def trainsTable(scrollPanel):
    '''Add the plugin to the bottom of the trains window'''

    jmri.jmrit.operations.trains.TrainsTableFrame().add(scrollPanel)
    print(scriptRev)

    return

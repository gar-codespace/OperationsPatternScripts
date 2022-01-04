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

'''Different locations for the Pattern Script plugin.
This script must be self contained.'''

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

class MakePatternScriptsWindow():
    '''Makes a JFrame that the control panel is set into'''

    def __init__(self, scrollPanel, button):

        self.controlPanel = scrollPanel
        self.button = button
        self.uniqueWindow = jmri.util.JmriJFrame(u'Pattern Scripts')
        return

    def helpItemSelected(self, ACTION_PERFORMED):

        helpStubPath = 'file:///' + jmri.util.FileUtil.getPreferencesPath() + 'jmrihelp\\psStub.html'
        fixPath1 = helpStubPath.replace('\\', '/')
        fixPath2 = fixPath1.replace(' ', '%20')
        jmri.util.HelpUtil.openWebPage(fixPath2)

        return

    def makeWindow(self):

        helpMenuItem = javax.swing.JMenuItem(u'Window Help...')
        helpMenuItem.addActionListener(self.helpItemSelected)

        helpMenu = javax.swing.JMenu(u'Help')
        helpMenu.add(helpMenuItem)

        toolsMenu = javax.swing.JMenu(u'Tools')
        toolsMenu.add(jmri.jmrit.operations.setup.OptionAction())
        toolsMenu.add(jmri.jmrit.operations.setup.PrintOptionAction())
        toolsMenu.add(jmri.jmrit.operations.setup.BuildReportOptionAction())

        psMenuBar = javax.swing.JMenuBar()
        psMenuBar.add(toolsMenu)
        psMenuBar.add(jmri.jmrit.operations.OperationsMenu())
        psMenuBar.add(jmri.util.WindowMenu(self.uniqueWindow))
        psMenuBar.add(helpMenu)
        # jmri.util.HelpUtil.helpMenu(psMenuBar, 'psStub', False)

        self.uniqueWindow.addWindowListener(PatternScriptsWindowListener(self.button))
        self.uniqueWindow.setJMenuBar(psMenuBar)
        self.uniqueWindow.add(self.controlPanel)
        self.uniqueWindow.pack()

        return self.uniqueWindow.setVisible(True)

def panelPro(scrollPanel):
    '''Add the plugin to the Panel Pro home screen
NOTE: This location does not support DecoderPro'''

    Apps.buttonSpace().add(scrollPanel)
    Apps.buttonSpace().revalidate()
    print(scriptRev)

    return

def panelProButton(scrollPanel):
    '''makes a button on the PanelPro frame'''

    def homeButtonClick(MOUSE_CLICKED):

        homePanelButton.setEnabled(False)
        psWindow = MakePatternScriptsWindow(scrollPanel, homePanelButton)
        psWindow.makeWindow()
        return

    homePanelButton = javax.swing.JButton(text = u'Pattern Scripts')
    homePanelButton.actionPerformed = homeButtonClick
    Apps.buttonSpace().add(homePanelButton)
    Apps.buttonSpace().revalidate()

    print(scriptRev)

    return

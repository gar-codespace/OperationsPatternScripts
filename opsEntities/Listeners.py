"""
Main script listeners.
"""

from opsEntities import PSE
from opsBundle import Bundle

SCRIPT_NAME = 'OperationsPatternScripts.opsEntities.Listeners'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.OE.Listeners')


def patternScriptsButtonAction(MOUSE_CLICKED):
    """The Pattern Scripts button on the Panel Pro frame."""

    _psLog.debug(MOUSE_CLICKED)

    PSE.buildThePlugin()

    return

def ptItemSelected(TRANSLATE_PLUGIN_EVENT):
    """Pattern Scripts/Tools/Translate Plugin"""

    _psLog.debug(TRANSLATE_PLUGIN_EVENT)

    textBundles = Bundle.getAllTextBundles()
    Bundle.makePluginBundle(textBundles)

    Bundle.makeHelpBundle()
    Bundle.makeHelpPage()

    PSE.closePsWindow()
    PSE.buildThePlugin()

    _psLog.info('Pattern Scripts plugin translated')
    _psLog.info('Pattern Scripts plugin restarted')

    return

def rsItemSelected(RESTART_PLUGIN_EVENT):
    """Pattern Scripts/Tools/Restart Plugin"""

    _psLog.debug(RESTART_PLUGIN_EVENT)

    PSE.deleteConfigFile()

    PSE.closePsWindow()
    PSE.buildThePlugin()

    _psLog.info('Pattern Scripts plugin restarted')

    return

def helpItemSelected(OPEN_HELP_EVENT):
    """Pattern Scripts/Help/Window help..."""

    _psLog.debug(OPEN_HELP_EVENT)

    stubFileTarget = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getPreferencesPath(), 'jmrihelp', PSE.psLocale()[:2], 'psStub.html')
    stubUri = PSE.JAVA_IO.File(stubFileTarget).toURI()
    if PSE.JAVA_IO.File(stubUri).isFile():
        PSE.JAVA_AWT.Desktop.getDesktop().browse(stubUri)
    else:
        _psLog.warning('Help file not found')

    return

def logItemSelected(OPEN_LOG_EVENT):
    """Pattern Scripts/Help/View Log"""

    _psLog.debug(OPEN_LOG_EVENT)

    patternLog = PSE.makePatternLog()

    logFileTarget = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'buildstatus', 'PatternScriptsLog_temp.txt')

    PSE.genericWriteReport(logFileTarget, patternLog)
    PSE.genericDisplayReport(logFileTarget)

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

    return

def ghItemSelected(OPEN_GH_EVENT):
    """Pattern Scripts/Help/GitHub Page"""

    _psLog.debug(OPEN_GH_EVENT)

    ghURL = 'https://github.com/gar-codespace/OperationsPatternScripts'
    PSE.JMRI.util.HelpUtil.openWebPage(ghURL)

    return

def ecItemSelected(OPEN_EC_EVENT):
    """Pattern Scripts/Help/Edit Config File"""

    _psLog.debug(OPEN_EC_EVENT)

    configTarget = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'PatternConfig.json')

    if PSE.JAVA_IO.File(configTarget).isFile():
        PSE.genericDisplayReport(configTarget)
    else:
        _psLog.warning('Not found: ' + configTarget)

    return

def ofItemSelected(OPEN_OF_EVENT):
    """Pattern Scripts/Help/Operations Folder"""

    _psLog.debug(OPEN_OF_EVENT)

    opsFolderPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations')

    opsFolder = PSE.JAVA_IO.File(opsFolderPath)
    if opsFolder.exists():
        PSE.JAVA_AWT.Desktop.getDesktop().open(opsFolder)
    else:
        _psLog.warning('Not found: ' + opsFolderPath)

    return


class PatternScriptsWindow(PSE.JAVA_AWT.event.WindowListener):
    """Listener to respond to the plugin window operations.
        Might be expanded in v3.
        """

    def __init__(self):

        return

    def windowClosed(self, WINDOW_CLOSED):

        button = PSE.getPsButton()
        button.setEnabled(True)

        return

    def windowClosing(self, WINDOW_CLOSING):

        PSE.updateWindowParams(WINDOW_CLOSING.getSource())
        PSE.closeSetCarsWindows()
        WINDOW_CLOSING.getSource().dispose()

        return

    def windowOpened(self, WINDOW_OPENED):

        button = PSE.getPsButton()
        button.setEnabled(False)

        return

    def windowActivated(self, WINDOW_ACTIVATED):

        PSE.updateYearModeled()

        return

    def windowIconified(self, WINDOW_ICONIFIED):
        return
    def windowDeiconified(self, WINDOW_DEICONIFIED):
        return

    def windowDeactivated(self, WINDOW_DEACTIVATED):
        return

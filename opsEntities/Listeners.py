"""
Main Script listeners.
"""

from opsEntities import PSE
from opsBundle import Bundle

SCRIPT_NAME = 'OperationsPatternScripts.opsEntities.Listeners'
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.OE.Listeners')


"""Tools menu items"""


def ptItemSelected(TRANSLATE_PLUGIN_EVENT):
    """
    Pattern Scripts/Tools/Translate Plugin.
    """

    _psLog.debug(TRANSLATE_PLUGIN_EVENT)

    Bundle.translateBundles()

    xModule = __import__('MainScript')
    xModule.restartThePlugin()

    _psLog.info('Pattern Scripts plugin translated')

    return

def ecItemSelected(OPEN_EC_EVENT):
    """
    Pattern Scripts/Help/Edit Config File.
    """

    _psLog.debug(OPEN_EC_EVENT)

    configTarget = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'configFile.json')

    PSE.genericDisplayReport(configTarget)

    return

def rsItemSelected(RESTART_PLUGIN_EVENT):
    """
    Pattern Scripts/Tools/Restart From Default.
    """

    _psLog.debug(RESTART_PLUGIN_EVENT)

    PSE.deleteConfigFile()

    xModule = __import__('MainScript')
    xModule.restartThePlugin()

    return


"""Help menu items"""


def helpItemSelected(OPEN_HELP_EVENT):
    """
    Pattern Scripts/Help/Window help...
    """

    _psLog.debug(OPEN_HELP_EVENT)

    stubFileTarget = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getPreferencesPath(), 'jmrihelp', PSE.psLocale()[:2], 'psStub.html')
    stubUri = PSE.JAVA_IO.File(stubFileTarget).toURI()
    if PSE.JAVA_IO.File(stubUri).isFile():
        PSE.JAVA_AWT.Desktop.getDesktop().browse(stubUri)
    else:
        _psLog.warning('Help file not found')

    return

def ghItemSelected(OPEN_GH_EVENT):
    """
    Pattern Scripts/Help/GitHub Page.
    """

    _psLog.debug(OPEN_GH_EVENT)

    gitHubUrl = PSE.readConfigFile('Main Script')['CP']['GP']

    try:
        PSE.JMRI.util.HelpUtil.openWebPage(gitHubUrl)
    except PSE.JMRI.JmriException as e:
        print('Git Hub page error: ' + e.getMessage())
        _psLog.warning('Git Hub page error: ' + e.getMessage())

    return

def ofItemSelected(OPEN_OF_EVENT):
    """
    Pattern Scripts/Help/Operations Folder.
    """

    _psLog.debug(OPEN_OF_EVENT)

    opsFolderPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations')

    opsFolder = PSE.JAVA_IO.File(opsFolderPath)
    if opsFolder.exists():
        PSE.JAVA_AWT.Desktop.getDesktop().open(opsFolder)
    else:
        _psLog.warning('Not found: ' + opsFolderPath)

    return

def logItemSelected(OPEN_LOG_EVENT):
    """
    Pattern Scripts/Help/View Log.
    """

    _psLog.debug(OPEN_LOG_EVENT)

    patternLog = PSE.makePatternLog()

    logFileTarget = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'buildstatus', 'PatternScriptsLog_temp.txt')

    PSE.genericWriteReport(logFileTarget, patternLog)
    PSE.genericDisplayReport(logFileTarget)

    return


class PatternScriptsWindow(PSE.JAVA_AWT.event.WindowListener):
    """
    Listener to respond to the plugin window operations.
    """

    def __init__(self):
        
        pass

    def windowClosed(self, WINDOW_CLOSED):

        _psLog.debug(WINDOW_CLOSED)

        PSE.getPsButton().setEnabled(True)

        return

    def windowClosing(self, WINDOW_CLOSING):

        _psLog.debug(WINDOW_CLOSING)

        PSE.updateWindowParams(WINDOW_CLOSING.getSource())
        PSE.closeWindowByName('popupFrame')
        PSE.closeWindowByName('setCarsWindow')
        PSE.remoteCalls('shutdownCalls')

        WINDOW_CLOSING.getSource().dispose()
            
        return

    def windowOpened(self, WINDOW_OPENED):

        _psLog.debug(WINDOW_OPENED)

        PSE.remoteCalls('startupCalls')
        
        PSE.getPsButton().setEnabled(False)

        return

    def windowActivated(self, WINDOW_ACTIVATED):

        _psLog.debug(WINDOW_ACTIVATED)

        WINDOW_ACTIVATED.getSource().firePropertyChange('opsWindowActivated', False, True)

        return

    def windowIconified(self, WINDOW_ICONIFIED):
        return
    def windowDeiconified(self, WINDOW_DEICONIFIED):
        return
    def windowDeactivated(self, WINDOW_DEACTIVATED):
        return

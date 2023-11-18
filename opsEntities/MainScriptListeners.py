"""
Listeners attached to the Main Script.
"""

from opsEntities import PSE
from opsBundle import Bundle

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.OE.MainScriptListeners')


"""Tools menu items"""


def dropDownMenuItem(EVENT):
    """
    menu item-Tools/Show/Hide <Subroutine>
    """

    _psLog.debug(EVENT)

    configFile = PSE.readConfigFile()
    subroutineName = EVENT.getSource().getName()

    if configFile[subroutineName]['SV']: # Hide this subroutine
        menuText = '{} {}'.format(PSE.getBundleItem('Show'), subroutineName)
        configFile[subroutineName].update({'SV':False})
        _psLog.info('Hide ' + subroutineName)
    else: # Show this subroutine
        menuText = '{} {}'.format(PSE.getBundleItem('Hide'), subroutineName)
        configFile[subroutineName].update({'SV':True})
        _psLog.info('Show ' + subroutineName)

    EVENT.getSource().setText(menuText)

    PSE.writeConfigFile(configFile)
    PSE.repaintPatternScriptsFrame()

    return

def erItemSelected(TRANSLATE_PLUGIN_EVENT):
    """
    Pattern Scripts/Tools/Extended reports on.
    """

    _psLog.debug(TRANSLATE_PLUGIN_EVENT)

    configFile = PSE.readConfigFile()

    menuText = PSE.getBundleItem('Extended reports on')
    if not configFile['Main Script']['CP']['ER']:
        menuText = PSE.getBundleItem('Extended reports off')
    TRANSLATE_PLUGIN_EVENT.getSource().setText(menuText)
    
    configFile['Main Script']['CP']['ER'] = not configFile['Main Script']['CP']['ER']

    PSE.writeConfigFile(configFile)
    PSE.repaintPatternScriptsFrame()

    return

def ptItemSelected(TRANSLATE_PLUGIN_EVENT):
    """
    Pattern Scripts/Tools/Translate Plugin.
    """

    _psLog.debug(TRANSLATE_PLUGIN_EVENT)

    Bundle.translateBundles()
    # Bundle.translateHelpHtml()

    PSE.closeWindowByName('PatternScriptsFrame')
    PSE.getPsButton().setEnabled(True)

    xModule = PSE.IM('MainScript')
    xModule.makePsPlugin()

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

    PSE.closeWindowByName('PatternScriptsFrame')
    PSE.deleteConfigFile()
    PSE.getPsButton().setEnabled(True)

    xModule = PSE.IM('MainScript')
    xModule.makePsPlugin()

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

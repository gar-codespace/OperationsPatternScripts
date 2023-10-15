"""
Main Script listeners.
"""

from opsEntities import PSE
from opsBundle import Bundle

SCRIPT_NAME = 'OperationsPatternScripts.opsEntities.Listeners'
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.OE.Listeners')


class PatternScriptsFrameListener(PSE.JAVA_AWT.event.WindowListener):
    """
    Listener to respond to the plugin window operations.
    """

    def __init__(self):
        
        pass

    def windowOpened(self, WINDOW_OPENED):
        """
        When the plugin window is opened, add the listeners needed for the plugin and initialize the subroutines.
        """

        _psLog.debug(WINDOW_OPENED)

        addSubroutineListeners()

        for subroutine in PSE.getSubroutineDirs():
            xModule = 'Subroutines_Activated.{}'.format(subroutine)
            package = __import__(xModule, fromlist=['Model'], level=-1)
            package.Model.initializeSubroutine()

        return

    def windowActivated(self, WINDOW_ACTIVATED):
        """
        When the plugin window is active, refresh all the included subroutines.
        """

        _psLog.debug(WINDOW_ACTIVATED)

        for subroutine in PSE.getSubroutineDirs():
            xModule = 'Subroutines_Activated.{}'.format(subroutine)
            package = __import__(xModule, fromlist=['Model'], level=-1)
            package.Model.refreshSubroutine()

        return

    def windowClosing(self, WINDOW_CLOSING):
        """
        As the plugin window is closing, remove all the needed listeners,
        and update the plugin frame parameters.
        """

        _psLog.debug(WINDOW_CLOSING)

        removeSubroutineListeners()
        
        PSE.updateWindowParams(WINDOW_CLOSING.getSource())
        PSE.removePSPropertyListeners()
        PSE.removePSWindowListeners()

        PSE.getPsButton().setEnabled(True)
            
        return

    def windowClosed(self, WINDOW_CLOSED):
        return
    def windowIconified(self, WINDOW_ICONIFIED):
        return
    def windowDeiconified(self, WINDOW_DEICONIFIED):
        return
    def windowDeactivated(self, WINDOW_DEACTIVATED):
        return


def addSubroutineListeners():
    """
    mini controller.
    """

    addTrainListener()
    addTrainsTableListener()
    addLocationListener()
    addLocationsTableListener()
    addDivisionListener()
    addDivisionsTableListener()

    print('Main Script.Listeners.addSubroutineListeners')
    _psLog.debug('Main Script.Listeners.addSubroutineListeners')

    return

def removeSubroutineListeners():
    """
    Mini controller.
    """

    removeTrainListener()
    removeTrainsTableListener()
    removeLocationListener()
    removeLocationsTableListener()
    removeDivisionListener()
    removeDivisionsTableListener()

    print('Main Script.Listeners.removeSubroutineListeners')
    _psLog.debug('Main Script.Listeners.removeSubroutineListeners')

    return

def addTrainListener():

    for train in PSE.TM.getTrainsByIdList():
        train.addPropertyChangeListener(TrainsPropertyChange())

        _psLog.debug('Main Script.Listeners.addTrainListener: ' + train.toString())

    return

def addTrainsTableListener():

    PSE.TM.addPropertyChangeListener(TrainsPropertyChange())

    _psLog.debug('Main Script.Listeners.addTrainsTableListener')

    return

def addLocationListener():

    for location in PSE.LM.getList():
        location.addPropertyChangeListener(LocationsPropertyChange())

        _psLog.debug('Main Script.Listeners.addLocationListener: ' + location.toString())

    return

def addLocationsTableListener():

    PSE.LM.addPropertyChangeListener(LocationsPropertyChange())

    _psLog.debug('Main Script.Listeners.addLocationsTableListener')

    return

def addDivisionListener():

    for division in PSE.DM.getList():
        division.addPropertyChangeListener(LocationsPropertyChange())

        _psLog.debug('Main Script.Listeners.addDivisionListener: ' + division.toString())

    return

def addDivisionsTableListener():

    PSE.DM.addPropertyChangeListener(LocationsPropertyChange())

    _psLog.debug('Main Script.Listeners.addDivisionsTableListener')

    return

def removeTrainListener():

    for train in PSE.TM.getTrainsByIdList():
        for listener in train.getPropertyChangeListeners():
            if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'TrainsPropertyChange' in listener.toString():
                train.removePropertyChangeListener(listener)

                _psLog.debug('Main Script.Listeners.removeTrainListener: ' + train.toString())

    return

def removeTrainsTableListener():

    for listener in PSE.TM.getPropertyChangeListeners():
        if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'TrainsPropertyChange' in listener.toString():
            PSE.TM.removePropertyChangeListener(listener)

            _psLog.debug('Main Script.Listeners.removeTrainsTableListener')

    return

def removeLocationListener():

    for location in PSE.LM.getList():
        for listener in location.getPropertyChangeListeners():
            if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'LocationsPropertyChange' in listener.toString():
                location.removePropertyChangeListener(listener)

                _psLog.debug('Main Script.Listeners.removeLocationListener: ' + location.toString())

    return

def removeLocationsTableListener():

    for listener in PSE.LM.getPropertyChangeListeners():
        if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'LocationsPropertyChange' in listener.toString():
            PSE.LM.removePropertyChangeListener(listener)

            _psLog.debug('Main Script.Listeners.removeLocationsTableListener')

    return

def removeDivisionListener():

    for division in PSE.DM.getList():
        for listener in division.getPropertyChangeListeners():
            if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'LocationsPropertyChange' in listener.toString():
                division.removePropertyChangeListener(listener)

                _psLog.debug('Main Script.Listeners.removeDivisionListener: ' + division.toString())
    return

def removeDivisionsTableListener():

    for listener in PSE.DM.getPropertyChangeListeners():
        if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'LocationsPropertyChange' in listener.toString():
            PSE.DM.removePropertyChangeListener(listener)

            _psLog.debug('Main Script.Listeners.removeDivisionsTableListener')

    return


class TrainsPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Events that are triggered with changes to JMRI Trains.
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        sourceName = str(PROPERTY_CHANGE_EVENT.source)
        propertyName = PROPERTY_CHANGE_EVENT.getPropertyName()
        logMessage = 'Main Script.Listeners.TrainsPropertyChange- {} {}'.format(sourceName, propertyName)

        if PROPERTY_CHANGE_EVENT.propertyName == 'TrainsListLength':
        # Fired from JMRI.

            removeTrainListener()
            addTrainListener()

            _psLog.debug(logMessage)

        if PROPERTY_CHANGE_EVENT.propertyName == 'TrainBuilt' and PROPERTY_CHANGE_EVENT.newValue == True:
        # Fired from JMRI.
            print('TrainBuilt')
            train = PROPERTY_CHANGE_EVENT.getSource()

            if 'Scanner' in PSE.readConfigFile()['Main Script']['SL']:
                xModule = 'Subroutines_Activated.Scanner'
                package = __import__(xModule, fromlist=['Model'], level=-1)
                package.Model.modifyTrainManifest(train)           
            
            if 'o2o' in PSE.readConfigFile()['Main Script']['SL']:
                xModule = 'Subroutines_Activated.o2o'
                package = __import__(xModule, fromlist=['ModelWorkEvents'], level=-1)
                package.ModelWorkEvents.o2oWorkEvents().getManifest(train)

            _psLog.debug(logMessage)

        if PROPERTY_CHANGE_EVENT.propertyName == 'patternsSwitchList' and PROPERTY_CHANGE_EVENT.newValue == True:
        # Fired from OPS

            print('patternsSwitchList')

            _psLog.debug(logMessage)

        return

class LocationsPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Events that are triggered with changes to JMRI Locations.
    """

    def __init__(self):

        pass
    
    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionsListLength':
        # Fired from JMRI.
            for subroutine in PSE.getSubroutineDirs():
                xModule = 'Subroutines_Activated.{}'.format(subroutine)
                package = __import__(xModule, fromlist=['Model'], level=-1)
                package.Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionName':
        # Fired from JMRI.
            for subroutine in PSE.getSubroutineDirs():
                xModule = 'Subroutines_Activated.{}'.format(subroutine)
                package = __import__(xModule, fromlist=['Model'], level=-1)
                package.Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationsListLength':
        # Fired from JMRI.
            for subroutine in PSE.getSubroutineDirs():
                xModule = 'Subroutines_Activated.{}'.format(subroutine)
                package = __import__(xModule, fromlist=['Model'], level=-1)
                package.Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationName':
        # Fired from JMRI.
            for subroutine in PSE.getSubroutineDirs():
                xModule = 'Subroutines_Activated.{}'.format(subroutine)
                package = __import__(xModule, fromlist=['Model'], level=-1)
                package.Model.resetSubroutine()
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'extendedDetails':
        # Fired from OPS
            for subroutine in PSE.getSubroutineDirs():
                xModule = 'Subroutines_Activated.{}'.format(subroutine)
                package = __import__(xModule, fromlist=['Model'], level=-1)
                package.Model.refreshSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'jmriDataSets':
        # Fired from OPS
            for subroutine in PSE.getSubroutineDirs():
                xModule = 'Subroutines_Activated.{}'.format(subroutine)
                package = __import__(xModule, fromlist=['Model'], level=-1)
                package.Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        return


"""Tools menu items"""


def dropDownMenuItem(EVENT):
    """
    menu item-Tools/Show/Hide <Subroutine>
    """

    _psLog.debug(EVENT)

    configFile = PSE.readConfigFile()

    subroutineName = EVENT.getSource().toString()

    if configFile[subroutineName]['SV']: # Hide this subroutine
        menuText = PSE.getBundleItem('Show') + ' ' + subroutineName
        configFile[subroutineName].update({'SV':False})
        _psLog.info('Hide ' + subroutineName)
    else: # Show this subroutine
        menuText = PSE.getBundleItem('Hide') + ' ' + subroutineName
        configFile[subroutineName].update({'SV':True})
        _psLog.info('Show ' + subroutineName)

    EVENT.getSource().setText(menuText)
    PSE.writeConfigFile(configFile)

    PSE.repaintPatternScriptsFrame()

    return

def ptItemSelected(TRANSLATE_PLUGIN_EVENT):
    """
    Pattern Scripts/Tools/Translate Plugin.
    """

    _psLog.debug(TRANSLATE_PLUGIN_EVENT)

    Bundle.translateBundles()
    Bundle.translateHelpHtml()

    xModule = PSE.IM('MainScript')
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

    # PSE.LM.firePropertyChange('windowClosing', False, True)

    PSE.closeWindowByName('PatternScriptsFrame')
    PSE.deleteConfigFile()
    # PSE.makeNewConfigFile()
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

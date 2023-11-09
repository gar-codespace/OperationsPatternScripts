"""
'Plugin' or 'Global' level listeners.
Listeners for OPS interoperability.
Listeners for JMRI events.
"""

from opsEntities import PSE
from opsEntities import TextReports

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.OE.PluginListeners')


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

    def windowActivated(self, WINDOW_ACTIVATED):

        _psLog.debug(WINDOW_ACTIVATED)

        refreshSubroutines()

        return
    def windowClosed(self, WINDOW_CLOSED):
        return
    def windowIconified(self, WINDOW_ICONIFIED):
        return
    def windowDeiconified(self, WINDOW_DEICONIFIED):
        return
    def windowDeactivated(self, WINDOW_DEACTIVATED):
        return


def refreshSubroutines():

    for subroutine in PSE.getSubroutineDirs():
        xModule = 'Subroutines_Activated.{}'.format(subroutine)
        package = __import__(xModule, fromlist=['Model'], level=-1)
        package.Model.refreshSubroutine()

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
    """
    Adds a listener to each location
    and each track at each location.
    """

    for location in PSE.LM.getList():
        location.addPropertyChangeListener(LocationsPropertyChange())
        for track in location.getTracksList():
            track.addPropertyChangeListener(LocationsPropertyChange())

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
    """
    Removes the listeners attached to each location
    and each track at each location.
    """

    for location in PSE.LM.getList():
        for listener in location.getPropertyChangeListeners():
            if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'LocationsPropertyChange' in listener.toString():
                location.removePropertyChangeListener(listener)

                _psLog.debug('Main Script.Listeners.removeLocationListener: ' + location.toString())

        for track in location.getTracksList():
            for listener in track.getPropertyChangeListeners():
                if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'LocationsPropertyChange' in listener.toString():
                    track.removePropertyChangeListener(listener)

                    _psLog.debug('Main Script.Listeners.removeLocationListener: ' + track.toString())
                    
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
    Events that are triggered with changes to OPS switch lists.
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        print(PROPERTY_CHANGE_EVENT.source.toString())
        print(PROPERTY_CHANGE_EVENT.propertyName)
        print(PROPERTY_CHANGE_EVENT.oldValue)
        print(PROPERTY_CHANGE_EVENT.newValue)

        if PROPERTY_CHANGE_EVENT.propertyName == 'TrainsListLength': # Fired from JMRI
        
            _psLog.debug('PluginListeners.TrainsPropertyChange.PROPERTY_CHANGE_EVENT.TrainsListLength')

            removeTrainListener()
            addTrainListener()

            return

        _psLog.debug('PluginListeners.TrainsPropertyChange.TrainsPropertyParser.preProcess')
        for subroutine in PSE.getSubroutineDirs():
            xModule = 'Subroutines_Activated.{}'.format(subroutine)
            package = __import__(xModule, fromlist=['Controller'], level=-1)
            package.Controller.TrainsPropertyParser(PROPERTY_CHANGE_EVENT).preProcess()

        _psLog.debug('PluginListeners.TrainsPropertyChange.TrainsPropertyParser.process')
        for subroutine in PSE.getSubroutineDirs():
            xModule = 'Subroutines_Activated.{}'.format(subroutine)
            package = __import__(xModule, fromlist=['Controller'], level=-1)
            package.Controller.TrainsPropertyParser(PROPERTY_CHANGE_EVENT).process()

        _psLog.debug('PluginListeners.TrainsPropertyChange.TrainsPropertyParser.postProcess')
        for subroutine in PSE.getSubroutineDirs():
            xModule = 'Subroutines_Activated.{}'.format(subroutine)
            package = __import__(xModule, fromlist=['Controller'], level=-1)
            package.Controller.TrainsPropertyParser(PROPERTY_CHANGE_EVENT).postProcess()


class LocationsPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Events that are triggered with changes to JMRI Divisions, Locations and Tracks.
    """

    def __init__(self):

        pass
    
    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        jmriProperties = ['divisionsListLength', 'divisionName', 'locationsListLength', 'locationName', 'trackListLength', 'trackName']
        if PROPERTY_CHANGE_EVENT.propertyName in jmriProperties:

            for subroutine in PSE.getSubroutineDirs():
                xModule = 'Subroutines_Activated.{}'.format(subroutine)
                package = __import__(xModule, fromlist=['Model'], level=-1)
                package.Model.initializeSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'opsResetSubroutine':
        # Fired from OPS
            for subroutine in PSE.getSubroutineDirs():
                xModule = 'Subroutines_Activated.{}'.format(subroutine)
                package = __import__(xModule, fromlist=['Model'], level=-1)
                package.Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            
        return

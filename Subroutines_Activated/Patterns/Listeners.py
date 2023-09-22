"""
Listeners for the Patterns subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines_Activated.Patterns import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.PT.Listeners')


class ListenToThePSWindow(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Listens for changes to the Pattern Scripts plugin window.
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):
    
        if PROPERTY_CHANGE_EVENT.propertyName == 'windowOpened':

            addSubroutineListeners()
            Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'windowActivated':

            Model.refreshSubroutine()
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'windowClosing':
            
            removeSubroutineListeners()
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)
            
        return

def addSubroutineListeners():
    """
    Mini controller.
    """

    addDivisionsTableListener()
    addDivisionsListener()
    addLocationsTableListener()
    addLocationsListener()

    print('Patterns.Listeners.addSubroutineListeners')
    _psLog.debug('Patterns.Listeners.addSubroutineListeners')

    return

def removeSubroutineListeners():
    """
    Mini controller.
    """

    removeDivisionsTableListener()
    removeDivisionsListener()
    removeLocationsTableListener()
    removeLocationsListener()

    _psLog.debug('Patterns.Listeners.removeSubroutineListeners')

    return


def addDivisionsTableListener():

    PSE.DM.addPropertyChangeListener(PatternsPropertyChange())

    _psLog.debug('Patterns.Listeners.addDivisionsTableListener')

    return

def addLocationsTableListener():

    PSE.LM.addPropertyChangeListener(PatternsPropertyChange())

    _psLog.debug('Patterns.Listeners.addLocationsTableListener')

    return

def addDivisionsListener():

    for division in PSE.DM.getList():
        division.addPropertyChangeListener(PatternsPropertyChange())
        _psLog.debug('Patterns.Listeners.addDivisionsListener: ' + division.getName())

    return

def addLocationsListener():

    for location in PSE.LM.getList():
        location.addPropertyChangeListener(PatternsPropertyChange())
        _psLog.debug('Patterns.Listeners.addLocationsListener: ' + location.getName())

    return

def removeDivisionsTableListener():

    for listener in PSE.DM.getPropertyChangeListeners():
        if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'PatternsPropertyChange' in listener.toString():
            PSE.DM.removePropertyChangeListener(listener)

            _psLog.debug('Patterns.Listeners.removeDivisionsTableListener')

    print('Patterns.Listeners.removeDivisionsTableListener')

    return

def removeDivisionsListener():

    for division in PSE.DM.getList():
        for listener in division.getPropertyChangeListeners():
            if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'PatternsPropertyChange' in listener.toString():
                division.removePropertyChangeListener(listener)
                _psLog.debug('Patterns.Listeners.removeDivisionsListener: ' + division.getName())

    print('Patterns.Listeners.removeDivisionsListener')

    return

def removeLocationsTableListener():
    """
    Also removes  PatternsSubroutine listener.
    """

    for listener in PSE.LM.getPropertyChangeListeners():
        if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'PatternsPropertyChange' in listener.toString():
            PSE.LM.removePropertyChangeListener(listener)

            _psLog.debug('Patterns.Listeners.removeLocationsTableListener')

    print('Patterns.Listeners.removeLocationsTableListener')

    return

def removeLocationsListener():

    for location in PSE.LM.getList():
        for listener in location.getPropertyChangeListeners():
            if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'PatternsPropertyChange' in listener.toString():
                location.removePropertyChangeListener(listener)

                _psLog.debug('Patterns.Listeners.removeLocationsListener: ' + location.getName())

    print('Patterns.Listeners.removeLocationsListener')

    return


class PatternsPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    A property change listener attached to:
    The divisions table
    Each division
    The locations table
    Each location
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'jmriDataSets':
        # Fired from o2o
            Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionsListLength':
            Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionName':
            Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationsListLength':
            Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationName':
            Model.resetSubroutine()
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)

        return
    

class DivisionAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Divisions combo box is selected.
    """

    def __init__(self):

        pass

    def actionPerformed(self, EVENT):

        Model.divComboSelected(EVENT)
        Model.locComboUpdater()
        Model.makeTrackRows()

        return


class LocationAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Locations combo box is selected.
    """

    def __init__(self):

        pass

    def actionPerformed(self, EVENT):

        Model.locComboSelected(EVENT)
        Model.makeTrackRows()

        return


class TextBoxEntry(PSE.JAVA_AWT.event.MouseAdapter):
    """
    When any of the 'Set Cars Form for Track X' text input boxes is clicked on.
    """

    def __init__(self):

        pass

    def mouseClicked(self, MOUSE_CLICKED):

        if PSE.TRACK_NAME_CLICKED_ON:
            MOUSE_CLICKED.getSource().setText(PSE.TRACK_NAME_CLICKED_ON)
        else:
            _psLog.warning('No track was selected')

        return

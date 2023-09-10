"""
Listeners for the Patterns subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines.Patterns import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.PT.Listeners')

def actionListener(EVENT):
    """
    menu item-Tools/Show Subroutines.Patterns
    """

    _psLog.debug(EVENT)

    configFile = PSE.readConfigFile()
    subroutineName = __package__.split('.')[1]

    if configFile[subroutineName]['SV']: # Hide this subroutine
        menuText = PSE.getBundleItem('Show') + ' ' + __package__
        configFile[subroutineName].update({'SV':False})
        _psLog.info('Hide ' + __package__)
        print('Hide ' + __package__)
    else: # Show this subroutine
        menuText = PSE.getBundleItem('Hide') + ' ' + __package__
        configFile[subroutineName].update({'SV':True})
        _psLog.info('Show ' + __package__)
        print('Show ' + __package__)

    PSE.writeConfigFile(configFile)
    PSE.repaintPatternScriptsWindow()

    EVENT.getSource().setText(menuText)

    return

def addSubroutineListeners():
    """
    Mini controller.
    """

    addDivisionsTableListener()
    addLocationsTableListener()
    addDivisionsListener()
    addLocationsListener()

    print('Patterns.Listeners.addSubroutineListeners')
    _psLog.debug('Patterns.Listeners.addSubroutineListeners')

    return

def removeSubroutineListeners():
    """
    Mini controller.
    """

    removeDivisionsTableListener()
    removeLocationsTableListener()
    removeDivisionsListener()
    removeLocationsListener()

    _psLog.debug('Patterns.Listeners.removeSubroutineListeners')

    return


class OpsWindowPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    A property change listener attached to the Operations Pattern Scripts window.
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'opsWindowActivated':
            Model.refreshSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

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

        if PROPERTY_CHANGE_EVENT.propertyName == 'opsWindowActivated' and PROPERTY_CHANGE_EVENT.newValue == True:
            print('opsWindowActivated')
            Model.refreshSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'jmriDataSets':
            Model.divComboUpdater()
            Model.locComboUpdater()

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionsListLength':
            Model.divComboUpdater()
            Model.locComboUpdater()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionName':
            Model.divComboUpdater()
            Model.locComboUpdater()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationsListLength':
            Model.locComboUpdater()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationName':
            Model.locComboUpdater()
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)

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

    _psLog.debug('Add division name change listener')

    return

def addLocationsListener():

    for location in PSE.LM.getList():
        location.addPropertyChangeListener(PatternsPropertyChange())
        _psLog.debug('Add location name change listener')

    _psLog.debug('Patterns.Listeners.addLocationsListener')

    return

def removeDivisionsTableListener():

    for listener in PSE.DM.getPropertyChangeListeners():
        if isinstance(listener, PatternsPropertyChange):
            PSE.DM.removePropertyChangeListener(listener)

            print('Patterns.Listeners.removeDivisionsTableListener.PatternsPropertyChange')
            _psLog.debug('Patterns.Listeners.removeSubroutineListeners')

    return

def removeLocationsTableListener():

    for listener in PSE.LM.getPropertyChangeListeners():
        if isinstance(listener, PatternsPropertyChange):
            PSE.LM.removePropertyChangeListener(listener)

            print('Patterns.Listeners.removeLocationsTableListener.PatternsPropertyChange')
            _psLog.debug('Patterns.Listeners.removeLocationsTableListener')

    return

def removeDivisionsListener():

    for division in PSE.DM.getList():
        for listener in division.getPropertyChangeListeners():
            if isinstance(listener, PatternsPropertyChange):
                division.removePropertyChangeListener(listener)

    print('Patterns.Listeners.removeDivisionsListener.PatternsPropertyChange')
    _psLog.debug('Patterns.Listeners.removeDivisionsListener')

    return

def removeLocationsListener():

    for location in PSE.LM.getList():
        for listener in location.getPropertyChangeListeners():
            if isinstance(listener, PatternsPropertyChange):
                location.removePropertyChangeListener(listener)

    print('Patterns.Listeners.removeLocationsListener.PatternsPropertyChange')
    _psLog.debug('Patterns.Listeners.removeLocationsListener')

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
        Model.trackRowManager()

        return


class LocationAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Locations combo box is selected.
    """

    def __init__(self):

        pass

    def actionPerformed(self, EVENT):

        Model.locComboSelected(EVENT)
        Model.trackRowManager()

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

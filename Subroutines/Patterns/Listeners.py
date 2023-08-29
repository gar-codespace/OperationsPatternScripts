"""
Listeners for the Patterns subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines.Patterns import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

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
    # Do subroutine specific stuff here



    else: # Show this subroutine
        menuText = PSE.getBundleItem('Hide') + ' ' + __package__
        configFile[subroutineName].update({'SV':True})
        _psLog.info('Show ' + __package__)
        print('Show ' + __package__)
    # Do subroutine specific stuff here



    PSE.writeConfigFile(configFile)
    PSE.repaintPatternScriptsWindow()

    EVENT.getSource().setText(menuText)

    return


class DivisionsLocationsPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
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

        if PROPERTY_CHANGE_EVENT.propertyName == 'o2oUpdate':
            Model.divComboUpdater()
            Model.locComboUpdater()

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.o2oUpdate')

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionsListLength':
            Model.divComboUpdater()
            Model.locComboUpdater()
            # Model.trackRowManager()

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.divisionsListLength')

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionName':
            Model.divComboUpdater()
            Model.locComboUpdater()
            # Model.trackRowManager()

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.divisionName')

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationsListLength':
            Model.locComboUpdater()
            # Model.trackRowManager()

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.locationsListLength')

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationName':
            Model.locComboUpdater()
            # Model.trackRowManager()
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.locationName')

        return

def addDivisionsTableListener():

    PSE.DM.addPropertyChangeListener(DivisionsLocationsPropertyChange())

    print('Patterns.Listeners.addDivisionsTableListener')
    _psLog.debug('Patterns.Listeners.addDivisionsTableListener')

    return

def addLocationsTableListener():

    PSE.LM.addPropertyChangeListener(DivisionsLocationsPropertyChange())

    print('Patterns.Listeners.addLocationsTableListener')
    _psLog.debug('Patterns.Listeners.addLocationsTableListener')

    return

def addDivisionsListener():

    for division in PSE.DM.getList():
        division.addPropertyChangeListener(DivisionsLocationsPropertyChange())

    print('Patterns.Listeners.addDivisionsListener')
    _psLog.debug('Add division name change listener')

    return

def addLocationsListener():

    for location in PSE.LM.getList():
        location.addPropertyChangeListener(DivisionsLocationsPropertyChange())
        _psLog.debug('Add location name change listener')

    print('Patterns.Listeners.addLocationsListener')
    _psLog.debug('Patterns.Listeners.addLocationsListener')

    return

def removeDivisionsTableListener():

    for listener in PSE.DM.getPropertyChangeListeners():
        if isinstance(listener, DivisionsLocationsPropertyChange):
            PSE.DM.removePropertyChangeListener(listener)

            print('Patterns.Listeners.removeDivisionsTableListener')
            _psLog.debug('Patterns.Listeners.removeDivisionsTableListener')

    return

def removeLocationsTableListener():

    for listener in PSE.LM.getPropertyChangeListeners():
        if isinstance(listener, DivisionsLocationsPropertyChange):
            PSE.LM.removePropertyChangeListener(listener)

            print('Patterns.Listeners.removeLocationsTableListener')
            _psLog.debug('Patterns.Listeners.removeLocationsTableListener')

    return

def removeDivisionsListener():

    for division in PSE.DM.getList():
        for listener in division.getPropertyChangeListeners():
            if isinstance(listener, DivisionsLocationsPropertyChange):
                division.removePropertyChangeListener(listener)

    print('Patterns.Listeners.removeDivisionsListener')
    _psLog.debug('Patterns.Listeners.removeDivisionsListener')

    return

def removeLocationsListener():

    for location in PSE.LM.getList():
        for listener in location.getPropertyChangeListeners():
            if isinstance(listener, DivisionsLocationsPropertyChange):
                location.removePropertyChangeListener(listener)

    _psLog.debug('Patterns.Listeners.removeLocationsListener')
    print('Patterns.Listeners.removeLocationsListener')

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

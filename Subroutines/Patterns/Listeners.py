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
    """

    def __init__(self):

        return
    
    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionsListLength':
            PSE.remoteCalls('refreshCalls')

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.DivisionsLocationsPropertyChange.divisionsListLength')

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionName':
            PSE.remoteCalls('refreshCalls')

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.DivisionsLocationsPropertyChange.divisionName')

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationsListLength':
            PSE.remoteCalls('refreshCalls')

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.DivisionsLocationsPropertyChange.locationsListLength')

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationName':
            PSE.remoteCalls('refreshCalls')
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.DivisionsLocationsPropertyChange.locationName')

        return
    

def addPatternsListeners():
    """
    Adds DivisionsLocationsPropertyChange to divisions and locations.
    """
# Divisions
    PSE.DM.addPropertyChangeListener(DivisionsLocationsPropertyChange())
    _psLog.debug('Add divisions list length listener')

    for division in PSE.DM.getList():
        division.addPropertyChangeListener(DivisionsLocationsPropertyChange())
        _psLog.debug('Add division name change listener')
# Locations
    PSE.LM.addPropertyChangeListener(DivisionsLocationsPropertyChange())
    _psLog.debug('Add locations list length listener')

    for location in PSE.LM.getList():
        location.addPropertyChangeListener(DivisionsLocationsPropertyChange())
        _psLog.debug('Add location name change listener')

    return

def removePatternListeners():
    """
    Removes DivisionsLocationsPropertyChange from divisions and locations.
    """
# Divisions
    for listener in PSE.DM.getPropertyChangeListeners():
        if isinstance(listener, DivisionsLocationsPropertyChange):
            PSE.DM.removePropertyChangeListener(listener)
            _psLog.debug('Remove divisions list length listener')

    for division in PSE.DM.getList():
        for listener in division.getPropertyChangeListeners():
            if isinstance(listener, DivisionsLocationsPropertyChange):
                division.removePropertyChangeListener(listener)
                _psLog.debug('Remove division name change listener')
# Locations
    for listener in PSE.LM.getPropertyChangeListeners():
        if isinstance(listener, DivisionsLocationsPropertyChange):
            PSE.LM.removePropertyChangeListener(listener)
            _psLog.debug('Remove locations list length listener')

    for location in PSE.LM.getList():
        for listener in location.getPropertyChangeListeners():
            if isinstance(listener, DivisionsLocationsPropertyChange):
                location.removePropertyChangeListener(listener)
                _psLog.debug('Remove location name change listener')

    return
    

class DivisionAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Divisions combo box is selected.
    """

    def __init__(self):

        return

    def actionPerformed(self, EVENT):

        Model.divisionComboBoxManager(EVENT)

        return


class LocationAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Locations combo box is selected.
    """

    def __init__(self):

        return

    def actionPerformed(self, EVENT):

        Model.locationComboBoxManager(EVENT)

        return


class TextBoxEntry(PSE.JAVA_AWT.event.MouseAdapter):
    """
    When any of the 'Set Cars Form for Track X' text input boxes is clicked on.
    """

    def __init__(self):

        return

    def mouseClicked(self, MOUSE_CLICKED):

        if PSE.TRACK_NAME_CLICKED_ON:
            MOUSE_CLICKED.getSource().setText(PSE.TRACK_NAME_CLICKED_ON)
        else:
            _psLog.warning('No track was selected')

        return

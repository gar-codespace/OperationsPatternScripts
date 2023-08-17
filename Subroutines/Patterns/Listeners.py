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


class ComboBoxPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Restarts the Patterns sub on a change to the JMRI Locations roster.
    """

    def __init__(self):

        return
    
    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionsListLength' and PROPERTY_CHANGE_EVENT.newValue == True:
            PSE.restartSubroutineByName(__package__)

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.ComboBoxPropertyChange.divisionsListLength ' + str(SCRIPT_REV))

        if PROPERTY_CHANGE_EVENT.propertyName == 'divisionName' and PROPERTY_CHANGE_EVENT.newValue == True:
            PSE.restartSubroutineByName(__package__)

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.ComboBoxPropertyChange.divisionName ' + str(SCRIPT_REV))

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationsListLength' and PROPERTY_CHANGE_EVENT.newValue == True:
            PSE.restartSubroutineByName(__package__)

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.ComboBoxPropertyChange.locationsListLength ' + str(SCRIPT_REV))

        if PROPERTY_CHANGE_EVENT.propertyName == 'locationName' and PROPERTY_CHANGE_EVENT.newValue == True:
            PSE.restartSubroutineByName(__package__)
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.ComboBoxPropertyChange.locationName ' + str(SCRIPT_REV))

        return
    

def addPatternsListeners():

    PSE.DM.addPropertyChangeListener(ComboBoxPropertyChange())
    PSE.LM.addPropertyChangeListener(ComboBoxPropertyChange())

    for division in PSE.DM.getList():
        PSE.DM.removePropertyChangeListener(ComboBoxPropertyChange())
        division.addPropertyChangeListener(ComboBoxPropertyChange())

    for location in PSE.LM.getList():
        location.removePropertyChangeListener(ComboBoxPropertyChange())
        location.addPropertyChangeListener(ComboBoxPropertyChange())
        
    print('Patterns.activatedCalls.Listeners.addDivisionsListeners')
    print('Patterns.activatedCalls.Listeners.addLocationsListeners')

    return

def removePatternListeners():

    PSE.DM.removePropertyChangeListener(ComboBoxPropertyChange())
    PSE.LM.removePropertyChangeListener(ComboBoxPropertyChange())

    for division in PSE.DM.getList():
        division.removePropertyChangeListener(ComboBoxPropertyChange())

    for location in PSE.LM.getList():
        location.removePropertyChangeListener(ComboBoxPropertyChange())

    print('Patterns.deactivatedCalls.Listeners.removeDivisionListeners')
    print('Patterns.deactivatedCalls.Listeners.removeLocationListeners')
    return
    

class DivisionAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Divisions combo box is selected.
    """

    def __init__(self):

        return

    def actionPerformed(self, EVENT):

        itemSelected = EVENT.getSource().getSelectedItem()
        Model.divisionComboBox(itemSelected)
        PSE.restartSubroutineByName(__package__)

        return


class LocationAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Locations combo box is selected.
    """

    def __init__(self):

        return

    def actionPerformed(self, EVENT):

        itemSelected = EVENT.getSource().getSelectedItem()
        Model.locationComboBox(itemSelected)
        PSE.restartSubroutineByName(__package__)

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

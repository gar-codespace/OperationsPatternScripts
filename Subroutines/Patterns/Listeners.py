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

def addDivisionListeners():

    PSE.DM.addPropertyChangeListener(DivisionComboBoxProperty())
    print('o2o.activatedCalls.Listeners.DivisionComboBoxProperty')

    for division in PSE.DM.getList():
        PSE.DM.removePropertyChangeListener(DivisionComboBoxProperty())
        division.addPropertyChangeListener(DivisionProperty())

    return

def removeDivisionListeners():

    PSE.DM.removePropertyChangeListener(DivisionComboBoxProperty())
    print('o2o.activatedCalls.Listeners.DivisionComboBoxProperty')

    for division in PSE.DM.getList():
        division.removePropertyChangeListener(DivisionProperty())

    return


class DivisionComboBoxProperty(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Restarts the Patterns sub on a change to the divisions roster.
    """

    def __init__(self):

        return
    
    def propertyChange(self, COMBO_BOX_UPDATE):

        _psLog.debug(COMBO_BOX_UPDATE)
        print(SCRIPT_NAME + '.DivisionComboBoxProperty ' + str(SCRIPT_REV))

        if COMBO_BOX_UPDATE.propertyName == 'divisionsListLength':
            PSE.restartSubroutineByName(__package__)

        return
    

class DivisionProperty(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Restarts the Patterns sub on the change of a division name.
    """

    def __init__(self):

        return
    
    def propertyChange(self, DIVISION_UPDATE):

        _psLog.debug(DIVISION_UPDATE)

        if DIVISION_UPDATE.propertyName == 'divisionName':
            PSE.restartSubroutineByName(__package__)

        return


def addLocationListeners():

    PSE.LM.addPropertyChangeListener(LocationComboBoxProperty())
    print('o2o.activatedCalls.Listeners.LocationComboBoxProperty')

    for location in PSE.LM.getList():
        location.removePropertyChangeListener(LocationComboBoxProperty())
        location.addPropertyChangeListener(LocationComboBoxProperty())

    return

def removeLocationListeners():

    PSE.LM.removePropertyChangeListener(LocationComboBoxProperty())
    print('o2o.activatedCalls.Listeners.LocationComboBoxProperty')

    for location in PSE.LM.getList():
        location.removePropertyChangeListener(LocationComboBoxProperty())

    return


class LocationComboBoxProperty(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Restarts the Patterns sub on a change to the locations roster.
    """

    def __init__(self):

        return
    
    def propertyChange(self, COMBO_BOX_UPDATE):

        _psLog.debug(COMBO_BOX_UPDATE)
        print(SCRIPT_NAME + '.LocationComboBoxProperty ' + str(SCRIPT_REV))

        if COMBO_BOX_UPDATE.propertyName == 'locationsListLength':
            PSE.restartSubroutineByName(__package__)

        if COMBO_BOX_UPDATE.propertyName == 'locationName':
            PSE.restartSubroutineByName(__package__)

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
    Action taken when an item is selected in the Locations combo box.
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

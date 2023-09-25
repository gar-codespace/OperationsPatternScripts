"""
Listeners for the Scanner subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines_Activated.Scanner import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.SC.Listeners')


class ListenToThePSWindow(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Every subroutine has this class.
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
    A listener to detect if an event outside of this subroutine
    needs to trigger something within this subroutine.
    Check the other subroutines for ideas on how to implement this.
    """

    # print('Scanner.Listeners.addSubroutineListeners')
    # _psLog.debug('Scanner.Listeners.addSubroutineListeners')

    return

def removeSubroutineListeners():
    """
    When the Pattern Scripts window is closed, turn off the listeners for this subroutine.
    Check the other subroutines for ideas on how to implement this.
    """
            
    # print('Scanner.Listeners.removeSubroutineListeners')
    # _psLog.debug('Scanner.Listeners.removeSubroutineListeners')

    return

class TemplatePropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    A property change listener that will trigger an event in this subroutine
    when something outside this subroutine happens.
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'whatever you are listening for':
            # Model.resetSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'add as many as you need':

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

        return


class LocationAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Locations combo box is selected.
    """

    def __init__(self):

        pass

    def actionPerformed(self, EVENT):

        # Model.locComboSelected(EVENT)
        # Model.makeTrackRows()

        return

class ScannerAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Locations combo box is selected.
    """

    def __init__(self):

        pass

    def actionPerformed(self, EVENT):

        # Model.locComboSelected(EVENT)
        # Model.makeTrackRows()

        return
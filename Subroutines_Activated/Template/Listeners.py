"""
Listeners for the Template subroutine.
JAVAX action performed methods are in Controller.
Replace XX with a designator for this subroutines name.
"""

from opsEntities import PSE
from Subroutines_Activated.Template import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.XX.Listeners')


class TemplateSubroutine(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):
        if PROPERTY_CHANGE_EVENT.propertyName == 'windowClosing':
            
            removeSubroutineListeners()
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)
    
        if PROPERTY_CHANGE_EVENT.propertyName == 'windowOpened':

            addSubroutineListeners()
            Model.resetSubroutine()
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'windowActivated':

            Model.refreshSubroutine()
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)

        return
    

def addSubroutineListeners():
    """
    A listener to detect if an event outside of this subroutine
    needs to trigger something within this subroutine.
    """

    # print('Template.Listeners.addSubroutineListeners')
    # _psLog.debug('Template.Listeners.addSubroutineListeners')

    return

def removeSubroutineListeners():
    """
    When the Pattern Scripts window is closed, turn off the listeners for this subroutine.
    """
            
    # print('Template.Listeners.removeSubroutineListeners')
    # _psLog.debug('Template.Listeners.removeSubroutineListeners')

    return

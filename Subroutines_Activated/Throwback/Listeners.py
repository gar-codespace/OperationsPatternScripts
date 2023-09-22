"""
Listeners for the Throwback Subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines_Activated.Throwback import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.TB.Listeners')


class ListenToThePSWindow(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Listens for changes to the Pattern Scripts plugin window.
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):
    
        if PROPERTY_CHANGE_EVENT.propertyName == 'windowOpened':            

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'windowActivated':
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)

        if PROPERTY_CHANGE_EVENT.propertyName == 'windowClosing':
            
            _psLog.debug(PROPERTY_CHANGE_EVENT)
            
        return

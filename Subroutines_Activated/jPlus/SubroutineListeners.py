"""
'Local' level listeners for the jPlus subroutine.
For OPS interoperability or JMRI events, add a laitener to opsEntities.PluginListeners.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines_Activated.jPlus import Model

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.JP.SubroutineListeners')

class ExtendedAttributesListener(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Extended railroad details are pushed to jPlus.
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        # propertyOldValue = PROPERTY_CHANGE_EVENT.oldValue # list object
        # propertyName = PROPERTY_CHANGE_EVENT.propertyName # string
        # propertyNewValue = PROPERTY_CHANGE_EVENT.newValue # bool
        # PROPERTY_CHANGE_EVENT.source.toString() # object.string

        if PROPERTY_CHANGE_EVENT.propertyName == 'opsExtendedProperties':
            Model.putExtendedProperties(PROPERTY_CHANGE_EVENT.oldValue) # list object
            Model.refreshSubroutine()

        return
"""
'Local' level listeners for the jPlus subroutine.
For OPS interoperability or JMRI events, add a laitener to opsEntities.PluginListeners.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.JP.SubroutineListeners')

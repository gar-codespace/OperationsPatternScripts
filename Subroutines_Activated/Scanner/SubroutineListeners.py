"""
'Local' level listeners for the Scanner subroutine.
For OPS interoperability or JMRI events, add a laitener to opsEntities.PluginListeners.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines_Activated.Scanner import Model

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.SC.PluginListeners')


class ScannerSelection(PSE.JAVA_AWT.event.ActionListener):
    """
    Runs a routine on the selected scanner.
    """

    def __init__(self):

        pass

    def actionPerformed(self, EVENT):

        Model.recordSelection(EVENT.getSource())

        return

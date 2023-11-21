"""
'Local' level listeners for the Patterns subroutine.
For OPS interoperability or JMRI events, add a listener to opsEntities.PluginListeners.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines_Activated.Patterns import Model

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.PT.PluginListeners')


class DivisionAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Divisions combo box is selected.
    """

    def __init__(self):

        pass

    def actionPerformed(self, EVENT):

        Model.divComboSelected(EVENT)
        Model.locComboUpdater()
        Model.makeTrackRows()

        return


class LocationAction(PSE.JAVA_AWT.event.ActionListener):
    """
    Action taken when an item in the Locations combo box is selected.
    """

    def __init__(self):

        pass

    def actionPerformed(self, EVENT):

        Model.locComboSelected(EVENT)
        Model.makeTrackRows()

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

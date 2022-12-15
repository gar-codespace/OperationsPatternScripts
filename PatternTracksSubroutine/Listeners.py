"""
Listeners for the Pattern Tracks subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.Listeners'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.PT.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Enable Track Pattern subroutine"""

    _psLog.debug(EVENT)
    patternConfig = PSE.readConfigFile()

    if patternConfig['CP']['PatternTracksSubroutine']: # If enabled, turn it off
        patternConfig['CP']['PatternTracksSubroutine'] = False
        EVENT.getSource().setText(PSE.BUNDLE[u'Enable Track Pattern subroutine'])

        _psLog.info('Track Pattern support deactivated')
        print('Track Pattern support deactivated')
    else:
        patternConfig['CP']['PatternTracksSubroutine'] = True
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable Track Pattern subroutine'])

        _psLog.info('Track Pattern support activated')
        print('Track Pattern support activated')

    PSE.writeConfigFile(patternConfig)

    return


class GenericComboBox(PSE.JAVA_AWT.event.ActionListener):
    """Event triggered from any combobox use.
        Be sure to set the name of the combobox that uses this class.
        """

    def __init__(self, subroutineFrame):

        self.subroutineFrame = subroutineFrame

        return

    def actionPerformed(self, EVENT):

        xModule = __import__('PatternTracksSubroutine', globals(), locals(), ['Controller', 'Model'], 0)

        xModule.Model.updatePatternLocation(EVENT.getSource())
        xModule.Controller.restartSubroutine(self.subroutineFrame)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return


class TextBoxEntry(PSE.JAVA_AWT.event.MouseAdapter):
    """When any of the 'Set Cars Form for Track X' text input boxes is clicked on."""

    def __init__(self):

        return

    def mouseClicked(self, MOUSE_CLICKED):

        if PSE.TRACK_NAME_CLICKED_ON:
            MOUSE_CLICKED.getSource().setText(PSE.TRACK_NAME_CLICKED_ON)
        else:
            _psLog.warning('No track was selected')

        return

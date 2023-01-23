"""
Listeners for the Pattern Tracks subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.PT.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Enable Track Pattern subroutine"""

    _psLog.debug(EVENT)
    patternConfig = PSE.readConfigFile()
    OSU = PSE.JMRI.jmrit.operations.setup

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')
    targetSubroutine = PSE.getComponentByName(frameTitle, __package__)

    if patternConfig['CP'][__package__]: # If enabled, turn it off
        EVENT.getSource().setText(PSE.BUNDLE[u'Enable'] + ' ' + __package__)

    # Do stuff here

        patternConfig['CP'].update({__package__:False})
        PSE.writeConfigFile(patternConfig)

        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' removed from pattern scripts frame')
        print(__package__ + ' deactivated')
    else:
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable'] + ' ' + __package__)

    # Do stuff here

        patternConfig['CP'].update({__package__:True})
        PSE.writeConfigFile(patternConfig)

        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' added to pattern scripts frame')
        print(__package__ + ' activated')

    targetPanel.validate()
    targetPanel.repaint()

    return


class PTComboBox(PSE.JAVA_AWT.event.ActionListener):
    """Event triggered from any pattern tracks combo box use.
        Be sure to set the name of the combobox that uses this class.
        """

    def __init__(self):

        return

    def actionPerformed(self, EVENT):

        xModule = __import__(__package__, globals(), locals(), ['Model'], 0)
        xModule.Model.updatePatternLocation(EVENT.getSource())

        PSE.restartSubroutineByName(__package__)

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

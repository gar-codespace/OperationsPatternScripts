"""
Listeners for the Pattern Tracks subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.PT.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Enable Subroutines.Throwback"""

    _psLog.debug(EVENT)

    PSE.closeTroublesomeWindows()

    patternConfig = PSE.readConfigFile()

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')

# If it's on, turn it off
    if patternConfig['Main Script']['CP'][__package__]: 
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__
        patternConfig['Main Script']['CP'].update({__package__:False})
        
    # Do stuff specific to this subroutine here


        PSE.writeConfigFile(patternConfig)
        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' removed from pattern scripts frame')
        print(__package__ + ' deactivated')

# If it's off, turn it on
    else:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
        patternConfig['Main Script']['CP'].update({__package__:True})
        
    # Do stuff specific to this subroutine here


        PSE.writeConfigFile(patternConfig)
        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' added to pattern scripts frame')
        print(__package__ + ' activated')

    targetPanel.validate()
    targetPanel.repaint()

    EVENT.getSource().setText(menuText)

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
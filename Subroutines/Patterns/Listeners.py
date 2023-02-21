"""
Listeners for the Patterns subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.PT.Listeners')

def actionListener(EVENT):
    """menu item-Tools/Show Subroutines.Patterns"""

    _psLog.debug(EVENT)

    PSE.closeSubordinateWindows()

    configFile = PSE.readConfigFile()

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')

# If it's on, turn it off
    if configFile['Main Script']['CP'][__package__]: 
        menuText = PSE.BUNDLE[u'Show'] + ' ' + __package__
        configFile['Main Script']['CP'].update({__package__:False})
        
    # Do stuff specific to this subroutine here

        _psLog.info(__package__ + ' removed from pattern scripts frame')
        print(__package__ + ' deactivated')

# If it's off, turn it on
    else:
        menuText = PSE.BUNDLE[u'Hide'] + ' ' + __package__
        configFile['Main Script']['CP'].update({__package__:True})
        
    # Do stuff specific to this subroutine here


        _psLog.info(__package__ + ' added to pattern scripts frame')
        print(__package__ + ' activated')

    PSE.writeConfigFile(configFile)
    targetPanel.removeAll()
    targetPanel = PSE.addActiveSubroutines(targetPanel)
    targetPanel.validate()
    targetPanel.repaint()

    EVENT.getSource().setText(menuText)

    return


class PTComboBox(PSE.JAVA_AWT.event.ActionListener):
    """
    Event triggered from any Patterns combo box use.
    The method name is the name of the combo box.
    """

    def __init__(self):

        return

    def actionPerformed(self, EVENT):

        xModule = __import__(__package__, globals(), locals(), ['Model'], 0)
        methodName = EVENT.getSource().getName()
        itemSelected = EVENT.getSource().getSelectedItem()

        getattr(xModule.Model, methodName)(itemSelected)

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

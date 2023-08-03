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

    configFile = PSE.readConfigFile()
    subroutineName = __package__.split('.')[1]

    if configFile[subroutineName]['SV']: # Hide this subroutine
        menuText = PSE.getBundleItem('Show') + ' ' + __package__
        configFile[subroutineName].update({'SV':False})
        _psLog.info('Hide ' + __package__)
        print('Hide ' + __package__)
    # Do subroutine specific stuff here



    else: # Show this subroutine
        menuText = PSE.getBundleItem('Hide') + ' ' + __package__
        configFile[subroutineName].update({'SV':True})
        _psLog.info('Show ' + __package__)
        print('Show ' + __package__)
    # Do subroutine specific stuff here



    PSE.writeConfigFile(configFile)
    PSE.repaintPatternScriptsWindow()

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

        xModule = __import__(__package__, globals(), locals(), ['model'], 0)
        methodName = EVENT.getSource().getName()
        itemSelected = EVENT.getSource().getSelectedItem()

        getattr(xModule.Model, methodName)(itemSelected)

        # PSE.restartSubroutineByName(__package__)

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

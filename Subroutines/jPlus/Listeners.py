"""
Listeners for the jPlus subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Enable Subroutines.jPlus."""

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
        OSU = PSE.JMRI.jmrit.operations.setup
        OSU.Setup.setRailroadName(patternConfig['Main Script']['LD']['LN'])

        PSE.writeConfigFile(patternConfig)
        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' removed from pattern scripts frame')
        print(__package__ + ' deactivated')
    else:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
        patternConfig['Main Script']['CP'].update({__package__:True})
        
    # Do stuff specific to this subroutine here
        OSU = PSE.JMRI.jmrit.operations.setup
        eHeader = PSE.expandedHeader().replace(';', '\n')
        OSU.Setup.setRailroadName(eHeader)
        PSE.JMRI.jmrit.operations.setup.OperationsSettingsPanel().savePreferences()

        PSE.writeConfigFile(patternConfig)
        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' added to pattern scripts frame')
        print(__package__ + ' activated')

    targetPanel.validate()
    targetPanel.repaint()

    EVENT.getSource().setText(menuText)

    return

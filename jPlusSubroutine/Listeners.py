"""
Listeners for the jPlus subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.jPlusSubroutine.Listeners'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')

def actionListener(EVENT):
    """menu item-Tools/Enable jPlusSubroutine."""

    _psLog.debug(EVENT)
    patternConfig = PSE.readConfigFile()
    OSU = PSE.JMRI.jmrit.operations.setup

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')

    if patternConfig['CP'][__package__]: # If enabled, turn it off
        EVENT.getSource().setText(PSE.BUNDLE[u'Enable'] + ' ' + __package__)

    # Do stuff here
        OSU.Setup.setRailroadName(patternConfig['CP']['LN'])

        patternConfig['CP'].update({__package__:False})
        PSE.writeConfigFile(patternConfig)

        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' removed from pattern scripts frame')
        print(__package__ + ' deactivated')
    else:
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable'] + ' ' + __package__)

        patternConfig['CP'].update({__package__:True})
        patternConfig['CP'].update({'LN':OSU.Setup.getRailroadName()})
        PSE.writeConfigFile(patternConfig)

    # Do stuff here
        jPlusHeader = PSE.jPlusHeader().replace(';', '\n')
        OSU.Setup.setRailroadName(jPlusHeader)

        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' added to pattern scripts frame')
        print(__package__ + ' activated')

    targetPanel.validate()
    targetPanel.repaint()

    return

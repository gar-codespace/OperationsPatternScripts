"""
Listeners for the TemplateSubroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.TemplateSubroutine.Listeners'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.xxx.Listeners')


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

        _psLog.info('Pattern Tracks subroutine deactivated')
        print('Pattern Tracks subroutine deactivated')
    else:
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable'] + ' ' + __package__)

    #  Do stuff here

        patternConfig['CP'].update({__package__:True})
        PSE.writeConfigFile(patternConfig)

        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info('Pattern Tracks subroutine activated')
        print('Pattern Tracks subroutine activated')

    targetPanel.validate()
    targetPanel.repaint()

    return
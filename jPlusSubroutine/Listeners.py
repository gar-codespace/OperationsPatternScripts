"""
Listeners for the jPlus subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.jPlusSubroutine.Listeners'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')

def actionListener(EVENT):
    """menu item-Tools/Enable j Plus Subroutine."""

    _psLog.debug(EVENT)
    patternConfig = PSE.readConfigFile()
    OSU = PSE.JMRI.jmrit.operations.setup

    if patternConfig['CP']['jPlusSubroutine']: # If enabled, turn it off
        patternConfig['CP'].update({'jPlusSubroutine':False})
        EVENT.getSource().setText(PSE.BUNDLE[u'Enable j Plus subroutine'])

        OSU.Setup.setRailroadName(patternConfig['CP']['LN'])

        _psLog.info('j Plus support deactivated')
        print('j Plus support deactivated')
    else:
        patternConfig['CP'].update({'jPlusSubroutine':True})
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable j Plus subroutine'])

        patternConfig['CP'].update({'LN':OSU.Setup.getRailroadName()})
        jPlusHeader = PSE.jPlusHeader().replace(';', '\n')
        OSU.Setup.setRailroadName(jPlusHeader)

        _psLog.info('j Plus support activated')
        print('j Plus support activated')

    PSE.writeConfigFile(patternConfig)
    PSE.closePsWindow()
    PSE.buildThePlugin()

    return

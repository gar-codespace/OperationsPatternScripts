"""
Listeners for the o2o subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from opsEntities import Listeners

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.Listeners'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Enable o2o subroutine"""

    _psLog.debug(EVENT)
    patternConfig = PSE.readConfigFile()

    if patternConfig['CP']['o2oSubroutine']: # If enabled, turn it off
        patternConfig['CP']['o2oSubroutine'] = False
        EVENT.getSource().setText(PSE.BUNDLE[u'Enable o2o subroutine'])

        Listeners.removeTrainsTableListener()

        _psLog.info('o2o subroutine deactivated')
        print('o2o subroutine deactivated')
    else:
        patternConfig['CP']['o2oSubroutine'] = True
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable o2o subroutine'])

        Listeners.addTrainsTableListener()

        _psLog.info('o2o subroutine activated')
        print('o2o subroutine activated')

    PSE.writeConfigFile(patternConfig)
    PSE.closePsWindow()
    PSE.buildThePlugin()

    return

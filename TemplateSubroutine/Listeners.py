"""
Listeners for the TemplateSubroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.TemplateSubroutine.Listeners'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.xxx.Listeners')

def actionListener(EVENT):
    """menu item-Tools/Enable xxx Subroutine."""

    _psLog.debug(EVENT)
    patternConfig = PSE.readConfigFile()

    if patternConfig['CP']['TemplateSubroutine']: # If enabled, turn it off
        patternConfig['CP']['TemplateSubroutine'] = False
        EVENT.getSource().setText(PSE.BUNDLE[u'Enable xxx subroutine'])

        # Do stuff here

        _psLog.info('jxxx support deactivated')
        print('xxx support deactivated')
    else:
        patternConfig['CP']['TemplateSubroutine'] = True
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable xxx subroutine'])

        #  Do stuff here

        _psLog.info('xxx support activated')
        print('xxx support activated')

    PSE.writeConfigFile(patternConfig)
    PSE.closePsWindow()
    PSE.buildThePlugin()

    return

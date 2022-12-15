"""
Listeners for the jPlus subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from jPlusSubroutine import Controller

SCRIPT_NAME = 'OperationsPatternScripts.jPlusSubroutine.Listeners'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')

def actionListener(EVENT):
    """menu item-Tools/Enable j Plus Subroutine."""

    _psLog.debug(EVENT)
    patternConfig = PSE.readConfigFile()
    OSU = PSE.JMRI.jmrit.operations.setup

    thisSubroutine = __package__

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')
    targetSubroutine = PSE.getComponentByName(frameTitle, thisSubroutine)

    if patternConfig['CP']['jPlusSubroutine']: # If enabled, turn it off
        patternConfig['CP'].update({thisSubroutine:False})
        EVENT.getSource().setText(PSE.BUNDLE[u'Enable' + ' ' + thisSubroutine])

        OSU.Setup.setRailroadName(patternConfig['CP']['LN'])

        targetPanel.remove(targetSubroutine)

        _psLog.info('j Plus support deactivated')
        print('j Plus support deactivated')
    else:
        patternConfig['CP'].update({thisSubroutine:True})
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable' + ' ' + thisSubroutine])

        patternConfig['CP'].update({'LN':OSU.Setup.getRailroadName()})
        jPlusHeader = PSE.jPlusHeader().replace(';', '\n')
        OSU.Setup.setRailroadName(jPlusHeader)


        for sub in patternConfig['CP']['IL']:
            target = PSE.getComponentByName(frameTitle, sub)
            try:
                targetPanel.remove(target)
            except:
                pass









        startUp = Controller.StartUp()
        subroutineFrame = startUp.makeSubroutineFrame()
        targetPanel.add(subroutineFrame)





        _psLog.info('j Plus support activated')
        print('j Plus support activated')

    PSE.writeConfigFile(patternConfig)

    targetPanel.revalidate()


    return

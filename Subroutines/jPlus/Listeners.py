"""
Listeners for the jPlus subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Enable jPlusSubroutine."""

    _psLog.debug(EVENT)

    patternConfig = PSE.readConfigFile()

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')

    OSU = PSE.JMRI.jmrit.operations.setup

# If it's on, turn it off
    if patternConfig['Main Script']['CP'][__package__]: 
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__
        patternConfig['Main Script']['CP'].update({__package__:False})
        
    # Do stuff specific to this subroutine here
        OSU.Setup.setRailroadName(patternConfig['jPlus']['LN'])


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
        OSU.Setup.setRailroadName(patternConfig['jPlus']['LN'])


        PSE.writeConfigFile(patternConfig)
        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' added to pattern scripts frame')
        print(__package__ + ' activated')








    # frameTitle = PSE.BUNDLE['Pattern Scripts']
    # targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')

    # if patternConfig['CP'][__package__]: # If enabled, turn it off
    #     EVENT.getSource().setText(PSE.BUNDLE[u'Enable'] + ' ' + __package__)

    # # Do stuff here
    #     OSU.Setup.setRailroadName(patternConfig['CP']['LN'])

    #     patternConfig['CP'].update({__package__:False})
    #     PSE.writeConfigFile(patternConfig)

    #     targetPanel.removeAll()
    #     targetPanel = PSE.addActiveSubroutines(targetPanel)

    #     _psLog.info(__package__ + ' removed from pattern scripts frame')
    #     print(__package__ + ' deactivated')
    # else:
    #     EVENT.getSource().setText(PSE.BUNDLE[u'Disable'] + ' ' + __package__)

    #     patternConfig['CP'].update({__package__:True})
    #     patternConfig['CP'].update({'LN':OSU.Setup.getRailroadName()})
    #     PSE.writeConfigFile(patternConfig)

    # # Do stuff here
    #     jPlusHeader = PSE.jPlusHeader().replace(';', '\n')
    #     OSU.Setup.setRailroadName(jPlusHeader)

    #     targetPanel.removeAll()
    #     targetPanel = PSE.addActiveSubroutines(targetPanel)

    #     _psLog.info(__package__ + ' added to pattern scripts frame')
    #     print(__package__ + ' activated')

    targetPanel.validate()
    targetPanel.repaint()



    EVENT.getSource().setText(menuText)
    

    return

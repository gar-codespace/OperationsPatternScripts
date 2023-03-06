"""
Listeners for the TemplateSubroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.TB.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Show Subroutines.Template"""

    _psLog.debug(EVENT)

    # PSE.closeSubordinateWindows()

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
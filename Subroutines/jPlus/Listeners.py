"""
Listeners for the jPlus subroutine.
JAVAX action performed methods are in Controller.
"""

from Subroutines.jPlus import Model
from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Show Subroutines.jPlus."""

    _psLog.debug(EVENT)

    # PSE.closeSubordinateWindows()

    configFile = PSE.readConfigFile()

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')

    # Hide this subroutine
    if configFile['Main Script']['CP'][__package__]: 
        menuText = PSE.BUNDLE[u'Show'] + ' ' + __package__
        configFile['Main Script']['CP'].update({__package__:False})
        
    # Do stuff specific to this subroutine here



        _psLog.info(__package__ + ' removed from pattern scripts frame')
        print(__package__ + ' deactivated')
    # Show this subroutine
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

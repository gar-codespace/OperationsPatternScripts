"""
Listeners for the jPlus subroutine.
JAVAX action performed methods are in Controller.
"""

from Subroutines.jPlus import Model
from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Enable Subroutines.jPlus."""

    _psLog.debug(EVENT)

    PSE.closeSubordinateWindows()

    configFile = PSE.readConfigFile()

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')

# If it's on, turn it off
    if configFile['Main Script']['CP'][__package__]: 
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__
        configFile['Main Script']['CP'].update({__package__:False})
        
    # Do stuff specific to this subroutine here
        OSU = PSE.JMRI.jmrit.operations.setup
        OSU.Setup.setRailroadName(configFile['Main Script']['LD']['LN'])
        PSE.JMRI.jmrit.operations.setup.OperationsSettingsPanel().savePreferences()


        _psLog.info(__package__ + ' removed from pattern scripts frame')
        print(__package__ + ' deactivated')
    else:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
        configFile['Main Script']['CP'].update({__package__:True})
        
    # Do stuff specific to this subroutine here
        Model.setExpandedHeader()



        _psLog.info(__package__ + ' added to pattern scripts frame')
        print(__package__ + ' activated')

    PSE.writeConfigFile(configFile)
    targetPanel.removeAll()
    targetPanel = PSE.addActiveSubroutines(targetPanel)
    targetPanel.validate()
    targetPanel.repaint()

    EVENT.getSource().setText(menuText)

    return

"""
Listeners for the Template subroutine.
JAVAX action performed methods are in Controller.
Replace XX with a designator for this subroutines name.
"""

from opsEntities import PSE
from Subroutines.Template import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.XX.Listeners')

def actionListener(EVENT):
    """
    menu item-Tools/Show Subroutines.Template
    """

    _psLog.debug(EVENT)

    configFile = PSE.readConfigFile()
    subroutineName = __package__.split('.')[1]

    if configFile[subroutineName]['SV']: # Hide this subroutine
        menuText = PSE.getBundleItem('Show') + ' ' + __package__
        configFile[subroutineName].update({'SV':False})
        _psLog.info('Hide ' + __package__)
        print('Hide ' + __package__)
    # Do subroutine specific stuff here



    else: # Show this subroutine
        menuText = PSE.getBundleItem('Hide') + ' ' + __package__
        configFile[subroutineName].update({'SV':True})
        _psLog.info('Show ' + __package__)
        print('Show ' + __package__)
    # Do subroutine specific stuff here



    PSE.writeConfigFile(configFile)
    PSE.repaintPatternScriptsWindow()

    EVENT.getSource().setText(menuText)

    return

def addSubroutineListeners():

    print('Template.Listeners.addSubroutineListeners')
    _psLog.debug('Template.Listeners.addSubroutineListeners')

    return

def removeSubroutineListeners():

    print('Template.Listeners.removeSubroutineListeners')
    _psLog.debug('Template.Listeners.removeSubroutineListeners')

    return


class OpsWindowPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    A property change listener attached to the Operations Pattern Scripts window.:
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'opsWindowActivated':
            Model.refreshSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        return

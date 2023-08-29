"""
Listeners for the jPlus subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines.jPlus import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')


def actionListener(EVENT):
    """
    menu item-Tools/Show Subroutines.jPlus.
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

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
    frame.addPropertyChangeListener(OpsWindowPropertyChange())

    PSE.LM.addPropertyChangeListener(jPlusPropertyChange())

    print('jPlus.Listeners.addSubroutineListeners')
    _psLog.debug('jPlus.Listeners.addSubroutineListeners')

    return

def removeSubroutineListeners():

    for listener in PSE.LM.getPropertyChangeListeners():
        if isinstance(listener, jPlusPropertyChange):
            PSE.LM.removePropertyChangeListener(listener)

            print('jPlus.Listeners.removeSubroutineListeners')
            _psLog.debug('jPlus.Listeners.removeSubroutineListeners')

    return


class OpsWindowPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    A property change listener attached to:
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'opsWindowActivated' and PROPERTY_CHANGE_EVENT.newValue == True:
            Model.refreshSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        return


class jPlusPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    A property change listener attached to:
    """

    def __init__(self):

        pass
    
    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'o2oUpdate':
            Model.refreshSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        return

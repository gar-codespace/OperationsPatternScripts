"""
Listeners for the Template subroutine.
JAVAX action performed methods are in Controller.
Replace XX with a designator for this subroutines name.
"""

from opsEntities import PSE
from Subroutines.Template import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.XX.Listeners')

def addSubroutineListeners():

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
    frame.addPropertyChangeListener(OpsWindowPropertyChange())

    print('Template.Listeners.addSubroutineListeners')
    _psLog.debug('Template.Listeners.addSubroutineListeners')

    return

def removeSubroutineListeners():

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    for listener in frame.getPropertyChangeListeners():
        if isinstance(listener, OpsWindowPropertyChange):
            PSE.LM.removePropertyChangeListener(listener)
            print('jPlus.Listeners.removeSubroutnieListeners.OpsWindowPropertyChange')
            
    print('Template.Listeners.removeSubroutineListeners')
    _psLog.debug('Template.Listeners.removeSubroutineListeners')

    return


class OpsWindowPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    A property change listener attached to the Operations Pattern Scripts window.
    
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'opsWindowActivated':
            Model.refreshSubroutine()

            _psLog.debug(PROPERTY_CHANGE_EVENT)

        return

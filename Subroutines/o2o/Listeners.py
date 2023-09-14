"""
Listeners for the o2o subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines.o2o import Model
from Subroutines.o2o import ModelWorkEvents

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Listeners')

def addSubroutineListeners():

    addTrainsTableListener()
    addTrainsListener()

    print('o2o.Listeners.addSubroutineListeners')
    _psLog.debug('o2o.Listeners.addSubroutineListeners')

    return

def removeSubroutineListeners():

    removeTrainsTableListener()
    removeTrainsListener()

    _psLog.debug('o2o.Listeners.removeSubroutineListeners')

    return

def addTrainsTableListener():

    PSE.TM.addPropertyChangeListener(o2oPropertyChange())

    _psLog.debug('o2o.Listeners.addTrainsTableListener')

    return

def addTrainsListener():
    """
    Adds a listener to each train.
    """

    for train in PSE.TM.getTrainsByIdList():
        train.addPropertyChangeListener(o2oPropertyChange())

    _psLog.debug('o2o.Listeners.addTrainsListener')

    return

def removeTrainsTableListener():

    for listener in PSE.TM.getPropertyChangeListeners():
        if isinstance(listener, o2oPropertyChange):
            PSE.TM.removePropertyChangeListener(listener)

            print('o2o.Listeners.removeTrainsTableListener.o2oPropertyChange')
            _psLog.debug('o2o.Listeners.removeTrainsTableListener')

    return

def removeTrainsListener():
    """
    Removes the listener attached to each train.
    """

    for train in PSE.TM.getTrainsByIdList():
        for listener in train.getPropertyChangeListeners():
            if isinstance(listener, o2oPropertyChange):
                train.removePropertyChangeListener(listener)

    print('o2o.Listeners.removeTrainsListener.o2oPropertyChange')
    _psLog.debug('o2o.Listeners.removeTrainsListener')

    return


class o2oPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Events that are triggered with changes to JMRI Trains and OPS/o2o switch lists.
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        sourceName = str(PROPERTY_CHANGE_EVENT.source)
        propertyName = PROPERTY_CHANGE_EVENT.getPropertyName()
        logMessage = 'o2o.Listeners.o2oPropertyChange- ' + sourceName + ' ' + propertyName

        if PROPERTY_CHANGE_EVENT.propertyName == 'TrainsListLength':
            """
            Called when a new train is added or an existing train is removed.
            """

            removeTrainsListener()
            addTrainsListener()

            _psLog.debug(logMessage)

        if PROPERTY_CHANGE_EVENT.propertyName == 'TrainBuilt' and PROPERTY_CHANGE_EVENT.newValue == True:
            """
            Called when a train is built.
            """

            ModelWorkEvents.convertJmriManifest()

            _psLog.debug(logMessage)

        if PROPERTY_CHANGE_EVENT.propertyName == 'patternsSwitchList' and PROPERTY_CHANGE_EVENT.newValue == True:
            """
            Called when the o2o Set Cars window Switch List button is pressed.
            """

            ModelWorkEvents.convertOpsSwitchList()

            _psLog.debug(logMessage)

        return

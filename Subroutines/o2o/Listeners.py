"""
Listeners for the o2o subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines.o2o import ModelWorkEvents

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Listeners')

def actionListener(EVENT):
    """menu item-Tools Show/Hide Subroutines.o2o."""

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


def addTrainsTableListener():

    PSE.TM.addPropertyChangeListener(TrainsPropertyChange())

    print('o2o.Listeners.addTrainsTableListener')
    _psLog.debug('o2o.Listeners.addTrainsTableListener')

    return

def addTrainsListener():
    """
    Adds a listener to each train.
    """

    for train in PSE.TM.getTrainsByIdList():
        train.addPropertyChangeListener(TrainsPropertyChange())

    print('o2o.Listeners.addTrainsListener')
    _psLog.debug('o2o.Listeners.addTrainsListener')

    return

def removeTrainsTableListener():

    for listener in PSE.TM.getPropertyChangeListeners():
        if isinstance(listener, TrainsPropertyChange):
            PSE.TM.removePropertyChangeListener(listener)
            print('o2o.Listeners.removeTrainsTableListener')
            _psLog.debug('o2o.Listeners.removeTrainsTableListener')

    return

def removeTrainsListener():
    """
    Removes the listener attached to each train.
    """

    for train in PSE.TM.getTrainsByIdList():
        for listener in train.getPropertyChangeListeners():
            if isinstance(listener, TrainsPropertyChange):
                train.removePropertyChangeListener(listener)

    print('o2o.Listeners.removeTrainsListener')
    _psLog.debug('o2o.Listeners.removeTrainsListener')

    return


class TrainsPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Events that are triggered with changes to JMRI Trains and OPS/o2o switch lists.
    """

    def __init__(self):

        pass

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        sourceName = str(PROPERTY_CHANGE_EVENT.source)
        propertyName = PROPERTY_CHANGE_EVENT.getPropertyName()
        logMessage = 'o2o.Listeners.TrainsPropertyChange- ' + sourceName + ' ' + propertyName

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

        if PROPERTY_CHANGE_EVENT.propertyName == 'o2oSwitchList' and PROPERTY_CHANGE_EVENT.newValue == True:
            """
            Called when the o2o Set Cars window Switch List button is pressed.
            """

            ModelWorkEvents.convertOpsSwitchList()

            _psLog.debug(logMessage)

        return

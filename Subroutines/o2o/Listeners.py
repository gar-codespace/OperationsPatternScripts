"""
Listeners for the o2o subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Show Subroutines.o2o."""

    _psLog.debug(EVENT)

    # PSE.closeSubordinateWindows()

    configFile = PSE.readConfigFile()

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')

# If it's on, turn it off
    if configFile['Main Script']['CP'][__package__]: 
        menuText = PSE.BUNDLE[u'Show'] + ' ' + __package__
        configFile['Main Script']['CP'].update({__package__:False})

    # Do stuff here
        # removeBuiltTrainListener()

        _psLog.info(__package__ + ' removed from pattern scripts frame')
        print(__package__ + ' deactivated')
    else:
        menuText = PSE.BUNDLE[u'Hide'] + ' ' + __package__
        configFile['Main Script']['CP'].update({__package__:True})

    # Do stuff here
        addBuiltTrainListener()

        _psLog.info(__package__ + ' added to pattern scripts frame')
        print(__package__ + ' activated')

    PSE.writeConfigFile(configFile)
    targetPanel.removeAll()
    targetPanel = PSE.addActiveSubroutines(targetPanel)
    targetPanel.validate()
    targetPanel.repaint()

    EVENT.getSource().setText(menuText)

    return

def addTrainsTableListener():

    PSE.TM.addPropertyChangeListener(o2oTrainsTable())

    return


class o2oTrainsTable(PSE.JAVA_BEANS.PropertyChangeListener):
    """The trains table model gets this listener."""

    def __init__(self):

        return

    def propertyChange(self, TRAIN_LIST):

        _psLog.debug(TRAIN_LIST)

        if TRAIN_LIST.propertyName == 'TrainsListLength':

            removeBuiltTrainListener()
            addBuiltTrainListener()

        return


def addBuiltTrainListener():
    """
    Adds BuiltTrain to every train in the roster.
    """

    removeBuiltTrainListener()

    trainList = PSE.TM.getTrainsByIdList()
    for train in trainList:
        train.addPropertyChangeListener(BuiltTrain())
    return

def removeBuiltTrainListener():
    """
    Removes BuiltTrain from every train in the roster.
    """
        
    trainList = PSE.TM.getTrainsByIdList()
    for train in trainList:
        for listener in train.getPropertyChangeListeners():
            if listener.getClass() == BuiltTrain:
                train.removePropertyChangeListener(listener)

    return


class BuiltTrain(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Starts o2oWorkEventsBuilder on trainBuilt.
    """

    def propertyChange(self, TRAIN_BUILT):

        _psLog.debug(TRAIN_BUILT)

        if TRAIN_BUILT.propertyName == 'TrainBuilt' and TRAIN_BUILT.newValue == True:
            xModule = __import__(__package__, globals(), locals(), ['BuiltTrainExport'], 0)
            o2oWorkEvents = xModule.BuiltTrainExport.o2oWorkEventsBuilder()
            o2oWorkEvents.passInTrain(TRAIN_BUILT.getSource())
            o2oWorkEvents.start()

        return

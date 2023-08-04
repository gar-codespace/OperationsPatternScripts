"""
Listeners for the o2o subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines.o2o import ModelWorkEvents

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')

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

    PSE.TM.addPropertyChangeListener(o2oTrainsTable())

    return

def removeTrainsTableListener():

    PSE.TM.removePropertyChangeListener(o2oTrainsTable())

    return


class o2oTrainsTable(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    The trains table model gets this listener.
    """

    def __init__(self):

        return

    def propertyChange(self, TRAIN_LIST):

        _psLog.debug(TRAIN_LIST)
        print(SCRIPT_NAME + '.o2oTrainsTable ' + str(SCRIPT_REV))

        if TRAIN_LIST.propertyName == 'TrainsListLength':
            removeBuiltTrainListener()
            addBuiltTrainListener()
            _psLog.info('Train roster changed')

        if TRAIN_LIST.propertyName == 'PatternsSwitchList' and TRAIN_LIST.newValue == True:
            ModelWorkEvents.o2oWorkListMaker()
            _psLog.info('Patterns switch list generated')

        return


def addBuiltTrainListener():
    """
    Adds o2oBuiltTrain to every train in the roster.
    """

    removeBuiltTrainListener()

    trainList = PSE.TM.getTrainsByIdList()
    for train in trainList:
        train.addPropertyChangeListener(o2oBuiltTrain())
    return

def removeBuiltTrainListener():
    """
    Removes o2oBuiltTrain from every train in the roster.
    """
        
    trainList = PSE.TM.getTrainsByIdList()
    for train in trainList:
        for listener in train.getPropertyChangeListeners():
            if listener.getClass() == o2oBuiltTrain:
                train.removePropertyChangeListener(listener)

    return


class o2oBuiltTrain(PSE.JAVA_BEANS.PropertyChangeListener):
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


class o2oSwitchList(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Starts ModelWorkEvents.o2oWorkListMaker() on trainBuilt.
    """

    def propertyChange(self, OPS_SWITCH_LIST):

        _psLog.debug(OPS_SWITCH_LIST)

        if OPS_SWITCH_LIST.propertyName == 'xyzzy' and OPS_SWITCH_LIST.newValue == True:
            print('Yipee')
            # ModelWorkEvents.o2oWorkListMaker()
            # xModule = __import__(__package__, globals(), locals(), ['BuiltTrainExport'], 0)
            # o2oWorkEvents = xModule.BuiltTrainExport.o2oWorkEventsBuilder()
            # o2oWorkEvents.passInTrain(TRAIN_BUILT.getSource())
            # o2oWorkEvents.start()

        return

    
"""
Listeners for the o2o subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines.o2o import ModelWorkEvents
from Subroutines.o2o import BuiltTrainExport

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


def addTrainsListener():

    PSE.TM.addPropertyChangeListener(TrainsPropertyChange())

    trainList = PSE.TM.getTrainsByIdList()
    for train in trainList:
        train.addPropertyChangeListener(TrainsPropertyChange())

    print('o2o.activatedCalls.Listeners.addTrainsTableListener')
    print('o2o.activatedCalls.Listeners.addBuiltTrainListener')

    return

def removeTrainsListener():

    PSE.TM.removePropertyChangeListener(TrainsPropertyChange())

    trainList = PSE.TM.getTrainsByIdList()
    for train in trainList:
        train.removePropertyChangeListener(TrainsPropertyChange())

    print('o2o.activatedCalls.Listeners.removeTrainsTableListener')
    print('o2o.activatedCalls.Listeners.removeBuiltTrainListener')

    return


class TrainsPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
    """
    Events that are triggered with changes to JMRI Trains.
    """

    def __init__(self):

        return

    def propertyChange(self, PROPERTY_CHANGE_EVENT):

        if PROPERTY_CHANGE_EVENT.propertyName == 'TrainsListLength':
            removeTrainsListener()
            addTrainsListener()

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.TrainsPropertyChange.TrainsListLength ' + str(SCRIPT_REV))

        if PROPERTY_CHANGE_EVENT.propertyName == 'TrainBuilt' and PROPERTY_CHANGE_EVENT.newValue == True:
            xModule = __import__(__package__, globals(), locals(), ['BuiltTrainExport'], 0)
            o2oWorkEvents = xModule.BuiltTrainExport.o2oWorkEventsBuilder()
            o2oWorkEvents.passInTrain(PROPERTY_CHANGE_EVENT.getSource())
            o2oWorkEvents.start()

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.TrainsPropertyChange.TrainBuilt ' + str(SCRIPT_REV))

        if PROPERTY_CHANGE_EVENT.propertyName == 'PatternsSwitchList' and PROPERTY_CHANGE_EVENT.newValue == True:

            BuiltTrainExport.o2oWorkListMaker()

            _psLog.debug(PROPERTY_CHANGE_EVENT)
            print(SCRIPT_NAME + '.TrainsPropertyChange.PatternsSwitchList ' + str(SCRIPT_REV))

        return

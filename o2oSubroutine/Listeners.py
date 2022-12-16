"""
Listeners for the o2o subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
# from opsEntities import Listeners

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.Listeners'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Enable o2oSubroutine."""

    _psLog.debug(EVENT)
    patternConfig = PSE.readConfigFile()
    OSU = PSE.JMRI.jmrit.operations.setup

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')

    if patternConfig['CP'][__package__]: # If enabled, turn it off
        EVENT.getSource().setText(PSE.BUNDLE[u'Enable'] + ' ' + __package__)

    # Do stuff here

        patternConfig['CP'].update({__package__:False})
        PSE.writeConfigFile(patternConfig)

        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info('o2o subroutine deactivated')
        print('o2o subroutine deactivated')
    else:
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable'] + ' ' + __package__)

    # Do stuff here

        patternConfig['CP'].update({__package__:True})
        PSE.writeConfigFile(patternConfig)

        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info('o2o subroutine activated')
        print('o2o subroutine activated')

    targetPanel.validate()
    targetPanel.repaint()

    return


class TrainsTable(PSE.JAVX_SWING.event.TableModelListener):
    """Catches user add or remove train while o2oSubroutine is enabled."""

    def __init__(self, builtTrainListener):

        self.builtTrainListener = builtTrainListener

        return

    def tableChanged(self, TABLE_CHANGE):

        _psLog.debug(TABLE_CHANGE)

        # removeBuiltTrainListener()
        # addBuiltTrainListener()

        # trainList = PSE.TM.getTrainsByIdList()
        # for train in trainList:
        # # Does not throw error if there is no listener to remove :)
        #     print('removeBuiltTrainListener')
        #     train.removePropertyChangeListener(self.builtTrainListener)
        #     train.addPropertyChangeListener(self.builtTrainListener)

        return


class BuiltTrain(PSE.JAVA_BEANS.PropertyChangeListener):
    """Starts o2oWorkEventsBuilder on trainBuilt."""

    def propertyChange(self, TRAIN_BUILT):

        configFile = PSE.readConfigFile('CP')

        if TRAIN_BUILT.propertyName != 'TrainBuilt':
            return

        if configFile['o2oSubroutine'] and TRAIN_BUILT.newValue == True:
            xModule = __import__('o2oSubroutine', globals(), locals(), ['BuiltTrainExport'], 0)
            o2oWorkEvents = xModule.BuiltTrainExport.o2oWorkEventsBuilder()
            o2oWorkEvents.passInTrain(TRAIN_BUILT.getSource())
            o2oWorkEvents.start()

        # if configFile['jPlusSubroutine'] and TRAIN_BUILT.newValue == True:
        #     trainManifest = 'train (' + TRAIN_BUILT.getSource().getName() + ').txt'
        #     # Expand this later

        return


def addTrainsTableListener():
    """ """

    builtTrainListener = BuiltTrain()
    trainsTableListener = TrainsTable(builtTrainListener)

    trainsTableModel = PSE.JMRI.jmrit.operations.trains.TrainsTableModel()
    trainsTableModel.addTableModelListener(trainsTableListener)

    return

def addBuiltTrainListener():
    """Called by:
        PatternScriptsWindow.windowOpened
        o2oSubroutine.Listeners.actionListener
        """

    trainList = PSE.TM.getTrainsByIdList()
    for train in trainList:
        train.addPropertyChangeListener(BuiltTrain())
    return

def removeBuiltTrainListener():
    """Called by:
        PatternScriptsWindow.windowClosing
        o2oSubroutine.Listeners.actionListener
        """
        
    trainList = PSE.TM.getTrainsByIdList()
    for train in trainList:
        for listener in train.getPropertyChangeListeners():
            if listener.getClass() == BuiltTrain:
                train.removePropertyChangeListener(listener)

    return
"""
Listeners for the o2o subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.JP.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Enable Subroutines.o2o."""

    _psLog.debug(EVENT)

    PSE.closeSubordinateWindows()

    patternConfig = PSE.readConfigFile()

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'subroutinePanel')

# If it's on, turn it off
    if patternConfig['Main Script']['CP'][__package__]: 
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__
        patternConfig['Main Script']['CP'].update({__package__:False})

    # Do stuff here
        removeBuiltTrainListener()


        PSE.writeConfigFile(patternConfig)
        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' removed from pattern scripts frame')
        print(__package__ + ' deactivated')
    else:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
        patternConfig['Main Script']['CP'].update({__package__:True})

    # Do stuff here
        addBuiltTrainListener()


        PSE.writeConfigFile(patternConfig)
        targetPanel.removeAll()
        targetPanel = PSE.addActiveSubroutines(targetPanel)

        _psLog.info(__package__ + ' added to pattern scripts frame')
        print(__package__ + ' activated')

    targetPanel.validate()
    targetPanel.repaint()

    EVENT.getSource().setText(menuText)

    return


class TrainsTable(PSE.JAVX_SWING.event.TableModelListener):
    """Catches user add or remove train while o2oSubroutine is enabled.
    Check into TM.newTrain.LISTLENGTH_CHANGED_PROPERTY"""

    def __init__(self, builtTrainListener):

        self.builtTrainListener = builtTrainListener

        return

    def tableChanged(self, TABLE_CHANGE):

        _psLog.debug(TABLE_CHANGE)

        removeBuiltTrainListener()
        addBuiltTrainListener()

        return


class BuiltTrain(PSE.JAVA_BEANS.PropertyChangeListener):
    """Starts o2oWorkEventsBuilder on trainBuilt."""

    def propertyChange(self, TRAIN_BUILT):

        configFile = PSE.readConfigFile()

        if TRAIN_BUILT.propertyName != 'TrainBuilt':
            return

        if configFile['Main Script']['CP'][__package__] and TRAIN_BUILT.newValue == True:
            xModule = __import__(__package__, globals(), locals(), ['BuiltTrainExport'], 0)
            o2oWorkEvents = xModule.BuiltTrainExport.o2oWorkEventsBuilder()
            o2oWorkEvents.passInTrain(TRAIN_BUILT.getSource())
            o2oWorkEvents.start()

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

    removeBuiltTrainListener()

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
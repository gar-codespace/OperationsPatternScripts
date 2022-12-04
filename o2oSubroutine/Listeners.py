"""
Listeners for the o2o subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from opsEntities import Listeners

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.Listeners'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Listeners')


def actionListener(EVENT):
    """menu item-Tools/Enable o2o subroutine"""

    _psLog.debug(EVENT)
    patternConfig = PSE.readConfigFile()

    if patternConfig['CP']['o2oSubroutine']: # If enabled, turn it off
        patternConfig['CP']['o2oSubroutine'] = False
        EVENT.getSource().setText(PSE.BUNDLE[u'Enable o2o subroutine'])

        Listeners.removeTrainsTableListener()

        _psLog.info('o2o subroutine deactivated')
        print('o2o subroutine deactivated')
    else:
        patternConfig['CP']['o2oSubroutine'] = True
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable o2o subroutine'])

        Listeners.addTrainsTableListener()

        _psLog.info('o2o subroutine activated')
        print('o2o subroutine activated')

    PSE.writeConfigFile(patternConfig)
    PSE.closePsWindow()
    PSE.buildThePlugin()

    return


# class TrainsTable(PSE.JAVX_SWING.event.TableModelListener):
#     """Catches user add or remove train while o2oSubroutine is enabled."""

#     def __init__(self, builtTrainListener):

#         self.builtTrainListener = builtTrainListener

#         return

#     def tableChanged(self, TABLE_CHANGE):

#         trainList = PSE.TM.getTrainsByIdList()
#         for train in trainList:
#         # Does not throw error if there is no listener to remove :)
#             train.removePropertyChangeListener(self.builtTrainListener)
#             train.addPropertyChangeListener(self.builtTrainListener)

#         return


# class BuiltTrain(PSE.JAVA_BEANS.PropertyChangeListener):
#     """Starts o2oWorkEventsBuilder on trainBuilt."""

#     def propertyChange(self, TRAIN_BUILT):

#         configFile = PSE.readConfigFile('CP')

#         if not TRAIN_BUILT.propertyName == 'TrainBuilt' and TRAIN_BUILT.newValue:
#             return

#         if configFile['o2oSubroutine']:
#             xModule = __import__('o2oSubroutine', globals(), locals(), ['BuiltTrainExport'], 0)
#             o2oWorkEvents = xModule.BuiltTrainExport.o2oWorkEventsBuilder()
#             o2oWorkEvents.passInTrain(TRAIN_BUILT.getSource())
#             o2oWorkEvents.start()

#         if configFile['jPlusSubroutine']:
#             trainManifest = 'train (' + TRAIN_BUILT.getSource().getName() + ').txt'

#         return

# """
# Support methods for TrainsTable and BuiltTrain.
# Move these back to Controller?
# """

# def addTrainsTableListener():

#     builtTrainListener = BuiltTrain()
#     trainsTableListener = TrainsTable(builtTrainListener)

#     trainsTableModel = PSE.JMRI.jmrit.operations.trains.TrainsTableModel()
#     trainsTableModel.addTableModelListener(trainsTableListener)

#     return

# def removeTrainsTableListener():

#     trainsTableModel = PSE.JMRI.jmrit.operations.trains.TrainsTableModel()
#     try:
#         trainsTableModel.removeTableModelListener(trainsTableListener)
#     except:
#         pass

#     removeBuiltTrainListener()

#     return

# def addBuiltTrainListener():

#     trainList = PSE.TM.getTrainsByIdList()
#     for train in trainList:
#         train.addPropertyChangeListener(BuiltTrain())
#     return

# def removeBuiltTrainListener():

#     trainList = PSE.TM.getTrainsByIdList()
#     for train in trainList:
#         for listener in train.getPropertyChangeListeners():
#             if listener.getClass() == BuiltTrain:
#                 train.removePropertyChangeListener(listener)

#     return

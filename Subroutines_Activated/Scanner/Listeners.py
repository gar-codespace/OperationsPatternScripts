"""
Listeners for the Scanner subroutine.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
from Subroutines_Activated.Scanner import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.SC.Listeners')


class ScannerSelection(PSE.JAVA_AWT.event.ActionListener):
    """
    Runs a routine on the selected scanner.
    """

    def __init__(self):

        pass

    def actionPerformed(self, EVENT):

        Model.recordSelection(EVENT.getSource())

        return
    


# class ListenToThePSWindow(PSE.JAVA_BEANS.PropertyChangeListener):
#     """
#     Every subroutine has this class.
#     Listens for changes to the Pattern Scripts plugin window.
#     """

#     def __init__(self):

#         pass

#     def propertyChange(self, PROPERTY_CHANGE_EVENT):
    
#         if PROPERTY_CHANGE_EVENT.propertyName == 'windowOpened':

#             addSubroutineListeners()
#             Model.initializeSubroutine()
            
#             _psLog.debug(PROPERTY_CHANGE_EVENT)

#         if PROPERTY_CHANGE_EVENT.propertyName == 'windowActivated':

#             Model.refreshSubroutine()
            
#             _psLog.debug(PROPERTY_CHANGE_EVENT)

#         if PROPERTY_CHANGE_EVENT.propertyName == 'windowClosing':
            
#             # removeSubroutineListeners()
            
#             _psLog.debug(PROPERTY_CHANGE_EVENT)
            
#         return
    

# def addSubroutineListeners():
#     """
#     A listener to detect if an event outside of this subroutine
#     needs to trigger something within this subroutine.
#     Check the other subroutines for ideas on how to implement this.
#     """

#     addTrainsListener()
#     # print('Scanner.Listeners.addSubroutineListeners')
#     # _psLog.debug('Scanner.Listeners.addSubroutineListeners')

#     return

# def removeSubroutineListeners():
#     """
#     When the Pattern Scripts window is closed, turn off the listeners for this subroutine.
#     Check the other subroutines for ideas on how to implement this.
#     """

#     # _psLog.debug('Scanner.Listeners.removeSubroutineListeners')

#     return




    
# def addTrainsListener():
#     """
#     Adds a listener to each train.
#     """

#     for train in PSE.TM.getTrainsByIdList():
#         train.addPropertyChangeListener(ScannerPropertyChange())
#         _psLog.debug('Scanner.Listeners.addTrainsListener: ' + train.getName())

#     return


# class ScannerPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
#     """
#     Events that are triggered with changes to JMRI Trains and OPS/o2o switch lists.
#     """

#     def __init__(self):

#         pass

#     def propertyChange(self, PROPERTY_CHANGE_EVENT):

#         sourceName = str(PROPERTY_CHANGE_EVENT.source)
#         propertyName = PROPERTY_CHANGE_EVENT.getPropertyName()
#         logMessage = 'Scanner.Listeners.ScannerPropertyChange- ' + sourceName + ' ' + propertyName


#         if PROPERTY_CHANGE_EVENT.propertyName == 'TrainBuilt' and PROPERTY_CHANGE_EVENT.newValue == True:
#             """
#             Called when a train is built.
#             """

#             train = PROPERTY_CHANGE_EVENT.getSource()
#             Model.modifyTrainManifest(train)

#             _psLog.debug(logMessage)

"""
'Local' level listeners for the jPlus subroutine.
For OPS interoperability or JMRI events, add a laitener to opsEntities.PluginListeners.
JAVAX action performed methods are in Controller.
"""

from opsEntities import PSE
# from Subroutines_Activated.jPlus import Model

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.JP.SubroutineListeners')


# class ListenToThePSWindow(PSE.JAVA_BEANS.PropertyChangeListener):
#     """
#     Listens for changes to the Pattern Scripts plugin window.
#     """

#     def __init__(self):

#         pass

#     def propertyChange(self, PROPERTY_CHANGE_EVENT):
    
#         if PROPERTY_CHANGE_EVENT.propertyName == 'windowOpened':

#             addSubroutineListeners()
#             Model.resetSubroutine()
            
#             _psLog.debug(PROPERTY_CHANGE_EVENT)

#         if PROPERTY_CHANGE_EVENT.propertyName == 'windowActivated':

#             Model.refreshSubroutine()
            
#             _psLog.debug(PROPERTY_CHANGE_EVENT)

#         if PROPERTY_CHANGE_EVENT.propertyName == 'windowClosing':

#             removeSubroutineListeners()
            
#             _psLog.debug(PROPERTY_CHANGE_EVENT)
            
#         return
    

# def addSubroutineListeners():

#     PSE.LM.addPropertyChangeListener(jPlusPropertyChange())

#     print('jPlus.Listeners.addSubroutineListeners')
#     _psLog.debug('jPlus.Listeners.addSubroutineListeners')

#     return

# def removeSubroutineListeners():

#     for listener in PSE.LM.getPropertyChangeListeners():
#         if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'jPlusPropertyChange' in listener.toString():
#             PSE.LM.removePropertyChangeListener(listener)

#             print('jPlus.Listeners.removeSubroutnieListeners')
#             _psLog.debug('jPlus.Listeners.removeSubroutineListeners')

#     return


# class jPlusPropertyChange(PSE.JAVA_BEANS.PropertyChangeListener):
#     """
#     A property change listener attached to the Location Manager.
#     """

#     def __init__(self):

#         pass
    
#     def propertyChange(self, PROPERTY_CHANGE_EVENT):

#         if PROPERTY_CHANGE_EVENT.propertyName == 'extendedDetails':
#             Model.refreshSubroutine()

#             _psLog.debug(PROPERTY_CHANGE_EVENT)

#         return

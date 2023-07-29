# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from opsEntities import PSE
from Subroutines.o2o import Listeners
from Subroutines.o2o import ModelWorkEvents


def activatedCalls():
    """Methods called when this subroutine is activated."""

    configFile = PSE.readConfigFile()
    if configFile['Main Script']['CP'][__package__]:
        Listeners.addTrainsTableListener()
        Listeners.addBuiltTrainListener()
        print('addBuiltTrainListener')

    return

def deActivatedCalls():
    """Methods called when this subroutine is deactivated."""

    Listeners.removeTrainsTableListener()
    Listeners.removeBuiltTrainListener()
    print('removeBuiltTrainListener')

    return

def refreshCalls():
    """Methods called when the subroutine needs to be refreshed."""

    return

def resetCalls():
    """Methods called to reset this subroutine."""

    return
    
def specificCalls():
    """Methods called to run specific tasks."""

    ModelWorkEvents.o2oWorkListMaker()

    return
    
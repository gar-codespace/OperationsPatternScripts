# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from Subroutines.o2o import Model
from Subroutines.o2o import Listeners

def activatedCalls():
    """
    Methods called when this subroutine is activated.
    """

    Listeners.addTrainsTableListener()
    Listeners.addTrainsListener()

    return

def deactivatedCalls():
    """
    Methods called when this subroutine is deactivated.
    """

    Listeners.removeTrainsTableListener()
    Listeners.removeTrainsListener()

    return

def refreshCalls():
    """
    Methods called when the subroutine needs to be refreshed.
    """

    Model.refreshSubroutine()

    return

def resetCalls():
    """
    Methods called to reset this subroutine.
    """

    return
    
def specificCalls():
    """
    Methods called to run specific tasks.
    """

    return
    
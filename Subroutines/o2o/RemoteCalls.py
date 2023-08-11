# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from Subroutines.o2o import Listeners

def activatedCalls():
    """Methods called when this subroutine is activated."""

    Listeners.addTrainsListener()

    return

def deActivatedCalls():
    """Methods called when this subroutine is deactivated."""

    Listeners.removeTrainsListener()

    return

def refreshCalls():
    """Methods called when the subroutine needs to be refreshed."""

    return

def resetCalls():
    """Methods called to reset this subroutine."""

    return
    
def specificCalls():
    """Methods called to run specific tasks."""

    return
    
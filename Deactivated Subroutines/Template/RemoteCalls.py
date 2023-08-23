# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from Subroutines.Template import Model


def activatedCalls():
    """Methods called when this subroutine is activated."""

    return

def deactivatedCalls():
    """Methods called when this subroutine is deactivated."""

    return

def refreshCalls():
    """Methods called when the subroutine needs to be refreshed."""

    Model.refreshSubroutine()
    
    return

def resetCalls():
    """Methods called to reset this subroutine."""

    Model.resetConfigFileItems()
   
    return
    
def specificCalls():
    """Methods called to run specific tasks."""

    return
    
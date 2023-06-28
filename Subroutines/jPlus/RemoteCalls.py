# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from Subroutines.jPlus import Model


def activatedCalls():
    """Methods called when this subroutine is activated."""

    # Model.extendedHeaderActivator(False)
    
    return

def deActivatedCalls():
    """Methods called when this subroutine is deactivated."""

    Model.extendedHeaderActivator(False)

    return

def refreshCalls():
    """Methods called when the subroutine needs to be refreshed."""

    Model.updateYearModeled()
    Model.extendedRailroadDetails()
    
    return

def resetCalls():
    """Methods called to reset this subroutine."""

    # Model.resetConfigFileItems()

    return
        
def specificCalls():
    """Methods called to run specific tasks."""

    return
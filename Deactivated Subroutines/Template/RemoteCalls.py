# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from opsEntities import PSE


def activatedCalls():
    """Methods called when this subroutine is activated."""

    # configFile = PSE.readConfigFile()
    # if configFile['Main Script']['CP'][__package__]:

    return

def deActivatedCalls():
    """Methods called when this subroutine is deactivated."""

    return

def refreshCalls():
    """Methods called when the subroutine needs to be refreshed."""

    PSE.restartSubroutineByName(__package__)
    
    return

def resetCalls():
    """Methods called to reset this subroutine."""

   # Model.resetConfigFileItems()
   
    return
    
def specificCalls():
    """Methods called to run specific tasks."""

    return
    
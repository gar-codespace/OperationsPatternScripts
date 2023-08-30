# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from Subroutines.Patterns import Model
from Subroutines.Patterns import Listeners

def startupCalls():
    """
    Called when the plugin is started.
    """

    Model.initializeSubroutine()
    Listeners.addSubroutineListeners()
    
    return

def shutdownCalls():
    """
    Called when the plugin is shut down.
    """

    Listeners.removeSubroutineListeners()

    return

def resetCalls():
    """
    Depricated.
    """

    Model.resetConfigFileItems()
    
    return

def nonSpecificCalls():
    """
    Catchall if the others are not appropriate
    """

    return
    
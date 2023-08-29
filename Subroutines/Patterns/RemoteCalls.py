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
    Methods called when the plugin is started.
    """

    Model.initializeSubroutine()
    Listeners.addSubroutineListeners()
    
    return

def shutdownCalls():
    """
    Methods called when the plugin is shut down.
    """

    Listeners.removeSubroutineListeners()

    return

def resetCalls():
    """
    Methods called to reset this subroutine.
    """

    Model.resetConfigFileItems()
    
    return

def specificCalls():
    """
    Methods called to run specific tasks.
    """

    return
    
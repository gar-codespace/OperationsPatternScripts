# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from Subroutines.o2o import Model
from Subroutines.o2o import Listeners

def startupCalls():
    """
    Methods called when the plugin is started.
    """

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

    return
    
def specificCalls():
    """
    Methods called to run specific tasks.
    """

    return
    
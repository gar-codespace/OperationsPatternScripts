# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from opsEntities import PSE
from Subroutines.o2o import Listeners
from Subroutines.o2o import ModelWorkEvents

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.o2o.RemoteCalls')


def startupCalls():
    """Methods called when this subroutine is initialized by the Main Script.
        These calls are not turned off.
        """

    Listeners.addTrainsTableListener()

    return

def activatedCalls():
    """Methods called when this subroutine is activated."""

    Listeners.addBuiltTrainListener()

    return

def deActivatedCalls():
    """Methods called when this subroutine is deactivated."""

    Listeners.removeBuiltTrainListener()

    return

def refreshCalls():
    """Methods called when the subroutine needs to be refreshed."""

    return

def specificCalls():
    """Methods called to run specific tasks."""

    ModelWorkEvents.o2oWorkListMaker()

    return
    
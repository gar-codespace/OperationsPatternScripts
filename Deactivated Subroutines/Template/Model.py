# coding=utf-8
# © 2023 Greg Ritacco

"""
Template subroutine.
Replace XX with a designator for this subroutines name.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.XX.Model')

def initializeSubroutine():
    """
    Called from PSE.remoteCalls('activatedCalls')
    After the subroutine is built, set it to its' initial values.
    """

    return

def resetConfigFileItems():
    """Called from PSE.remoteCalls('resetCalls')"""

    return

def refreshSubroutine():
    """
    Called from PSE.remoteCalls('refreshCalls')
    """

    return
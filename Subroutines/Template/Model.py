# coding=utf-8
# © 2023 Greg Ritacco

"""
Template subroutine.
Replace XX with a designator for this subroutines name.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.XX.Model')

def initializeSubroutine():
    """
    """

    return

def resetConfigFileItems():
    """
    """

    return

def refreshSubroutine():
    """
    """
    
    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

    return
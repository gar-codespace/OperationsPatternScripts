# coding=utf-8
# © 2023 Greg Ritacco

"""
Template subroutine.
Replace XX with a designator for this subroutines name.
"""

from opsEntities import PSE

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.XX.Model')


""" Routines called by the plugin listeners """


def resetConfigFileItems():

    return

def initializeSubroutine():
    
    return

def resetSubroutine():

    return

def refreshSubroutine():

    return

def addSubroutineListeners():
    """
    Add any listeners specific to this subroutine.
    """

    return

def removeSubroutineListeners():
    """
    Removes any listeners specific to this subroutine.
    """

    return


""" Routines specific to this subroutine """

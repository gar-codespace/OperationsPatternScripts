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

def resetConfigFileItems():
    """
    Put configFile items here that need to be set to their defaults when this subroutine is reset.
    """

    return

def initializeSubroutine():
    """
    If any widgets need to be set to a value saved in the config file when the Pattern Scripts window is opened,
    set those widgets here.
    """
    
    return

def resetSubroutine():
    """
    When the Pattern Scripts window is opened, this subroutine is reset to catch any outside 
    changes made to JMRI that would effect this subroutine.
    """

    return

def refreshSubroutine():
    """
    When the Pattern Scripts window is activated by clicking on it,
    update any widgets in this subroutine that can't otherwise be updated by a listener.
    """

    return
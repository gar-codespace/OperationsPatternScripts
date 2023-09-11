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
    After the subroutine is built, set it to its' initial values.
    """

    return

def resetConfigFileItems():
    """
    Put configFile items here that need to be set to their defaults when this subroutine is reset.
    """

    # configFile = PSE.readConfigFile()

    # Reset stuff here

    # PSE.writeConfigFile(configFile)

    return

def refreshSubroutine():
    """
    """
    
    _psLog.debug('refreshSubroutine')
    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

    return
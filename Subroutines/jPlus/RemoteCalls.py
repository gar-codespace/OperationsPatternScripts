# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from opsEntities import PSE
from Subroutines.jPlus import Model

# SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
# SCRIPT_REV = 20230201

# _psLog = PSE.LOGGING.getLogger('OPS.JP.RemoteCalls')


def startupCalls():
    """
    Methods called when this subroutine is initialized by the Main Script.
    These calls are not turned off.
    """

    print('jPlus startupCalls')

    OSU = PSE.JMRI.jmrit.operations.setup
    configFile = PSE.readConfigFile()
    if configFile['Main Script']['LD']['LN'] == '':
        configFile['Main Script']['LD'].update({'LN':OSU.Setup.getRailroadName()})
        PSE.writeConfigFile(configFile)

    return

def activatedCalls():
    """Methods called when this subroutine is activated."""

    # Model.setExpandedHeader()
    print('jPlus activated')

    return

def deActivatedCalls():
    """Methods called when this subroutine is deactivated."""

    Model.setDefaultHeader()
    print('jPlus deactivated')

    return

def refreshCalls():
    """Methods called when the subroutine needs to be refreshed."""

    Model.updateYearModeled()
    
    return

def resetCalls():
    """Methods called to reset this subroutine."""

    Model.resetConfigFileItems()

    return
        
def specificCalls():
    """Methods called to run specific tasks."""

    return
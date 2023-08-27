# coding=utf-8
# © 2023 Greg Ritacco

"""
Throwback
"""

from opsEntities import PSE
from Subroutines.Throwback import GUI

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.TB.View')

class ManageGui:

    def __init__(self):

        pass

    def makeSubroutine(self):
        """
        Makes the complete subroutine.
        """       

        subroutine = GUI.subroutineGui()
        gui = subroutine.guiMaker()
        widgets = subroutine.guiWidgetGetter()
    
        return gui, widgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

# coding=utf-8
# © 2023 Greg Ritacco

"""
Patterns
"""

from opsEntities import PSE
from Subroutines_Activated.Patterns import GUI

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001


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

    print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

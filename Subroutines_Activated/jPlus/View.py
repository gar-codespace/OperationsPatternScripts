# coding=utf-8
# © 2023 Greg Ritacco

"""
jPlus
"""

from opsEntities import PSE
from Subroutines_Activated.jPlus import GUI

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901


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

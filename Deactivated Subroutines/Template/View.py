# coding=utf-8
# © 2023 Greg Ritacco

"""
Template
"""

from opsEntities import PSE
from Subroutines.Template import GUI

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.XX.View')

class ManageGui:

    def __init__(self):

        return

    def makeSubroutine(self):
        """
        Makes the complete subroutine.
        """

        subroutineFrame = PSE.JAVX_SWING.JPanel() 
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.getBundleItem('Template Subroutine'))

        subroutineGui = GUI.subroutineGui()
        gui = subroutineGui.guiMaker()

        subroutineFrame.add(gui)
        widgets = subroutineGui.guiWidgetGetter()
    
        return subroutineFrame, widgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

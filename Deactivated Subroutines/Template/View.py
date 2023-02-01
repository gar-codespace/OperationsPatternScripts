# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Template subroutine.
Replace XX with a designator for this subroutines' name.
"""

from opsEntities import PSE
from Subroutines.Template import ViewEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.XX.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('Template')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the template controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE['Template Subroutine'])

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the controls."""

        _psLog.debug('TemplateSubroutine.View.makeSubroutinePanel')

        templateSubroutinePanel = ViewEntities.templateSubroutinePanel()
        subroutinesPanel = templateSubroutinePanel.templatePanelMaker()
        subroutinePanelWidgets = templateSubroutinePanel.templateWidgetGetter()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

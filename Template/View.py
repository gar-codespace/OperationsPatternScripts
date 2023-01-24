# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Template
"""

from opsEntities import PSE
from TemplateSubroutine import ViewEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.XX.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('XX')
        # Add an XX section to the PatternConfig.json

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

        xxSubroutinePanel = ViewEntities.xxSubroutinePanel()
        subroutinesPanel = xxSubroutinePanel.xxPanelMaker()
        subroutinePanelWidgets = xxSubroutinePanel.xxWidgetGetter()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

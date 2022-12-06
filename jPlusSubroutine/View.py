# coding=utf-8
# © 2021, 2022 Greg Ritacco

""" """

from opsEntities import PSE
from jPlusSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.jPlusSubroutine.View'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.JP.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile()

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the jPlus controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(u'jPlusSubroutine')
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE[u'j Plus Subroutine'])

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the jPlus controls"""

        _psLog.debug('jPlusSubroutine.View.makeSubroutinePanel')

        jPlusSubroutinePanel = ViewEntities.jPlusSubroutinePanel()
        if self.configFile['CP']['o2oSubroutine']:
            subroutinesPanel = jPlusSubroutinePanel.jPlusPanelFixed()
        else:
            subroutinesPanel = jPlusSubroutinePanel.jPlusPanelEditable()

        subroutinePanelWidgets = jPlusSubroutinePanel.jPlusWidgets()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

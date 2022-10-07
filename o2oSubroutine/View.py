# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE
from o2oSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.View'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.o2o.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('o2o')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the o2o controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(u'o2oSubroutine')
        # encodedKey = unicode('o2o Subroutine', PSE.ENCODING)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(
            PSE.BUNDLE[u'o2o Subroutine']
            )

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the o2o controls"""

        _psLog.debug('makeSubroutinePanel')

        o2oSubroutinePanel = ViewEntities.O2oSubroutinePanel()
        subroutinesPanel = o2oSubroutinePanel.o2oPanelMaker()
        subroutinePanelWidgets = o2oSubroutinePanel.o2oWidgetGetter()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

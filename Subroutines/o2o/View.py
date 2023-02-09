# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE
from Subroutines.o2o import ViewEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.o2o.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('o2o')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the o2o controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE[u'o2o Subroutine'])

        return subroutineFrame

    def makeSubroutineGui(self):
        """Make the o2o GUI."""

        _psLog.debug('o2oSubroutine.View.makeSubroutineGui')

        o2oSubroutinePanel = ViewEntities.O2oSubroutinePanel()
        subroutinesPanel = o2oSubroutinePanel.o2oPanelMaker()
        subroutinePanelWidgets = o2oSubroutinePanel.o2oWidgetGetter()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

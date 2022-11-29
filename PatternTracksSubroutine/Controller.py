# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE
from PatternTracksSubroutine import Listeners
from PatternTracksSubroutine import View
from PatternTracksSubroutine import Model
from o2oSubroutine import Model as o2oModel

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.Controller'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.PT.Controller')


def updateSubroutine(parent):
    """Allows other subroutines to update and restart the PT Subroutine.
        Used by:
    def newJmriRailroad(self, EVENT):
        o2oController.StartUp.newJmriRailroad
        """

    if not parent:
        return

    Model.resetPatternLocation()

    for component in parent.getComponents():
        if component.getName() == 'PatternTracksSubroutine':
            restartSubroutine(component.getComponents()[0])

    return

def restartSubroutine(subroutineFrame):
    """Subroutine restarter.
        Used by:
        opsEntities.Listeners.GenericComboBox.actionPerformed
        updateSubroutine
        """

    subroutinePanel = StartUp(subroutineFrame).makeSubroutinePanel()
    subroutineFrame.removeAll()
    subroutineFrame.add(subroutinePanel)
    subroutineFrame.revalidate()

    return

def setDropDownText():
    """Pattern Scripts/Tools/itemMethod - Set the drop down text per the config file PatternTracksSubroutine Include flag ['CP']['IT']"""

    patternConfig = PSE.readConfigFile('CP')
    if patternConfig['PatternTracksSubroutine']:
        menuText = PSE.BUNDLE[u'Disable Track Pattern subroutine']
    else:
        menuText = PSE.BUNDLE[u'Enable Track Pattern subroutine']

    return menuText, 'tpItemSelected'


class StartUp:
    """Start the pattern tracks subroutine"""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        _psLog.info('pattern tracks makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame
            Change this to call widgets by name
            """

        Model.updateLocations()

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        _psLog.info('pattern tracks panel completed')

        return self.subroutinePanel

    def activateWidgets(self):

        self.widgets[0].addActionListener(Listeners.GenericComboBox(self.subroutineFrame))
        self.widgets[1].addActionListener(Listeners.GenericComboBox(self.subroutineFrame))
        # self.widgets[1].addActionListener(Listeners.LocationComboBox(self.subroutineFrame))
        self.widgets[2].actionPerformed = self.yardTrackOnlyCheckBox
        self.widgets[5].actionPerformed = self.trackPatternButton
        self.widgets[6].actionPerformed = self.setRsButton

        return

    def yardTrackOnlyCheckBox(self, EVENT):

        if self.widgets[2].selected:
            allTracksAtLoc = PSE.getTracksNamesByLocation('Yard')
        else:
            allTracksAtLoc = PSE.getTracksNamesByLocation(None)

        configFile = PSE.readConfigFile()
        trackDict = Model.updatePatternTracks(allTracksAtLoc)
        configFile['PT'].update({'PT': trackDict})
        configFile['PT'].update({'PA': self.widgets[2].selected})
        configFile['PT'].update({'PI': self.widgets[3].selected})
        PSE.writeConfigFile(configFile)

        subroutinePanel = StartUp(self.subroutineFrame).makeSubroutinePanel()
        self.subroutineFrame.removeAll()
        self.subroutineFrame.add(subroutinePanel)
        self.subroutineFrame.revalidate()

        return

    def trackPatternButton(self, EVENT):
        """Makes a pattern tracks report based on the config file (PR)"""

        _psLog.debug('trackPatternButton')

        Model.updateConfigFile(self.widgets)

        if not Model.verifySelectedTracks():
            _psLog.warning('Track not found, re-select the location')
            return

        if not PSE.getSelectedTracks():
            _psLog.warning('No tracks were selected for the pattern button')
            return

        PSE.REPORT_ITEM_WIDTH_MATRIX = PSE.makeReportItemWidthMatrix()

        Model.trackPatternButton()
        View.trackPatternButton()

        if PSE.JMRI.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled():
            View.trackPatternAsCsv()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def setRsButton(self, EVENT):
        """Opens a "Pattern Report for Track X" window for each checked track
            Resets the o2o switchlist with a new header
            """

        _psLog.debug('setRsButton')

        Model.updateConfigFile(self.widgets)

        if not Model.verifySelectedTracks():
            _psLog.warning('Track not found, re-select the location')
            return

        o2oModel.o2oWorkEventReset()

        PSE.REPORT_ITEM_WIDTH_MATRIX = PSE.makeReportItemWidthMatrix()

        View.setRsButton()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

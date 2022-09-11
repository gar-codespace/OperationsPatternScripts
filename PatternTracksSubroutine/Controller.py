# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import View
from PatternTracksSubroutine import Model
from PatternTracksSubroutine import ModelEntities
from o2oSubroutine import ModelWorkEvents

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.Controller'
SCRIPT_REV = 20220101

class LocationComboBox(PatternScriptEntities.JAVA_AWT.event.ActionListener):
    """Event triggered from location combobox selection"""

    def __init__(self, subroutineFrame):

        self.subroutineFrame = subroutineFrame

        return

    def actionPerformed(self, EVENT):

        Model.updatePatternLocation(EVENT.getSource().getSelectedItem())
        subroutinePanel = StartUp(self.subroutineFrame).makeSubroutinePanel()
        self.subroutineFrame.removeAll()
        self.subroutineFrame.add(subroutinePanel)
        self.subroutineFrame.revalidate()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

class StartUp:
    """Start the pattern tracks subroutine"""

    def __init__(self, subroutineFrame=None):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.Controller')
        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        self.psLog.info('pattern tracks makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame"""

        if not PatternScriptEntities.readConfigFile('PT')['AL']:
            Model.updateLocations()

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def activateWidgets(self):

        self.widgets[0].addActionListener(LocationComboBox(self.subroutineFrame))
        self.widgets[1].actionPerformed = self.yardTrackOnlyCheckBox
        self.widgets[4].actionPerformed = self.trackPatternButton
        self.widgets[5].actionPerformed = self.setRsButton

        return

    def yardTrackOnlyCheckBox(self, EVENT):

        if (self.widgets[1].selected):
            # trackList = Model.makeTrackList(self.widgets[0].getSelectedItem(), 'Yard')
            trackList = PatternScriptEntities.getTracksByLocation('Yard')
        else:
            # trackList = Model.makeTrackList(self.widgets[0].getSelectedItem(), None)
            trackList = PatternScriptEntities.getTracksByLocation(None)

        configFile = PatternScriptEntities.readConfigFile()
        trackDict = Model.updatePatternTracks(trackList)
        configFile['PT'].update({'PT': trackDict})
        configFile['PT'].update({'PA': self.widgets[1].selected})
        configFile['PT'].update({'PI': self.widgets[2].selected})
        PatternScriptEntities.writeConfigFile(configFile)

        subroutinePanel = StartUp(self.subroutineFrame).makeSubroutinePanel()
        self.subroutineFrame.removeAll()
        self.subroutineFrame.add(subroutinePanel)
        self.subroutineFrame.revalidate()

        return

    def trackPatternButton(self, EVENT):
        """Makes a pattern tracks report based on the config file (PR)"""

        self.psLog.debug('Controller.trackPatternButton')

        Model.updateConfigFile(self.widgets)

        if not Model.verifySelectedTracks():
            self.psLog.warning('Track not found, re-select the location')
            return

        if not PatternScriptEntities.getSelectedTracks():
            self.psLog.warning('No tracks were selected for the pattern button')
            return

        PatternScriptEntities.REPORT_ITEM_WIDTH_MATRIX = PatternScriptEntities.makeReportItemWidthMatrix()

        Model.trackPatternButton()
        View.trackPatternButton()

        if PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled():
            workEventName = PatternScriptEntities.BUNDLE['Track Pattern Report']
            Model.writeTrackPatternCsv(workEventName)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def setRsButton(self, EVENT):
        """Opens a "Pattern Report for Track X" window for each checked track
            Resets the o2o switchlist with a new header
            """

        self.psLog.debug('Controller.setRsButton')

        Model.updateConfigFile(self.widgets)

        if not Model.verifySelectedTracks():
            self.psLog.warning('Track not found, re-select the location')
            return

        PatternScriptEntities.REPORT_ITEM_WIDTH_MATRIX = PatternScriptEntities.makeReportItemWidthMatrix()

        View.setRsButton()
    # Reset the o2o switchlist
        newHeader = ModelEntities.makeGenericHeader()
        PatternScriptEntities.writeWorkEvents(newHeader)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

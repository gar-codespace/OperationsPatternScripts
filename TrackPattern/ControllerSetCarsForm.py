# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import java.awt
import logging
# from os import system as osSystem

from psEntities import MainScriptEntities
from TrackPattern import Model
from TrackPattern import ModelSetCarsForm
from TrackPattern import ViewSetCarsForm

'''Makes a "Pattern Report for Track X" form for each selected track'''

scriptName = 'OperationsPatternScripts.ControllerSetCarsForm'
scriptRev = 20220101

class TextBoxEntryListener(java.awt.event.MouseAdapter):
    '''When any of the "Pattern Report for Track X" text boxes is clicked on'''

    def __init__(self):
        self.psLog = logging.getLogger('PS.TP.TextBoxEntryListener')

    def mouseClicked(self, MOUSE_CLICKED):

        if (MainScriptEntities._trackNameClickedOn):
            MOUSE_CLICKED.getSource().setText(MainScriptEntities._trackNameClickedOn)
        else:
            self.psLog.warning('No track was selected')

        return

class CreatePatternReportGui():
    '''Creates an instance of each "Pattern Report for Track X" window'''

    def __init__(self, setCarsForm):

        self.psLog = logging.getLogger('PS.TP.CreatePatternReportGui')

        self.setCarsForm = setCarsForm
        self.locationName = setCarsForm['locations'][0]['locationName']
        self.trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
        self.buttonDict = {}

        return

    def makeFrame(self):
        '''Create a JMRI jFrame window'''

        self.patternReportForTrackForm, self.buttonDict = ViewSetCarsForm.makePatternReportForTrackForm(self.setCarsForm)
        patternReportForTrackWindow = ViewSetCarsForm.patternReportForTrackWindow(self.patternReportForTrackForm)
        self.activateButtons()

        return patternReportForTrackWindow

    def activateButtons(self):

        for track in self.buttonDict['trackButtons']:
            track.actionPerformed = self.trackRowButton

        for inputText in self.buttonDict['textBoxEntry']:
            inputText.addMouseListener(TextBoxEntryListener())

        for schedule in self.buttonDict['scheduleButton']:
            if schedule:
                schedule.actionPerformed = self.scheduleButton

        self.buttonDict['footerButtons'][0].actionPerformed = self.printButton
        self.buttonDict['footerButtons'][1].actionPerformed = self.setButton
        try:
            self.buttonDict['footerButtons'][2].actionPerformed = self.trainPlayerButton
        except IndexError:
            pass

        return

    def quickCheck(self):

        if not ModelSetCarsForm.testValidityOfForm(self.setCarsForm, self.buttonDict['textBoxEntry']):
            self.psLog.critical('FAIL - ModelSetCarsForm.testValidityOfForm')
            return False
        else:
            self.psLog.info('PASS - ModelSetCarsForm.testValidityOfForm')
            return True

    def trackRowButton(self, MOUSE_CLICKED):
        '''Any of the "Pattern Report for Track X" - row of track buttons'''

        MainScriptEntities._trackNameClickedOn = unicode(MOUSE_CLICKED.getSource().getText(), MainScriptEntities.setEncoding())

        return

    def scheduleButton(self, MOUSE_CLICKED):
        '''The named schedule button if displayed on any "Pattern Report for Track X" window'''

        scheduleName = MOUSE_CLICKED.getSource().getText()
        schedule = MainScriptEntities._sm.getScheduleByName(scheduleName)
        track = MainScriptEntities._lm.getLocationByName(self.locationName).getTrackByName(self.trackName, None)
        jmri.jmrit.operations.locations.schedules.ScheduleEditFrame(schedule, track)

        print(scriptName + ' ' + str(scriptRev))

        return

    def printButton(self, MOUSE_CLICKED):
        '''Makes a Set Cars (SC) switch list for the active "Pattern Report for Track X" window'''

        if not self.quickCheck():
            return

        locationDict = ModelSetCarsForm.makeLocationDict(self.setCarsForm, self.buttonDict['textBoxEntry'])
        modifiedReport = Model.modifyReport(locationDict, 'SC')
        Model.printWorkEventList(modifiedReport, trackTotals=False)

        print(scriptName + ' ' + str(scriptRev))

        return

    def setButton(self, MOUSE_CLICKED):
        '''Event that moves cars to the tracks entered in the text box of the "Pattern Report for Track X" form'''

        if not self.quickCheck():
            return

        ModelSetCarsForm.setCarsToTrack(self.setCarsForm, self.buttonDict['textBoxEntry'])

        setCarsWindow = MOUSE_CLICKED.getSource().getTopLevelAncestor()
        setCarsWindow.setVisible(False)
        setCarsWindow.dispose()

        print(scriptName + ' ' + str(scriptRev))

        return

    def trainPlayerButton(self, MOUSE_CLICKED):
        '''Accumulate switch lists into one TrainPlayer switch list'''

        if not self.quickCheck():
            return

        MOUSE_CLICKED.getSource().setBackground(java.awt.Color.GREEN)

        ModelSetCarsForm.exportToTrainPlayer(self.setCarsForm, self.buttonDict['textBoxEntry'])

        print(scriptName + ' ' + str(scriptRev))

        return

# class AnyButtonPressedListener(java.awt.event.ActionListener):
#
#     def __init__(self, object1=None, object2=None):
#
#         self.psLog = logging.getLogger('PS.TP.AnyButtonPressedListener')
#     # scheduleButton
#         self.locationName = object1
#         self.trackName = object2
#     # printButton, setButton, TrainPlayerButton
#         self.setCarsForm = object1
#         self.textBoxEntry = object2
#
#         return
#
#     def trackRowButton(self, MOUSE_CLICKED):
#         '''Any of the "Pattern Report for Track X" - row of track buttons'''
#
#         MainScriptEntities._trackNameClickedOn = unicode(MOUSE_CLICKED.getSource().getText(), MainScriptEntities.setEncoding())
#
#         return

    # def scheduleButton(self, MOUSE_CLICKED):
    #     '''The named schedule button if displayed on any "Pattern Report for Track X" window'''
    #
    #     scheduleName = MOUSE_CLICKED.getSource().getText()
    #     schedule = MainScriptEntities._sm.getScheduleByName(scheduleName)
    #     track = MainScriptEntities._lm.getLocationByName(self.locationName).getTrackByName(self.trackName, None)
    #     jmri.jmrit.operations.locations.schedules.ScheduleEditFrame(schedule, track)
    #
    #     return

    # def printButton(self, MOUSE_CLICKED):
    #     '''Makes a Set Cars (SC) switch list for the active "Pattern Report for Track X" window'''
    #
    #     if not ModelSetCarsForm.testValidityOfForm(self.setCarsForm, self.textBoxEntry):
    #         self.psLog.critical('Could not create switch list')
    #         return
    #
    #     locationDict = ModelSetCarsForm.makeLocationDict(self.setCarsForm, self.textBoxEntry)
    #     modifiedReport = Model.modifyReport(locationDict, 'SC')
    #     Model.printWorkEventList(modifiedReport, trackTotals=False)
    #
    #     print(scriptName + ' ' + str(scriptRev))
    #
    #     return
    #
    # def setButton(self, MOUSE_CLICKED):
    #     '''Event that moves cars to the tracks entered in the text box of the "Pattern Report for Track X" form'''
    #
    #     if not ModelSetCarsForm.testValidityOfForm(self.setCarsForm, self.textBoxEntry):
    #         self.psLog.critical('Could not set cars to track')
    #         return
    #
    #     ModelSetCarsForm.setCarsToTrack(self.setCarsForm, self.textBoxEntry)
    #
    #     setCarsWindow = MOUSE_CLICKED.getSource().getTopLevelAncestor()
    #     setCarsWindow.setVisible(False)
    #     setCarsWindow.dispose()
    #
    #     print(scriptName + ' ' + str(scriptRev))
    #
    #     return
    #
    # def trainPlayerButton(self, MOUSE_CLICKED):
    #     '''Accumulate switch lists into one TrainPlayer switch list'''
    #
    #     if not ModelSetCarsForm.testValidityOfForm(self.setCarsForm, self.textBoxEntry):
    #         self.psLog.critical('Could not set cars to track')
    #         return
    #
    #     MOUSE_CLICKED.getSource().setBackground(java.awt.Color.GREEN)
    #
    #     ModelSetCarsForm.exportToTrainPlayer(self.setCarsForm, self.textBoxEntry)
    #
    #     print(scriptName + ' ' + str(scriptRev))
    #
    #     return

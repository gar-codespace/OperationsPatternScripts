# coding=utf-8
# © 2021 Greg Ritacco

import jmri
import java.awt
# import javax.swing
import logging
from os import system as osSystem

import psEntities.MainScriptEntities
import TrackPattern.Model
import TrackPattern.View
# import TrackPattern.ModelEntities
import TrackPattern.ModelSetCarsForm
import TrackPattern.ViewSetCarsForm
import TrackPattern.ExportToTrainPlayer

'''Makes a "Pattern Report for Track X" form for each selected track'''

scriptName = 'OperationsPatternScripts.TrackPattern.ControllerSetCarsForm'
scriptRev = 20220101

class AnyButtonPressedListener(java.awt.event.ActionListener):

    def __init__(self, object1=None, object2=None):

        self.psLog = logging.getLogger('PS.TP.AnyButtonPressedListener')
        self.sm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.schedules.ScheduleManager)
    # scheduleButton
        self.trackObject = object1
    # printButton, setButton, TrainPlayerButton
        self.trackData = object1
        self.textBoxEntry = object2

        return

    def trackRowButton(self, MOUSE_CLICKED):
        '''Any of the "Pattern Report for Track X" - row of track buttons'''

        TrackPattern._trackNameClickedOn = unicode(MOUSE_CLICKED.getSource().getText(), psEntities.MainScriptEntities.setEncoding())

        return

    def scheduleButton(self, MOUSE_CLICKED):
        '''The named schedule button if displayed on any "Pattern Report for Track X" window'''

        scheduleName = MOUSE_CLICKED.getSource().getText()
        scheduleObject = self.sm.getScheduleByName(scheduleName)
        jmri.jmrit.operations.locations.schedules.ScheduleEditFrame(scheduleObject, self.trackObject)

        return

    def printButton(self, MOUSE_CLICKED):
        '''Print a switch list for each "Pattern Report for Track X" window'''

        if TrackPattern.ModelSetCarsForm.testFormValidity(self.trackData, self.textBoxEntry):
            testSwitchListBody = TrackPattern.ModelSetCarsForm.makeSetCarsSwitchList(self.trackData, self.textBoxEntry)
            switchListBody = TrackPattern.ModelSetCarsForm.modifySwitchListForPrint(testSwitchListBody)
            switchList = TrackPattern.Model.makeSwitchListHeader()
            switchList['tracks'] = [switchListBody]
            # switchListBody has to be added as a one element list to be compatable with TrackPattern.Model.makeTextSwitchListBody(switchListname)
            trackName = switchList['tracks'][0]['Name']
            reportTitle = psEntities.MainScriptEntities.readConfigFile('TP')['RT']['SC']
            switchList['description'] = reportTitle + ' ' + unicode(trackName, psEntities.MainScriptEntities.setEncoding())
            switchListname = TrackPattern.Model.writeSwitchlistAsJson(switchList)
            textSwitchListHeader = TrackPattern.Model.makeTextSwitchListHeader(switchListname)
            textSwitchListBody = TrackPattern.Model.makeTextSwitchListBody(switchListname)
            textSwitchList = textSwitchListHeader + textSwitchListBody
            TrackPattern.Model.writeTextSwitchList(textSwitchList)
            TrackPattern.View.displayTextSwitchList(textSwitchList)
        else:
            self.psLog.critical('Could not create switch list')

        print(scriptName + ' ' + str(scriptRev))

        return

    def setButton(self, MOUSE_CLICKED):
        '''Event that moves cars to the tracks entered in the text box of the "Pattern Report for Track X" form'''

        if TrackPattern.ModelSetCarsForm.testFormValidity(self.trackData, self.textBoxEntry):
            TrackPattern.ModelSetCarsForm.setCarsToTrack(self.trackData, self.textBoxEntry)
        else:
            self.psLog.critical('Could not set cars to track')

        setCarsWindow = MOUSE_CLICKED.getSource().getTopLevelAncestor()
        setCarsWindow.setVisible(False)
        setCarsWindow.dispose()
        print(scriptName + ' ' + str(scriptRev))

        return

    def trainPlayerButton(self, MOUSE_CLICKED):
        '''Accumulate switch lists into one TrainPlayer switch list'''

        MOUSE_CLICKED.getSource().setBackground(java.awt.Color.GREEN)
        try:
            body = TrackPattern.ModelSetCarsForm.makeSetCarsSwitchList(self.trackData, self.textBoxEntry)
        except:
            self.psLog.critical('Could not create switch list')
            return
        tpBody = TrackPattern.ExportToTrainPlayer.JmriTranslationToTp(body).modifyJmriSwitchListForTp()
        appendedTpSwitchList = TrackPattern.ExportToTrainPlayer.JmriTranslationToTp(tpBody).appendSwitchListForTp()
        # TrackPattern.ModelSetCarsForm.writeTpSwitchListFromJson(switchListName)

        print(scriptName + ' ' + str(scriptRev))

        return

class TextBoxEntryListener(java.awt.event.MouseAdapter):
    '''When any of the "Pattern Report for Track X" text boxes is clicked on'''

    def __init__(self):
        self.psLog = logging.getLogger('PS.TP.TextBoxEntryListener')

    def mouseClicked(self, MOUSE_CLICKED):

        if (TrackPattern._trackNameClickedOn):
            MOUSE_CLICKED.getSource().setText(TrackPattern._trackNameClickedOn)
        else:
            self.psLog.warning('No track was selected')

        return

class CreatePatternReportGui():
    '''Creates an instance of each "Pattern Report for Track X" window'''

    def __init__(self, header, body):

        self.header = header
        self.body = body

        return

    def makeFrame(self):
        '''Create the windows'''

        patternReportForTrackForm = TrackPattern.ViewSetCarsForm.patternReportForTrackForm(self.header, self.body)
        patternReportForTrackWindow = TrackPattern.ViewSetCarsForm.patternReportForTrackWindow(patternReportForTrackForm)

        return patternReportForTrackWindow

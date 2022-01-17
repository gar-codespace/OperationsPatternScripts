# coding=utf-8
# Extended ìÄÅÉî
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
import javax.swing
import logging
# from codecs import open as cOpen
from os import system
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern')
import TrackPattern.ModelSetCarsForm
import TrackPattern.ViewSetCarsForm
import MainScriptEntities

'''Makes a set cars form for each selected track'''

scriptRev = 'TrackPattern.ViewSetCarsForm v20211210'

class AnyButtonPressedListener(java.awt.event.ActionListener):

    def __init__(self, object1=None, object2=None, object3=None):

        self.psLog = logging.getLogger('PS.TP.AnyButtonPressedListener')
    # scheduleButton
        self.scheduleObject = object1
        self.trackObject = object2
    # printPrButton, setPrButton
        self.trackData = object1
        self.textBoxEntry = object2

        return

    def trackRowButton(self, MOUSE_CLICKED):
        '''Any of the "Pattern Report for Track X" - row of track buttons'''

        MainScriptEntities._trackNameClickedOn = unicode(MOUSE_CLICKED.getSource().getText(), MainScriptEntities.setEncoding())

        return

    def scheduleButton(self, MOUSE_CLICKED):
        '''The named schedule button if displayed on any set cars window'''

        jmri.jmrit.operations.locations.schedules.ScheduleEditFrame(self.scheduleObject, self.trackObject)

        return

    def printPrButton(self, MOUSE_CLICK):
        '''Event that prints the yard pattern for the selected track'''

    # Make the switch list
        processedTrackData = TrackPattern.ModelSetCarsForm.processYpForPrint(self.trackData, self.textBoxEntry)
    # write the switch list
        switchListLocation = TrackPattern.ModelSetCarsForm.writeSwitchList(processedTrackData)
    # Print the switch list
        system(MainScriptEntities.systemInfo(switchListLocation))

        print(scriptRev)

        return

    def setPrButton(self, MOUSE_CLICK):
        '''Event that moves cars to the tracks entered in the text box of the "Pattern Report for Track X" form'''

    # set the cars to a track
        TrackPattern.ModelSetCarsForm.setCarsToTrack(self.trackData, self.textBoxEntry)
    # Wrap it up
        self.setCarsWindow = MOUSE_CLICK.getSource().getParent().getTopLevelAncestor()
        self.setCarsWindow.setVisible(False)
        self.setCarsWindow.dispose()
        print(scriptRev)

        return

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

    def __init__(self, pattern):

        self.trackPattern = pattern # all the data for the selected track, car roster is sorted

        return

    def makeFrame(self):
        '''Create the windows'''

        patternReportForTrackForm = TrackPattern.ViewSetCarsForm.patternReportForTrackForm(self.trackPattern)
        patternReportForTrackWindow = TrackPattern.ViewSetCarsForm.patternReportForTrackWindow(patternReportForTrackForm)


        return patternReportForTrackWindow

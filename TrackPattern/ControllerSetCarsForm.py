# coding=utf-8
# Extended ìÄÅÉî
# Makes a set cars form for each selected track
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
# import java.awt.event
import javax.swing
import logging
from codecs import open as cOpen
from os import system
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern')
import TrackPattern.ModelSetCarsForm
import TrackPattern.ViewSetCarsForm
import MainScriptEntities

class AnyButtonPressedListener(java.awt.event.ActionListener):

    scriptRev = 'TrackPattern.ViewSetCarsForm v20211210'

    def __init__(self, object1=None, object2=None, object3=None, object4=None):

        self.psLog = logging.getLogger('PS.TP.AnyButtonPressedListener')
        self.scheduleObject = object1
        self.trackData = object1
        self.trackObject = object2
        self.textBoxEntry = object3
        self.setCarsWindow = object4

        return

    def trackRowButton(self, MOUSE_CLICKED):
        '''Any of the track buttons on the set cars window - row of track buttons'''

        MainScriptEntities.trackNameClickedOn = unicode(MOUSE_CLICKED.getSource().getText(), MainScriptEntities.setEncoding())

        return

    def scheduleButton(self, MOUSE_CLICKED):
        '''The named schedule button if displayed on any set cars window'''

        jmri.jmrit.operations.locations.schedules.ScheduleEditFrame(self.scheduleObject, self.trackObject)

        return

    def printPrButton(self, MOUSE_CLICK):
        '''Event that prints the yard pattern for the selected track'''

    # Make the switch list
        processedTrackData = TrackPattern.ModelSetCarsForm.processYpForPrint(self.trackData, self.textBoxEntry)
    # Print the switch list
        TrackPattern.ModelEntities.printSwitchList(processedTrackData)
        print(AnyButtonPressedListener.scriptRev)

        return

    def setPrButton(self, MOUSE_CLICK):
        '''Event that moves cars to the tracks entered in the pattern window'''

    # set the cars to a track
        TrackPattern.ModelSetCarsForm.setCarsToTrack(self.trackData, self.textBoxEntry)
    # Wrap it up
        self.setCarsWindow.setVisible(False)
        print(AnyButtonPressedListener.scriptRev)

        return

class textBoxEntryListener(java.awt.event.MouseAdapter):
    '''When any of the Set Cars to Track text boxes is clicked on'''

    def __init__(self):
        self.psLog = logging.getLogger('PS.TP.textBoxEntryListener')

    def mouseClicked(self, MOUSE_CLICKED):

        if (MainScriptEntities.trackNameClickedOn):
            MOUSE_CLICKED.getSource().setText(MainScriptEntities.trackNameClickedOn)
        else:
            self.psLog.warning('No track was selected')

        return

class ManageGui():
    '''Manages an instance of each -Pattern Report for track- window'''

    def __init__(self, pattern):

        self.trackPattern = pattern # all the data for the selected track, car roster is sorted

        return

    def makeFrame(self, offSet):
        '''Creates each of the Pattern Report for Track windows'''

        patternReportForTrackWindow = TrackPattern.ViewSetCarsForm.patternReportForTrackWindow(self.trackPattern, offSet)
        patternReportForTrackWindow.pack()
        patternReportForTrackWindow.setVisible(True)


        return

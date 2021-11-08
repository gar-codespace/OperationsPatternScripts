# coding=utf-8
# Extended ìÄÅÉî
# Data munipulation for the track pattern subroutine
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import logging
from os import path as oPath
from shutil import copy as sCopy
from json import loads as jLoads, dumps as jDumps
from codecs import open as cOpen
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import TrackPattern.View
import TrackPattern.Controller
import TrackPattern.ModelEntities

def validateUserInput(controls):
    '''Validates the user submitted location, and returns a track list for a valid location'''

    location = unicode(controls[0].text, MainScriptEntities.setEncoding())
    allFlag = controls[1].selected
    useAll = None
    if (allFlag == True):
        useAll = 'Yard'
    validBool = TrackPattern.ModelEntities.checkYard(location, useAll)
    focusOn = MainScriptEntities.readConfigFile('TP')
    focusOn.update({"PL": ''})
    focusOn.update({"PA": allFlag})
    trackList = {}
    if (validBool):
        locationTracks = TrackPattern.ModelEntities.getTracksByLocation(location, useAll)
        focusOn.update({"PL": location})
        for track in locationTracks:
            trackList[track] = True
    focusOn.update({"PT": trackList})

    return focusOn

def getAllTracks(trackCheckBoxes):
    '''Returns a dictionary of track names and their check box status'''

    dict = {}
    for item in trackCheckBoxes:
        dict[unicode(item.text, MainScriptEntities.setEncoding())] = item.selected

    return dict

def updateTrackList(trackList):
    '''Updates the config file with current track check box status'''

    # configFile = MainScriptEntities.readConfigFile()
    focusOn = MainScriptEntities.readConfigFile('TP')
    focusOn.update({'PT': trackList})
    # configFile.update({"TP": focusOn})

    return focusOn

def makeTrackPatternDict(trackList):
    '''Make a track pattern as a dictionary'''

    trackPattern = MainScriptEntities.readConfigFile('TP')

    return TrackPattern.ModelEntities.makeYardPattern(trackList, trackPattern['PL'])

def getSelectedTracks():
    '''Makes a list of just the selected tracks'''

    trackPattern = MainScriptEntities.readConfigFile('TP')
    trackList = []
    for track, bool in trackPattern['PT'].items():
        if (bool):
            trackList.append(track)

    return trackList

def writePatternJson(location, trackPatternDict):
    '''Write the track pattern dictionary as a JSON file'''

    jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\Track Pattern (' + location + ').json'
    jsonObject = jDumps(trackPatternDict, indent=2, sort_keys=True) #trackPatternDict
    with cOpen(jsonCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
        jsonWorkFile.write(jsonObject)

    return jsonObject

def writeTextSwitchList(location, trackPatternDict):
    '''Write the track pattern dictionary as a text switch list'''

    textCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\Track Pattern (' + location + ').txt'
    textObject = TrackPattern.ModelEntities.makeSwitchlist(trackPatternDict, True)
    with cOpen(textCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as textWorkFile:
        textWorkFile.write(textObject)

    return textObject

def writeCsvSwitchList(location, trackPatternDict):
    '''Write the track pattern dictionary as a CSV switch list'''

    csvSwitchlistPath = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists'
    if not (oPath.isdir(csvSwitchlistPath)):
        mkdir(csvSwitchlistPath)
    csvCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists\\Track Pattern (' + location + ').csv'
    csvObject = TrackPattern.ModelEntities.makeCsvSwitchlist(trackPatternDict)
    with cOpen(csvCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as csvWorkFile:
        csvWorkFile.write(csvObject)

    return

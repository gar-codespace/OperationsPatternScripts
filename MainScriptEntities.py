# coding=utf-8
# Extended ìÄÅÉî
# support methods for the main script
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
import javax.swing
import time
from json import loads as jLoads, dumps as jDumps
from codecs import open as cOpen
from os import path as oPath
from shutil import copy as sCopy

def validateConfigFile():
    '''Checks for a config file and adds one if missing'''

    copyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
    if not (oPath.exists(copyTo)):
        copyFrom = jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts\\PatternConfig.json'
        sCopy(copyFrom, copyTo)
        result = u'Configuration file created'
    else:
        result = u'Configuration file found'
    return result

def readConfigFile(subConfig='all'):
    '''Read in the PatternConfig.json for a profile and return it as a dictionary
    This needs error handling built into it'''

    configFileLoc = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
    with cOpen(configFileLoc, 'r', encoding=setEncoding()) as configWorkFile:
        configFile = jLoads(configWorkFile.read())
    if (subConfig == 'all'):
        return configFile
    else:
        return configFile[subConfig]

def updateConfigFile(configFile):
    '''Updates the PatternConfig.json file'''

    jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
    jsonObject = jDumps(configFile, indent=2, sort_keys=True)
    with cOpen(jsonCopyTo, 'wb', encoding=setEncoding()) as jsonWorkFile:
        jsonWorkFile.write(jsonObject)
    return 'Configuration file updated'

def setEncoding():
    '''Expand on this later'''

    return 'utf-8' #ascii, utf-16

def makeControlPanel():
    '''Create the control panel, with a scroll bar, that all sub panels go into
    This holds trackPatternPanel and future panels'''

    configFile = readConfigFile('ControlPanel')
    controlPanel = javax.swing.JPanel() # The whole panel that everything goes into
    scrollPanel = javax.swing.JScrollPane(controlPanel) # and that goes into a scroll pane
    scrollPanel.border = javax.swing.BorderFactory.createLineBorder(java.awt.Color.GRAY)
    scrollPanel.setPreferredSize(java.awt.Dimension(configFile['PW'], configFile['PH']))
    scrollPanel.setMaximumSize(scrollPanel.getPreferredSize())
    return controlPanel, scrollPanel

def timeStamp():
    '''Valid Time, get local time adjusted for time zone and dst'''

    epochTime = time.time()
    if time.localtime(epochTime).tm_isdst and time.daylight: # If local dst and dst are both 1
        timeOffset = time.altzone
    else:
        timeOffset = time.timezone # in seconds
    return time.strftime('%a %b %d %Y %I:%M %p %Z', time.gmtime(epochTime - timeOffset))

def systemInfo():
    '''Which computer type is this script run on'''

    osName = jmri.util.SystemType.getType()
    textEdit = {
        1: 'Mac Classic ',
        2: 'open -t ', # OSX
        4: 'start notepad.exe ', # Windows
        5: 'nano ', # Linux
        6: 'OS2 ',
        7: 'Unix ', # Unix
        }
    return textEdit[osName]

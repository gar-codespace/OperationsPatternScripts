# coding=utf-8
# Extended ìÄÅÉî
# support methods for the main script
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
# import java.awt.event
import javax.swing
import logging
import time
from json import loads as jLoads, dumps as jDumps
from codecs import open as cOpen
from os import path as oPath
from shutil import copy as sCopy

scriptRev = 'OperationsPatternScripts.MainScriptEntities v20211210'

# 'global' variables passed between modules
trackNameClickedOn = None
carTypeByEmptyDict = {}
defaultLoadEmpty = u''

def setEncoding():
    '''Expand on this later'''

    return 'utf-8' #ascii, utf-16

def setLoggingLevel(loggerObject):

    configLogLevel = readConfigFile('LL')
    logLevel = configLogLevel[str(jmri.jmrit.operations.setup.Setup.getBuildReportLevel())]
    loggerObject.parent.setLevel(logLevel)

    return

def timeStamp():
    '''Valid Time, get local time adjusted for time zone and dst'''

    epochTime = time.time()
    if time.localtime(epochTime).tm_isdst and time.daylight: # If local dst and dst are both 1
        timeOffset = time.altzone
    else:
        timeOffset = time.timezone # in seconds

    return time.strftime('%a %b %d %Y %I:%M %p %Z', time.gmtime(epochTime - timeOffset))

def systemInfo():
    '''Which type of computer is being used'''

    osName = jmri.util.SystemType.getType()
    textEdit = {
        1: 'Mac Classic ',
        2: 'open -a TextEdit ', # OSX
        4: 'start notepad.exe ', # Windows
        5: 'gedit ', # Linux
        6: 'OS2 ',
        7: 'kwrite ', # Unix
        }

    return textEdit[osName]

def validateConfigFile():
    '''Checks for a config file and adds one if missing'''

    try:
        configFileLoc = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
        with cOpen(configFileLoc, 'r', encoding=setEncoding()) as configWorkFile:
            configFile = jLoads(configWorkFile.read())
        return True
    except:
        return False

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

def writeConfigFile(configFile):
    '''Updates the PatternConfig.json file'''

    jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
    jsonObject = jDumps(configFile, indent=2, sort_keys=True)
    with cOpen(jsonCopyTo, 'wb', encoding=setEncoding()) as jsonWorkFile:
        jsonWorkFile.write(jsonObject)

    return 'Configuration file updated'

def writeNewConfigFile():
    '''Copies the default config file to the profile location'''

    copyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
    copyFrom = jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts\\PatternConfig.json'
    sCopy(copyFrom, copyTo)

    return 'New PatternConfig.json file for this profile created'

def makeControlPanel():
    '''Create the control panel, with a scroll bar, that all subroutines go into
    This holds trackPatternPanel and future panels'''

    configFile = readConfigFile('CP')
    controlPanel = javax.swing.JPanel() # The whole panel that everything goes into
    scrollPanel = javax.swing.JScrollPane(controlPanel) # and that goes into a scroll pane
    scrollPanel.border = javax.swing.BorderFactory.createLineBorder(java.awt.Color.GRAY)
    scrollPanel.setPreferredSize(java.awt.Dimension(configFile['PW'], configFile['PH']))
    scrollPanel.setMaximumSize(scrollPanel.getPreferredSize())

    return controlPanel, scrollPanel

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

def readConfigFile(subConfig):
    '''Read in the tpConfig.json for a profile and return it as a dictionary'''

    configFileLoc = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
    with cOpen(configFileLoc, 'r', encoding=setEncoding()) as configWorkFile:
        configFile = configWorkFile.read()
        configFile = jLoads(configFile)
    if (subConfig == 'all'):
        return configFile
    else:
        return configFile[subConfig]

def updateConfigFile(configFile):
    '''Updates the tpConfig.json file'''

    jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
    jsonObject = jDumps(configFile, indent=2, sort_keys=True)
    with cOpen(jsonCopyTo, 'wb', encoding=setEncoding()) as jsonWorkFile:
        jsonWorkFile.write(jsonObject)
    return 'Configuration file updated'

def setEncoding():
    '''Expand on this later'''

    return 'utf-8' #ascii, utf-16

def makeSwingBox(xWidth, xHeight):
    ''' Makes a swing box to the desired size'''

    xName = javax.swing.Box(javax.swing.BoxLayout.X_AXIS)
    xName.setPreferredSize(java.awt.Dimension(width=xWidth, height=xHeight))
    return xName

def makeWindow():
    '''Makes a swing frame with the desired name'''

    pFrame = javax.swing.JFrame()
    pFrame.contentPane.setLayout(javax.swing.BoxLayout(pFrame.contentPane, javax.swing.BoxLayout.Y_AXIS))
    pFrame.contentPane.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    pFrame.contentPane.setAlignmentX(0.0)
    iconPath = jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern\\decpro5.png'
    icon = java.awt.Toolkit.getDefaultToolkit().getImage(iconPath)
    pFrame.setIconImage(icon)
    return pFrame

def makeControlPanel():
    '''Create the control panel, with a scroll bar, that all sub panels go into
    This holds trackPatternPanel and future panels'''

    # configFile = readConfigFile()
    configFile = readConfigFile('ControlPanel')
    controlPanel = javax.swing.JPanel() # The whole panel that everything goes into
    scrollPanel = javax.swing.JScrollPane(controlPanel) # and that goes into a scroll pane
    scrollPanel.border = javax.swing.BorderFactory.createLineBorder(java.awt.Color.GRAY)
    scrollPanel.setPreferredSize(java.awt.Dimension(configFile['PW'], configFile['PH']))
    scrollPanel.setMaximumSize(scrollPanel.getPreferredSize())
    return controlPanel, scrollPanel

def validTime():
    '''Valid Time, get local time adjusted for time zone and dst'''

    jT = time.time()
    if time.localtime(jT).tm_isdst and time.daylight: # If local dst and dst are both 1
        jTO = time.altzone
    else:
        jTO = time.timezone # in seconds
    return time.strftime('%a %b %d %Y %I:%M %p %Z', time.gmtime(jT - jTO))

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

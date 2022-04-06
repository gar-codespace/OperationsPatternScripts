# coding=utf-8
# © 2021 Greg Ritacco

import jmri
from java import io as javaIo
import java.awt
import javax.swing
import logging
import time
from json import loads as jsonLoads, dumps as jsonDumps
from codecs import open as codecsOpen
from os import mkdir as osMakeDir
from shutil import copy as shutilCopy

'''Support methods for any Pattern Script'''

_lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
_tm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.trains.TrainManager)
_em = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.engines.EngineManager)
_cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
_cmx = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManagerXml)
_sm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.schedules.ScheduleManager)
_pm = jmri.InstanceManager.getDefault(jmri.util.gui.GuiLafPreferencesManager)

_currentPath = ''
_trackNameClickedOn = None
_listOfAssignedRs = []

scriptName = 'OperationsPatternScripts.psEntities.MainScriptEntities'
scriptRev = 20220101
psLog = logging.getLogger('PS.TP.MainScriptEntities')

def setEncoding():
    '''Expand on this later'''

    return 'utf-8' #ascii, utf-16

def setColors():
    '''Call this before using color'''

    colorDefinition = readConfigFile('CD')

    r = colorDefinition['CP'][colorDefinition['color1']]["R"]
    g = colorDefinition['CP'][colorDefinition['color1']]["G"]
    b = colorDefinition['CP'][colorDefinition['color1']]["B"]
    global _COLOR1
    _COLOR1 = java.awt.Color(r, g, b)

    r = colorDefinition['CP'][colorDefinition['color2']]["R"]
    g = colorDefinition['CP'][colorDefinition['color2']]["G"]
    b = colorDefinition['CP'][colorDefinition['color2']]["B"]
    global _COLOR2
    _COLOR2 = java.awt.Color(r, g, b)

    r = colorDefinition['CP'][colorDefinition['color3']]["R"]
    g = colorDefinition['CP'][colorDefinition['color3']]["G"]
    b = colorDefinition['CP'][colorDefinition['color3']]["B"]
    global _COLOR3
    _COLOR3 = java.awt.Color(r, g, b)

    return

def timeStamp(epochTime=0):
    '''Valid Time, get local time adjusted for time zone and dst'''

    if epochTime == 0:
        epochTime = time.time()
    if time.localtime(epochTime).tm_isdst and time.daylight: # If local dst and dst are both 1
        timeOffset = time.altzone
    else:
        timeOffset = time.timezone # in seconds

    return time.strftime('%a %b %d %Y %I:%M %p %Z', time.gmtime(epochTime - timeOffset))

def openEditorByComputerType(switchListLocation=None):
    '''Opens a text file in a text editor for each type of computer.'''

    osType = jmri.util.SystemType.getType()
    editorMatrix = readConfigFile('EM')
    textEditor = editorMatrix[str(osType)]
    openEditor = textEditor + '"' + switchListLocation + '"'

    return openEditor

def validateStubFile():
    '''Copy of the JMRI Java version of createStubFile'''

    locale = u'en'
    locale = unicode(_pm.getLocale(), setEncoding())
    stubLocation = jmri.util.FileUtil.getPreferencesPath() + '\\jmrihelp\\'
    try:
        osMakeDir(stubLocation)
        psLog.warning('Stub location created at: ' + stubLocation)
    except OSError:
        psLog.info('Stub location already exists')
    stubFileName = stubLocation + 'psStub.html'
    helpFilePath = javaIo.File(_currentPath + '/Support/psHelp.html').toURI()
    helpFilePath = unicode(helpFilePath, setEncoding())
    stubTemplateLocation = jmri.util.FileUtil.getProgramPath() + 'help\\' + locale[:2] + '\\local\\stub_template.html'
    with codecsOpen(stubTemplateLocation, 'r', encoding=setEncoding()) as template:
        contents = template.read()
        contents = contents.replace("../index.html#", "")
        contents = contents.replace("<!--HELP_KEY-->", helpFilePath)
        contents = contents.replace("<!--URL_HELP_KEY-->", "")
    with codecsOpen(stubFileName, 'wb', encoding=setEncoding()) as stubWorkFile:
        stubWorkFile.write(contents)
        psLog.debug('psStub writen from stub_template')

    return

def validateFileDestinationDirestories():
    '''Checks that the folders this plugin writes to exist'''
# Can't use jmri.util.FileUtil.createDirectory().... does not return anything
    x = 0
    destDirPath = jmri.util.FileUtil.getProfilePath() + 'operations\\'
    try:
        osMakeDir(destDirPath + 'buildstatus')
        psLog.warning('buildstatus folder created')
    except OSError:
        x += 1
    try:
        osMakeDir(destDirPath + 'csvSwitchLists')
        psLog.warning('csvSwitchLists folder created')
    except OSError:
        x += 1
    try:
        osMakeDir(destDirPath + 'jsonManifests')
        psLog.warning('jsonManifests folder created')
    except OSError:
        x += 1
    try:
        osMakeDir(destDirPath + 'switchLists')
        psLog.warning('switchLists folder created')
    except OSError:
        x += 1

    if (x == 4):
        psLog.info('Destination folders check OK')

    return

def validateConfigFile():
    '''Checks that the config file is the current version'''

    with codecsOpen(_currentPath + '\\PatternConfig.json', 'r', encoding=setEncoding()) as validConfigFileLoc:
        validConfigFile = jsonLoads(validConfigFileLoc.read())

    if validConfigFile['CP']['RV'] == getConfigFile()['CP']['RV']:
        psLog.info('The PatternConfig.JSON file is the correct version')
        return True
    else:
        psLog.warning('PatternConfig.JSON version mismatch')
        return False

def readConfigFile(subConfig='all'):

    try:
        configFile = getConfigFile(subConfig)
        return configFile
    except ValueError:
        psLog.warning('Defective PatternConfig.JSON found, new file written')
        writeNewConfigFile()
        configFile = getConfigFile(subConfig)
        return configFile
    except IOError:
        psLog.warning('No PatternConfig.JSON found, new file written')
        writeNewConfigFile()
        configFile = getConfigFile(subConfig)
        return configFile

def backupConfigFile():

    copyTo = javaIo.File(jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json.bak')
    copyFrom = javaIo.File(jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json')
    jmri.util.FileUtil.copy(copyFrom, copyTo)

    return

def getConfigFile(subConfig='all'):
    '''Returns the config file, wether its compromised or not'''

    configFileLoc = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'

    with codecsOpen(configFileLoc, 'r', encoding=setEncoding()) as configWorkFile:
        configFile = jsonLoads(configWorkFile.read())
    if (subConfig == 'all'):
        return configFile
    else:
        return configFile[subConfig]

def writeConfigFile(configFile):
    '''Updates the PatternConfig.json file'''

    jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
    jsonObject = jsonDumps(configFile, indent=2, sort_keys=True)
    with codecsOpen(jsonCopyTo, 'wb', encoding=setEncoding()) as jsonWorkFile:
        jsonWorkFile.write(jsonObject)

    return

def writeNewConfigFile():
    '''Copies the default config file to the profile location'''

    copyTo = javaIo.File(jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json')
    copyFrom = javaIo.File(_currentPath + '\\PatternConfig.json')
    jmri.util.FileUtil.copy(copyFrom, copyTo)

    return

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

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

scriptName = 'OperationsPatternScripts.psEntities.MainScriptEntities'
scriptRev = 20220101
psLog = logging.getLogger('PS.TP.MainScriptEntities')

def setEncoding():
    '''Expand on this later'''

    return 'utf-8' #ascii, utf-16

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

    osName = jmri.util.SystemType.getType()
    textEdit = {
        1: 'Mac Classic ',
        2: 'open -a TextEdit "' + switchListLocation + '"', # OSX
        4: 'start notepad.exe "' + switchListLocation + '"', # put the switchListLocation in quotes to work around names with &
        5: 'nano "' + switchListLocation + '"', # Linux
        6: 'OS2 ',
        7: 'kwrite ', # Unix
        }

    return textEdit[osName]

def validateStubFile():
    '''Copy of the JMRI Java version of createStubFile'''

    locale = u'en'
    locale = unicode(_pm.getLocale(), setEncoding())
    stubLocation = jmri.util.FileUtil.getPreferencesPath() + '\\jmrihelp\\'
    try:
        osMakeDir(stubLocation)
        psLog.warning('stub location created at: ' + stubLocation)
    except OSError:
        psLog.info('stub location already exists')
    stubFileName = stubLocation + 'psStub.html'
    helpFilePath = javaIo.File(_currentPath + '/Support/psHelp.html').toURI()
    helpFilePath = unicode(helpFilePath, setEncoding())
    stubTemplateLocation = jmri.util.FileUtil.getProgramPath() + 'help\\' + locale[:2] + '\\local\\stub_template.html'
    with codecsOpen(stubTemplateLocation, 'r', encoding=setEncoding()) as template:
        contents = template.read()
        replaceContents = contents.replace("../index.html#", "")
        replaceContents = replaceContents.replace("<!--HELP_KEY-->", helpFilePath)
        replaceContents = replaceContents.replace("<!--URL_HELP_KEY-->", "")
        with codecsOpen(stubFileName, 'wb', encoding=setEncoding()) as stubWorkFile:
            stubWorkFile.write(replaceContents)
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
    '''Checks for an up to date, missing or ureadable config file'''

    try:
        readConfigFile()
    except ValueError:
        psLog.warning('Defective PatternConfig.JSON found')
        writeNewConfigFile()
    except IOError:
        psLog.warning('No PatternConfig.JSON found')
        writeNewConfigFile()

    with codecsOpen(_currentPath + '\\PatternConfig.json', 'r', encoding=setEncoding()) as validConfigFileLoc:
        validConfigFile = jsonLoads(validConfigFileLoc.read())

    if validConfigFile['CP']['RV'] == readConfigFile()['CP']['RV']:
        psLog.info('PatternConfig.JSON file is up to date')

    else:
        psLog.warning('PatternConfig.JSON version mismatch')
        copyTo = javaIo.File(jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json.bak')
        copyFrom = javaIo.File(jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json')
        jmri.util.FileUtil.copy(copyFrom, copyTo)
        psLog.warning('PatternConfig.json.bak file written')
        writeNewConfigFile()

    return

def readConfigFile(subConfig='all'):
    '''Read in the PatternConfig.json for a profile and return it as a dictionary'''

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
    psLog.warning('New PatternConfig.JSON file created for this profile')

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

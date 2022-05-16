# coding=utf-8
# © 2021, 2022 Greg Ritacco

'''Support methods for all Pattern Script subroutines'''

import jmri
from java import io as javaIo
import java.awt
import javax.swing

import logging
import time
from json import loads as jsonLoads, dumps as jsonDumps
from codecs import open as codecsOpen
from os import mkdir as osMakeDir
from os import system as osSystem
from shutil import copy as shutilCopy

LM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
TM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.trains.TrainManager)
EM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.engines.EngineManager)
CM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
SM = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.schedules.ScheduleManager)
PM = jmri.InstanceManager.getDefault(jmri.util.gui.GuiLafPreferencesManager)

'''Global variables for now, this may change'''
SCRIPT_ROOT = ''
BUNDLE = {}

SCRIPT_NAME = 'OperationsPatternScripts.psEntities.PatternScriptEntities'
SCRIPT_REV = 20220101

psLog = logging.getLogger('PS.PE.PatternScriptEntities')

class Logger:

    def __init__(self, logPath):

        logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.psFileHandler = logging.FileHandler(logPath, mode='w', encoding='utf-8')
        self.psFileHandler.setFormatter(logFileFormat)

        return

    def startLogger(self, log):

        psLog = logging.getLogger(log)
        psLog.setLevel(10)
        psLog.addHandler(self.psFileHandler)

        return

    def stopLogger(self, log):

        psLog = logging.getLogger(log)
        psLog.removeHandler(self.psFileHandler)

        return

    def initialLogMessage(self, log):

        log.debug('Initialize log file - DEBUG level test message')
        log.info('Initialize log file - INFO level test message')
        log.warning('Initialize log file - WARNING level test message')
        log.error('Initialize log file - ERROR level test message')
        log.critical('Initialize log file - CRITICAL level test message')

        return

class CheckTpDestination:
    '''Verify or create a TrainPlayer destination directory'''

    def __init__(self):

        self.psLog = logging.getLogger('PS.TP.CheckTpDestination')

        return

    def directoryExists(self):

        try:
            osMakeDir(jmri.util.FileUtil.getHomePath() + 'AppData\\Roaming\\TrainPlayer\\Reports')
            self.psLog.warning('TrainPlayer destination directory created')
        except OSError:
            self.psLog.info('TrainPlayer destination directory OK')

        return

def psLocale():

    return PM.getLocale().toString()
    # return unicode(PM.getLocale(), setEncoding())

def setEncoding():
    '''Move this to the confif file?'''

    # psEncoding = readConfigFile('CP')['SE']

    return 'utf-8' #ascii, utf-16

def formatText(item, length):
    '''Truncate each item to its defined length in PatternConfig.json and add a space at the end'''
    # This version works with utf-8

    if len(item) < length:
        xItem = item.ljust(length)
    else:
        xItem = item[:length]

    return xItem + u' '

def occuranceTally(listOfOccurances):
    '''Tally the occurances of a word in a list and return a dictionary'''

    dict = {}
    while len(listOfOccurances):
        occurance = listOfOccurances[-1]
        tally = 0
        for i in xrange(len(listOfOccurances) - 1, -1, -1): # run list from bottom up
            if (listOfOccurances[i] == occurance):
                tally += 1
                listOfOccurances.pop(i)
        dict[occurance] = tally

    return dict

def getStubPath():
    '''Convert an OS path to a browser acceptable URI, there is probably a method that does this'''

    stubPath = 'file:///' + jmri.util.FileUtil.getPreferencesPath() + 'jmrihelp/psStub.html'
    stubPath = stubPath.replace('\\', '/')
    stubPath = stubPath.replace(' ', '%20')
    stubPath = stubPath.replace('  ', '%20%20')

    return stubPath

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

def validateStubFile(currentRootDir):
    '''Copy of the JMRI Java version of createStubFile'''

    stubLocation = jmri.util.FileUtil.getPreferencesPath() + '\\jmrihelp\\'
    try:
        osMakeDir(stubLocation)
        psLog.info('Stub location created at: ' + stubLocation)
    except OSError:
        psLog.info('Stub location already exists')

    stubFileName = stubLocation + 'psStub.html'

    helpFilePath = currentRootDir + '\psSupport\psHelp.html'
    helpFilePath = javaIo.File(helpFilePath).toURI()
    helpFilePath = unicode(helpFilePath, setEncoding())

    stubTemplateLocation = jmri.util.FileUtil.getProgramPath() + 'help\\' + psLocale() + '\\local\\stub_template.html'
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
    destDirPath = jmri.util.FileUtil.getProfilePath() + 'operations\\'
    listOfDirectories = ['csvManifests', 'csvSwitchLists', 'jsonManifests', 'switchLists']
    x = 0
    for directory in listOfDirectories:
        try:
            osMakeDir(destDirPath + directory)
            psLog.warning(directory + ' folder created')
        except OSError:
            x += 1
    if (x == 4):
        psLog.info('Destination folders check OK')

    return

def validateConfigFile(currentRootDir):
    '''Checks that the config file is the current version'''

    configFilePath = currentRootDir + '\psEntities\PatternConfig.json'
    with codecsOpen(configFilePath, 'r', encoding=setEncoding()) as validConfigFileLoc:
        validPatternConfig = jsonLoads(validConfigFileLoc.read())

    userPatternConfig = getConfigFile()
    if validPatternConfig['CP']['RV'] == userPatternConfig['CP']['RV']:
        psLog.info('The PatternConfig.JSON file is the correct version')
        return True
    else:
        psLog.warning('PatternConfig.JSON version mismatch')
        return False

def backupConfigFile():

    copyFrom = javaIo.File(jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json')
    copyTo = javaIo.File(jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json.bak')
    jmri.util.FileUtil.copy(copyFrom, copyTo)

    return

def readConfigFile(subConfig=None):

    try:
        getConfigFile()
    except ValueError:
        writeNewConfigFile()
        psLog.warning('Defective PatternConfig.JSON found, new file written')
    except IOError:
        writeNewConfigFile()
        psLog.warning('No PatternConfig.JSON found, new file written')

    if not subConfig:
        return getConfigFile()
    else:
        return getConfigFile()[subConfig]

def getConfigFile():
    '''Returns the users PatternConfig file from the active profile'''

    configFileLoc = jmri.util.FileUtil.getProfilePath() + 'operations\PatternConfig.json'

    with codecsOpen(configFileLoc, 'r', encoding=setEncoding()) as configWorkFile:
        patternConfig = jsonLoads(configWorkFile.read())

    return patternConfig

def writeConfigFile(configFile):
    '''Updates the users PatternConfig.json file'''

    jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
    jsonObject = jsonDumps(configFile, indent=2, sort_keys=True)
    with codecsOpen(jsonCopyTo, 'wb', encoding=setEncoding()) as jsonWorkFile:
        jsonWorkFile.write(jsonObject)

    return

def writeNewConfigFile():
    '''Copies the default PatternConfig.JSON to the profile location'''

    defaultConfigFilePath = SCRIPT_ROOT + '\psEntities\PatternConfig.json'
    copyFrom = javaIo.File(defaultConfigFilePath)
    copyTo = javaIo.File(jmri.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json')
    jmri.util.FileUtil.copy(copyFrom, copyTo)

    return

def makePatternLog():
    '''creates a pattern log for display based on the log level, as set by getBuildReportLevel'''

    outputPatternLog = ''
    buildReportLevel = int(jmri.jmrit.operations.setup.Setup.getBuildReportLevel())
    configLoggingIndex = readConfigFile('LI')
    logLevel = configLoggingIndex[jmri.jmrit.operations.setup.Setup.getBuildReportLevel()]
    logFileLocation = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog.txt'
    with codecsOpen(logFileLocation, 'r', encoding=setEncoding()) as patternLogFile:
        while True:
            thisLine = patternLogFile.readline()
            if not (thisLine):
                break
            if (configLoggingIndex['9'] in thisLine and buildReportLevel > 0): # critical
                outputPatternLog += thisLine
            if (configLoggingIndex['7'] in thisLine and buildReportLevel > 0): # error
                outputPatternLog += thisLine
            if (configLoggingIndex['5'] in thisLine and buildReportLevel > 0): # warning
                outputPatternLog += thisLine
            if (configLoggingIndex['3'] in thisLine and buildReportLevel > 2): # info
                outputPatternLog += thisLine
            if (configLoggingIndex['1'] in thisLine and buildReportLevel > 4): # debug
                outputPatternLog += thisLine

    tempLogFileLocation = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog_temp.txt'
    with codecsOpen(tempLogFileLocation, 'w', encoding=setEncoding()) as tempPatternLogFile:
        tempPatternLogFile.write(outputPatternLog)

    return

def printPatternLog():
    '''Opens the pattern log in notepad or other'''

    psLog.debug('displayPatternLog')

    tempPatternLog = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\PatternScriptsLog_temp.txt'
    osSystem(openEditorByComputerType(tempPatternLog))

    return

def getCarColor():

    colorDefinition = readConfigFile('CD')

    r = colorDefinition['CP'][colorDefinition['carColor']]["R"]
    g = colorDefinition['CP'][colorDefinition['carColor']]["G"]
    b = colorDefinition['CP'][colorDefinition['carColor']]["B"]
    a = colorDefinition['CP'][colorDefinition['carColor']]["A"]

    return java.awt.Color(r, g, b, a)

def getLocoColor():

    colorDefinition = readConfigFile('CD')

    r = colorDefinition['CP'][colorDefinition['locoColor']]["R"]
    g = colorDefinition['CP'][colorDefinition['locoColor']]["G"]
    b = colorDefinition['CP'][colorDefinition['locoColor']]["B"]
    a = colorDefinition['CP'][colorDefinition['locoColor']]["A"]

    return java.awt.Color(r, g, b, a)

def getAlertColor():

    colorDefinition = readConfigFile('CD')

    r = colorDefinition['CP'][colorDefinition['alertColor']]["R"]
    g = colorDefinition['CP'][colorDefinition['alertColor']]["G"]
    b = colorDefinition['CP'][colorDefinition['alertColor']]["B"]
    a = colorDefinition['CP'][colorDefinition['alertColor']]["A"]

    return java.awt.Color(r, g, b, a)

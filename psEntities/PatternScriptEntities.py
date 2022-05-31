# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Support methods for all Pattern Script subroutines"""

import jmri as JMRI
import java.awt as JAVA_AWT
import javax.swing as JAVAX_SWING
import logging as LOGGING

import time
from java import io as javaIo
from json import loads as jsonLoads, dumps as jsonDumps
from codecs import open as codecsOpen
from os import system as osSystem

PLUGIN_ROOT = ''
ENCODING = ''
BUNDLE = {}
PROFILE_PATH = JMRI.util.FileUtil.getProfilePath()

SCRIPT_NAME = 'OperationsPatternScripts.psEntities.PatternScriptEntities'
SCRIPT_REV = 20220101

LM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.locations.LocationManager)
TM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.trains.TrainManager)
EM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.rollingstock.engines.EngineManager)
CM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.rollingstock.cars.CarManager)
SM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.locations.schedules.ScheduleManager)
PM = JMRI.InstanceManager.getDefault(JMRI.util.gui.GuiLafPreferencesManager)

psLog = LOGGING.getLogger('PS.PE.PatternScriptEntities')

class Logger:

    def __init__(self, logPath):

        logFileFormat = LOGGING.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.psFileHandler = LOGGING.FileHandler(logPath, mode='w', encoding='utf-8')
        self.psFileHandler.setFormatter(logFileFormat)

        return

    def startLogger(self, log):

        psLog = LOGGING.getLogger(log)
        psLog.setLevel(10)
        psLog.addHandler(self.psFileHandler)

        return

    def stopLogger(self, log):

        psLog = LOGGING.getLogger(log)
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
    """Verify or create a TrainPlayer destination directory"""

    def __init__(self):

        self.psLog = LOGGING.getLogger('PS.TP.CheckTpDestination')

        return

    def directoryExists(self):

        tpDirectory = JMRI.util.FileUtil.getHomePath() + 'AppData\\Roaming\\TrainPlayer\\Reports\\'
        tpDrrectoryFlag = javaIo.File(tpDirectory).isDirectory()
        if tpDrrectoryFlag:
            self.psLog.info('TrainPlayer destination directory OK')
        else:
            self.psLog.warning('TrainPlayer Reports destination directory not found')
            print('TrainPlayer Reports destination directory not found')

        return tpDrrectoryFlag

def psLocale():

    return PM.getLocale().toString()
    # return unicode(PM.getLocale(), ENCODING)

def formatText(item, length):
    """Truncate each item to its defined length in PatternConfig.json and add a space at the end"""

    if len(item) < length:
        xItem = item.ljust(length)
    else:
        xItem = item[:length]

    return xItem + u' '

def occuranceTally(listOfOccurances):
    """Tally the occurances of a word in a list and return a dictionary
    Home grown version of collections.Counter"""

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
    """Convert an OS path to a browser acceptable URI.
    There is probably a method that already does this
    """

    stubPath = 'file:///' + JMRI.util.FileUtil.getPreferencesPath() + 'jmrihelp/psStub.html'
    stubPath = stubPath.replace('\\', '/')
    stubPath = stubPath.replace(' ', '%20')
    stubPath = stubPath.replace('  ', '%20%20')

    return stubPath

def timeStamp(epochTime=0):
    """Valid Time, get local time adjusted for time zone and dst"""

    if epochTime == 0:
        epochTime = time.time()
    if time.localtime(epochTime).tm_isdst and time.daylight: # If local dst and dst are both 1
        timeOffset = time.altzone
    else:
        timeOffset = time.timezone # in seconds

    return time.strftime('%a %b %d %Y %I:%M %p %Z', time.gmtime(epochTime - timeOffset))

def genericWriteReport(filePath, textSwitchList):

    with codecsOpen(filePath, 'wb', encoding=ENCODING) as textWorkFile:
        textWorkFile.write(textSwitchList)

    return

def genericDisplayReport(genericReportPath):

    osSystem(openEditorByComputerType(genericReportPath))

    return

def openEditorByComputerType(switchListLocation=None):
    """Opens a text file in a text editor for each type of computer."""

    osType = JMRI.util.SystemType.getType()
    editorMatrix = readConfigFile('EM')
    textEditor = editorMatrix[str(osType)]
    openEditor = textEditor + '"' + switchListLocation + '"' # Double quotes escapes the & symbol

    backupConfigFile()
    return openEditor



class validateStubFile:
    """Copy of the JMRI Java version of createStubFile"""

    def __init__(self):

        self.stubLocation = JMRI.util.FileUtil.getPreferencesPath() + '\\jmrihelp\\'
        self.stubFileName = self.stubLocation + 'psStub.html'
        self.helpFilePath = ''
        self.newStubFile = ''

        return

    def validateStubLocation(self):

        if javaIo.File(self.stubLocation).mkdir():
            psLog.info('Stub location created at: ' + self.stubLocation)
        else:
            psLog.info('Stub location already exists')

        return

    def makehelpFilePath(self):

        self.helpFilePath = PLUGIN_ROOT + '\psSupport\psHelp.html'
        self.helpFilePath = javaIo.File(self.helpFilePath).toURI()
        self.helpFilePath = unicode(self.helpFilePath, ENCODING)

    def updateStubTemplate(self):

        stubTemplateLocation = JMRI.util.FileUtil.getProgramPath() + 'help\\' + psLocale() \
        + '\\local\\stub_template.html'

        with codecsOpen(stubTemplateLocation, 'r', encoding=ENCODING) as template:
            self.newStubFile = template.read()
            self.newStubFile = self.newStubFile.replace("../index.html#", "")
            self.newStubFile = self.newStubFile.replace("<!--HELP_KEY-->", self.helpFilePath)
            self.newStubFile = self.newStubFile.replace("<!--URL_HELP_KEY-->", "")

        return self.newStubFile

    def writeStubFile(self):

        with codecsOpen(self.stubFileName, 'wb', encoding=ENCODING) as stubWorkFile:
            stubWorkFile.write(self.newStubFile)
            psLog.debug('psStub writen from stub_template')

            return

    def isStubFile(self):

        self.validateStubLocation()
        self.makehelpFilePath()
        self.updateStubTemplate()
        self.writeStubFile()

        return

def validateFileDestinationDirestories():
    """Checks that the folders this plugin writes to exist"""

    destDirPath = JMRI.util.FileUtil.getProfilePath() + 'operations\\'
    listOfDirectories = ['csvManifests', 'csvSwitchLists', 'jsonManifests', 'switchLists', 'patternReports']
    x = 0
    for directory in listOfDirectories:
        testDirectory = destDirPath + directory + '\\'
        if javaIo.File(testDirectory).isDirectory():
            x += 1
        else:
            javaIo.File(testDirectory).mkdir()
            psLog.warning(directory + ' created at ' + destDirPath)

    if x == len(listOfDirectories):
        psLog.info('Destination folders check OK')

    return

def validateConfigFileVersion(currentRootDir):
    """Checks that the config file is the current version"""

    configFilePath = currentRootDir + '\psEntities\PatternConfig.json'
    with codecsOpen(configFilePath, 'r', encoding=ENCODING) as validConfigFileLoc:
        validPatternConfig = jsonLoads(validConfigFileLoc.read())

    userPatternConfig = getConfigFile()

    if validPatternConfig['CP']['RV'] == userPatternConfig['CP']['RV']:
        psLog.info('The PatternConfig.json file is the correct version')
        return True
    else:
        psLog.warning('PatternConfig.json version mismatch')
        return False

def backupConfigFile():

    copyFrom = javaIo.File(JMRI.util.FileUtil.getProfilePath() \
             + 'operations\\PatternConfig.json')
    copyTo = javaIo.File(JMRI.util.FileUtil.getProfilePath() \
           + 'operations\\PatternConfig.json.bak')
    JMRI.util.FileUtil.copy(copyFrom, copyTo)

    return

def restoreConfigFile():

    copyFrom = javaIo.File(JMRI.util.FileUtil.getProfilePath() \
             + 'operations\PatternConfig.json.bak')
    copyTo = javaIo.File(JMRI.util.FileUtil.getProfilePath() \
           + 'operations\\PatternConfig.json')
    JMRI.util.FileUtil.copy(copyFrom, copyTo)

    return

def mergeConfigFiles():
    """Implemented in v3"""
    return

def readConfigFile(subConfig=None):

    configFile = tryConfigFile()

    if not subConfig:
        return configFile
    else:
        return configFile[subConfig]

def tryConfigFile():
    """Catch some user edit mistakes"""

    try:
        configFile = getConfigFile()
    except ValueError:
        restoreConfigFile()
        configFile = getConfigFile()
        psLog.warning('Defective PatternConfig.json found, new file restored from backup')
    except IOError:
        writeNewConfigFile()
        configFile = getConfigFile()
        psLog.warning('No PatternConfig.json found, new file written')

    return configFile

def getConfigFile():

    configFileLoc = JMRI.util.FileUtil.getProfilePath() + 'operations\PatternConfig.json'

    with codecsOpen(configFileLoc, 'r', encoding='utf-8') as configWorkFile:
        patternConfig = jsonLoads(configWorkFile.read())

    return patternConfig

def writeConfigFile(configFile):

    jsonCopyTo = JMRI.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json'
    jsonObject = jsonDumps(configFile, indent=2, sort_keys=True)
    with codecsOpen(jsonCopyTo, 'wb', encoding='utf-8') as jsonWorkFile:
        jsonWorkFile.write(jsonObject)

    return

def writeNewConfigFile():

    defaultConfigFilePath = PLUGIN_ROOT + '\psEntities\PatternConfig.json'
    copyFrom = javaIo.File(defaultConfigFilePath)
    copyTo = javaIo.File(JMRI.util.FileUtil.getProfilePath() + 'operations\\PatternConfig.json')
    JMRI.util.FileUtil.copy(copyFrom, copyTo)

    return

def makePatternLog():
    """creates a pattern log for display based on the log level, as set by getBuildReportLevel"""

    outputPatternLog = ''
    buildReportLevel = JMRI.jmrit.operations.setup.Setup.getBuildReportLevel()
    loggingIndex = readConfigFile('LI')
    logLevel = loggingIndex[buildReportLevel]
    logFileLocation = JMRI.util.FileUtil.getProfilePath() \
                    + 'operations\\buildstatus\\PatternScriptsLog.txt'
    with codecsOpen(logFileLocation, 'r', encoding=ENCODING) as patternLogFile:
        while True:
            thisLine = patternLogFile.readline()
            if not thisLine:
                break
            if (loggingIndex['9'] in thisLine and int(buildReportLevel) > 0): # critical
                outputPatternLog += thisLine
            if (loggingIndex['7'] in thisLine and int(buildReportLevel) > 0): # error
                outputPatternLog += thisLine
            if (loggingIndex['5'] in thisLine and int(buildReportLevel) > 0): # warning
                outputPatternLog += thisLine
            if (loggingIndex['3'] in thisLine and int(buildReportLevel) > 2): # info
                outputPatternLog += thisLine
            if (loggingIndex['1'] in thisLine and int(buildReportLevel) > 4): # debug
                outputPatternLog += thisLine

    return 'PatternScriptsLog_temp', outputPatternLog

def getRollingStock(rsId):

    try:
        rs = CM.getById(rsId)
        if not rs:
            rs = EM.getById(rsId)
    except:
        rs = None

    return rs

def getAllLocations():
    """JMRI sorts the list"""

    allLocations = LM.getLocationsByNameList()
    locationList = []
    for item in allLocations:
        locationList.append(unicode(item.getName(), ENCODING))

    return locationList

def getCarColor():
    """backupConfigFile() is a bit of user edit protection"""

    colorDefinition = readConfigFile('CD')

    r = colorDefinition['CP'][colorDefinition['carColor']]["R"]
    g = colorDefinition['CP'][colorDefinition['carColor']]["G"]
    b = colorDefinition['CP'][colorDefinition['carColor']]["B"]
    a = colorDefinition['CP'][colorDefinition['carColor']]["A"]

    backupConfigFile()
    return JAVA_AWT.Color(r, g, b, a)

def getLocoColor():

    colorDefinition = readConfigFile('CD')

    r = colorDefinition['CP'][colorDefinition['locoColor']]["R"]
    g = colorDefinition['CP'][colorDefinition['locoColor']]["G"]
    b = colorDefinition['CP'][colorDefinition['locoColor']]["B"]
    a = colorDefinition['CP'][colorDefinition['locoColor']]["A"]

    backupConfigFile()
    return JAVA_AWT.Color(r, g, b, a)

def getAlertColor():

    colorDefinition = readConfigFile('CD')

    r = colorDefinition['CP'][colorDefinition['alertColor']]["R"]
    g = colorDefinition['CP'][colorDefinition['alertColor']]["G"]
    b = colorDefinition['CP'][colorDefinition['alertColor']]["B"]
    a = colorDefinition['CP'][colorDefinition['alertColor']]["A"]

    backupConfigFile()
    return JAVA_AWT.Color(r, g, b, a)

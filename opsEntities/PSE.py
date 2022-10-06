# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""PSE is an abbreviation for PatternScriptEntities.
    Support methods and package constants for all Pattern Script subroutines.
    """

import jmri as JMRI
import logging as LOGGING
from java import io as JAVA_IO
import java.beans as JAVA_BEANS
from HTMLParser import HTMLParser as HTML_PARSER
from os import path as OS_PATH
from apps import Apps as APPS

import time
from json import loads as jsonLoads, dumps as jsonDumps
from codecs import open as codecsOpen

PLUGIN_ROOT = ''
PROFILE_PATH = JMRI.util.FileUtil.getProfilePath()
ENCODING = ''
BUNDLE = {}
REPORT_ITEM_WIDTH_MATRIX = {}
TRACK_NAME_CLICKED_ON = ''

# Dealers choice, both work OK:
J_BUNDLE = JMRI.jmrit.operations.setup.Setup()
# SB = JMRI.jmrit.operations.setup.Bundle()

SCRIPT_NAME = 'OperationsPatternScripts.opsEntities.PSE'
SCRIPT_REV = 20220101

OM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.OperationsManager)
PM = JMRI.InstanceManager.getDefault(JMRI.util.gui.GuiLafPreferencesManager)
TM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.trains.TrainManager)
RM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.routes.RouteManager)
LM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.locations.LocationManager)
CM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.rollingstock.cars.CarManager)
KM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.rollingstock.cars.KernelManager)
SM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.locations.schedules.ScheduleManager)
EM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.rollingstock.engines.EngineManager)
ZM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.rollingstock.engines.ConsistManager)

OMX = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.setup.OperationsSetupXml)
TMX = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.trains.TrainManagerXml)
RMX = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.routes.RouteManagerXml)
LMX = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.locations.LocationManagerXml)
CMX = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.rollingstock.cars.CarManagerXml)
EMX = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.rollingstock.engines.EngineManagerXml)

_psLog = LOGGING.getLogger('OPS.PSE.PSE')


class Logger:
    """Homebrew logging."""

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


class CreateStubFile:
    """Copy of the JMRI Java version of CreateStubFile."""

    def __init__(self):

        self.stubLocation = OS_PATH.join(JMRI.util.FileUtil.getPreferencesPath(), 'jmrihelp')

        self.helpFilePath = ''
        self.newStubFile = ''

        return

    def validateStubLocation(self):

        if JAVA_IO.File(self.stubLocation).mkdir():
            _psLog.info('Stub location created at: ' + self.stubLocation)
        else:
            _psLog.info('Stub location already exists')

        return

    def getHelpFileURI(self):

        helpFileName = 'Help.' + psLocale() + '.html'
        helpFilePath = OS_PATH.join(PLUGIN_ROOT, 'opsSupport', helpFileName)

        if not JAVA_IO.File(helpFilePath).isFile():
            helpFileName = 'Help.en.html'
            helpFilePath = OS_PATH.join(PLUGIN_ROOT, 'opsSupport', helpFileName)

        self.helpFilePath = JAVA_IO.File(helpFilePath).toURI().toString()

        return

    def makeNewStubFile(self):

        stubTemplateFile = 'stub_template.html'
        stubTemplatePath = OS_PATH.join(JMRI.util.FileUtil.getProgramPath(), 'help', psLocale()[:2], 'local', stubTemplateFile)
        if not JAVA_IO.File(stubTemplatePath).isFile():
            stubTemplatePath = OS_PATH.join(PLUGIN_ROOT, 'opsEntities', stubTemplateFile)

        stubTemplate = genericReadReport(stubTemplatePath)
        stubTemplate = stubTemplate.replace("../index.html#", "")
        stubTemplate = stubTemplate.replace("<!--HELP_KEY-->", self.helpFilePath)
        self.newStubFile = stubTemplate.replace("<!--URL_HELP_KEY-->", "")

        return

    def writeStubFile(self):

        stubFilePath = OS_PATH.join(self.stubLocation, 'psStub.html')

        genericWriteReport(stubFilePath, self.newStubFile)
        _psLog.debug('psStub writen from stub_template')

        return

    def make(self):
        """Mini controller guides the new stub file process."""

        self.validateStubLocation()
        self.getHelpFileURI()
        self.makeNewStubFile()
        self.writeStubFile()

        return


"""GUI Methods"""

def getPsButton():
    """Gets the Pattern Scripts button on the PanelPro frame"""

    buttonSpaceComponents = APPS.buttonSpace().getComponents()
    for component in buttonSpaceComponents:
        if component.getName() == 'psButton':
            return component
        else:
            return None

def closeSetCarsWindows():
    """Close all the Set Cars windows when the Pattern Scripts window is closed"""

    for frame in JMRI.util.JmriJFrame.getFrameList():
        if frame.getName() == 'setCarsWindow':
            frame.setVisible(False)
            frame.dispose()

    return

def updateWindowParams(window):
    """This can be done automatically by setting a prop somewhere"""

    configPanel = readConfigFile()
    configPanel['CP'].update({'PH': window.getHeight()})
    configPanel['CP'].update({'PW': window.getWidth()})
    configPanel['CP'].update({'PX': window.getX()})
    configPanel['CP'].update({'PY': window.getY()})
    writeConfigFile(configPanel)

    return

"""Utility Methods"""

def psLocale():
    """Dealers choice, both work.
        Used by:
        Bundle
        Translaters
        """

    return PM.getLocale().toString()
    # return unicode(PM.getLocale(), ENCODING)

def occuranceTally(listOfOccurances):
    """Tally the occurances of a word in a list and return a dictionary.
        Home grown version of collections.Counter.
        Used by:
        ModelEntities.getKernelTally
        ViewEntities.makeTextReportLocations
        """

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

def getAllLocationNames():
    """JMRI sorts the list, returns list of location names.
        Used by:
        Model.UpdateLocationsAndTracks
        PSE.getAllTrackIds
        Model.updatePatternLocation
        Model.updateLocations
        ModelEntities.testSelectedItem
        """

    locationNames = []
    for item in LM.getLocationsByNameList():
        locationNames.append(unicode(item.getName(), ENCODING))

    return locationNames

def getAllTracks():
    """All track objects for all locations.
        Used by:
        Model.UpdateLocationsAndTracks
        ModelEntities.setNonSpurTrackLength
        Model.updatePatternLocation
        """

    trackList = []
    for location in LM.getList():
        trackList += location.getTracksByNameList(None)

    return trackList

def getAllTrackIds():
    """All track IDs for all locations."""

    trackIds = []
    for location in getAllLocationNames():
        trackList = LM.getLocationByName(location).getTracksList()
        for track in trackList:
            trackIds.append(track.getComment())

    return trackIds

def getSelectedTracks():
    """Gets the track objects checked in the Track Pattern Subroutine.
        Used by:
        Controller.StartUp.trackPatternButton
        ModelEntities.makeTrackPattern
        View.setRsButton
        """

    patternTracks = readConfigFile('PT')['PT']

    return [track for track, include in sorted(patternTracks.items()) if include]

def getTracksNamesByLocation(trackType):
    """Used by:
        Model.verifySelectedTracks
        ViewEntities.merge
        """

    patternLocation = readConfigFile('PT')['PL']
    allTracksAtLoc = []
    try: # Catch on the fly user edit of config file error
        for track in LM.getLocationByName(patternLocation).getTracksByNameList(trackType):
            allTracksAtLoc.append(unicode(track.getName(), ENCODING))
        return allTracksAtLoc
    except AttributeError:
        return allTracksAtLoc

"""Formatting Methods"""

def timeStamp(epochTime=0):
    """Valid Time, get local time adjusted for time zone and dst."""

    if epochTime == 0:
        epochTime = time.time()
    if time.localtime(epochTime).tm_isdst and time.daylight: # If local dst and dst are both 1
        timeOffset = time.altzone
    else:
        timeOffset = time.timezone # in seconds

    return time.strftime('%a %b %d %Y %I:%M %p %Z', time.gmtime(epochTime - timeOffset))

def convertJmriDateToEpoch(jmriTime):
    """Example: 2022-02-26T17:16:17.807+0000"""

    epochTime = time.mktime(time.strptime(jmriTime, "%Y-%m-%dT%H:%M:%S.%f+0000"))

    if time.localtime(epochTime).tm_isdst and time.daylight: # If local dst and dst are both 1
        epochTime -= time.altzone
    else:
        epochTime -= time.timezone # in seconds

    return epochTime

def formatText(item, length):
    """Truncate each item to its defined length in PatternConfig.json and add a space at the end."""

    if isinstance(item, bool): # Hazardous is a boolean
        item = 'HazMat'
    if len(item) < length:
        xItem = item.ljust(length)
    else:
        xItem = item[:length]

    return xItem + u' '

def makeReportItemWidthMatrix():
    """The attribute widths (AW) for each of the rolling stock attributes is defined in the report matrix (RM) of the config file."""

    reportMatrix = {}
    attributeWidths = readConfigFile('RM')['AW']

    for aKey, aValue in attributeWidths.items():
        reportMatrix[aKey] = aValue

    return reportMatrix

def getShortLoadType(car):
    """Replaces empty and load with E, L, or O for occupied.
        JMRI defines custom load type as empty but default load type as Empty, hence the 'or' statement.
        Load, Empty, Occupied and Unknown are translated by the bundle.
        Used by:
        ViewEntities.modifyTrackPatternReport
        ModelWorkEvent.o2oSwitchListConversion.parsePtRs
        ModelWorkEvents.jmriManifestConversion.parseRS
        """

    try:
        rs = CM.getByRoadAndNumber(car['Road'], car['Number']) # Pattern scripts nomenclature
    except:
        rs = CM.getByRoadAndNumber(car['road'], car['number']) # JMRI nomenclature

    lt =  BUNDLE['unknown'].upper()[0]
    if rs.getLoadType() == 'empty' or rs.getLoadType() == 'Empty':
        lt = BUNDLE['empty'].upper()[0]

    if rs.getLoadType() == 'load' or rs.getLoadType() == 'Load':
        lt = BUNDLE['load'].upper()[0]

    if rs.isCaboose() or rs.isPassenger():
        lt = BUNDLE['occupied'].upper()[0]

    return lt

"""File Handling Methods"""

def makeBuildStatusFolder():
    """The buildStatus folder is created first so the log file can be written"""

    opsDirectory = JMRI.util.FileUtil.getProfilePath() + '\\operations'
    targetDirectory = OS_PATH.join(opsDirectory, 'buildstatus')
    if not JAVA_IO.File(targetDirectory).isDirectory():
        JAVA_IO.File(targetDirectory).mkdirs()

    return

def makeReportFolders():
    """Checks/creates the folders this plugin writes to."""

    opsDirectory = JMRI.util.FileUtil.getProfilePath() + '\\operations'
    directories = ['csvManifests', 'csvSwitchLists', 'jsonManifests', 'switchLists', 'patternReports']
    x = 0
    for directory in directories:
        targetDirectory = OS_PATH.join(opsDirectory, directory)
        if not JAVA_IO.File(targetDirectory).isDirectory():
            JAVA_IO.File(targetDirectory).mkdirs()
            _psLog.info('Directory created: ' + targetDirectory)
            x += 1

    if x == 0:
        _psLog.info('Destination folders check OK')
    else:
        _psLog.info(str(x) + 'Destination folders created')

    return

def genericReadReport(filePath):
    """try/except catches initial read of config file."""

    try:
        ENCODING
    except UnboundLocalError:
        ENCODING = 'utf-8'

    with codecsOpen(filePath, 'r', encoding=ENCODING) as textWorkFile:
        genericReport = textWorkFile.read()

    return genericReport

def genericWriteReport(filePath, genericReport):

    with codecsOpen(filePath, 'wb', encoding=ENCODING) as textWorkFile:
        textWorkFile.write(genericReport)

    return

def genericDisplayReport(genericReportPath):
    """Dealer's choice, the JMRI or Java version."""

    # JMRI.util.HelpUtil.openWindowsFile(genericReportPath)
    JAVA_AWT.Desktop.getDesktop().edit(JAVA_IO.File(genericReportPath))

    return

def loadJson(switchList):

    jsonSwitchList = jsonLoads(switchList)

    return jsonSwitchList

def dumpJson(switchList):

    jsonSwitchList = jsonDumps(switchList, indent=2, sort_keys=True)

    return jsonSwitchList

"""Configuration File Methods"""

def validateConfigFileVersion():
    """Checks that the config file is the current version."""

    targetDir =  PLUGIN_ROOT + '\\opsEntities'
    fileName = 'PatternConfig.json'
    targetPath = OS_PATH.join(targetDir, fileName)
    validPatternConfig = loadJson(genericReadReport(targetPath))

    if validPatternConfig['CP']['RV'] == readConfigFile('CP')['RV']:
        _psLog.info('The PatternConfig.json file is the correct version')
        return True
    else:
        _psLog.warning('PatternConfig.json version mismatch')
        return False

def mergeConfigFiles():
    """Implemented in v3"""
    return

def readConfigFile(subConfig=None):
    """tryConfigFile will return the config file if it's ok or a new one otherwise."""

    configFile = tryConfigFile()

    if not subConfig:
        return configFile
    else:
        return configFile[subConfig]

def tryConfigFile():
    """Try/except catches some user edit mistakes."""

    try:
        configFile = getConfigFile()
    except ValueError:
        writeNewConfigFile()
        configFile = getConfigFile()
        _psLog.warning('Defective PatternConfig.json found, new file written')
    except IOError:
        writeNewConfigFile()
        configFile = getConfigFile()
        _psLog.warning('No PatternConfig.json found, new file written')

    return configFile

def getConfigFile():

    targetDir = PROFILE_PATH + '\\operations'
    fileName = 'PatternConfig.json'
    targetPath = OS_PATH.join(targetDir, fileName)

    return loadJson(genericReadReport(targetPath))

def writeConfigFile(configFile):

    configFilePath = PROFILE_PATH + 'operations\\PatternConfig.json'
    formattedConfigFile = dumpJson(configFile)
    genericWriteReport(configFilePath, formattedConfigFile)

    return

def writeNewConfigFile():

    targetDir = PROFILE_PATH + 'operations\\'
    JAVA_IO.File(targetDir).mkdir()

    fileName = 'PatternConfig.json'

    targetDir = PLUGIN_ROOT + '\\opsEntities'
    targetPath = OS_PATH.join(targetDir, fileName)
    copyFrom = JAVA_IO.File(targetPath)

    targetDir = PROFILE_PATH + '\\operations'
    targetPath = OS_PATH.join(targetDir, fileName)
    copyTo = JAVA_IO.File(targetPath)

    JMRI.util.FileUtil.copy(copyFrom, copyTo)

    return

def deleteConfigFile():

    configFilePath = PROFILE_PATH + 'operations\PatternConfig.json'
    JAVA_IO.File(configFilePath).delete()

    return

"""Logging Methods"""

def makePatternLog():
    """creates a pattern log for display based on the log level, as set by getBuildReportLevel."""

    outputPatternLog = ''
    buildReportLevel = JMRI.jmrit.operations.setup.Setup.getBuildReportLevel()

    loggingIndex = logIndex()
    logLevel = loggingIndex[buildReportLevel]

    fileName = 'PatternScriptsLog.txt'
    targetDir = PROFILE_PATH + 'operations\\buildstatus'
    targetPath = OS_PATH.join(targetDir, fileName)
    patternLogFile = genericReadReport(targetPath)
    for thisLine in patternLogFile.splitlines():

        if loggingIndex['9'] in thisLine and int(buildReportLevel) > 0: # critical
            outputPatternLog += thisLine + '\n'
        if loggingIndex['7'] in thisLine and int(buildReportLevel) > 0: # error
            outputPatternLog += thisLine + '\n'
        if loggingIndex['5'] in thisLine and int(buildReportLevel) > 0: # warning
            outputPatternLog += thisLine + '\n'
        if loggingIndex['3'] in thisLine and int(buildReportLevel) > 2: # info
            outputPatternLog += thisLine + '\n'
        if loggingIndex['1'] in thisLine and int(buildReportLevel) > 4: # debug
            outputPatternLog += thisLine + '\n'

    return outputPatternLog

def logIndex():
    """Moved here but may be put back into configFile."""

    loggingIndex = {"9": "- CRITICAL -", "7": "- ERROR -", "5": "- WARNING -", "3": "- INFO -", "1": "- DEBUG -"}

    return loggingIndex

"""Color Handling Methods"""

def getGenericColor(colorName):
    """Try/Except is a bit of protection against bad edits."""

    colorPalette = readConfigFile('CD')['CP']

    try:
        r = colorPalette[colorName]["R"]
        g = colorPalette[colorName]["G"]
        b = colorPalette[colorName]["B"]
        a = colorPalette[colorName]["A"]

        return JAVA_AWT.Color(r, g, b, a)

    except KeyError:

        return None

def getCarColor():

    colorName = readConfigFile('CD')['carColor']
    color = getGenericColor(colorName)
    if not color:
        _psLog.warning('Car color definition not found in PatternConfig.json')

    return color

def getLocoColor():

    colorName = readConfigFile('CD')['locoColor']
    color = getGenericColor(colorName)
    if not color:
        _psLog.warning('Engine color definition not found in PatternConfig.json')

    return color

def getAlertColor():

    colorName = readConfigFile('CD')['alertColor']
    color = getGenericColor(colorName)
    if not color:
        _psLog.warning('Alert color definition not found in PatternConfig.json')

    return color

"""Translation Methods"""

def translateMessageFormat():
    """The messageFormat is in the locale's language, it has to be hashed to the plugin fields.
        Dealers choice, J_BUNDLE.ROAD or SB.handleGetMessage('Road').
        """

    rosetta = {}
#Common
    rosetta[J_BUNDLE.ROAD] = 'Road'
    rosetta[J_BUNDLE.NUMBER] = 'Number'
    rosetta[J_BUNDLE.TYPE] = 'Type'
    rosetta[J_BUNDLE.LENGTH] = 'Length'
    rosetta[J_BUNDLE.WEIGHT] = 'Weight'
    rosetta[J_BUNDLE.COLOR] = 'Color'
    rosetta[J_BUNDLE.OWNER] = 'Owner'
    rosetta[J_BUNDLE.TRACK] = 'Track'
    rosetta[J_BUNDLE.LOCATION] = 'Location'
    rosetta[J_BUNDLE.COMMENT] = 'Comment'
    rosetta[J_BUNDLE.DESTINATION] = 'Destination'
    rosetta[J_BUNDLE.DEST_TRACK] = 'Dest&Track'
    rosetta[J_BUNDLE.TAB] = 'Tab'
    rosetta[J_BUNDLE.TAB2] = 'Tab2'
    rosetta[J_BUNDLE.TAB3] = 'Tab3'
# Cars
    rosetta[J_BUNDLE.LOAD] = 'Load'
    rosetta[J_BUNDLE.LOAD_TYPE] = 'Load Type'
    rosetta[J_BUNDLE.HAZARDOUS] = 'Hazardous'
    rosetta[J_BUNDLE.KERNEL] = 'Kernel'
    rosetta[J_BUNDLE.KERNEL_SIZE] = 'Kernel Size'
    rosetta[J_BUNDLE.FINAL_DEST] = 'Final Dest'
    rosetta[J_BUNDLE.FINAL_DEST_TRACK] = 'FD&Track'
    rosetta[J_BUNDLE.DROP_COMMENT] = 'SetOut Msg'
    rosetta[J_BUNDLE.PICKUP_COMMENT] = 'PickUp Msg'
    rosetta[J_BUNDLE.RWE] = 'RWE'
    # rosetta[J_BUNDLE.RWL] = 'RWL'
# Locos
    rosetta[J_BUNDLE.MODEL] = 'Model'
    rosetta[J_BUNDLE.CONSIST] = 'Consist'
# Unique to this plugin
    rosetta['On_Train'] = 'On Train'
    rosetta['Set_To'] = 'Set to'
    rosetta['PUSO'] = 'PUSO'
    rosetta[' '] = ' '

    return rosetta
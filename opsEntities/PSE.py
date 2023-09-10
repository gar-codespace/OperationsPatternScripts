# coding=utf-8
# © 2023 Greg Ritacco

"""
PSE is an abbreviation for Pattern Script Entities.
Support methods and package constants for all Pattern Script subroutines.
"""

import jmri as JMRI
from java import io as JAVA_IO
import java.awt as JAVA_AWT
import java.nio.file as JAVA_NIO
import java.beans as JAVA_BEANS # Called by the listeners
import javax.swing as JAVX_SWING

import logging as LOGGING
import apps as APPS
import time as TIME
from HTMLParser import HTMLParser as HTML_PARSER
from json import loads as jsonLoadS, dumps as jsonDumpS
from codecs import open as codecsOpen

"""
Ghost imports from MainScript:
    PSE.PLUGIN_ROOT = PLUGIN_ROOT
    PSE.SCRIPT_DIR = SCRIPT_DIR
    PSE.JMRI = jmri
    PSE.SYS = sys
    PSE.OS_PATH = OS_PATH
    PSE.BUNDLE = mainScript/handle/Bundle.getBundleForLocale()
    PSE.ENCODING = PSE.readConfigFile('Main Script')['CP']['SE']
Ghost imports from Bundle:
    PSE.BUNDLE_DIR = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle')
"""

PROFILE_PATH = JMRI.util.FileUtil.getProfilePath()
BUNDLE = {}
REPORT_ITEM_WIDTH_MATRIX = {}
TRACK_NAME_CLICKED_ON = ''

"""
The formatting is a little different so don't use this:
J_BUNDLE = JMRI.jmrit.operations.setup.Setup()
"""
SB = JMRI.jmrit.operations.setup.Bundle()

SCRIPT_NAME = 'OperationsPatternScripts.opsEntities.PSE'
SCRIPT_REV = 20230901

OM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.OperationsManager)
PM = JMRI.InstanceManager.getDefault(JMRI.util.gui.GuiLafPreferencesManager)
TM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.trains.TrainManager)
RM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.routes.RouteManager)
LM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.locations.LocationManager)
DM = JMRI.InstanceManager.getDefault(JMRI.jmrit.operations.locations.divisions.DivisionManager)
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

_psLog = LOGGING.getLogger('OPS.OE.PSE')


class Logger:
    """
    Homebrew logging.
    """

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


def makePatternLog():
    """
    creates a pattern log for display based on the log level, as set by getBuildReportLevel.
    Called by:
    MainScript.Controller.logItemSelected
    """

    outputPatternLog = ''
    buildReportLevel = JMRI.jmrit.operations.setup.Setup.getBuildReportLevel()

    loggingIndex = logIndex()
    logLevel = loggingIndex[buildReportLevel]

    fileName = 'PatternScriptsLog.txt'
    targetPath = OS_PATH.join(PROFILE_PATH, 'operations', 'buildstatus', fileName)
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
    """
    Moved here but may be put back into configFile.
    Called by:
    PSE.makePatternLog
    """

    loggingIndex = {"9": "- CRITICAL -", "7": "- ERROR -", "5": "- WARNING -", "3": "- INFO -", "1": "- DEBUG -"}

    return loggingIndex


"""GUI Methods"""


def repaintPatternScriptsWindow():
    """
    Repaints the Pattern Scripts window.
    Called by:
    All Show/Hide pulldowns.
    """

    configFile = readConfigFile()
    frameName = getBundleItem('Pattern Scripts')

    for subroutineName in getSubroutineDirs():
        subroutine = 'Subroutines.' + subroutineName
        targetPanel = getComponentByName(frameName, subroutine)
        targetPanel.setVisible(configFile[subroutineName]['SV'])

    return

def getComponentByName(frameTitle, componentName):
    """
    Gets a frame by title.
    Searches a frame for a component by name.
    Uses crawler() to find a component in a frame.
    """

    global CRAWLER
    CRAWLER = []
    frame = JMRI.util.JmriJFrame.getFrame(frameTitle)

    crawler(frame)

    if len(CRAWLER) == 0:
        print(componentName + ' not found in ' + frameTitle)
        return

    for component in CRAWLER:
        if component.getName() == componentName:
            return component

    return

def crawler(frame):
    """
    Recursively returns all the components in a frame.
    """

    for component in frame.getComponents():
        CRAWLER.append(component)

        crawler(component)

    return

def openSystemConsole():

    console = APPS.SystemConsole.getConsole()
    console.setVisible(readConfigFile('Main Script')['US']['OC'])

    return

def openOutputFrame(message):
    """
    The Script Output Window is used to display critical errors.
    Adds the message to the Script Output window.
    https://groups.io/g/jmriusers/message/33745
    https://groups.io/g/jmriusers/message/33747
    """

    bundle = JMRI.jmrit.jython.Bundle()
    frameName = bundle.handleGetMessage('TitleOutputFrame')
    frame = JMRI.util.JmriJFrame.getFrame(frameName)

    if not frame:
        JMRI.jmrit.jython.JythonWindow().actionPerformed(None)

    frame = JMRI.util.JmriJFrame.getFrame(frameName)

    global CRAWLER
    CRAWLER = []
    crawler(frame)
    for component in CRAWLER:
        if component.getClass() == JAVX_SWING.JTextArea:
           component.text += message + '\n'
           break

    return

def closeWindowByName(windowName):
    """
    Close all the windows of a certain name.
    Called by:
    """

    for frame in JMRI.util.JmriJFrame.getFrameList():
        if frame.getName() == windowName:
            frame.setVisible(False)
            frame.dispose()

    return

def closeWindowByLevel(level):
    """
    Closes a group of windows depending upon the level chosen.
    """

    console = APPS.Bundle().handleGetMessage('TitleConsole')
    patternScripts = getBundleItem('Pattern Scripts')
    trainsTable = JMRI.jmrit.operations.trains.Bundle().handleGetMessage('TitleTrainsTable')
    routesTable = JMRI.jmrit.operations.routes.Bundle().handleGetMessage('TitleRoutesTable')
    locationsTable = JMRI.jmrit.operations.locations.Bundle().handleGetMessage('TitleLocationsTable')

    if level == 1:
        keepTheseWindows = [console, 'PanelPro', patternScripts]

    if level == 2:
        keepTheseWindows = [console, 'PanelPro', patternScripts, locationsTable]

    if level == 3:
        keepTheseWindows = [console, 'PanelPro', patternScripts, routesTable, trainsTable, locationsTable]
    
    for frame in JMRI.util.JmriJFrame.getFrameList():
        if frame.getTitle() in keepTheseWindows:
            continue
        else:
            frame.setVisible(False)
            frame.dispose()

    return

def getPsButton():
    """
    Gets the Pattern Scripts button on the PanelPro frame.
    Called by:
    Listeners.PatternScriptsWindow.windowClosed
    Listeners.PatternScriptsWindow.windowOpened
    """

    buttonSpaceComponents = APPS.Apps.buttonSpace().getComponents()
    for component in buttonSpaceComponents:
        if component.getName() == 'psButton':
            return component
        else:
            return None

def updateWindowParams(window):
    """
    Setting JmriJFrame(True, True) has no effect that I can figure.
    Called by:
    Listeners.PatternScriptsWindow.windowClosing
    """

    configPanel = readConfigFile()
    configPanel['Main Script']['CP'].update({'PH': window.getHeight()})
    configPanel['Main Script']['CP'].update({'PW': window.getWidth()})
    configPanel['Main Script']['CP'].update({'PX': window.getX()})
    configPanel['Main Script']['CP'].update({'PY': window.getY()})
    writeConfigFile(configPanel)

    return


"""Utility Methods"""


def remoteCalls(call):
    """
    'call' is one of the remote calls in each subroutine RemoteCalls module.
    activatedCalls, deactivatedCalls, refreshCalls Etc.
    """

    for subroutine in getSubroutineDirs():
        subroutine = 'Subroutines.' + subroutine
        package = __import__(subroutine, fromlist=['RemoteCalls'], level=-1)
        getattr(package.RemoteCalls, call)()

    return

def psLocale():
    """
    Dealers choice, both work.
    Called by:
    Bundle
    Translaters
    """

    return PM.getLocale().toString()
    # return unicode(PM.getLocale(), ENCODING)

def occuranceTally(listOfOccurances):
    """
    Tally the occurances of a word in a list and return a dictionary.
    Home grown version of collections.Counter.
    Called by:
    ModelEntities.getKernelTally
    ViewEntities.makeTextReportLocations
    o2o.ModelEntities
    """

    dict = {}
    while len(listOfOccurances):
        occurance = listOfOccurances[-1]
        tally = 0
        for i in xrange(len(listOfOccurances) - 1, -1, -1): # run list from bottom up
            if listOfOccurances[i] == occurance:
                tally += 1
                listOfOccurances.pop(i)
        dict[occurance] = tally

    return dict

def locationNameLookup(locationName):
    """
    A default location 'Unreported' is exported by Trainplayer for all RS not on a labeled track.
    This method returns the translated word for 'Unreported'.
    All other locations are passed through.
    """

    if locationName == 'Unreported':
        locationName = getBundleItem('Unreported')

    return locationName

def getAllDivisionNames():
    """
    JMRI sorts the list.
    """

    divisionNames = []
    for item in DM.getDivisionsByNameList():
        divisionNames.append(unicode(item.getName(), ENCODING))

    return divisionNames

def getLocationNamesByDivision():
    """
    Returned list is sorted.
    """

    locationsByDivision = []
    divisionName = readConfigFile()['Patterns']['PD']

    if divisionName == None:
        for location in LM.getList():
            if not location.getDivisionName():
                locationsByDivision.append(location.getName())
    else:
        for location in LM.getList():
            if location.getDivisionName() == divisionName:
                locationsByDivision.append(location.getName())

    return sorted(locationsByDivision)

def getAllLocationNames():
    """
    JMRI sorts the list, returns list of location names.
    Called by:
    o2oSubroutine.Model.Divisionator.assignDivisions
    o2oSubroutine.Model.Trackulator.checkLocations
    """

    locationNames = []
    for item in LM.getLocationsByNameList():
        locationNames.append(unicode(item.getName(), ENCODING))

    return locationNames

def getAllTracks():
    """
    All track objects for all locations.
    Called by:
    o2oSubroutine.Model.RollingStockulator.checkTracks
    o2oSubroutine.Model.RollingStockulator.getAllSpurs
    """

    trackList = []
    for location in LM.getList():
        trackList += location.getTracksByNameList(None)

    return trackList

def getOpsProSettingsItems():
    """
    From JMRI settings, get railroad name, year modeled, and scale.
    """

    items = {}
    scaleRubric = readConfigFile('Main Script')['SR']
    scaleRubric = {sIndex:sScale for sScale, sIndex in scaleRubric.items()}

    OSU = JMRI.jmrit.operations.setup
    scale = scaleRubric[OSU.Setup.getScale()]

    items['YR'] = OSU.Setup.getYearModeled()
    items['LN'] = OSU.Setup.getRailroadName()
    items['SC'] = scale

    return items

def getExtendedRailroadName():
    """
    Returns either the extended railroad name or the JMRI railroad name.
    """

    configFile = readConfigFile()
    OSU = JMRI.jmrit.operations.setup
    
    railroadName = OSU.Setup.getRailroadName()
    if configFile['Main Script']['CP']['EH']:
        railroadName = configFile['Main Script']['LD']['JN']

    return railroadName

def makeCompositRailroadName(layoutDetails):
    """
    Uses configFile['Main Script']['LD'] data to make a composite name for use by OPS subroutines.
    """

    _psLog.debug('makeCompositRailroadName')

    a = ''
    if layoutDetails['OR']:
        a = layoutDetails['OR'] + '\n'

    b = ''
    if layoutDetails['TR']:
        b = layoutDetails['TR'] + '\n'

    c = ''
    if layoutDetails['LO']:
        c = layoutDetails['LO']

    return a + b + c


"""Formatting Methods"""


def validTime(epochTime=0):
    """
    Valid Time, get local time adjusted for time zone and dst.
    Called by:
    o2oSubroutine.ModelImport.TrainPlayerImporter.processFileHeaders
    o2oSubroutine.ModelWorkEvents.jmriManifestConversion.convertHeader
    PatternTracksSubroutine.ModelEntities.initializeReportHeader
    Nov 15, 2022 11:53 AM PST vs Valid 11/15/2022 11:54
    """

    year = getYear()
    time = getTime(epochTime)

    if JMRI.jmrit.operations.setup.Setup.is12hrFormatEnabled():
        return TIME.strftime('Valid %b %d, ' + year + ', %I:%M %p', time)
    else:
        return TIME.strftime('Valid %b %d, ' + year + ', %H:%M', time)

    # return TIME.strftime('%m/%d/%Y %I:%M', TIME.gmtime(epochTime - timeOffset))
    # return TIME.strftime('%a %b %d %Y %I:%M %p %Z', TIME.gmtime(epochTime - timeOffset))
    # return TIME.strftime('%b %d, ' + year + ' %I:%M %p %Z', TIME.gmtime(epochTime - timeOffset))

def timeStamp():
    """
    Returns the time in format: YYYY.MO.DY.24.MN.SC
    Used by Throwback.
    """

    return TIME.strftime('%Y.%m.%d.%H.%M.%S', getTime())

def getTime(epochTime=0):

    if epochTime == 0:
        epochTime = TIME.time()

    if TIME.localtime(epochTime).tm_isdst and TIME.daylight: # If local dst and dst are both 1
        timeOffset = TIME.altzone
    else:
        timeOffset = TIME.timezone # in seconds

    return TIME.gmtime(epochTime - timeOffset)

def getYear():
    """
    Either the current year or the entry in settings: year modeled.
    """

    railroadYear = JMRI.jmrit.operations.setup.Setup.getYearModeled()
    if railroadYear:
        return railroadYear
    else:
        return TIME.strftime('%Y', TIME.gmtime(TIME.time()))

def convertJmriDateToEpoch(jmriTime):
    """
    Example: "date" : "2022-02-26T17:16:17.807+0000"
    Example: "date" : "1915-04-24T20:55:40.227+00:00"
    Called by:
    o2oSubroutine.ModelWorkEvents.jmriManifestConversion.convertHeader
    """
    try:
        epochTime = TIME.mktime(TIME.strptime(jmriTime, "%Y-%m-%dT%H:%M:%S.%f+0000"))
    except ValueError:
        pass
    try:
        epochTime = TIME.mktime(TIME.strptime(jmriTime, "%Y-%m-%dT%H:%M:%S.%f+00:00"))
    except ValueError:
        pass
    

    if TIME.localtime(epochTime).tm_isdst and TIME.daylight: # If local dst and dst are both 1
        epochTime -= TIME.altzone
    else:
        epochTime -= TIME.timezone # in seconds

    return epochTime

def formatText(item, length):
    """
    Truncate each item to its defined length in configFile.json and add a space at the end.
    Called by:
    PatternsSubroutine.ModelEntities.ETC
    """
        
    if len(item) < length:
        xItem = item.ljust(length)
    else:
        xItem = item[:length]

    return xItem + u' '

def getShortLoadType(car):
    """
    Replaces empty and load with E, L, or O for occupied.
    JMRI defines custom load type as empty but default load type as E, hence the 'or' statement.
    Load, Empty, Occupied and Unknown are translated by the bundle.
    Called by:
    o2oSubroutine.ModelWorkEvents
    PatternsSubroutine.Model`
    """

    try: # car is sent in from Patterns
        carObject = CM.getByRoadAndNumber(car[SB.handleGetMessage('Road')], car[SB.handleGetMessage('Number')])
    except KeyError: # car is sent in from JMRI manifest json
        carObject = CM.getByRoadAndNumber(car['road'], car['number'])

    lt =  getBundleItem('Unknown').upper()[0]
    if carObject.getLoadType() == 'empty' or carObject.getLoadType() == 'E':
        lt = getBundleItem('Empty').upper()[0]

    if carObject.getLoadType() == 'load' or carObject.getLoadType() == 'L':
        lt = getBundleItem('Load').upper()[0]

    if carObject.isCaboose() or carObject.isPassenger():
        lt = getBundleItem('Occupied').upper()[0]

    return lt

def makeReportItemWidthMatrix():
    """
    The attribute widths (AW) for each of the rolling stock attributes is defined in the report matrix (RM) of the config file.
    """

    reportMatrix = {}
    attributeWidths = readConfigFile('Patterns')['US']['AW']

    for aKey, aValue in attributeWidths.items():
        try: # Include translated JMRI fields
            reportMatrix[SB.handleGetMessage(aKey)] = aValue
        except: # Include custom OPS fields
            reportMatrix[aKey] = aValue

    global REPORT_ITEM_WIDTH_MATRIX
    REPORT_ITEM_WIDTH_MATRIX = reportMatrix

    return


"""File Handling Methods"""


def makeReportFolders():
    """
    Checks/creates the folders this plugin writes to.
    Used By:
    MainScript.Controller
    """

    opsDirectory = OS_PATH.join(PROFILE_PATH, 'operations')
    directories = ['buildstatus', 'csvManifests', 'csvSwitchLists', 'jsonManifests', 'switchLists', 'manifests']
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
    """
    try/except catches initial read of config file.
    Called by:
    Everything
    """

    try:
        ENCODING
    except UnboundLocalError:
        ENCODING = 'utf-8'

    with codecsOpen(filePath, 'r', encoding=ENCODING) as textWorkFile:
        genericReport = textWorkFile.read()

    return genericReport

def genericWriteReport(filePath, genericReport):
    """
    Called by:
    Everything
    """

    try:
        ENCODING
    except UnboundLocalError:
        ENCODING = 'utf-8'

    with codecsOpen(filePath, 'wb', encoding=ENCODING) as textWorkFile:
        textWorkFile.write(genericReport)

    return

def genericDisplayReport(genericReportPath):
    """
    Called by:
    MainScript.Controller.logItemSelected
    MainScript.Controller.ecItemSelected
    PatternTracksSubroutine.View.trackPatternButton
    PatternTracksSubroutine.ViewSetCarsForm.switchListButton
    """

    targetFile = JAVA_IO.File(genericReportPath)

    JMRI.util.HelpUtil.openWindowsFile(targetFile)
# Does not work on Windows 11
    # JAVA_AWT.Desktop.getDesktop().edit(targetFile)
    # Windows 11 throws error with json file

    return

def loadJson(file):
    """
    Called by:
    Everything
    """

    return jsonLoadS(file)

def dumpJson(file):
    """
    Called by:
    Everything
    """

    return jsonDumpS(file, indent=2, sort_keys=True)


"""Configuration File Methods"""


def validateConfigFile():
    """
    Checks and corrects the configFile.
    """

    configFile = OS_PATH.join(PROFILE_PATH, 'operations', 'configFile.json')
# Does one exist?
    if not JAVA_IO.File(configFile).isFile():
        makeNewConfigFile()
# Is it the right version?
    validateConfigFileVersion()
# Does it have all the needed components?
    validateConfigFileComponents()

    return

def validateConfigFileVersion():
    """
    Checks that the config file is the current version.
    Called by:
    OperationsPatternScripts.MainScript.Model
    """

    fileName = 'OPS.json'
    targetPath = OS_PATH.join(PLUGIN_ROOT, 'opsEntities', fileName)
    validConfigFile = loadJson(genericReadReport(targetPath))
    validVersion = validConfigFile['Main Script']['CP']['RV']
    currentVersion = readConfigFile('Main Script')['CP']['RV']

    if currentVersion == validVersion:
        _psLog.info('The configFile.json file is the correct version')
        return True
    else:
        makeNewConfigFile()

        _psLog.warning('configFile  .json version mismatch')
        return False

def validateConfigFileComponents():
    """
    Checks that each subroutine in the Subroutines folder has a configFile component.
    """

    configFile = readConfigFile()

    for subroutine in getSubroutineDirs():
        try:
            configFile[subroutine]
        except KeyError:
            chunkPath = OS_PATH.join(PLUGIN_ROOT, 'Subroutines', subroutine, 'config.json')
            configChunk = loadJson(genericReadReport(chunkPath))
            configFile[subroutine] = configChunk

    writeConfigFile(configFile)

    return

def getSubroutineDirs():
    """
    Returns a list of subroutine names in the Subroutines directory.
    """

    subroutines = []

    subroutinePath = OS_PATH.join(PLUGIN_ROOT, 'Subroutines')
    dirContents = JAVA_IO.File(subroutinePath).list()

    for item in dirContents:
        dirPath = OS_PATH.join(PLUGIN_ROOT, 'Subroutines', item)
        if JAVA_IO.File(dirPath).isDirectory():
            subroutines.append(item)

    return subroutines

def mergeConfigFiles():
    """
    Implemented in v3?
    """

    return

def readConfigFile(subConfig=None):
    """
    checkConfigFile will return the config file if it's ok or a new one otherwise.
    Called by:
    Everything
    """

    configFile = checkConfigFile()

    if not subConfig:
        return configFile
    else:
        return configFile[subConfig]

def checkConfigFile():

    fileName = 'configFile.json'
    targetPath = OS_PATH.join(PROFILE_PATH, 'operations', fileName)

    try:
        loadJson(genericReadReport(targetPath))
    except:
        makeNewConfigFile()
        print('Exception at: PSE.checkConfigFile')
        print('Using new configFile')

    return loadJson(genericReadReport(targetPath))

def makeNewConfigFile():
    """
    Makes a combined configFile.json from OPS.json and each of the subroutine json files.
    For every subroutine, the chunck of config file is named config.json.
    """

    fileName = 'OPS.json'
    targetPath = OS_PATH.join(PLUGIN_ROOT, 'opsEntities', fileName)
    configFile = loadJson(genericReadReport(targetPath))

    subroutines = getSubroutineDirs()
    for subroutine in subroutines:
        dirPath = OS_PATH.join(PLUGIN_ROOT, 'Subroutines', subroutine)
        if JAVA_IO.File(dirPath).isDirectory():
            chunkPath = OS_PATH.join(PLUGIN_ROOT, 'Subroutines', subroutine, 'config.json')
            configChunk = loadJson(genericReadReport(chunkPath))
            configFile[subroutine] = configChunk

    writeConfigFile(configFile)

    return

def tryConfigFile():
    """
    Try/except catches some user edit mistakes.
    Called by:
    PSE.readConfigFile
    """

    try:
        configFile = getConfigFile()
    except ValueError:
        writeNewConfigFile()
        configFile = getConfigFile()
        _psLog.warning('Defective configFile.json found, new file written')
    except IOError:
        writeNewConfigFile()
        configFile = getConfigFile()
        _psLog.warning('No configFile.json found, new file written')

    return configFile

def getConfigFile():
    """
    Called by:
    tryConfigFile
    """

    fileName = 'configFile.json'
    targetPath = OS_PATH.join(PROFILE_PATH, 'operations', fileName)

    return loadJson(genericReadReport(targetPath))

def writeConfigFile(configFile):
    """
    Called by:
    Everything
    """

    fileName = 'configFile.json'
    targetPath = OS_PATH.join(PROFILE_PATH, 'operations', fileName)
    targetFile = dumpJson(configFile)
    genericWriteReport(targetPath, targetFile)

    return

def writeNewConfigFile():
    """
    Called by:
    PSE.tryConfigFile
    """

    targetDir = OS_PATH.join(PROFILE_PATH, 'operations')
    JAVA_IO.File(targetDir).mkdir()

    fileName = 'configFile.json'

    targetFile = OS_PATH.join(PLUGIN_ROOT, 'opsEntities', fileName)
    copyFrom = JAVA_IO.File(targetFile).toPath()

    targetFile = OS_PATH.join(PROFILE_PATH, 'operations', fileName)
    copyTo = JAVA_IO.File(targetFile).toPath()

    JAVA_NIO.Files.copy(copyFrom, copyTo, JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)

    return

def deleteConfigFile():
    """
    Called by:
    MainScript.Controller.rsItemSelected
    """

    fileName = 'configFile.json'
    targetFile = OS_PATH.join(PROFILE_PATH, 'operations', fileName)
    JAVA_IO.File(targetFile).delete()

    return


"""Color Handling Methods"""


def getSpecificColor(colorName):
    """
    Called by:
    PSE.getCarColor
    PSE.getLocoColor
    PSE.getAlertColor
    """

    colorPalette = readConfigFile('Main Script')['US']['CD']

    r = colorPalette[colorName]["R"]
    g = colorPalette[colorName]["G"]
    b = colorPalette[colorName]["B"]
    a = colorPalette[colorName]["A"]

    return JAVA_AWT.Color(r, g, b, a)

def getColorA():
    """
    Try/Except is a bit of protection against bad edits.
    Called by:
    PatternTracksSubroutine.ViewSetCarsForm.MakeSetCarsEqptRows
    """

    try:
        colorName = readConfigFile('Main Script')['US']['CD']['colorA']
        color = getSpecificColor(colorName)
        return color
    except:
        print('Exception at: PSE.getColorA')
        _psLog.warning('colorA definition not found in configFile.json')
        return JAVA_AWT.Color(0, 0, 0, 0)

def getColorB():
    """
    Try/Except is a bit of protection against bad edits.
    Called by:
    PatternTracksSubroutine.ViewSetCarsForm.MakeSetCarsEqptRows
    """

    try:
        colorName = readConfigFile('Main Script')['US']['CD']['colorB']
        color = getSpecificColor(colorName)
        return color
    except:
        print('Exception at: PSE.getColorB')
        _psLog.warning('colorB definition not found in configFile.json')
        return JAVA_AWT.Color(0, 0, 0, 0)

def getColorC():
    """
    Try/Except is a bit of protection against bad edits.
    Called by:
    PatternTracksSubroutine.ViewSetCarsForm.MakeSetCarsEqptRows
    """

    try:
        colorName = readConfigFile('Main Script')['US']['CD']['colorC']
        color = getSpecificColor(colorName)
        return color
    except:
        print('Exception at: PSE.getColorC')
        _psLog.warning('colorC definition not found in configFile.json')
        return JAVA_AWT.Color(0, 0, 0, 0)


"""Translation Methods"""

def getBundleItem(item):
    """
    Centralized method for translation.
    Retrieves the item from the bundle.
    """

    try:
        return unicode(BUNDLE[item], ENCODING)
    except KeyError:
        return ''


# def translateMessageFormat():
#     """
#     DEPRICATED
#     The messageFormat is in the locale's language, it has to be hashed to the plugin fields.
#     """

#     rosetta = {}
# #Common
#     rosetta[SB.handleGetMessage('Road')] = 'Road'
#     rosetta[SB.handleGetMessage('Number')] = 'Number'
#     rosetta[SB.handleGetMessage('Type')] = 'Type'
#     rosetta[SB.handleGetMessage('Length')] = 'Length'
#     rosetta[SB.handleGetMessage('Color')] = 'Color'
#     rosetta[SB.handleGetMessage('Weight')] = 'Weight'
#     rosetta[SB.handleGetMessage('Comment')] = 'Comment'
#     rosetta[SB.handleGetMessage('Division')] = 'Division'
#     rosetta[SB.handleGetMessage('Location')] = 'Location'
#     rosetta[SB.handleGetMessage('Track')] = 'Track'
#     rosetta[SB.handleGetMessage('Destination')] = 'Destination'
#     rosetta[SB.handleGetMessage('Owner')] = 'Owner'
#     rosetta[SB.handleGetMessage('Tab')] = 'Tab'
#     rosetta[SB.handleGetMessage('Tab2')] = 'Tab2'
#     rosetta[SB.handleGetMessage('Tab3')] = 'Tab3'
# # Locos
#     rosetta[SB.handleGetMessage('Model')] = 'Model'
#     rosetta[SB.handleGetMessage('DCC_Address')] = 'DCC_Address'
#     rosetta[SB.handleGetMessage('Consist')] = 'Consist'
# # Cars
#     rosetta[SB.handleGetMessage('Load_Type')] = 'Load_Type'
#     rosetta[SB.handleGetMessage('Load')] = 'Load'
#     rosetta[SB.handleGetMessage('Hazardous')] = 'Hazardous'
#     rosetta[SB.handleGetMessage('Kernel')] = 'Kernel'
#     rosetta[SB.handleGetMessage('Kernel_Size')] = 'Kernel_Size'
#     rosetta[SB.handleGetMessage('Dest&Track')] = 'Dest&Track'
#     rosetta[SB.handleGetMessage('Final_Dest')] = 'Final_Dest'
#     rosetta[SB.handleGetMessage('Track')] = 'FD&Track'
#     rosetta[SB.handleGetMessage('SetOut_Msg')] = 'SetOut_Msg'
#     rosetta[SB.handleGetMessage('PickUp_Msg')] = 'PickUp_Msg'
#     rosetta[SB.handleGetMessage('RWE')] = 'RWE'
#     # rosetta[J_BUNDLE.RWL] = 'RWL'
# # Unique to this plugin
#     rosetta['onTrain'] = 'onTrain'
#     rosetta['setTo'] = 'setTo'
#     rosetta['puso'] = 'puso'
#     rosetta[' '] = ' '

#     return rosetta

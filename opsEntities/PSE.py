# coding=utf-8
# © 2023 Greg Ritacco

"""
PSE is an abbreviation for Pattern Script Entities.
Support methods, functions and package constants for all Pattern Script subroutines.
"""

import jmri as JMRI
from java import io as JAVA_IO
import java.awt as JAVA_AWT
import java.nio.file as JAVA_NIO
import javax.swing as JAVX_SWING
import java.beans as JAVA_BEANS # Called by the listeners
from importlib import import_module as IM # Called by the listeners

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
    PSE.SUBROUTINE_DIR = 'Subroutines_Activated'
    PSE.JMRI = jmri
    PSE.SYS = sys
    PSE.OS_PATH = OS_PATH
    PSE.BUNDLE = mainScript/handle/Bundle.getBundleForLocale()
    PSE.ENCODING = PSE.readConfigFile('Main Script')['CP']['SE']
Ghost imports from Bundle:
    PSE.BUNDLE_DIR = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle')
Ghost import from Scanner
    PSE.SEQUENCE_HASH = PSE.loadJson(PSE.genericReadReport(sequenceFilePath))
"""

SCRIPT_NAME = 'OperationsPatternScripts.opsEntities.PSE'
SCRIPT_REV = 20231001
PROFILE_PATH = JMRI.util.FileUtil.getProfilePath()
BUNDLE = {}
REPORT_ITEM_WIDTH_MATRIX = {}
ROSETTA = {}
TRACK_NAME_CLICKED_ON = ''

# Don't use this: J_BUNDLE = JMRI.jmrit.operations.setup.Setup()
SB = JMRI.jmrit.operations.setup.Bundle()

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

    loggingIndex = _logIndex()

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

def _logIndex():
    """
    Helper function for makePatternLog()
    Moved here but may be put back into configFile.
    """

    loggingIndex = {"9": "- CRITICAL -", "7": "- ERROR -", "5": "- WARNING -", "3": "- INFO -", "1": "- DEBUG -"}

    return loggingIndex


"""Translation Functions"""


def getBundleItem(item):
    """
    Centralized function for translation.
    Retrieves the item from the bundle.
    """

    try:
        return unicode(BUNDLE[item], ENCODING)
    except KeyError:
        return ''


"""GUI Functions"""


class ListenToThePSWindow(JAVA_BEANS.PropertyChangeListener):
    """
    Listens for changes to the Pattern Scripts plugin window.
    This should be attached to any windows this plugin may open.
    PSE.LM.addPropertyChangeListener(PSE.ListenToThePSWindow(frame))
    """

    def __init__(self, frame):

        self.frame = frame

        return

    def propertyChange(self, PROPERTY_CHANGE_EVENT):
    
        if PROPERTY_CHANGE_EVENT.propertyName == 'windowOpened':

            pass

        if PROPERTY_CHANGE_EVENT.propertyName == 'windowActivated':
            
            pass

        if PROPERTY_CHANGE_EVENT.propertyName == 'windowClosing':

            self.frame.setVisible(False)
            self.frame.dispose()
            
            _psLog.debug('Window closed: ' + self.frame.getTitle())
            
        return

def removePSPropertyListeners():
    """
    Every subroutine attaches a property change listener to PSE.LM to monitor the PS window status.
    This method removes all of them.
    """

    for listener in LM.getPropertyChangeListeners():
        if isinstance(listener, JAVA_BEANS.PropertyChangeListener) and 'ListenToThePSWindow' in listener.toString():
            LM.removePropertyChangeListener(listener)

            print('PSE.removePSWindowListener')
            _psLog.debug('PSE.removePSWindowListener')

    return

def removePSWindowListeners():
    """
    Removea all window listener types from the Pattern Scripts window.
    """

    frameName = getBundleItem('Pattern Scripts')
    frame = JMRI.util.JmriJFrame.getFrame(frameName)

    for listener in frame.getWindowListeners():
        frame.removeWindowListener(listener)
    for listener in frame.getWindowFocusListeners():
        frame.removeWindowFocusListener(listener)
    for listener in frame.getWindowStateListeners():
        frame.removeWindowStateListener(listener)

    return

def repaintPatternScriptsFrame():
    """
    Repaints the Pattern Scripts window.
    """

    configFile = readConfigFile()
    frameName = getBundleItem('Pattern Scripts')

    for subroutineName in getSubroutineDirs():
        subroutine = SUBROUTINE_DIR + '.' + subroutineName
        targetPanel = getComponentByName(frameName, subroutine)
        targetPanel.setVisible(configFile[subroutineName]['SV'])

    return

def getComponentByName(frameTitle, componentName):
    """
    Gets a frame by title.
    Searches a frame for a component by name.
    Uses crawler() to find a component in a frame.
    Assumes that each component has a unique name.
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
        JMRI.jmrit.jython.JythonWindow().actionPerformed(None) # This command opens the frame

    frame = JMRI.util.JmriJFrame.getFrame(frameName)
    LM.addPropertyChangeListener(ListenToThePSWindow(frame))

    global CRAWLER
    CRAWLER = []
    crawler(frame)
    for component in CRAWLER:
        if component.getClass() == JAVX_SWING.JTextArea:
           component.text += '{}\n'.format(message)
           break

    return

def closeWindowByName(windowName):
    """
    Close all the windows of a certain name.
    """

    for frame in JMRI.util.JmriJFrame.getFrameList():
        if frame.getName() == windowName:
            frame.setVisible(False)
            frame.dispose()

    return

def closeWindowByLevel(level=None):
    """
    Closes a group of windows depending upon the level chosen.
    """

    console = APPS.Bundle().handleGetMessage('TitleConsole')
    patternScripts = getBundleItem('Pattern Scripts')
    trainsTable = JMRI.jmrit.operations.trains.Bundle().handleGetMessage('TitleTrainsTable')
    routesTable = JMRI.jmrit.operations.routes.Bundle().handleGetMessage('TitleRoutesTable')
    locationsTable = JMRI.jmrit.operations.locations.Bundle().handleGetMessage('TitleLocationsTable')

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
    """

    configPanel = readConfigFile()
    configPanel['Main Script']['CP'].update({'PH': window.getHeight()})
    configPanel['Main Script']['CP'].update({'PW': window.getWidth()})
    configPanel['Main Script']['CP'].update({'PX': window.getX()})
    configPanel['Main Script']['CP'].update({'PY': window.getY()})
    writeConfigFile(configPanel)

    return


"""Utility Functions"""


def psLocale():
    """
    Dealers choice, both work.
    """

    return PM.getLocale().toString()
    # return unicode(PM.getLocale(), ENCODING)

def occuranceTally(listOfOccurances):
    """
    Tally the occurances of a word in a list and return a dictionary.
    Home grown version of collections.Counter.
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

def getAllDivisionNames():
    """
    JMRI sorts the list.
    """

    divisionNames = []
    for item in DM.getDivisionsByNameList():
        divisionNames.append(unicode(item.getName(), ENCODING))

    return divisionNames

# def getLocationNamesByDivision(divisionName):
#     """
#     Returned list is sorted.
#     """

#     locationsByDivision = []
#     # divisionName = readConfigFile()['Patterns']['PD']

#     if divisionName == None:
#         for location in LM.getList():
#             if not location.getDivisionName():
#                 locationsByDivision.append(location.getName())
#     else:
#         for location in LM.getList():
#             if location.getDivisionName() == divisionName:
#                 locationsByDivision.append(location.getName())

#     return sorted(locationsByDivision)

def getAllLocationNames():
    """
    JMRI sorts the list, returns list of location names.
    """

    locationNames = []
    for item in LM.getLocationsByNameList():
        locationNames.append(unicode(item.getName(), ENCODING))

    return locationNames

# def getAllTracks():
#     """
#     All track objects for all locations.
#     Called by:
#     o2oSubroutine.Model.RollingStockulator.checkTracks
#     o2oSubroutine.Model.RollingStockulator.getAllSpurs
#     """

#     trackList = []
#     for location in LM.getList():
#         trackList += location.getTracksByNameList(None)

#     return trackList

# def getOpsProSettingsItems():
#     """
#     From JMRI settings, get railroad name, year modeled, and scale.
#     """

#     items = {}
#     scaleRubric = readConfigFile('Main Script')['SR']
#     scaleRubric = {sIndex:sScale for sScale, sIndex in scaleRubric.items()}

#     OSU = JMRI.jmrit.operations.setup
#     scale = scaleRubric[OSU.Setup.getScale()]

#     items['YR'] = OSU.Setup.getYearModeled()
#     items['LN'] = OSU.Setup.getRailroadName()
#     items['SC'] = scale

#     return items

def makeCompositRailroadName(layoutDetails):
    """
    Uses configFile['Main Script']['LD'] data to make a composite name for use by OPS subroutines.
    """

    _psLog.debug('PSE.makeCompositRailroadName')

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

def getNewestTrain():
    """
    If more than 1 train is built, pick the newest one.
    Returns a train object.
    """

    _psLog.debug('findNewestTrain')

    if not TM.isAnyTrainBuilt():
        return None

    newestBuildTime = ''
    for train in [train for train in TM.getTrainsByStatusList() if train.isBuilt()]:
        trainManifest = JMRI.jmrit.operations.trains.JsonManifest(train).getFile()
        trainManifest = JMRI.util.FileUtil.readFile(trainManifest)
        testDate = loadJson(trainManifest)['date']
        if testDate > newestBuildTime:
            newestBuildTime = testDate
            newestTrain = train

    return newestTrain

def getTrainManifest(train):

    trainName = 'train-{}.json'.format(train.toString())
    manifestPath = OS_PATH.join(PROFILE_PATH, 'operations', 'jsonManifests', trainName)
    manifest = loadJson(genericReadReport(manifestPath))

    return manifest

# def saveManifest(manifest, train):

#     trainName = 'train-{}.json'.format(train.toString())
#     manifestPath = OS_PATH.join(PROFILE_PATH, 'operations', 'jsonManifests', trainName)
#     genericWriteReport(manifestPath, dumpJson(manifest))

#     return

# def getOpsSwitchList():

#     trainName = '{}.json'.format(getBundleItem('ops-Switch List'))
#     manifestPath = OS_PATH.join(PROFILE_PATH, 'operations', 'jsonManifests', trainName)
#     manifest = loadJson(genericReadReport(manifestPath))

#     return manifest


"""Formatting Functions"""


# def isoValidTime(timeStamp):
#     """
#     Input the JMRI generated iso time stamp.
#     Return format: Valid Oct 08, 1915, 11:11
#     """

#     valid = getBundleItem('Valid') + ' ' + JMRI.jmrit.operations.trains.TrainCommon.getDate(True)

#     return valid

def convertIsoToValidTime(isoDate):
    """
    Convert ISO time generated by JMRI or OPS into the JMRI standard date time.
    Example: "date" : "2022-02-26T17:16:17.807+0000"
    """

    epochTime = _convertIsoTimeToEpoch(isoDate)

    return _validTime(epochTime)

def _convertIsoTimeToEpoch(isoTime):
    """
    Helper function for convertIsoToValidTime()
    """
    try:
        epochTime = TIME.mktime(TIME.strptime(isoTime, "%Y-%m-%dT%H:%M:%S.%f+0000"))
    except ValueError:
        pass
    try:
        epochTime = TIME.mktime(TIME.strptime(isoTime, "%Y-%m-%dT%H:%M:%S.%f+00:00"))
    except ValueError:
        pass
    

    if TIME.localtime(epochTime).tm_isdst and TIME.daylight: # If local dst and dst are both 1
        epochTime -= TIME.altzone
    else:
        epochTime -= TIME.timezone # in seconds

    return epochTime

def _validTime(epochTime=0):
    """
    Helper function for convertIsoToValidTime()
    Get local time adjusted for time zone and dst.
    Uses calander or railroad year.
    Valid 11/15/2022 11:54
    """

    valid = getBundleItem('Valid')
    year = _getYear()
    time = _getTime(epochTime)

    if JMRI.jmrit.operations.setup.Setup.is12hrFormatEnabled():
        return TIME.strftime(valid + ' %m/%d/' + year + ' %I:%M %p', time)
    else:
        return TIME.strftime(valid + ' %m/%d/' + year + ' %H:%M', time)

def _getYear():
    """
    Helper function for convertIsoToValidTime()
    Either the current year or the entry in settings: year modeled.
    """

    railroadYear = JMRI.jmrit.operations.setup.Setup.getYearModeled()
    if railroadYear:
        return railroadYear
    else:
        return TIME.strftime('%Y', TIME.gmtime(TIME.time()))

def _getTime(epochTime=0):
    """
    Helper function for convertIsoToValidTime()
    """

    if epochTime == 0:
        epochTime = TIME.time()

    if TIME.localtime(epochTime).tm_isdst and TIME.daylight: # If local dst and dst are both 1
        timeOffset = TIME.altzone
    else:
        timeOffset = TIME.timezone # in seconds

    return TIME.gmtime(epochTime - timeOffset)

def isoTimeStamp():
    """
    Returns the iso8601 format time stamp adjusted for model year.
    """

    bool = False
    if JMRI.jmrit.operations.setup.Setup.getYearModeled():
        bool = True

    return JMRI.jmrit.operations.trains.TrainCommon.getISO8601Date(bool)

# def timeStamp():
#     """
#     Returns the time in format: YYYY.MO.DY.24.MN.SC
#     Used by Throwback.
#     """

#     return TIME.strftime('%Y.%m.%d.%H.%M.%S', getTime())

def findLongestStringLength(list):
    """
    list is a list or tuple of strings.
    Returns the length of the longest string.
    """

    longestString = 0

    for string in list:
        longestString = max(longestString, len(string))

    return longestString

def extendManifest(reportName):
    """
    Adds additional attributes found in the print options dialog.
    Called by Patterns, jPlus and Scanner
    """

    reportPath = OS_PATH.join(PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = loadJson(genericReadReport(reportPath))
    for location in report['locations']:
        # Engines
        for loco in location['engines']['add']:
            locoObject = EM.getByRoadAndNumber(loco['road'], loco['number'])
            loco['dccAddress'] = locoObject.getDccAddress()
        for loco in location['engines']['remove']:
            locoObject = EM.getByRoadAndNumber(loco['road'], loco['number'])
            loco['dccAddress'] = locoObject.getDccAddress()
        # Cars
        for car in location['cars']['add']:
            carObject = CM.getByRoadAndNumber(car['road'], car['number'])
            kSize = 0
            kernelName = carObject.getKernelName()
            if kernelName:
                kSize = KM.getKernelByName(kernelName).getSize()
            car['kernelSize'] = kSize
            car['finalDestination']={'userName':carObject.getFinalDestinationName(), 'track':{'userName':carObject.getFinalDestinationTrackName()}}
            car['loadType'] = carObject.getLoadType()
            car['division'] = LM.getLocationByName(car['location']['userName']).getDivisionName()

        for car in location['cars']['remove']:
            carObject = CM.getByRoadAndNumber(car['road'], car['number'])
            kSize = 0
            kernelName = carObject.getKernelName()
            if kernelName:
                kSize = KM.getKernelByName(kernelName).getSize()
            car['kernelSize'] = kSize
            car['finalDestination']={'userName':carObject.getFinalDestinationName(), 'track':{'userName':carObject.getFinalDestinationTrackName()}}
            car['loadType'] = carObject.getLoadType()
            car['division'] = LM.getLocationByName(car['location']['userName']).getDivisionName()

    genericWriteReport(reportPath, dumpJson(report))

    return


"""File Handling Functions"""


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
    Called by everything
    """

    try:
        ENCODING
    except UnboundLocalError:
        ENCODING = 'utf-8'

    with codecsOpen(filePath, 'wb', encoding=ENCODING) as textWorkFile:
        textWorkFile.write(genericReport)

    return

def genericDisplayReport(genericReportPath):

    targetFile = JAVA_IO.File(genericReportPath)

    JMRI.util.HelpUtil.openWindowsFile(targetFile)
# Windows 11 throws error with json file
    # JAVA_AWT.Desktop.getDesktop().edit(targetFile)

    return

def loadJson(file):
    """
    Called by everything
    """

    return jsonLoadS(file)

def dumpJson(file):
    """
    Called by everything
    """

    return jsonDumpS(file, indent=2, sort_keys=True)


"""Configuration File Functions"""


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
            chunkPath = OS_PATH.join(PLUGIN_ROOT, 'Subroutines_Activated', subroutine, 'config.json')
            configChunk = loadJson(genericReadReport(chunkPath))
            configFile[subroutine] = configChunk

    writeConfigFile(configFile)

    return

def getSubroutineDirs():
    """
    Returns a list of subroutine names in the Subroutines_Activated directory.
    """

    subroutines = []

    subroutinePath = OS_PATH.join(PLUGIN_ROOT, 'Subroutines_Activated')
    dirContents = JAVA_IO.File(subroutinePath).list()

    for item in dirContents:
        dirPath = OS_PATH.join(PLUGIN_ROOT, 'Subroutines_Activated', item)
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
    Called by everything.
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
        dirPath = OS_PATH.join(PLUGIN_ROOT, 'Subroutines_Activated', subroutine)
        if JAVA_IO.File(dirPath).isDirectory():
            chunkPath = OS_PATH.join(PLUGIN_ROOT, 'Subroutines_Activated', subroutine, 'config.json')
            configChunk = loadJson(genericReadReport(chunkPath))
            configFile[subroutine] = configChunk

    writeConfigFile(configFile)

    return

def tryConfigFile():
    """
    Try/except catches some user edit mistakes.
    """

    try:
        configFile = _getConfigFile()
    except ValueError:
        _writeNewConfigFile()
        configFile = _getConfigFile()
        _psLog.warning('Defective configFile.json found, new file written')
    except IOError:
        _writeNewConfigFile()
        configFile = _getConfigFile()
        _psLog.warning('No configFile.json found, new file written')

    return configFile

def _getConfigFile():
    """
    Helper function for tryConfigFile()
    """

    fileName = 'configFile.json'
    targetPath = OS_PATH.join(PROFILE_PATH, 'operations', fileName)

    return loadJson(genericReadReport(targetPath))

def _writeNewConfigFile():
    """
    Helper function for tryConfigFile()
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

def writeConfigFile(configFile):
    """
    Called by everything.
    """

    fileName = 'configFile.json'
    targetPath = OS_PATH.join(PROFILE_PATH, 'operations', fileName)
    targetFile = dumpJson(configFile)
    genericWriteReport(targetPath, targetFile)

    return

def deleteConfigFile():

    fileName = 'configFile.json'
    targetFile = OS_PATH.join(PROFILE_PATH, 'operations', fileName)
    JAVA_IO.File(targetFile).delete()

    return


"""Color Handling Functions"""


def getColorA():
    """
    Try/Except is a bit of protection against bad edits.
    Called by:
    PatternTracksSubroutine.ViewSetCarsForm.MakeSetCarsEqptRows
    """

    try:
        colorName = readConfigFile('Main Script')['US']['CD']['colorA']
        color = _getSpecificColor(colorName)
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
        color = _getSpecificColor(colorName)
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
        color = _getSpecificColor(colorName)
        return color
    except:
        print('Exception at: PSE.getColorC')
        _psLog.warning('colorC definition not found in configFile.json')
        return JAVA_AWT.Color(0, 0, 0, 0)

def _getSpecificColor(colorName):
    """
    Helper function for getColor<>()
    """

    colorPalette = readConfigFile('Main Script')['US']['CD']

    r = colorPalette[colorName]["R"]
    g = colorPalette[colorName]["G"]
    b = colorPalette[colorName]["B"]
    a = colorPalette[colorName]["A"]

    return JAVA_AWT.Color(r, g, b, a)

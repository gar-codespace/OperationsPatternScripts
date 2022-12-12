# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
PSE is an abbreviation for Pattern Script Entities.
Support methods and package constants for all Pattern Script subroutines.
"""

import jmri as JMRI
import logging as LOGGING
from java import io as JAVA_IO
import java.nio.file as JAVA_NIO
import java.beans as JAVA_BEANS
from HTMLParser import HTMLParser as HTML_PARSER
import apps as APPS

from json import loads as jsonLoadS, dumps as jsonDumpS
from codecs import open as codecsOpen

"""
Ghost imports from MainScript:
    PSE.PLUGIN_ROOT = PLUGIN_ROOT
    PSE.JMRI = jmri
    PSE.SYS = sys
    PSE.OS_PATH = OS_PATH
    PSE.JAVA_AWT = java.awt
    PSE.JAVX_SWING = javax.swing
    PSE.TIME = time
    PSE.ENCODING = PSE.readConfigFile('CP')['SE']
Ghost imports from PSE
    buildThePlugin().BUNDLE = mainScript.Bundle.getBundleForLocale()
"""

PROFILE_PATH = JMRI.util.FileUtil.getProfilePath()
BUNDLE = {}
REPORT_ITEM_WIDTH_MATRIX = {}
TRACK_NAME_CLICKED_ON = ''
CRAWLER = []

# Dealers choice, both work OK:
J_BUNDLE = JMRI.jmrit.operations.setup.Setup()
# SB = JMRI.jmrit.operations.setup.Bundle()
# SB.handleGetMessage('Road')

SCRIPT_NAME = 'OperationsPatternScripts.opsEntities.PSE'
SCRIPT_REV = 20221010

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

        self.stubLocation = OS_PATH.join(JMRI.util.FileUtil.getPreferencesPath(), 'jmrihelp', psLocale()[:2])

        self.helpFilePath = ''
        self.newStubFile = ''

        return

    def validateStubLocation(self):

        if JAVA_IO.File(self.stubLocation).mkdirs():
            _psLog.info('Stub location created at: ' + self.stubLocation)
        else:
            _psLog.info('Stub location already exists')

        return

    def getHelpFileURI(self):

        helpFileName = 'help.' + psLocale()[:2] + '.html'
        helpFilePath = OS_PATH.join(PLUGIN_ROOT, 'opsSupport', helpFileName)

        if not JAVA_IO.File(helpFilePath).isFile():
            helpFileName = 'help.en.html'
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

        _psLog.debug('CreateStubFile.writeStubFile')

        stubFilePath = OS_PATH.join(self.stubLocation, 'psStub.html')

        genericWriteReport(stubFilePath, self.newStubFile)

        return

    def make(self):
        """Mini controller guides the new stub file process."""

        self.validateStubLocation()
        self.getHelpFileURI()
        self.makeNewStubFile()
        self.writeStubFile()

        return


"""GUI Methods"""


def closePsWindow():
    """Called by:
        Listeners.ptItemSelected
        Listeners.rsItemSelected
        """

    frameName = BUNDLE['Pattern Scripts']
    window = JMRI.util.JmriJFrame.getFrame(frameName)

    if window:
        updateWindowParams(window)
        window.setVisible(False)
        window.dispose()

    closeSetCarsWindows()

    return

def updateYearModeled():
    """Called by:
        Listeners.PatternScriptsWindow
        """

    configFile = readConfigFile()

    OSU = JMRI.jmrit.operations.setup
    yr = OSU.Setup.getYearModeled()
    
    configFile['JP'].update({'YR':yr})
    writeConfigFile(configFile)

    return

def buildThePlugin():
    """Called by:
        jPlusSubroutine.Listeners
        o2oSubroutine.Listeners
        opsEntities.Listeners.patternScriptsButtonAction
        opsEntities.Listeners.ptItemSelected
        opsEntities.Listeners.rsItemSelected
        PatternTracksSubroutine.Listeners
        """

    # mainScript = __import__('MainScript')
    mainScript = __import__('MainScript', globals(), locals(), [], 0)

    global BUNDLE
    BUNDLE = mainScript.Bundle.getBundleForLocale()

    CreateStubFile().make()
    mainScript.Bundle.makeHelpPage()

    view = mainScript.View()
    emptyPluginPanel = view.makePluginPanel()
    populatedPluginPanel = view.makePatternScriptsPanel(emptyPluginPanel)
    scrollPanel = view.makeScrollPanel(populatedPluginPanel)
    view.makePatternScriptsWindow(scrollPanel)
    menuItemList = view.getPsPluginMenuItems()

    for menuItem in menuItemList:
        menuItem.addActionListener(getattr(mainScript.Listeners, menuItem.getName()))

    return

def restartSubroutineByName(subRoutineName):
    """Finds the named subroutine in the plugin and restarts it."""

    frameName = BUNDLE['Pattern Scripts']
    frame = getComponentByName(frameName, subRoutineName)
    if frame:
        frame = frame.getComponents()[0] 
        reStart = __import__(subRoutineName, globals(), locals(), ['Controller'], 0)
        reStart.Controller.restartSubroutine(frame)
        print('Restarted: ' + subRoutineName)
    else:
        print('Not currently active: ' + subRoutineName)
    return

def getComponentByName(frameName, componentName):
    """Uses crawler() to find a component in a frame."""
 
    frame = JMRI.util.JmriJFrame.getFrame(frameName)

    crawler(frame)

    if len(CRAWLER) == 0:
        print(componentName + ' not found in ' + frameName)
        return

    for component in CRAWLER:
        if component.getName() == componentName:
            return component
            global CRAWLER
            CRAWLER = []

    return

def crawler(frame):
    """Recursively returns all the components in a frame."""

    for component in frame.getComponents():
        CRAWLER.append(component)

        crawler(component)

    return

def openSystemConsole():

    console = APPS.SystemConsole.getConsole()
    console.setVisible(readConfigFile()['CP']['OC'])

    return

def openOutputFrame(message):
    """The Script Output Window is used to display critical errors.
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

def closeOutputFrame():

    bundle = JMRI.jmrit.jython.Bundle()
    frameName = bundle.handleGetMessage('TitleOutputFrame')
    frame = JMRI.util.JmriJFrame.getFrame(frameName)

    if frame:
        frame.setVisible(False)
        frame.dispose()

    return

def closeTroublesomeWindows():
    """Close all the 'Troublesome' windows when the o2o New JMRI Railroad button is pressed.
        Called by:
        o2oSubroutine.Model.newJmriRailroad
        o2oSubroutine.Model.updateJmriRailroad
        """

    console = APPS.Bundle().handleGetMessage('TitleConsole')
    patternScripts = BUNDLE['Pattern Scripts']
    trainsTable = JMRI.jmrit.operations.trains.Bundle().handleGetMessage('TitleTrainsTable')
    routesTable = JMRI.jmrit.operations.routes.Bundle().handleGetMessage('TitleRoutesTable')

    keepTheseWindows = [console, 'PanelPro', patternScripts, routesTable, trainsTable]
    
    for frame in JMRI.util.JmriJFrame.getFrameList():
        if frame.getTitle() in keepTheseWindows:
            continue
        else:
            frame.setVisible(False)
            frame.dispose()

    return

def getPsButton():
    """Gets the Pattern Scripts button on the PanelPro frame.
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

def closeSetCarsWindows():
    """Close all the Set Cars windows when the Pattern Scripts window is closed.
        Called by:
        MainScript.Controller.closePsWindow
        Listeners.PatternScriptsWindow.windowClosing
        """

    for frame in JMRI.util.JmriJFrame.getFrameList():
        if frame.getName() == 'setCarsWindow':
            frame.setVisible(False)
            frame.dispose()

    return

def updateWindowParams(window):
    """Setting JmriJFrame(True, True) has no effect that I can figure.
        Called by:
        MainScript.Controller.closePsWindow
        Listeners.PatternScriptsWindow.windowClosing
        """

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
        Called by:
        Bundle
        Translaters
        """

    return PM.getLocale().toString()
    # return unicode(PM.getLocale(), ENCODING)

def occuranceTally(listOfOccurances):
    """Tally the occurances of a word in a list and return a dictionary.
        Home grown version of collections.Counter.
        Called by:
        ModelEntities.getKernelTally
        ViewEntities.makeTextReportLocations
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

def jPlusHeader():
    """Called by:
        makeGenericHeader
        """

    configFile = readConfigFile()
    detailedHeader = ''

    operatingRoad = configFile['JP']['OR']
    if not operatingRoad:
        OSU = JMRI.jmrit.operations.setup
        operatingRoad = unicode(OSU.Setup.getRailroadName(), ENCODING)

    # patternDivision = configFile['PT']['PD']
    # if patternDivision:
    #     detailedHeader += operatingRoad + ' - ' + patternDivision
    # else:
    #     detailedHeader += operatingRoad

    detailedHeader += operatingRoad
    if configFile['JP']['TR']:
        detailedHeader += ';' + configFile['JP']['TR']

    if configFile['JP']['LO']:
        detailedHeader += ';' + configFile['JP']['LO']

    return detailedHeader

def getAllDivisionNames():
    """JMRI sorts the list.
        Called by:
        Model.updatePatternLocation
        """

    divisionNames = []
    for item in DM.getDivisionsByNameList():
        divisionNames.append(unicode(item.getName(), ENCODING))

    return divisionNames

def getLocationNamesByDivision(divisionName):

    locationsByDivision = []

    for locationName in getAllLocationNames():
        if LM.getLocationByName(locationName).getDivisionName() == divisionName:
            locationsByDivision.append(locationName)

    return locationsByDivision

def getAllLocationNames():
    """JMRI sorts the list, returns list of location names.
        Called by:
        o2o.Model.UpdateLocationsAndTracks
        PSE.getAllTrackIds
        Model.updatePatternLocation
        Model.updateLocations
        ModelEntities.testSelectedItem
        o2oSubroutine.Model.UpdateLocationsAndTracks.addNewLocations
        """

    locationNames = []
    for item in LM.getLocationsByNameList():
        locationNames.append(unicode(item.getName(), ENCODING))

    return locationNames

def getAllTracks():
    """All track objects for all locations.
        Called by:
        Model.UpdateLocationsAndTracks
        ModelEntities.setNonSpurTrackLength
        Model.updatePatternLocation
        """

    trackList = []
    for location in LM.getList():
        trackList += location.getTracksByNameList(None)

    return trackList

def getSelectedTracks():
    """Gets the track objects checked in the Track Pattern Subroutine.
        Called by:
        Controller.StartUp.trackPatternButton
        ModelEntities.makeTrackPattern
        View.setRsButton
        """

    patternTracks = readConfigFile('PT')['PT']

    return [track for track, include in sorted(patternTracks.items()) if include]

def getTracksNamesByLocation(trackType):
    """Called by:
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
    """Valid Time, get local time adjusted for time zone and dst.
        Called by:
        o2oSubroutine.ModelImport.TrainPlayerImporter.processFileHeaders
        o2oSubroutine.ModelWorkEvents.jmriManifestConversion.convertHeader
        PatternTracksSubroutine.ModelEntities.makeGenericHeader
        Nov 15, 2022 11:53 AM PST vs Valid 11/15/2022 11:54
        """

    year = getYear()

    if epochTime == 0:
        epochTime = TIME.time()
    if TIME.localtime(epochTime).tm_isdst and TIME.daylight: # If local dst and dst are both 1
        timeOffset = TIME.altzone
    else:
        timeOffset = TIME.timezone # in seconds

    if JMRI.jmrit.operations.setup.Setup.is12hrFormatEnabled():
        return TIME.strftime('Valid %b %d, ' + year + ', %I:%M %p', TIME.gmtime(epochTime - timeOffset))
    else:
        return TIME.strftime('Valid %b %d, ' + year + ', %H:%M', TIME.gmtime(epochTime - timeOffset))


    # return TIME.strftime('%m/%d/%Y %I:%M', TIME.gmtime(epochTime - timeOffset))
    # return TIME.strftime('%a %b %d %Y %I:%M %p %Z', TIME.gmtime(epochTime - timeOffset))
    # return TIME.strftime('%b %d, ' + year + ' %I:%M %p %Z', TIME.gmtime(epochTime - timeOffset))

def getYear():
    """Either the current year or the entry in settings: year modeled."""

    railroadYear = JMRI.jmrit.operations.setup.Setup.getYearModeled()
    if railroadYear:
        return railroadYear
    else:
        return TIME.strftime('%Y', TIME.gmtime(TIME.time()))

def convertJmriDateToEpoch(jmriTime):
    """Example: 2022-02-26T17:16:17.807+0000
        Called by:
        o2oSubroutine.ModelWorkEvents.jmriManifestConversion.convertHeader
        """

    epochTime = TIME.mktime(TIME.strptime(jmriTime, "%Y-%m-%dT%H:%M:%S.%f+0000"))

    if TIME.localtime(epochTime).tm_isdst and TIME.daylight: # If local dst and dst are both 1
        epochTime -= TIME.altzone
    else:
        epochTime -= TIME.timezone # in seconds

    return epochTime

def formatText(item, length):
    """Truncate each item to its defined length in PatternConfig.json and add a space at the end.
        Called by:
        PatternTracksSubroutine.ViewEntities.merge
        PatternTracksSubroutine.ViewEntities.loopThroughRs
        """

    if isinstance(item, bool): # Hazardous is a boolean
        item = 'HazMat'
    if len(item) < length:
        xItem = item.ljust(length)
    else:
        xItem = item[:length]

    return xItem + u' '

def makeReportItemWidthMatrix():
    """The attribute widths (AW) for each of the rolling stock attributes is defined in the report matrix (RM) of the config file.
        Called by:
        PatternTracksSubroutine.Controller.StartUp.trackPatternButton
        PatternTracksSubroutine.Controller.StartUp.setRsButton
        PatternTracksSubroutine.ControllerSetCarsForm.CreateSetCarsFormGui.switchListButton
        PatternTracksSubroutine.ControllerSetCarsForm.CreateSetCarsFormGui.setRsButton
        """

    reportMatrix = {}
    attributeWidths = readConfigFile('RM')['AW']

    for aKey, aValue in attributeWidths.items():
        reportMatrix[aKey] = aValue

    return reportMatrix

def getShortLoadType(car):
    """Replaces empty and load with E, L, or O for occupied.
        JMRI defines custom load type as empty but default load type as Empty, hence the 'or' statement.
        Load, Empty, Occupied and Unknown are translated by the bundle.
        Called by:
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


def getTpRailroadJson(reportName):
    """Any of the TP exports imported into JMRI as a json file:
        tpRailroadData
        tpRollingStockData
        tpLocaleData
        """

    fileName = reportName + '.json'
    targetPath = OS_PATH.join(PROFILE_PATH, 'operations', fileName)

    if not JAVA_IO.File(targetPath).isFile():
        _psLog.info(fileName + '.json not found')
        return {}

    JAVA_IO.File(targetPath).isFile()
    report = genericReadReport(targetPath)
    tpReport = loadJson(report)

    _psLog.info(fileName + ': OK')

    return tpReport

def makeBuildStatusFolder():
    """The buildStatus folder is created first so the log file can be written.
        Called by:
        MainScript.Controller
        """

    targetDirectory = OS_PATH.join(PROFILE_PATH, 'operations', 'buildstatus')
    if not JAVA_IO.File(targetDirectory).isDirectory():
        JAVA_IO.File(targetDirectory).mkdirs()

    return

def makeReportFolders():
    """Checks/creates the folders this plugin writes to.
        Used By:
        MainScript.Controller
        """

    opsDirectory = OS_PATH.join(PROFILE_PATH, 'operations')
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
    """try/except catches initial read of config file.
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
    """Called by:
        Everything"""

    with codecsOpen(filePath, 'wb', encoding=ENCODING) as textWorkFile:
        textWorkFile.write(genericReport)

    return

def genericDisplayReport(genericReportPath):
    """Dealer's choice, the JMRI or Java version.
        Called by:
        MainScript.Controller.logItemSelected
        MainScript.Controller.ecItemSelected
        PatternTracksSubroutine.View.trackPatternButton
        PatternTracksSubroutine.ViewSetCarsForm.switchListButton
        """

    # JMRI.util.HelpUtil.openWindowsFile(genericReportPath)
    JAVA_AWT.Desktop.getDesktop().edit(JAVA_IO.File(genericReportPath))

    return

def loadJson(file):
    """Called by:
        Everything"""

    return jsonLoadS(file)

def dumpJson(file):
    """Called by:
        Everything"""

    return jsonDumpS(file, indent=2, sort_keys=True)


"""Configuration File Methods"""


def validateConfigFileVersion():
    """Checks that the config file is the current version.
        Called by:
        OperationsPatternScripts.MainScript.Model
        """

    fileName = 'PatternConfig.json'
    targetPath = OS_PATH.join(PLUGIN_ROOT, 'opsEntities', fileName)
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
    """tryConfigFile will return the config file if it's ok or a new one otherwise.
        Called by:
        Everything
        """

    configFile = checkConfigFile()

    if not subConfig:
        return configFile
    else:
        return configFile[subConfig]

def checkConfigFile():

    fileName = 'PatternConfig.json'
    targetPath = OS_PATH.join(PROFILE_PATH, 'operations', fileName)

    try:
        loadJson(genericReadReport(targetPath))
    except:
        writeNewConfigFile()
        print('Defective config file')

    return loadJson(genericReadReport(targetPath))



def tryConfigFile():
    """Try/except catches some user edit mistakes.
        Called by:
        PSE.readConfigFile
        """

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
    """Called by:
        tryConfigFile
        """

    fileName = 'PatternConfig.json'
    targetPath = OS_PATH.join(PROFILE_PATH, 'operations', fileName)

    return loadJson(genericReadReport(targetPath))

def writeConfigFile(configFile):
    """Called by:
        MainScript.Controller
        PSE.updateWindowParams
        PatternTracksSubroutine.Controller.StartUp.yardTrackOnlyCheckBox
        PatternTracksSubroutine.Model
        """

    fileName = 'PatternConfig.json'
    targetPath = OS_PATH.join(PROFILE_PATH, 'operations', fileName)
    targetFile = dumpJson(configFile)
    genericWriteReport(targetPath, targetFile)

    return

def writeNewConfigFile():
    """Called by:
        MainScript.Model.validatePatternConfig
        PSE.tryConfigFile
        """

    targetDir = OS_PATH.join(PROFILE_PATH, 'operations')
    JAVA_IO.File(targetDir).mkdir()

    fileName = 'PatternConfig.json'

    targetFile = OS_PATH.join(PLUGIN_ROOT, 'opsEntities', fileName)
    copyFrom = JAVA_IO.File(targetFile).toPath()

    targetFile = OS_PATH.join(PROFILE_PATH, 'operations', fileName)
    copyTo = JAVA_IO.File(targetFile).toPath()

    JAVA_NIO.Files.copy(copyFrom, copyTo, JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)

    return

def deleteConfigFile():
    """Called by:
        MainScript.Controller.rsItemSelected
        """

    fileName = 'PatternConfig.json'
    targetFile = OS_PATH.join(PROFILE_PATH, 'operations', fileName)
    JAVA_IO.File(targetFile).delete()

    return


"""Logging Methods"""


def makePatternLog():
    """creates a pattern log for display based on the log level, as set by getBuildReportLevel.
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
    """Moved here but may be put back into configFile.
        Called by:
        PSE.makePatternLog
        """

    loggingIndex = {"9": "- CRITICAL -", "7": "- ERROR -", "5": "- WARNING -", "3": "- INFO -", "1": "- DEBUG -"}

    return loggingIndex


"""Color Handling Methods"""


def getGenericColor(colorName):
    """Called by:
        PSE.getCarColor
        PSE.getLocoColor
        PSE.getAlertColor
        """

    colorPalette = readConfigFile('CD')['CP']


    r = colorPalette[colorName]["R"]
    g = colorPalette[colorName]["G"]
    b = colorPalette[colorName]["B"]
    a = colorPalette[colorName]["A"]

    return JAVA_AWT.Color(r, g, b, a)

def getCarColor():
    """Try/Except is a bit of protection against bad edits.
        Called by:
        PatternTracksSubroutine.ViewSetCarsForm.MakeSetCarsEqptRows
        """

    try:
        colorName = readConfigFile('CD')['carColor']
        color = getGenericColor(colorName)
        return color
    except:
        _psLog.warning('Car color definition not found in PatternConfig.json')
        return JAVA_AWT.Color(0, 0, 0, 0)

def getLocoColor():
    """Try/Except is a bit of protection against bad edits.
        Called by:
        PatternTracksSubroutine.ViewSetCarsForm.MakeSetCarsEqptRows
        """

    try:
        colorName = readConfigFile('CD')['locoColor']
        color = getGenericColor(colorName)
        return color
    except:
        _psLog.warning('Engine color definition not found in PatternConfig.json')
        return JAVA_AWT.Color(0, 0, 0, 0)

def getAlertColor():
    """Try/Except is a bit of protection against bad edits.
        Called by:
        PatternTracksSubroutine.ViewSetCarsForm.MakeSetCarsEqptRows
        """

    try:
        colorName = readConfigFile('CD')['alertColor']
        color = getGenericColor(colorName)
        return color
    except:
        _psLog.warning('Alert color definition not found in PatternConfig.json')
        return JAVA_AWT.Color(0, 0, 0, 0)


"""Translation Methods"""


def translateMessageFormat():
    """The messageFormat is in the locale's language, it has to be hashed to the plugin fields.
        Dealers choice, J_BUNDLE.ROAD or SB.handleGetMessage('Road').
        Called by:
        PatternTracksSubroutine.ViewEntities.loopThroughRs
        PatternTracksSubroutine.ViewSetCarsForm.MakeSetCarsEqptRows
        """

    rosetta = {}
#Common
    # rosetta[SB.handleGetMessage('Road')] = 'Road'
    # rosetta[SB.handleGetMessage('Number')] = 'Number'

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

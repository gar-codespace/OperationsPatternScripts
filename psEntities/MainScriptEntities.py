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

'''Support methods for all Pattern Script modules'''

_lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
_tm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.trains.TrainManager)
_em = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.engines.EngineManager)
_cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
_sm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.schedules.ScheduleManager)
_pm = jmri.InstanceManager.getDefault(jmri.util.gui.GuiLafPreferencesManager)
# _cmx = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManagerXml)
SCRIPT_ROOT = ''

SCRIPT_NAME = 'OperationsPatternScripts.psEntities.MainScriptEntities'
SCRIPT_REV = 20220101

psLog = logging.getLogger('PS.TP.MainScriptEntities')

def setEncoding():
    '''Expand on this later'''

    return 'utf-8' #ascii, utf-16

def scrubPath():
    '''Convert an OS path to a browser acceptable path'''

    helpStubPath = 'file:///' + jmri.util.FileUtil.getPreferencesPath() + 'jmrihelp\\psStub.html'
    helpStubPath = helpStubPath.replace('\\', '/')
    helpStubPath = helpStubPath.replace(' ', '%20')
    helpStubPath = helpStubPath.replace('  ', '%20%20')

    return helpStubPath

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

    # helpFilePath = __file__.replace('\psEntities\MainScriptEntities.py', '\Support\psHelp.html')
    # helpFilePath = __file__.replace('\psEntities\MainScriptEntities$py.class', '\Support\psHelp.html')
    stubLocation = jmri.util.FileUtil.getPreferencesPath() + '\\jmrihelp\\'
    try:
        osMakeDir(stubLocation)
        psLog.info('Stub location created at: ' + stubLocation)
    except OSError:
        psLog.info('Stub location already exists')

    stubFileName = stubLocation + 'psStub.html'

    helpFilePath = currentRootDir + '\Support\psHelp.html'
    helpFilePath = javaIo.File(helpFilePath).toURI()
    helpFilePath = unicode(helpFilePath, setEncoding())

    locale = unicode(_pm.getLocale(), setEncoding())
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

def readConfigFile(subConfig='all'):

    # configFilePath = SCRIPT_ROOT + '\psEntities\PatternConfig.json'

    try:
        patternConfig = getConfigFile()
    except ValueError:
        psLog.warning('Defective PatternConfig.JSON found, new file written')
        writeNewConfigFile()
        patternConfig = getConfigFile()
    except IOError:
        psLog.warning('No PatternConfig.JSON found, new file written')
        writeNewConfigFile()
        patternConfig = getConfigFile()
    if subConfig == 'all':
        return patternConfig
    else:
        return patternConfig[subConfig]

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

class makeControlPanel:
    '''This is the main panel for the plugin'''

    def makePluginPanel(self):

        self.pluginPanel = javax.swing.JPanel()

        return self.pluginPanel

    def makeScrollPanel(self):

        configPanel = readConfigFile('CP')
        scrollPanel = javax.swing.JScrollPane(self.pluginPanel)
        scrollPanel.border = javax.swing.BorderFactory.createLineBorder(java.awt.Color.GRAY)
        scrollPanel.setPreferredSize(java.awt.Dimension(configPanel['PW'], configPanel['PH']))
        scrollPanel.setMaximumSize(scrollPanel.getPreferredSize())

        return scrollPanel

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

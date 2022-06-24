# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Choose or create a language translation bundle for the current locale"""

from urllib2 import urlopen
import time

from psEntities import PatternScriptEntities
from psBundle import Translators

SCRIPT_NAME = 'OperationsPatternScripts.psBundle.Bundle'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.B.Bundle')

BUNDLE_DIR = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'

PLUGIN = []
HELP_PAGE = []

def getBundleForLocale():
    """Gets the bundle for the current locale if it exists, otherwise english."""

    psLocale = 'bundle.' + PatternScriptEntities.psLocale() + '.json'
    fileList = PatternScriptEntities.JAVA_IO.File(BUNDLE_DIR).list()

    if psLocale in fileList:
        bundleFileLocation = BUNDLE_DIR + psLocale
    else:
        bundleFileLocation = BUNDLE_DIR + 'bundle.en.json'

    bundleFile = PatternScriptEntities.genericReadReport(bundleFileLocation)
    bundleFile = PatternScriptEntities.loadJson(bundleFile)

    return bundleFile

def getHelpPageForLocale():
    """Gets the help page for the current locale, otherwise english."""

    psLocale = PatternScriptEntities.psLocale() + '.json'
    fileList = PatternScriptEntities.JAVA_IO.File(BUNDLE_DIR).list()

    if psLocale in fileList:
        bundleFileLocation = BUNDLE_DIR + 'help.' + psLocale + '.json'
    else:
        bundleFileLocation = BUNDLE_DIR + 'help.en.json'

    helpBundleFile = PatternScriptEntities.genericReadReport(bundleFileLocation)

def makeBundleForPlugin():

    startTime = time.time()

    bundleSource = BUNDLE_DIR + 'templateBundle.txt'
    bundleTarget = BUNDLE_DIR + 'bundle.' + PatternScriptEntities.psLocale()[:2] + '.json'
    scratchFile = PLUGIN
    bundleFile = getBundleTemplate(bundleSource)

    translation = baseTranslator(bundleFile, scratchFile)
    PatternScriptEntities.genericWriteReport(bundleTarget, translation)

    runTime = time.time() - startTime
    _psLog.info('Plugin translation time: ' + str(round(runTime, 2)))

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

def makeBundleForHelpPage():

    startTime = time.time()

    bundleSource = BUNDLE_DIR + 'templateHelp.txt'
    bundleTarget = BUNDLE_DIR + 'help.' + PatternScriptEntities.psLocale()[:2] + '.json'
    scratchFile = HELP_PAGE
    bundleFile = getBundleTemplate(bundleSource)

    translation = baseTranslator(bundleFile, scratchFile)
    PatternScriptEntities.genericWriteReport(bundleTarget, translation)

    runTime = time.time() - startTime
    _psLog.info('Help page translation time: ' + str(round(runTime, 2)))

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

def baseTranslator(bundleFile, scratchFile):

    translator = Translator(bundleFile, scratchFile)
    translator.setTranslationService()
    translator.translateItems()
    baseTranslation = translator.makeDictionary()
    translation = PatternScriptEntities.dumpJson(baseTranslation)

    return translation

def getBundleTemplate(file):

    baseTemplate = PatternScriptEntities.genericReadReport(file)

    bundleTemplate = baseTemplate.splitlines()

    return bundleTemplate


class Translator:
    """Choice of translators from patternConfig,
    chosen translator is in Translators.py
    """

    def __init__(self, bundleFile, scratchFile):

        self.bundleFile = bundleFile
        self.translationDict = {'version' : SCRIPT_REV}
        self.tempResult = []
        self.scratchFile = scratchFile

        controlPanel = PatternScriptEntities.readConfigFile('CP')
        self.translatorChoice = controlPanel['TS'][controlPanel['TC']]

        return

    def setTranslationService(self):
        """Gets the translator from readConfigFile('CP')['TC']"""

        self.translationService = getattr(Translators, self.translatorChoice)()

        return

    def translateItems(self):
        """Based on https://gist.github.com/snim2/561630"""

        i = 0
        for item in self.bundleFile:
            bundleItem = MakeBundleItem()
            url = self.translationService.getTheUrl(item)
            bundleItem.passInAttributes(self.scratchFile, url, item)
            bundleItem.start()
            i += 1
            if i == 10:
                i = 0
                time.sleep(.7)

        timeOut = time.time() + 10
        while True: # Homebrew version of await
            if time.time() > timeOut:
                _psLog.warning('Connection Timed Out')
                print('Connection Timed Out')
                break
            if len(self.scratchFile) == len(self.bundleFile):
                print('Translation Completed')
                break

    def makeDictionary(self):

        self.translationDict = {}

        for item in self.scratchFile:
            translatedLine = self.translationService.parseResult(item)
            self.translationDict[translatedLine[0]] = translatedLine[1]

        return self.translationDict


class MakeBundleItem(PatternScriptEntities.JMRI.jmrit.automat.AbstractAutomaton):
    """Homebrew version of concurrency."""

    def init(self):


        return

    def passInName(self, name):

        self.scratchFile = name

        return

    def passInUrl(self, url, item):

        self.url = url
        self.item = item

        return

    def passInAttributes(self, scratchFile, url, item):

        self.scratchFile = scratchFile
        self.url = url
        self.item = item

        return

    def handle(self):
        """Harden this against errors"""

        translation = {}
        response = None
        name = []

        for i in range(3):
            try:
                response = urlopen(self.url)
                translation = PatternScriptEntities.loadJson(response.read())
                response.close()
            except:
                _psLog.warning('Not translated: ' + self.item)
            if response:
                break
            time.sleep(.05)

        translation['source'] = self.item
        translation['error'] = self.item

        self.scratchFile.append(translation)

        return False

def makeHelpPage():
    """Makes the help page for the current locale."""

    helpPageTemplatePath = BUNDLE_DIR + 'templateHelp.html.txt'
    baseHelpPage = PatternScriptEntities.genericReadReport(helpPageTemplatePath)

    translationMatrixPath = BUNDLE_DIR + 'help.' + PatternScriptEntities.psLocale() + '.json'
    baseTranslationMatrix = PatternScriptEntities.genericReadReport(translationMatrixPath)
    translationMatrix = PatternScriptEntities.loadJson(baseTranslationMatrix)

    for hKey, hValue in translationMatrix.items():

        hKey = unicode(hKey, PatternScriptEntities.ENCODING)
        hValue = unicode(hValue, PatternScriptEntities.ENCODING)

        baseHelpPage = baseHelpPage.replace(hKey, hValue)

    helpPagePath = PatternScriptEntities.PLUGIN_ROOT + '\\psSupport\\' + 'Help.' + PatternScriptEntities.psLocale() + '.html'
    PatternScriptEntities.genericWriteReport(helpPagePath, baseHelpPage)

    return

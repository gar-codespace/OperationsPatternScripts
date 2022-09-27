# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Choose or create a language translation bundle for the current locale"""

from urllib2 import urlopen
import sys

from psEntities import PSE
from psBundle import Translators

SCRIPT_NAME = 'OperationsPatternScripts.psBundle.Bundle'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.B.Bundle')

BUNDLE_DIR = PSE.PLUGIN_ROOT + '\\psBundle\\'

PLUGIN = [] # Scratch file for translation
HELP = [] # Scratch file for translation

def getBundleForLocale():
    """Gets the bundle for the current locale if it exists, otherwise english."""

    psLocale = 'plugin.' + PSE.psLocale() + '.json'
    fileList = PSE.JAVA_IO.File(BUNDLE_DIR).list()

    if psLocale in fileList:
        bundleFileLocation = BUNDLE_DIR + psLocale
    else:
        bundleFileLocation = BUNDLE_DIR + 'plugin.en.json'

    bundleFile = PSE.genericReadReport(bundleFileLocation)
    bundleFile = PSE.loadJson(bundleFile)

    return bundleFile

def getHelpPageForLocale():
    """Gets the help page for the current locale if it exists, otherwise english."""

    psLocale = PSE.psLocale() + '.json'
    fileList = PSE.JAVA_IO.File(BUNDLE_DIR).list()

    if psLocale in fileList:
        bundleFileLocation = BUNDLE_DIR + 'help.' + psLocale + '.json'
    else:
        bundleFileLocation = BUNDLE_DIR + 'help.en.json'

    helpBundleFile = PSE.genericReadReport(bundleFileLocation)

def validateKeyFile():
    """Checks that the keys.py file exists"""

    itemTarget =  BUNDLE_DIR + 'Keys.py'
    if PSE.JAVA_IO.File(itemTarget).isFile():
        return True
    else:
        _psLog.warning('Authentication key file not found')
        print('Authentication key file not found')
        return False

def makeBundles():
    """Makes a translated bundle for each of the items in readConfigFile('CP')['BT']"""

    bundleTargets = PSE.readConfigFile('CP')['BT']

    for item in bundleTargets:

        startTime = PSE.TIME.time()

        itemSource =  BUNDLE_DIR + 'template' + item + '.txt'
        itemTarget =  BUNDLE_DIR + item.lower() + '.' + PSE.psLocale()[:2] + '.json'
        itemScratch = getattr(sys.modules[__name__], item.upper())
        bundleFile = getBundleTemplate(itemSource)

        if not PSE.JAVA_IO.File(itemTarget).isFile():
            translation = baseTranslator(bundleFile, itemScratch)
            PSE.genericWriteReport(itemTarget, translation)

            runTime = PSE.TIME.time() - startTime
            _psLog.info(item + ' translation time: ' + str(round(runTime, 2)))

        else:
            _psLog.info(item + ' already exists')

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

    return

def getBundleTemplate(file):

    baseTemplate = PSE.genericReadReport(file)

    bundleTemplate = baseTemplate.splitlines()

    return bundleTemplate

def baseTranslator(bundleFile, scratchFile):

    translator = Translator(bundleFile, scratchFile)
    translator.setTranslationService()
    translator.translateItems()
    baseTranslation = translator.makeDictionary()
    translation = PSE.dumpJson(baseTranslation)

    return translation


class Translator:
    """Choice of translators from PSE.readConfigFile('CP')['TS']['TC']"""

    def __init__(self, bundleFile, scratchFile):

        self.bundleFile = bundleFile
        self.translationDict = {u'version' : SCRIPT_REV}
        self.tempResult = []
        self.scratchFile = scratchFile

        controlPanel = PSE.readConfigFile('CP')
        self.translatorChoice = controlPanel['TS'][controlPanel['TC']]

        return

    def setTranslationService(self):
        """Gets the translator from readConfigFile('CP')['TC']"""

        self.translationService = getattr(Translators, self.translatorChoice)()

        return

    def translateItems(self):
        """Based on https://gist.github.com/snim2/561630"""

    # Meter the items to be translated
        i = 0
        for item in self.bundleFile:
            encodedItem = unicode(item, PSE.ENCODING)
            bundleItem = MakeBundleItem()
            url = self.translationService.getTheUrl(encodedItem)
            bundleItem.passInAttributes(self.scratchFile, url, item)
            bundleItem.start()
            i += 1
            if i == 10:
                i = 0
                PSE.TIME.sleep(.7)

    # Homebrew version of await
        timeOut = PSE.TIME.time() + 20
        while True:
            if PSE.TIME.time() > timeOut:
                _psLog.warning('Connection Timed Out')
                print('Connection Timed Out')
                break
            if len(self.scratchFile) == len(self.bundleFile):
                print('Translation Completed')
                break
            PSE.TIME.sleep(.1)

    def makeDictionary(self):

        for item in self.scratchFile:
            translatedLine = self.translationService.parseResult(item)
            self.translationDict[translatedLine[0]] = translatedLine[1]

        return self.translationDict


class MakeBundleItem(PSE.JMRI.jmrit.automat.AbstractAutomaton):
    """Homebrew version of concurrency."""

    def init(self):


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
                translation = PSE.loadJson(response.read())
                response.close()
            except:
                _psLog.warning('Not translated: ' + self.item)
            if response:
                break
            PSE.TIME.sleep(.05)

        translation['source'] = self.item
        translation['error'] = self.item

        self.scratchFile.append(translation)

        return False

def makeHelpPage():
    """Makes the help page for the current locale."""

    helpPageTemplatePath = BUNDLE_DIR + 'templateHelp.html.txt'
    baseHelpPage = PSE.genericReadReport(helpPageTemplatePath)

    translationMatrixPath = BUNDLE_DIR + 'help.' + PSE.psLocale() + '.json'
    baseTranslationMatrix = PSE.genericReadReport(translationMatrixPath)
    translationMatrix = PSE.loadJson(baseTranslationMatrix)

    for hKey, hValue in translationMatrix.items():

        hKey = unicode(hKey, PSE.ENCODING)
        hValue = unicode(hValue, PSE.ENCODING)

        baseHelpPage = baseHelpPage.replace(hKey, hValue)

    helpPagePath = PSE.PLUGIN_ROOT + '\\psSupport\\' + 'Help.' + PSE.psLocale() + '.html'
    PSE.genericWriteReport(helpPagePath, baseHelpPage)

    return

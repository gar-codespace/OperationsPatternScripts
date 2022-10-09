# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Choose or create a language translation bundle for the current locale"""

from urllib2 import urlopen

from opsEntities import PSE
from opsBundle import Translators

SCRIPT_NAME = 'OperationsPatternScripts.opsBundle.Bundle'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.OB.Bundle')

PSE.BUNDLE_DIR = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle')


def getBundleForLocale():
    """Gets the bundle json for the current locale if it exists, otherwise english.
        Used by:
        Main.Controller.buildThePlugin
        Main.Controller.ptItemSelected
        BuiltTrainExport
        """

    psLocale = 'plugin.' + PSE.psLocale() + '.json'
    fileList = PSE.JAVA_IO.File(PSE.BUNDLE_DIR).list()

    if psLocale in fileList:
        bundleFileLocation = PSE.OS_PATH.join(PSE.BUNDLE_DIR, psLocale)
    else:
        bundleFileLocation = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'plugin.en.json')

    bundleFile = PSE.genericReadReport(bundleFileLocation)
    bundleFile = PSE.loadJson(bundleFile)

    return bundleFile

def getAllTextBundles():
    """Combines the plugin bundle.txt file with all the bundle.txt files
        for each subroutine listed in configFile("CP")["SI"].
        Each bundle.txt file ends with a <CR>.
        """

    _psLog.debug('getAllTextBundles')

    targetPath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle', 'bundle.txt')
    textBundles = PSE.genericReadReport(targetPath)

    listOfSubroutines = []
    subroutine = PSE.readConfigFile('CP')['SI']
    for item in subroutine:
        listOfSubroutines.append(''.join(item.keys()))

    for subroutine in listOfSubroutines:
        targetPath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, subroutine, 'bundle.txt')
        bundle = PSE.genericReadReport(targetPath)
        textBundles += bundle

    return textBundles

def makePluginBundle(textBundle):
    """Makes the plugin.<locale>.json file from getAllTextBundles()"""

    fileName = 'plugin.' + PSE.psLocale()[:2] + '.json'
    targetFile = PSE.OS_PATH.join(PSE.BUNDLE_DIR, fileName)

    if PSE.JAVA_IO.File(targetFile).isFile():
        _psLog.info('Translated bundle already exists')

        return

    translation = baseTranslator(textBundle)
    PSE.genericWriteReport(targetFile, translation)

    return

def makeHelpBundle():
    """Makes the help.<locale>.json file from bundle.help.txt"""

    itemTarget = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'bundle.help.txt')
    textBundle = PSE.genericReadReport(itemTarget)

    fileName = 'help.' + PSE.psLocale()[:2] + '.json'
    targetFile = PSE.OS_PATH.join(PSE.BUNDLE_DIR, fileName)

    if PSE.JAVA_IO.File(targetFile).isFile():
        _psLog.info('Translated bundle already exists')

        return

    translation = baseTranslator(textBundle)
    PSE.genericWriteReport(targetFile, translation)

    return

def baseTranslator(textBundle):
    """Mini controller translates each item in the bundleFile,
        then appends it to the RAM based scratchFile.
        used by:
        makePluginBundle
        makeHelpBundle
        """

    startTime = PSE.TIME.time()

    scratch = []
    translation = {}

    inputBundle = textBundle.splitlines()
    translator = Translator(inputBundle, scratch)
    translator.setTranslationService()
    translator.translateItems()
    baseTranslation = translator.makeDictionary()
    translation = PSE.dumpJson(baseTranslation)

    runTime = PSE.TIME.time() - startTime
    _psLog.info('Bundle translation time: ' + str(round(runTime, 2)))

    return translation

def makeHelpPage():
    """Makes the help page for the current locale.
        Used by:
        Main.Controller.rsItemSelected
        Main.Controller.ptItemSelected
        """

    helpPageTemplatePath = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'help.html.txt')
    baseHelpPage = PSE.genericReadReport(helpPageTemplatePath)

    fileName = 'help.' + PSE.psLocale() + '.json'
    translationMatrixPath = PSE.OS_PATH.join(PSE.BUNDLE_DIR, fileName)
    baseTranslationMatrix = PSE.genericReadReport(translationMatrixPath)
    translationMatrix = PSE.loadJson(baseTranslationMatrix)

    for hKey, hValue in translationMatrix.items():
        hKey = unicode(hKey, PSE.ENCODING)
        hValue = unicode(hValue, PSE.ENCODING)

        baseHelpPage = baseHelpPage.replace(hKey, hValue)

    fileName = 'help.' + PSE.psLocale() + '.html'
    helpPagePath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', fileName)
    PSE.genericWriteReport(helpPagePath, baseHelpPage)

    return

def validateKeyFile():
    """Checks that the keys.py file exists
        Used by:
        Main.View
        """

    itemTarget =  PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'Keys.py')
    if PSE.JAVA_IO.File(itemTarget).isFile():
        return True
    else:
        _psLog.warning('Authentication key file not found')
        print('Authentication key file not found')
        return False



class Translator:
    """Choice of translators from PSE.readConfigFile('CP')['TS']"""

    def __init__(self, bundleFile, scratchFile):

        self.bundleFile = bundleFile
        self.translationDict = {u'version' : SCRIPT_REV}
        self.tempResult = []
        self.scratchFile = scratchFile

        controlPanel = PSE.readConfigFile('CP')
        self.translatorChoice = controlPanel['TS'][controlPanel['TC']]

        return

    def setTranslationService(self):
        """Gets the translator from readConfigFile('CP')['TC']
            Example: self.translationService = Translators.UseDeepL()"""

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

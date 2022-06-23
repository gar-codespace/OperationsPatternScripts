# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Choose or create a language translation bundle for the current locale"""

from urllib2 import urlopen
from urllib import urlencode
import time

from psEntities import PatternScriptEntities
from psBundle import Keys

SCRIPT_NAME = 'OperationsPatternScripts.psBundle.Bundle'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.B.Bundle')
_base_Translation = []
_help_Translation = []
_bundle_Translation = []
PLUGIN = []
HELP = []

def getBundleForLocale():
    """Gets the bundle for the current locale if it exists, otherwise english."""

    psLocale = 'bundle.' + PatternScriptEntities.psLocale() + '.json'
    bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
    fileList = PatternScriptEntities.JAVA_IO.File(bundleDir).list()

    if psLocale in fileList:
        bundleFileLocation = bundleDir + psLocale
    else:
        bundleFileLocation = bundleDir + 'bundle.en.json'

    bundleFile = PatternScriptEntities.genericReadReport(bundleFileLocation)
    bundleFile = PatternScriptEntities.loadJson(bundleFile)

    return bundleFile

def getHelpPageForLocale():
    """Gets the help page for the current locale, otherwise english."""

    psLocale = PatternScriptEntities.psLocale() + '.json'
    bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
    fileList = PatternScriptEntities.JAVA_IO.File(bundleDir).list()

    if psLocale in fileList:
        bundleFileLocation = bundleDir + 'help.' + psLocale + '.json'
    else:
        bundleFileLocation = bundleDir + 'help.en.json'

    helpBundleFile = PatternScriptEntities.genericReadReport(bundleFileLocation)

# def makeBundle():
#
#     bundleLocale = PatternScriptEntities.psLocale()[:2]
#     bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
#
#     templateName = 'templateBundle.txt'
#     bundleSource = bundleDir + templateName
#
#     targetName = templateName.replace('.txt', '.' + bundleLocale + '.json')
#     targetName = targetName.replace('template', '')
#     bundleTarget = bundleDir + targetName
#
#     fileToTranslate = getBundleTemplate(bundleSource)
#     baseTranslation = translateItems(fileToTranslate)
#     translation = PatternScriptEntities.dumpJson(baseTranslation)
#     PatternScriptEntities.genericWriteReport(bundleTarget, translation)
#
#     _psLog.info('Bundle created: ' + targetName)
#     print('Bundle created: ' + targetName)
#         # time.sleep(10)
#
#     print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

    return

def makeHelpPage():
    """Makes the help page for the current locale."""

    helpDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'

    helpPageTemplatePath = helpDir + 'templateHelp.html.txt'
    baseHelpPage = PatternScriptEntities.genericReadReport(helpPageTemplatePath)
    # baseHelpPage = unicode(baseHelpPage, PatternScriptEntities.ENCODING)
    # baseHelpPage = repr(baseHelpPage)

    # translationMatrixPath = helpDir + 'Bundle.' + PatternScriptEntities.psLocale() + '.json'
    translationMatrixPath = helpDir + 'help.' + PatternScriptEntities.psLocale() + '.json'
    baseTranslationMatrix = PatternScriptEntities.genericReadReport(translationMatrixPath)
    translationMatrix = PatternScriptEntities.loadJson(baseTranslationMatrix)

    for hKey, hValue in translationMatrix.items():

        hKey = unicode(hKey, PatternScriptEntities.ENCODING)
        hValue = unicode(hValue, PatternScriptEntities.ENCODING)

        # hKey = repr(hKey)

        # hKey = PatternScriptEntities.HTML_PARSER().unescape(hKey)
        # hValue = PatternScriptEntities.HTML_PARSER().unescape(hValue)

        # baseHelpPage = baseHelpPage.decode("utf-8").replace(hKey, hValue).encode("utf-8")
        # baseHelpPage = baseHelpPage.encode("utf-8")

        baseHelpPage = baseHelpPage.replace(hKey, hValue)

    helpPagePath = PatternScriptEntities.PLUGIN_ROOT + '\\psSupport\\' + 'Help.' + PatternScriptEntities.psLocale() + '.html'
    PatternScriptEntities.genericWriteReport(helpPagePath, baseHelpPage)

    return

def getBundleTemplate(file):

    baseTemplate = PatternScriptEntities.genericReadReport(file)

    bundleTemplate = baseTemplate.splitlines()

    return bundleTemplate

# def translateBundle(bundleTarget, fileToTranslate):
#
#     translator = Translator(fileToTranslate)
#     translator.translateItems()
#     translation = translator.makeDictionary()
#     print(translation)
    # PatternScriptEntities.genericWriteReport(bundleTarget, translation)



    # translatedItems = translateItems(fileToTranslate)
    # translation = PatternScriptEntities.dumpJson(translatedItems)

    # return


class Translator:
    """Move useDeepL to the config file"""

    def __init__(self, file):

        self.file = file
        self.translationDict = {'version' : SCRIPT_REV}
        self.translationService = useDeepL()
        self.tempResult = []

        return

    def translateItems(self):
        """Based on https://gist.github.com/snim2/561630"""

        # self.tempResult = bundleItem.getTempResult()
        i = 0
        for item in self.file:
            url = self.translationService.getTheUrl(item)
            bundleItem = MakeBundleItem()
            bundleItem.passInName(PLUGIN)
            bundleItem.passInUrl(url, item)
            bundleItem.start()
            i += 1
            if i == 10:
                i = 0
                time.sleep(.7)

        timeOut = time.time() + 1
        while True: # Homebrew version of await
            if time.time() > timeOut:
                _psLog.warning('Connection Timed Out')
                print('Connection Timed Out')
                break
            if len(self.tempResult) == len(self.file):
                _psLog.info('Translation Completed')
                print('Translation Completed')
                break

    def makeDictionary(self, name):

        self.translationDict = name

        for item in self.tempResult:
            translatedLine = self.translationService.parseResult(item)
            self.translationDict[translatedLine[0]] = translatedLine[1]

        return self.translationDict


class MakeBundleItem(PatternScriptEntities.JMRI.jmrit.automat.AbstractAutomaton):
    """Homebrew version of concurrency."""

    def init(self):


        self.tempResult = []

        return

    def getTempResult(self):


        return self.tempResult

    def passInName(self, name):

        self.name = name

        return

    def passInUrl(self, url, item):

        self.url = url
        self.item = item

        return

    def handle(self):
        """Harden this against errors"""

        translation = {}
        response = None

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
        print(translation)
        self.name.append(translation)

        return False


class ForPlugin:

    def __init__(self):

        bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
        self.bundleSource = bundleDir + 'templateBundle.txt'
        self.bundleTarget = bundleDir + 'bundle.' + PatternScriptEntities.psLocale()[:2] + '.json'
        self.PLUGIN = PLUGIN

        return

    def make(self):

        bundleFile = getBundleTemplate(self.bundleSource)
        translator = Translator(bundleFile)
        translator.translateItems()





        # baseTranslation = translator.makeDictionary(, self.PLUGIN)
        # translation = PatternScriptEntities.dumpJson(baseTranslation)
        # PatternScriptEntities.genericWriteReport(self.bundleTarget, translation)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return


class ForHelpPage:

    def __init__(self):

        bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
        self.bundleSource = bundleDir + 'templateHelp.txt'
        self.bundleTarget = bundleDir + 'help.' + PatternScriptEntities.psLocale()[:2] + '.json'

        return

    def make(self):


        helpFile = getBundleTemplate(self.bundleSource)
        translator = Translator(helpFile, HELP)
        translator.translateItems()
        baseTranslation = translator.makeDictionary()
        translation = PatternScriptEntities.dumpJson(baseTranslation)
        PatternScriptEntities.genericWriteReport(self.bundleTarget, translation)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return


class useDeepL:
    """Specifics for using DeepL"""

    def __init__(self):

        self.BASE_URL = 'https://api-free.deepl.com/v2/translate?'
        self.DOCUMENT_URL = 'https://api-free.deepl.com/v2/document?'
        self.AUTH_KEY = Keys.DEEPL_KEY
        self.SOURCE_LANG = 'en'

        return

    def getTheUrl(self, item):

        params = urlencode( (('auth_key', self.AUTH_KEY),
                                 ('text', item),
                                 ('source_lang', self.SOURCE_LANG),
                                 ('target_lang', PatternScriptEntities.psLocale()),
                                 ('split_sentences', 0))
                                 )

        return self.BASE_URL + params

    def parseResult(self, response):

        source = response['source']
        error = response['error']
        try:
            translation = response['translations'][0]['text']
        except:
            translation = error

        return (source, translation)

# def translateItems(file):
#     """Based on https://gist.github.com/snim2/561630
#     """
#
#     translationDict = {'version' : SCRIPT_REV}
#     translator = useDeepL()
#
#     i = 0
#     for item in file:
#         url = translator.getTheUrl(item)
#         bundleItem = MakeBundleItem()
#         bundleItem.passInUrl(url, item)
#         bundleItem.start()
#         i += 1
#         if i == 10:
#             i = 0
#             time.sleep(.7)
#
#     timeOut = time.time() + 30
#     while True: # Homebrew version of await
#         if time.time() > timeOut:
#             _psLog.warning('Connection Timed Out')
#             print('Connection Timed Out')
#             break
#         if len(_base_Translation) == len(file):
#             _psLog.info('Translation Completed')
#             print('Translation Completed')
#             break
#
#
#     for item in _base_Translation:
#         translatedLine = translator.parseResult(item)
#         translationDict[translatedLine[0]] = translatedLine[1]
#
#     return translationDict

# def createBundleForLocale():
#     """Creates a new plugin bundle for JMRI's locale setting."""
#
#     bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
#
#     bundleSource = bundleDir + 'templateBundle.txt'
#     bundleTarget = bundleDir + 'bundle.' + PatternScriptEntities.psLocale()[:2] + '.json'
#
#     fileToTranslate = getBundleTemplate(bundleSource)
#     translateBundle(bundleTarget, fileToTranslate)
#
#     print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))
#
#     return


# def translateItems(file):
#     """Based on https://gist.github.com/snim2/561630
#     """
#
#     translationDict = {'version' : SCRIPT_REV}
#     translator = useDeepL()
#
#
#     for item in file:
#         url = translator.getTheUrl(item)
#
#         bundleItem = MakeBundleItem()
#         bundleItem.passInUrl(url, item)
#         bundleItem.start()
#         time.sleep(.1)
#
#
#
#     timeOut = time.time() + 30
#     while True: # Homebrew version of await
#         if time.time() > timeOut:
#             _psLog.warning('Connection Timed Out')
#             print('Connection Timed Out')
#             break
#         if len(_base_Translation) == len(file):
#             _psLog.info('Translation Completed')
#             print('Translation Completed')
#             break
#
#
#     for item in _base_Translation:
#         translatedLine = translator.parseResult(item)
#         translationDict[translatedLine[0]] = translatedLine[1]
#
#     return translationDict



# def createBundleForHelpPage():
#     """Creates a new help page bundle for JMRI's locale setting."""
#
#     bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
#
#     bundleSource = bundleDir + 'templateHelp.txt'
#     bundleTarget = bundleDir + 'help.' + PatternScriptEntities.psLocale()[:2] + '.json'
#
#     fileToTranslate = getBundleTemplate(bundleSource)
#     translateBundle(bundleTarget, fileToTranslate)
#
#     # makeHelpPageForLocale()
#
#     print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

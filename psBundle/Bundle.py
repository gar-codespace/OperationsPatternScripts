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

def getBundleForLocale():
    """Gets the bundle for the current locale if it exists, otherwise english."""

    psLocale = PatternScriptEntities.psLocale() + '.json'
    bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
    fileList = PatternScriptEntities.JAVA_IO.File(bundleDir).list()

    if psLocale in fileList:
        bundleFileLocation = bundleDir + psLocale
    else:
        bundleFileLocation = bundleDir + 'en.json'

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


def createBundleForLocale():
    """Creates a new plugin bundle for JMRI's locale setting."""

    bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'

    bundleSource = bundleDir + 'templateBundle.txt'
    bundleTarget = bundleDir + PatternScriptEntities.psLocale()[:2] + '.json'

    fileToTranslate = getBundleTemplate(bundleSource)
    translateBundle(bundleTarget, fileToTranslate)

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

    return

def createBundleForHelpPage():
    """Creates a new help page bundle for JMRI's locale setting."""

    bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'

    bundleSource = bundleDir + 'templateHelpPage.txt'
    bundleTarget = bundleDir + 'help.' + PatternScriptEntities.psLocale()[:2] + '.json'

    fileToTranslate = getBundleTemplate(bundleSource)
    translateBundle(bundleTarget, fileToTranslate)

    makeHelpPageForLocale()

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

def makeHelpPageForLocale():
    """Makes the help page for the current locale."""

    helpDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'

    helpSource = helpDir + 'templatePsHelp.html.txt'
    helpBase = PatternScriptEntities.genericReadReport(helpSource)

    translationMatrixSource = helpDir + 'help.' + PatternScriptEntities.psLocale() + '.json'
    helpMatrix = PatternScriptEntities.genericReadReport(translationMatrixSource)
    helpMatrix = PatternScriptEntities.loadJson(helpMatrix)

    for hKey, hValue in helpMatrix.items():

        helpBase = helpBase.replace(unicode(hKey, PatternScriptEntities.ENCODING), unicode(hValue, PatternScriptEntities.ENCODING))

    helpTarget = PatternScriptEntities.PLUGIN_ROOT + '\\psSupport\\' + 'psHelp.' + PatternScriptEntities.psLocale() + '.html'
    PatternScriptEntities.genericWriteReport(helpTarget, helpBase)

    return

def getBundleTemplate(file):

    baseTemplate = PatternScriptEntities.genericReadReport(file)

    bundleTemplate = baseTemplate.splitlines()

    return bundleTemplate

def translateBundle(bundleTarget, fileToTranslate):

    translatedItems = translateItems(fileToTranslate)
    translation = PatternScriptEntities.dumpJson(translatedItems)
    PatternScriptEntities.genericWriteReport(bundleTarget, translation)

    return

def translateItems(file):
    """Based on https://gist.github.com/snim2/561630
    https://stackoverflow.com/questions/10115126/python-requests-close-http-connection#15511852
    """

    translationDict = {'version' : SCRIPT_REV}
    translator = useDeepL()

    for item in file:

        url = translator.getTheUrl(item)

        bundleItem = MakeBundleItem()
        bundleItem.passInUrl(url, item)
        bundleItem.start()

    timeOut = time.time() + 30
    while True: # Homebrew version of await
        if time.time() > timeOut:
            _psLog.warning('Connection Timed Out')
            print('Connection Timed Out')
            break
        if len(_base_Translation) == len(file):
            _psLog.info('Translation Completed')
            print('Translation Completed')
            break

    for item in _base_Translation:
        translatedLine = translator.parseResult(item)
        translationDict[translatedLine[0]] = translatedLine[1]

    return translationDict


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


class MakeBundleItem(PatternScriptEntities.JMRI.jmrit.automat.AbstractAutomaton):
    """Homebrew version of concurrency."""

    def init(self):

        return

    def passInUrl(self, url, item):

        self.url = url
        self.item = item

        return

    def handle(self):
        """Harden this against errors"""

        translation = {}
        response = None

        for i in range(4):
            try:
                response = urlopen(self.url)
                translation = PatternScriptEntities.loadJson(response.read())
                response.close()
            except:
                _psLog.warning('Not translated: ' + self.item)
            if response:
                break

        translation['source'] = self.item
        translation['error'] = self.item
        _base_Translation.append(translation)

        return False

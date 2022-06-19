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

_base_Translation = []

def createBundleForLocale():
    """Creates a new bundle for JMRI's locale setting"""

    bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
    bundleTarget = bundleDir + PatternScriptEntities.psLocale()[:2] + '.json'

    translatedItems = translateItems()

    translation = PatternScriptEntities.dumpJson(translatedItems)
    PatternScriptEntities.genericWriteReport(bundleTarget, translation)

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

    return

def getBundleForLocale():

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

def translateItems():
    """Based on https://gist.github.com/snim2/561630
    https://stackoverflow.com/questions/10115126/python-requests-close-http-connection#15511852
    """

    bundleTemplate = getBundleTemplate()
    translationDict = {'version' : SCRIPT_REV}
    translator = useDeepL()

    for item in bundleTemplate:

        url = translator.getTheUrl(item)

        bundleItem = MakeBundleItem()
        bundleItem.passInUrl(url, item)
        bundleItem.start()

    timeOut = time.time() + 60 # times out after 60 seconds
    while True: # Homebrew version of await
        if len(_base_Translation) == len(bundleTemplate) or time.time() > timeOut:
            break

    for item in _base_Translation:
        translatedLine = translator.parseResult(item)
        translationDict[translatedLine[0]] = translatedLine[1]

    return translationDict

def quickCheck(translator, item):

    url = translator.getTheUrl(item)

    try:
        response = urlopen(url)
        translation = PatternScriptEntities.loadJson(response.read())
        translatedLine = translator.parseResult(translation)
        response.close()
        print('Connection Ok')
        return True
    except:
        print('Connection failed')
        return False

def getBundleTemplate():

    bundleFileLocation = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\bundleTemplate.txt'

    baseTemplate = PatternScriptEntities.genericReadReport(bundleFileLocation)

    bundleTemplate = baseTemplate.splitlines()

    return bundleTemplate


class useDeepL:
    """Specifics for using DeepL"""

    def __init__(self):

        self.BASE_URL = 'https://api-free.deepl.com/v2/translate?'
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
        translation = response['translations'][0]['text']

        return (source, translation)


class MakeBundleItem(PatternScriptEntities.JMRI.jmrit.automat.AbstractAutomaton):
    """Homebrew version of concurrency"""

    def init(self):

        return

    def passInUrl(self, url, item):

        self.url = url
        self.item = item

        return

    def handle(self):
        """Harden this against errors"""

        response = urlopen(self.url)
        translation = PatternScriptEntities.loadJson(response.read())
        response.close()
        translation['source'] = self.item
        _base_Translation.append(translation)

        return False


# class MakeBundle(PatternScriptEntities.JMRI.jmrit.automat.AbstractAutomaton):
#
#     def init(self):
#
#         self.bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
#         self.bundleTemplate = self.bundleDir + 'bundleTemplate.txt'
#
#         return
#
#     def quickCheck(self, translator, item):
#
#         url = translator.getTheUrl(item)
#
#         try:
#             response = urlopen(url)
#             translation = PatternScriptEntities.loadJson(response.read())
#             translatedLine = translator.parseResult(translation)
#             response.close()
#             print('Connection Ok')
#             return True
#         except:
#             print('Connection failed')
#             return False
#
#     def getBundleTemplate(self):
#
#         baseTemplate = PatternScriptEntities.genericReadReport(self.bundleTemplate)
#
#         bundleTemplate = baseTemplate.splitlines()
#
#         return bundleTemplate
#
#     def translateItems(self):
#         """Based on https://gist.github.com/snim2/561630
#         https://stackoverflow.com/questions/10115126/python-requests-close-http-connection#15511852
#         """
#
#         bundleTemplate = self.getBundleTemplate()
#         translatedItems = {'version' : SCRIPT_REV}
#         translator = useDeepL()
#
#         # if not quickCheck(translator, bundleTemplate[0]):
#         #
#         #     return
#
#         for item in bundleTemplate:
#
#             url = translator.getTheUrl(item)
#
#             try:
#                 response = urlopen(url)
#                 translation = PatternScriptEntities.loadJson(response.read())
#                 translatedLine = translator.parseResult(translation)
#                 response.close()
#             except:
#                 translatedLine = item
#
#             translatedItems[item] = translatedLine
#
#         print('Done')
#         return translatedItems
#
#     def handle(self):
#
#         bundleTarget = self.bundleDir + PatternScriptEntities.psLocale()[:2] + '.json'
#
#         translatedItems = self.translateItems()
#
#         translation = PatternScriptEntities.dumpJson(translatedItems)
#         PatternScriptEntities.genericWriteReport(bundleTarget, translation)
#
#         print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))
#
#         return False

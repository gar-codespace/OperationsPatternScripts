# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Choose or create a language translation bundle for the current local"""

from urllib2 import urlopen
from urllib import urlencode

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.psBundle.Bundle'
SCRIPT_REV = 20220101

def createBundleForLocale():
    """Creates a new bundle for JMRI's locale setting"""

    bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
    bundleTarget = bundleDir + PatternScriptEntities.psLocale() + '.json'

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

        try:
            response = urlopen(url)
            translation = PatternScriptEntities.loadJson(response.read())
            translatedLine = translator.parseResult(translation)
            response.close()
        except:
            translatedLine = item

        translationDict[item] = translatedLine

    return translationDict

def getBundleTemplate():

    bundleFileLocation = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\bundleTemplate.txt'

    baseTemplate = PatternScriptEntities.genericReadReport(bundleFileLocation)

    bundleTemplate = baseTemplate.splitlines()

    return bundleTemplate


class useDeepL:
    """Specifics for using DeepL"""

    def __init__(self):

        self.BASE_URL = 'https://api-free.deepl.com/v2/translate?'
        self.AUTH_KEY = ''
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

    def parseResult(self, translation):

        return translation['translations'][0]['text']

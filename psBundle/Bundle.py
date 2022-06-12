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

    # xyz = PatternScriptEntities.JMRI.jmrit.operations.Bundle()
    # print(xyz.handleGetMessage('Length'))

    bundleDir = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\'
    bundleTarget = bundleDir + PatternScriptEntities.psLocale() + '.jso'

    translatedItems = translateItems()
    translatedAttributes = translateAttributes()
    mergedTranslation = translatedItems.update(translatedAttributes)

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

def getBundleTemplate():

    bundleFileLocation = PatternScriptEntities.PLUGIN_ROOT + '\\psBundle\\bundleTemplate.txt'

    baseTemplate = PatternScriptEntities.genericReadReport(bundleFileLocation)

    bundleTemplate = baseTemplate.splitlines()

    return bundleTemplate

def translateItems():

    BASE_URL = 'https://api-free.deepl.com/v2/translate?'
    AUTH_KEY = ''
    SOURCE_LANG = 'en'

    bundleTemplate = getBundleTemplate()
    translationDict = {'version' : SCRIPT_REV}
    # translationDict['version'] = SCRIPT_REV
    # targetLang = PatternScriptEntities.psLocale()
    targetLang = 'fr'

    for item in bundleTemplate:
        params = urlencode( (('auth_key', AUTH_KEY),
                                 ('text', item),
                                 ('source_lang', SOURCE_LANG),
                                 ('target_lang', targetLang),
                                 ('split_sentences', 0)) )

        url = BASE_URL + params

        response = PatternScriptEntities.loadJson(urlopen(url).read())
        translation = response['translations'][0]['text']

        translationDict[item] = translation

    return translationDict

def translateAttributes():

    return {'attribute' : 'attribute'}

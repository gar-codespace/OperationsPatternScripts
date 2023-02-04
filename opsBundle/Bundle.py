# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Choose or create a language translation bundle for the current locale"""

from urllib2 import urlopen
import re

from opsEntities import PSE
from opsBundle import Translators

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

PSE.BUNDLE_DIR = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle')

_psLog = PSE.LOGGING.getLogger('OPS.OB.Bundle')


"""Plugin and subroutine bundle methods"""

def setupBundle():
    """Mini controller to set up the bundles."""

# Plugin bundle stuff
    allBundles = getAllBundles()
    makeDefaultPluginBundle(allBundles)
    PSE.BUNDLE = getBundleForLocale()

# Help bundle stuff
    PSE.CreateStubFile().make()
    makeDefaultHelpFile() # Default help file is in english
    validateHelpForLocale()
    updateHelpFileForLocale()

    return

def getAllBundles():

    targetPath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle', 'bundle.txt')
    pluginBundle = PSE.genericReadReport(targetPath)

    allSubs = PSE.getSubroutineDirs()
    for sub in allSubs:
        targetPath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'Subroutines', sub, 'bundle.txt')
        subroutineBundle = PSE.genericReadReport(targetPath)
        pluginBundle += subroutineBundle

    return pluginBundle

def makeDefaultPluginBundle(allBundles):
    """Makes the default english plugin bundle without using the translator."""

    defaultBundle = {}
    bundleFileLocation = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'plugin.en.json')

    allBundles = allBundles.splitlines()
    for bundleItem in allBundles:
        defaultBundle[bundleItem] = bundleItem

    defaultBundle = PSE.dumpJson(defaultBundle)
    PSE.genericWriteReport(bundleFileLocation, defaultBundle)

    return

def getBundleForLocale():
    """Gets the bundle json for the current locale if it exists, otherwise english.
        Called by:
        Main.Controller.buildThePlugin
        Main.Controller.ptItemSelected
        BuiltTrainExport
        """

    bundleFileLocation = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'plugin.en.json')
    defaultBundle = PSE.loadJson(PSE.genericReadReport(bundleFileLocation))
    if PSE.psLocale()[:2] == 'en':
        return defaultBundle

    psLocale = 'plugin.' + PSE.psLocale()[:2] + '.json'
    bundleFileLocation = PSE.OS_PATH.join(PSE.BUNDLE_DIR, psLocale)
    if not PSE.JAVA_IO.File(bundleFileLocation).isFile():
        return defaultBundle
# For partially translated bundles mashup the translated bundle with the english items
    compositeBundle = {}
    localeBundle = PSE.loadJson(PSE.genericReadReport(bundleFileLocation))
    for item, translation in defaultBundle.items():
        try:
            compositeBundle[item] = localeBundle[item]
        except:
            compositeBundle[item] = translation

    return compositeBundle


"""Help file methods"""


def makeDefaultHelpFile():
    """Gather up all the help.html.txt files and combine them into Help.en.html"""

    targetPath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', 'header.html')
    helpHtml = PSE.genericReadReport(targetPath)

    targetPath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', 'help.html')
    helpHtml += PSE.genericReadReport(targetPath)

    allSubs = PSE.getSubroutineDirs()
    for sub in allSubs:
        targetPath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'Subroutines', sub, 'help.html')
        subroutineBundle = PSE.genericReadReport(targetPath)
        helpHtml += subroutineBundle

    helpHtml += '\n</body>\n</html>\n'
    helpFileLocation = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', 'Help.en.html')
    PSE.genericWriteReport(helpFileLocation, helpHtml)

    return

def validateHelpForLocale():
    """Checks taht a help html exists for the current locale.
        If not, copy the default english version as the current locales' help file."""

    localeHelpHtml = 'Help.' + PSE.psLocale()[:2] + '.html'
    localeHelpFileLocation = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', localeHelpHtml)
    if PSE.JAVA_IO.File(localeHelpFileLocation).isFile():
        return

    defaultHelpFileLocation = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', 'Help.en.html')

    copyFrom = PSE.JAVA_IO.File(defaultHelpFileLocation).toPath()

    copyTo = PSE.JAVA_IO.File(localeHelpFileLocation).toPath()

    PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)

    return

def updateHelpFileForLocale():
    """Checks that all the activated subroutines have entries in the help html for the current locale.
        If not, the english version is added to the locales' help file.
        """

    if PSE.psLocale()[:2] =='en':
        return

    helpFileName = 'Help.' + PSE.psLocale()[:2] + '.html'
    localeHelpFileLocation = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', helpFileName)
    localeHelpHtml = PSE.genericReadReport(localeHelpFileLocation)


    defaultEncoding = '<html lang="en">'
    localeEncoding = '<html lang="' + PSE.psLocale()[:2] + '">'
    localeHelpHtml = localeHelpHtml.replace(defaultEncoding, localeEncoding)

    for sub in PSE.getSubroutineDirs():
        includeCheck = sub + ' help section html -->'
        if includeCheck in localeHelpHtml:
            continue

        targetPath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'Subroutines', sub, 'help.html')
        subroutineHelp = PSE.genericReadReport(targetPath)
        localeHelpHtml += subroutineHelp

    PSE.genericWriteReport(localeHelpFileLocation, localeHelpHtml)

    return


"""Bundle translation methods"""


def translateBundle():
    """Mini controller to translate the bundle and help file."""

    # allBundles = getAllBundles()
    # makeTranslatedBundle(allBundles)

    translateHelpHtml()

    return

def makeTranslatedBundle(textBundle):
    """Makes the plugin.<locale>.json file from getAllTextBundles()"""

    if PSE.psLocale()[:2] == 'en':
        return

    fileName = 'plugin.' + PSE.psLocale()[:2] + '.json'
    targetFile = PSE.OS_PATH.join(PSE.BUNDLE_DIR, fileName)

    translation = batchTranslator(textBundle)
    PSE.genericWriteReport(targetFile, translation)

    return

def translateHelpHtml():
    """Translate the help html one line at a time.
        Use re to cull out only the text portions of the help html.
        Breaking re up into 3 patterns seems more managable.
        """

    translator = Translator()
    translator.setTranslationService()
    translatedHelpHtml = ''

    pPattern = re.compile('(<p>)(.+)(<.+>)') # finds <p>Overview of this plugin</p>
    hPattern = re.compile('(<h.>)(.+)(<.+>)') # finds <h2>Pattern Scripts plugin</h2>
    fPattern = re.compile('(.+<font.+>)(.+)(<.+>|<.+>.+)') # finds <p><font color="green">User editable keys are described in green.</font></p>

    templateFileName = 'Help.en.html'
    templateFileLocation = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', templateFileName)
    baseHelpHtml = PSE.genericReadReport(templateFileLocation)
    i = 0
    for line in baseHelpHtml.splitlines():
        # if i == 5:
        #     break
        tLine = ''
        if pPattern.match(line) != None:
            search = pPattern.match(line)
            tLine = search.group(2)

        elif hPattern.match(line) != None:
            search = hPattern.match(line)
            tLine = search.group(2)
            
        elif fPattern.match(line) != None:
            search = fPattern.match(line)
            tLine = search.group(2)

        if tLine:
            translation = translator.translateSingle(tLine)
            translatedLine = translation['translations'][0]['text']
            line = line.replace(tLine, translatedLine)
            translatedHelpHtml += line + '\n'
            i += 1
        else:
            translatedHelpHtml += line + '\n'

    translatedFileName = 'Help.' + PSE.psLocale()[:2] + '.html'
    localeHelpFileLocation = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', translatedFileName)
    PSE.genericWriteReport(localeHelpFileLocation, translatedHelpHtml)

    return

def validateKeyFile():
    """Checks that the keys.py file exists
        Called by:
        Main.View
        """

    itemTarget =  PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'Keys.py')
    if PSE.JAVA_IO.File(itemTarget).isFile():
        return True
    else:
        _psLog.warning('Authentication key file not found')
        print('Authentication key file not found')
        return False



def batchTranslator(textBundle):
    """Mini controller translates each item in the bundleFile,
        then appends it to the RAM based scratchFile.
        used by:
        makeTranslatedBundle
        """

    startTime = PSE.TIME.time()

    translation = {}

    inputBundle = textBundle.splitlines()

    translator = Translator()
    translator.setTranslationService()
    translator.translateItems(inputBundle)

    batchTranslation = translator.makeDictionary()
    translation = PSE.dumpJson(batchTranslation)

    runTime = PSE.TIME.time() - startTime
    _psLog.info('Bundle translation time: ' + str(round(runTime, 2)))

    return translation

class Translator:
    """Choice of translators from PSE.readConfigFile('CP')['TS']"""

    def __init__(self):

        controlPanel = PSE.readConfigFile('Main Script')['CP']
        self.translatorChoice = controlPanel['TS'][controlPanel['TC']]

        self.translationDict = {}
        self.tempResult = []
        self.scratchFile = []

        return

    def setTranslationService(self):
        """Gets the translator from readConfigFile('CP')['TC']
            Example: self.translationService = Translators.UseDeepL()"""

        self.translationService = getattr(Translators, self.translatorChoice)()

        return

    def translateSingle(self, singleItem):
        """Translate items one at a time."""

        encodedItem = unicode(singleItem, PSE.ENCODING)
        url = self.translationService.getTheUrl(encodedItem)
        response = urlopen(url)
        translation = PSE.loadJson(response.read())
        response.close()

        


        return translation

    def translateItems(self, bundleFile):
        """Based on https://gist.github.com/snim2/561630"""

    # Meter the items to be translated
        i = 0
        for item in bundleFile:
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
            if len(self.scratchFile) == len(bundleFile):
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



# def makeHelpBundle():
#     """Makes the help.<locale>.json file from bundle.help.txt"""

#     itemTarget = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'bundle.help.txt')
#     textBundle = PSE.genericReadReport(itemTarget)

#     fileName = 'help.' + PSE.psLocale()[:2] + '.json'
#     targetFile = PSE.OS_PATH.join(PSE.BUNDLE_DIR, fileName)

#     if not PSE.JAVA_IO.File(targetFile).isFile():
#         translation = batchTranslator(textBundle)
#         PSE.genericWriteReport(targetFile, translation)

#     return



# def makeHelpPage():
#     """Makes the help page for the current locale.
#         Defaults to english on errors.
#         Called by:
#         Main.Controller.rsItemSelected
#         Main.Controller.ptItemSelected
#         """

#     helpPageTemplatePath = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'help.html.txt')
#     helpPageTemplate = PSE.genericReadReport(helpPageTemplatePath)

#     helpBundleName = 'help.' + PSE.psLocale()[:2] + '.json'
#     helpBundlePath = PSE.OS_PATH.join(PSE.BUNDLE_DIR, helpBundleName)
#     if not PSE.JAVA_IO.File(helpBundlePath).isFile():
#         helpBundleName = 'help.en.json'
#         helpBundlePath = PSE.OS_PATH.join(PSE.BUNDLE_DIR, helpBundleName)

#     translationLookUp = PSE.loadJson(PSE.genericReadReport(helpBundlePath))

#     for hKey, hValue in translationLookUp.items():
#         hKey = unicode(hKey, PSE.ENCODING)
#         hValue = unicode(hValue, PSE.ENCODING)

#         helpPageTemplate = helpPageTemplate.replace(hKey, hValue)

#     helpPageName = 'help.' + PSE.psLocale()[:2] + '.html'
#     helpPagePath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', helpPageName)
#     PSE.genericWriteReport(helpPagePath, helpPageTemplate)

#     return



    # fileList = PSE.JAVA_IO.File(PSE.BUNDLE_DIR).list()
    # if psLocale in fileList:
    #     bundleFileLocation = PSE.OS_PATH.join(PSE.BUNDLE_DIR, psLocale)

    # localeBundle = PSE.loadJson(PSE.genericReadReport(bundleFileLocation))
    # if len(localeBundle) == len(defaultBundle):
    #     return localeBundle
    # else:
    #     return defaultBundle


    
# def validateHelpBundle():
#     """If any files are damaged,
#         if the length of BUNDLE and getAllTextBundles are not the same,
#         if plugin.en.json is missing:
#         make the default help bundle."""

#     defaultBundle = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'help.en.json')
#     if not PSE.JAVA_IO.File(defaultBundle).isFile():
#         _psLog.warning('FAIL: default help bundle file missing. Nwe file created.')
#         makeDefaultHelpBundle()

#     helpTextBundle = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'bundle.help.txt')
#     try:
#         helpTextBundle = PSE.genericReadReport(helpTextBundle).splitlines()
#         helpTextBundle = list(set(helpTextBundle))
#         helpTextBundleLength = len(helpTextBundle)
#     except:
#         helpTextBundleLength = 0

#     fileName = 'help.' + PSE.psLocale()[:2] + '.json'
#     targetFile = PSE.OS_PATH.join(PSE.BUNDLE_DIR, fileName)
#     if not PSE.JAVA_IO.File(targetFile).isFile():
#         fileName = 'help.en.json'
#         targetFile = PSE.OS_PATH.join(PSE.BUNDLE_DIR, fileName)

#     try:
#         helpBunde = PSE.loadJson(PSE.genericReadReport(targetFile))
#         helpBundleLength = len(helpBunde)
#     except:
#         helpBundleLength = 1

#     if helpTextBundleLength != helpBundleLength:
#         fileName = 'help.' + PSE.psLocale()[:2] + '.json'
#         oldFile = PSE.OS_PATH.join(PSE.BUNDLE_DIR, fileName)
#         PSE.JAVA_IO.File(oldFile).delete()

#         fileName = 'help.' + PSE.psLocale()[:2] + '.html'
#         oldFile = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', fileName)
#         PSE.JAVA_IO.File(oldFile).delete()

#         _psLog.warning('FAIL: help bundle length mismatch, rebuilding help bundle file.')
#         makeDefaultHelpBundle()

#     return

# def makeDefaultHelpBundle():
#     """Makes the default english help bundle without using the translator."""

#     defaultBundle = {}
#     bundleFileLocation = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'help.en.json')

#     helpTextBundle = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'bundle.help.txt')
#     helpTextBundle = PSE.genericReadReport(helpTextBundle).splitlines()
#     for bundleItem in helpTextBundle:
#         defaultBundle[bundleItem] = bundleItem

#     defaultBundle = PSE.dumpJson(defaultBundle)
#     PSE.genericWriteReport(bundleFileLocation, defaultBundle)

#     return

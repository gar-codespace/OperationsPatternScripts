# coding=utf-8
# © 2023 Greg Ritacco

"""
Choose or create a language translation bundle for the current locale.
"""

from opsEntities import PSE
from opsBundle import Translators

from urllib2 import urlopen, HTTPError
import re

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

PSE.BUNDLE_DIR = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle')

_psLog = PSE.LOGGING.getLogger('OPS.OB.Bundle')


class CreateStubFile:
    """
    Copy of the JMRI Java version of CreateStubFile.
    The stub file will substitute english in the help file if the current locale doesn't exist.
    """

    def __init__(self):

        self.stubLocation = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getPreferencesPath(), 'jmrihelp', PSE.psLocale()[:2])

        self.helpFilePath = ''
        self.newStubFile = ''

        return

    def validateStubLocation(self):

        if PSE.JAVA_IO.File(self.stubLocation).mkdirs():
            _psLog.info('Stub location created at: ' + self.stubLocation)
        else:
            _psLog.info('Stub location already exists')

        return

    def getHelpFileURI(self):

        helpFileName = 'help.' + PSE.psLocale()[:2] + '.html'
        helpFilePath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', helpFileName)

        if not PSE.JAVA_IO.File(helpFilePath).isFile():
            helpFileName = 'help.en.html'
            helpFilePath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsSupport', helpFileName)

        self.helpFilePath = PSE.JAVA_IO.File(helpFilePath).toURI().toString()

        return

    def makeNewStubFile(self):

        stubTemplateFile = 'stub_template.html'
        stubTemplatePath = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getProgramPath(), 'help', PSE.psLocale()[:2], 'local', stubTemplateFile)
        if not PSE.JAVA_IO.File(stubTemplatePath).isFile():
            stubTemplatePath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsEntities', stubTemplateFile)

        stubTemplate = PSE.genericReadReport(stubTemplatePath)
        stubTemplate = stubTemplate.replace("../index.html#", "")
        stubTemplate = stubTemplate.replace("<!--HELP_KEY-->", self.helpFilePath)
        self.newStubFile = stubTemplate.replace("<!--URL_HELP_KEY-->", "")

        return

    def writeStubFile(self):

        _psLog.debug('CreateStubFile.writeStubFile')

        stubFilePath = PSE.OS_PATH.join(self.stubLocation, 'psStub.html')
        PSE.genericWriteReport(stubFilePath, self.newStubFile)

        return

    def make(self):
        """
        Mini controller.
        """

        self.validateStubLocation()
        self.getHelpFileURI()
        self.makeNewStubFile()
        self.writeStubFile()

        return


"""Bundle and Help methods"""


def setupBundle():
    """
    Mini controller to set up the bundles.
    """

# Plugin bundle stuff
    
    makeDefaultPluginBundle()
    PSE.BUNDLE = getBundleForLocale()

# Help bundle stuff
    CreateStubFile().make()
    makeDefaultHelpFile() # Default help file is in english
    validateHelpForLocale()
    updateHelpFileForLocale()

    return


"""Bundle methods"""


def makeDefaultPluginBundle():
    """
    Makes the default english plugin bundle without using the translator.
    """

    defaultBundle = {}
    allBundles = getAllBundles()
    bundleFileLocation = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'plugin.en.json')

    allBundles = allBundles.splitlines()
    for bundleItem in allBundles:
        defaultBundle[bundleItem] = bundleItem

    defaultBundle = PSE.dumpJson(defaultBundle)
    PSE.genericWriteReport(bundleFileLocation, defaultBundle)

    return

def getBundleForLocale():
    """
    Gets the bundle json for the current locale if it exists, otherwise english.
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
            print('Bundle item not found: ' + translation)
            compositeBundle[item] = translation

    return compositeBundle

def getAllBundles():
    """
    Gets the bundle file for each subroutine.
    """

    targetPath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'opsBundle', 'bundle.txt')
    pluginBundle = PSE.genericReadReport(targetPath)

    allSubs = PSE.getSubroutineDirs()
    for sub in allSubs:
        targetPath = PSE.OS_PATH.join(PSE.PLUGIN_ROOT, 'Subroutines', sub, 'bundle.txt')
        subroutineBundle = PSE.genericReadReport(targetPath)
        pluginBundle += subroutineBundle

    return pluginBundle


"""Help methods"""


def makeDefaultHelpFile():
    """
    Gather up all the help.html.txt files and combine them into Help.en.html
    """

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
    """
    Checks that a help html exists for the current locale.
    If not, copy the default english version as the current locales' help file.
    """

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
    """
    Checks that all the activated subroutines have entries in the help html for the current locale.
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


"""Bundle and Help translation methods"""


def validateKeyFile():
    """
    Checks that the keys.py file is valid.
    Called by:
    Main Script.View
    """

    returnValue = True

    itemTarget =  PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'Keys.py')
    if not PSE.JAVA_IO.File(itemTarget).isFile():
        _psLog.warning('Authentication key file not found')
        print('Authentication key file not found')
        returnValue = False

    translator = Translator()
    translator.setTranslationService()
    # if not translator.testTranslationService():
    #     returnValue = False
    
    return returnValue

def translateBundles():
    """
    Makes the plugin.<locale>.json file from getAllBundles()
    """

    if PSE.psLocale()[:2] == 'en':
        return

    fileName = 'plugin.' + PSE.psLocale()[:2] + '.json'
    targetFile = PSE.OS_PATH.join(PSE.BUNDLE_DIR, fileName)

    allBundles = getAllBundles()
    translation = batchTranslator(allBundles)
    PSE.genericWriteReport(targetFile, translation)

    return

def translateHelpHtml():
    """
    Translate the help html one line at a time.
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

def batchTranslator(textBundle):
    """
    Mini controller translates each item in the bundleFile,
    then appends it to the RAM based scratchFile.
    used by:
    translateBundles
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
    """
    Choice of translators from PSE.readConfigFile('CP')['TS']
    """

    def __init__(self):

        self.controlPanel = PSE.readConfigFile('Main Script')['CP']
        self.translatorChoice = self.controlPanel['TS'][self.controlPanel['TC']]

        self.translationDict = {}
        self.tempResult = []
        self.scratchFile = []

        return

    def setTranslationService(self):
        """
        Gets the translator from readConfigFile('CP')['TC']
        Example: self.translationService = Translators.UseDeepL()
        """

        self.translationService = getattr(Translators, self.translatorChoice)()

        return
    
    def testTranslationService(self):
        """
        On start of the plugin, test that the translation service is available.
        """

        url = self.translationService.testTheService()
        try:
            response = urlopen(url)
            response.close()
            _psLog.info('PASS: Translation service check')
            return True
        except HTTPError as error:
            errorCode = self.controlPanel['EC'][str(error.code)]
            _psLog.warning('FAIL: Translation service check: ' + errorCode)
            return False

    def translateSingle(self, singleItem):
        """
        Translate items one at a time.
        """

        encodedItem = unicode(singleItem, PSE.ENCODING)
        url = self.translationService.getTheUrl(encodedItem)
        response = urlopen(url)
        translation = PSE.loadJson(response.read())
        response.close()

        return translation

    def translateItems(self, bundleFile):
        """
        Based on https://gist.github.com/snim2/561630
        """

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
    """
    Homebrew version of concurrency.
    """

    def init(self):

        return

    def passInAttributes(self, scratchFile, url, item):

        self.scratchFile = scratchFile
        self.url = url
        self.item = item

        return

    def handle(self):
        """
        Harden this against errors.
        """

        translation = {}
        response = None
        name = []

        for i in range(3):
            try:
                response = urlopen(self.url)
                translation = PSE.loadJson(response.read())
                response.close()
            except:
                print('Exception at: Bundle.handle')
                _psLog.warning('Not translated: ' + self.item)
            if response:
                break
            PSE.TIME.sleep(.05)

        translation['source'] = self.item
        translation['error'] = self.item

        self.scratchFile.append(translation)

        return False


def translateUtility():
    """
    Utility to translate the TrainPlayer side bundle files.
    Translates one line at a time, so it's slow.
    Preserves line order.
    Translate other text files that need it.
    """

    controlPanel = PSE.readConfigFile('Main Script')['CP']
    translatorChoice = controlPanel['TS'][controlPanel['TC']]
    translationService = getattr(Translators, translatorChoice)()

# TrainPlayer bundle files
    bundleFiles = ['Help.txt', 'Message.txt', 'o2o.txt', 'Utility.txt']
    # bundleFiles = ['Help.txt']
    locale = PSE.psLocale()[:2]
    targetDir = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'TrainPlayer', locale)
    PSE.JAVA_IO.File(targetDir).mkdir()

    for file in bundleFiles:
        translatedFile = ''
        source = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'TrainPlayer', 'en', file)
        sourceFile = PSE.genericReadReport(source)
        for line in sourceFile.splitlines():
            encodedItem = unicode(line, PSE.ENCODING)
            url = translationService.getTheUrl(encodedItem)
            response = urlopen(url)
            translation = PSE.loadJson(response.read())
            response.close()
            translatedFile += translation['translations'][0]['text'] + '\n'

        destination = PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'TrainPlayer', locale, file)
        PSE.genericWriteReport(destination, translatedFile)

    return

# coding=utf-8
# © 2023 Greg Ritacco

"""
Bundle translation services.
The Translation Services offered are in configFile('CP')['TS']
The Translation Choice is configFile('CP')['TC']
"""

from urllib import urlencode
from urllib2 import urlopen

from opsEntities import PSE
try:
    from opsBundle import Keys
except ImportError:
    print('Keys module not found')

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.OB.Translators')


class UseDeepL:
    """
    Specifics for using DeepL
    Format:
    https://api-free.deepl.com/v2/translate?auth_key=e331f340-8f59-dc09-0df7-44c5cab582f4%3Afx&text=Locomotives+at&source_lang=en&target_lang=de&split_sentences=0
    """

    def __init__(self):

        self.BASE_URL = 'https://api-free.deepl.com/v2/translate?'
        self.DOCUMENT_URL = 'https://api-free.deepl.com/v2/document?'
        self.AUTH_KEY = None

        self.SOURCE_LANG = 'en'

        return
    
    def testTheService(self):

        returnValue = True
        returnValue = self.checkKeyLocation()
        returnValue = self.checkKey()
        returnValue = self.testKey()

        # testURL = self.getTheUrl('test')

        return returnValue
    
    def checkKeyLocation(self):

        itemTarget =  PSE.OS_PATH.join(PSE.BUNDLE_DIR, 'Keys.py')
        if PSE.JAVA_IO.File(itemTarget).isFile():
            _psLog.debug('File found: Keys.py')
            print('File found: Keys.py')
            return True
        else:
            _psLog.warning('File not found: Keys.py')
            print('File not found: Keys.py')
            return False
        
    def checkKey(self):
        """
        Checks Keys.py for a constant: DEEPL_KEY
        """

        try:
            self.AUTH_KEY = Keys.DEEPL_KEY
            _psLog.debug('Validated attribute: Keys.DEEPL_KEY')
            print('Validated attribute: Keys.DEEPL_KEY')
            return True
        except:
            _psLog.warning('Validation failed: Keys.DEEPL_KEY')
            print('Validation failed: Keys.DEEPL_KEY')
            return False
        
    def testKey(self):
        """
        Tests the the provided key actually works.
        """

        try:
            url = self.getTheUrl('Test Message')
            response = urlopen(url)
            response.close()
            _psLog.debug('Validated key: Keys.DEEPL_KEY')
            print('Validated key: Keys.DEEPL_KEY')
            return True
        except:
             print('Invalid key: Keys.DEEPL_KEY')
             _psLog.warning('Invalid key: Keys.DEEPL_KEY')
             return False
    
    def getTheUrl(self, item):

        params = urlencode( (('auth_key', self.AUTH_KEY),
                                 ('text', item.encode(PSE.ENCODING)),
                                 ('source_lang', self.SOURCE_LANG),
                                 ('target_lang', PSE.psLocale()),
                                 ('split_sentences', 0))
                                 )

        return self.BASE_URL + params

    def parseResult(self, response):

        source = response['source']
        error = response['error']
        try:
            translation = response['translations'][0]['text']
        except:
            print('Exception at: Translators.UseDeepL.parseResult')
            translation = error

        return (source, translation)
    
    def errorCodes(self):
    
        EC =   {400 : "400 - Bad Request: Unable to translate the current language.", \
                402 : "402 - Requested page not found", \
                403 : "403 - Forbidden. The key is invalid.", \
                456 : "456 - Usage limits exceeded."}
        
        return EC

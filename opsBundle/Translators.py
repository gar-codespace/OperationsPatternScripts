# coding=utf-8
# © 2023 Greg Ritacco

"""
Bundle translation services.
The Translation Services offered are in configFile('CP')['TS']
The Translation Choice is configFile('CP')['TC']
"""

from urllib import urlencode

from opsEntities import PSE
try:
    from opsBundle import Keys
except:
    print('Exception at: Translators.from opsBundle import Keys')
    pass

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

class UseDeepL:
    """Specifics for using DeepL"""

    def __init__(self):

        self.BASE_URL = 'https://api-free.deepl.com/v2/translate?'
        self.DOCUMENT_URL = 'https://api-free.deepl.com/v2/document?'
        self.AUTH_KEY = Keys.DEEPL_KEY
        self.SOURCE_LANG = 'en'

        return

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

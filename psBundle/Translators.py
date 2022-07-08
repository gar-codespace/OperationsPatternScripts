# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Bundle translation services."""

from urllib import urlencode

from psEntities import PatternScriptEntities
try:
    from psBundle import Keys
except:
    pass
    
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
                                 ('text', item.encode(PatternScriptEntities.ENCODING)),
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

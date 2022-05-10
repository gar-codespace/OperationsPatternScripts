# coding=utf-8
# © 2021, 2022 Greg Ritacco

from json import loads as jsonLoads
from codecs import open as codecsOpen

from psEntities import PatternScriptEntities

def getBundleForLocale(SCRIPT_ROOT):
    '''To be expanded in Version 3'''

    locale = PatternScriptEntities.psLocale()

    bundleFileLocation = SCRIPT_ROOT + '\\psBundle\\en.json'

    with codecsOpen(bundleFileLocation, 'r', encoding=PatternScriptEntities.setEncoding()) as workingFile:
        bundleFile = jsonLoads(workingFile.read())

    return bundleFile

# coding=utf-8
# © 2021, 2022 Greg Ritacco

from java import io as javaIo

from json import loads as jsonLoads
from codecs import open as codecsOpen

from psEntities import PatternScriptEntities

def getBundleForLocale(SCRIPT_ROOT):
    '''To be expanded in Version 3'''

    psLocale = PatternScriptEntities.psLocale() + '.json'
    bundleDir = SCRIPT_ROOT + '\\psBundle\\'
    fileList = javaIo.File(bundleDir).list()

    if psLocale in fileList:
        bundleFileLocation = bundleDir + psLocale
    else:
        bundleFileLocation = bundleDir + 'en.json'

    with codecsOpen(bundleFileLocation, 'r', encoding=PatternScriptEntities.setEncoding()) as workingFile:
        bundleFile = jsonLoads(workingFile.read())

    return bundleFile

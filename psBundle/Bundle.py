# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities

def getBundleForLocale(SCRIPT_ROOT):

    psLocale = PatternScriptEntities.psLocale() + '.json'
    bundleDir = SCRIPT_ROOT + '\\psBundle\\'
    fileList = PatternScriptEntities.JAVA_IO.File(bundleDir).list()

    if psLocale in fileList:
        bundleFileLocation = bundleDir + psLocale
    else:
        bundleFileLocation = bundleDir + 'en.json'

    bundleFile = PatternScriptEntities.genericReadReport(bundleFileLocation)
    bundleFile = PatternScriptEntities.loadJson(bundleFile)

    return bundleFile

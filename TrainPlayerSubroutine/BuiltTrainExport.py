# coding=utf-8
# © 2021, 2022 Greg Ritacco

import jmri
import java

import logging
import time
from json import loads as jsonLoads, dumps as jsonDumps
from HTMLParser import HTMLParser
from codecs import open as codecsOpen
from os import mkdir as osMakeDir
from sys import path as sysPath

SCRIPT_NAME ='OperationsPatternScripts.TrainPlayerSubroutine.BuiltTrainExport'
SCRIPT_REV = 20220101

SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b2'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b3'

SCRIPT_ROOT = jmri.util.FileUtil.getPreferencesPath() + SCRIPT_DIR
sysPath.append(SCRIPT_ROOT)

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import Model

class ManifestForTrainPlayer(jmri.jmrit.automat.AbstractAutomaton):
    '''Runs on JMRI train manifest builds'''

    def init(self):

        self.SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.BuiltTrainExport.ManifestForTrainPlayer'
        self.SCRIPT_REV = 20220101

        logPath = jmri.util.FileUtil.getProfilePath() + 'operations\\buildstatus\\BuiltTrainExportLog.txt'
        self.logger = PatternScriptEntities.Logger(logPath)
        self.logger.startLogger('TP')

        return

    def passInTrain(self, train):

        self.train = train

        return

    def handle(self):

        timeNow = time.time()

        self.tpLog = logging.getLogger('TP.BuiltTrainExport')
        self.logger.initialLogMessage(self.tpLog)

        Model.CheckTpDestination().directoryExists()

        jmriExport = Model.ExportJmriLocations()
        locationList = jmriExport.makeLocationList()
        jmriExport.toTrainPlayer(locationList)
        self.tpLog.info('Export JMRI locations to TrainPlayer')

        jmriManifestTranslator = Model.JmriTranslationToTp()
        builtTrainAsDict = jmriManifestTranslator.getTrainAsDict(self.train)
        translatedManifest = jmriManifestTranslator.translateManifestHeader(builtTrainAsDict)
        translatedManifest['locations'] = jmriManifestTranslator.translateManifestBody(builtTrainAsDict)

        processedManifest = Model.ProcessWorkEventList()
        processedManifest.writeTpWorkEventListAsJson(translatedManifest)
        tpManifestHeader = processedManifest.makeTpHeader(translatedManifest)
        tpManifestLocations = processedManifest.makeTpLocations(translatedManifest)

        Model.WriteWorkEventListToTp(tpManifestHeader + tpManifestLocations).asCsv()

        self.tpLog.info('Export JMRI manifest to TrainPlyer: ' + self.train.getName())
        self.tpLog.info('Export to TrainPlayer script location: ' + SCRIPT_ROOT)
        self.tpLog.info('Manifest export (sec): ' + ('%s' % (time.time() - timeNow))[:6])

        print(self.SCRIPT_NAME + ' ' + str(self.SCRIPT_REV))
        print('Manifest export (sec): ' + ('%s' % (time.time() - timeNow))[:6])

        self.logger.stopLogger('TP')

        return False

if __name__ == "__builtin__":
    ManifestForTrainPlayer().start()

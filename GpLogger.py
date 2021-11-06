# coding=utf-8
# Extended ìÄÅÉî
# general purpose logger
# No restrictions on use
# © 2021 Greg Ritacco

import logging

class gpLogging():
    '''General purpose logger.'''

    def __init__(self, logName):
        self.logger = logging.getLogger(logName)
        self.logger.setLevel(10)
        self.scriptRev = 'GpLogger 20211101'
        return

    def gpStartLogFile(self, path, level):
        self.logFileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.gpfh = logging.FileHandler(path, mode='w', encoding='utf-8')
        self.gpfh.setLevel(level)
        self.gpfh.setFormatter(self.logFileFormat)
        self.logger.addHandler(self.gpfh)
        print('OperationsGPLogging ' + self.scriptRev)
        return self.gpfh

    def gpStopLogFile(self, yHandle):
        self.logger.removeHandler(yHandle)
        return

    def gpDebug(self, message=''):
        self.logger.debug(message)
        return

    def gpInfo(self, message=''):
        self.logger.info(message)
        return

    def gpWarning(self, message=''):
        self.logger.warning(message)
        return

    def gpError(self, message=''):
        self.logger.error(message)
        return

    def gpCritical(self, message=''):
        self.logger.critical(message)
        return

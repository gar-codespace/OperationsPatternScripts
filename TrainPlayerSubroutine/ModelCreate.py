# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities

import org.w3c.dom
import javax.xml.parsers

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.ModelCreate'
SCRIPT_REV = 20220101


class NewJmriRailroad:

    def __init__(self):

        self.ops = PatternScriptEntities.JMRI.jmrit.operations.setup.OperationsSetupXml()
        self.location =  PatternScriptEntities.JMRI.jmrit.operations.locations.LocationManagerXml()
        self.car = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarManagerXml()
        self.loco =  PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.EngineManagerXml()
        self.train = PatternScriptEntities.JMRI.jmrit.operations.trains.TrainManagerXml()

        rrFile = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRailroadData.json'
        TpRailroad = PatternScriptEntities.genericReadReport(rrFile)
        self.TpRailroad = PatternScriptEntities.loadJson(TpRailroad)

        return

    def deleteXml(self):

        return

    def initializeXml(self):
        """Creates the 5 xml files. Routes is not built since there is no TP equivalent"""

        self.ops.initialize()
        self.location.initialize()
        self.car.initialize()
        self.loco.initialize()
        self.train.initialize()

        return

    def writeXml(self):

        self.ops.writeOperationsFile()
        self.location.writeOperationsFile()
        self.car.writeOperationsFile()
        self.loco.writeOperationsFile()
        self.train.writeOperationsFile()

        return


    def setupOperations(self):

        PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.setRailroadName(self.TpRailroad['railroadName'])
        PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.setComment(self.TpRailroad['railroadDescription'])
        PatternScriptEntities.JMRI.jmrit.operations.setup.Setup.setMainMenuEnabled(True)

        return

    def updateRoads(self):

        tpRoads = self.TpRailroad['roads']

        workFilePath = PatternScriptEntities.PROFILE_PATH + 'operations\\OperationsCarRoster.xml'
        textWorkFile = PatternScriptEntities.JAVA_IO.File(workFilePath)

        tree = javax.xml.parsers.DocumentBuilder.parse(textWorkFile)



        return

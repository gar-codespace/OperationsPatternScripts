# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities

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

        return

    def addRoads(self):

        tpRoads = self.TpRailroad['roads']

        x = PatternScriptEntities.PROFILE_PATH + 'operations\\OperationsCarRoster.xml'
        y = PatternScriptEntities.JAVA_IO.File(x)
        root = self.car.rootFromFile(y)


        topElement = root.getChild('roads')
        topElement.addContent('testing')



        print(topElement.getContentSize())
        z = topElement.getChildren()
        for _ in range(len(z)):
            topElement.removeChild('road')
            print('l')



        # carHack = PatternScriptEntities.HackXml('OperationsCarRoster')
        # carHack.getXmlTree()
        # carHack.updateXmlElement('roads', tpRoads)
        # carHack.patchUpDom(u'<!DOCTYPE operations-config SYSTEM "/xml/DTD/operations-cars.dtd">')
        # carHack.saveUpdatedXml()

        return

# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities
from TrainPlayerSubroutine import ModelXml

# import org.w3c.dom
# import javax.xml.parsers
# import javax.xml.parsers.DocumentBuilder
# import javax.xml.parsers.DocumentBuilderFactory

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

    def updateRsRosters(self):
        """Mini Controller to update the OperationsCarRoster.xml roads and types elements
            and the OperationsEngineRoster.xml ??? elements
            """

        updatedOperationsCarRoster = MakeAllTpRosters()
        updatedOperationsCarRoster.checkList()

        carHack = ModelXml.HackXml('OperationsCarRoster')
        carHack.getXmlTree()

        allTpItems = updatedOperationsCarRoster.getAllTpRoads()
        carHack.updateXmlElement('roads', allTpItems)

        allTpItems = updatedOperationsCarRoster.getAllTpCarAar()
        carHack.updateXmlElement('types', allTpItems)


        allTpItems = updatedOperationsCarRoster.getAllTpLoads()
        carHack.updateXmlLoads('loads', allTpItems)


        carHack.patchUpDom(u'<!DOCTYPE operations-config SYSTEM "/xml/DTD/operations-cars.dtd">')
        carHack.saveUpdatedXml()

        locoHack = ModelXml.HackXml('OperationsEngineRoster')
        locoHack.getXmlTree()

        allTpItems = updatedOperationsCarRoster.getAllTpLocoTypes()
        locoHack.updateXmlElement('types', allTpItems)

        allTpItems = updatedOperationsCarRoster.getAllTpLocoModels()
        locoHack.updateXmlElement('models', allTpItems)

        locoHack.patchUpDom(u'<!DOCTYPE operations-config SYSTEM "/xml/DTD/operations-engines.dtd">')
        locoHack.saveUpdatedXml()

        return


class MakeAllTpRosters:

    def __init__(self):

        self.tpInventoryFile = 'TrainPlayer Report - Inventory.txt'
        self.tpLocationsFile = 'TrainPlayer Report - Locations.txt'
        self.tpLoadsFile = 'TrainPlayer Report - Industries.txt'
        self.tpInventory = []
        self.tpLocations = []
        self.tpLoads = []

        self.allTpAar = []
        self.allTpCarAar = []
        self.allTpLocoAar = []
        self.allTpRoads = []
        self.allTpLoads = []

        self.allJmriRoads = []

        return

    def checkList(self):

        try:
            self.tpInventory = ModelEntities.getTpExport(self.tpInventoryFile)
            self.tpInventory.pop(0) # Remove timestamp
            self.tpInventory.pop(0) # Remove the key
        except:
            pass

        try:
            self.tpLocations = ModelEntities.getTpExport(self.tpLocationsFile)
            self.tpLocations.pop(0) # Remove timestamp
            self.tpLocations.pop(0) # Remove the railroad name
            self.tpLocations.pop(0) # Remove the railroad description
            self.tpLocations.pop(0) # Remove the key
        except:
            pass

        try:
            self.tpLoads = ModelEntities.getTpExport(self.tpLoadsFile)
            self.tpLoads.pop(0) # Remove timestamp
            self.tpLoads.pop(0) # Remove the key
        except:
            pass

    def getAllTpRoads(self):

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            road, number = ModelEntities.parseCarId(splitItem[0])
            self.allTpRoads.append(road)

        self.allTpRoads = list(set(self.allTpRoads))

        return self.allTpRoads

    def getAllTpCarAar(self):

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('E'):
                continue
            else:
                self.allTpCarAar.append(splitItem[2])

        return list(set(self.allTpCarAar))

    def getAllTpLoads(self):

        loadFlag = self.tpLoads.pop(0)

        tpLoadScratch = []
        for lineItem in self.tpLoads:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('E'):
                continue
            else:
                tpLoadScratch.append((splitItem[4], splitItem[6]))

        carAarList = list(set(self.allTpCarAar))
        for aar in carAarList:
            tempList = [u'Load']
            for xAar, xLoad in tpLoadScratch:
                if aar == xAar:
                    tempList.append(xLoad)
            self.allTpLoads.append({aar: list(set(tempList))})

        return self.allTpLoads

    def getAllTpLocoTypes(self):
        """Don't include tenders"""

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('ET'):
                continue
            if splitItem[2].startswith('E'):
                self.allTpLocoAar.append(splitItem[2])

        return list(set(self.allTpLocoAar))

    def getAllTpLocoModels(self):
        """JMRI Loco models limited to 12 characters
            Don't include tenders
            """

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('ET'):
                continue
            if splitItem[2].startswith('E'):
                self.allTpLocoAar.append(splitItem[1][0:11])

        return list(set(self.allTpLocoAar))

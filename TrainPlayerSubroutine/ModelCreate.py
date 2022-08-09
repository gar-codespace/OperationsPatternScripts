# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""From tpRailroadData.json, a new rr is created and the xml files are seeded"""

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities
from TrainPlayerSubroutine import ModelXml

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.ModelCreate'
SCRIPT_REV = 20220101


class NewJmriRailroad:

    def __init__(self):

        self.Operations = PatternScriptEntities.JMRI.jmrit.operations.setup.OperationsSetupXml()
        self.OperationsCarRoster = PatternScriptEntities.CMX
        self.OperationsEngineRoster =  PatternScriptEntities.EMX
        self.OperationsLocationRoster =  PatternScriptEntities.LMX

        rrFile = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRailroadData.json'
        TpRailroad = PatternScriptEntities.genericReadReport(rrFile)
        self.TpRailroad = PatternScriptEntities.loadJson(TpRailroad)

        # self.train = PatternScriptEntities.JMRI.jmrit.operations.trains.TrainManagerXml()
        # self.OperationsCarRoster = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarManagerXml()
        # self.OperationsEngineRoster =  PatternScriptEntities.JMRI.jmrit.operations.rollingstock.engines.EngineManagerXml()
        # self.OperationsLocationRoster =  PatternScriptEntities.JMRI.jmrit.operations.locations.LocationManagerXml()
        return

    def addNewXml(self):
        """Creates the 4 xml files if they are not already built.
            Routes is not built since there is no TP equivalent.
            Trains is not built since JMRI trains is the point of this plugin.
            """

        pathPrefix = PatternScriptEntities.PROFILE_PATH + 'operations\\'
        xmlList = ['Operations', 'OperationsCarRoster', 'OperationsEngineRoster', 'OperationsLocationRoster']
        for file in xmlList:
            filePath = pathPrefix + file + '.xml'
            if PatternScriptEntities.JAVA_IO.File(filePath).isFile():
                continue

            getattr(self, file).initialize()
            getattr(self, file).writeOperationsFile()\
            # getattr(self, file).setDirty(True)

        return

    def writeXml(self):

        self.Operations.writeOperationsFile()
        self.OperationsLocationRoster.writeOperationsFile()
        self.OperationsCarRoster.writeOperationsFile()
        self.OperationsEngineRoster.writeOperationsFile()

        return

    def initializeXml(self):
        """  """

        self.Operations.initialize()
        self.OperationsLocationRoster.initialize()
        self.OperationsCarRoster.initialize()
        self.OperationsEngineRoster.initialize()

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

        allTpRosters = MakeAllTpRosters()
        allTpRosters.checkFile()
    # Update car roster
        carHack = ModelXml.HackXml('OperationsCarRoster')
        carHack.getXmlTree()

        allTpItems = allTpRosters.getAllTpRoads()
        carHack.updateXmlElement('roads', allTpItems)

        allTpItems = allTpRosters.getAllTpCarAar()
        carHack.updateXmlElement('types', allTpItems)

        allTpItems = allTpRosters.getAllTpLoads()
        carHack.updateXmlLoads('loads', allTpItems)

        allTpItems = allTpRosters.getAllTpKernels()
        carHack.updateXmlElement('newKernels', allTpItems)

        carHack.patchUpDom(u'<!DOCTYPE operations-config SYSTEM "/xml/DTD/operations-cars.dtd">')
        carHack.saveUpdatedXml()
    # Update loco roster
        locoHack = ModelXml.HackXml('OperationsEngineRoster')
        locoHack.getXmlTree()

        allTpItems = allTpRosters.getAllTpLocoModels()
        locoHack.updateXmlElement('models', allTpItems)

        allTpItems = allTpRosters.getAllTpLocoTypes()
        locoHack.updateXmlElement('types', allTpItems)

        allTpItems = allTpRosters.getAllTpLocoConsists()
        locoHack.updateXmlElement('newConsists', allTpItems)

        locoHack.patchUpDom(u'<!DOCTYPE operations-config SYSTEM "/xml/DTD/operations-engines.dtd">')
        locoHack.saveUpdatedXml()

        return


class MakeAllTpRosters:

    def __init__(self):

        self.tpRailroadData = {}
        self.reportPath = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRailroadData.json'

        self.allTpRoads = []

        self.allTpCarAar = []
        self.allTpLoads = []
        self.allTpCarKernels = []

        self.allTpLocoAar = []
        self.allTpLocoModels = []
        self.allLocoConsists = []

        self.allJmriRoads = []

        return

    def checkFile(self):
        """Fill out the else statement"""

        if PatternScriptEntities.JAVA_IO.File(self.reportPath).isFile():
            tpRailroadData = PatternScriptEntities.genericReadReport(self.reportPath)
            self.tpRailroadData = PatternScriptEntities.loadJson(tpRailroadData)
        else:
            pass

        return

    def getAllTpRoads(self):

        self.allTpRoads = self.tpRailroadData['roads']

        return self.allTpRoads

    def getAllTpCarAar(self):

        self.allTpCarAar = self.tpRailroadData['carAAR']

        return self.allTpCarAar

    def getAllTpLoads(self):
    # Make a list of tuples(aar,load)
        tpLoadScratch = []
        for item, data in self.tpRailroadData['industries'].items():
            tpLoadScratch.append((data['type'], data['load'])) # Tuple(aar, load)

    # Make a list of dictionaries {aar: [loads for that aar]}
        for aar in self.allTpCarAar:
            tempList = [u'Load']
            for xAar, xLoad in tpLoadScratch:
                if aar == xAar:
                    tempList.append(xLoad)
            self.allTpLoads.append({aar: list(set(tempList))})

        return self.allTpLoads

    def getAllTpKernels(self):

        self.allTpCarKernels = self.tpRailroadData['carKernel']

        return self.allTpCarKernels

    def getAllTpLocoModels(self):
        """JMRI Loco models limited to 12 characters
            Don't include tenders
            Read this value from JMRI
            """

        for item in self.tpRailroadData['locoModels']:
            self.allTpLocoModels.append(item[0:11])

        return self.allTpLocoModels

    def getAllTpLocoTypes(self):
        """Don't include tenders"""

        self.allTpLocoAar = self.tpRailroadData['locoTypes']

        return self.allTpLocoAar

    def getAllTpLocoConsists(self):
        """Don't include tenders"""

        self.allLocoConsists = self.tpRailroadData['locoConsists']

        return self.allLocoConsists

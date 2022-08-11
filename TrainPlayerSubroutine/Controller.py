# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""The TrainPlayer Subroutine will be implemented in V3, this is just the framework"""

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelWorkEvents
from TrainPlayerSubroutine import ModelImport
from TrainPlayerSubroutine import ModelCreate
from TrainPlayerSubroutine import View

# from apps import Apps

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.Controller'
SCRIPT_REV = 20220101

class StartUp:
    """Start the TrainPlayer subroutine"""

    def __init__(self, subroutineFrame=None):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.Controller')
        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        self.psLog.info('TrainPlayer makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame"""

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def activateWidgets(self):
        '''Maybe get them by name?'''

        self.widgets[0].actionPerformed = self.railroadImporter
        self.widgets[1].actionPerformed = self.railroadCreator
        self.widgets[2].actionPerformed = self.railroadUpdater

        return

    def railroadImporter(self, EVENT):
        '''Writes a json file from the 3 TrainPlayer report files'''

        trainPlayerImport = ModelImport.TrainPlayerImporter()
        trainPlayerImport.checkFiles()
        trainPlayerImport.makeRrHeader()
        trainPlayerImport.getRrLocations()
        trainPlayerImport.getRrLocales()
        trainPlayerImport.getAllTpRoads()
        trainPlayerImport.getAllTpIndustry()

        trainPlayerImport.getAllTpCarAar()
        trainPlayerImport.getAllTpCarKernels()

        trainPlayerImport.getAllTpLocoTypes()
        trainPlayerImport.getAllTpLocoModels()
        trainPlayerImport.getAllTpLocoConsists()

        trainPlayerImport.writeTPLayoutData()


        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def railroadCreator(self, EVENT):
        '''Creates a new JMRI railroad from the json file'''

        newJmriRailroad = ModelCreate.NewJmriRailroad()
        newJmriRailroad.addNewXml()

        newJmriRailroad.setupOperations()
        newJmriRailroad.updateRsRosters()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def railroadUpdater(self, EVENT):
        '''Updates JMRI railroad from the json file'''

        updatedLocations = ModelCreate.UpdateLocations()
        updatedLocations.checkFile()
        updatedLocations.updateLocations()
        updatedLocations.updateTracks()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

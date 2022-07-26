# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""The TrainPlayer Subroutine will be implemented in V3, this is just the framework"""

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import Model
from TrainPlayerSubroutine import View

from apps import Apps

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

        self.widgets[0].actionPerformed = self.locationUpdator
        self.widgets[1].actionPerformed = self.inventoryUpdator

        return

    def inventoryUpdator(self, EVENT):
        '''Updates JMRI rolling stock locations based on TrainPlayer inventory export'''

        reconsiledInventory = Model.ReconsileInventory()
        if not reconsiledInventory.checkList():
            self.psLog.info('No TrainPlayer inventory list to update')
            return

        reconsiledInventory.getJmriRs()
        reconsiledInventory.makeIdLists()

        reconsiledInventory.getJmriOrphans()
        reconsiledInventory.deleteJmriOrphans()

        reconsiledInventory.getTpOrphans()
        reconsiledInventory.addTpOrphans()

        reconsiledInventory.updateLocations()

        self.psLog.info('Updated Rolling stock locations from TrainPlayer')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def locationUpdator(self, EVENT):
        '''Updates JMRI locations, tracks, and their parameters'''

        Model.updateRoadsAndTypes()




        # x = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarRoads()
        # Apps.revalidate(x)
        #
        # x.updateComboBox()
        # print(dir(x))
        # x = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarEditFrame()
        # Apps.revalidate(x.roadComboBox)
        # x.roadComboBox
        # print(dir(x.roadComboBox))




        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

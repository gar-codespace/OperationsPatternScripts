# coding=utf-8
# © 2023 Greg Ritacco

"""
The o2o Subroutine creates a JMRI railroad from TrainPlayer data.
It also exports a JMRI manifest and Patterns switch list into a Quick Keys work events list.
On the TrainPlayer side, the Quick Keys suite of scripts is used
to import from and export to the JMRI railroad.
"""

from opsEntities import PSE
from Subroutines_Activated.o2o import Model
from Subroutines_Activated.o2o import ModelImport
from Subroutines_Activated.o2o import ModelWorkEvents
from Subroutines_Activated.o2o import View

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Controller')

def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>"""

    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    configFile = PSE.readConfigFile()
    if configFile[subroutineName]['SV']:
        menuText = '{} {}'.format(PSE.getBundleItem('Hide'), __package__)
    else:
        menuText = '{} {}'.format(PSE.getBundleItem('Show'), __package__)
    menuItem.setName(__package__)
    menuItem.setText(menuText)

    return menuItem


class TrainsPropertyParser:
    """
    What get called when any of three listeners are fired:
    preProcess, process, postProcess
    """

    def __init__(self, pce):

        self.propertySource = pce.source
        self.propertyName = pce.propertyName
        self.oldValue = pce.oldValue
        self.newValue = pce.newValue

        return
    
    def preProcess(self):

        if self.propertyName == 'opsPatternReport':
            manifestName = 'ops-Pattern Report.json'
            Model.modifyManifest(manifestName)

        if self.propertyName == 'opsSwitchList':
            manifestName = 'ops-Switch List.json'
            Model.modifyManifest(manifestName)

        if self.propertyName == 'TrainBuilt':
            manifestName = 'train-{}.json'.format(self.propertySource.toString())
            Model.modifyManifest(manifestName)
            
        return
    
    def process(self):

        return
    
    def postProcess(self):

        tpDirectory = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getHomePath(), 'AppData', 'Roaming', 'TrainPlayer', 'Reports')
        if not tpDirectory:
            _psLog.warning('TrainPlayer Reports destination directory not found')
            print('TrainPlayer Reports destination directory not found')

            return    

        if self.propertyName == 'TrainBuilt':
            workList = PSE.getTrainManifest(self.propertySource.toString())

        elif self.propertyName == 'opsSwitchList':
            workList = getOpsSwitchList()

        else:
            return

        o2oWorkEvents = ModelWorkEvents.o2oWorkEvents(workList)
        outPutName = 'JMRI Report - o2o Workevents.csv'
        o2oWorkEventPath = PSE.OS_PATH.join(tpDirectory, outPutName)
        PSE.genericWriteReport(o2oWorkEventPath, o2oWorkEvents)

        return

def getOpsSwitchList():

    trainName = 'ops-Switch List.json'
    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', trainName)
    manifest = PSE.loadJson(PSE.genericReadReport(manifestPath))

    return manifest


class StartUp:
    """Start the o2o subroutine"""

    def __init__(self):

        self.configFile = PSE.readConfigFile()

        return

    def getSubroutine(self):
        """
        Returns the subroutine and activates the widgets.
        """

        subroutine, self.widgets = View.ManageGui().makeSubroutine()
        subroutineName = __package__.split('.')[1]
        subroutine.setVisible(self.configFile[subroutineName]['SV'])
        self.activateWidgets()

        _psLog.info(__package__ + ' makeFrame completed')

        return subroutine

    def startUpTasks(self):
        
        return

    def activateWidgets(self):
        """
        The *.getName value is the name of the action for the widget.
        IE: initializeJmriRailroad, aoLocations
        """

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def getWidget(self, name):

        for widget in self.widgets:
            if widget.getName() == name:
                return widget
            
    def initializeJmriRailroad(self, EVENT):
        """
        Initializes JMRI Cars, Engines, and Locations.
        Backs up Trains and Routes.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return
        
        PSE.closeWindowByLevel(level=1)

        firstPress = PSE.getBundleItem('Initialize Railroad')
        secondPress = PSE.getBundleItem('Confirm')

        if EVENT.getSource().text == firstPress:
            EVENT.getSource().setText(secondPress)
            self.getWidget('cancel').setVisible(True)
        else:
            Model.resetBuiltTrains()
            Model.initializeJmriRailroad()
            EVENT.getSource().setText(firstPress)
            self.getWidget('cancel').setVisible(False)

            PSE.LM.firePropertyChange('opsResetSubroutine', False, True)
            PSE.LM.firePropertyChange('opsRefreshSubroutine', False, True)

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))
        return

    def aoLocations(self, EVENT):
        """
        Import Trainplayer's Advanced Ops/Locations button.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return

        PSE.closeWindowByLevel(level=2)

        Model.resetBuiltTrains()
        Model.updateJmriLocations()

        PSE.LM.firePropertyChange('opsResetSubroutine', False, True)

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

    def aoIndustries(self, EVENT):
        """
        Import Trainplayer's Advanced Ops/Industries button.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return

        PSE.closeWindowByLevel(level=2)

        Model.resetBuiltTrains()
        Model.updateJmriTracks()

        PSE.LM.firePropertyChange('opsResetSubroutine', False, True)

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return
    
    def aoCars(self, EVENT):
        """
        Import Trainplayer's Advanced Ops/Cars button.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return

        PSE.closeWindowByLevel(level=2)

        Model.resetBuiltTrains()
        Model.updateJmriRollingingStock()

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

    def extendedDetail(self, EVENT):
        """
        Import Personalized Settings/Extended Detail button.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return
        
        Model._updateJmriProperties()

        extendedProperties = Model.getExtendedProperties()
        PSE.LM.firePropertyChange('opsExtendedProperties', extendedProperties, True)

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

    def cancel(self, EVENT):
        """
        Cancel the initialization.
        """

        EVENT.getSource().setVisible(False)
        self.getWidget('initializeJmriRailroad').setText(PSE.getBundleItem('Initialize Railroad'))

        return
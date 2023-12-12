# coding=utf-8
# © 2023 Greg Ritacco

"""
Scanner subroutine.
Only cars are sequenced.
Engines will be sequenced in a future revision.
"""

from opsEntities import PSE
from Subroutines_Activated.Scanner import SubroutineListeners
from Subroutines_Activated.Scanner import Model
from Subroutines_Activated.Scanner import View

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.SC.Controller')

def getSubroutineDropDownItem():
    """
    Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>
    """

    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    configFile = PSE.readConfigFile()
    if configFile[subroutineName]['SV']:
        menuText = u'{} {}'.format(PSE.getBundleItem('Hide'), __package__)
    else:
        menuText = u'{} {}'.format(PSE.getBundleItem('Show'), __package__)

    menuItem.setName(__package__)
    menuItem.setText(menuText)

    return menuItem


class TrainsPropertyParser:
    """
    What gets called when any of three listeners are fired:
    preProcess, process, postProcess
    """
    
    def __init__(self, pce):

        self.propertySource = pce.source
        self.propertyName = pce.propertyName
        self.oldValue = pce.oldValue
        self.newValue = pce.newValue

        return
    
    def preProcess(self):

        if self.propertyName == 'TrainBuilt' and self.newValue:
            if PSE.readConfigFile()['Main Script']['CP']['ER']:
                PSE.extendManifest(self.propertySource) # The train object is passed in

        return
    
    def process(self):

        if self.propertyName == 'opsSetCarsToTrack':
            Model.decreaseSequenceNumber(self.oldValue) # self.oldValue is the car object
            Model.resequenceCarsAtLocation(self.newValue) # self.newValue is the location name

        if self.propertyName == 'opsSwitchList':
            reportName = PSE.readConfigFile()['Main Script']['US']['OSL'].format('OPS', 'json')
            Model.addSequenceToManifest(reportName)
            Model.resequenceManifestJson(reportName)

        if self.propertyName == 'TrainBuilt' and self.newValue:
            if PSE.readConfigFile()['Main Script']['CP']['ER']:
                manifestName = u'train-{}.json'.format(self.propertySource.toString())
                Model.addSequenceToManifest(manifestName)
                Model.resequenceManifestJson(manifestName)

        if self.propertyName == 'TrainMoveComplete' and self.newValue:
            if PSE.readConfigFile()['Main Script']['CP']['ER'] :
                Model.increaseSequenceNumber(self.newValue.toString())

        if self.propertyName == 'TrainMoveComplete' and self.oldValue:
            if PSE.readConfigFile()['Main Script']['CP']['ER']:
                Model.resequenceCarsAtLocation(self.oldValue.toString())

        return
    
    def postProcess(self):

        # if self.propertyName == 'opsSetCarsToTrack':
        #     Model.resequenceCarsAtLocation(self.newValue) # self.newValue is the location name

        # if self.propertyName == 'opsSwitchList':
        #     reportName = PSE.readConfigFile()['Main Script']['US']['OSL'].format('OPS', 'json')
        #     Model.resequenceManifestJson(reportName)

        # if self.propertyName == 'TrainBuilt' and self.newValue:
        #     if PSE.readConfigFile()['Main Script']['CP']['ER']:
        #         manifestName = u'train-{}.json'.format(self.propertySource.toString())
        #         Model.resequenceManifestJson(manifestName)

        # if self.propertyName == 'TrainMoveComplete' and self.oldValue:
        #     if PSE.readConfigFile()['Main Script']['CP']['ER']:
        #         Model.resequenceCarsAtLocation(self.oldValue.toString())

        return


class StartUp:
    """
    Start the subroutine.
    """

    def __init__(self):

        self.configFile = PSE.readConfigFile()

        return

    def getSubroutine(self):
        """
        Gets the title border frame.
        """

        subroutine, self.widgets = View.ManageGui().makeSubroutine()
        subroutineName = __package__.split('.')[1]
        subroutine.setVisible(self.configFile[subroutineName]['SV'])
        self.activateWidgets()

        _psLog.info(__package__ + ' makeFrame completed')

        return subroutine

    def startUpTasks(self):
        """
        Run these tasks when this subroutine is started.
        No GUI items as the GUI is not built yet.
        """

        Model.validateSequenceEntries()

        OSU = PSE.JMRI.jmrit.operations.setup
        OSU.Setup.setRfidEnabled(True)
        OSU.Setup.setValueEnabled(True)
        
        return
        
    def activateWidgets(self):

        self.widgets[0].actionPerformed = self.qrCodeButton
        self.widgets[1].addActionListener(SubroutineListeners.ScannerSelection())
        self.widgets[2].actionPerformed = self.applyButton

        return

    def qrCodeButton(self, EVENT):

        _psLog.debug(EVENT)

        Model.applyRfidData()

        return

    def applyButton(self, EVENT):

        _psLog.debug(EVENT)

        scannerReportPath = Model.getScannerReportPath()
        if scannerReportPath:
            Model.validateScanReport(scannerReportPath)
            Model.applyScanReport(scannerReportPath)

        print('{} rev:{}'.format(SCRIPT_NAME, SCRIPT_REV))

        return

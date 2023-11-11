# coding=utf-8
# © 2023 Greg Ritacco

"""
Scanner subroutine.
Only cars are sequenced.
Engines will be sequenced in a future revision.
"""

from opsEntities import PSE
from opsEntities import TextReports
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
        menuText = '{} {}'.format(PSE.getBundleItem('Hide'), __package__)
    else:
        menuText = '{} {}'.format(PSE.getBundleItem('Show'), __package__)

    menuItem.setName(__package__)
    menuItem.setText(menuText)

    return menuItem


class TrainsPropertyParser:

    def __init__(self, pce):

        self.propertySource = pce.source
        self.propertyName = pce.propertyName
        self.oldValue = pce.oldValue
        self.newValue = pce.newValue

        return
    
    def preProcess(self):

        if self.propertyName == 'opsSetCarsToTrack':
            Model.resequenceCarsAtLocation()

        if self.propertyName == 'opsSwitchList':
            Model.extendSwitchListJson()

        if self.propertyName == 'TrainBuilt':
            manifestName = 'train-{}.json'.format(self.propertySource.toString())
            Model.extendManifestJson(manifestName)

        if self.propertyName == 'TrainMoveComplete' and self.newValue:
            Model.increaseSequenceNumber(self.newValue.toString())

        return
    
    def process(self):

        if self.propertyName == 'opsSwitchList':
            switchListName = 'ops-Switch List.json'
            Model.resequenceManifestJson(switchListName)

        if self.propertyName == 'TrainBuilt':
            manifestName = 'train-{}.json'.format(self.propertySource.toString())
            Model.resequenceManifestJson(manifestName)

        if self.propertyName == 'TrainMoveComplete' and self.oldValue:
            Model.resequenceCarsAtLocation(self.oldValue.toString())

        return
    
    def postProcess(self):

        if self.propertyName == 'TrainBuilt':

            jmriManifest = PSE.getTrainManifest(self.propertySource.toString())
        # Make the OPS train list
            opsTrainList = PSE.getOpsTrainList(jmriManifest)
            trainListText = TextReports.opsTrainList(opsTrainList)
            trainListName = 'ops train ({}).txt'.format(self.propertySource.toString())
            trainListPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', trainListName)
            PSE.genericWriteReport(trainListPath, trainListText)
        # Make the OPS work order
            workOrderText = TextReports.opsJmriWorkOrder(jmriManifest)
            workOrderName = 'ops train ({}).txt'.format(self.propertySource.toString())
            workOrderPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchLists', workOrderName)
            PSE.genericWriteReport(workOrderPath, workOrderText)

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

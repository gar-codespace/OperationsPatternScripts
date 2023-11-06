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

def opsPreProcess(message=None):
    """
    Extends the json files.
    """

    if message == 'opsSetCarsToTrack':
        Model.resequenceCarsAtLocation()

    if message == 'opsSwitchList':
        Model.extendSwitchListJson()

    if message == 'TrainBuilt':
        Model.extendManifestJson()

    return

def opsProcess(message=None):
    """
    Process the extended json files.
    Note: the pattern report is sorted using user defined criteria.
    """

    if message == 'opsSwitchList':
        switchListName = 'ops-Switch List.json'
        Model.resequenceManifestJson(switchListName)

    if message == 'TrainBuilt':
        trainName = 'train-{}.json'.format(PSE.getNewestTrain().toString())
        Model.resequenceManifestJson(trainName)

    return

def opsPostProcess(message=None):
    """
    Writes the processed json files to text files.
    """

    if message == 'TrainBuilt':
        train = PSE.getNewestTrain()
        manifest = PSE.getTrainManifest(train)

        textManifest = TextReports.opsJmriManifest(manifest)
        manifestName = 'ops train ({}).txt'.format(train.toString())
        manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', manifestName)
        PSE.genericWriteReport(manifestPath, textManifest)

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
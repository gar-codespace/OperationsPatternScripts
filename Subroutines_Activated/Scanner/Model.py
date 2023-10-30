# coding=utf-8
# © 2023 Greg Ritacco

"""
Scanner subroutine.
"""

from opsEntities import PSE
from opsEntities import TextReports

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.SC.Model')


""" Routines called by the plugin listeners """


def resetConfigFileItems():

    return

def initializeSubroutine():

    scannerComboUpdater()
    
    return

def resetSubroutine():

    return

def refreshSubroutine():

    configFile = PSE.readConfigFile()

    scannerComboUpdater(configFile['Scanner']['SI'])

    return


""" Routines specific to this subroutine """


def scannerComboUpdater(selected=None):
    """
    Updates the contents of the scanners combo box.
    """

    _psLog.debug('scannerComboUpdater')

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
    component = PSE.getComponentByName(frame, 'sScanner')
    component.removeAllItems()

    pulldownList = _updateScannerList()
    for scanName in pulldownList:
        component.addItem(scanName)

    component.setSelectedItem(selected)
    
    return

def validateSequenceData():
    """
    Checks that rsSequenceData.json exists.
    If not then create one.
    """
    
    sequenceFilePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'rsSequenceData.json')
    if not PSE.JAVA_IO.File(sequenceFilePath).isFile():
        initialSequenceHash = getInitialSequenceHash()
        PSE.genericWriteReport(sequenceFilePath, PSE.dumpJson(initialSequenceHash))

    return

def getSequenceHash():
    """
    Load the sequence file into memory.
    """

    sequenceFilePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'rsSequenceData.json')
    PSE.SEQUENCE_HASH = PSE.loadJson(PSE.genericReadReport(sequenceFilePath))

    return

def getScannerReportPath():
    """
    Writes the name of the selected scanner report to the config file.
    """

    configFile = PSE.readConfigFile()
    scannerPath = configFile['Scanner']['US']['SP']

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
    component = PSE.getComponentByName(frame, 'sScanner')

    itemSelected = component.getSelectedItem()
    try:
        itemSelected = itemSelected + '.txt'
        scannerReportPath = PSE.OS_PATH.join(scannerPath, itemSelected)
    except:
        scannerReportPath = None

    return scannerReportPath

def validateScanReport(scannerReportPath=None):

    _psLog.debug('validateScanReport')

    return True

def applyScanReport(scannerReportPath):
    """
    Assign a sequence number to the RS in the selected scan report.
    """

    _psLog.debug('applyScanReport')

    locoSequence = 8001
    carSequence = 8001

    scannerReport = PSE.genericReadReport(scannerReportPath)
    splitReport = scannerReport.split('\n')
    splitReport.pop(-1) # Pop off the empty line at the end.
    header = splitReport.pop(0).split(',')

    scannerName = header[0]
    direction = header[1].upper()[0:1]
    if direction == 'W':
        splitReport.reverse()

    for item in splitReport:
        rs = item.split(',')
        if rs[1].startswith('ET'):
            continue
        elif rs[1].startswith('E'):
            PSE.SEQUENCE_HASH['locos'].update({rs[0]:locoSequence})
            locoSequence += 1
        else:
            PSE.SEQUENCE_HASH['cars'].update({rs[0]:carSequence})
            carSequence += 1


    _psLog.debug('applyScanReport for scanner: ' + scannerName)
    print('applyScanReport for scanner: ' + scannerName)

    return

def saveSequenceHash():
    
    sequenceFilePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'rsSequenceData.json')
    PSE.genericWriteReport(sequenceFilePath, PSE.dumpJson(PSE.SEQUENCE_HASH))

    return

def recordSelection(comboBox):
    """
    Write the combo box selected item to the configfile.
    """

    configFile = PSE.readConfigFile()
    configFile['Scanner'].update({'SI':comboBox.getSelectedItem()})
    PSE.writeConfigFile(configFile)

    return

def modifyManifestJson():
    """
    Modifies the JMRI created json manifest.
    """

    reportName = 'train-{}.json'.format(PSE.getNewestTrain().toString())
    PSE.extendManifest(reportName)
    _modifyAction(reportName)

    return

def _modifyAction(reportName):

    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))
    _addSequenceToManifest(report)

    PSE.genericWriteReport(reportPath, PSE.dumpJson(report))

    return

def _addSequenceToManifest(manifest):
    """
    Add a sequence attribute to a JMRI train manifest json.
    """

    for location in manifest['locations']:
        for car in location['cars']['add']:
            carID = car['road'] + ' ' + car['number']
            try:
                sequence = PSE.SEQUENCE_HASH['cars'][carID]
            except:
                sequence = 8000
            car['sequence'] = sequence

        for car in location['cars']['remove']:
            carID = car['road'] + ' ' + car['number']
            try:
                sequence = PSE.SEQUENCE_HASH['cars'][carID]
            except:
                sequence = 8000
            sequence = PSE.SEQUENCE_HASH['cars'][carID]
            car['sequence'] = sequence

    for location in manifest['locations']:
        cars = location['cars']['add']
        cars.sort(key=lambda row: row['sequence'])

        cars = location['cars']['remove']
        cars.sort(key=lambda row: row['sequence'])

    return manifest

# def modifyTrainManifest(train):
#     """
#     Modifies the existing JMRI manifest, sorts by sequence number.
#     """
    
#     TextReports.extendJmriManifest(train)

#     textManifest = TextReports.opsJmriManifest(train)
#     manifestName = 'train (' + train.toString() + ').txt'
#     manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', manifestName)
#     PSE.genericWriteReport(manifestPath, textManifest)

#     return

def resequenceManifestJson():
    """
    Resequences an existing json manifest by its sequence value.
    """

    trainName = 'train-{}.json'.format(PSE.getNewestTrain().toString())
    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', trainName)
    manifest = PSE.loadJson(PSE.genericReadReport(manifestPath))

    for location in manifest['locations']:
        cars = location['cars']['add']
        cars.sort(key=lambda row: row['sequence'])

        cars = location['cars']['remove']
        cars.sort(key=lambda row: row['sequence'])

    PSE.genericWriteReport(manifestPath, PSE.dumpJson(manifest))

    return

def getInitialSequenceHash():

    scannerHash = {}
    locoHash = {}
    carHash = {}

    for loco in PSE.EM.getList():
        id = loco.getRoadName() + ' ' + loco.getNumber()
        locoHash.update({id:8000})

    for car in PSE.CM.getList():
        id =  car.getRoadName() + ' ' + car.getNumber()
        carHash.update({id:8000})
                        
    scannerHash.update({'locos':locoHash})
    scannerHash.update({'cars':carHash})

    return scannerHash

def _updateScannerList():
    """
    Gets the file names in the designated scanner path.
    """

    configFile = PSE.readConfigFile()
    scannerPath = configFile['Scanner']['US']['SP']
    dirContents = PSE.JAVA_IO.File(scannerPath).list()

    pulldownList = []
    for file in dirContents:
        pulldownList.append(file.split('.')[0])

    return pulldownList

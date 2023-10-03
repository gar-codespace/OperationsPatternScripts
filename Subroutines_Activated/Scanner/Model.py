# coding=utf-8
# © 2023 Greg Ritacco

"""
Scanner subroutine.
"""

from opsEntities import PSE
from opsEntities import Manifest

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.SC.Model')

def resetConfigFileItems():
    """
    Put configFile items here that need to be set to their defaults when this subroutine is reset.
    """

    return

def initializeSubroutine():
    """
    If any widgets need to be set to a value saved in the config file when the Pattern Scripts window is opened,
    set those widgets here.
    """

    updateScannerList()
    scannerComboUpdater()
    
    return

def resetSubroutine():
    """
    When the Pattern Scripts window is opened, this subroutine is reset to catch any outside 
    changes made to JMRI that would effect this subroutine.
    """

    return

def refreshSubroutine():
    """
    When the Pattern Scripts window is activated by clicking on it,
    update any widgets in this subroutine that can't otherwise be updated by a listener.
    """

    updateScannerList()
    # scannerComboUpdater()
    return

def validateSequenceData():
    """
    Checks that rsSequenceData.json exists.
    If not then create one.
    """
    
    sequenceFilePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'rsSequenceData.json')
    if not PSE.JAVA_IO.File(sequenceFilePath).isFile():
        initialSequenceHash = getInitialScannerHash()
        PSE.genericWriteReport(sequenceFilePath, PSE.dumpJson(initialSequenceHash))

    return

def modifyTrainManifest(train):
    """
    Mini controller.
    Modifies the existing JMRI manifest, sorts by sequence number.
    """
    
    Manifest.jsonManifest(train)

    textManifest = Manifest.jmriManifest(train)
    manifestName = 'train (' + train.toString() + ').txt'
    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', manifestName)
    PSE.genericWriteReport(manifestPath, textManifest)

    return

def addSequenceToManifest(train):
    """
    Adds an attribute called 'sequence' and it's value to an existing json manifest.
    """

    isSequenceHash, sequenceHash = PSE.getSequenceHash()

    trainName = 'train-' + train + '.json'
    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', trainName)
    manifest = PSE.loadJson(PSE.genericReadReport(manifestPath))

    for location in manifest['locations']:
        for car in location['cars']['add']:
            carID = car['road'] + ' ' + car['number']
            sequence = sequenceHash['cars'][carID]
            car['sequence'] = sequence
        for car in location['cars']['remove']:
            carID = car['road'] + ' ' + car['number']
            sequence = sequenceHash['cars'][carID]
            car['sequence'] = sequence

    PSE.genericWriteReport(manifestPath, PSE.dumpJson(manifest))

    return

def resequenceManifest(train):
    """
    Resequences an existing json manifest by its sequence value.
    """

    trainName = 'train-' + train + '.json'
    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', trainName)
    manifest = PSE.loadJson(PSE.genericReadReport(manifestPath))

    for location in manifest['locations']:
        cars = location['cars']['add']
        cars.sort(key=lambda row: row['sequence'])

        cars = location['cars']['remove']
        cars.sort(key=lambda row: row['sequence'])

    PSE.genericWriteReport(manifestPath, PSE.dumpJson(manifest))

    return

def getInitialScannerHash():

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

def updateScannerList():
    """
    Update the contents of the scanner combo box.
    """

    configFile = PSE.readConfigFile()
    scannerPath = configFile['Scanner']['US']['SP']
    dirContents = PSE.JAVA_IO.File(scannerPath).list()

    pulldownList = []
    for file in dirContents:
        pulldownList.append(file.split('.')[0])

    configFile['Scanner'].update({'PL':pulldownList})
    PSE.writeConfigFile(configFile)

    return

def scannerComboUpdater():
    """
    Updates the contents of the locations combo box when the listerers detect a change.
    """

    _psLog.debug('scannerComboUpdater')
    configFile = PSE.readConfigFile()
    pulldownList = configFile['Scanner']['PL']

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    component = PSE.getComponentByName(frame, 'sScanner')
    component.removeAllItems()
    for scanName in pulldownList:
        component.addItem(scanName)

    return

def getScannerReport(EVENT):
    """
    Writes the name of the selected scanner report to the config file.
    """

    configFile = PSE.readConfigFile()
    scannerPath = configFile['Scanner']['US']['SP']

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
    component = PSE.getComponentByName(frame, 'sScanner')

    itemSelected = component.getSelectedItem()
    itemSelected = itemSelected + '.txt'
    scannerReportPath = PSE.OS_PATH.join(scannerPath, itemSelected)

    configFile['Scanner'].update({'RP':scannerReportPath})
    PSE.writeConfigFile(configFile)

    return

def applyScanReport():
    """
    Assign a sequence number to the RS in the selected scan report.
    """

    _psLog.debug('applyScanReport')

    sequenceFilePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'rsSequenceData.json')
    sequenceFile = PSE.loadJson(PSE.genericReadReport(sequenceFilePath))

    locoSequence = 8001
    carSequence = 8001

    configFile = PSE.readConfigFile()
    reportPath = configFile['Scanner']['RP']

    scannerReport = PSE.genericReadReport(reportPath)
    splitReport = scannerReport.split('\n')
    splitReport.pop(-1) # Pop off the empty line at the end.
    header = splitReport.pop(0).split(',')

    scannerName = header[0]
    direction = header[1].upper()[0:1]
    if direction == 'W':
        splitReport.reverse()

    print(direction)



    for item in splitReport:
        rs = item.split(',')
        if rs[1].startswith('ET'):
            continue
        elif rs[1].startswith('E'):
            sequenceFile['locos'].update({rs[0]:locoSequence})
            locoSequence += 1
        else:
            sequenceFile['cars'].update({rs[0]:carSequence})
            carSequence += 1

    PSE.genericWriteReport(sequenceFilePath, PSE.dumpJson(sequenceFile))

    _psLog.debug('applyScanReport for scanner: ' + scannerName)
    print('applyScanReport for scanner: ' + scannerName)

    return
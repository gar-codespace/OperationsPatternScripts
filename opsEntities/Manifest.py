# coding=utf-8
# © 2023 Greg Ritacco

"""
Unified report formatting for all OPS generated reports.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

TMT = PSE.JMRI.jmrit.operations.trains.TrainManifestText()

_psLog = PSE.LOGGING.getLogger('OPS.OE.Manifest')

def extendJmriManifest(train):
    """
    Mini controller
    Modifies the JMRI generated json manifest and sorts it in sequence order.
    """
    
    extendJmriManifestJson(train)

    if 'Scanner' in PSE.readConfigFile('Main Script')['SL']:
        resequenceJmriManifest(train)

    return

def extendJmriManifestJson(train):
    """
    Adds an attribute called 'sequence' and it's value to an existing json manifest.
    Adds additional items found in the Setup.get< >ManifestMessageFormat()
    """

    _psLog.debug('Manifest.extendJmriManifestJson')

    isSequenceHash, sequenceHash = PSE.getSequenceHash()

    trainName = 'train-' + train.toString() + '.json'
    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', trainName)
    manifest = PSE.loadJson(PSE.genericReadReport(manifestPath))

    for location in manifest['locations']:
        for car in location['cars']['add']:
            carID = car['road'] + ' ' + car['number']
            sequence = sequenceHash['cars'][carID]
            car['sequence'] = sequence

            carObj = PSE.CM.getByRoadAndNumber(car['road'], car['number'])
            car['finalDestination'] = carObj.getFinalDestinationName()
            car['fdTrack'] = carObj.getFinalDestinationTrackName()
            car['loadType'] = PSE.getShortLoadType(car)
            car['kernelSize'] = 'NA'
            car['division'] = PSE.LM.getLocationByName(car['location']['userName']).getDivisionName()

        for car in location['cars']['remove']:
            carID = car['road'] + ' ' + car['number']
            sequence = sequenceHash['cars'][carID]
            car['sequence'] = sequence

            carObj = PSE.CM.getByRoadAndNumber(car['road'], car['number'])
            car['finalDestination'] = carObj.getFinalDestinationName()
            car['fdTrack'] = carObj.getFinalDestinationTrackName()
            car['loadType'] = PSE.getShortLoadType(car)
            car['kernelSize'] = 'NA'
            car['division'] = PSE.LM.getLocationByName(car['location']['userName']).getDivisionName()

    PSE.genericWriteReport(manifestPath, PSE.dumpJson(manifest))

    return

def resequenceJmriManifest(train):
    """
    Resequences an existing json manifest by its sequence value.
    """

    _psLog.debug('Manifest.resequenceJmriManifest')

    trainName = 'train-' + train.toString() + '.json'
    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', trainName)
    manifest = PSE.loadJson(PSE.genericReadReport(manifestPath))

    for location in manifest['locations']:
        cars = location['cars']['add']
        cars.sort(key=lambda row: row['sequence'])

        cars = location['cars']['remove']
        cars.sort(key=lambda row: row['sequence'])

    PSE.genericWriteReport(manifestPath, PSE.dumpJson(manifest))

    return

def opsTextPatternReport(location):
    """
    Creates a text Pattern Report from a json file.
    Formatting is similar to a JMRI text manifest.
    """

    PSE.makeReportItemWidthMatrix()
    PSE.translateMessageFormat()

    reportName = PSE.getBundleItem('ops-Pattern Report') + '.json'
    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))

    textPatternReport = ''

# Header
    textPatternReport += PSE.getExtendedRailroadName() + '\n'
    textPatternReport += '\n'

    textPatternReport += PSE.getBundleItem('Pattern Report for location') + ' (' + location + ')\n'
    epochTime = PSE.convertJmriDateToEpoch(report['date'])
    textPatternReport += PSE.validTime(epochTime) + '\n'
    textPatternReport += '\n'
# Body
    for location in report['locations']:
        carLength = 0
        textPatternReport += PSE.getBundleItem('List of inventory at') + ' ' + location['userName'] + '\n'
    # Pick up locos
        for loco in location['engines']['add']:
            seq = loco['sequence'] - 8000
            formatPrefix = PSE.formatText(str(seq), 4)
    # Move cars
        for car in location['cars']['add']:
            carLength += int(car['length'])
            seq = car['sequence'] - 8000
            formatPrefix = ' ' + str(seq).rjust(2, '0') + '  '
            line = PSE.localMoveCar(car, True, False)
            textPatternReport += formatPrefix + ' ' + line + '\n'
        
        totalCars = str(len(location['cars']['add']))
        textPatternReport += PSE.getBundleItem('Total Cars:') + ' ' + totalCars + PSE.getBundleItem('Track Length:') + '\n'
        textPatternReport += '\n'

    print(textPatternReport)
    return

def opsTextManifest(train):
    """"
    OPS version of the JMRI generated text manifest.
    """

    PSE.makeReportItemWidthMatrix()
    PSE.translateMessageFormat()

    pep = PSE.JMRI.jmrit.operations.setup.Setup.getPickupEnginePrefix()
    dep = PSE.JMRI.jmrit.operations.setup.Setup.getDropEnginePrefix()
    pcp = PSE.JMRI.jmrit.operations.setup.Setup.getPickupCarPrefix()
    dcp = PSE.JMRI.jmrit.operations.setup.Setup.getDropCarPrefix()
    mcp = PSE.JMRI.jmrit.operations.setup.Setup.getLocalPrefix()
    hcp = PSE.getBundleItem('Hold')

    longestStringLength = PSE.findLongestStringLength((pep, dep, pcp, dcp, mcp, hcp))

    trainName = 'train-' + train.toString() + '.json'
    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', trainName)
    manifest = PSE.loadJson(PSE.genericReadReport(manifestPath))

    textManifest = ''

# Header
    textManifest += PSE.getExtendedRailroadName() + '\n'
    textManifest += '\n'

    textManifest += TMT.getStringManifestForTrain().format(train.getName(), train.getDescription()) + '\n'
    epochTime = PSE.convertJmriDateToEpoch(manifest['date'])
    textManifest += PSE.validTime(epochTime) + '\n'
    textManifest += '\n'
# Body
    for location in manifest['locations']:
        textManifest += TMT.getStringScheduledWork().format(location['userName']) + '\n'
    
    # Pick up locos
        for loco in location['engines']['add']:
            formatPrefix = PSE.formatText(pep, longestStringLength)

    # Set out locos
        for loco in location['engines']['remove']:
            formatPrefix = PSE.formatText(dep, longestStringLength)

    # Pick up cars
        for car in location['cars']['add']:
            if car['isLocal']:
                continue
            formatPrefix = PSE.formatText(pcp, longestStringLength)
            line = PSE.pickupCar(car, True, False)
            textManifest += formatPrefix + ' ' + line + '\n'
    # Move cars
        for car in location['cars']['add']:
            if not car['isLocal']:
                continue
            formatPrefix = PSE.formatText(mcp, longestStringLength)
            line = PSE.localMoveCar(car, True, False)
            textManifest += formatPrefix + ' ' + line + '\n'
    # Set out cars
        for car in location['cars']['remove']:
            if car['isLocal']:
                continue
            formatPrefix = PSE.formatText(dcp, longestStringLength)
            line = PSE.dropCar(car, True, False)
            textManifest += formatPrefix + ' ' + line + '\n'

        try:
        # Location summary
            td = PSE.JMRI.jmrit.operations.setup.Setup.getDirectionString(location['trainDirection'])
            textManifest += TMT.getStringTrainDepartsCars().format(location['userName'], td, str(location['cars']['total']), str(location['length']['length']), location['length']['unit'], str(location['weight'])) + '\n'
        except:
        # Footer
            textManifest += TMT.getStringTrainTerminates().format(manifest['locations'][-1]['userName']) + '\n'

        textManifest += '\n'

    return textManifest

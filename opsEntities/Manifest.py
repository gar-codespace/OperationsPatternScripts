# coding=utf-8
# © 2023 Greg Ritacco

"""
Unified report formatting for all OPS generated reports.
The idea is to have all the JMRI and OPS text reports share a similar look.
-Extends the JMRI generated json manifest.
-Creates a new JMRI text manifest.
-Creates the OPS text Pattern Report.
-Creates the OPS text Switch List.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

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
            car['loadType'] = carObj.getLoadType()
            car['kernelSize'] = 'NA'
            car['division'] = PSE.LM.getLocationByName(car['location']['userName']).getDivisionName()

        for car in location['cars']['remove']:
            carID = car['road'] + ' ' + car['number']
            sequence = sequenceHash['cars'][carID]
            car['sequence'] = sequence

            carObj = PSE.CM.getByRoadAndNumber(car['road'], car['number'])
            car['finalDestination'] = carObj.getFinalDestinationName()
            car['fdTrack'] = carObj.getFinalDestinationTrackName()
            car['loadType'] = carObj.getLoadType()
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
    Creates a text Pattern Report from an OPS generated json file.
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

    textPatternReport += PSE.getBundleItem('Pattern Report for location ({})').format(location) + '\n'
    epochTime = PSE.convertJmriDateToEpoch(report['date'])
    textPatternReport += PSE.validTime(epochTime) + '\n'
    textPatternReport += '\n'
    fdTally = []
# Body
    for location in report['locations']:
        carLength = 0
        textPatternReport += PSE.getBundleItem('List of inventory at {}').format(location['userName']) + '\n'
    # Pick up locos
        for loco in location['engines']['add']:
            seq = loco['sequence'] - 8000
            formatPrefix = ' ' + str(seq).rjust(2, '0') + ' '
    # Move cars
        for car in location['cars']['add']:
            carLength += int(car['length'])
            fdTally.append(car['finalDestination'])
            seq = car['sequence'] - 8000
            formatPrefix = ' ' + str(seq).rjust(2, '0') + ' '
            line = PSE.localMoveCar(car, True, False)
            textPatternReport += formatPrefix + ' ' + line + '\n'
        
        totalCars = str(len(location['cars']['add']))
        trackLength = location['length']['length']
        eqptLength = carLength
        avail = trackLength - eqptLength
        summaryText = PSE.getBundleItem('Total cars: {} Track length: {} Equipment length: {} Available: {}')
        textPatternReport += summaryText.format(totalCars, trackLength, eqptLength, avail) + '\n'
        textPatternReport += '\n'

    textPatternReport += PSE.getBundleItem('Final Destination Totals:') + '\n'

    for track, count in sorted(PSE.occuranceTally(fdTally).items()):
        if not track:
            track = PSE.getBundleItem('None')
        textPatternReport += ' ' + track + ' - ' + str(count) + '\n'

    return textPatternReport

def opsTextSwitchList():
    """
    Creates a text Switch List from an OPS generated json file.
    """
    PSE.makeReportItemWidthMatrix()
    PSE.translateMessageFormat()

    configFile = PSE.readConfigFile()

    location = configFile['Patterns']['PL']
    dep = PSE.JMRI.jmrit.operations.setup.Setup.getDropEnginePrefix()
    mcp = PSE.JMRI.jmrit.operations.setup.Setup.getLocalPrefix()
    hcp = configFile['Patterns']['US']['HCP']
    longestStringLength = PSE.findLongestStringLength((dep, mcp, hcp))


    reportName = PSE.getBundleItem('ops-Switch List') + '.json'
    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))

    textSwitchList = ''

# Header
    textSwitchList += PSE.getExtendedRailroadName() + '\n'
    textSwitchList += '\n'

    textSwitchList += PSE.getBundleItem('Switch List for location ({})').format(location) + '\n'
    epochTime = PSE.convertJmriDateToEpoch(report['date'])
    textSwitchList += PSE.validTime(epochTime) + '\n'
    textSwitchList += '\n'
# Body
    for location in report['locations']: # For the OPS switch list, the locations list is a track list.
        carLength = 0
        textSwitchList += PSE.getBundleItem('List of inventory at {}').format(location['userName']) + '\n'
    # Pick up locos
        for loco in location['engines']['add']:
            currentTrack = car['location']['track']['userName']
            destTrack = car['destination']['track']['userName']
            if currentTrack == destTrack:
                formatPrefix = hcp.format(longestStringLength)
            else:
                formatPrefix = dep.format(longestStringLength)

            # line = PSE.localMoveCar(loco, True, False)
            # textSwitchList += formatPrefix + ' ' + line + '\n'
    # Move cars
        for car in location['cars']['add']:
            currentTrack = car['location']['track']['userName']
            destTrack = car['destination']['track']['userName']
            if currentTrack == destTrack:
                formatPrefix = hcp.ljust(longestStringLength)
            elif car['onTrain']:
                formatPrefix = hcp.ljust(longestStringLength)
            else:
                formatPrefix = mcp.ljust(longestStringLength)

            line = PSE.localMoveCar(car, True, False)
            textSwitchList += formatPrefix + line + '\n'

        textSwitchList += '\n'

    return textSwitchList

def opsTextManifest(train):
    """"
    OPS version of the JMRI generated text manifest.
    """

    PSE.makeReportItemWidthMatrix()
    PSE.translateMessageFormat()

    TMT = PSE.JMRI.jmrit.operations.trains.TrainManifestText()
    pep = PSE.JMRI.jmrit.operations.setup.Setup.getPickupEnginePrefix()
    dep = PSE.JMRI.jmrit.operations.setup.Setup.getDropEnginePrefix()
    pcp = PSE.JMRI.jmrit.operations.setup.Setup.getPickupCarPrefix()
    dcp = PSE.JMRI.jmrit.operations.setup.Setup.getDropCarPrefix()
    mcp = PSE.JMRI.jmrit.operations.setup.Setup.getLocalPrefix()
    hcp = PSE.readConfigFile()['Patterns']['US']['HCP']

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
            formatPrefix = pep.ljust(longestStringLength)

    # Set out locos
        for loco in location['engines']['remove']:
            formatPrefix = dep.ljust(longestStringLength)

    # Pick up cars
        for car in location['cars']['add']:
            if car['isLocal']:
                continue
            formatPrefix = pcp.ljust(longestStringLength)
            line = PSE.pickupCar(car, True, False)
            textManifest += formatPrefix + ' ' + line + '\n'
    # Move cars
        for car in location['cars']['add']:
            if not car['isLocal']:
                continue
            formatPrefix = mcp.ljust(longestStringLength)
            line = PSE.localMoveCar(car, True, False)
            textManifest += formatPrefix + ' ' + line + '\n'
    # Set out cars
        for car in location['cars']['remove']:
            if car['isLocal']:
                continue
            formatPrefix = dcp.ljust(longestStringLength)
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

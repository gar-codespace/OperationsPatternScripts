# coding=utf-8
# © 2023 Greg Ritacco

"""
Unified report formatting for all OPS generated reports.
The idea is to have all the JMRI and OPS text reports share a similar look.
None of the text reports are processed, only formatting at this module.
-Extends the JMRI generated json manifest.
-Creates a new JMRI text manifest.
-Creates the OPS text Pattern Report.
-Creates the OPS text Switch List.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.OE.Manifest')

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
    textPatternReport += report['railroad'] + '\n'
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
    textSwitchList += report['railroad'] + '\n'
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

def opsTextManifest(manifest):
    """"
    manifest is a string from the json file.
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

    textManifest = ''

# Header
    textManifest += PSE.getExtendedRailroadName() + '\n'
    textManifest += '\n'
    # textManifest += TMT.getStringManifestForTrain().format(train.getName(), train.getDescription()) + '\n'
    textManifest += '{}, {}'.format(manifest['userName'], manifest['description']) + '\n'
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

def o2oWorkEvents(manifest):
    """
    Makes an o2o workevents list from a manifest.
    manifest is a string from the json file.
    """

    _psLog.debug('o2oWorkEvents')
# Header
    o2oWorkEvents = 'HN,' + manifest['railroad'].replace('\n', ';') + '\n'
    o2oWorkEvents += 'HT,' + manifest['userName'] + '\n'
    o2oWorkEvents += 'HD,' + manifest['description'] + '\n'
    epochTime = PSE.convertJmriDateToEpoch(manifest['date'])
    o2oWorkEvents += 'HV,' + PSE.validTime(epochTime) + '\n'
    o2oWorkEvents += 'WT,' + str(len(manifest['locations'])) + '\n'
# Body
    for i, location in enumerate(manifest['locations'], start=1):
        o2oWorkEvents += 'WE,{},{}\n'.format(str(i), location['userName'])
        for loco in location['engines']['add']:
            o2oWorkEvents += 'PL,{}\n'.format(_makeLine(loco))
        for loco in location['engines']['remove']:
            o2oWorkEvents += 'SL,{}\n'.format(_makeLine(loco))
        for car in location['cars']['add']:
            o2oWorkEvents += 'PC,{}\n'.format(_makeLine(car))
        for car in location['cars']['remove']:
            o2oWorkEvents += 'SC,{}\n'.format(_makeLine(car))
        
    return o2oWorkEvents

def _makeLine(rs):
    """
    Helper function to make the rs line for o2oWorkEvents.
    format: TP ID, Road, Number, Car Type, L/E/O, Load or Model, From, To
    """

    try: # Cars
        loadName = rs['load']
        lt = PSE.getShortLoadType(rs)
    except: # Locos
        loadName = rs['model']
        lt = PSE.getBundleItem('Occupied').upper()[0]

    ID = rs['road'] + ' ' + rs['number']
    pu = rs['location']['userName'] + ';' + rs['location']['track']['userName']
    so = rs['destination']['userName'] + ';' + rs['destination']['track']['userName']

    line = '{},{},{},{},{},{},{},{}'.format(ID, rs['road'], rs['number'], rs['carType'], lt, loadName, pu, so)

    return line

# coding=utf-8
# © 2023 Greg Ritacco

"""
Unified report formatting for all OPS generated reports.
The idea is to have all the JMRI and OPS text reports share a similar look.
All the reports are built from a json file, formatted like JMRI manifest.json.
    -Creates an OPS version of a JMRI train manifest, formatted on the JMRI model.
    -Creates an OPS version of the JMRI train switch list, formatted on the JMRI model.(Not yet)
    -Creates the OPS Pattern Report, formatted on the JMRI model.
    -Creates the OPS Switch List, formatted on the JMRI model.
"""

from opsEntities import TRE
from opsEntities import PSE

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.OE.TextReports')

def printExtendedTrainList(trainName):
    """
    Break this into two functions.
    """

    trainListName = u'train list ({}).txt'.format(trainName)
    trainListPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', trainListName)

    jmriManifest = PSE.getTrainManifest(trainName)
    trainList = PSE.getOpsTrainList(jmriManifest)
    trainListText = opsTrainList(trainList)
    PSE.genericWriteReport(trainListPath, trainListText)
    PSE.genericDisplayReport(trainListPath)

    return

def printExtendedWorkOrder(trainName):
    """
    Break this into two functions.
    """
    
    workOrderName = u'work order ({}).txt'.format(trainName)
    workOrderPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchLists', workOrderName)

    jmriManifest = PSE.getTrainManifest(trainName)
    workOrderText = opsJmriWorkOrder(jmriManifest)
    PSE.genericWriteReport(workOrderPath, workOrderText)
    PSE.genericDisplayReport(workOrderPath)

    return


""" Text report functions """


def opsTextPatternReport():
    """
    Creates a text Pattern Report from an OPS generated json file.
    """

    _psLog.debug('opsTextPatternReport')

    TRE.makeReportItemWidthMatrix()
    TRE.translateMessageFormat()

    reportName = 'pattern report-OPS.json'
    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))

    textPatternReport = ''
# Header


    
    textPatternReport += report['railroad'] + '\n'
    textPatternReport += '\n'
    textPatternReport += PSE.getBundleItem(u'Pattern Report for location ({})').format(report[u'userName']) + '\n'
    textPatternReport += PSE.convertIsoToValidTime(report[u'date']) + '\n'
    textPatternReport += '\n'
    textPatternReport += u'{}: {}\n'.format(PSE.getBundleItem('Engines sorted by'), ', '.join(PSE.getSortList('SL')))
    textPatternReport += u'{}: {}\n'.format(PSE.getBundleItem('Cars sorted by'), ', '.join(PSE.getSortList('SC')))
    textPatternReport += '\n'
    fdTally = []
# Body
    for location in report['locations']:
        carLength = 0
        textPatternReport += PSE.getBundleItem('List of inventory at {}').format(location[u'userName']) + '\n'
    # Engines
        textPatternReport += u'{}:\n'.format(PSE.getBundleItem(u'Engines'))
        if not location['engines']['add']:
            textPatternReport += u' {}\n'.format(PSE.getBundleItem(u'None'))
        for loco in location['engines']['add']:
            formatPrefix = u' [{}] '.format('  ')
            line = TRE.pickupLoco(loco, True, False)
            textPatternReport += u'{} {}\n'.format(formatPrefix ,line)
    # Cars
        textPatternReport += u'{}:\n'.format(PSE.getBundleItem(u'Cars'))
        if not location['cars']['add']:
            textPatternReport += u' {}\n'.format(PSE.getBundleItem(u'None'))
        for car in location['cars']['add']:
            carLength += int(car['length'])
            fdTally.append(car['finalDestination']['userName'])
            formatPrefix = u' [{}] '.format('  ')
            line = TRE.localMoveCar(car, True, False)
            textPatternReport += formatPrefix + ' ' + line + '\n'

        summaryText = PSE.getBundleItem(u'Total cars:{},  Loads:{},  Empties:{}')
        textPatternReport += summaryText.format(location['total'], location['loads'], location['empties']) + '\n'

        trackLength = location['length']['length']
        avail = trackLength - carLength
        summaryText = PSE.getBundleItem('Track length:{},  Equipment length:{},  Available:{}')
        textPatternReport += summaryText.format(trackLength, carLength, avail) + '\n'

        textPatternReport += '\n'

    textPatternReport += PSE.getBundleItem(u'Final Destination Totals:') + '\n'

    for track, count in sorted(PSE.occuranceTally(fdTally).items()):
        if not track:
            track = PSE.getBundleItem(u'None')
        textPatternReport += ' ' + track + ' - ' + str(count) + '\n'

    return textPatternReport

def opsTextSwitchList():
    """
    Creates a text Switch List from an OPS generated json file.
    """

    _psLog.debug('opsTextSwitchList')

    TRE.makeReportItemWidthMatrix()
    TRE.translateMessageFormat()

    configFile = PSE.readConfigFile()

    location = configFile['Patterns'][u'PL']
    mcp = unicode(PSE.JMRI.jmrit.operations.setup.Setup.getLocalPrefix(), PSE.ENCODING)
    hcp = configFile['Main Script']['US']['HCP']
    longestStringLength = PSE.findLongestStringLength((mcp, hcp))

    reportName = 'switch list-OPS.json'
    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))

    textSwitchList = ''

# Header
    textSwitchList += report['railroad'] + '\n'
    textSwitchList += '\n'
    textSwitchList += PSE.getBundleItem(u'Switch List for location ({})').format(location) + '\n'
    textSwitchList += u'{}\n'.format(PSE.convertIsoToValidTime(report[u'date']))
    textSwitchList += '\n'
# Body
    for location in report[u'locations']: # For the OPS switch list, the locations list is a track list.
        textSwitchList += PSE.getBundleItem(u'List of inventory at {}').format(location[u'userName']) + '\n'
    # Locos
        textSwitchList += u'{}:\n'.format(PSE.getBundleItem(u'Engines'))
        if not location['engines']['add']:
            textSwitchList += u' {}\n'.format(PSE.getBundleItem(u'None'))
        for loco in location['engines']['add']:
            currentTrack = loco['location']['track'][u'userName']
            destTrack = loco['destination']['track'][u'userName']
            if currentTrack == destTrack:
                formatPrefix = hcp.format(longestStringLength)
            else:
                formatPrefix = mcp.format(longestStringLength)

            line = TRE.setoutLoco(loco, True, False)
            textSwitchList += u'{} {} {}\n'.format(formatPrefix, line, loco['destination']['track'][u'userName'])
    # Cars
        textSwitchList += u'{}:\n'.format(PSE.getBundleItem('Cars'))
        if not location['cars']['add']:
            textSwitchList += u' {}\n'.format(PSE.getBundleItem(u'None'))
        for car in location['cars']['add']:
            currentTrack = car['location']['track'][u'userName']
            destTrack = car['destination']['track'][u'userName']
            if currentTrack == destTrack:
                formatPrefix = hcp.ljust(longestStringLength)
            elif car[u'trainName']:
                formatPrefix = hcp.ljust(longestStringLength)
            else:
                formatPrefix = mcp.ljust(longestStringLength)

            line = TRE.localMoveCar(car, True, False)
            textSwitchList += u'{} {}\n'.format(formatPrefix, line)
        textSwitchList += '\n'

    return textSwitchList

def opsJmriWorkOrder(manifest):
    """"
    OPS version of the JMRI generated text manifest.
    """

    _psLog.debug('opsJmriWorkOrder')

    TRE.makeReportItemWidthMatrix()
    TRE.translateMessageFormat()

    TMT = PSE.JMRI.jmrit.operations.trains.TrainManifestText()
    pep = PSE.JMRI.jmrit.operations.setup.Setup.getPickupEnginePrefix()
    dep = PSE.JMRI.jmrit.operations.setup.Setup.getDropEnginePrefix()
    pcp = PSE.JMRI.jmrit.operations.setup.Setup.getPickupCarPrefix()
    dcp = PSE.JMRI.jmrit.operations.setup.Setup.getDropCarPrefix()
    mcp = PSE.JMRI.jmrit.operations.setup.Setup.getLocalPrefix()
    hcp = PSE.readConfigFile()['Main Script']['US']['HCP']

    longestStringLength = PSE.findLongestStringLength((pep, dep, pcp, dcp, mcp, hcp))
    textWorkOrder = ''
# Header
    textWorkOrder += manifest[u'railroad'] + '\n'
    textWorkOrder += '\n'
    textWorkOrder += u'{} ({}) {}\n'.format(PSE.getBundleItem(u'Work order for train'), manifest[u'userName'], manifest[u'description'])
    textWorkOrder += u'{}\n'.format(PSE.convertIsoToValidTime(manifest[u'date']))
    textWorkOrder += '\n'
# Body
    for location in manifest['locations']:
        textWorkOrder += TMT.getStringScheduledWork().format(location[u'userName']) + '\n'
    
    # Pick up locos
        textWorkOrder += u'{}:\n'.format(PSE.getBundleItem(u'Engines'))
        for loco in location['engines']['add']:
            formatPrefix = pep.ljust(longestStringLength)
            line = TRE.pickupLoco(loco, True, False)
            textWorkOrder += u'{} {}\n'.format(formatPrefix ,line)
    # Set out locos
        for loco in location['engines']['remove']:
            formatPrefix = dep.ljust(longestStringLength)
            line = TRE.setoutLoco(loco, True, False)
            textWorkOrder += u'{} {}\n'.format(formatPrefix ,line)

        if len(location['engines']['add']) + len(location['engines']['remove']) == 0:
            textWorkOrder += u' {}: {}\n'.format(PSE.getBundleItem(u'No work at'), location[u'userName'])

    # Pick up cars
        textWorkOrder += u'{}:\n'.format(PSE.getBundleItem(u'Cars'))
        for car in location['cars']['add']:
            if car['isLocal']:
                continue
            formatPrefix = pcp.ljust(longestStringLength)
            line = TRE.pickupCar(car, True, False)
            textWorkOrder += u'{} {}\n'.format(formatPrefix ,line)
    # Move cars
        for car in location['cars']['add']:
            if not car['isLocal']:
                continue
            formatPrefix = mcp.ljust(longestStringLength)
            line = TRE.localMoveCar(car, True, False)
            textWorkOrder += u'{} {}\n'.format(formatPrefix ,line)
    # Set out cars
        for car in location['cars']['remove']:
            if car['isLocal']:
                continue
            formatPrefix = dcp.ljust(longestStringLength)
            line = TRE.dropCar(car, True, False)
            textWorkOrder += u'{} {}\n'.format(formatPrefix ,line)

        if len(location['cars']['add']) + len(location['cars']['remove']) == 0:
            textWorkOrder += u' {}: {}\n'.format(PSE.getBundleItem(u'No work at'), location[u'userName'])

        try:
        # Location summary
            td = PSE.JMRI.jmrit.operations.setup.Setup.getDirectionString(location[u'trainDirection'])
            textWorkOrder += TMT.getStringTrainDepartsCars().format(location[u'userName'], td, str(location['cars']['total']), str(location['length']['length']), location['length']['unit'], str(location['weight'])) + '\n'
        except:
        # Footer
            textWorkOrder += TMT.getStringTrainTerminates().format(manifest['locations'][-1][u'userName']) + '\n'

        textWorkOrder += '\n'

    return textWorkOrder

def opsTrainList(manifest):
    """
    Makes an OPS train list text report.
    """

    _psLog.debug('opsTrainList')

    TRE.makeReportItemWidthMatrix()
    TRE.translateMessageFormat()
    TMT = PSE.JMRI.jmrit.operations.trains.TrainManifestText()

# Header
    trainListText = u'{}\n'.format(manifest[u'railroad'])
    trainListText += '\n'
    trainListText += u'{} ({}) {}\n'.format(PSE.getBundleItem(u'Train list for train'), manifest[u'userName'], manifest[u'description'])
    trainListText += u'{}\n'.format(PSE.convertIsoToValidTime(manifest[u'date']))
    trainListText += '\n'

# Body
    for location in manifest['locations']:
        trainListText += u'{}: {}\n'.format(PSE.getBundleItem(u'Train consist at'), location[u'userName'])

    # Pick up locos
        trainListText += '{}:\n'.format(PSE.getBundleItem(u'Engines'))
        if not location['engines']['add']:
            trainListText += ' {}\n'.format(PSE.getBundleItem(u'None'))
        for loco in location['engines']['add']:
            line = TRE.pickupLoco(loco, True, False)
            trainListText += u' {}\n'.format(line)
    # Pick up cars
        trainListText += u'{}:\n'.format(PSE.getBundleItem(u'Cars'))
        if not location['cars']['add']:
            trainListText += u' {}\n'.format(PSE.getBundleItem(u'None'))
        for car in location['cars']['add']:
            if car['isLocal']:
                continue
            line = TRE.pickupCar(car, True, False)
            formattedSequence = u'{:02d}'.format(int(car['sequence']) - 6000)
            trainListText += u' {} {}\n'.format(formattedSequence, line)

        try: # Location summary
            td = PSE.JMRI.jmrit.operations.setup.Setup.getDirectionString(location[u'trainDirection'])
            # trainListText += unicode(location['userName'], PSE.ENCODING) + '\n'
            # trainListText += PSE.getBundleItem(u'Pattern Report for location ({})').format(location[u'userName']) + '\n'
            # trainListText += unicode(location['userName'], PSE.ENCODING) + '\n'
            trainListText += TMT.getStringTrainDepartsCars().format(location['userName'], td, str(location['cars']['total']), str(location['length']['length']), location['length']['unit'], str(location['weight'])) + '\n\n'
            # trainListText += u'{}\n\n'.format(TMT.getStringTrainDepartsCars().format(location[u'userName'], td, str(location['cars']['total']), str(location['length']['length']), location['length']['unit'], str(location['weight'])))
            # u'Train departs {} {} with {} cars, {} {}, {} tons'.format(location[u'userName'], td, str(location['cars']['total']), str(location['length']['length']), location['length']['unit'], str(location['weight']))
        except: # Terminates
            trainListText += TMT.getStringTrainTerminates().format(manifest['locations'][-1][u'userName']) + '\n'
            return trainListText



    return trainListText

def getDetailsForRollingStock(rs):

    rsDetailDict = {}

# Common items for all JMRI RS
    rsDetailDict['road'] = rs.getRoadName()
    rsDetailDict['number'] = rs.getNumber()
    rsDetailDict['carType'] = rs.getTypeName()
    rsDetailDict['length'] = rs.getLength()
    rsDetailDict['color'] = rs.getColor()
    rsDetailDict['weightTons'] = rs.getWeightTons()
    rsDetailDict['comment'] = rs.getComment()
    rsDetailDict['division'] = rs.getDivisionName()
    rsDetailDict['location']={'userName':rs.getTrackName(), 'track':{'userName':rs.getTrackName()}}
    rsDetailDict['destination']={'userName':rs.getDestinationName(), 'track':{'userName':rs.getDestinationTrackName()}}
    rsDetailDict['owner'] = rs.getOwnerName()
# Common items for all OPS RS
    rsDetailDict['Id'] = u'{} {}'.format(rs.getRoadName(), rs.getNumber())
    rsDetailDict['train'] = rs.getTrainName()

    return rsDetailDict

def getDetailsForCar(carObject):
    """
    Mimics jmri.jmrit.operations.setup.Setup.getCarAttributes()
    """

    kernelName = carObject.getKernelName()
    kSize = 0
    if kernelName:
        kSize = PSE.KM.getKernelByName(kernelName).getSize()

    carDetailDict = {}
# JMRI car attributes
    carDetailDict['loadType'] = carObject.getLoadType()
    carDetailDict['load'] = carObject.getLoadName()
    carDetailDict['hazardous'] = carObject.isHazardous()
    carDetailDict['kernel'] = carObject.getKernelName()
    carDetailDict['kernelSize'] = str(kSize)
    carDetailDict['returnWhenEmpty'] = carObject.getReturnWhenEmptyDestinationName()
    carDetailDict['caboose'] = carObject.isCaboose()
    carDetailDict['passenger'] = carObject.isPassenger()
    carDetailDict['removeComment'] = carObject.getDropComment()
    carDetailDict['addComment'] = carObject.getPickupComment()
    carDetailDict['finalDestination']={'userName':carObject.getFinalDestinationName(), 'track':{'userName':carObject.getFinalDestinationTrackName()}}

    return carDetailDict

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

def printExtendedManifest(trainName):


    
    return

def printExtendedWorkOrder(trainName):

    workOrderName = 'ops train ({}).txt'.format(trainName)
    workOrderPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchLists', workOrderName)
    if PSE.JAVA_IO.File(workOrderPath).isFile():
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

    reportName = PSE.getBundleItem('ops-Pattern Report') + '.json'
    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))

    textPatternReport = ''
# Header
    textPatternReport += report['railroad'] + '\n'
    textPatternReport += '\n'
    textPatternReport += PSE.getBundleItem('Pattern Report for location ({})').format(report['userName']) + '\n'
    textPatternReport += PSE.convertIsoToValidTime(report['date']) + '\n'
    textPatternReport += '\n'
    fdTally = []
# Body
    for location in report['locations']:
        carLength = 0
        textPatternReport += PSE.getBundleItem('List of inventory at {}').format(location['userName']) + '\n'
    # Engines
        textPatternReport += '{}:\n'.format(PSE.getBundleItem('Engines'))
        for loco in location['engines']['add']:
            formatPrefix = ' [{}] '.format('  ')
            line = TRE.pickupLoco(loco, True, False)
            textPatternReport += '{} {}\n'.format(formatPrefix ,line)
        if len(location['engines']['add']) == 0:
            textPatternReport += ' {}: {}\n\n'.format(PSE.getBundleItem('No engines at'), location['userName'])
    # Cars
        textPatternReport += '{}:\n'.format(PSE.getBundleItem('Cars'))
        for car in location['cars']['add']:
            carLength += int(car['length'])
            fdTally.append(car['finalDestination']['userName'])
            formatPrefix = ' [{}] '.format('  ')
            line = TRE.localMoveCar(car, True, False)
            textPatternReport += formatPrefix + ' ' + line + '\n'
        if len(location['cars']['add']) == 0:
            textPatternReport += ' {}: {}\n\n'.format(PSE.getBundleItem('No cars at'), location['userName'])

        summaryText = PSE.getBundleItem('Total cars:{},  Loads:{},  Empties:{}')
        textPatternReport += summaryText.format(location['total'], location['loads'], location['empties']) + '\n'

        trackLength = location['length']['length']
        avail = trackLength - carLength
        summaryText = PSE.getBundleItem('Track length:{},  Equipment length:{},  Available:{}')
        textPatternReport += summaryText.format(trackLength, carLength, avail) + '\n'

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

    _psLog.debug('opsTextSwitchList')

    TRE.makeReportItemWidthMatrix()
    TRE.translateMessageFormat()

    configFile = PSE.readConfigFile()

    location = configFile['Patterns']['PL']
    mcp = PSE.JMRI.jmrit.operations.setup.Setup.getLocalPrefix()
    hcp = configFile['Patterns']['US']['HCP']
    longestStringLength = PSE.findLongestStringLength((mcp, hcp))

    reportName = PSE.getBundleItem('ops-Switch List') + '.json'
    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))

    textSwitchList = ''

# Header
    textSwitchList += report['railroad'] + '\n'
    textSwitchList += '\n'
    textSwitchList += PSE.getBundleItem('Switch List for location ({})').format(location) + '\n'
    textSwitchList += '{}\n'.format(PSE.convertIsoToValidTime(report['date']))
    textSwitchList += '\n'
# Body
    for location in report['locations']: # For the OPS switch list, the locations list is a track list.
        textSwitchList += PSE.getBundleItem('List of inventory at {}').format(location['userName']) + '\n'
    # Locos
        textSwitchList += '{}:\n'.format(PSE.getBundleItem('Engines'))
        for loco in location['engines']['add']:
            currentTrack = loco['location']['track']['userName']
            destTrack = loco['destination']['track']['userName']
            if currentTrack == destTrack:
                formatPrefix = hcp.format(longestStringLength)
            else:
                formatPrefix = mcp.format(longestStringLength)

            line = TRE.setoutLoco(loco, True, False)
            textSwitchList += '{} {} {}\n'.format(formatPrefix, line, loco['destination']['track']['userName'])
    # Cars
        textSwitchList += '{}:\n'.format(PSE.getBundleItem('Cars'))
        for car in location['cars']['add']:
            currentTrack = car['location']['track']['userName']
            destTrack = car['destination']['track']['userName']
            if currentTrack == destTrack:
                formatPrefix = hcp.ljust(longestStringLength)
            elif car['trainName']:
                formatPrefix = hcp.ljust(longestStringLength)
            else:
                formatPrefix = mcp.ljust(longestStringLength)

            line = TRE.localMoveCar(car, True, False)
            textSwitchList += '{} {}\n'.format(formatPrefix, line)
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
    hcp = PSE.readConfigFile()['Patterns']['US']['HCP']

    longestStringLength = PSE.findLongestStringLength((pep, dep, pcp, dcp, mcp, hcp))
    textWorkOrder = ''
# Header
    textWorkOrder += manifest['railroad'] + '\n'
    textWorkOrder += '\n'
    textWorkOrder += '{} ({}) {}\n'.format(PSE.getBundleItem('Work order for train'), manifest['userName'], manifest['description'])
    textWorkOrder += '{}\n'.format(PSE.convertIsoToValidTime(manifest['date']))
    textWorkOrder += '\n'
# Body
    for location in manifest['locations']:
        textWorkOrder += TMT.getStringScheduledWork().format(location['userName']) + '\n'
    
    # Pick up locos
        textWorkOrder += '{}:\n'.format(PSE.getBundleItem('Engines'))
        for loco in location['engines']['add']:
            formatPrefix = pep.ljust(longestStringLength)
            line = TRE.pickupLoco(loco, True, False)
            textWorkOrder += '{} {}\n'.format(formatPrefix ,line)
    # Set out locos
        for loco in location['engines']['remove']:
            formatPrefix = dep.ljust(longestStringLength)
            line = TRE.setoutLoco(loco, True, False)
            textWorkOrder += '{} {}\n'.format(formatPrefix ,line)

        if len(location['engines']['add']) + len(location['engines']['remove']) == 0:
            textWorkOrder += ' {}: {}\n'.format(PSE.getBundleItem('No work at'), location['userName'])

    # Pick up cars
        textWorkOrder += '{}:\n'.format(PSE.getBundleItem('Cars'))
        for car in location['cars']['add']:
            if car['isLocal']:
                continue
            formatPrefix = pcp.ljust(longestStringLength)
            line = TRE.pickupCar(car, True, False)
            textWorkOrder += '{} {}\n'.format(formatPrefix ,line)
    # Move cars
        for car in location['cars']['add']:
            if not car['isLocal']:
                continue
            formatPrefix = mcp.ljust(longestStringLength)
            line = TRE.localMoveCar(car, True, False)
            textWorkOrder += '{} {}\n'.format(formatPrefix ,line)
    # Set out cars
        for car in location['cars']['remove']:
            if car['isLocal']:
                continue
            formatPrefix = dcp.ljust(longestStringLength)
            line = TRE.dropCar(car, True, False)
            textWorkOrder += '{} {}\n'.format(formatPrefix ,line)

        if len(location['cars']['add']) + len(location['cars']['remove']) == 0:
            textWorkOrder += ' {}: {}\n'.format(PSE.getBundleItem('No work at'), location['userName'])

        try:
        # Location summary
            td = PSE.JMRI.jmrit.operations.setup.Setup.getDirectionString(location['trainDirection'])
            textWorkOrder += TMT.getStringTrainDepartsCars().format(location['userName'], td, str(location['cars']['total']), str(location['length']['length']), location['length']['unit'], str(location['weight'])) + '\n'
        except:
        # Footer
            textWorkOrder += TMT.getStringTrainTerminates().format(manifest['locations'][-1]['userName']) + '\n'

        textWorkOrder += '\n'

    return textWorkOrder

def opsJmriManifest(manifest):
    """
    OPS version of the JMRI generated text switch list.
    Makes new switch lists from a JMRI train.
    This one is still under construction.
    The name is too similar to the OPS switch list.
    """

    _psLog.debug('opsJmriManifest')

    TRE.makeReportItemWidthMatrix()
    TRE.translateMessageFormat()

    TMT = PSE.JMRI.jmrit.operations.trains.TrainManifestText()
    # dep = PSE.JMRI.jmrit.operations.setup.Setup.getDropEnginePrefix()
    # pcp = PSE.JMRI.jmrit.operations.setup.Setup.getPickupCarPrefix()
    # dcp = PSE.JMRI.jmrit.operations.setup.Setup.getDropCarPrefix()
    # mcp = PSE.JMRI.jmrit.operations.setup.Setup.getLocalPrefix()
    # hcp = PSE.readConfigFile()['Patterns']['US']['HCP']

    # longestStringLength = PSE.findLongestStringLength((dep, pcp, dcp, mcp, hcp))

    for location in manifest['locations']:
    # Header
        manifestText = '{}\n'.format(PSE.getExtendedRailroadName())
        manifestText += '\n'
        manifestText += TMT.getStringManifestForTrain().format(manifest['userName'], manifest['description']) + '\n'
        manifestText += '{}\n'.format(PSE.convertIsoToValidTime(manifest['date']))
        manifestText += '\n'
        manifestText += '{}\n'.format(SMT.getStringSwitchListByTrack())

        trackList = PSE.LM.getLocationByName(location['userName']).getTracksByNameList(None)
        for track in trackList:
            manifestText += '\n'
            manifestText += '{}\n'.format(track.getName())
        # Pick up Locos
        # Set out locos
        # Pick up cars
        # Set out cars


    return

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
    rsDetailDict['Id'] = '{} {}'.format(rs.getRoadName(), rs.getNumber())
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

# coding=utf-8
# © 2023 Greg Ritacco

"""
Unified report formatting for all OPS generated reports.
The idea is to have all the JMRI and OPS text reports share a similar look.
All the reports are built from a json file, formatted like JMRI manifest.json.
    -Creates an OPS version of a JMRI train manifest, formatted on the JMRI model.
    -Creates an OPS version of the JMRI train switch list, formatted on the JMRI model.
    -Creates the OPS Pattern Report, formatted on the JMRI model.
    -Creates the OPS Switch List, formatted on the JMRI model.
"""

from opsEntities import TRE
from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.OE.TextReports')

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
    # There is no Move Engines so use Pickup Engines
        for loco in location['engines']['add']:
            pass
    # Move cars
        for car in location['cars']['add']:
            carLength += int(car['length'])
            fdTally.append(car['finalDestination']['userName'])
            formatPrefix = ' [{}] '.format('  ')
            line = TRE.localMoveCar(car, True, False)
            textPatternReport += formatPrefix + ' ' + line + '\n'
        

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

def opsTextSwitchList():
    """
    Creates a text Switch List from an OPS generated json file.
    """

    _psLog.debug('opsTextSwitchList')

    TRE.makeReportItemWidthMatrix()
    TRE.translateMessageFormat()

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
    epochTime = PSE.convertIsoTimeToEpoch(report['date'])
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

            # line = TRE.localMoveCar(loco, True, False)
            # textSwitchList += formatPrefix + ' ' + line + '\n'
    # Move cars
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
            textSwitchList += formatPrefix + line + '\n'

        textSwitchList += '\n'

    return textSwitchList

def opsTextManifest(manifest):
    """"
    OPS version of the JMRI generated text manifest.
    """

    _psLog.debug('opsTextManifest')

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

    textManifest = ''

# Header
    textManifest += manifest['railroad'] + '\n'
    textManifest += '\n'
    textManifest += '{}, {}'.format(manifest['userName'], manifest['description']) + '\n'
    epochTime = PSE.convertIsoTimeToEpoch(manifest['date'])
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
            line = TRE.pickupCar(car, True, False)
            textManifest += formatPrefix + ' ' + line + '\n'
    # Move cars
        for car in location['cars']['add']:
            if not car['isLocal']:
                continue
            formatPrefix = mcp.ljust(longestStringLength)
            line = TRE.localMoveCar(car, True, False)
            textManifest += formatPrefix + ' ' + line + '\n'
    # Set out cars
        for car in location['cars']['remove']:
            if car['isLocal']:
                continue
            formatPrefix = dcp.ljust(longestStringLength)
            line = TRE.dropCar(car, True, False)
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


def opsTextSwitchLists(manifest, typeFlag):
    """
    OPS version of the JMRI generated text switch list.
    Makes new switch lists from a JMRI train.
    This one is still under construction.
    The name is too similar to the OPS switch list.
    """

    _psLog.debug('opsTextSwitchLists')

    TRE.makeReportItemWidthMatrix()
    TRE.translateMessageFormat()

    configFile = PSE.readConfigFile()
    isSequence, sequenceHash = PSE.getSequenceHash()

    messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getPickupSwitchListMessageFormat()
    TMT = PSE.JMRI.jmrit.operations.trains.TrainManifestText()
    SMT = PSE.JMRI.jmrit.operations.trains.TrainSwitchListText()
    pep = PSE.JMRI.jmrit.operations.setup.Setup.getPickupEnginePrefix()
    dep = PSE.JMRI.jmrit.operations.setup.Setup.getDropEnginePrefix()
    pcp = PSE.JMRI.jmrit.operations.setup.Setup.getPickupCarPrefix()
    dcp = PSE.JMRI.jmrit.operations.setup.Setup.getDropCarPrefix()
    mcp = PSE.JMRI.jmrit.operations.setup.Setup.getLocalPrefix()
    hcp = PSE.readConfigFile()['Patterns']['US']['HCP']

    longestStringLength = PSE.findLongestStringLength((pep, dep, pcp, dcp, mcp, hcp))

    for location in manifest['locations']:
    # Header
        epochTime = PSE.convertIsoTimeToEpoch(manifest['date'])

        textSwitchList = '{}\n'.format(PSE.getExtendedRailroadName())
        textSwitchList += '\n'
        textSwitchList += '{}\n'.format(SMT.getStringSwitchListFor().format(location['userName']))
        textSwitchList += '{}\n'.format(PSE.validTime(epochTime))
        textSwitchList += '\n'
        textSwitchList += '{}\n'.format(SMT.getStringSwitchListByTrack())
        

        trackList = PSE.LM.getLocationByName(location['userName']).getTracksByNameList(None)
        for track in trackList:
            textSwitchList += '\n'
            textSwitchList += '{}\n'.format(track.getName())
        # Pick up Locos
        # Set out locos
        # Pick up cars
            carList = PSE.CM.getList(track)
            carSeq = []
            for car in carList:
                carSeq.append((car.toString(), sequenceHash['cars'][car.toString()]))
            carSeq.sort(key=lambda row: row[1])
            carList = [car[0] for car in carSeq] # strip off the seq number
            
            for car in carList:
                carX = car.split(' ')
                carObject = PSE.CM.getByRoadAndNumber(carX[0], carX[1])
                if carObject.getTrainName():
                     textSwitchList += '{}\n'.format(pcp)
                     carAttribs = getDetailsForCar(carObject)
                     rsAttribs = getDetailsForRollingStock(carObject)
                     carAttribs.update(rsAttribs)



                else:
                    roadName = carObject.getRoadName().ljust(PSE.REPORT_ITEM_WIDTH_MATRIX['Road'])
                    roadNumber = carObject.getNumber().rjust(PSE.REPORT_ITEM_WIDTH_MATRIX['Number'])
                    formatPrefix = hcp.ljust(longestStringLength)
                    textSwitchList += '{} {} {}\n'.format(formatPrefix, roadName, roadNumber)
                    

        # Set out cars
            for car in location['cars']['remove']:
                if car['destination']['track']['userName'] == track.getName():
                    formatPrefix = dcp.ljust(longestStringLength)
                    line = PSE.dropCar(car, False, False)
                    textSwitchList += formatPrefix + ' ' + line + '\n'

        textSwitchList += '\n'

        switchListName = 'location ({}).txt'.format(location['userName'])
        switchListPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'switchlists', switchListName)
        PSE.genericWriteReport(switchListPath, textSwitchList)

    return

# def o2oWorkEvents(manifest):
#     """
#     Makes an o2o workevents list from a manifest.
#     manifest is a string from the json file.
#     """

#     _psLog.debug('o2oWorkEvents')
# # Header
#     o2oWorkEvents = 'HN,' + manifest['railroad'].replace('\n', ';') + '\n'
#     o2oWorkEvents += 'HT,' + manifest['userName'] + '\n'
#     o2oWorkEvents += 'HD,' + manifest['description'] + '\n'
#     epochTime = PSE.convertIsoTimeToEpoch(manifest['date'])
#     o2oWorkEvents += 'HV,' + PSE.validTime(epochTime) + '\n'
#     o2oWorkEvents += 'WT,' + str(len(manifest['locations'])) + '\n'
# # Body
#     for i, location in enumerate(manifest['locations'], start=1):
#         o2oWorkEvents += 'WE,{},{}\n'.format(str(i), location['userName'])
#         for loco in location['engines']['add']:
#             o2oWorkEvents += 'PL,{}\n'.format(_makeLine(loco))
#         for loco in location['engines']['remove']:
#             o2oWorkEvents += 'SL,{}\n'.format(_makeLine(loco))
#         for car in location['cars']['add']:
#             o2oWorkEvents += 'PC,{}\n'.format(_makeLine(car))
#         for car in location['cars']['remove']:
#             o2oWorkEvents += 'SC,{}\n'.format(_makeLine(car))
        
#     return o2oWorkEvents

# def _makeLine(rs):
#     """
#     Helper function to make the rs line for o2oWorkEvents.
#     format: TP ID, Road, Number, Car Type, L/E/O, Load or Model, From, To
#     """

#     try: # Cars
#         loadName = rs['load']
#         lt = PSE.getShortLoadType(rs)
#     except: # Locos
#         loadName = rs['model']
#         lt = PSE.getBundleItem('Occupied').upper()[0]

#     ID = rs['road'] + ' ' + rs['number']
#     pu = rs['location']['userName'] + ';' + rs['location']['track']['userName']
#     so = rs['destination']['userName'] + ';' + rs['destination']['track']['userName']

#     line = '{},{},{},{},{},{},{},{}'.format(ID, rs['road'], rs['number'], rs['carType'], lt, loadName, pu, so)

#     return line
